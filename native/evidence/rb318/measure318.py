"""RB-3.18 verification measurement from raw logs + result files: scores, possessions, points by method, carry/move events."""
import json, sys, collections, statistics as st, os
R=sys.argv[1]
EV=('stretch_start','stretch_goal','stiff_arm','stiff_arm_effect','truck','truck_broken','truck_stopped','handoff_complete','handoff_fumble','block_engaged','tackle_count','strip')
out={}
for cfg in ('rule','on'):
    rows={}
    for b,s in (('real',1),('real',3),('real',5),('control',1)):
        d=json.load(open(f'{R}/{cfg}/{b}/raw-{b}-seed{s:02d}.json')); m=json.load(open(f'{R}/{cfg}/{b}/{b}-seed{s:02d}.json'))['metrics']
        log=d['log']; P=m['points']; meth=collections.Counter(); rc=0
        for e in log:
            if e['event']=='goal':
                g=e['data']; meth[g['method']]+=g['points']; rc+=1 if g.get('release_carry') else 0
        ev=collections.Counter(e['event'] for e in log if e['event'] in EV)
        rows[f'{b}{s}']=dict(score=[P[t]['play']+P[t]['penalty_awards'] for t in 'AB'], possessions=[m['possessions'][t]['count'] for t in 'AB'],
            attempt_share=[round(m['possessions'][t]['share_ending_in_attempt'],3) for t in 'AB'], points_by_method=dict(meth), release_carry_goals=rc,
            carry_goals=m['carry_attempts']['A']['goals']+m['carry_attempts']['B']['goals'], events=dict(ev))
    real=[x for k,v in rows.items() if k.startswith('real') for x in v['score']]
    rows['_real_team_score_median']=st.median(real); rows['_real_possessions_mean']=round(st.mean([x for k,v in rows.items() if k.startswith('real') for x in v['possessions']]),1)
    out[cfg]=rows
print(json.dumps(out,indent=1))
