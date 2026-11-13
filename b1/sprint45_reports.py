"""Generate SPRINT45_IMPLEMENTATION_REPORT.md and SPRINT45_OWNER_BRIEFING.md from recorded evidence."""
import json
import subprocess
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
git = lambda *a: subprocess.run(['git', *a], cwd=ROOT, text=True, capture_output=True).stdout.strip()
S = json.loads((ROOT / 'b1/evidence_sprint45/summary.json').read_text())
SRC, R1, BR = '4b19719', '99cf83a', 'experiment/prism-sprint-45'
URL = 'https://github.com/drelenj/beastball_simulator'
code = git('rev-parse', 'HEAD')
files = git('diff', '--name-status', SRC, 'HEAD').splitlines()
log = (ROOT / 'SPRINT45_TIMING.log').read_text().strip().splitlines()
m, ms, rp, t = S['match_seed1'], S['multi_seed'], S['replay'], S['tests']
rules, rc, out = m.get('rules') or {}, m.get('release_contract') or {}, m.get('outcomes_by_status') or {}
term = lambda rows: dict(Counter(str(x['terminal']) for x in rows))
passes = {k: v for k, v in out.items() if k.startswith('pass_')}
unknown = sum(v for k, v in out.items() if k.startswith('unknown'))
MILE = [
 ('M1 decision-to-outcome (one athlete + G1)', 'IMPLEMENTED (Base A, provisional; NOT accepted, H3 open)', 'Base A code and its 25 tests are kept unchanged and pass. Its `core.decide` and pass-release-v1 release code now also run inside the N-athlete loop.'),
 ('M2 plans, communication, receiver cognition', 'PARTIAL (PRIMITIVE)', 'Receiver cognition (pass call, intercept of the believed ball path) and one lossless team shout exist. Plan layer, PlanStageActivation, ReactionGate, real communication channel, give-and-go: MISSING.'),
 ('M3 all roles under the boundary', 'PARTIAL (PRIMITIVE)', 'Field, Keeper and Archer decide from own view/belief; Archer legality is belief-driven (true-state interlock removed); Keeper protection respected in cognition. Still engine-owned: Keeper save execution (C4c kernel), Archer platform movement, contact micro-behaviour, restart placement, substitutions.'),
 ('M4 rules state, restarts, full match', 'PARTIAL (PRIMITIVE)', 'New authoritative possession/rules-state layer (R-01..R-22 as transitions, unit-tested) runs in every match and feeds zone violations to B0 restarts; ruleset 1.0.2 on the B1 instance. Scoring, fouls, other restarts and the clock remain B0 state; KP breaches recorded only; KP-08/KP-OG missing; 4 x 600 s profile not run.'),
 ('M5 gates A/B/C, performance, acceptance bundle', 'MISSING', 'Only replay determinism and a small multi-seed smoke run. No behavioural gates, no paired statistics, no performance budget.'),
]
common = f"""- Branch: `{BR}` ({URL}/tree/{BR})
- Source commits: Base A `{SRC}` (`b1/m1-decision-outcome`) merged with Round 1 `{R1}` (`experiment/prism-sprint-30`), `git merge --no-ff`, no conflicts
- Code+evidence commit these reports were generated from: `{code}` (the report commit follows it; see `git log`)
- Frozen B0 `2abe497`: no B0 file changed (`git diff --name-status 2abe497 HEAD -- . ':!b1'` shows additions only)
- Measured clock (`SPRINT45_TIMING.log`): first `{log[0]}`, last `{log[-1]}`
"""
tests_line = f"`{t['command']}`: **{t['summary']}**; per file {t['by_file']}"
integ = ['## 0. Integration result (Phase B step 0)', '',
         '- Branch created from `4b19719` (the prompt names its parent `77604e1` in Phase A and `4b19719` in section 2 and Phase B; `4b19719` was used) and pushed empty first.',
         '- Round 1 merged cleanly. Before any Round 2 change: `pytest -q b1` gave 51 passed, 1 failed (the known inventory guard), and the seed-1 match reproduced Round 1 exactly (9-3, 42,143 decisions, trace hash `02b95a47...`).',
         '- Nothing from Round 1 was lost. No Codex test was changed; `core.py` and `runtime.py` are unmodified.', '']
