"""Generate the EMERGENCE1_*.md reports from recorded evidence (results/*.json[l])."""
import json
import subprocess
from collections import Counter
from pathlib import Path

from .params import BOUNDS, DEFAULT
from .readout import aggregate, paired_summary, render

ROOT = Path(__file__).resolve().parents[2]
RES = ROOT / 'b1/emergence/results'
git = lambda *a: subprocess.run(['git', *a], cwd=ROOT, text=True, capture_output=True).stdout.strip()
load = lambda p: [json.loads(l) for l in p.read_text().splitlines() if l.strip()] if p.exists() else []
SRC, BR, URL = 'c64d92e', 'experiment/emergence-1', 'https://github.com/drelenj/beastball_simulator'


def main():
    st = json.loads((RES / 'search/search_state.json').read_text()) if (RES / 'search/search_state.json').exists() else {}
    fin = json.loads((RES / 'final_summary.json').read_text()) if (RES / 'final_summary.json').exists() else {}
    tests = json.loads((RES / 'tests_summary.json').read_text()) if (RES / 'tests_summary.json').exists() else {}
    search_rows, held, sym, full = load(RES / 'search/matches.jsonl'), load(RES / 'heldout.jsonl'), load(RES / 'symmetry.jsonl'), load(RES / 'full_length.jsonl')
    log = (ROOT / 'EMERGENCE1_TIMING.log').read_text().strip().splitlines()
    code = git('rev-parse', 'HEAD')
    files = git('diff', '--name-status', SRC, 'HEAD').splitlines()
    ok = lambda rs: [r for r in rs if r.get('status') == 'final']
    att = len(search_rows) + len(held) + len(sym) + len(full)
    comp = len(ok(search_rows)) + len(ok(held)) + len(ok(sym)) + len(ok(full))
    hs = paired_summary(held, 'baseline', 'evolved') if held else None
    fs = paired_summary(full, 'baseline', 'evolved') if full else None
    head = f"""- Branch `{BR}` ({URL}/tree/{BR}); source commit `{SRC}` (`experiment/prism-sprint-45`); reports generated from commit `{code}` (the report commit follows it; see `git log`)
- Clock (`EMERGENCE1_TIMING.log`): first `{log[0]}`, last `{log[-1]}`; cores: 4 (`nproc`)
- Matches: attempted {att}, completed {comp}, failed {att - comp} (search {len(search_rows)}, held-out {len(held)}, symmetry {len(sym)}, full-length {len(full)})
- Status words: IMPLEMENTED / TESTED only. **Nothing here is ACCEPTED.** Quality is judged by match results only.
"""
    repro = """```
pip install scipy numpy pytest
python -m b1.match_run --seed 1                                  # one full match, default parameters
python -m b1.emergence.harness --seeds 1 --period-s 45           # one paired, side-swapped PROXY match
python -m b1.emergence.search --minutes 15 --pop 8 --out b1/emergence/results/search
python -m b1.emergence.final && python -m b1.emergence.report    # held-out, symmetry, full-length sample, reports
python3 -m pytest -q b1
```"""
    # ---------------- RESULTS
    R = ['# EMERGENCE1 RESULTS', '', head, '## Search (PROXY matches: 2 x 45 s)', '']
    if st:
        R += [f"- population {st['pop']}, generations completed {st['generations_completed']}, search matches attempted {st['attempted']}, completed {st['completed']}, failed {st['failed']}, elapsed {st['elapsed_s']} s",
              f"- one paired, side-swapped seed per pairing per generation (seeds {st['search_seeds_used']}); fitness = points (3/1/0), then goal difference", '',
              '| gen | top 3 (label: points, goal diff) | baseline rank |', '|---|---|---|']
        for h in st['history']:
            lab = [e['label'] for e in h['standings']]
            R.append(f"| {h['generation']} | " + '; '.join(f"{e['label']}: {e['points']}, {e['gd']:+d}" for e in h['standings'][:3]) + f" | {lab.index('baseline') + 1} of {len(lab)} |")
        ev = st['best_non_baseline_params']
        R += ['', f"Vector taken to held-out evaluation (best non-baseline of the last completed generation, `{st['best_non_baseline_label']}`):", '', '| parameter | baseline | evolved | bounds |', '|---|---|---|---|']
        R += [f"| `{k}` | {getattr(DEFAULT, k)} | {ev[k]} | [{BOUNDS[k][0]}, {BOUNDS[k][1]}] |" for k in BOUNDS]
        R += ['', 'With one seed per pairing per generation the ranking inside a generation is noisy; the search result is a candidate, not a finding. Only the held-out comparison below counts.', '']
    else:
        R += ['Search state missing: search did not complete a generation.', '']
    R += ['## Held-out comparison (seeds never used in the search; PROXY 2 x 45 s)', '']
    if hs:
        R += [f"```\n{json.dumps(hs, sort_keys=True, indent=1)}\n```", '',
              f"**Evolved vs baseline on {hs.get('pairs')} held-out paired seeds: evolved better on {hs.get('b_pair_wins')} pairs, worse on {hs.get('b_pair_losses')}, tied {hs.get('pair_draws')}; exact two-sided sign-test p = {hs.get('sign_test_p')}.** "
              + ('The evolved vector beat baseline beyond noise at p < 0.05.' if (hs.get('sign_test_p') or 1) < .05 and (hs.get('b_pair_wins') or 0) > (hs.get('b_pair_losses') or 0)
                 else 'The evolved vector did NOT beat baseline beyond noise on held-out seeds.'), '']
    else:
        R += ['Held-out comparison not performed.', '']
    R += ['## Proxy vs full-length agreement (small sample)', '']
    if fs and hs:
        agree = ((fs.get('mean_goal_diff_per_pair') or 0) > 0) == ((hs.get('mean_goal_diff_per_pair') or 0) > 0)
        R += [f"- full 2 x 120 s, {fs.get('pairs')} paired seeds: evolved pair wins {fs.get('b_pair_wins')}, losses {fs.get('b_pair_losses')}, draws {fs.get('pair_draws')}, mean goal difference {fs.get('mean_goal_diff_per_pair')}, sign-test p {fs.get('sign_test_p')}",
              f"- proxy mean goal difference {hs.get('mean_goal_diff_per_pair')}; direction {'agrees' if agree else 'DISAGREES'} with full length. With {fs.get('pairs')} pairs this is a sanity check only, not a validation of the proxy.", '']
    else:
        R += ['Not performed.', '']
    R += ['## Side-swap symmetry (identical parameters on both sides, PROXY)', '']
    if fin.get('symmetry'):
        s = fin['symmetry']
        dec = s['A_wins'] + s['B_wins']
        R += [f"- {s['matches']} seeds: side A wins {s['A_wins']}, side B wins {s['B_wins']}, draws {s['draws']}; A share of decided matches {round(s['A_wins'] / dec, 3) if dec else None}; mean A goal difference {s['A_goal_diff_mean']}",
              '- All comparisons above use both side assignments on every seed, so a side bias cancels in the paired unit.', '']
    R += ['## Emergence read-out (held-out matches, baseline vs evolved)', '']
    R += [render(held, 'baseline', 'evolved') if held else 'No held-out rows.', '']
    R += ['## Reproduce', '', repro, '']
    (ROOT / 'EMERGENCE1_RESULTS.md').write_text('\n'.join(R))
    # ---------------- EXPLOIT LOG
    allrows = ok(search_rows) + ok(held) + ok(sym) + ok(full)
    X = ['# EMERGENCE1 EXPLOIT LOG', '', head, 'Entries are **EXPLOIT-CANDIDATE** for owner review: behaviour that may be a physics or rules quirk. Nothing was fixed, patched or excluded. Each entry gives seed, row id and trace hash; reproduce with `python -m b1.emergence.harness --seeds <seed> --period-s <period>` using the row\'s `params_A`/`params_B` from the JSONL.', '']
    n = 0

    def entry(title, rule, body, rows):
        nonlocal n
        n += 1
        X.extend([f'## X-{n} EXPLOIT-CANDIDATE: {title}', '', f'- Rule / engine row involved: {rule}', f'- Observation: {body}'])
        for r in rows[:3]:
            X.append(f"- seed {r['seed']}, row `{r['id']}`, trace `{r['trace_hash'][:16]}`, score {r['score']}, method {r.get('method')}")
        X.append('')
    odd = [r for r in allrows if r.get('method') not in ('regulation', 'overtime', 'shootout')]
    if odd:
        entry('match ended by a non-regulation method', 'B0 engine 18.x (forfeit / lineup)', f"{len(odd)} matches ended by {dict(Counter(r.get('method') for r in odd))}.", odd)
    if fin.get('symmetry'):
        s = fin['symmetry']
        dec = s['A_wins'] + s['B_wins']
        if dec and abs(s['A_wins'] / dec - .5) >= .2:
            entry('side asymmetry with identical parameters', 'B0 setup / opening scrimmage / roster generation per side (make_rosters gives each side different athletes)',
                  f"side A won {s['A_wins']} of {dec} decided matches with identical parameters (mean A goal difference {s['A_goal_diff_mean']}). Rosters differ per side, so this may be roster strength rather than a rules quirk; not separated here.", ok(sym))
    zv = [r for r in allrows if (r.get('metrics') or {}).get('match', {}).get('zone_violations')]
    if zv:
        entry('zone-clock / zone-entry violations occurring in play', 'D1 record R-11..R-13 (ZR-C, ZR-T, ZR-1), enforced by a provisional centre restart',
              f"{len(zv)} of {len(allrows)} matches had at least one violation: {dict(sum((Counter(r['metrics']['match']['zone_violations']) for r in zv), Counter()))}. Whether a vector profits from conceding or forcing them was not analysed.", zv)
    stop = sorted(allrows, key=lambda r: -((r.get('metrics') or {}).get('match', {}).get('stoppages') or 0))
    if stop and (stop[0].get('metrics') or {}).get('match', {}).get('stoppages'):
        m0 = stop[0]['metrics']['match']
        entry('high stoppage / restart counts', 'B0 restart rules (boundary, zone inbound) and RESTARTS_NOTES',
              f"most stoppages in one proxy match: {m0['stoppages']} ({m0.get('restarts_by_reason')}). Possible restart farming or simply failed passes going out; not separated.", stop)
    hi = sorted(allrows, key=lambda r: -max(r['score'].values()))
    if hi:
        r0 = hi[0]
        side = 'A' if r0['score']['A'] >= r0['score']['B'] else 'B'
        g = ((r0.get('metrics') or {}).get(side) or {})
        entry('very high single-team score in a short match', 'B0 scoring methods (inner / release / outside points, carry value 4)',
              f"highest team score {max(r0['score'].values())} in a {2 * r0['period_s']} s match by label `{r0['label_' + side]}`; goals by method {g.get('goals')}, shots {g.get('shots')}, passes completed {g.get('pass_completed')}. Check whether one scoring method dominates independent of ratings.", hi)
    ev_p = st.get('best_non_baseline_params') or {}
    if held and ev_p.get('bias_pass', 0) <= -3:
        agg = aggregate(held)[0]
        keep = ('pass_released', 'pass_completed', 'shots', 'points', 'turnovers_lost')
        entry('never-pass play outscoring passing play', 'Engine constraint, not a rule: pass-release-v1 admits a fixed 27 m/s pass with no loft or speed choice and B1 pass completion is low (see limitations)',
              f"the evolved vector has bias_pass = {ev_p.get('bias_pass')} (passing effectively switched off) and scores by carrying and close shots. If passing is dominated only because the pass mechanics are primitive, this is an artifact of the build, not a finding about Beastball. Per-match means by label on held-out matches: {json.dumps({l: {k: m.get(k) for k in keep} for l, m in agg.items()})}", held)
    og = [r for r in allrows if any('own_goal' in (((r.get('metrics') or {}).get(sd) or {}).get('goals') or {}) for sd in 'AB')]
    if og:
        entry('goals credited by method `own_goal`', 'B0 engine goal(): method own_goal; D1 KP-OG (Keeper own goal) is not implemented in B1',
              f"{len(og)} of {len(allrows)} completed matches contain at least one `own_goal` score. These are points gained without an attacking action by the scoring team (the ball enters a goal off the defending side, e.g. a failed pass or clearance). A vector can profit simply by the opponent's passing errors; frequency by vector was not analysed.", og)
    meth = Counter()
    for r in allrows:
        for side in 'AB':
            for k, v in (((r.get('metrics') or {}).get(side) or {}).get('goals') or {}).items():
                meth[k] += v if isinstance(v, int) else 1
    if meth:
        X += [f'## Scoring methods across all {len(allrows)} completed matches (context for X entries)', '', f'- {dict(meth)}', '']
    fouls = Counter()
    for r in allrows:
        fouls.update((r.get('metrics') or {}).get('match', {}).get('fouls_by_reason') or {})
    if fouls:
        X += ['## Fouls by reason across all completed matches (context)', '', f'- {dict(fouls.most_common(10))}', '']
    X += ['## Not examined', '', '- Stalling with the ball, Keeper-hold loopholes, Archer platform quirks and rating-independent scoring were not analysed beyond the counts above. Absence of an entry is not evidence of absence.', '']
    (ROOT / 'EMERGENCE1_EXPLOIT_LOG.md').write_text('\n'.join(X))
    # ---------------- TEST REPORT
    T = ['# EMERGENCE1 TEST REPORT', '', head, '## Suites run', '']
    if tests:
        T += [f"- `{tests['command']}` -> **{tests['summary']}**; passed per file {tests['by_file']}"] + [f"  - NOT OK: `{x}`" for x in tests['not_ok']]
    else:
        T += ['- full suite result not recorded']
    T += ['', '## Required checks', '',
          '- Existing suite: see above (known failing test: `test_frozen_B0_file_identity`, 23 inventory files never committed).',
          '- Poison / perturbation test for positioning: `test_poison_hidden_state_and_other_team_params_do_not_reach_decisions` (all live bodies, ball and carrier poisoned after capture; views and decisions identical; other team\'s vector never reaches an athlete). Failing case shown by `test_weights_drive_the_choice_view_change_changes_decision`.',
          '- Determinism: `test_determinism_same_seed_same_params`, `test_parallel_and_serial_and_order_give_identical_hashes` (4 matches serial vs 2 workers in reversed order).',
          '- Parameter bounds and logging: `test_bounds_validation_and_size`, `test_params_are_per_team_fixed_and_logged`, `test_bias_and_risk_parameters_change_ball_decisions`.',
          f"- Side-swap symmetry: {fin.get('symmetry')} (identical parameters, seeds 7000+).",
          '- Metrics collector is read-only: `test_metrics.py` (hash identical with and without the collector).',
          '- Independent boundary / ownership check by a fresh agent: `b1/emergence/results/INDEPENDENT_REVIEW.md`.', '',
          '## Not run', '', '- No 4 x 600 s matches; no search on full-length matches; no per-role parameter search; metric differences are descriptive (no significance test).', '', '## Reproduce', '', repro, '']
    (ROOT / 'EMERGENCE1_TEST_REPORT.md').write_text('\n'.join(T))
    # ---------------- IMPLEMENTATION REPORT
    I = ['# EMERGENCE1 IMPLEMENTATION REPORT', '', head, '## Existing files and functions edited (for the merge with Codex)', '',
         '- `b1/cognition.py`: imports of `emergence.params` / `emergence.positioning`; new field `AthleteView.policy`; new helper `_position(...)`; in `decide(...)` the four call sites that produced `home` / `support` / `mark` now call `_position` (dead-ball non-taker, loose-ball fallback, team-mate carrier, opponent carrier); `32` -> `view.policy.shot_range`; a bias / risk block immediately before `chosen = max(...)`; `policy` added to the decision record; `view_from_json` restores `policy`. `home_position` is left in the file but is unreachable from `decide` (tested).',
         '- `b1/matchport.py`: `MatchPort.__init__(..., policies=None, period_seconds=None)` (validation, settings copy); `deliver` passes `policy=self.policies[a.team]`; `run_match(..., policies, period_seconds, on_decision, on_step)` and the two hook calls; parameters and settings hashed into the trace hash; `policy_params` in the result; `position` added to `LOCOMOTION`.',
         '- `b1/test_sprint.py`: BR-1 import allow-list extended by the two pure emergence modules.',
         '- NOT touched: `b1/core.py`, `b1/runtime.py`, `b1/possession.py`, Keeper save (`_keeper_motor`), restart taker (`_ready`, `_restart_receiver`), Archer movement, release withholding, any B0 file.', '',
         '## New files', '', '- `b1/emergence/params.py`, `positioning.py`, `harness.py`, `search.py`, `final.py`, `metrics.py`, `readout.py`, `report.py`, tests, `results/`.', '',
         '## Changed files (vs source commit)', '', '```', *files, '```', '',
         '## Architectural decisions', '',
         '1. `PolicyParams`: 16 bounded numbers, frozen, validated at construction; one vector per team, fixed before the match, carried in each athlete\'s own view; logged in the match result, every decision record and the trace hash.',
         '2. Positioning: 9 candidate points (stay or 6 m in 8 directions) scored from the athlete\'s belief; offence/defence mode comes only from the public passive-possession signal; no slot or formation input.',
         '3. Option biases are additive on the existing option values; risk parameters filter options (lane clearance, shot range).',
         '4. Harness: one process-local engine per match, parallel pool, rows keyed and sorted by job id; both side assignments on every seed.',
         '5. Search: population with a fixed baseline anchor, round-robin, results-only fitness, time-boxed; proxy 2 x 45 s.', '',
         '## Deviations', '', '- Parameters are per team, not per role. `match_run` CLI has no parameter flags (use the harness).',
         '- The search started at minute 5 (earlier than the planned minute 20) to gain generations and was time-boxed to 25 minutes.',
         '- "Mark" and "support" no longer exist as option kinds; they are absorbed into positioning weights (`pos_opp_def`, `pos_lane`, ...).', '',
         '## Known defects', '', 'See `EMERGENCE1_LIMITATIONS.md` and the independent review.', '', '## Reproduce', '', repro, '']
    (ROOT / 'EMERGENCE1_IMPLEMENTATION_REPORT.md').write_text('\n'.join(I))
    # ---------------- LIMITATIONS
    cons = (ROOT / 'b1/emergence/ENGINE_CONSTRAINTS.md').read_text() if (ROOT / 'b1/emergence/ENGINE_CONSTRAINTS.md').exists() else ''
    L = ['# EMERGENCE1 LIMITATIONS', '', head, '## PRIMITIVE modules added in this sprint', '',
         '- `emergence.positioning` PRIMITIVE: 9 candidates at a fixed 6 m step; fixed caps (nearest-teammate 12 m, nearest-opponent 10 m, lane 10 m), fixed 0.1 scaling, fixed edge band 6 m and Keeper-zone penalty shape; one-step greedy, no anticipation. These constants are not searched and shape what can emerge.',
         '- `emergence.params` PRIMITIVE: one vector per team (not per role or athlete); additive biases on top of hand-set option values from SPRINT-45 and Base A (e.g. carry 10 under pressure vs pass at most about 7), so the search can only shift, not replace, those values.',
         '- `emergence.search` PRIMITIVE: one paired seed per pairing per generation; a handful of generations; no statistics inside the search.',
         '- `emergence.harness` PROXY: search and held-out matches are 2 x 45 s; agreement with 2 x 120 s checked on a very small sample only.',
         '- `emergence.metrics` PRIMITIVE: 1 Hz position samples; pass metrics exclude restart passes; descriptive only.', '',
         '## Findings of the independent review (`b1/emergence/results/INDEPENDENT_REVIEW.md`), not fixed (decision code was frozen while the search ran)', '',
         '- OWN-4 FAIL: the decision record keeps only the chosen position, not the candidate scores, so a positioning decision cannot be re-derived from harness output alone (harness runs with telemetry off).',
         '- The `position` option has a fixed value 1.0: the nine `pos_*` weights decide where to stand, never whether positioning beats pursue / press / pass. Strongest non-parameter bias.',
         '- Built-in attractor: an athlete alone in defence mode with default weights converges to about (20, 50) in front of its own goal; the attack/defence split and role filters are imposed.',
         '- Parameter values are rounded to 4 decimals for logging and hashing.',
         '- `search.standings` ignores non-final (crashed) matches, so a vector that crashed matches would lose no points (no match crashed in this run).',
         '- Generation count depends on wall clock and machine load; exact ties in the standings resolve alphabetically (favouring `baseline`).',
         '- `harness.run_jobs` appends to its output file; metric-hook exceptions are swallowed into `metric_errors`.',
         '- `home_position` is dead code still present in `b1/cognition.py` and `home` is still listed in `LOCOMOTION`; a mistyped team key in `policies` silently yields the default vector.',
         '- NOT TESTED by the reviewer: OWN-5, BR-6, BR-7; full-length determinism.', '',
         '## Known weaknesses carried over (not hidden)', '',
         '- Pass completion is low; most decisions are still non-ball decisions (`position` replaces `home`).',
         '- Rosters differ between sides, so side effects exist; all comparisons are side-swapped.',
         '- Delayed public signals (immunity, direct holder) are exact; pass call is the only communication.', '',
         '## Engine-owned choices and primitives that constrain emergence', '', cons, '']
    (ROOT / 'EMERGENCE1_LIMITATIONS.md').write_text('\n'.join(L))
    # ---------------- OWNER BRIEFING
    verdict = 'not evaluated'
    if hs:
        verdict = (f"evolved better on {hs.get('b_pair_wins')} of {hs.get('pairs')} held-out paired seeds, worse on {hs.get('b_pair_losses')}, tied {hs.get('pair_draws')}; mean goal difference {hs.get('mean_goal_diff_per_pair')}; exact sign-test p = {hs.get('sign_test_p')}")
    O = ['# EMERGENCE1 OWNER BRIEFING', '', '**Nothing is ACCEPTED. Experiment evidence only.**', '', head,
         '## 1. Accomplished', '', 'A complete loop runs: parametrized athletes -> parallel paired matches -> search -> held-out comparison -> read-out. The `home` formation grid is gone from decisions; athletes choose positions from their own belief with searched weights.', '',
         '## 2. What B1 can do now', '', '- One match: `python -m b1.match_run --seed 1`; one paired proxy match: `python -m b1.emergence.harness --seeds 1 --period-s 45`; one search: `python -m b1.emergence.search --minutes 15 --pop 8`.', '',
         '## 3. Unimplemented or unproven', '', f'- Held-out result: {verdict}.', '- See `EMERGENCE1_RESULTS.md` for what the read-out shows and `EMERGENCE1_LIMITATIONS.md` for what constrains it.', '',
         '## 4. Blocking', '', '- Compute (4 cores, minutes of search) and the engine-owned choices listed in the limitations.', '',
         '## 5. Recommended action', '', '- Review the exploit log; merge Codex\'s ownership enablers; rerun the search with far more paired seeds (`EMERGENCE1_NEXT_STEPS.md`).', '',
         '## Links', '', *[f'- {URL}/blob/{BR}/{f}' for f in ('EMERGENCE1_RESULTS.md', 'EMERGENCE1_EXPLOIT_LOG.md', 'EMERGENCE1_LIMITATIONS.md', 'EMERGENCE1_IMPLEMENTATION_REPORT.md', 'EMERGENCE1_TEST_REPORT.md', 'EMERGENCE1_NEXT_STEPS.md', 'b1/emergence/README.md', 'b1/emergence/results/INDEPENDENT_REVIEW.md')], '']
    (ROOT / 'EMERGENCE1_OWNER_BRIEFING.md').write_text('\n'.join(O))
    print('reports written from', code, '| held-out:', verdict)


if __name__ == '__main__':
    main()
