import sys, json, collections; ARGS=list(sys.argv)
import tend_check as T, pocket4_proto as X
sd=int(ARGS[1]); short=ARGS[2]=='short'; off=tuple(ARGS[3].split(',')) if len(ARGS)>3 and ARGS[3] else ()
import traceback
try:
    r,log,m,names=T.go(off,sd,short)
except Exception:
    traceback.print_exc(); m=X.S.last
    print('CRASH', m.s.phase, m.s.now/1000.); print(dict(X.S.rs_stats)); sys.exit(1)
c=collections.Counter(e['event'] for e in log)
print(r['score'],r['result']['method'],'live_s',r.get('live_s'))
print('events',{k:c[k] for k in ('goal','tackle_count','restart_awarded','restart_release','scrimmage_set','restart_offside','hunt_start','hunt_live','hunt_timeout','opening_failed','boundary','possession_change','foul','discipline')})
print('stats',dict(X.S.rs_stats))
for l in X.S.rs_log[:40]: print('  ',l)
