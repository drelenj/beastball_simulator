import sys, collections, os, json; ARGS=list(sys.argv)
import tend_check as T, pocket4_proto as X
tag=ARGS[1]; seeds=[int(x) for x in ARGS[2].split(',')]; short=(len(ARGS)<4 or ARGS[3]!='full')
tot=collections.Counter(); rng=[]; vict=collections.Counter(); tgt=collections.Counter()
for sd in seeds:
    P=X.install(X.load_pocket())
    over,ex,names=X.make_rosters(T.G.read_csv('Ala_Lady_Reds_input.csv'),T.G.read_csv('Xenar_Dzaku_input.csv'),sd)
    r,log,el=X.run(P,over,ex,names,off=(),seed=sd,short=short)
    arrow_team={}; 
    for e in log:
        ev=e['event']; d=e['data']
        if ev=='arrow_release':
            tm=d['player'][0]; arrow_team[d['arrow']]=tm; tot['fired_'+tm]+=1; rng.append(d.get('range',0)); tgt[names[d['target']]['position']]+=1
            tot['fired_at_carrier' if False else 'fired']+=1
        elif ev=='arrow_miss': tot['miss']+=1
        elif ev=='freeze' and d.get('arrow') is not None:
            tot['freeze']+=1; tot['freeze_carrier' if d.get('was_carrier') else 'freeze_noncarrier']+=1; vict[names[d['player']]['position']]+=1
        elif ev=='inert_impact': tot['inert']+=1
        elif ev=='freeze_cap': tot['capped']+=1
        elif ev=='arrow_geometry_impact': tot['blocked' if d.get('blocked') else 'ontarget']+=1
        elif ev=='tackle_count': tot['tackles']+=1
        elif ev=='possession_change': tot['poss_change']+=1
        elif ev=='goal': tot['goals_'+d['team']]+=1
    for k_,v_ in getattr(X.S,'prism_stats',{}).items(): tot['prism_'+k_]+=v_
    for rec_ in getattr(X.S,'prism_log',{}).get('release',[]):
        r_=(rec_.get('v') or {}).get('lsq_.4')
        if r_ and 'miss_belief' in r_: tot['aim_n']+=1; tot['aim_hit']+=bool(r_.get('miss_belief_hit')); tot['aim_dist_sum']+=r_['miss_belief']
    for k_,v_ in getattr(X.S,'fstats',{}).items(): tot['f_'+k_]+=v_
    for tm_,(aid_,pr_) in getattr(X.S,'prism',{}).items():
        for k_,v_ in pr_.stats.items(): tot['pr_'+k_]+=v_
    for k_,v_ in getattr(X.S,'fz_diag',{}).items(): tot['fzd_'+k_]+=v_
    for k_,v_ in r.get('turnover_causes',{}).items(): tot['to_'+k_]+=v_
    tot['poss_elapsed_sum']+=r.get('mean_possession_elapsed_s',0) or 0; tot['poss_live_sum']+=r.get('mean_completed_possession_live_s',0) or 0
    tot['pts_A']+=r['score']['A']; tot['pts_B']+=r['score']['B']; tot['games']+=1
out=dict(tag=tag,tot=dict(tot),mean_range=round(sum(rng)/max(len(rng),1),1),victim_pos=dict(vict.most_common(6)),target_pos=dict(tgt.most_common(6)))
print(json.dumps(out),flush=True); open(f'plat_{tag}.json','w').write(json.dumps(out))
