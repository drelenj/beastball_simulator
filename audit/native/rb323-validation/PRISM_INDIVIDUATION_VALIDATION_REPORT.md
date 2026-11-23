# RB-3.23 PRISM individuation — independent validation report

## Executive verdict: INCOMPLETE

The inspected implementation runs a deterministic, opt-in rating path and passes the focused suite, the independently rerun RB-3.22 real-seed compatibility fixture, and all six legacy hash rows. Several ratings have isolated causal tests. The evidence does not yet meet the directive's full independent coverage: many effects have only one controlled scenario or option-value evidence, and the requested multi-rating full-match/adversarial matrix is not complete. This report is an engineering recommendation, not owner acceptance.

## Owner briefing

1. I created the validation branch from the implementation commit and independently checked compatibility and legacy replay evidence.
2. The candidate build completes the full real seed-1 compatibility match, with matching trace/state/config hashes and all 260 restarts closed. Focused tests demonstrate several perception, decision, motor, and physics rating effects.
3. The causal matrix is incomplete for physical outcomes and multi-seed distributions. The canonical workbook does not supply independently authored draft ratings, and default mode therefore uses shared .70 fallbacks for them. Unequal/equalized and specialized full-match combinations were not fully tested.
4. No functional blocker was observed in the tested flows. The registry is stale, and the coverage gaps in the matrix remain material for an independent acceptance audit.
5. Recommendation: repair the registry and add matched low/mid/high outcome studies plus representative full-match profiles, then return for owner review. Do not treat this audit as acceptance.

## Branch and source identity

- Validation branch: `codex/rb-3-23-individuation-validation`
- Implementation commit tested: `d1845d022625ddaf6d0f9d5ddc5e60179c63be34`
- Implementation source/test commit: `32ef9dad14ee9407e32d4214edd541867c9b7a6e`
- Verified RB-3.22 parent: `eb30f605f24b906777b88d6cb3a552b3584639ef`, tree `9ef4eff55dd3d91a7f3f11bb65d992545cd0bfa0`; it has the same tree as Claude tip `e6ca6a4e3bc7e76493d6aa2999acb48f4bf9dcc5` (also tree `9ef4eff55dd3d91a7f3f11bb65d992545cd0bfa0`). `git diff-tree` between them returned no paths. The implementation parent is the authorized Codex reconciliation commit.
- Validation commit: recorded after evidence is finalized.
- Branch setup: local validation branch was created from exact implementation head `d1845d0…`. A fresh `git fetch` attempt failed because the managed shell cannot connect through its configured proxy; the pre-existing `origin/codex/rb-3-23-prism-individuation` remote-tracking ref already pointed to that exact commit. Push status is recorded after the upload attempt.

## Coverage summary

The independent status matrix is `PRISM_RATING_TEST_MATRIX.csv`. Counts cover the 16 canonical and 18 draft ratings only: **16 PASS, 18 PARTIAL, 0 FAIL, 0 BLOCKED, 0 UNVERIFIED**. This is a local-mechanism status, not a claim that every rating changes match-level success. Additional fields: Acceleration PASS; Durability and Injury BLOCKED pending authorized trait/state semantics. `passing` is an alias; `kicking` is fixed/no Native action.

Directly exercised transforms are listed in `PRISM_CAUSAL_SENSITIVITY_RESULTS.csv`. No confidence intervals are claimed: most checks are deterministic paired scenarios, not repeated random trials. Formula values are not match-level effect sizes.

## Evidence and commands

Environment: Python 3.12.14, repository `.venv`, with the managed runtime's `openpyxl 3.1.5` added through `PYTHONPATH` because `openpyxl` is absent from the project virtualenv in this environment.

