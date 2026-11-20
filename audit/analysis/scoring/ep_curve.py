"""Expected points of the rest of the possession, by distance to the attacked goal at the moment of control.
EP(d) = mean points the controlling team scores before the possession ends. Built from raw logs of one build."""
import sys, json, collections, statistics as st
sys.path.insert(0,'/home/claude/wt310/native/evidence/rb311diag/tools')
from offense_diagnosis import Match
S='/tmp/claude-0/-home-claude/65ce685a-b94d-53f8-bbf7-8c3464c490cd/scratchpad/ep/'
bins=[(0,10),(10,20),(20,30),(30,40),(40,50),(50,60),(60,70),(70,80),(80,100)]
res={}
for b in sys.argv[1:]:
    acc=collections.defaultdict(list)
    for seed in (1,3,5):
        m=Match(S+b+'/soak','/nonexistent','real',seed); log=m.log
        # possession boundaries: team of control changes; points from goal events
        ctl=[(i,e['data']['player'].split(':')[0]) for i,e in enumerate(log) if e['event']=='control']
        goals=[(i,e['data']['team'],e['data']['points']) for i,e in enumerate(log) if e['event']=='goal']
        # segment possessions by consecutive controls of same team (a goal ends it)
        for k,(i,tm) in enumerate(ctl):
            # end of this team's possession: next control by other team, or a goal
            j=next((ii for ii,t in ctl[k+1:] if t!=tm), len(log))
            pts=sum(p for gi,gt,p in goals if i<gi<=j and gt==tm)
            # stop counting after first goal by anyone in window (possession ends at a score)
            first_goal=next((gi for gi,gt,p in goals if i<gi<=j),None)
            if first_goal is not None: pts=sum(p for gi,gt,p in goals if gi==first_goal and gt==tm)
            d=m.gdist(i,tm,log[i]['ball'][0],log[i]['ball'][1])
            for lo,hi in bins:
                if lo<=d<hi: acc[(lo,hi)].append(pts); break
    res[b]={f'{lo}-{hi}':(round(st.mean(v),3),len(v)) for (lo,hi),v in sorted(acc.items())}
print(json.dumps(res,indent=1))
