"""Render the smoke-check tables from immutable per-game evidence. No simulator imports."""
import argparse
from collections import Counter
import gzip
import json
from math import hypot
from pathlib import Path
from statistics import median

ARMS=('RB332','A0','A1','A2','A3','A4','A5','A5prime')
COMPARISONS=(*zip(ARMS[1:],ARMS),('A5','A0'))


def pct(n,d):
    return 100*n/d if d else None


def quantile(values,q):
    if not values:
        return None
    values=sorted(values)
    index=(len(values)-1)*q
    lo=int(index)
    return values[lo]+(index-lo)*(values[min(lo+1,len(values)-1)]-values[lo])


def measures(r):
    d=r['diagnosis']
    teams=r['box']['teams']
    def total(key):
        return sum(t[key] for t in teams)
    values={}
    def add(section,key,value):
        values[section,key]=value
    section='Possession losses and boundaries'
    for k in ('interception','out_of_bounds','fumble','strip','tackle','zone_violation','play_clock','opponent_control','major','turnover','held_ball','toss_timeout','score_restart'):
        add(section,k,d['total'].get(k,0)/2)
    add(section,'Targeted drops (events)',total('drops')/2)
    add(section,'Deflected ball went out',sum(q['kind']=='deflection' for q in r['boundary'])/2)
    counts=Counter()
    for b in r['boundary']:
        x,y=b['crossing']
        group='body' if b['kind']=='carrier' else 'ball'
        mouth='outside'
        if (x<=1 or x>=99) and abs(y-50)<=3:
            z=b.get('ball_z')
            mouth='unknown height' if z is None else 'inside' if hypot(y-50,z)+.1075<=3 and z>=.1075 else 'outside'
        counts[group,mouth]+=1
    for group in ('body','ball'):
        for mouth in ('inside','outside','unknown height'):
            add(section,f'Boundary events, {group}, {mouth}',counts[group,mouth]/2)
    section='Passing'
    attempts=total('passes_attempted')
    add(section,'Attempts',attempts/2)
    add(section,'Completions (%)',pct(total('passes_completed'),attempts))
    for lo,hi in ((0,.6),(.6,.7),(.7,.8),(.8,1.01)):
        players=[p for p in r['box']['players'] if lo<=r['ratings'][p['player']]<hi]
        targets=sum(p['targets'] for p in players)
        label=f'Catching {lo:.2f}–{min(hi,1):.2f}'
        add(section,label+' targets',targets/2)
        add(section,label+' targeted completion (%)',pct(sum(p['receptions'] for p in players),targets))
        drops=sum(p['drops'] for p in players)
        add(section,label+' drops',drops/2)
        add(section,label+' drop rate (%)',pct(drops,targets))
    for q in (.1,.5,.9):
        add(section,f'Speed P{int(q*100)} (m/s)',quantile([p['speed'] for p in r['passes']],q))
    for low,high in ((0,35),(35,50),(50,65),(65,float('inf'))):
        misses=[p['lateral_miss_m'] for p in r['passes'] if low<=p['speed']<high]
        label=f'{low}–{high} m/s'
        add(section,label+' releases',len(misses)/2)
        for q in (.5,.9):
            add(section,label+f' lateral miss P{int(q*100)} (m)',quantile(misses,q))
    section='Takedowns'
    t=d['tackles']['overall']
    add(section,'Commitments',t['n']/2)
    add(section,'Target was a non-carrier (%)',pct(t['n']-t['targeted_actual_carrier'],t['n']))
    for k in ('wrap_abort','wrap_retarget'):
        add(section,k,r['events'].get(k,0)/2)
    add(section,'All commitments ending in grounding (%)',pct(t['made'],t['n']))
    add(section,'Driving holds ending in grounding (%)',pct(d['ledger']['made'],d['ledger']['attempts']))
    section='Keeper'
    for band in (2,3,4):
        shots=d['keepers']['by_band'].get(str(band),{})
        add(section,f'{band}-point band saves/faced (%)',pct(shots.get('saves',0),shots.get('faced',0)))
    reached=[q for q in r['keeper'] if 'reachable' in q]
    add(section,'Classifiable on-target shots',len(reached)/2)
    add(section,'Inside release-time reach envelope (%)',pct(sum(q['reachable'] for q in reached),len(reached)))
    add(section,'Projection mismatches',(len(r['keeper'])-len(reached))/2)
    add(section,'No save commitment on reachable shot',sum(q.get('cause')=='no_commit' for q in reached)/2)
    add(section,'Reachable, touched without save',sum(q.get('cause')=='touch_without_save' for q in reached)/2)
    add(section,'Moving above set speed at release',r['unset']/2)
    add(section,'Unset incidence (% shots faced)',pct(r['unset'],d['keepers']['total']['faced']))
    section='Carries'
    c=d['carries']
    add(section,'Carry goals',c['governed_goals']/2)
    for k in ('stretch_start','stretch_goal'):
        add(section,k,c['stretch'].get(k,0)/2)
    add(section,'Near-goal stopped short',c['outcomes'].get('stopped_short',{}).get('n',0)/2)
    section='Score and possessions (descriptive only)'
    a,b=r['score']['A'],r['score']['B']
    add(section,'Garvian points',a)
    add(section,'Ala points',b)
    add(section,'Ala minus Garvian',b-a)
    add(section,'Points per team',(a+b)/2)
    for k in ('carry','throw_2','throw_3','throw_4','half_goal','full_goal_award','own'):
        add(section,'Points from '+k,sum(t['scoring_points_by_method'].get(k,0) for t in teams)/2)
    add(section,'Possessions',total('possessions')/2)
    add(section,'Possessions ending in attempt (%)',pct(total('possessions_ending_in_attempt'),total('possessions')))
    add('Runtime','CPU seconds/game',r['cpu_s'])
    return values


def render(root):
    runs={arm:json.loads(gzip.decompress((root/(arm+'.json.gz')).read_bytes())) for arm in ARMS}
    data={arm:measures(r) for arm,r in runs.items()}
    lines=['# RB-3.33 seed-1 paired check','',
        'Garvian Guardians vs Ala Apex. Counts are per team per game unless a team is named. Rates pool both teams. Differences of percentages are percentage points. An em dash means the denominator was zero.','']
    def table(header,items):
        lines.append('| '+' | '.join(header)+' |')
        lines.append('|'+'|'.join(['---']+['---:']*(len(header)-1))+'|')
        for label,row in items:
            lines.append('| '+label+' | '+' | '.join('—' if x is None else f'{x:.2f}' for x in row)+' |')
        lines.append('')
    for section in dict.fromkeys(k[0] for k in data['A0']):
        keys=[k for k in data['A0'] if k[0]==section]
        lines.extend(['## '+section,''])
        table(('Measure',*ARMS),[(k[1],[data[a][k] for a in ARMS]) for k in keys])
        table(('Difference',*(a+' − '+b for a,b in COMPARISONS)),[(k[1],[
            None if None in (data[a][k],data[b][k]) else data[a][k]-data[b][k] for a,b in COMPARISONS]) for k in keys])
    return '\n'.join(lines)+'\n'


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('evidence',type=Path)
    p.add_argument('out',type=Path)
    args=p.parse_args()
    args.out.write_text(render(args.evidence))