- Focused: `python -m pytest -q native/rulebook/test_individuation.py` with the environment above → **37 passed, 1 warning in 11.24s**. Raw output: `evidence/focused-pytest.txt`.
- Full suite: `python -m pytest -q b1 native` → **699 passed, 1 warning, 23 subtests passed in 799.27s**. Raw output: `evidence/full-pytest.txt`.
- Legacy: `python -m native.rulebook.scoring_audit --legacy`; six rows matched `native/evidence/rb3-reach/legacy-hashes.txt` byte-for-byte (`diff` exit 0). Raw: `evidence/legacy-hashes.txt`.
- Compatibility real seed 1: `python -m native.rulebook.individuation_run --compatibility --seed 1 --out ...`. Final score A 57–B 76, 32,528 steps, restart closure 260/260. Trace `44399b0853ac8a4a87ac7e7c336bd4932219b7969630838c616d6cc458fbc072`; state `046ea55bb1756364ecfdf0f91576ed16cb4052259b7284883e519c61c5f6865d`; config `3d66214c927b42abf493bfe93c9d7ef85675364f54b5e6a9f245daadc4799550`. All six fields compared exactly with committed RB-3.22 fixture. Raw JSON/log in `evidence/compatibility-real.*`.
- New-mode full-match repeatability: two separate fresh-process real seed-1 runs finished, scoring 67–123 in 34,354 steps. Runtime was 173.671 s and 171.794 s. Both have 280/280 restarts closed. Both independently match each other and the two committed implementation runs on status, score, steps, trace, state, and config hashes. Trace `da8e42307e99a2bab2d7925c5903664fd617d19b9b441a1ce49530ff3b1f219d`; state `291c0baff747503c522643fc0c86f57b0403365c6f1bda481c51eb8a08a20d14`; config `51362523dadf2ddcfd41a2af08b3e7da9f579f2819511df309dd00436ab44c4b`.
- Independent benchmark: two 1,500-step windows per mode, alternating mode order over seeds 1 and 3. Median CPU 4.843 ms/step compatibility vs 4.622 ms/step enabled. This small sample shows no measured regression in these windows; it is not a speedup claim. Raw: `evidence/benchmark.json`.

## Data and architectural audit

The code keeps own ratings on the athlete view; tracks expose perceived public state and not private opponent ratings. The poison test passes for equal-position opponent changes. The decision/motor/physics/rulebook boundary is preserved in the inspected flows. Full per-decision replay provenance across all alternatives and rulings is not available, so the end-to-end audit is scenario-based.

The registry `audit/native/rb323/rating-consumers.json` is stale: it describes all 18 draft ratings as inert and omits the active runtime paths/measurements for them. It also leaves active Stamina/Keeper Skill/Archery Accuracy marked inert and Acceleration without a consumer entry. Code and focused tests contain those effects; the registry should be regenerated before downstream use.

Independent ratings are not present in the canonical workbook. Draft ratings default to `.70`; Contact Resistance defaults to Balance in the compatibility NBL adapter. The explicit loader accepts the fields and records provenance, but actual franchise-to-franchise mental/technical variation from authoritative source data is therefore unproven.

## Independence / alias results

- `throw_accuracy` is the single source used for legacy `passing`; no independent Passing effect is introduced.
- Awareness, Vision, and Clarity affect separate horizontal noise, field-of-view, and vertical sample error. Awareness retains a pre-existing Keeper-response use, conceptually adjacent to Reaction; no factorial interaction was run.
- Reaction alters decision scheduling while release preparation, sensor delivery, Keeper course timing, and motor execution remain separate clocks.
- Touch alters vertical pitch allocation; Ball Handling affects release preparation and existing secure physics.
- Finishing changes shot valuation; Throw Accuracy changes release yaw. Goalkeeping changes perceived-course positioning; Keeper Skill changes push-off execution. Their match outcome effects remain unmeasured.
- NBL Contact Resistance is not independent by default because the source workbook lacks it; the current fallback equals Balance. Explicit values remain loadable.
- `kicking` is zeroed by the NBL adapter; there is no Native kick command. Obsolete `kick_power` is rejected by the roster schema. Historical frozen `core_src` contains kicking references, but not on the Native action path tested here.

## Performance and full-match scope

Independent paired bounded benchmark: median CPU was 4.843 ms/step in compatibility and 4.622 ms/step enabled across two 1,500-step windows per mode. This is a small sample and does not support a speedup or equivalence claim. Peak RSS was 102,772 KiB for the four-window benchmark process (not isolated by mode). Full-match wall time was 179.271 s compatibility versus 173.671/171.794 s enabled; the matches diverge in behavior, so this is not a controlled full-match speed comparison. Decision throughput was 851.99 decisions/s compatibility and 823.11/s enabled for the one full run; this is descriptive only. Perception-only cost was not isolated. Full-match robustness across the requested equalized/unequalized and specialized talent combinations, high/low Keeper and Archer profiles, and adversarial edge cases remains UNVERIFIED.

## Defects, limitations, and recommendation

No implementation source was changed. See `PRISM_DEFECT_REGISTER.md` for severity and fixes. The main confirmed defect is the stale machine-readable registry. The main acceptance limitation is incomplete causal outcome evidence: selected-action rates, tackle/catch/save distributions, late-period fatigue and representative profile matchups need controlled tests. For those reasons the recommendation is **repair documentation and expand evidence before owner review**; the owner retains final acceptance authority.
