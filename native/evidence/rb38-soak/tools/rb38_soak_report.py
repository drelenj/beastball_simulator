"""RB-3.8 mass-soak report. Reads per-match JSON and raw logs; runs no match.
python3 native/evidence/rb38-soak/tools/rb38_soak_report.py native/evidence/rb38-soak
Writes soak_table.json and SUMMARY_TABLE.md into the root directory.
"""
import json
import statistics
import sys
from collections import Counter
from pathlib import Path


def gz_or_plain(path):
    import gzip
    if path.exists():
        return path.read_bytes().decode()
    gz = Path(str(path) + '.gz')
    return gzip.open(gz, 'rt').read()


def analyse(root, block, name):
    res = json.loads((root / block / f'{name}.json').read_text())
    if res.get('status') not in ('final', 'partial'):
        return dict(name=name, block=block, status=res.get('status'), error=res.get('error'), runtime_s=res.get('runtime_s'))
    rawp = root / block / f'raw-{name}.json'
    text = gz_or_plain(rawp)
    raw = json.loads(text)
    log = raw['log']
    play = Counter(); award = Counter(); zone = []; ev = Counter()
    for r in log:
        d = r['data']
        ev[r['event']] += 1
        if r['event'] == 'goal':
            play[d['team']] += d['points']
        elif r['event'] == 'foul_award':
            award[d['team']] += d['points']
        elif r['event'] == 'zone_foul_diagnosis' and d['kind'] == 'zone_unmarked':
            zone.append(dict(t_live_ms=r['live_ms'], period=r['period'], fouler=d['fouler']['id'], team=d['fouler']['team']))
    m = res.get('metrics', {}) or {}
    poss = m.get('possessions', {})
    shots = Counter(a['team'] for a in raw.get('rb_attempts', []) if a.get('shot_attempt'))
    carry = m.get('carry_attempts', {})
    total = sum(play.values()) + sum(award.values())
    fr = text.count('freeze_recovery')
    return dict(
        name=name, block=block, status=res['status'], steps=res['steps'], live_ms=res['live_ms'], end_ms=res['end_ms'],
        score=res['score'], trace_hash=res['trace_hash'], state_hash=res['state_hash'],
        config_digest=res.get('config_digest'), runtime_s=res.get('runtime_s'),
        raw_log=f'native/evidence/rb38-soak/{block}/raw-{name}.json.gz',
        result_file=f'native/evidence/rb38-soak/{block}/{name}.json',
        possessions={t: poss[t]['count'] for t in poss},
        possessions_ending_in_attempt_pct={t: round(100 * poss[t]['share_ending_in_attempt'], 2) for t in poss if poss[t].get('share_ending_in_attempt') is not None},
        shot_attempts={t: shots.get(t, 0) for t in ('A', 'B')},
        carry_attempts={t: carry.get(t, {}).get('attempts', 0) for t in ('A', 'B')},
        carry_goals={t: carry.get(t, {}).get('goals', 0) for t in ('A', 'B')},
        points_from_play={t: play.get(t, 0) for t in ('A', 'B')},
        points_from_foul_awards={t: award.get(t, 0) for t in ('A', 'B')},
        share_points_from_fouls=round(sum(award.values()) / total, 4) if total else None,
        foul_reasons=res.get('foul_reasons', {}),
        dqs={t: m.get('dqs', {}).get(t) for t in ('A', 'B')},
        legal_arrow_rate={t: m.get('arrows', {}).get(t, {}).get('legal_rate') for t in ('A', 'B')},
        arrows={t: m.get('arrows', {}).get(t) for t in ('A', 'B')},
        restart_timeouts=m.get('restart_timeouts'),
        restart_completion_ratio=res.get('restart_completion_ratio'),
        zone_unmarked=len(zone), zone_unmarked_calls=zone,
        freeze_recovery_in_raw_log=fr,
        freeze_recovery_in_foul_reasons=res.get('foul_reasons', {}).get('freeze_recovery', 0),
        non_finishing=res.get('non_finishing'),
    )


def stats(rows, key):
    vals = [r[key] for r in rows if isinstance(r.get(key), (int, float))]
    if not vals:
        return None
    return dict(min=min(vals), median=statistics.median(vals), max=max(vals), n=len(vals))


