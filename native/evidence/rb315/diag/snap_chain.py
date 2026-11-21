"""RB-3.11 Part B: snap first touch and the chain to the next tackle (log-only)."""
import json, gzip, sys, collections
def load(p): return json.load(gzip.open(p,'rt')) if p.endswith('.gz') else json.load(open(p))
def team(pid): return pid.split(':')[0] if pid else None
def med(x):
    x=sorted(x); return round(x[len(x)//2],2) if x else None
first=collections.Counter(); trav=collections.defaultdict(list); lat=collections.defaultdict(list)
chain=collections.Counter(); tk_who=collections.Counter(); tk_dx=[]; tk_t=[]; npass=collections.Counter(); back=collections.Counter()
for p in sys.argv[1:]:
    log=load(p)['log']
    for i,r in enumerate(log):
        if r['event']!='scrimmage_formation': continue
        f=r['data']; tm=f['team']; R=f['receiver']; S=f['snapper']; spot=f['spot']; kind=f['reason']
        rs=f['receiver_spot']; sign=1 if rs[0]<spot[0] else -1   # +1: attack toward +x (receiver behind = smaller x)
        k=i+1; rel=None
        while k<len(log) and log[k]['event'] not in ('restart_release',): k+=1
        if k>=len(log): continue
        t0=log[k]['live_ms']
        for q in range(k+1,min(len(log),k+60)):
            e=log[q]
            if e['event']=='control':
                pid=e['data']['player']; who='receiver' if pid==R else ('snapper' if pid==S else ('own_other' if team(pid)==tm else 'opponent'))
                first[(kind=='period_start',who)]+=1
                bx,by=e['ball'][0],e['ball'][1]; trav[who].append(abs(bx-spot[0])+0.0); lat[who].append(abs(by-50)); break
        if kind!='first_tackle': continue
        passes=0; res=None
        for q in range(k+1,len(log)):
            e=log[q]; ev=e['event']; d=e.get('data') or {}
            if ev=='release' and team(d.get('player'))==tm and d.get('kind')=='pass':
                passes+=1; vx=d['velocity'][0]; back['forward' if vx*sign>0 else 'backward_or_level']+=1
            if ev=='tackle_count' and team(d.get('target'))==tm:
                tg=d['target']; tk_who['snapper' if tg==S else ('receiver' if tg==R else 'other')]+=1
                tk_dx.append(round((e['ball'][0]-spot[0])*sign,1)); tk_t.append(e['live_ms']-t0); res='second_tackle'; break
            if ev=='restart_awarded' or (ev=='possession' and d.get('team')!=tm) or ev=='goal': res=ev; break
        chain[res]+=1; npass[passes]+=1
print('first control after release (is_snap40, who):', first.most_common())
for w in trav: print(f'  {w}: median ball travel to first touch {med(trav[w])} m, median lateral offset {med(lat[w])} m, n={len(trav[w])}')
print('first-tackle scrimmages -> next:', chain.most_common())
print('  passes before that:', sorted(npass.items()))
print('  pass direction after snap:', dict(back))
print('  second tackle on:', dict(tk_who), ' median gain from line (m, + = forward):', med(tk_dx), ' median s after snap:', round(med(tk_t)/1000,2))
import statistics
print('  gain quartiles:', [round(x,1) for x in statistics.quantiles(tk_dx,n=4)])
