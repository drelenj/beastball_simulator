import sys, json, pickle, collections; ARGS=list(sys.argv)
import tend_check as T, game_stats as GS, positional_tendencies_v1 as PT, pocket4_proto as X
seeds=[int(x) for x in ARGS[1].split(',')]; short=ARGS[2]=='short'; modes=ARGS[3].split(',')
V={'off':('tendencies',),'nodef':('tend_nodefadv',),'def':()}
out=[]
for sd in seeds:
    for k in modes:
        r,log,m,names=T.go(V[k],sd,short)
        pickle.dump(dict(log=log,names=names,mins={},score=r['score'],result=r['result']),open('/tmp/_g.pkl','wb'))
        d,P,Tm=GS.build('/tmp/_g.pkl')
        pos=collections.defaultdict(collections.Counter)
        for pid,c in P.items():
            if pid in names:
                for kk in ('points','goals','shots','tackles','interceptions','controls'): pos[names[pid]['position']][kk]+=c[kk]
        row=dict(mode=k,seed=sd,score=r['score'],pos={a:dict(b) for a,b in pos.items()},adv=dict(X.PT.S.adv_stat) if hasattr(X.PT,'S') else None)
        try: row['adv']={a:list(b) for a,b in X.S.adv_stat.items()}
        except Exception: pass
        out.append(row); print(k,sd,r['score'],'DEFpts',sum(pos[p]['points'] for p in('GRD','TRP')),'adv',row['adv'],flush=True)
json.dump(out,open('def_%s_%s.json'%(ARGS[1].replace(',','_'),ARGS[2]),'w'))
