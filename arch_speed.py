import sys, collections; ARGS=list(sys.argv)
import tend_check as T, pocket4_proto as X
V=float(ARGS[1]); seeds=[int(x) for x in ARGS[2].split(',')]
tot=collections.Counter()
import types
def patch(P):
    Match=P.CORE.match.Match; o=Match.arrow_decisions
    def ad(self):
        if V>0:
            self.cfg['pocket']['arrow_limit']=V; self.e.pocket['arrow_limit']=V
            for p in self.s.players.values():
                if p.role=='archer': p.a.archery_release_speed=V
        return o(self)
    Match.arrow_decisions=ad
for sd in seeds:
    P=X.install(X.load_pocket()); patch(P)
    over,ex,names=X.make_rosters(T.G.read_csv('Ala_Lady_Reds_input.csv'),T.G.read_csv('Xenar_Dzaku_input.csv'),sd)
    r,log,el=X.run(P,over,ex,names,off=(),seed=sd,short=True)
    c=collections.Counter()
    for e in log:
        if e['event']=='arrow_release': c['fired_'+e['data']['player'][0]]+=1
        elif e['event']=='arrow_miss': c['miss']+=1
        elif e['event']=='freeze' and e['data'].get('arrow') is not None: c['freeze']+=1
        elif e['event']=='inert_impact': c['inert_'+str(e['data'].get('reason') or 'cond')]+=1
        elif e['event']=='arrow_geometry_impact': c['geom_blocked' if e['data'].get('blocked') else 'geom_ontarget']+=1
        elif e['event']=='foul' and e['data'].get('reason') in('arrow_speed','early_arrow','archer_lane'): c['arrow_foul']+=1
    tot.update(c); tot['score']+=sum(r['score'].values()); tot['games']+=1
print('arrow speed',V,dict(tot),flush=True)
