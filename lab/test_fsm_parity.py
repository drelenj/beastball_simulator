import json, random, sys
sys.path.insert(0, '/home/claude/work/p4')
import pose_maneuvers_v0 as M
from playwright.sync_api import sync_playwright
r = random.Random(5); streams = []
for trial in range(150):
    start = r.choice(M.POSES); cmds = []
    for _ in range(50):
        x = r.random()
        if x < .25: cmds.append(('man', r.choice(list(M.ALLOWED)), r.randint(1, 140)))
        elif x < .45: cmds.append(('pose', r.choice(M.POSES), r.randint(1, 140)))
        elif x < .55: cmds.append(('contact', None, r.randint(1, 140)))
        elif x < .6: cmds.append(('pin', r.random() < .5, r.randint(1, 140)))
        else: cmds.append(('wait', None, r.randint(1, 140)))
    streams.append((start, cmds))
def py_run(start, cmds):
    c = M.Carrier(start)
    for k, a, ms in cmds:
        if k == 'man': c.start_maneuver(a)
        elif k == 'pose': c.request_pose(a)
        elif k == 'contact': c.on_contact()
        elif k == 'pin': c.pinned = a
        c.step(ms)
    return [list(e) for e in c.log], c.pose
JS = """(streams) => { const F = window.__lab.PoseFSM, out = [];
  const nameMap = {stiffarm:'stiffarm'};
  for (const [start, cmds] of streams){ const c = new F(start);
    for (const [k,a,ms] of cmds){ if(k==='man') c.start_maneuver(a); else if(k==='pose') c.request_pose(a); else if(k==='contact') c.on_contact(); else if(k==='pin') c.pinned=a; c.step(ms); }
    out.push([c.log, c.pose]); }
  return out; }"""
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(); pg.goto("file:///home/claude/work/p4/lab/maneuver_lab.html"); pg.wait_for_timeout(300)
    js = pg.evaluate(JS, streams)
bad = 0
for (start, cmds), (jlog, jpose) in zip(streams, js):
    plog, ppose = py_run(start, cmds)
    jl = [[e[0], e[1], e[2]] for e in jlog]
    if jl != plog or jpose != ppose: bad += 1
print('streams', len(streams), 'mismatches', bad)