def main():
    root = Path(sys.argv[1])
    rows = []
    for block in ('real', 'control'):
        for p in sorted((root / block).glob(f'{block}-seed*.json')):
            name = p.stem
            rows.append(analyse(root, block, name))
    (root / 'soak_table.json').write_text(json.dumps(rows, indent=2, sort_keys=True) + '\n')
    lines = ['# RB-3.8 mass soak: per-match and summary (measurements, not ACCEPTED)', '']
    lines.append('## Per match')
    lines.append('| match | status | steps | score A-B | play pts A/B | foul-award pts A/B | share pts from fouls | possessions A/B | ending in attempt % A/B | shot att A/B | carry att A/B | carry goals A/B | DQs A/B | legal-arrow rate A/B | restart timeouts | restart completion | zone_unmarked | freeze_recovery (raw/reason) | runtime s | trace_hash | state_hash |')
    lines.append('|' + '---|' * 21)
    def f(x):
        return '—' if x is None else (f'{x:.3f}' if isinstance(x, float) else str(x))
    for r in rows:
        if r['status'] not in ('final', 'partial'):
            lines.append(f"| {r['name']} | **FAILED** | — | {r.get('error')} | | | | | | | | | | | | | | | {r.get('runtime_s')} | | |")
            continue
        pa = r['possessions']; pe = r['possessions_ending_in_attempt_pct']
        lines.append(
            f"| {r['name']} | {r['status']}{' (NON-FINISHING)' if r['status']=='partial' else ''} | {r['steps']} | {r['score']['A']}-{r['score']['B']} | "
            f"{r['points_from_play']['A']}/{r['points_from_play']['B']} | {r['points_from_foul_awards']['A']}/{r['points_from_foul_awards']['B']} | {f(r['share_points_from_fouls'])} | "
            f"{pa.get('A')}/{pa.get('B')} | {f(pe.get('A'))}/{f(pe.get('B'))} | {r['shot_attempts']['A']}/{r['shot_attempts']['B']} | "
            f"{r['carry_attempts']['A']}/{r['carry_attempts']['B']} | {r['carry_goals']['A']}/{r['carry_goals']['B']} | "
            f"{r['dqs']['A']}/{r['dqs']['B']} | {f(r['legal_arrow_rate']['A'])}/{f(r['legal_arrow_rate']['B'])} | {r['restart_timeouts']} | "
            f"{f(r['restart_completion_ratio'])} | {r['zone_unmarked']} | {r['freeze_recovery_in_raw_log']}/{r['freeze_recovery_in_foul_reasons']} | "
            f"{r['runtime_s']} | `{r['trace_hash']}` | `{r['state_hash']}` |")
    lines.append('')
    lines.append('## Foul counts by reason (per match)')
    reasons = sorted({k for r in rows if 'foul_reasons' in r for k in r['foul_reasons']})
    lines.append('| match | ' + ' | '.join(reasons) + ' |')
    lines.append('|' + '---|' * (len(reasons) + 1))
    for r in rows:
        if 'foul_reasons' in r:
            lines.append(f"| {r['name']} | " + ' | '.join(str(r['foul_reasons'].get(k, 0)) for k in reasons) + ' |')
    lines.append('')
    for block in ('real', 'control'):
        br = [r for r in rows if r['block'] == block and r['status'] in ('final', 'partial')]
        if not br:
            continue
        lines.append(f'## Summary: {block} (n = {len(br)} finished; min / median / max across seeds)')
        lines.append('| measure | min | median | max |')
        lines.append('|---|---|---|---|')
        def row(label, fn):
            vals = [fn(r) for r in br]
            vals = [v for v in vals if v is not None]
            if not vals:
                lines.append(f'| {label} | — | — | — |'); return
            fmt = lambda x: round(x, 4) if isinstance(x, float) else x
            lines.append(f'| {label} | {fmt(min(vals))} | {fmt(statistics.median(vals))} | {fmt(max(vals))} |')
        row('score A', lambda r: r['score']['A'])
        row('score B', lambda r: r['score']['B'])
        row('points from play A', lambda r: r['points_from_play']['A'])
        row('points from play B', lambda r: r['points_from_play']['B'])
        row('foul-award pts A', lambda r: r['points_from_foul_awards']['A'])
        row('foul-award pts B', lambda r: r['points_from_foul_awards']['B'])
        row('share of points from fouls', lambda r: r['share_points_from_fouls'])
        row('possessions A', lambda r: r['possessions']['A'])
        row('possessions B', lambda r: r['possessions']['B'])
        row('% possessions ending in attempt A', lambda r: r['possessions_ending_in_attempt_pct'].get('A'))
        row('% possessions ending in attempt B', lambda r: r['possessions_ending_in_attempt_pct'].get('B'))
        row('shot attempts A', lambda r: r['shot_attempts']['A'])
        row('shot attempts B', lambda r: r['shot_attempts']['B'])
        row('carry attempts A', lambda r: r['carry_attempts']['A'])
        row('carry attempts B', lambda r: r['carry_attempts']['B'])
        row('carry goals A', lambda r: r['carry_goals']['A'])
        row('carry goals B', lambda r: r['carry_goals']['B'])
        row('DQs A', lambda r: r['dqs']['A'])
        row('DQs B', lambda r: r['dqs']['B'])
        row('legal-arrow rate A', lambda r: r['legal_arrow_rate']['A'])
        row('legal-arrow rate B', lambda r: r['legal_arrow_rate']['B'])
        row('restart timeouts', lambda r: r['restart_timeouts'])
        row('restart completion ratio', lambda r: r['restart_completion_ratio'])
        row('zone_unmarked calls', lambda r: r['zone_unmarked'])
        row('freeze_recovery in raw log', lambda r: r['freeze_recovery_in_raw_log'])
        lines.append('')
    (root / 'SUMMARY_TABLE.md').write_text('\n'.join(lines) + '\n')
    print('rows', len(rows))


if __name__ == '__main__':
    main()
