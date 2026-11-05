from playwright.sync_api import sync_playwright
JS = """([cfg,pf]) => { const L=window.__lab; Object.assign(L.STD,cfg); const row={}; let tot=0,n=0;
  for (const k of ['straight','cut','juke','spin','stiffarm','truck']){ let sc=0,N=200; for(let s=1;s<=N;s++){ const w=L.runTrial(k,{seed:5000+s,lead:.55,defender:pf}); if(w.result.startsWith('SCORE')) sc++; } row[k]=Math.round(100*sc/N); tot+=row[k]; n++; } row.avg=Math.round(tot/n); return row; }"""
base=dict(reaction=.6,instinct=.5)
runs=[(f'J={j} pow{pw}',dict(j_blend_pow=pw),dict(base,judgment=j)) for pw in (1,3) for j in (0,.5,1.0)]
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); pg.goto("file:///home/claude/work/p4/lab/maneuver_lab.html"); pg.wait_for_timeout(300)
    for n,c,pf in runs:
        pg.reload(); pg.wait_for_timeout(100); print(f"{n:16}", pg.evaluate(JS,[c,pf]))
