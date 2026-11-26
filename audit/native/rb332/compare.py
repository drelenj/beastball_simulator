"""Paired game-block results; scores and percentages resample the same game in both arms."""
import argparse
from collections import Counter, defaultdict
import gzip
import json
from pathlib import Path
from random import Random
from statistics import mean, median, stdev

from .match import ARMS

CASES = {(p,s) for p,n in enumerate((10,5,5,2,2,2,2,2)) for s in range(1,n+1)}
TRIAL_ARMS = tuple(a for a in ARMS if a!='archive')
BOOTSTRAP = 1000


def read(path):
    return json.loads(gzip.decompress(path.read_bytes()))


def components(r):
    lines = r['team_lines']
    d = r['measures']
    counts = Counter(d['total'])
    points = tuple(r['score'][t] for t in 'AB')
    throws = sum(team['scoring_points_by_method'].get('throw_4',0) for team in lines)
    tackle = d['tackles']['overall']
    carry = d['carries']
    keeps = d['keepers']['total']
    attempts = sum(line['passes_attempted'] for line in lines)
    complete = sum(line['passes_completed'] for line in lines)
    possessions = sum(line['possessions'] for line in lines)
    attempt_ends = sum(line['possessions_ending_in_attempt'] for line in lines)
    planned = sum(e['data']['reason'] in ('planned_return','planned_out') for e in r['rotations'])
    exits = sum(e['data']['reason']=='energy_override' for e in r['rotations'])
    return dict(score=points,turnovers=counts, pass_pair=(complete,attempts),
                carries={k:v['n'] for k,v in carry['outcomes'].items()},
                carry_goals=carry['governed_goals'],stretches=carry['stretch'] | {
                    'end.'+reason:n for reason,n in carry.get('stretch_ends',{}).items()},
                tackle=(tackle['made'],tackle['n'],tackle['n']-tackle['targeted_actual_carrier']),
                holds=(d['ledger']['made'],d['ledger']['attempts']),
                keeper_pair=(keeps['saves'],keeps['faced']), on_target_pair=(keeps['saves'],keeps['on_target']),
                possession_pair=(attempt_ends,possessions), four_points=(throws,sum(points)),
                substitutions=(planned,exits),matchup=r['pair'])


def aggregate(records, turnover_kinds, carry_kinds, stretch_kinds):
    games = len(records)
    points = [p for r in records for p in r['score']]
    margins = [r['score'][1]-r['score'][0] for r in records]
    ala = [m for r,m in zip(records,margins) if r['matchup']==0]
    def total(k,index=None):
        return sum(r[k] if index is None else r[k][index] for r in records)
    def ratio(k):
        denominator = total(k,1)
        return total(k,0)/denominator if denominator else None
    result = dict(
        turnovers_per_team=sum(sum(r['turnovers'].values()) for r in records)/(2*games),
        near_goal_carries_per_team=sum(sum(r['carries'].values()) for r in records)/(2*games),
        median_team_score=median(points),possessions=total('possession_pair',1)/(2*games),
        attempt_share=ratio('possession_pair'),pass_completion=ratio('pass_pair'),
        passes_attempted_per_team=total('pass_pair',1)/(2*games),
        interceptions_per_team=sum(r['turnovers']['interception'] for r in records)/(2*games),
        boundaries_per_team=sum(r['turnovers']['out_of_bounds'] for r in records)/(2*games),
        carry_goals_per_team=total('carry_goals')/(2*games),
        tackle_commits_per_team=total('tackle',1)/(2*games),
        tackle_wrong_target_share=total('tackle',2)/total('tackle',1) if total('tackle',1) else None,
        tackle_episode_success=ratio('tackle'),tackle_hold_success=ratio('holds'),
        keeper_save_rate=ratio('keeper_pair'),keeper_save_on_target_rate=ratio('on_target_pair'),
        four_point_share=ratio('four_points'),median_absolute_margin=median(map(abs,margins)),
        within_five=sum(abs(m)<=5 for m in margins)/games,
        team_score_sd=stdev(points),ala_minus_garvian_margin=mean(ala) if ala else None,
        ala_margin_se=stdev(ala)/len(ala)**.5 if len(ala)>1 else None,
        ala_win_share=sum(m>0 for m in ala)/len(ala) if ala else None,
        planned_changes_per_team=total('substitutions',0)/(2*games),
        override_exits_per_team=total('substitutions',1)/(2*games))
    for kinds, key in ((turnover_kinds,'turnovers'),(carry_kinds,'carries'),(stretch_kinds,'stretches')):
        result.update({f'{key}.{kind}':sum(r[key].get(kind,0) for r in records)/(2*games) for kind in kinds})
    return result


