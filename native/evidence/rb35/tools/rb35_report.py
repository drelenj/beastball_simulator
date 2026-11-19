"""RB-3.5 zone-foul diagnosis report from soak_driver2 raw logs (reads files; runs no match).
python3 native/evidence/rb35/tools/rb35_report.py native/evidence/rb35
"""
import json, sys
from collections import Counter
from pathlib import Path


def q(xs):
    xs = sorted(x for x in xs if x is not None)
    if not xs: return None
    at = lambda f: xs[min(len(xs) - 1, int(round(f * (len(xs) - 1))))]
    return dict(n=len(xs), min=round(xs[0], 2), q1=round(at(.25), 2), median=round(at(.5), 2), q3=round(at(.75), 2), max=round(xs[-1], 2))


def summarise(diags):
    nob = [d['nearest_off_ball_offence']['distance_to_fouler'] for d in diags if d['nearest_off_ball_offence']]
    n = len(diags)
    band = Counter('<=10m' if x <= 10 else '10-20m' if x <= 20 else '>20m' for x in nob)
    since = [d['fouler']['live_ms_since_last_exit'] for d in diags]
    return dict(
        fouls=n,
        fouler_distance_to_zone_centre_m=q([d['fouler']['distance_to_zone_centre'] for d in diags]),
        fouler_y=q([d['fouler']['y'] for d in diags]),
        distance_to_ball_m=q([d['ball']['distance_to_fouler'] for d in diags]),
        ball_distance_to_zone_centre_m=q([d['ball']['distance_to_zone_centre'] for d in diags]),
        distance_to_carrier_m=q([d['ball']['carrier']['distance_to_fouler'] for d in diags if d['ball']['carrier']]),
        no_carrier_share=round(sum(1 for d in diags if not d['ball']['carrier']) / n, 3) if n else None,
        distance_to_nearest_off_ball_offence_m=q(nob),
        nearest_off_ball_offence_band_share={k: round(v / len(nob), 3) for k, v in sorted(band.items())} if nob else None,
        nearest_off_ball_offence_distance_to_zone_centre_m=q([d['nearest_off_ball_offence']['distance_to_zone_centre'] for d in diags if d['nearest_off_ball_offence']]),
        offence_within_10m=q([d['offence_within_10m'] for d in diags]), offence_within_20m=q([d['offence_within_20m'] for d in diags]),
        teammates_in_same_zone=q([d['teammates_in_same_zone'] for d in diags]),
        live_s_in_zone=q([d['fouler']['live_ms_in_zone'] / 1000 for d in diags]),
        reentered_within_5s_share=round(sum(d['fouler']['reentered_within_5s'] for d in diags) / n, 3) if n else None,
        last_exit_within_10s_share=round(sum(1 for x in since if x is not None and x <= 10000) / n, 3) if n else None,
        frozen_or_immune_prev_10s_share=round(sum(d['fouler']['frozen_or_immune_prev_10s'] for d in diags) / n, 3) if n else None,
        ball_status=dict(Counter(d['ball']['status'] for d in diags)),
        fouler_roles=dict(Counter(d['fouler']['role'] for d in diags)))


def analyse(root, block, seed):
    name = f'{block}-seed{seed:02d}'
    res = json.loads((root/block/f'{name}.json').read_text())
    log = json.loads((root/block/f'raw-{name}.json').read_text())['log']
    diags = [r['data'] for r in log if r['event'] == 'zone_foul_diagnosis']
    summ = [r['data'] for r in log if r['event'] == 'zone_time_summary']
    return dict(name=name, status=res['status'], score=res.get('score'), runtime_s=res.get('runtime_s'),
                trace_hash=res.get('trace_hash'), state_hash=res.get('state_hash'), foul_reasons=res.get('foul_reasons'),
                zone_unmarked=sum(d['kind'] == 'zone_unmarked' for d in diags), zone_residence=sum(d['kind'] == 'zone_residence' for d in diags),
                defender_live_time=summ[-1]['teams'] if summ else None,
                zone_unmarked_diagnosis=summarise([d for d in diags if d['kind'] == 'zone_unmarked']),
                zone_residence_diagnosis=summarise([d for d in diags if d['kind'] == 'zone_residence'])), diags


if __name__ == '__main__':
    root = Path(sys.argv[1]); rows = []; every = []
    for block, seed in (('real', 1), ('real', 3), ('control', 1)):
        if (root/block/f'{block}-seed{seed:02d}.json').exists():
            row, diags = analyse(root, block, seed); rows.append(row); every += diags
    overall = dict(zone_unmarked=summarise([d for d in every if d['kind'] == 'zone_unmarked']),
                   zone_residence=summarise([d for d in every if d['kind'] == 'zone_residence']))
    (root/'rb35_table.json').write_text(json.dumps(dict(matches=rows, overall=overall), indent=2, sort_keys=True) + '\n')
    print(json.dumps(dict(matches=rows, overall=overall), indent=1, sort_keys=True))
