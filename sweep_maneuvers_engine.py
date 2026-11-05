import sys, os, json, collections
os.chdir('/home/claude/work/p4'); sys.path.insert(0,'/home/claude/work/p4')
seeds=[int(x) for x in sys.argv[1].split(',')]
import tend_check as T, pocket4_proto as X
tot=collections.Counter()
for sd in seeds:
    P=X.install(X.load_pocket())
    over,ex,names=X.make_rosters(T.G.read_csv('Ala_Lady_Reds_input.csv'),T.G.read_csv('Xenar_Dzaku_input.csv'),sd)
    r,log,el=X.run(P,over,ex,names,off=(),seed=sd,short=True)
    ev=collections.Counter(e['event'] for e in log)
    tot['games']+=1; tot['goals']+=r['score']['A']+r['score']['B']; tot['tackles']+=ev['tackle_count']; tot['strips']+=ev['strip']; tot['poss']+=ev['possession_change']
    for k,v in (getattr(X.S,'pm',None).stats.items() if getattr(X.S,'pm',None) else []): tot[k]+=v
print(os.environ.get('PM_NUDGE'), json.dumps({k:v for k,v in sorted(tot.items()) if not k.startswith('pose_')}))
