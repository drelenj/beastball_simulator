"""Builds summary tables and extended metrics from per-seed outputs. Read-only on inputs."""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO = '/home/user/beastball_simulator'
sys.path.insert(0, REPO)
from native.nbl_roster import load_canon_nbl  # noqa: E402

OUT = Path(REPO) / 'native/evidence/soak-rb32'
ROLES_CONTROL = ['field'] * 18 + ['keeper'] * 2 + ['archer'] * 2


def role_map(block):
    m = {}
    if block == 'real':
        R = load_canon_nbl(('Garvian Guardians', 'Ala Apex'))
        for t in 'AB':
            for a in R[t].athletes:
                m[f'{t}:{a.source_id}'] = a.role
    else:
        for t in 'AB':
            for n, role in enumerate(ROLES_CONTROL):
                m[f'{t}:{n}'] = role
    return m


def extended(block, seed, roles):
    raw = json.loads((OUT / block / f'raw-{block}-seed{seed:02d}.json').read_text())
    L = raw['log']
    unmapped = Counter()

    def role_of(pid):
        if pid in roles:
            return roles[pid]
        unmapped[pid] += 1
        return 'unmapped'

    fouls = Counter()
    for x in L:
        if x['event'] == 'foul':
            d = x['data']
            actor = d.get('actor')
            fouls[(d['reason'], role_of(actor), actor.split(':')[0])] += 1
    dq = Counter()
    for c in raw['calls']:
        if c['kind'] == 'discipline' and c.get('dq'):
            dq[(c['kind_of_foul'], role_of(c['player']), c['player'].split(':')[0])] += 1
    awards = Counter()
    for x in L:
        if x['event'] == 'foul_award':
            d = x['data']
            awards[(d['method'], d['points'], d['team'])] += 1
    # Arrows per Archer. Legal = arrow_release (has player). Illegal target = foul
    # reason archery_target (has actor). Forfeit calls carry team only, so per-player
    # illegal counts come from the foul record. Miss is not recorded.
    arrows = defaultdict(lambda: dict(legal=0, illegal_target=0))
    shooter_roles = Counter()
    for x in L:
        if x['event'] == 'arrow_release':
            shooter_roles[role_of(x['data']['player'])] += 1
            arrows[x['data']['player']]['legal'] += 1
        if x['event'] == 'foul' and x['data']['reason'] == 'archery_target':
            arrows[x['data']['actor']]['illegal_target'] += 1
    # Per-Archer rows keep only Archer-role players; field/keeper releases are counted separately.
    arrow_rows = {pid: dict(v, role=role_of(pid), team=pid.split(':')[0]) for pid, v in arrows.items() if role_of(pid) == 'archer'}
    # Goals: restart-linked if no possession change to the other team has occurred
    # since the most recent restart awarded. Otherwise live play.
    goal_split = Counter()
    restart_team = None
    for x in L:
        ev = x['event']
        if ev == 'restart_awarded':
            restart_team = x['data']['team']
        elif ev == 'possession' and restart_team is not None and x['data'].get('team') != restart_team:
            restart_team = None
        elif ev == 'goal':
            d = x['data']
            kind = 'restart_linked' if restart_team is not None and d['team'] == restart_team else 'live'
            goal_split[(d['team'], kind)] += d['points']
    # Carry attempts by outcome: NOT RECORDED (no outcome field in the engine report).
    carry_events = raw['carry_events']
    return dict(
        fouls={f'{k[0]}|{k[1]}|team{k[2]}': v for k, v in sorted(fouls.items())},
        dqs={f'{k[0]}|{k[1]}|team{k[2]}': v for k, v in sorted(dq.items())},
        foul_award_points={f'{k[0]}|{k[1]}pt|team{k[2]}': v for k, v in sorted(awards.items())},
        arrows_per_archer=dict(sorted(arrow_rows.items())),
        legal_releases_by_shooter_role=dict(shooter_roles),
        goal_points_split={f'{t}|{k}': v for (t, k), v in sorted(goal_split.items())},
        carry_events_observed=len(carry_events),
        unmapped_player_ids=dict(unmapped),
        missing_fields=['carry outcome (tackled/grounded/turnover/stopped short) not recorded',
                        'foul_award -> originating foul/rule link not recorded',
                        'DQ -> rule link not recorded (discipline call has kind_of_foul only)',
                        'arrow miss not recorded as a distinct outcome',
                        'illegal-target forfeits not attributed to a player in arrow_forfeited calls (taken from foul records)'],
    )


def main():
    blocks = {'real': [1, 2, 3, 7, 8, 9, 10], 'control': list(range(1, 11))}
    summary = {}
    ext = {}
    for block, seeds in blocks.items():
        roles = role_map(block)
        summary[block] = []
        ext[block] = {}
        for seed in seeds:
            p = OUT / block / f'{block}-seed{seed:02d}.json'
            if not p.exists():
                summary[block].append(dict(seed=seed, status='missing'))
                continue
            d = json.loads(p.read_text())
            summary[block].append(d)
            if d.get('status') in ('final', 'partial'):
                ext[block][seed] = extended(block, seed, roles)
    (OUT / 'summary.json').write_text(json.dumps(summary, indent=2, sort_keys=True, default=str) + '\n')
    (OUT / 'extended.json').write_text(json.dumps(ext, indent=2, sort_keys=True, default=str) + '\n')
    print('ok', {b: len(v) for b, v in summary.items()})


if __name__ == '__main__':
    main()
