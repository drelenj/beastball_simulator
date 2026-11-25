"""Aggregate diagnostic witnesses and the existing possession/score measures."""
import argparse
from collections import Counter, defaultdict
import gzip
import json
from pathlib import Path
from statistics import mean, median

from audit.native.rb330.analysis import summarize

FAILURES = {'no_contact','contact_without_confirmed_grip','grip_lost','maneuver','released_first','grip_unresolved'}


def fraction(count, total):
    return count / total if total else None


def average(values):
    values = [v for v in values if v is not None]
    return mean(values) if values else None


def rating_band(r):
    if r is None:
        return 'missing'
    return '<0.65' if r < .65 else '.65–.79' if r < .80 else '≥.80'


def buckets(rows, group, reduce):
    combined = defaultdict(list)
    for row in rows:
        combined[group(row)].append(row)
    return {k: reduce(v) for k,v in sorted(combined.items())}


def shot_rates(rows):
    faced, on_target = sum(bool(r['keeper']) for r in rows), sum(r['on_target'] and bool(r['keeper']) for r in rows)
    saves = sum(r['save'] for r in rows)
    return dict(shots=len(rows),faced=faced,on_target=on_target,saves=saves,
                save_per_faced=fraction(saves,faced),save_per_on_target=fraction(saves,on_target),
                goals=sum(r['goal'] for r in rows),goals_touched=sum(r['goal'] and r['keeper_touch'] for r in rows))


def tackle_rates(rows):
    return dict(n=len(rows),made=sum(r['outcome']=='takedown' for r in rows),
                made_rate=fraction(sum(r['outcome']=='takedown' for r in rows),len(rows)),
                median_ms=median(r['end_ms']-r['start_ms'] for r in rows),
                targeted_actual_carrier=sum(r['targeted_actual_carrier'] for r in rows),
                mean_commit_distance=average(r['distance_at_commit'] for r in rows))


def turnover_report(runs):
    by_type = Counter()
    credits = Counter()
    for run in runs:
        for row in run['team_lines']:
            by_type.update(row['turnovers_by_type'])
            credits.update(turnovers=row['turnovers'],interceptions=row['interceptions'],
                           attempts=row['tackles_attempted'],made=row['tackles_made'])
    return dict(total=by_type,per_team_game={k:v/(2*len(runs)) for k,v in by_type.items()},ledger=credits)


def interception_report(rows):
    n = len(rows)
    measured = [r for r in rows if 'true_margin' in r]
    overlaps = [r for r in measured if r['believed_margin'] >= 0 > r['true_margin']]
    yaw_crosses = [r for r in measured if r['true_margin'] >= 0 > r['thrown_margin']]
    return dict(n=n, restart=sum(r['restart'] for r in rows), usable=len(measured),
                never_seen=sum(r.get('ever_perceived') is False for r in rows),
                absent_latest=sum(r.get('perceived') is False for r in rows),
                in_cone=sum(r.get('in_cone') is True for r in rows),
                in_radar=sum(r.get('in_radar') is True for r in rows),
                geometry_sample=sum('in_radar' in r for r in rows),
                believed_clear_true_blocked=len(overlaps),yaw_changed_clear_to_blocked=len(yaw_crosses),
                distance=average(r.get('distance') for r in rows),
                believed_margin=average(r['believed_margin'] for r in measured),
                true_margin=average(r['true_margin'] for r in measured),
                thrown_margin=average(r['thrown_margin'] for r in measured),
                mean_abs_yaw=average(abs(r['yaw_deg']) for r in rows if 'yaw_deg' in r),
                believed_pressure=sum(r['believed_pressure'] for r in measured),
                true_pressure=sum(r['true_pressure'] for r in measured),
                ratings={key:average(r.get(key) for r in rows) for key in ('passing','playmaking','vision')})


def diagnose(runs):
    totals = turnover_report(runs)
    def field(name):
        return [r for run in runs for r in run['diagnosis'][name]]
    intercepted, carries, tackles, shots, epochs = (field(k) for k in
        ('interceptions','carries','tackles','shots','quota_epochs'))
    possessions = [p for run in runs for p in run['possessions']]
    freezes = [p for p in possessions if p['freezes']]
    turnovers = sum(p['turnover'] for p in possessions)
    opportunity = [p for p in possessions if p['relevant_freezes']]
    stretch = Counter(row['event'] for row in field('stretches'))
    carry_ends = buckets(carries,lambda c:c['outcome'],lambda group:dict(
        n=len(group),median_plane=median(c['plane'] for c in group),minimum_plane=min(c['plane'] for c in group)))
    totals.update(interceptions=interception_report(intercepted),
                  interception_open=interception_report([r for r in intercepted if not r['restart']]),
                  carries=dict(total=len(carries),outcomes=carry_ends,within_3=sum(r['plane']<3 for r in carries),
                               within_1=sum(r['plane']<1 for r in carries),
                               stretch=stretch, shot_followups=Counter(r['shot_after_carry'] for r in carries if r.get('shot_after_carry')),
                               governed_goals=sum(line['goals_by_method'].get('carry',0)
                                   for run in runs for line in run['team_lines'])),
                  tackles=dict(overall=tackle_rates(tackles),
                               by_outcome=buckets(tackles,lambda r:r['outcome'],tackle_rates),
                               by_rating={key:buckets(tackles,lambda r:rating_band(r[key]),tackle_rates)
                                          for key in ('tackling','evasion','strength','balance')},
                               maneuvers=Counter(r['maneuver'] for r in tackles if r['maneuver']),
                               moves_near_failed=Counter(m for r in tackles if r['outcome'] in FAILURES for m in r['nearby_maneuvers'])),
                  archers=dict(defensive_possessions=len(possessions),arrows=sum(r['arrows'] for r in possessions),
                               hits=sum(r['hits'] for r in possessions),freezes=sum(r['freezes'] for r in possessions),
                               with_freeze=len(freezes),relevant_freeze_possessions=len(opportunity),
                               turnovers=turnovers,turnovers_soon=sum(p['turnover_after_freeze'] for p in possessions),
                               ppp_frozen=average(p['points'] for p in freezes),
                               ppp_unfrozen=average(p['points'] for p in possessions if not p['freezes']),
                               quota_epochs=len(epochs),max_charged=max(r['peak'] for r in epochs),
                               max_freezes=max(r['freezes'] for r in epochs),
                               at_arrow_limit=sum(r['peak']==15 for r in epochs),at_freeze_limit=sum(r['freezes']==5 for r in epochs)),
                  keepers=dict(total=shot_rates(shots),
                               by_band=buckets(shots,lambda r:r['band'],shot_rates),
                               by_aim_offset=buckets(shots,lambda r:'missing' if r['aim_offset'] is None
                                  else '<1 m' if r['aim_offset']<1 else '1–2 m' if r['aim_offset']<2 else '≥2 m',shot_rates)))
    return totals


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root',type=Path)
    args=parser.parse_args()
    root=args.root
    runs=[json.loads(gzip.decompress(path.read_bytes())) for path in sorted((root/'runs').glob('*.json.gz'))]
    expected={(i,seed) for i,n in enumerate((10,5,5,2,2,2,2,2)) for seed in range(1,n+1)}
    assert len(runs)==30 and {(r['pair'],r['seed']) for r in runs}==expected
    soak,_=summarize(root)
    outcomes=diagnose(runs)
    (root/'diagnosis.json').write_text(json.dumps(dict(soak=soak,diagnosis=outcomes),indent=2,ensure_ascii=False)+'\n')
    print(root/'diagnosis.json')


if __name__=='__main__':
    main()
