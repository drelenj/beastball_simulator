"""Do positions/archetypes matter?  Team X = a role-ablated roster, team Y = the intact roster, same style, same seeds, sides swapped.  positive = the ablated team did better.
python3 ablation_roles.py seeds"""
import sys, os, json, random, multiprocessing as mp
os.environ.setdefault('RULES_V03', '1'); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import selfplay_v0 as SP
N = int(sys.argv[1]) if len(sys.argv) > 1 else 24
def ci(v, rng=random.Random(3)):
    m = sum(v) / len(v); bs = sorted(sum(rng.choice(v) for _ in v) / len(v) for _ in range(2000)); return m, bs[50], bs[1949]
if __name__ == '__main__':
    pool = mp.Pool(2, maxtasksperchild=8); g = SP.clampg(SP.BASE); seeds = list(range(7000, 7000 + N)); out = json.load(open('ablation_roles.json')) if os.path.exists('ablation_roles.json') else {}
    for variant in os.environ.get('VARIANTS', 'mismatch,no_tend,identical,generic').split(','):
        if variant in out: continue
        jobs = []
        for sd in seeds: jobs += [(g, g, sd, 60, (variant, 'A')), (g, g, sd, 60, (variant, 'B'))]     # ablated team is A in the first game, B in the second
        res = pool.map(SP.game, jobs); per = []
        for i in range(len(seeds)):
            a, b = res[2 * i], res[2 * i + 1]
            per.append(SP.fit(a['s'], 'A', 'B') + SP.fit(b['s'], 'B', 'A'))
        m = ci(per); out[variant] = dict(mean=m[0], lo=m[1], hi=m[2], n_games=len(jobs))
        print('%-10s ablated minus intact, per seed-pair: %+.2f  95%% [%+.2f, %+.2f]  (%d games)' % (variant, m[0], m[1], m[2], len(jobs)), flush=True)
        json.dump(out, open('ablation_roles.json', 'w'))
