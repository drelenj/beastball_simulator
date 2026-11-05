import json, sys
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(viewport={"width":390,"height":780}, has_touch=True, device_scale_factor=2); pg = ctx.new_page()
    errs=[]; pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: errs.append(m.text) if m.type=="error" else None)
    pg.goto("file:///home/claude/work/p4/lab/maneuver_lab.html"); pg.wait_for_timeout(500)
    pg.screenshot(path="/tmp/lab0.png")
    res = pg.evaluate("() => window.__lab.matrix(200, {})")
    print(json.dumps(res)); print("errors:", errs)
