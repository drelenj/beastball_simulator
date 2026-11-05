import unittest, math, prism_archer_v0 as PR
EYE = (-5., 50., 15. + .72 * 2.5)
def body(i, x, y, h=2.5, r=.43): return dict(id=i, x=x, y=y, z=0., h=h, r=r)
def run(pr, bodies, secs=3., focus=(40., 50.), step=.1, face=0.):
    t = 0.; seen = []
    while t <= secs: seen += pr.tick(t, EYE, face, bodies, focus); t += step
    return seen
class T(unittest.TestCase):
    def test_1_occluded_target_never_detected(self):
        # blocker on the sight line right in front of the target: from 15 m up the shadow behind a 2.5 m body is ~3.6 m at 50 m range
        tgt = body('T', 50., 50.); blk = body('B', 49., 50., h=3.2)
        pr = PR.ArcherPrism(1, .9, .25); seen = run(pr, [tgt, blk], 5.)
        self.assertNotIn('T', seen); self.assertIn('B', seen); self.assertEqual(pr.stats['occluded'] >= 1, True)
    def test_2_same_target_seen_when_blocker_moves_away(self):
        tgt = body('T', 50., 50.); blk = body('B', 40., 50.)
        seen = run(PR.ArcherPrism(1, .9, .25), [tgt, blk], 2.); self.assertIn('T', seen)
    def test_3_outside_field_of_view_not_detected(self):
        behind = body('X', -30., 50.)          # behind the platform, archer faces +x
        self.assertNotIn('X', run(PR.ArcherPrism(1, .9, .25), [behind], 3.))
    def test_4_beliefs_are_stale_and_wrong(self):
        pr = PR.ArcherPrism(2, .7, .3); b = body('T', 30., 50.); run(pr, [b], 2.)
        bel = pr.bel['T']; self.assertGreater(pr.latency_s, 0)
        b['x'] = 45.                                          # target moves; archer has not looked since
        self.assertAlmostEqual(bel.at(2.0)[0] - 30., 0., delta=1.0); self.assertGreater(abs(bel.at(2.0)[0] - b['x']), 5.)
        self.assertLess(pr.confidence('T', 2.0), 1.0); self.assertLess(pr.confidence('T', 9.0), .1)
    def test_5_awareness_changes_error_and_latency(self):
        def err(aw):
            e = []
            for seed in range(30):
                pr = PR.ArcherPrism(seed, aw, .25); b = body('T', 45., 55.); run(pr, [b], 1.5, focus=(45., 55.)); bl = pr.bel.get('T')
                if bl: e.append(math.hypot(bl.x - 45., bl.y - 55.))
            return sum(e) / len(e)
        self.assertLess(err(.95), err(.5)); self.assertLess(PR.ArcherPrism(1, .95, .25).latency_s, PR.ArcherPrism(1, .5, .25).latency_s)
    def test_6_deterministic(self):
        def go(): pr = PR.ArcherPrism(7, .8, .25); b = [body('T', 45., 55.), body('U', 30., 40.)]; run(pr, b, 2.); return {k: (v.x, v.y) for k, v in pr.bel.items()}
        self.assertEqual(go(), go())

class TInference(unittest.TestCase):
    def _track(self, aw, mover, secs=3., seed=3):
        pr = PR.ArcherPrism(seed, aw, .25); b = body('T', 30., 50.); t = 0.
        while t <= secs:
            mover(b, t); pr.tick(t, EYE, 0., [b], (b['x'], b['y'])); t += .1
        return pr, t
    def test_7_straight_runner_more_predictable_than_zigzag(self):
        def straight(b, t): b['x'] = 30. + 8. * t; b['y'] = 50.
        def zig(b, t): b['x'] = 30. + 8. * t; b['y'] = 50. + 4. * math.sin(t * 6.)
        ps, t = self._track(.9, straight); pz, _ = self._track(.9, zig)
        self.assertGreater(ps.p_hit('T', t, .2, 50.), pz.p_hit('T', t, .2, 50.))
    def test_8_hit_probability_falls_with_horizon_and_rises_with_awareness(self):
        def straight(b, t): b['x'] = 30. + 8. * t; b['y'] = 50.
        pr, t = self._track(.9, straight)
        self.assertGreater(pr.p_hit('T', t, .1, 50.), pr.p_hit('T', t, 1.0, 50.))
        lo, tl = self._track(.5, straight)
        self.assertGreaterEqual(pr.p_hit('T', t, .3, 50.), lo.p_hit('T', tl, .3, 50.) - 1e-9)
    def test_9_untracked_player_has_zero_hit_probability(self):
        self.assertEqual(PR.ArcherPrism(1, .9, .25).p_hit('nobody', 1., .2, 40.), 0.)

if __name__ == '__main__': unittest.main()
