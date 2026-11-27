"""Same-machine RB-3.22/RB-3.23 bounded-window benchmark."""
import argparse
import json
from pathlib import Path
import statistics
import time

from native.individuation import VERSION
from native.nbl_roster import load_canon_nbl
from native.rulebook.config import RulebookConfigV3
from native.rulebook.port import RulebookPort
from native.run import run_match


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--steps', type=int, default=1500)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    rosters = load_canon_nbl(('Garvian Guardians', 'Ala Apex'))
    digests = tuple(rosters[side].digest for side in ('A', 'B'))
    runs = {}
    for seed in (1, 3):
        for mode in ('off', VERSION) if seed == 1 else (VERSION, 'off'):
            cfg = RulebookConfigV3(tackles_per_possession=2, roster_digests=digests, individuation=mode)
            start = time.process_time()
            result, _ = run_match(seed, cfg, rosters=rosters, max_steps=args.steps,
                                  port_factory=RulebookPort)
            elapsed = time.process_time() - start
            runs.setdefault(mode, []).append(dict(
                seed=seed, steps=result['steps'], live_ms=result['live_ms'],
                cpu_seconds=elapsed, cpu_ms_per_step=elapsed * 1000 / result['steps'],
                trace_hash=result['trace_hash'], state_hash=result['state_hash'],
                config_digest=result['config_digest']))
    args.out.write_text(json.dumps(dict(
        runs=runs, median_cpu_ms_per_step={
            mode: statistics.median(r['cpu_ms_per_step'] for r in cases)
            for mode, cases in runs.items()
        }), indent=2) + '\n')


if __name__ == '__main__':
    main()
