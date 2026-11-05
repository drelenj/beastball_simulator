import json
from playwright.sync_api import sync_playwright
JS = """
() => { const L=window.__lab, out={};
 for (const k of ['juke','spin','truck']) { out[k]={};
  for (const r of [.2,.6,.95]) for (const i of [0,.5,1]) { let sc=0,n=400; for(let s=1;s<=n;s++){ const w=L.runTrial(k,{seed:s,lead:.7,defender:{reaction:r,instinct:i}}); if(w.result&&w.result.startsWith('SCORE')) sc++; } out[k]['r'+r+'_i'+i]=+(100*sc/n).toFixed(0); } }
 // a cut that the defender can also use: defender agility/decel effect on cut
 out.cut_vs_agility={}; for (const a of [.5,.85,1]) { let sc=0,n=300; for(let s=1;s<=n;s++){ const w=L.runTrial('cut',{seed:s,lead:.4,defender:{agility:a,reaction:.95,instinct:1}}); if(w.result&&w.result.startsWith('SCORE')) sc++; } out.cut_vs_agility['def_agility_'+a]=+(100*sc/n).toFixed(0); }
 return out; }
"""
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(); pg.goto("file:///home/claude/work/p4/lab/maneuver_lab.html"); pg.wait_for_timeout(400)
    print(json.dumps(pg.evaluate(JS)))
