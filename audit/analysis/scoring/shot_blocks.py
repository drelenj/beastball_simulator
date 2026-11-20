"""Where field defenders take shots: before the goal (block/intercept) or after (rebound)."""
import sys, math, collections, statistics as st
sys.path.insert(0,'/home/claude/wt310/native/evidence/rb311diag/tools')
from offense_diagnosis import Match
S='/tmp/claude-0/-home-claude/65ce685a-b94d-53f8-bbf7-8c3464c490cd/scratchpad/ep/'
for b in ('r310','r312','r313'):
    frac=[]; ms=[]; spd=[]; spd_sc=[]; hz=[]
    for seed in (1,3,5):
        m=Match(S+b+'/soak','/nonexistent','real',seed); log=m.log
        for i,r in enumerate(log):
            d=r.get('data') or {}
            if r['event']=='release' and d.get('kind')=='shot':
                tm=d['player'].split(':')[0]; g=m.gdist(i,tm,r['ball'][0],r['ball'][1]); v=d['velocity']; sp=math.hypot(*v[:2])
                for e in log[i+1:i+90]:
                    if e['event']=='goal': spd_sc.append(sp); break
                    if e['event'] in ('keeper_contact','boundary','restart_awarded'): break
                    if e['event']=='control':
                        if e['data']['player'].split(':')[0]!=tm:
                            dd=math.hypot(e['ball'][0]-r['ball'][0],e['ball'][1]-r['ball'][1]); frac.append(dd/max(g,1e-3)); ms.append(e['live_ms']-r['live_ms']); spd.append(sp); hz.append(e['ball'][2])
                        break
    q=lambda x:[round(v,2) for v in st.quantiles(x,n=4)]
    print(b,'defence controls',len(frac),'| fraction of shot distance travelled at control: quartiles',q(frac),'| share before goal line (<0.95):',round(sum(f<0.95 for f in frac)/len(frac),2),'| ms after release quartiles',q(ms),'| ball height at control quartiles',q(hz),'| shot speed (blocked) median',round(st.median(spd),1),'(scored) median',round(st.median(spd_sc),1) if spd_sc else None)
