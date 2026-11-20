"""RB-3.16 soak measurement across 13 matches. Reads raw logs and result files only.
Definitions follow native/evidence/rb316/measure.py. Keeper = the team's first role-keeper in
roster order (real: NBL24-07-11 / NBL24-01-11, identical to measure.py's hard-coded ids;
control: index 18). Field = any other opponent.
python3 native/evidence/rb316-soak/tools/measure316_soak.py native/evidence/rb316-soak
"""
import gzip
import json
import math
import statistics
import sys
from collections import Counter
from pathlib import Path

REPO = Path('/home/user/beastball_simulator')
sys.path.insert(0, str(REPO))
from native.nbl_roster import load_canon_nbl  # noqa: E402
from native.roster import rb3_control_rosters  # noqa: E402


def keepers_by_team(block):
    R = load_canon_nbl(('Garvian Guardians', 'Ala Apex')) if block == 'real' else rb3_control_rosters()
    out = {}
    for t in 'AB':
        first = next(a for a in R[t].athletes if a.role == 'keeper')
        out[t] = f'{t}:{first.source_id}'
    return out


def read(path):
    p = Path(path)
    if p.exists():
        return json.loads(p.read_text())
    return json.loads(gzip.open(str(p) + '.gz', 'rt').read())


def row(root, block, name, keepers):
    res = read(root / block / f'{name}.json')
    if res.get('status') not in ('final', 'partial'):
        return dict(name=name, block=block, status=res.get('status'), error=res.get('error'))
    text = gzip.open(root / block / f'raw-{name}.json.gz', 'rt').read() if (root / block / f'raw-{name}.json.gz').exists() else (root / block / f'raw-{name}.json').read_text()
    raw = json.loads(text)
    log = raw['log']
    m = res['metrics']
    P = m['points']
    K = set(keepers.values())
    methods = Counter()
    for e in log:
        d = e.get('data') or {}
        if e['event'] == 'goal':
            methods[(d['team'], d['method'])] += d['points']
        elif e['event'] == 'foul_award':
            methods[(d['team'], {'half_goal': 'half', 'full_goal_award': 'award'}.get(d['method'], d['method']))] += d['points']
    sh = Counter(); pas = Counter(); shot_team = Counter(); near = 0
    for i, r in enumerate(log):
        dd = r.get('data') or {}
        if r['event'] != 'release' or dd.get('kind') not in ('shot', 'pass'):
            continue
        tm = dd['player'].split(':')[0]
        o = 'other'
        for e in log[i + 1:i + 90]:
            if e['event'] == 'goal':
                o = 'scored'; break
            if e['event'] == 'keeper_contact':
                o = 'keeper'; break
            if e['event'] == 'control':
                p = e['data']['player']
                if p.split(':')[0] == tm:
                    o = 'own'
                elif p in K:
                    o = 'keeper'
                else:
                    o = 'field'
                if dd['kind'] == 'pass' and o in ('field', 'keeper'):
                    if math.hypot(e['ball'][0] - r['ball'][0], e['ball'][1] - r['ball'][1]) <= 3:
                        near += 1
                break
            if e['event'] in ('boundary', 'restart_awarded'):
                o = 'out/award'; break
        (sh if dd['kind'] == 'shot' else pas)[o] += 1
        if dd['kind'] == 'shot':
            shot_team[tm] += 1
    ns = sum(sh.values()); npas = sum(pas.values())
    tackles = Counter(e['data'].get('actor', '').split(':')[0] for e in log if e['event'] == 'tackle_count')
    zone_calls = [e for e in log if e['event'] == 'zone_foul_diagnosis' and e['data'].get('kind') == 'zone_unmarked']
    return dict(
        name=name, block=block, status=res['status'], steps=res['steps'], runtime_s=res['runtime_s'],
        trace_hash=res['trace_hash'], state_hash=res['state_hash'], score=res['score'],
        points_play={t: P[t]['play'] for t in 'AB'}, points_awards={t: P[t]['penalty_awards'] for t in 'AB'},
        points_by_method={f'{t}|{k}': v for (t, k), v in sorted(methods.items())},
        possessions={t: m['possessions'][t]['count'] for t in 'AB'},
        attempt_share={t: m['possessions'][t]['share_ending_in_attempt'] for t in 'AB'},
        shots_by_team=dict(shot_team),
        shot_outcomes={k: v for k, v in sh.most_common()},
        shot_outcome_shares_pct={k: round(100 * v / ns, 1) for k, v in sh.items()} if ns else {},
        shots_total=ns,
        passes=npas, pass_outcomes=dict(pas),
        pass_interception_pct=round(100 * (pas['field'] + pas['keeper']) / npas, 1) if npas else None,
        interceptions_within_3m=near,
        tackles_by_actor_team=dict(tackles), tackles_total=sum(tackles.values()),
        carry_attempts={t: m['carry_attempts'][t]['attempts'] for t in 'AB'},
        carry_goals={t: m['carry_attempts'][t]['goals'] for t in 'AB'},
        foul_reasons=res.get('foul_reasons', {}),
        dqs={t: m['dqs'][t] for t in 'AB'},
        legal_arrow_rate={t: m['arrows'][t]['legal_rate'] for t in 'AB'},
        restart_timeouts=m['restart_timeouts'], restart_completion_ratio=res['restart_completion_ratio'],
        zone_unmarked_calls=len(zone_calls),
        zone_unmarked_call_detail=[dict(live_ms=e['live_ms'], period=e['period'], fouler=e['data']['fouler']['id']) for e in zone_calls],
        zone_events={k: sum(1 for e in log if e['event'] == k) for k in ('zone_foul_diagnosis', 'zone_unmarked_diagnosis', 'zone_time_summary')},
        zone_residence_events=sum(1 for e in log if 'residence' in e['event']),
        keepers=keepers,
    )


def pct(vals, q):
    return statistics.quantiles(vals, n=100, method='inclusive')[q - 1]


def main():
    root = Path(sys.argv[1])
    keepers = {b: keepers_by_team(b) for b in ('real', 'control')}
    rows = []
    for block in ('real', 'control'):
        for p in sorted((root / block).glob(f'{block}-seed*.json')):
            rows.append(row(root, block, p.stem, keepers[block]))
    (root / 'measure316_table.json').write_text(json.dumps(rows, indent=2, sort_keys=True, default=str) + '\n')
    team_games = [s for r in rows if r.get('block') == 'real' and r.get('status') == 'final' for s in (r['score']['A'], r['score']['B'])]
    summary = {}
    if team_games:
        summary['real_team_scores'] = dict(
            n=len(team_games), median=statistics.median(team_games), mean=round(statistics.mean(team_games), 2),
            sd_sample=round(statistics.stdev(team_games), 2), sd_population=round(statistics.pstdev(team_games), 2),
            p5=pct(team_games, 5), p95=pct(team_games, 95), min=min(team_games), max=max(team_games))
        summary['owner_target_canon'] = dict(median=76, sd=12.7, p5_p95=[59, 102])
    (root / 'measure316_summary.json').write_text(json.dumps(summary, indent=2, sort_keys=True) + '\n')
    print(json.dumps(summary, indent=1))
    print('rows', len(rows), 'keepers', keepers)


if __name__ == '__main__':
    main()
