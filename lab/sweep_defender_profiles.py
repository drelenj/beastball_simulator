import json
from playwright.sync_api import sync_playwright
JS = """
() => { const L = window.__lab, kinds=['straight','cut','juke','spin','stiffarm','truck'], profs={weak:{reaction:.2,instinct:.2},default:{reaction:.6,instinct:.5},elite:{reaction:.95,instinct:1}}, leads=[.25,.4,.55,.7,.9], out={};
 for (const [pn,pd] of Object.entries(profs)){ out[pn]={};
  for (const k of kinds){ let best=null;
   for (const lead of leads){ let sc=0,n=300; for(let s=1;s<=n;s++){ const w=L.runTrial(k,{seed:s,lead,defender:pd}); if(w.result && w.result.startsWith('SCORE')) sc++; }
    if(!best||sc>best.sc) best={sc,lead}; }
   out[pn][k]={score_pct:+(100*best.sc/300).toFixed(0),best_lead:best.lead}; } }
 // starting pose cost: juke/spin from loaded vs tucked, default defender
 out.startpose={}; for (const k of ['juke','spin','stiffarm','truck']) for (const sp of ['tucked','loaded','braced']){ let sc=0,n=300; for(let s=1;s<=n;s++){ const w=L.runTrial(k,{seed:s,lead:.7,defender:profs.default,startPose:sp}); if(w.result&&w.result.startsWith('SCORE')) sc++; } out.startpose[k+'_'+sp]=+(100*sc/n).toFixed(0); }
 return out; }
"""
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(); pg.goto("file:///home/claude/work/p4/lab/maneuver_lab.html"); pg.wait_for_timeout(400)
    r = pg.evaluate(JS); print(json.dumps(r, indent=1))
