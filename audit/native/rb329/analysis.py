"""Aggregate the rotation variants and diagnose possession swing from raw matches."""
import argparse
from collections import Counter, defaultdict
import csv
import gzip
import json
from math import sqrt
from pathlib import Path
from statistics import mean, median, pstdev, pvariance, stdev

from native.rulebook.fatigue_rotation import RHYTHMS


def read(path):
    return json.loads(gzip.decompress(path.read_bytes()))


def score_margin(row):
    return row['score']['B']-row['score']['A']


def moments(xs):
    return dict(n=len(xs), mean=mean(xs), median=median(xs), sd=pstdev(xs),
                min=min(xs), max=max(xs)) if xs else dict(n=0)


def distribution(holds):
    points = [p['points'] for p in holds]
    counts = Counter(str(p) if p<=5 else 'more' for p in points)
    endings = defaultdict(list)
    for p in holds:
        endings[p['end_reason']].append(p['points'])
    return dict(**moments(points), shares={str(k):counts[str(k)]/len(holds) for k in (*range(6),'more')},
                ends={k:dict(count=len(xs),share=len(xs)/len(holds),mean_points=mean(xs))
                      for k,xs in sorted(endings.items())})


def streaks(row):
    last, total, longest = None, 0, 0
    for _,team,points,_ in row['scores']:
        total = total+points if team==last else points
        last = team
        longest = max(total,longest)
    streak_count = {}
    for team in 'AB':
        run = count = 0
        for p in row['possessions']:
            if p['team']!=team:
                continue
            run = run+1 if p['points']>0 else 0
            count += run==3
        streak_count[team] = count
    return longest,streak_count


def rotation(rows):
    buckets = defaultdict(list)
    stints = []
    for row in rows:
        for p in row['participation']:
            key = p['role']+('_starter' if p['starter'] else '_bench')
            buckets[key].append(p['regulation_ms']/60000)
            if p['role']=='field':
                stints.extend(span/60000 for span in p['stints_ms'])
    p0=[score_margin(r) for r in rows if r['pair']==0]
    margins=[abs(score_margin(r)) for r in rows]
    tiers=Counter(s['data']['tier'] for row in rows for s in row['rotations'])
    return dict(games=len(rows), minutes={k:moments(v) for k,v in sorted(buckets.items())},
                stint_minutes=moments(stints), substitutions=dict(tiers),
                subs_per_team_match=sum(tiers.values())/(2*len(rows)),
                ala_garvian=dict(mean=mean(p0),se=stdev(p0)/sqrt(len(p0)) if len(p0)>1 else None,
                                ala_wins=sum(x>0 for x in p0),garvian_wins=sum(x<0 for x in p0),
                                ties=sum(x==0 for x in p0)) if p0 else {},
                team_scores=moments([p for row in rows for p in row['score'].values()]),
                possessions=moments([x['possessions'] for row in rows for x in row['team_lines']]),
                terminal_attempt_share=mean(x['possessions_ending_in_attempt']/x['possessions']
                                            for row in rows for x in row['team_lines'] if x['possessions']),
                abs_margin=moments(margins), within_five=mean(m<=5 for m in margins),
                ties=sum(m==0 for m in margins))


def covariance(xs,ys):
    a,b = mean(xs),mean(ys)
    return mean((x-a)*(y-b) for x,y in zip(xs,ys,strict=True))


