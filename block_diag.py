"""contact rate of assigned blockers: naive vs predictive aim.  python3 block_diag.py seeds"""
import sys, os, collections, multiprocessing as mp
os.environ.setdefault('RULES_V03', '1'); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import selfplay_v0 as SP
def one(a):
    mode, sd = a; os.environ['BLOCK_MODE'] = mode
    g = SP.clampg(dict(SP.BASE, block_rate=1., block_reach=12.)); return mode, SP.game((g, SP.clampg(SP.BASE), sd, 60))
if __name__ == '__main__':
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 10; pool = mp.Pool(2, maxtasksperchild=4)
    res = pool.map(one, [(m, 6000 + i) for i in range(N) for m in ('naive', 'persist')])
    tot = collections.defaultdict(collections.Counter)
    for m, r in res:
        tot[m]['games'] += 1; tot[m]['pairs'] += r['blk']['pairs']; tot[m]['hit'] += r['blk']['pairs_with_contact']; tot[m]['blocks_off'] += r['s']['A']['blocks_offence']
    for m, c in tot.items(): print(m, dict(c), 'contact rate %.0f%%' % (100 * c['hit'] / max(1, c['pairs'])), 'offence blocks/game %.1f' % (c['blocks_off'] / c['games']))
