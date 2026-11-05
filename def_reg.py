import sys, json, pickle, collections; ARGS=list(sys.argv)
import tend_check as T
sd=int(ARGS[1]); mode=ARGS[2]; V={'off':('tendencies',),'nodef':('tend_nodefadv',),'def':()}
import traceback
try:
    r,log,m,names=T.go(V[mode],sd,False)
except Exception:
    traceback.print_exc(); 
    import pocket4_proto as X
    m=X.S.last; print('CRASH state: phase',getattr(m,'s',None) and m.s.phase, 'now', m.s.now/1000., 'score', m.s.score if hasattr(m.s,'score') else None); sys.exit(1)
c=collections.Counter(e['event'] for e in log)
print(mode,sd,r['score'],r['result'],{a:c[a] for a in ('control','possession_change','goal','release','tackle_count','restart_awarded','keeper_confront','foul','discipline','boundary')},flush=True)
pickle.dump(dict(log=log,names=names,mins={},score=r['score'],result=r['result']),open('dreg/%s_%d.pkl'%(mode,sd),'wb'))
