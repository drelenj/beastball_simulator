import sys, pickle; ARGS=list(sys.argv)
import tend_check as T, pocket4_proto as X
sd=int(ARGS[1]); tag=ARGS[2]
r,log,m,names=T.go((),sd,False)
M=X.S.last
pickle.dump(dict(log=log,names=names,mins=dict(M.p4.mins),score=r['score'],result=r['result'],stats=dict(M.p4.stats),rot_log=list(M.p4.rot_log),rs=dict(X.S.rs_stats),rs_log=list(X.S.rs_log),adv=dict(X.S.adv_stat)),open('game_%s.pkl'%tag,'wb'))
print('DONE',r['score'],r['result'])
print(X.rotation_report(M,names))
print('restarts',dict(X.S.rs_stats)); print('advance share',{k:(v[1]/max(v[0],1)) for k,v in X.S.adv_stat.items()})
