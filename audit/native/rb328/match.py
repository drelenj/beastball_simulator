"""Run one ratings 0.4 regulation game and record participation."""
import argparse
from dataclasses import replace
import json
from pathlib import Path
from time import process_time

from audit.native.rb327.match import PAIRS, real_build

from native.rulebook.rb31_soak import measure


def run(build, enabled, steps=None, benchmark=False):
    start = process_time()
    build = replace(build, config=replace(build.config, fatigue_rotation=enabled))
    driver = build.create(record=False)
    port = driver.port
    s, engine = port.m.s, port.m.e
    minutes = {p.id: dict(role=p.role, starter=p.active, live_ms=0, regulation_ms=0)
               for p in s.players.values()}
    if not enabled and not benchmark:
        old_step = port.step
        regulation = port.config.periods * port.config.period_seconds * 1000

        def observe_minutes():
            start_live = s.live_ms
            active = tuple(p.id for p in s.players.values() if p.active)
            old_step()
            delta = s.live_ms - start_live
            if delta:
                for pid in active:
                    minutes[pid]['live_ms'] += delta
                    minutes[pid]['regulation_ms'] += min(s.live_ms, regulation) - min(start_live, regulation)

        port.step = observe_minutes

    carries = []
    original = engine.rb_carry_attempt
    if not benchmark:
        def observe_attempt(holder, *args, **kwargs):
            outcome = original(holder, *args, **kwargs)
            if outcome:
                carries.append((s.now, holder.team))
            return outcome

        engine.rb_carry_attempt = observe_attempt
    driver.play(steps)
    result = driver.result()
    result['cpu_ms_per_step'] = (process_time() - start) * 1000 / result['steps']
    result.pop('prism_commits', None)
    result['participation'] = result.pop('rotation', minutes)
    result['rules_substitutions'] = [r for r in engine.rb.calls if r['kind'] == 'substitution']
    result.update(measure(port, carries))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workbook', type=Path, required=True)
    parser.add_argument('--seed', type=int, required=True)
    parser.add_argument('--pair', type=int, choices=range(len(PAIRS)), default=0)
    parser.add_argument('--on', action='store_true')
    parser.add_argument('--steps', type=int)
    parser.add_argument('--benchmark', action='store_true')
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    build = real_build(args.seed, args.pair, args.workbook)
    row = run(build, args.on, args.steps, args.benchmark)
    row['teams'] = PAIRS[args.pair]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    scratch = args.out.with_suffix('.tmp')
    scratch.write_text(json.dumps(row, sort_keys=True) + '\n')
    scratch.replace(args.out)
    print(args.out, row['score'], row['status'], flush=True)


if __name__ == '__main__':
    main()
