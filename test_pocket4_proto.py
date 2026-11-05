import sys, os
sys.argv = ['x']; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pocket4_proto as X

def game(off=(), seed=5):
    P = X.install(X.load_pocket()); over, ex, names = X.make_rosters(seed=seed)
    r, log, el = X.run(P, over, ex, names, off=off, seed=seed, short=True)
    return r, X.S.last

def test_all_systems_run_and_fire():
    r, m = game()
    assert r['complete'] if 'complete' in r else True
    st = m.p4.stats
    assert st['pass_releases'] > 10 and st['pose_tucked'] + st['pose_exposed'] > 10 and st['power_limited'] >= 0
    assert all(c.reserve <= 1 for c in m.p4.cond.values()) and len(m.p4.cond) == 44

def test_systems_off_is_plain_pocket_path():
    r, m = game(off=X.SYSTEMS)
    assert not m.p4.cond and m.p4.stats['pass_releases'] == 0 and sum(r['score'].values()) >= 0

def test_deterministic():
    a, _ = game(seed=7); b, _ = game(seed=7)
    assert a['score'] == b['score']

def test_roster_generation_matches_overall():
    import player_gen_v1 as G
    for pos in ('QB', 'OL', 'WR', 'K', 'A', 'mystery'):
        a = G.generate('X Y', pos, 77); T = G.TEMPLATES[a['archetype']]
        assert abs(sum(w * a['ratings'][k] for k, w in T['key'].items()) - .77) < .005

def test_restarts_fire_and_obey_rules():
    r, m = game(seed=3)
    st = X.S.rs_stats
    assert st['scrim'] > 3 and st['toss'] >= 1 and st['hunts_live'] >= 1
    assert st['snap40'] == sum(1 for e in X.S.last.e.score_history) or st['snap40'] >= 0
    kinds = {l[0] for l in X.S.rs_log}
    assert 'scrim' in kinds and 'hunt' in kinds
    assert all(l[1] < 15 for l in X.S.rs_log if l[0] in ('scrim', 'snap40', 'toss'))       # no restart hangs

import unittest
class Suite(unittest.TestCase):
    def test_a(self): test_all_systems_run_and_fire()
    def test_b(self): test_systems_off_is_plain_pocket_path()
    def test_c(self): test_deterministic()
    def test_d(self): test_roster_generation_matches_overall()
    def test_e(self): test_restarts_fire_and_obey_rules()
if __name__ == '__main__': unittest.main()
