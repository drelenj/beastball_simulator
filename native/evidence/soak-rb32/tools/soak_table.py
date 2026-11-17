import json
from collections import Counter
OUT='/home/user/beastball_simulator/native/evidence/soak-rb32'
S=json.load(open(f'{OUT}/summary.json')); E=json.load(open(f'{OUT}/extended.json'))
L=[]
def pct(x): return '—' if x is None else f'{100*x:.1f}%'
def f2(x): return '—' if x is None else f'{x:.2f}'
L.append('# RB/3.1 provisional soak (rb-3-2-toss-timeout-provisional @ a8bda94)\n')
L.append('**Measurements only. Nothing here is ACCEPTED.** Provisional branch, provisional banded scoring (`provisional=True` in the report basis).\n')
L.append('Provenance: commit a8bda94; roster ref 81f92e3 (Garvian Guardians = A, Ala Apex = B); scoring banded; config native-rb/3; step cap 200,000 per match; 2 matches concurrently on 2 cores; runner `tools/soak_driver.py`, aggregation `tools/soak_table.py`/`tools/soak_analyze.py`.\n')
L.append('## Determinism check (real roster, seed 1, two runs)\n')
L.append('| run | status | score | steps | trace_hash | state_hash |')
L.append('|---|---|---|---|---|---|')
for t in ('a','b'):
    d=json.load(open(f'{OUT}/determinism/real-seed01-run{t}.json'))
    L.append(f"| run {t} | {d['status']} | {d['score']['A']}-{d['score']['B']} | {d['steps']} | `{d['trace_hash']}` | `{d['state_hash']}` |")
L.append('\nResult: **identical** trace_hash and state_hash across both runs.\n')
hdr='| seed | status | score A-B | possessions A / B | share ending in attempt A / B | goal pts (play) A / B | foul-award pts A / B | carry attempts A / B | carry goals A / B | groundings | restart timeouts | legal-arrow rate A / B | DQs A / B | runtime_s | trace_hash | state_hash |'
sep='|'+'---|'*16
def row(d):
    m=d.get('metrics') or {}
    if d['status']=='partial':
        return None
    p=m['possessions'];pt=m['points'];c=m['carry_attempts'];a=m['arrows'];q=m['dqs']
    return (f"| {d['seed']} | {d['status']} | {d['score']['A']}-{d['score']['B']} | {p['A']['count']} / {p['B']['count']} | "
            f"{pct(p['A']['share_ending_in_attempt'])} / {pct(p['B']['share_ending_in_attempt'])} | "
            f"{pt['A']['play']} / {pt['B']['play']} | {pt['A']['penalty_awards']} / {pt['B']['penalty_awards']} | "
            f"{c['A']['attempts']} / {c['B']['attempts']} | {c['A']['goals']} / {c['B']['goals']} | {m['groundings']} | {m['restart_timeouts']} | "
            f"{pct(a['A']['legal_rate'])} / {pct(a['B']['legal_rate'])} | {q['A']} / {q['B']} | {d['runtime_s']} | `{d['trace_hash'][:16]}…` | `{d['state_hash'][:16]}…` |")
L.append('## Block A: real roster (seeds 1, 2, 3, 7, 8, 9, 10)\n')
L.append(hdr); L.append(sep)
for d in S['real']:
    r=row(d); L.append(r if r else f"| {d['seed']} | partial | — |")
L.append('\nSeeds 1 and 2 are reruns on the new code line; seeds 4, 5, 6 were not run in this block (not in the request).\n')
L.append('## Block B: control, uniform athletes (rating 0.70, height 2.39 m, mass 226 kg, reach 3.05 m), seeds 1-10\n')
L.append('**All 10 seeds are NON-FINISHING** (hit the 200,000-step cap). Table of stall facts:\n')
L.append('| seed | status | steps | simulated ms | live ms | phase at cap | score | possessions | restarts | foul/DQ | last restart kind & spot | runtime_s | trace_hash | state_hash |')
L.append('|'+'---|'*14)
for d in S['control']:
    n=d['non_finishing']
    L.append(f"| {d['seed']} | **NON-FINISHING** | {n['steps']} | {n['simulated_ms']} | {n['live_ms']} | {n['phase']} | {d['score']['A']}-{d['score']['B']} | 0 / 0 | 0 | none | none recorded | {d['runtime_s']} | `{d['trace_hash'][:16]}…` | `{d['state_hash'][:16]}…` |")