def swing(rows):
    holds=[r for row in rows for r in row['possessions']]
    groups=defaultdict(list)
    for row in rows:
        groups[row['pair']].append(row)
    splits={}
    for pair, games in groups.items():
        teams=games[0]['teams']
        splits[pair]={name: distribution([p for row in games for p in row['possessions'] if p['team']==t])
                      for t,name in zip('AB',teams,strict=True)}
    margins=[score_margin(row) for row in rows]
    m=mean(margins)
    within=sum(sum((x-mean(xs))**2 for x in xs)
               for xs in ([score_margin(row) for row in gs] for gs in groups.values()))/len(rows)
    between=sum(len(gs)*(mean(score_margin(r) for r in gs)-m)**2 for gs in groups.values())/len(rows)
    nterms,qterms=[],[]
    by_method=Counter()
    method_rows=[]
    ovr_x,ovr_y=[],[]
    runs=[]
    for row in rows:
        a,b=(r['possessions'] for r in row['team_lines'])
        qa,qb=row['score']['A']/a,row['score']['B']/b
        nterms.append((b-a)*(qa+qb)/2)
        qterms.append((a+b)*(qb-qa)/2)
        assert abs(nterms[-1]+qterms[-1]-score_margin(row))<1e-9
        pointsA,pointsB=[Counter(r['scoring_points_by_method']) for r in row['team_lines']]
        by_method.update(pointsA)
        by_method.update(pointsB)
        pointsB.subtract(pointsA)
        method_rows.append(pointsB)
        runs.append(streaks(row))
    for match_rows in groups.values():
        a=match_rows[0]['starter_ovr']
        ovr_x.append(a['B']-a['A'])
        ovr_y.append(mean(score_margin(r) for r in match_rows))
    var=pvariance(margins)
    variance=dict(total=var,within_matchup=within,between_matchup=between,
                  count=pvariance(nterms),conversion=pvariance(qterms),
                  twice_covariance=2*covariance(nterms,qterms))
    assert abs(within+between-var)<1e-8
    by_method_margin={k:covariance([x[k] for x in method_rows],margins) for k in by_method}
    assert abs(sum(by_method_margin.values())-var)<1e-8
    return dict(possessions=distribution(holds), teams_by_matchup=splits,
                points_by_method={k:dict(points=v,share=v/sum(by_method.values())) for k,v in sorted(by_method.items())},
                points_outside_own_possession=sum(x['points_outside_own_possession']
                                                  for row in rows for x in row['team_lines']),
                variance=variance, margin_covariance_by_method=by_method_margin,
                streaks=dict(longest_run_points=moments([x for x,_ in runs]),
                             three_possession_runs=sum(sum(x.values()) for _,x in runs),
                             team_match_share_with_run=mean(v>0 for _,x in runs for v in x.values())),
                starter_ovr=dict(slope=covariance(ovr_x,ovr_y)/pvariance(ovr_x) if pvariance(ovr_x) else None,
                                 matchups=len(groups),
                                 points=[(groups[k][0]['teams'],x,y)
                                         for k,x,y in zip(groups,ovr_x,ovr_y,strict=True)]))


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('input',type=Path)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--partial',action='store_true')
    args=ap.parse_args()
    data={}
    for key in RHYTHMS:
        paths=(args.input/key).glob('*.json.gz')
        games=sorted(map(read,paths),key=lambda r:(r['pair'],r['seed']))
        if not args.partial:
            assert {(r['pair'],r['seed']) for r in games}=={
                (pair,seed) for pair in range(8)
                for seed in range(1,11 if pair==0 else 6 if pair in (1,2) else 3)}
        if games:
            assert all(r['status']=='final' and r['invariants']=='passed' and r['restart_completion_ratio']==1. for r in games)
            data[key]=games
    pooled=[row for games in data.values() for row in games]
    result={'variants':{k:dict(rotation=rotation(rows),swing=swing(rows)) for k,rows in data.items()},
            'pooled':dict(rotation=rotation(pooled),swing=swing(pooled))}
    args.out.mkdir(parents=True,exist_ok=True)
    (args.out/'summary.json').write_text(json.dumps(result,indent=2,ensure_ascii=False,sort_keys=True)+'\n')
    with (args.out/'matches.csv').open('w',newline='') as stream:
        writer=csv.writer(stream,lineterminator='\n')
        writer.writerow(('variant','pair','seed','team_A','team_B','score_A','score_B','margin_B_minus_A',
                         'possessions_A','possessions_B','rotations','longest_run_points',
                         'three_possession_runs_A','three_possession_runs_B','trace','state','cpu_s'))
        for row in pooled:
            count, runs = streaks(row)
            writer.writerow((row['variant'],row['pair'],row['seed'],*row['teams'],row['score']['A'],
                             row['score']['B'],score_margin(row),*(r['possessions'] for r in row['team_lines']),
                             len(row['rotations']),count,runs['A'],runs['B'],row['trace_hash'],row['state_hash'],row['cpu_s']))


if __name__=='__main__':
    main()