arch = ['## Architectural decisions', '',
        '1. **One pipeline.** `cognition.decide` delegates carry-vs-pass and defender pursuit/lane sub-decisions to Base A `core.decide`; pass releases execute through Base A `PhysicalExecutionPort._release_due` (pass-release-v1, 60 degree bound) via a duck-typed adapter. The Round 1 use of the B0 pass planner on true receiver state is removed.',
        '2. **Possession/rules-state layer** `b1/possession.py`: pure module, authoritative, fed only by engine events in `MatchPort._feed_rules` (carrier, CONTESTED mode, touch, release, strip, boundary, restart, goal, period). It never reads beliefs. Its public state reaches athletes only inside the latency-delayed snapshot as rules signals.',
        '3. **Ruleset 1.0.2** is set through the B0 engine configuration switch on the B1 match instance only.',
        '4. **Archer legality is a belief decision.** The motor has no true-state check; cognition filters targets and can `abort_draw`; a wrong belief becomes an engine foul.',
        '5. **Keeper protection** from the view only (Keeper track inside own zone while his team has passive possession): no press, no Archer target; breaches counted in the ledger.',
        '6. **Zone violations** found by the layer are enforced through a B0 restart award (provisional spot).',
        '7. **View construction never reads live state** for self or public data: it raises if no snapshot older than the latency exists.',
        '8. **Outcome causes come from engine events**; a score change during a flight without a matching goal event is `unknown:`.', '']
I = ['# SPRINT45 IMPLEMENTATION REPORT', '', 'Experimental build. Status words: DESIGN COMPLETE / IMPLEMENTED / TESTED / ACCEPTED. **Nothing is ACCEPTED.**', '', common, *integ,
     '## Changed files (vs Base A)', '', '```', *files, '(plus report files committed after this was generated)', '```', '', *arch,
     '## Milestone status (experiment evidence, not acceptance)', '', '| milestone | status | notes |', '|---|---|---|', *[f'| {a} | {b} | {c} |' for a, b, c in MILE], '',
     '## Deviations from specs', '', '- See `SPRINT45_LIMITATIONS.md`: BR-3, BA-7, record-only KP breaches, provisional RST-1 spot, touch source, public signals, engine-owned procedures.', '',
     '## Tests run', '', f'- {tests_line}', *[f'  - NOT OK: `{x}`' for x in t['not_ok']],
     f"- Deterministic replay seed 1 (two processes): identical = **{rp['identical']}**",
     f"- End-to-end match seed 1: `{m.get('status')}`, {m.get('result')}, {m.get('decisions_total')} decisions {m.get('decisions_by_role')}",
     f"- Rules ledger seed 1: {rules.get('ledger_entries')} entries, by row {rules.get('ledger_by_row')}, violations enforced {rules.get('violations_enforced')}",
     f"- Pass releases seed 1: {rc}; pass outcomes {passes}; unattributed outcomes (`unknown`): {unknown}",
     f"- Additional full-match seeds: attempted {ms['attempted']}, completed {ms['completed']}, failed {ms['failed']}",
     f"- G1 scenarios, 12 seeds each: open {term(S['g1'])}; defender on lane {term(S['g1_close'])}",
     '- Independent review by a fresh agent: `b1/evidence_sprint45/INDEPENDENT_REVIEW.md`. It ran before the last fixes (no live-state fallback in `deliver`, non-vacuous primitives test, extended poison test, violation enforcement); those are NOT re-reviewed. Its OWN-5 FAIL (engine procedures still choosing for athletes) and BR-3 FAIL stand.', '',
     '## Tests not run', '', '- 4 x 600 s profile, 100-seed matrices, paired sign tests, behavioural gates, performance budget, B0-vs-B1 comparison, regeneration of the Base A G1 matrix.', '',
     '## Known defects / incomplete milestone requirements', '', 'See `SPRINT45_LIMITATIONS.md` and the independent review.', '',
     '## Reproduce', '', '```', 'pip install scipy numpy pytest', 'python3 -m pytest -q b1', 'python -m b1.match_run --seed 1 --out /tmp/match_seed1.json',
     'python -m b1.sprint45_evidence 2 3 4 && python -m b1.sprint45_reports', '```', '']
