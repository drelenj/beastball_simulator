import sys, collections, os; ARGS=list(sys.argv)
import tend_check as T, pocket4_proto as X
lead=ARGS[1]=='lead'; seeds=[int(x) for x in ARGS[2].split(',')]
tot=collections.Counter()
for sd in seeds:
    P=X.install(X.load_pocket())
    over,ex,names=X.make_rosters(T.G.read_csv('Ala_Lady_Reds_input.csv'),T.G.read_csv('Xenar_Dzaku_input.csv'),sd)
    r,log,el=X.run(P,over,ex,names,off=() if lead else ('arrowlead',),seed=sd,short=True)
    c=collections.Counter()
    for e in log:
        ev=e['event']
        if ev=='arrow_release': c['fired_'+e['data']['player'][0]]+=1
        elif ev=='arrow_miss': c['miss']+=1
        elif ev=='freeze' and e['data'].get('arrow') is not None: c['freeze']+=1
        elif ev=='inert_impact': c['inert']+=1
        elif ev=='arrow_geometry_impact': c['geom_blocked' if e['data'].get('blocked') else 'geom_ontarget']+=1
    tot.update(c); tot['games']+=1
print(os.environ.get('ARROW_V','stock'),'lead' if lead else 'engine',dict(tot),dict(X.S.arrow_stats),flush=True)
