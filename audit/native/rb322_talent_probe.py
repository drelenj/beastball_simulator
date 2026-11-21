"""Recompute the RB-3.22 talent decomposition from per-match results."""
import argparse
import gzip
import json
import shutil
import statistics
import subprocess
import sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

MODES = ("default", "tech_neutral", "phys_neutral", "both_neutral")
OVERRIDES = dict(
    default=(),
    tech_neutral=('rb322_technical_source="neutral"',),
    phys_neutral=('rb322_physical_source="neutral"',),
    both_neutral=('rb322_technical_source="neutral"', 'rb322_physical_source="neutral"'),
)


def fill(root, source, jobs, modes, seeds):
    def run(case):
        mode, seed = case
        out = root / mode / "real"
        name = f"real-seed{seed:02d}"
        result = out / (name + ".json")
        if result.exists():
            if json.loads(result.read_text())["status"] != "final":
                raise ValueError(f"{result}: existing run is incomplete")
            return
        out.mkdir(parents=True, exist_ok=True)
        command = [sys.executable, "-m", "native.rulebook.reach_run", "--block", "real",
                   "--seed", str(seed), "--outdir", str(out)]
        for override in OVERRIDES[mode]:
            command.extend(("--override", override))
        with (out / f"{name}.stdout").open("w") as stdout:
            subprocess.run(command, cwd=source, stdout=stdout, stderr=subprocess.STDOUT, check=True)
        raw = out / f"raw-{name}.json"
        if raw.exists():
            with raw.open("rb") as src, gzip.open(raw.with_suffix(".json.gz"), "wb") as dst:
                shutil.copyfileobj(src, dst)
            raw.unlink()
        record = json.loads(result.read_text())
        print(mode, seed, record["status"], record.get("score"), flush=True)
        if record["status"] != "final":
            raise ValueError(f"{result}: match did not finish")

    cases = [(mode, seed) for seed in seeds for mode in modes]
    with ThreadPoolExecutor(max_workers=jobs) as pool:
        list(pool.map(run, cases))


def verify_raw(source, row):
    with gzip.open(source, "rt") as log:
        raw = json.load(log)
    points = Counter()
    for event in raw["log"]:
        if event["event"] in ("goal", "foul_award"):
            points[event["data"]["team"]] += event["data"]["points"]
    possessions = Counter(entry["team"] for entry in
                          raw["possession_history"] + raw["possession_ledger"]
                          if entry["event"] == "passive_possession"
                          or (entry["event"] == "restart_awarded" and entry.get("pp_changed")))
    for side in ("A", "B"):
        if points[side] != row["score"][side] or possessions[side] != row["metrics"]["possessions"][side]["count"]:
            raise ValueError(f"{source}: raw logs disagree with the reported score or possessions for {side}")


def summarize(root, allow_partial=False, check_raw=False):
    data = {}
    for mode in MODES:
        scores = {side: [] for side in ("A", "B")}
        possessions = []
        seeds = []
        for seed in range(1, 11):
            source = root / mode / "real" / f"real-seed{seed:02d}.json"
            if not source.exists() and allow_partial:
                continue
            row = json.loads(source.read_text())
            if row["seed"] != seed or row["status"] != "final":
                raise ValueError(f"{source}: wrong seed or incomplete match")
            if check_raw:
                verify_raw(source.with_name("raw-" + source.name + ".gz"), row)
            seeds.append(seed)
            for side in scores:
                scores[side].append(row["score"][side])
                possessions.append(row["metrics"]["possessions"][side]["count"])
        margins = [b - a for a, b in zip(scores["A"], scores["B"], strict=True)]
        if not margins:
            continue
        all_scores = scores["A"] + scores["B"]
        data[mode] = dict(
            seeds=seeds,
            median_team_score=statistics.median(all_scores),
            mean_possessions_per_team=statistics.mean(possessions),
            ala_mean_margin=statistics.mean(margins),
            ala_wins=sum(m > 0 for m in margins),
            ties=margins.count(0),
            sample_sd_garvian=statistics.stdev(scores["A"]) if len(margins) > 1 else None,
            sample_sd_ala=statistics.stdev(scores["B"]) if len(margins) > 1 else None,
            sample_sd_all=statistics.stdev(all_scores),
        )
    return data


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    parser.add_argument("--allow-partial", action="store_true")
    parser.add_argument("--verify-raw", action="store_true")
    parser.add_argument("--run-missing", choices=MODES, nargs="+")
    parser.add_argument("--source", type=Path, default=Path.cwd())
    parser.add_argument("--jobs", type=int, choices=(1, 2), default=1)
    parser.add_argument("--seeds", nargs="+", type=int, choices=range(1, 11), default=range(1, 11))
    args = parser.parse_args()
    if args.run_missing:
        fill(args.root.resolve(), args.source.resolve(), args.jobs, args.run_missing, args.seeds)
    print(json.dumps(summarize(args.root, args.allow_partial, args.verify_raw), indent=2))
