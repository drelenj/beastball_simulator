import sys, os, json, statistics as st; ARGS=list(sys.argv)
os.environ['PRISM']='1'
import tend_check as T, pocket4_proto as X
seeds=[int(x) for x in ARGS[1].split(',')]; short=(len(ARGS)<3 or ARGS[2]!='full'); tag=ARGS[3] if len(ARGS)>3 else 'run'
rel=[]; samp=[]; ev={'fired':0,'freeze':0,'freeze_carrier':0,'ontarget':0,'blocked':0,'miss':0,'pts':0}
for sd in seeds:
    P=X.install(X.load_pocket())
    over,ex,names=X.make_rosters(T.G.read_csv('Ala_Lady_Reds_input.csv'),T.G.read_csv('Xenar_Dzaku_input.csv'),sd)
    r,log,el=X.run(P,over,ex,names,off=(),seed=sd,short=short)
    for e in log:
        k=e['event']; d=e['data']
        if k=='arrow_release': ev['fired']+=1
        elif k=='freeze' and d.get('arrow') is not None: ev['freeze']+=1; ev['freeze_carrier']+=1 if d.get('was_carrier') else 0
        elif k=='arrow_geometry_impact': ev['blocked' if d.get('blocked') else 'ontarget']+=1
        elif k=='arrow_miss': ev['miss']+=1
    ev['pts']+=sum(r['score'].values())
    rel+=X.S.prism_log['release']; samp+=X.S.prism_log['sample']
def m(v): v=[x for x in v if x is not None]; return round(st.mean(v),2) if v else None
def med(v): v=[x for x in v if x is not None]; return round(st.median(v),2) if v else None
names=list(rel[0]['v'].keys()) if rel else []
omni=[r.get('miss_omni') for r in rel]
out=dict(tag=tag,games=len(seeds),events=ev,releases=len(rel),omni_miss_median=med(omni),omni_hit=sum(1 for r in rel if r.get('miss_omni_hit')),variants={})
for n in names:
    rs=[r['v'][n] for r in rel if r['v'].get(n)]
    ss=[s['per'][n] for s in samp if s.get('per',{}).get(n)]
    out['variants'][n]=dict(release_pos_err_median=med([x['pos_err'] for x in rs]),release_vel_err_mean=m([x['vel_err'] for x in rs]),release_vel_err_median=med([x['vel_err'] for x in rs]),
        aim_div_median=med([x.get('aim_divergence') for x in rs]),miss_belief_median=med([x.get('miss_belief') for x in rs]),would_hit=sum(1 for x in rs if x.get('miss_belief_hit')),
        sample_pos_err=m([a for a,b in ss]),sample_vel_err=m([b for a,b in ss]),n_samples=len(ss))
print(json.dumps(out,indent=1)); json.dump(out,open(f'prism_{tag}.json','w')); json.dump(rel,open(f'prism_{tag}_rel.json','w'))
