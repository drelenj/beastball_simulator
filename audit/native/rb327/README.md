# RB-3.27 evidence and reproduction

The engine parent is RB-3.26 at `14b393da76bd24b3655dc539fe7ab4ce2ab73972`. The ratings 0.4 workbook is pinned to `b284e822fa2f23c820987c795a2d780f16334fc3` on `claude/ratings-0-2`. The selection readback records the workbook fingerprint and the selected athlete IDs in `evidence/workbook.json`.

Run commands from the repository root with the simulator's Python environment and `openpyxl` installed. Keep any simultaneous mining, rollout or match workers to a total of two.

```bash
export PYTHONPATH="$PWD${PYTHONPATH:+:$PYTHONPATH}"
work=$(mktemp -d /tmp/rb327.XXXXXX)
source=b284e822fa2f23c820987c795a2d780f16334fc3
book='audit/arcade/ratings/NBL_2026-27_Opening_Night_Rosters_ratings-0.4_overall-trials.xlsx'
git show "$source:$book" > "$work/ratings-0.4.xlsx"
python audit/native/rb327/workbook.py "$work/ratings-0.4.xlsx" --out "$work/workbook.json"
pytest -q b1 native
python -m native.rulebook.scoring_audit --legacy > "$work/legacy.txt"
diff -u native/evidence/rb3-reach/legacy-hashes.txt "$work/legacy.txt"
python -m native.rulebook.individuation_run --compatibility --seed 1 --out "$work/compatibility.json"
python audit/native/rb327/match.py --seed 1 --out "$work/core.json"
```

## Mine, grade and fit

Use the original RB-3.26 capture directory `/workspace/rb326-evidence/mined` or regenerate it with the RB-3.26 checkpoint's mining command from the parent revision. Captured decision snapshots are engine-internal files. Use only snapshots from the trusted match runner. The grading output records the score at the end of the captured possession, observed intermediate action outcomes, stop reasons, and seeds for each option. A fixed watchdog stops an unusually long branch at 120 simulated seconds and keeps its accrued return. A single-option menu is shown separately from ties between options.

```bash
old=/workspace/rb326-evidence/mined
for seed in {4..10}; do
    python -m native.oracle.drill_v1 --old "$old" --new "$work/mined" \
        --grades "$work/grades" --mine "$seed"
done
python -m native.oracle.drill_v1 --old "$old" --new "$work/mined" --grades "$work/grades" --workers 2
python -m native.oracle.fit_v1 --old "$old" --new "$work/mined" --grades "$work/grades" \
    --out "$work/drill" --original-only
python -m native.oracle.fit_v1 --old "$old" --new "$work/mined" --grades "$work/grades" \
    --out "$work/drill" --artifact "$work/drill/drill-v1.json"
```

The fitting command withholds entire matches 9 and 10. It compares each table with the corresponding pooled training-set mean using mean squared prediction error. The replay dataset stores the choice and both regrets for each level using paired decision seeds. The standard error for the high-minus-low true-regret difference uses held-out moments as sampling units, with the 20 seed differences averaged within each moment.

## Regulation runs

The six anchor games use the neutral-real and control roster modes. The ratings 0.4 games use the named franchise pairings in `match.py`. The workbook is read with `technical='explicit'`. `OVR 0.422` orders the 2 Keepers, 2 Archers and 18 field players selected for each franchise's roster. Named ratings supply the runtime inputs. The two primary teams keep their sides across the ten seeds.

```bash
mkdir -p "$work/soak-off"
for pair in {0..5}; do
    count=2
    if [[ $pair == 0 ]]; then count=10; fi
    for ((seed=1; seed<=count; seed++)); do
        python audit/native/rb327/match.py --workbook "$work/ratings-0.4.xlsx" \
            --pair "$pair" --seed "$seed" --out "$work/soak-off/$pair-$seed.json"
    done
done
python audit/native/rb327/batch.py --out "$work" --workbook "$work/ratings-0.4.xlsx" \
    --values "$work/drill/drill-v1.json"
python audit/native/rb327/report.py "$work" --out "$work/report"
```

For single-game use, pass `--drill-values path/to/drill-v1.json` to `python -m native.rulebook.individuation_run`. The value file must accompany the opt-in configuration at match construction. Its SHA-256 is checked at construction and is recorded in the match fingerprint. Later decisions evaluate the loaded numeric tables against the athlete's view and beliefs.

## Timing and evidence checks

The 1,500-step timing pairs use the same archived roster input and the same seeds on both revisions. The reference worktree is RB-3.22 at `eb30f605f24b906777b88d6cb3a552b3584639ef`. Use the same Python executable for both worktrees, put the reference checkout first on its `PYTHONPATH`, and run the timings sequentially. The two seed pairs reverse the timing order.

```bash
repo=$PWD
ref=/path/to/rb322-worktree
for job in '1 rb322' '1 off' '1 on' '3 on' '3 off' '3 rb322'; do
    read -r seed mode <<< "$job"
    if [[ $mode == rb322 ]]; then
        (cd "$ref" && PYTHONPATH="$PWD" python "$repo/audit/native/rb324/bench.py" \
            --mode off --seed "$seed" --out "$work/bench-rb322-$seed.json")
    else
        opt=()
        if [[ $mode == on ]]; then opt=(--values "$work/drill/drill-v1.json"); fi
        python audit/native/rb327/match.py "${opt[@]}" --roster real --steps 1500 \
            --seed "$seed" --out "$work/bench-$mode-$seed.json"
    fi
done
python audit/native/rb327/match.py --values "$work/drill/drill-v1.json" --roster real \
    --steps 1500 --seed 1 --out "$work/bench-on-1-repeat.json"
python audit/native/rb327/verify.py "$work" --workbook "$work/ratings-0.4.xlsx" \
    --artifact "$work/drill/drill-v1.json"
```

CPU timings are recorded with the audit results. The value artifact fingerprints only the sampled games and fitted data, so regenerating identical results on a different machine does not change the loaded artifact digest.
