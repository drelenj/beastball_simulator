"""EMERGENCE-1 tournament harness: paired, side-swapped matches in parallel.

Each match is an independent process-local run (own engine, own RNG from the seed),
so results do not depend on worker count or completion order.
Provenance: 761dca5. Native requires four 600 s periods; no old results or evolved vectors are imported.
"""
import argparse
import json
import multiprocessing as mp
import os
import sys
import time
import traceback
from pathlib import Path

from .params import PolicyParams, DEFAULT

FULL_PERIOD_S = 600

def measurement_config():
    """Current owner-directed measurement basis; legacy Native is replay-only."""
    from ..rulebook.config import RulebookConfig
    return RulebookConfig()


def job(seed, period_s, label_a, params_a, label_b, params_b):
    return {'id': f'{seed}:{period_s}:{label_a}>{label_b}', 'seed': int(seed), 'period_s': int(period_s),
            'label_A': label_a, 'params_A': params_a.as_dict(), 'label_B': label_b, 'params_B': params_b.as_dict()}


def paired_jobs(seeds, period_s, label_a, params_a, label_b, params_b):
    """Both side assignments on every seed."""
    out = []
    for s in seeds:
        out.append(job(s, period_s, label_a, params_a, label_b, params_b))
        out.append(job(s, period_s, label_b, params_b, label_a, params_a))
    return out


def held_out_jobs(training_seeds, held_out_seeds, label_a, params_a, label_b, params_b):
    if set(training_seeds) & set(held_out_seeds):
        raise ValueError('held-out seeds must be disjoint')
    return paired_jobs(held_out_seeds,FULL_PERIOD_S,label_a,params_a,label_b,params_b)


def play(j):
    if j['period_s'] != FULL_PERIOD_S:
        raise ValueError('Native harness requires full canon duration')
    config = measurement_config()
    t = time.perf_counter()
    row = {k: j[k] for k in ('id', 'seed', 'period_s', 'label_A', 'label_B', 'params_A', 'params_B')}
    row['proxy'] = j['period_s'] != FULL_PERIOD_S
    row.update(config=config.record(), config_digest=config.digest)
    try:
        from ..rulebook.run import run_match
        try:
            from .metrics import MetricsCollector
            mc = MetricsCollector()
        except Exception:
            mc = None
        pol = {'A': PolicyParams.from_dict(j['params_A']), 'B': PolicyParams.from_dict(j['params_B'])}
        r, port = run_match(j['seed'], config=config, policies=pol)
        assert r['rulebook']['scoring_basis']['mode']=='banded'
        sc = r['score']
        res = getattr(port.m.s, 'result', None) or {}
        row.update(status=r['status'], score=sc, method=res.get('method'),
                   effective=r['effective'],
                   winner=res.get('winner') if res.get('winner') in ('A', 'B') else ('A' if sc['A'] > sc['B'] else 'B' if sc['B'] > sc['A'] else None),
                   trace_hash=r['trace_hash'], state_hash=r['state_hash'], end_ms=r['end_ms'],
                   decisions_total=r['decisions_total'], decisions_by_kind=r['decisions_by_kind'],
                   outcomes_by_status=r['outcomes_by_status'], rules_ledger_by_row=r['rules']['ledger_by_row'],
                   metrics=mc.finalize(port) if mc else None)
    except Exception as exc:                       # a crashed match is reported, never hidden
        row.update(status='crashed', error=repr(exc), traceback=traceback.format_exc()[-1500:])
    row['wall_s'] = round(time.perf_counter() - t, 2)
    return row


def run_jobs(jobs, out=None, workers=None, serial=False):
    """Returns rows sorted by job id (order-independent). Appends to `out` as matches finish."""
    workers = workers or os.cpu_count() or 1
    rows = []
    fh = open(out, 'a') if out else None

    def keep(row):
        rows.append(row)
        if fh:
            fh.write(json.dumps(row, sort_keys=True) + '\n')
            fh.flush()
    if serial or workers == 1:
        for j in jobs:
            keep(play(j))
    else:
        with mp.get_context('fork').Pool(workers, maxtasksperchild=8) as pool:
            for row in pool.imap_unordered(play, jobs, chunksize=1):
                keep(row)
    if fh:
        fh.close()
    return sorted(rows, key=lambda r: r['id'])


def main():
    ap = argparse.ArgumentParser(description='Paired side-swapped matches: params A vs params B.')
    ap.add_argument('--seeds', type=int, nargs='+', default=[1])
    ap.add_argument('--period-s', type=int, default=600, help='600 only: four full Native periods')
    ap.add_argument('--a-json', help='PolicyParams JSON for label a (default: baseline)')
    ap.add_argument('--b-json', help='PolicyParams JSON for label b (default: baseline)')
    ap.add_argument('--a-label', default='baseline')
    ap.add_argument('--b-label', default='other')
    ap.add_argument('--out')
    ap.add_argument('--serial', action='store_true')
    ap.add_argument('--workers', type=int)
    a = ap.parse_args()
    load = lambda p: PolicyParams.from_dict(json.loads(Path(p).read_text())) if p else DEFAULT
    if a.out:
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    rows = run_jobs(paired_jobs(a.seeds, a.period_s, a.a_label, load(a.a_json), a.b_label, load(a.b_json)),
                    a.out, a.workers, a.serial)
    for r in rows:
        print(json.dumps({k: r.get(k) for k in ('id', 'status', 'score', 'winner', 'method', 'trace_hash', 'wall_s', 'error')}, sort_keys=True))


if __name__ == '__main__':
    main()
