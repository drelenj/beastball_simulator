import sys; ARGS=list(sys.argv)
import tend_check as T, pocket4_proto as X, restarts_v1 as RS, collections
RS.SET.update(scrim_max_s=2.0, snap_max_s=3.0)
r,log,m,names=T.go((),int(ARGS[1]),True)
c=collections.Counter(e['event'] for e in log)
print(r['score'],'stats',dict(X.S.rs_stats))
for e in log:
    if e['event']=='restart_offside': print(e['live_ms']//1000,e['data'])
ph=collections.Counter((e['event'],e['phase']) for e in log if e['event'] in('arrow_draw','arrow_release','arrow_hit'))
print('arrow events by phase',dict(ph))
