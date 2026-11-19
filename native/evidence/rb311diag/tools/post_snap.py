"""RB-3.11 Part B: what happens after each scrimmage snap (log-only).
python3 post_snap.py <raw log json or json.gz> ..."""
import json, gzip, sys, collections
def load(p): return json.load(gzip.open(p,'rt')) if p.endswith('.gz') else json.load(open(p))
def team(pid): return pid.split(':')[0] if pid else None
def med(x):
    x=sorted(x); return round(x[len(x)//2],2) if x else None
out=collections.defaultdict(collections.Counter); tt=collections.defaultdict(list); rcv=collections.defaultdict(collections.Counter)
tk=collections.defaultdict(list); first_act=collections.defaultdict(list)
for p in sys.argv[1:]:
    log=load(p)['log']
    for i,r in enumerate(log):
        if r['event']!='scrimmage_formation': continue
        f=r['data']; kind=f['reason']; tm=f['team']; R=f['receiver']
        # find hold release
        j=i+1
        while j<len(log) and log[j]['event']!='snap_hold_released':
            if log[j]['event'] in ('restart_awarded',): break
            j+=1
        if j>=len(log) or log[j]['event']!='snap_hold_released': out[kind]['no_release']+=1; continue
        t0=log[j]['live_ms']; caught=None; res=None; first=None
        for k in range(j+1,len(log)):
            e=log[k]; ev=e['event']; d=e.get('data') or {}
            if ev=='control' and caught is None: caught=(d.get('player'), e['live_ms'])
            if ev=='release' and first is None and team(d.get('player'))==tm: first=(d.get('kind'), e['live_ms']-t0, d.get('player')==R)
            if ev=='tackle_count' and team(d.get('target'))==tm:
                if d.get('count_to',0)>=2 or kind!='first_tackle' and d.get('count_to')==1 and False: pass
                tk[kind].append(e['live_ms']-t0)
                if first is None: first=('tackled', e['live_ms']-t0, d.get('target')==R)
            if ev=='restart_awarded':
                res='award:'+d['reason']; break
            if ev=='possession' and d.get('team')!=tm:
                res='lost:'+(log[k-1]['event']); break
            if ev=='goal' or ev=='rb_goal': res='goal'; break
        out[kind][res]+=1
        if res: tt[kind].append(log[k]['live_ms']-t0)
        if caught: rcv[kind]['caught_by_receiver' if caught[0]==R else ('own_other' if team(caught[0])==tm else 'opponent')]+=1
        if first: first_act[kind].append(first)
for kind in out:
    n=sum(out[kind].values())
    print('==',kind,'n',n,'median live s to end',round((med(tt[kind]) or 0)/1000,2))
    print('  ends:',[(k,v,round(v/n*100,1)) for k,v in out[kind].most_common(9)])
    print('  first catch:',dict(rcv[kind]))
    fa=collections.Counter((a[0], a[2]) for a in first_act[kind])
    print('  first own action (kind, by receiver?):',fa.most_common(6))
    print('  median s to first own action:', round((med([a[1] for a in first_act[kind]]) or 0)/1000,2), ' median s to first tackle after snap:', round((med(tk[kind]) or 0)/1000,2), 'tackles', len(tk[kind]))