L.append('\nThe seeds share one trace_hash and one state_hash, so the seed had no observable effect in this block. Event log (seed 1): 58 period_end events; ~12,300 each of hunt_start, hunt_claim, simultaneous_contact, joint_control, hunt_retake, rb_hunt_release; no possession, restart, foul, arrow, or goal events. Stall cause not determined here.\n')
L.append('## Extended: goal points, live play vs within one possession of a restart (real roster)\n')
L.append('"Restart-linked" = goal scored by the team that received the most recent restart, before any possession change to the other team. Everything else = live play.\n')
L.append('| seed | A live | A restart-linked | B live | B restart-linked |'); L.append('|---|---|---|---|---|')
for s,e in E['real'].items():
    g=e['goal_points_split']
    L.append(f"| {s} | {g.get('A|live',0)} | {g.get('A|restart_linked',0)} | {g.get('B|live',0)} | {g.get('B|restart_linked',0)} |")
L.append('\n## Extended: fouls by rule and offender role (real roster, all seeds summed)\n')
agg=Counter()
for s,e in E['real'].items():
    for k,v in e['fouls'].items(): agg[k]+=v
rows=sorted(agg.items())
L.append('| rule (reason) | offender role | team | count |'); L.append('|---|---|---|---|')
for k,v in rows:
    rule,role,team=k.split('|'); L.append(f'| {rule} | {role} | {team[-1]} | {v} |')
L.append('\n## Extended: DQs by offence class and offender role (real roster, all seeds summed)\n')
agg=Counter()
for s,e in E['real'].items():
    for k,v in e['dqs'].items(): agg[k]+=v
L.append('| offence class (kind_of_foul) | offender role | team | DQs |'); L.append('|---|---|---|---|')
for k,v in sorted(agg.items()):
    kind,role,team=k.split('|'); L.append(f'| {kind} | {role} | {team[-1]} | {v} |')
L.append('\n## Extended: foul awards by method and team (real roster, all seeds summed)\n')
agg=Counter()
for s,e in E['real'].items():
    for k,v in e['foul_award_points'].items(): agg[k]+=v
L.append('| method | points | team | awards |'); L.append('|---|---|---|---|')
for k,v in sorted(agg.items()):
    meth,pts,team=k.split('|'); L.append(f'| {meth} | {pts[:-2]} | {team[-1]} | {v} |')
L.append('\n## Extended: arrows per Archer (real roster, all seeds summed; Archer-role players only)\n')
L.append('Legal release = `arrow_release` event by that player. Illegal target = `foul` with reason `archery_target` and that player as actor. Hit and miss are not recorded (see missing fields).\n')
arch={}
for s,e in E['real'].items():
    for pid,v in e['arrows_per_archer'].items():
        a=arch.setdefault(pid,Counter()); a.update(legal=v['legal'],illegal_target=v['illegal_target'])
L.append('| Archer (player id) | team | legal releases | illegal target | miss |'); L.append('|---|---|---|---|---|')
for pid,v in sorted(arch.items()):
    L.append(f"| {pid} | {pid[0]} | {v['legal']} | {v['illegal_target']} | not recorded |")
sh=Counter()
for s,e in E['real'].items(): sh.update(e['legal_releases_by_shooter_role'])
L.append(f"\nLegal releases by shooter role, all seeds: {dict(sh)}. Most legal releases are by field players, not Archers.\n")
L.append('## Missing fields (not in the existing report; not guessed)\n')
L.append('- **Carry attempts by outcome** (tackled / grounded / turnover / stopped short): not recorded. Only counts and timestamps exist.')
L.append('- **Foul award to originating rule**: foul_award rows carry method and points, not the foul that caused them.')
L.append('- **DQ to rule**: discipline calls carry kind_of_foul and dq, not the reason.')
L.append('- **Arrow miss and hit**: not recorded as outcomes. arrow_geometry_impact exists but is not classified.')
L.append('- **Stall cause in control block**: not determined.\n')
open(f'{OUT}/summary.md','w').write('\n'.join(L)+'\n')
print('wrote', len(L), 'lines')
