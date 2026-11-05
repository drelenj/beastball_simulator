import os, sys, json; sys.path.insert(0, '.'); os.environ.setdefault('RULES_V03', '1')
import selfplay_v0 as SP, multiprocessing as mp
if __name__ == '__main__':
    with mp.Pool(int(os.environ.get("NPROC","2"))) as pool: res = pool.map(SP.game, [(SP.BASE, SP.BASE, sd, 60) for sd in range(1, int(os.environ.get("NGAMES","8"))+1)])
    keys = [k for k in res[0]['s']['A'] if isinstance(res[0]['s']['A'][k], (int, float))]
    tot = {k: sum((r['s'][t].get(k) or 0) for r in res for t in 'AB') / len(res) for k in keys}
    print(os.environ.get('THROW_SPLIT'), {k: round(v, 2) for k, v in tot.items() if any(w in k for w in ('shot', 'goal', 'pass', 'complet', 'intercept', 'turnover', 'points_flat', 'tackle_count', 'carry'))})
