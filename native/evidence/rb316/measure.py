"""RB-3.16 measurement from raw logs and result files (same definitions as the scoring analysis)."""
import json, gzip, math, sys, collections
K={'A:NBL24-07-11','B:NBL24-01-11'}
def load(p): return json.load(gzip.open(p,'rt')) if p.endswith('.gz') else json.load(open(p))
def row(raw, res):
    d=load(raw); log=d['log']; m=load(res)['metrics']; P=m['points']
    sc=(P['A']['play']+P['A']['penalty_awards'], P['B']['play']+P['B']['penalty_awards'])
    sh=collections.Counter(); meth=collections.Counter(); pas=collections.Counter(); near=0
    keepers=K|{p for e in log for p in [ (e.get('data') or {}).get('player') ] if p and False}
    for i,r in enumerate(log):
        dd=r.get('data') or {}
        if r['event']=='goal': meth[dd['method']]+=dd['points']
        if r['event']=='release' and dd.get('kind') in ('shot','pass'):
            tm=dd['player'].split(':')[0]; o='other'
            for e in log[i+1:i+90]:
                if e['event']=='goal': o='scored'; break
                if e['event']=='keeper_contact': o='keeper'; break
                if e['event']=='control':
                    p=e['data']['player']; o='own' if p.split(':')[0]==tm else ('keeper' if p.endswith('-11') or p.endswith('-K') else 'field')
                    if dd['kind']=='pass' and o in ('field','keeper') and math.hypot(e['ball'][0]-r['ball'][0],e['ball'][1]-r['ball'][1])<=3: near+=1
                    break
                if e['event'] in ('boundary','restart_awarded'): o='out/award'; break
            (sh if dd['kind']=='shot' else pas)[o]+=1
    ns=sum(sh.values()); npas=sum(pas.values())
    return dict(score=sc, play_points=(P['A']['play'],P['B']['play']), award_points=(P['A']['penalty_awards'],P['B']['penalty_awards']),
        points_by_method=dict(meth), possessions=(m['possessions']['A']['count'],m['possessions']['B']['count']),
        attempt_share=(round(m['possessions']['A']['share_ending_in_attempt'],3),round(m['possessions']['B']['share_ending_in_attempt'],3)),
        shots=ns, shot_shares={k:round(v/ns*100,1) for k,v in sh.most_common()} if ns else {},
        passes=npas, pass_intercepted_pct=round((pas['field']+pas['keeper'])/max(npas,1)*100,1), intercepted_within_3m=near,
        tackles=sum(1 for e in log if e['event']=='tackle_count'),
        carries=(m['carry_attempts']['A']['attempts']+m['carry_attempts']['B']['attempts'] if 'attempts' in m['carry_attempts']['A'] else None, m['carry_attempts']['A']['goals']+m['carry_attempts']['B']['goals']))
out={}
base=sys.argv[1]
for b,s in (('real',1),('real',3),('real',5),('control',1)):
    out[f'{b}{s}']=row(f'{base}/{b}/raw-{b}-seed{s:02d}.json'+('' if not base.endswith('corrected') else '.gz'), f'{base}/{b}/{b}-seed{s:02d}.json')
print(json.dumps(out,indent=1))
