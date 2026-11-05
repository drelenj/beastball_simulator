"""Paired bounce test: same style/roster/seeds, sides swapped; only the bounce genes differ (X vs plain).  python3 bounce_test.py seeds"""
import sys, os, json, random, multiprocessing as mp
os.environ.setdefault('RULES_V03', '1'); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import selfplay_v0 as SP
N = int(sys.argv[1]) if len(sys.argv) > 1 else 24
def ci(v, rng=random.Random(3)):
    m = sum(v) / len(v); bs = sorted(sum(rng.choice(v) for _ in v) / len(v) for _ in range(2000)); return m, bs[50], bs[1949]
if __name__ == '__main__':
    pool = mp.Pool(2, maxtasksperchild=8); g = SP.clampg(SP.BASE); seeds = list(range(8000, 8000 + N)); out = json.load(open('bounce_test.json')) if os.path.exists('bounce_test.json') else {}
    for label, kw in (('dribble only', dict(dribble_rate=1.)), ('skip only', dict(skip_rate=1.)), ('bounce shot only', dict(bounce_shot_rate=1.)), ('all three', dict(dribble_rate=1., skip_rate=1., bounce_shot_rate=1.))):
        if label in out: continue
        gx = dict(g, **kw); jobs = []
        for sd in seeds: jobs += [(gx, g, sd, 60), (g, gx, sd, 60)]
        res = pool.map(SP.game, jobs); per = []; goals_x = goals_y = 0
        for i in range(len(seeds)):
            a, b = res[2 * i], res[2 * i + 1]; per.append(SP.fit(a['s'], 'A', 'B') + SP.fit(b['s'], 'B', 'A'))
        m = ci(per); out[label] = dict(mean=m[0], lo=m[1], hi=m[2], n_games=len(jobs))
        print('%-17s vs plain, per seed-pair: %+.2f  95%% [%+.2f, %+.2f]  (%d games)' % (label, m[0], m[1], m[2], len(jobs)), flush=True)
        json.dump(out, open('bounce_test.json', 'w'))
