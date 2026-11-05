from playwright.sync_api import sync_playwright
import sys
JS = """([cfg,pf]) => { const L=window.__lab; Object.assign(L.STD,cfg); const row={};
  for (const k of ['straight','cut','juke','spin','stiffarm','truck']){ let sc=0,N=200; for(let s=1;s<=N;s++){ const w=L.runTrial(k,{seed:2000+s,lead:.55,defender:pf}); if(w.result.startsWith('SCORE')) sc++; } row[k]=Math.round(100*sc/N); } return row; }"""
base=dict(reaction=.6,instinct=.5,vision=.6,awareness=.5,clarity=.6,focus=.8,anticipation=.5)
runs=[("PRISM off",dict(prism_def=0),base),("PRISM on, mid",dict(),base)]
for r in ['reaction','instinct','vision','awareness','clarity','focus','anticipation']:
    for v in (.1,.95): runs.append((f"{r}={v}",dict(),dict(base,**{r:v})))
runs.append(("all .1",dict(),{k:.1 for k in base})); runs.append(("all .95",dict(),{k:.95 for k in base}))
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); pg.goto("file:///home/claude/work/p4/lab/maneuver_lab.html"); pg.wait_for_timeout(300)
    for name,cfg,pf in runs:
        pg.reload(); pg.wait_for_timeout(100); print(f"{name:18}", pg.evaluate(JS,[cfg,pf]))
