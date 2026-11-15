const { chromium } = require('playwright');
(async () => {
const url = process.argv[2] || 'http://localhost:5173/?auto=ava';
const out = process.argv[3] || 'shot.png';
const wait = Number(process.argv[4] || 4000);
const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1280, height: 720 } });
const errs = []; p.on('pageerror', (e) => errs.push(String(e))); p.on('console', (m) => { if (m.type() === 'error') errs.push(m.text()); });
await p.goto(url); await p.waitForTimeout(wait); await p.screenshot({ path: out });
console.log('errors', JSON.stringify(errs)); await b.close();
})();
