import sys, collections, json; ARGS=list(sys.argv)
import tend_check as T, pocket4_proto as X, player_gen_v1 as G
seeds=range(int(ARGS[1]),int(ARGS[2]))
rows=[]; FAIL=collections.Counter()
for sd in seeds:
    P=X.install(X.load_pocket()); P.SETTINGS.update(period_seconds=10, periods=4)
    over,ex,names=X.make_rosters(G.read_csv('Ala_Lady_Reds_input.csv'),G.read_csv(__import__('os').environ.get('B_CSV','Xenar_Dzaku_input.csv')),sd)
    try: r,log,el=X.run(P,over,ex,names,off=(),seed=sd,short=True)
    except Exception as e: print('crash',sd,repr(e)[:100]); continue
    hs=[l for l in X.S.rs_log if l[0]=='hunt']
    for e in log:
        if e['event'] in('opening_failed',): FAIL[(e['data'].get('reason'))]+=1
        if e['event']=='restart_awarded' and e['data'].get('reason') in('opening_fallback','quarter_start'): FAIL['award_'+e['data']['reason']]+=1
    for e in log:
        if e['event']=='hunt_timeout' and sd<=int(ARGS[1])+2: print('timeout',sd,e['data'])
    for l in hs: rows.append(dict(seed=sd,dur=l[1],period=l[2],method=l[3],owner=l[4],first=l[5]))
    st=X.S.rs_stats; rows.append(dict(seed=sd,timeouts=st['hunt_timeouts'],started=st['hunts_started'],live=st['hunts_live']))
json.dump(rows,open('hunt_%s_%s.json'%(ARGS[1],ARGS[2]),'w'))
h=[r for r in rows if 'dur' in r]; t=[r for r in rows if 'timeouts' in r]
print('hunts live',len(h),'started',sum(r['started'] for r in t),'timeouts',sum(r['timeouts'] for r in t))
d=sorted(r['dur'] for r in h); print('duration s: mean %.2f median %.2f p95 %.2f max %.2f'%(sum(d)/len(d),d[len(d)//2],d[int(.95*len(d))-1],d[-1]))
print('method',collections.Counter(r['method'] for r in h)); print('owner team',collections.Counter(r['owner'] for r in h)); print('period',collections.Counter(r['period'] for r in h))
print('first touch team',collections.Counter((r['first'] or '?')[0] for r in h)); print('owner==first-touch team',sum(1 for r in h if r['first'] and r['owner']==r['first'][0]),'/',len(h))

print('failures',dict(FAIL))
