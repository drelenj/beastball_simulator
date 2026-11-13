"""EMERGENCE-1 final evaluation on seeds never used by the search:
held-out proxy comparison, side-symmetry check, and proxy-vs-full agreement sample."""
import argparse
import json
import time
from pathlib import Path

from .harness import job, paired_jobs, run_jobs
from .params import DEFAULT, PolicyParams


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--state', default='b1/emergence/results/search/search_state.json')
    ap.add_argument('--out', default='b1/emergence/results')
    ap.add_argument('--heldout', type=int, default=20)
    ap.add_argument('--symmetry', type=int, default=20)
    ap.add_argument('--full', type=int, default=4)
    ap.add_argument('--period-s', type=int, default=45)
    a = ap.parse_args()
    out = Path(a.out)
    st = json.loads(Path(a.state).read_text())
    best = PolicyParams.from_dict(st['best_non_baseline_params'])
    used = set(st['search_seeds_used'])
    held = [9000 + i for i in range(a.heldout)]
    sym = [7000 + i for i in range(a.symmetry)]
    full = [8000 + i for i in range(a.full)]
    assert not used & set(held + sym + full), 'held-out seeds overlap search seeds'
    t = time.time()
    # one pool: order of completion does not matter
    jobs = (paired_jobs(held, a.period_s, 'baseline', DEFAULT, 'evolved', best)
            + [job(s, a.period_s, 'baseline', DEFAULT, 'baseline', DEFAULT) for s in sym]
            + paired_jobs(full, 120, 'baseline', DEFAULT, 'evolved', best))
    for name in ('heldout.jsonl', 'symmetry.jsonl', 'full_length.jsonl'):
        (out / name).unlink(missing_ok=True)
    rows = run_jobs(jobs)
    files = {'heldout.jsonl': [], 'symmetry.jsonl': [], 'full_length.jsonl': []}
    for r in rows:
        key = 'full_length.jsonl' if r['period_s'] == 120 else 'symmetry.jsonl' if r['label_A'] == r['label_B'] else 'heldout.jsonl'
        files[key].append(r)
    for name, rs in files.items():
        (out / name).write_text(''.join(json.dumps(r, sort_keys=True) + '\n' for r in rs))
    ok = lambda rs: [r for r in rs if r.get('status') == 'final']
    s = ok(files['symmetry.jsonl'])
    summary = {'evolved_label_in_search': st['best_non_baseline_label'], 'evolved_params': best.as_dict(),
               'heldout_seeds': held, 'symmetry_seeds': sym, 'full_length_seeds': full, 'wall_s': round(time.time() - t, 1),
               'attempted': len(jobs), 'completed': len(ok(rows)), 'failed': len(rows) - len(ok(rows)),
               'symmetry': {'matches': len(s), 'A_wins': sum(r['winner'] == 'A' for r in s), 'B_wins': sum(r['winner'] == 'B' for r in s),
                            'draws': sum(r['winner'] is None for r in s),
                            'A_goal_diff_mean': round(sum(r['score']['A'] - r['score']['B'] for r in s) / max(1, len(s)), 3)}}
    (out / 'final_summary.json').write_text(json.dumps(summary, sort_keys=True, indent=1) + '\n')
    print(json.dumps(summary, sort_keys=True))


if __name__ == '__main__':
    main()
