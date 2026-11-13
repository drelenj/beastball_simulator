# EMERGENCE1 RESULTS

- Branch `experiment/emergence-1` (https://github.com/drelenj/beastball_simulator/tree/experiment/emergence-1); source commit `c64d92e` (`experiment/prism-sprint-45`); reports generated from commit `2e354573fe1e16ccae28c626d4ed2f56c476406a` (the report commit follows it; see `git log`)
- Clock (`EMERGENCE1_TIMING.log`): first `2026-11-13T13:24:23Z PHASE_A_START`, last `2026-11-13T14:02:18Z PHASE_E_FINAL_COMMIT_PUSH`; cores: 4 (`nproc`)
- Matches: attempted 460, completed 460, failed 0 (search 392, held-out 40, symmetry 20, full-length 8)
- Status words: IMPLEMENTED / TESTED only. **Nothing here is ACCEPTED.** Quality is judged by match results only.

## Search (PROXY matches: 2 x 45 s)

- population 8, generations completed 7, search matches attempted 392, completed 392, failed 0, elapsed 1434.2 s
- one paired, side-swapped seed per pairing per generation (seeds [1000, 1001, 1002, 1003, 1004, 1005, 1006]); fitness = points (3/1/0), then goal difference

| gen | top 3 (label: points, goal diff) | baseline rank |
|---|---|---|
| 0 | g0m2: 39, +70; g0m5: 36, +61; g0m7: 21, -15 | 4 of 8 |
| 1 | g0m2: 39, +87; g0m5: 33, +58; g1m2: 30, +45 | 6 of 8 |
| 2 | g0m2: 30, +20; g1m2: 30, +15; g2m3: 24, +18 | 8 of 8 |
| 3 | g3m4: 33, +74; g0m2: 30, +43; g2m3: 30, +37 | 8 of 8 |
| 4 | g0m2: 36, +55; g2m3: 33, +28; g4m2: 30, +29 | 8 of 8 |
| 5 | g5m4: 33, +63; g5m1: 30, +49; g0m2: 24, +26 | 8 of 8 |
| 6 | g6m2: 33, +51; g5m4: 24, +29; g5m1: 24, +5 | 8 of 8 |

Vector taken to held-out evaluation (best non-baseline of the last completed generation, `g6m2`):

| parameter | baseline | evolved | bounds |
|---|---|---|---|
| `bias_pass` | 0.0 | -6.0 | [-6.0, 6.0] |
| `bias_shoot` | 0.0 | 0.0 | [-6.0, 6.0] |
| `bias_press` | 0.0 | -2.7633 | [-6.0, 6.0] |
| `bias_pursue` | 0.0 | 1.9055 | [-6.0, 6.0] |
| `pass_min_clearance` | 0.0 | 0.0 | [0.0, 6.0] |
| `shot_range` | 32.0 | 31.7171 | [8.0, 60.0] |
| `pos_ball_att` | 0.6 | 0.6 | [-3.0, 3.0] |
| `pos_ball_def` | 1.2 | 3.0 | [-3.0, 3.0] |
| `pos_goal_att` | 1.0 | 1.0852 | [-3.0, 3.0] |
| `pos_goal_def` | 1.0 | -0.5336 | [-3.0, 3.0] |
| `pos_spread` | 1.0 | 2.9973 | [-3.0, 3.0] |
| `pos_opp_att` | 0.6 | 0.6 | [-3.0, 3.0] |
| `pos_opp_def` | 0.6 | 1.3967 | [-3.0, 3.0] |
| `pos_lane` | 0.8 | 0.8 | [-3.0, 3.0] |
| `pos_edge_zone` | 1.0 | 0.0 | [0.0, 3.0] |
| `archer_eager` | 0.0 | 0.0 | [-3.0, 3.0] |

With one seed per pairing per generation the ranking inside a generation is noisy; the search result is a candidate, not a finding. Only the held-out comparison below counts.

## Held-out comparison (seeds never used in the search; PROXY 2 x 45 s)

```
{
 "a": "baseline",
 "b": "evolved",
 "b_match_losses": 3,
 "b_match_wins": 35,
 "b_pair_losses": 1,
 "b_pair_wins": 19,
 "both_sides_pairs": 20,
 "match_draws": 2,
 "matches": 40,
 "mean_goal_diff_per_pair": 9.6,
 "pair_draws": 0,
 "pairs": 20,
 "sign_test_p": 4e-05
}
```

**Evolved vs baseline on 20 held-out paired seeds: evolved better on 19 pairs, worse on 1, tied 0; exact two-sided sign-test p = 4e-05.** The evolved vector beat baseline beyond noise at p < 0.05.

## Proxy vs full-length agreement (small sample)

- full 2 x 120 s, 4 paired seeds: evolved pair wins 4, losses 0, draws 0, mean goal difference 23.5, sign-test p 0.125
- proxy mean goal difference 9.6; direction agrees with full length. With 4 pairs this is a sanity check only, not a validation of the proxy.

## Side-swap symmetry (identical parameters on both sides, PROXY)

- 20 seeds: side A wins 13, side B wins 7, draws 0; A share of decided matches 0.65; mean A goal difference 1.35
- All comparisons above use both side assignments on every seed, so a side bias cancels in the paired unit.

## Emergence read-out (held-out matches, baseline vs evolved)

# EMERGENCE-1 read-out

Rows: 40; by status {'final': 40}. Comparison: `evolved` versus `baseline`.

## Results (the only quality measure)

| quantity | value |
|---|---|
| a | baseline |
| b | evolved |
| pairs | 20 |
| both_sides_pairs | 20 |
| b_pair_wins | 19 |
| pair_draws | 0 |
| b_pair_losses | 1 |
| mean_goal_diff_per_pair | 9.6 |
| sign_test_p | 4e-05 |
| matches | 40 |
| b_match_wins | 35 |
| match_draws | 2 |
| b_match_losses | 3 |

## Descriptive metrics per team-match (mean; n = 40 for `baseline`, 40 for `evolved`)

| metric | baseline | evolved | diff |
|---|---|---|---|
| arrows | 17.45 | 15.7 | -1.75 |
| centroid_ball_dist | 27.3 | 29.151 | 1.851 |
| depth | 65.686 | 70.549 | 4.863 |
| freezes_caused | 0.5 | 0.425 | -0.075 |
| mean_x_attack | 35.413 | 51.285 | 15.872 |
| pass_completed | 4.1 | 0.1 | -4.0 |
| pass_intercepted | 1.425 | 0.0 | -1.425 |
| pass_len_16-24 | 1.1 | 0.125 | -0.975 |
| pass_len_8-16 | 3.55 | 0.075 | -3.475 |
| pass_len_<8 | 3.65 | 0.0 | -3.65 |
| pass_len_>=24 | 0.85 | 0.0 | -0.85 |
| pass_len_mean | 11.277 | 16.067 | 4.79 |
| pass_out | 3.55 | 0.1 | -3.45 |
| pass_released | 9.15 | 0.2 | -8.95 |
| points | 1.25 | 6.05 | 4.8 |
| possession_share | 0.512 | 0.487 | -0.025 |
| press_dist_mean | 10.898 | None | None |
| score | 1.25 | 6.05 | 4.8 |
| shots | 0.525 | 2.45 | 1.925 |
| spread_nn | 12.858 | 13.727 | 0.869 |
| turnovers_lost | 10.675 | 10.725 | 0.05 |
| width | 76.971 | 72.138 | -4.833 |

Decision mix `baseline`: position 57.7%, search 12.3%, pursue 7.6%, keeper_set 7.0%, archer_hold 6.8%, press 2.3%, continue_current 2.3%, scan 1.6%, receive 1.0%, carry 0.5%
Pass network `baseline` (passer slot > target slot, releases): 1>3: 8, 3>6: 8, 0>4: 8, 0>1: 8, 3>4: 7, 4>8: 7, 9>3: 7, 0>2: 7

Decision mix `evolved`: position 61.0%, search 11.2%, pursue 7.4%, keeper_set 7.1%, archer_hold 7.0%, scan 2.2%, continue_current 1.8%, carry 1.5%, draw_release 0.2%, restart_pass 0.2%
Pass network `evolved` (passer slot > target slot, releases): 10>2: 2, 10>7: 2, 10>6: 1, 10>8: 1, 10>4: 1, 4>0: 1

## Plain words

`evolved` vs `baseline` over 20 paired seeds: 19 gained, 1 lost, 0 tied (exact sign-test p = 4e-05, mean goal difference 9.6 per pair).
Metric differences larger than 20% relative (descriptive only; no significance tested for metrics): mean_x_attack 35.413 -> 51.285; pass_completed 4.1 -> 0.1; pass_intercepted 1.425 -> 0.0; pass_len_16-24 1.1 -> 0.125; pass_len_8-16 3.55 -> 0.075; pass_len_<8 3.65 -> 0.0; pass_len_>=24 0.85 -> 0.0; pass_len_mean 11.277 -> 16.067; pass_out 3.55 -> 0.1; pass_released 9.15 -> 0.2; points 1.25 -> 6.05; score 1.25 -> 6.05; shots 0.525 -> 2.45.


## Reproduce

```
pip install scipy numpy pytest
python -m b1.match_run --seed 1                                  # one full match, default parameters
python -m b1.emergence.harness --seeds 1 --period-s 45           # one paired, side-swapped PROXY match
python -m b1.emergence.search --minutes 15 --pop 8 --out b1/emergence/results/search
python -m b1.emergence.final && python -m b1.emergence.report    # held-out, symmetry, full-length sample, reports
python3 -m pytest -q b1
```

## What emerged, in plain words (author's reading of the tables above)

- The search converged on **not passing**: every vector that led a generation carried `bias_pass = -6` (passing switched off). The evolved team carries the ball forward and shoots from close range (`inner_release` goals); on held-out matches it sits about 16 m further up the field than baseline (51 m vs 35 m from its own goal) and takes about 2.5 shots per match against 0.5. Mechanism visible in the metrics: about 0.2 pass releases per match against about 9 for baseline, with the same turnovers lost (10.7 each).
- Out of possession it is pulled hard toward the ball (`pos_ball_def` at its upper bound) and spreads from team-mates (`pos_spread` near its upper bound); it presses less by explicit choice (`bias_press` negative) and contests loose balls more (`bias_pursue` positive). Which of these matter was NOT isolated; only the whole vector was tested.
- No pass network, formation or role structure emerged. Width, depth and spacing differ by less than 10% from baseline.
- This is most likely a statement about the build, not about Beastball: passes are often lost (fixed pass speed, no loft, primitive receivers), so not giving the ball away wins. It is logged as exploit candidate X-4.
- With identical parameters side A won 13 of 20 proxy matches (rosters differ per side); all comparisons are side-swapped, so this cancels in the paired unit.
