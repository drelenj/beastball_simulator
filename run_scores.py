import sys, os, json, subprocess, collections
from concurrent.futures import ThreadPoolExecutor
H='/home/claude/work/p4'
RUN=r'''
import sys, os, json; os.chdir(%r); sys.path.insert(0,%r); os.environ['PRISM_I']='1'
import tend_check as T, pocket4_proto as X, drill_score_v0 as DS
seed=int(os.environ['SEED']); P=X.install(X.load_pocket())
over,ex,names=X.make_rosters(T.G.read_csv('Ala_Lady_Reds_input.csv'),T.G.read_csv('Xenar_Dzaku_input.csv'),seed)
r,log,el=X.run(P,over,ex,names,off=(),seed=seed,short=True)
print('RESULT'+json.dumps(dict(engine=r['score'],s=DS.score(log))))
'''%(H,H)
def one(sd):
    o=subprocess.run([sys.executable,'-c',RUN],env=dict(os.environ,SEED=str(sd)),capture_output=True,text=True,timeout=1800)
    l=[x for x in o.stdout.splitlines() if x.startswith('RESULT')]
    return sd,(json.loads(l[0][6:]) if l else {'err':o.stderr[-300:]})
seeds=list(range(1,13))
with ThreadPoolExecutor(4) as ex: res=list(ex.map(one,seeds))
json.dump(res,open('scores_12.json','w'))
tot=collections.Counter()
for sd,d in res:
    if 'err' in d: print('ERR',sd,d['err']); continue
    for t in 'AB':
        for k,v in d['s'][t].items():
            if isinstance(v,(int,float)): tot[k]+=v
        for b,n in d['s'][t].get('attempts_by_band',{}).items(): tot['att_'+b]+=n
        for b,n in d['s'][t].get('goals_by_band',{}).items(): tot['gl_'+b]+=n
n=len(res)*2
print('team-games',n)
for k in ('goals','points_flat','carry_goals','release_goals','shot_attempts','turnover','minor_fouls','major_fouls','minor_count_cost','overlay_points','overlay_awards_half','overlay_awards_full','overlay_turnover','distance_progressed_m'):
    print('%-24s total %8.1f  per team-game %6.2f'%(k,tot[k],tot[k]/n))
print('shot success %.3f'%(tot['release_goals']/max(1,tot['shot_attempts'])))
for b in ('0-5','5-10','10-15','15-20','20-30','30-99'): print('band',b,'att',tot['att_'+b],'goals',tot['gl_'+b])
