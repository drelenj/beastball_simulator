#!/usr/bin/env python3
"""Export the NBL opening-night workbook to data/rosters.json for the arcade.
Source: origin/claude/hp002-audit:audit/arcade/NBL_2026-27_Opening_Night_Rosters_CANON_OVR.xlsx
  git show origin/claude/hp002-audit:audit/arcade/NBL_2026-27_Opening_Night_Rosters_CANON_OVR.xlsx > .scratch/rosters.xlsx
Run: python3 -I scripts/export_rosters.py .scratch/rosters.xlsx
Canon fields are copied verbatim. Jersey numbers are ARCADE PLACEHOLDERS (workbook has none)."""
import sys, json, os, hashlib
import openpyxl
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, '.scratch', 'rosters.xlsx')
wb = openpyxl.load_workbook(src, read_only=True, data_only=True)
rows = list(wb['All 712 Players'].iter_rows(values_only=True))
hdr = rows[0]
overview = {r[0]: r for r in list(wb['League Overview'].iter_rows(values_only=True))[1:] if r[0]}
teams = {}
for r in rows[1:]:
    if not r[0]:
        continue
    d = dict(zip(hdr, r))
    teams.setdefault(d['Franchise'], []).append({
        'id': d['Player ID'], 'name': d['Player'], 'pos': d['Position'], 'age': d['Age'], 'yoe': d['YOE'],
        'ovrPreCamp': d['Pre-camp OVR'], 'ovrChange': d['OVR change'], 'ovr': d['Opening-day OVR'],
        'campScore': d['Camp score'], 'readiness': d['Readiness'], 'roleFamiliarity': d['Role familiarity'],
        'role': d['Opening-night role'], 'formation': d['Formation'], 'salaryMMEL': d['Salary (M MEL)'],
        'development': d['Development outcome']})
out, problems = [], []
for fr, players in teams.items():
    starters = [p for p in players if p['role'] == 'Projected starter']
    kpr = [p for p in starters if p['pos'] == 'KPR']; arc = [p for p in starters if p['pos'] == 'ARC']
    ov = overview.get(fr)
    if len(starters) != 12 or len(kpr) != 1 or len(arc) != 1:
        problems.append('%s: starters %d KPR %d ARC %d' % (fr, len(starters), len(kpr), len(arc)))
    if ov and (ov[1] != len(players) or ov[2] != len(starters)):
        problems.append('%s: overview mismatch registered %s/%d starters %s/%d' % (fr, ov[1], len(players), ov[2], len(starters)))
    used = set()
    for p in sorted(players, key=lambda p: p['id']):
        n = int(hashlib.md5(p['id'].encode()).hexdigest(), 16) % 99 + 1
        while n in used:
            n = n % 99 + 1
        used.add(n); p['jersey'] = n
    out.append({'franchise': fr, 'formation': starters[0]['formation'] if starters else None,
                'registered': len(players), 'players': players})
out.sort(key=lambda t: t['franchise'])
json.dump({'_source': 'NBL_2026-27_Opening_Night_Rosters_CANON_OVR.xlsx (branch claude/hp002-audit, audit/arcade/)',
           '_note': 'Canon fields verbatim. jersey = ARCADE PLACEHOLDER (deterministic from Player ID).',
           'teams': out}, open(os.path.join(ROOT, 'data', 'rosters.json'), 'w', encoding='utf-8'), ensure_ascii=False)
print('franchises', len(out), 'players', sum(len(t['players']) for t in out))
print('problems', problems or 'none')
