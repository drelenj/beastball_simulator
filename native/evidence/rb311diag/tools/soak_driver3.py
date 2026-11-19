"""Soak driver v3 = r2 driver plus --override field=value and --tag (harness only).

Runner path matches native/rulebook/rb31_soak.py::job, which reproduces the
KNOWN REFERENCE hashes: it calls native/run.py::run_match with a pre-built
instrumented RulebookPort. A per-match step cap is added through max_steps.
Non-finishing matches (cap reached) are recorded, never as completed.
"""
import argparse
import json
import sys
import time
import traceback
from dataclasses import asdict
from pathlib import Path

import os; REPO = os.environ.get('BB_REPO', '/home/claude/wt310')
sys.path.insert(0, REPO)

from native.run import run_match as native_run_match  # noqa: E402
from native.rulebook.config import RulebookConfigV3  # noqa: E402
from native.rulebook.port import RulebookPort  # noqa: E402
from native.rulebook.rb31_soak import measure  # noqa: E402
from native.nbl_roster import load_canon_nbl  # noqa: E402
from native.roster import RATINGS, load_rows  # noqa: E402

CAP_STEPS = 200000


def control_rosters():
    roles = ['field'] * 18 + ['keeper'] * 2 + ['archer'] * 2
    rows = []
    for n, role in enumerate(roles):
        row = {key: .7 for key in RATINGS}
        row.update(id=str(n), role=role, height_m=2.39, mass_kg=226., reach_m=3.05, acceleration=.7)
        rows.append(row)
    return {t: load_rows(rows, t) for t in ('A', 'B')}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--block', choices=('real', 'control'), required=True)
    ap.add_argument('--seed', type=int, required=True)
    ap.add_argument('--outdir', required=True)
    ap.add_argument('--max-steps', type=int, default=CAP_STEPS)
    ap.add_argument('--override', action='append', default=[], help='RulebookConfigV3 field=value (json value)')
    ap.add_argument('--tag', default='')
    a = ap.parse_args()
    out = Path(a.outdir)
    out.mkdir(parents=True, exist_ok=True)
    name = f"{a.block}-seed{a.seed:02d}" + (f'-{a.tag}' if a.tag else '')
    overrides = {k: json.loads(v) for k, v in (o.split('=', 1) for o in a.override)}
    started = time.monotonic()
    rosters = control_rosters() if a.block == 'control' else load_canon_nbl(('Garvian Guardians', 'Ala Apex'))
    cfg = RulebookConfigV3(roster_digests=tuple(rosters[t].digest for t in ('A', 'B')), **overrides)
    carry = []
    try:
        p = RulebookPort(a.seed, cfg, rosters=rosters)
        e = p.m.e
        old = e.rb_carry_attempt

        def count(holder, *args, **kw):
            result = old(holder, *args, **kw)
            if result:
                carry.append((p.m.s.now, holder.team))
            return result
        e.rb_carry_attempt = count
        progress = lambda row: print(json.dumps(dict(name=name, progress=True, **row), sort_keys=True), flush=True)
        r, _ = native_run_match(a.seed, cfg, max_steps=a.max_steps, rosters=rosters,
                                port_factory=lambda *x, **k: p, progress=progress)
        s = p.m.s
        status = r['status']
        try:
            metrics = measure(p, carry)
            metrics['points_check'] = {t: sum(metrics['points'][t].values()) == r['score'][t] for t in ('A', 'B')}
        except Exception as exc:
            metrics = dict(error=repr(exc))
        restart_rows = [row for row in e.log if 'restart' in str(row.get('event', ''))]
        pending = [rid for rid, st in e.restart_results.items() if st == 'pending']
        result = dict(
            name=name, block=a.block, seed=a.seed, status=status, max_steps=a.max_steps,
            score=r['score'], steps=r['steps'], live_ms=r['live_ms'], end_ms=r['end_ms'],
            trace_hash=r['trace_hash'], state_hash=r['state_hash'], config_digest=r['config_digest'],
            restart_completion_ratio=r['restart_completion_ratio'], restart_statuses=r['restart_statuses'],
            foul_reasons=r['foul_reasons'], metrics=metrics, runtime_s=round(time.monotonic() - started, 2),
            entry_point='native/run.py::run_match via rb31_soak.job path (matches reference hashes)',
            non_finishing=None if status == 'final' else dict(
                steps=r['steps'], simulated_ms=r['end_ms'], live_ms=r['live_ms'],
                last_restart_active=asdict(s.restart) if s.restart is not None else None,
                last_restart_event=restart_rows[-1] if restart_rows else None,
                pending_restart_count=len(pending), pending_restart_ids=pending[:20],
                phase=str(s.phase)),
            error=None,
        )
        raw = dict(name=name, log=e.log, calls=e.rb.calls, rb_attempts=e.rb_attempts,
                   restart_results=e.restart_results, possession_history=e.possession_history,
                   possession_ledger=e.possession.ledger, carry_events=carry)
    except Exception as exc:
        result = dict(name=name, block=a.block, seed=a.seed, status='failed', error=repr(exc),
                      traceback=traceback.format_exc(), runtime_s=round(time.monotonic() - started, 2))
        raw = None
    (out / f'{name}.json').write_text(json.dumps(result, indent=2, sort_keys=True, default=str) + '\n')
    if raw is not None:
        (out / f'raw-{name}.json').write_text(json.dumps(raw, default=str) + '\n')
    print(json.dumps({k: result.get(k) for k in ('name', 'status', 'score', 'steps', 'trace_hash', 'state_hash', 'runtime_s')}, sort_keys=True), flush=True)


if __name__ == '__main__':
    main()
