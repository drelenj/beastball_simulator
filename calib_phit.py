import sys, os, json; ARGS=list(sys.argv); os.environ['PRISM']='1'; os.environ['PRISM_DRIVE']='1'
import tend_check as T, pocket4_proto as X
seeds=[int(x) for x in ARGS[1].split(',')]; rows=[]
for sd in seeds:
    P=X.install(X.load_pocket()); over,ex,names=X.make_rosters(T.G.read_csv('Ala_Lady_Reds_input.csv'),T.G.read_csv('Xenar_Dzaku_input.csv'),sd)
    r,log,el=X.run(P,over,ex,names,off=(),seed=sd,short=True)
    ph={a:(p,t) for a,p,t in X.S.prism_log.get('phit',[])}; out={a:'miss' for a in ph}
    for e in log:
        d=e['data']
        if e['event']=='arrow_geometry_impact' and d.get('arrow') in out: out[d['arrow']]='blocked' if d.get('blocked') else 'ontarget'
    for e in log:
        d=e['data']
        if e['event']=='freeze' and d.get('arrow') in out: out[d['arrow']]='freeze'
    rows+=[(ph[a][0],out[a]) for a in ph if ph[a][0] is not None]
rows.sort(); n=len(rows); print('n',n)
for q in range(5):
    chunk=rows[q*n//5:(q+1)*n//5]; ps=[x for x,_ in chunk]
    print('quintile %d: p_hat %.3f-%.3f mean %.3f | ontarget %.1f%% freeze %.1f%% blocked %.1f%%'%(q+1,min(ps),max(ps),sum(ps)/len(ps),100*sum(o in('ontarget','freeze') for _,o in chunk)/len(chunk),100*sum(o=='freeze' for _,o in chunk)/len(chunk),100*sum(o=='blocked' for _,o in chunk)/len(chunk)))
json.dump(rows,open('calib_phit.json','w'))
