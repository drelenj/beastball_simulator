"""CLI: SPRINT-30 N-athlete B1 match / G1 scenario on the real B0 engine."""
import argparse
import json
import time
from pathlib import Path
from .matchport import run_match


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--seed', type=int, default=1)
    ap.add_argument('--scenario', choices=['match', 'g1', 'g1_close'], default='match')
    ap.add_argument('--max-ms', type=int)
    ap.add_argument('--out')
    ap.add_argument('--telemetry-off', action='store_true')
    a = ap.parse_args()
    t = time.perf_counter()
    result, _ = run_match(a.seed, None if a.scenario == 'match' else a.scenario,
                          a.max_ms if a.max_ms else (None if a.scenario == 'match' else 9000),
                          not a.telemetry_off)
    result['wall_s'] = round(time.perf_counter() - t, 3)
    if a.out:
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text(json.dumps(result, sort_keys=True, indent=1) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k not in ('trace', 'final_state', 'engine_events')}, sort_keys=True))


if __name__ == '__main__':
    main()