(ROOT / 'SPRINT45_IMPLEMENTATION_REPORT.md').write_text('\n'.join(I))
O = ['# SPRINT45 OWNER BRIEFING', '', '**Nothing is ACCEPTED. This is experiment evidence for review.**', '', common,
     '## 1. What was accomplished', '',
     f"Round 2 merged the Round 1 build onto Codex's M1 code and replaced the weakest pieces. One full match (seed 1, ruleset 1.0.2) ran to the end: {m.get('result')}, {m.get('decisions_total')} athlete decisions; the same seed replayed with identical hashes: {rp['identical']}.", '',
     'Run it: `pip install scipy numpy pytest && python -m b1.match_run --seed 1 --out /tmp/match_seed1.json`', '',
     '## 2. What B1 can actually do now', '',
     '- Tracks possession the way the decision record defines it (direct, passive, contested, 500 ms threshold, zone clock) from engine events, and tells athletes only through delayed rules signals.',
     '- Uses one decision and pass-release path (Codex M1 code) for all field players; passes no longer read the receiver\'s true state.',
     '- Archers judge legality from their own belief; Keepers inside their zone are not pressed or targeted; zone violations trigger a restart.', '',
     '## 3. What remains unimplemented or unproven', '', '| milestone | status | notes |', '|---|---|---|', *[f'| {a} | {b} | {c} |' for a, b, c in MILE], '',
     f"Seed-1 pass outcomes: {passes}. Most passes still do not reach a teammate; this is one seed and no rate claim is made.", '',
     '## 4. What is blocking the next step', '', '- M1 is not accepted (H3 open).', '- The engine still makes choices for athletes (Keeper save plan, restart taker and placement, Archer platform movement, wind-up refusal): the independent review rates OWN-5 FAIL for that reason.',
     '- B0 has no hand-level touch model, so "contested" is under-detected.', '- The B0 inventory guard fails on any clean checkout (23 files never committed).', '',
     '## 5. Recommended action', '', 'Review `SPRINT45_LIMITATIONS.md` and the independent review; do not merge. Next engineering step: move restart, Keeper-save and Archer-movement choices behind athlete intents, then run paired multi-seed statistics per `SPRINT45_UNLIMITED_STRATEGY.md`.', '',
     '## Tests and runs', '', f'- {tests_line}', *[f'  - NOT OK: `{x}`' for x in t['not_ok']],
     f"- Full matches: seed 1 completed; additional seeds attempted {ms['attempted']}, completed {ms['completed']}, failed {ms['failed']}.", '',
     '## Reports', '', *[f'- {URL}/blob/{BR}/{f}' for f in ('SPRINT45_OWNER_BRIEFING.md', 'SPRINT45_IMPLEMENTATION_REPORT.md', 'SPRINT45_TEST_REPORT.md', 'SPRINT45_LIMITATIONS.md', 'SPRINT45_UNLIMITED_STRATEGY.md', 'SPRINT45_EXECUTION_STRATEGY.md', 'b1/evidence_sprint45/INDEPENDENT_REVIEW.md', 'b1/sprint45/CANON_NOTES.md', 'b1/SPRINT45_README.md')], '']
(ROOT / 'SPRINT45_OWNER_BRIEFING.md').write_text('\n'.join(O))
print('reports written from', code)