def compare(root):
    rows = {arm:{(r['pair'],r['seed']):r for f in (root/arm).glob('*.json.gz') for r in (read(f),)}
            for arm in (*TRIAL_ARMS,'archive')}
    for arm in TRIAL_ARMS:
        for case,r in rows[arm].items():
            assert case in CASES and r['arm']==arm and r['status']=='final'
            assert r['invariants']=='passed' and r['restart_completion_ratio']==1
    common = sorted(set.intersection(*(set(rows[arm]) for arm in TRIAL_ARMS)))
    by_arm = {arm:[components(rows[arm][case]) for case in common] for arm in TRIAL_ARMS}
    all_records = [r for arm in TRIAL_ARMS for r in by_arm[arm]]
    kinds = tuple(sorted({k for r in all_records for k in r[group]})
                  for group in ('turnovers','carries','stretches'))
    kinds = (*kinds[:2], sorted(set(kinds[2]) | {'stretch_start','stretch_goal','stretch_end'}))
    result = dict(completed={a:len(r) for a,r in rows.items()},
                  common_cases=[dict(pair=p,seed=s,teams=rows['off'][p,s]['teams']) for p,s in common],
                  score_possession_margin_status='descriptive_not_judged',comparisons={})
    for arm in TRIAL_ARMS[1:]:
        if not common:
            continue
        off, on = by_arm['off'], by_arm[arm]
        for case in common:
            assert rows['off'][case]['planned_rate_scale']==rows[arm][case]['planned_rate_scale']
        off_est, on_est = (aggregate(group,*kinds) for group in (off,on))
        rng = Random(332)
        samples = defaultdict(list)
        # Preserve the number of games per matchup, keeping the seed pair intact.
        blocks = {p:[j for j,k in enumerate(common) if k[0]==p] for p in sorted({k[0] for k in common})}
        for _ in range(BOOTSTRAP):
            ids = [rng.choice(block) for block in blocks.values() for _ in range(len(block))]
            x,y = [aggregate([group[i] for i in ids],*kinds) for group in (off,on)]
            for key in x:
                if x[key] is not None and y[key] is not None:
                    samples[key].append(y[key]-x[key])
        metrics={}
        for k in off_est:
            old,new = off_est[k],on_est[k]
            metrics[k] = dict(off=old,on=new,delta=None if old is None or new is None else new-old,
                              se=stdev(samples[k]) if len(samples[k])>1 and len(common)>1 else None)
        result['comparisons'][arm]=dict(n=len(common),cases=common,metrics=metrics)
    archived_common = [case for case in common if case in rows['archive']]
    archive_flags=[flag for case in archived_common for flag in rows['archive'][case]['flags']]
    result['archive_clearance']=dict(n=len(archive_flags), measured=sum(r['arrival_margin'] is not None for r in archive_flags),
        flagged=sum(r['arrival_margin'] is not None and r['arrival_margin']<0 for r in archive_flags),
        cases=archived_common,expected=1020,complete=set(archived_common)==CASES)
    if result['archive_clearance']['complete']:
        assert len(archive_flags)==1020
    bounds = [r for case in common for r in rows['off'][case]['boundary']]
    by_source={}
    for key in sorted({r['kind'] for r in bounds}):
        group=[r for r in bounds if r['kind']==key]
        yaw=[abs(r['yaw_deg']) for r in group if 'yaw_deg' in r]
        distances=[r['believed_boundary_m'] for r in group if 'believed_boundary_m' in r]
        by_source[key]=dict(n=len(group),mean_abs_yaw=mean(yaw) if yaw else None,
            inside_aim=sum(r.get('aim_inside') is True for r in group),
            outside_aim=sum(r.get('aim_inside') is False for r in group),
            mean_believed_boundary_m=mean(distances) if distances else None,
            pressured=sum(r.get('believed_pressure') is True for r in group),
            pressure_sample=sum('believed_pressure' in r for r in group),
            loose_origins=Counter(r['loose_from'] for r in group if 'loose_from' in r),
            projected_landings=sum(r.get('first_ground_xy') is not None for r in group))
    result['boundary'] = by_source
    keepers=[r for case in common for r in rows['off'][case]['keeper_reach']]
    measured=[r for r in keepers if 'reachable' in r]
    reachable=[r for r in measured if r['reachable']]
    result['keeper_reach'] = dict(on_target=len(keepers),measured=len(measured),reachable=len(reachable),
         saves_reachable=sum(r['cause']=='save' for r in reachable),
         causes=Counter(r['cause'] for r in reachable),projection_mismatches=len(keepers)-len(measured),
         mean_flight_s=mean(r['flight_s'] for r in measured) if measured else None)
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root',type=Path)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    args.out.write_text(json.dumps(compare(args.root),indent=2)+'\n')


if __name__=='__main__':
    main()
