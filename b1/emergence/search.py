"""EMERGENCE-1 search: small population, round-robin on paired side-swapped seeds,
keep the best, mutate, repeat until the time budget is spent. Fitness = match results only.
PRIMITIVE: (mu + lambda)-style with a fixed baseline anchor; one paired seed per pairing per generation.
"""
import argparse
import itertools
import json
import random
import time
from pathlib import Path

from .harness import job, run_jobs
from .params import BOUNDS, NAMES, DEFAULT, PolicyParams, clip


def mutate(p, rng, scale=.25, n_dims=5):
    d = p.as_dict()
    for name in rng.sample(NAMES, n_dims):
        lo, hi = BOUNDS[name][:2]
        d[name] = clip(name, d[name] + rng.gauss(0., scale * (hi - lo)))
    return PolicyParams.from_dict(d)


def standings(labels, rows):
    """Results only: points (3/1/0), goal difference, goals for."""
    t = {l: {'label': l, 'played': 0, 'points': 0, 'gd': 0, 'gf': 0, 'w': 0, 'd': 0, 'l': 0} for l in labels}
    for r in rows:
        if r.get('status') != 'final':
            continue
        for side, other in (('A', 'B'), ('B', 'A')):
            e = t[r['label_' + side]]
            gf, ga = r['score'][side], r['score'][other]
            e['played'] += 1
            e['gf'] += gf
            e['gd'] += gf - ga
            if r['winner'] == side:
                e['points'] += 3
                e['w'] += 1
            elif r['winner'] is None:
                e['points'] += 1
                e['d'] += 1
            else:
                e['l'] += 1
    return sorted(t.values(), key=lambda e: (-e['points'], -e['gd'], -e['gf'], e['label']))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--minutes', type=float, default=15.)
    ap.add_argument('--pop', type=int, default=8)
    ap.add_argument('--period-s', type=int, default=45)
    ap.add_argument('--seed', type=int, default=20261113)
    ap.add_argument('--seed-base', type=int, default=1000, help='search seeds are seed_base + generation')
    ap.add_argument('--out', default='b1/emergence/results/search')
    ap.add_argument('--workers', type=int)
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    rng = random.Random(a.seed)
    t0 = time.time()
    budget = a.minutes * 60
    pop = {'baseline': DEFAULT}
    n = 0
    while len(pop) < a.pop:
        n += 1
        pop[f'g0m{n}'] = mutate(DEFAULT, rng, .3, 6)
    history, attempted, completed, failed, gen, gen_wall = [], 0, 0, 0, 0, None
    while True:
        if gen_wall is not None and time.time() - t0 + gen_wall * 1.1 > budget:
            break
        g0 = time.time()
        match_seed = a.seed_base + gen
        labels = sorted(pop)
        jobs = []
        for x, y in itertools.combinations(labels, 2):
            jobs += [job(match_seed, a.period_s, x, pop[x], y, pop[y]), job(match_seed, a.period_s, y, pop[y], x, pop[x])]
        rows = run_jobs(jobs, str(out / 'matches.jsonl'), a.workers)
        attempted += len(jobs)
        completed += sum(r.get('status') == 'final' for r in rows)
        failed += sum(r.get('status') != 'final' for r in rows)
        table = standings(labels, rows)
        gen_wall = time.time() - g0
        history.append({'generation': gen, 'match_seed': match_seed, 'wall_s': round(gen_wall, 1), 'matches': len(jobs),
                        'standings': table, 'population': {l: pop[l].as_dict() for l in labels}})
        ranked = [e['label'] for e in table]
        elites = ranked[:3]
        best = elites[0]
        state = {'search_seed': a.seed, 'period_s': a.period_s, 'proxy': a.period_s != 120, 'pop': a.pop,
                 'generations_completed': gen + 1, 'attempted': attempted, 'completed': completed, 'failed': failed,
                 'elapsed_s': round(time.time() - t0, 1), 'best_label': best, 'best_params': pop[best].as_dict(),
                 'best_non_baseline_label': next(l for l in ranked if l != 'baseline'),
                 'best_non_baseline_params': pop[next(l for l in ranked if l != 'baseline')].as_dict(),
                 'search_seeds_used': [a.seed_base + g for g in range(gen + 1)], 'history': history}
        (out / 'search_state.json').write_text(json.dumps(state, sort_keys=True, indent=1) + '\n')
        print(json.dumps({'gen': gen, 'wall_s': round(gen_wall, 1), 'top': table[:3], 'failed': failed}), flush=True)
        # next generation: baseline anchor + elites + mutants of elites
        gen += 1
        nxt = {'baseline': DEFAULT}
        for l in elites:
            nxt[l] = pop[l]
        k = 0
        while len(nxt) < a.pop:
            k += 1
            parent = elites[(k - 1) % len(elites)]
            nxt[f'g{gen}m{k}'] = mutate(pop[parent], rng)
        pop = nxt
    print(json.dumps({'done': True, 'generations': gen, 'attempted': attempted, 'completed': completed, 'failed': failed}))


if __name__ == '__main__':
    main()
