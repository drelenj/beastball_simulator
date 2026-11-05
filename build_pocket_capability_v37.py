"""Turn results_v37/capability_table_v37.json into (a) CSV, (b) markdown, (c) pocket_capability_v37.py - a dependency-free lookup with interpolation."""
import json, csv
rows = json.load(open('results_v37/capability_table_v37.json'))
def decel(r):
    for k, v in (('stop25', 25.), ('stop15', 15.), ('stop35', 35.)):
        s = r[k]
        if s['ok'] and s['d']: return round((v * v - 9.) / (2 * s['d']), 1)
    return None
flat = []
for r in rows:
    flat.append(dict(role=r['role'], rating=r['rating'], reserve=r['reserve'], region=r['region'], severity=r['severity'], top_mph=r['top_mph'], t10_s=r['t10'], t36_6_s=r['t36'],
                     stop15_m=r['stop15']['d'], stop25_m=r['stop25']['d'], stop35_m=r['stop35']['d'], stop25_ok=r['stop25']['ok'], stop25_reason=r['stop25'].get('reason', ''),
                     cut90_25_s=r['cut90_25']['t'], cut90_25_vmin_pct=r['cut90_25']['vmin_pct'], cut90_15_s=r['cut90_15']['t']))
with open('results_v37/capability_table_v37.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(flat[0])); w.writeheader(); w.writerows(flat)
def md(sel, cols):
    out = ['| ' + ' | '.join(cols) + ' |', '|' + '---|' * len(cols)]
    for r in sel: out.append('| ' + ' | '.join('-' if r[c] is None else str(r[c]) for c in cols) + ' |')
    return '\n'.join(out)
open('results_v37/capability_table_v37.md', 'w').write(
    '## Field athletes, fatigue (no injury)\n' + md([r for r in flat if r['role'] == 'field' and not r['region']], ['rating', 'reserve', 'top_mph', 't10_s', 't36_6_s', 'stop15_m', 'stop25_m', 'stop35_m', 'cut90_25_s', 'cut90_25_vmin_pct']) +
    '\n\n## Field athletes, injury (reserve 1)\n' + md([r for r in flat if r['role'] == 'field' and r['region']], ['region', 'severity', 'rating', 'top_mph', 't10_s', 't36_6_s', 'stop15_m', 'stop25_m', 'stop35_m', 'stop25_reason', 'cut90_25_s']) +
    '\n\n## Keepers, fatigue\n' + md([r for r in flat if r['role'] == 'keeper'], ['rating', 'reserve', 'top_mph', 't10_s', 't36_6_s', 'stop15_m', 'stop25_m', 'stop35_m', 'cut90_25_s']) + '\n')
METRICS = ['top_mph', 't10_s', 't36_6_s', 'stop15_m', 'stop25_m', 'stop35_m', 'cut90_25_s', 'cut90_25_vmin_pct']
data = {'field_fatigue': {}, 'keeper_fatigue': {}, 'injury': {}}
for r in flat:
    key = (r['rating'], r['reserve'])
    m = {k: r[k] for k in METRICS}
    if r['role'] == 'keeper': data['keeper_fatigue'][f"{r['rating']}|{r['reserve']}"] = m
    elif not r['region']: data['field_fatigue'][f"{r['rating']}|{r['reserve']}"] = m
    else: data['injury'][f"{r['region']}|{r['rating']}|{r['severity']}"] = m
for rr in (.6, .8, 1.0):                         # severity 0 row = rested, uninjured
    base = data['field_fatigue'][f'{rr}|1.0']
    for reg in ('hamstring', 'groin', 'knee', 'ankle', 'general'): data['injury'][f'{reg}|{rr}|0.0'] = base
src = '''"""Pocket capability lookup (Beastball locomotion v3.7 stack).  No dependencies; interpolates the generated table.

capability(rating, reserve=1., region='', severity=0., role='field') -> dict with
  top_mph, t10_s, t36_6_s (time to 10 m / 40 yd from standing), stop15_m / stop25_m / stop35_m (hard-stop distance to 3 m/s from 15 / 25 / 35 m/s), cut90_25_s (90-degree cut at 25 m/s, time to heading),
  cut90_25_vmin_pct (lowest speed during that cut, % of entry speed), plus 'notes'.
Rules: fatigue and injury combine multiplicatively relative to the rested uninjured value; ratings below 0.6 clamp to 0.6 (flagged).  A metric is None when
the simulator could not complete the manoeuvre at that condition (a severe injury that cannot stop).  Provisional design values.
"""
import bisect
DATA = @@DATA@@
RATINGS = [.6, .7, .8, .9, 1.0]; INJ_RATINGS = [.6, .8, 1.0]; KEEPER_RATINGS = [.6, .8, 1.0]
RESERVES = [0., .25, .5, .75, 1.]; KEEPER_RESERVES = [0., .5, 1.]; SEVERITIES = [0., .5, 1.]
METRICS = @@METRICS@@
def _bracket(grid, x):
    x = min(max(x, grid[0]), grid[-1]); i = min(max(bisect.bisect_right(grid, x) - 1, 0), len(grid) - 2)
    return grid[i], grid[i + 1], (x - grid[i]) / (grid[i + 1] - grid[i])
def _bilinear(get, ga, a, gb, b, metric):
    a0, a1, ta = _bracket(ga, a); b0, b1, tb = _bracket(gb, b)
    v = [get(a0, b0, metric), get(a0, b1, metric), get(a1, b0, metric), get(a1, b1, metric)]
    if any(x is None for x in v): return None
    return (v[0] * (1 - ta) * (1 - tb) + v[1] * (1 - ta) * tb + v[2] * ta * (1 - tb) + v[3] * ta * tb)
def _fat(role, rating, reserve, metric):
    d = DATA['keeper_fatigue' if role == 'keeper' else 'field_fatigue']
    gr, gv = (KEEPER_RATINGS, KEEPER_RESERVES) if role == 'keeper' else (RATINGS, RESERVES)
    return _bilinear(lambda r, s, m: d['%%s|%%s' %% (r, s)][m], gr, rating, gv, reserve, metric)
def _inj(region, rating, severity, metric):
    d = DATA['injury']
    return _bilinear(lambda r, s, m: d['%%s|%%s|%%s' %% (region, r, s)][m], INJ_RATINGS, rating, SEVERITIES, severity, metric)
def capability(rating, reserve=1., region='', severity=0., role='field'):
    notes = []
    if rating < .6: notes.append('rating clamped to 0.6'); rating = .6
    if role == 'keeper' and (region and severity > 0): notes.append('keeper injury not tabulated: injury ignored'); region = ''
    out = {}
    for m in METRICS:
        rested = _fat(role, rating, 1., m)
        v = _fat(role, rating, reserve, m)
        if v is not None and rested:
            f = v / rested
            if region and severity > 0:
                inj = _inj(region, rating, severity, m); base = _inj(region, rating, 0., m)
                v = None if (inj is None or not base) else rested * f * (inj / base)
        out[m] = None if v is None else round(v, 3)
    out['notes'] = notes
    return out
'''.replace('@@DATA@@', repr(data)).replace('@@METRICS@@', repr(METRICS)).replace('%%', '%')
open('pocket_capability_v37.py', 'w').write(src)
