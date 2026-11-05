import csv,json
from dataclasses import replace
from beastball_unified_locomotion_v30 import *
from pathlib import Path
root=Path(__file__).resolve().parent
rows=[]
for tier in ('developing','average','exceptional'):
 for role in ('field','keeper'):
  p=profile(tier,role)
  for speed in (0,10,20,30,40,44.704):
   for angle in (0,90):
    rows.append(assess(p,speed,Settings(turn_degrees=angle)))
for dt in (.0025,.005,.01):
 for speed in (10,20,40):
  rows.append(assess(profile('average','field'),speed,Settings(dt=dt,turn_degrees=90)))
with (root/'beastball_v30_results.csv').open('w',newline='') as f:
 writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
(root/'beastball_v30_results.json').write_text(json.dumps(rows,indent=2))
_,trace=assess(profile('average','field'),20,Settings(turn_degrees=90),trace=True)
with (root/'beastball_v30_trace.csv').open('w',newline='') as f:
 writer=csv.DictWriter(f,fieldnames=list(trace[0]));writer.writeheader();writer.writerows(trace)
from collections import Counter
print('trials',len(rows),'outcomes',dict(Counter('upright' if not r['grounded'] else r['reason'] for r in rows)))
for r in rows:
 if r['profile']=='field_average' and r['turn_degrees']==90 and r['dt_s']==.005 and r['initial_speed_m_s'] in (10,20,40,44.704):print(r)
