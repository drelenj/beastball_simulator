import unittest, random, math
from prism_perception_v012 import perception_profile, OWNS, RATINGS, Tracker2
from prism_reference import Tracker, cone_probability, radar_probability

class TIsolation(unittest.TestCase):
    def test_each_rating_changes_only_its_own_parameters(self):
        base = {k: .5 for k in RATINGS}; p0 = perception_profile(base)
        for r in RATINGS:
            for v in (.1, .9):
                p1 = perception_profile(dict(base, **{r: v})); changed = {k for k in p0 if abs(p0[k] - p1[k]) > 1e-12}
                self.assertTrue(changed <= OWNS[r], (r, v, changed - OWNS[r]))
                self.assertTrue(changed, (r, v, 'changed nothing'))
    def test_every_parameter_is_owned_by_exactly_one_rating(self):
        keys = set(perception_profile({})); owned = [k for s in OWNS.values() for k in s]
        self.assertEqual(len(owned), len(set(owned))); constants = {'fovea_deg', 'attention_delay_mult', 'radar_extra_delay_s'}
        self.assertEqual(keys - constants, set(owned))
    def test_monotone_directions(self):
        lo, hi = perception_profile({k: .1 for k in RATINGS}), perception_profile({k: .9 for k in RATINGS})
        for k in ('cone_half_angle_deg', 'cone_reach_m', 'radar_radius_m', 'tracked_count', 'gaze_slew_dps', 'belief_tau_s', 'intent_blend', 'options_considered', 'lookahead_s'): self.assertGreater(hi[k], lo[k], k)
        for k in ('delay_s', 'radar_pulse_period_s', 'identify_delay_s', 'classify_delay_s', 'decision_interval_s', 'radar_bearing_sigma_deg', 'cone_noise_scale'): self.assertLess(hi[k], lo[k], k)
    def test_minimum_sensor_sizes(self):
        z = perception_profile({k: 0. for k in RATINGS}); self.assertGreaterEqual(z['cone_half_angle_deg'], 60); self.assertGreaterEqual(z['radar_radius_m'], 3)

class TCone(unittest.TestCase):
    def test_vision_sets_size_clarity_does_not(self):
        self.assertEqual(cone_probability(50, .1, .5) < cone_probability(50, .9, .5), True)       # wider cone keeps more
        self.assertEqual(cone_probability(0, .1, .0), 1.0); self.assertEqual(cone_probability(0, .9, 1.0), 1.0)   # fovea unaffected
        self.assertEqual(cone_probability(60 + 60 * .1 + 1, .1, .5), 0.0); self.assertEqual(cone_probability(60 + 60 * .1 - 3, .1, .5) > 0, True)
    def test_clarity_reaches_zero_at_same_edge(self):
        for c in (0., .5, 1.): self.assertEqual(cone_probability(60 + 60 * .5, .5, c), 0.)

class TTracker(unittest.TestCase):
    def test_no_identity_output(self):
        t = Tracker2(); tr = t.update([(1, 1, 'cone')], 0.)[0]; self.assertFalse(hasattr(tr, 'identity'))
    def test_persistent_track_and_confidence_decay(self):
        t = Tracker2(); a = t.update([(1, 1, 'radar')], 0.)[0].tid; b = t.update([(1.5, 1, 'radar')], .2)[0].tid
        self.assertEqual(a, b); self.assertLess(t.confidence(a, 2.2), t.confidence(a, .2))
    def test_one_to_one(self):
        t = Tracker2(gate=3); t.update([(0, 0, 'cone'), (2, 0, 'cone')], 0.); out = t.update([(.2, 0, 'cone'), (1.8, 0, 'cone')], .1)
        self.assertEqual(len({x.tid for x in out}), 2)
    def test_velocity_prediction_keeps_a_fast_crossing_pair_apart(self):
        # two runners cross head-on at 8 m/s each; nearest-neighbour swaps, predicted-position gating does not
        def swaps(trk, noise=.1, trials=60):
            n = 0; r = random.Random(3)
            for _ in range(trials):
                t = trk(); ids = None
                for k in range(0, 41):
                    tt = k * .1; a = (-2 + 8 * tt + r.gauss(0, noise), r.gauss(0, noise), 'cone'); b = (2 - 8 * tt + r.gauss(0, noise), 0.8 + r.gauss(0, noise), 'cone')
                    obs = [a, b]; res = t.update(obs, tt); cur = tuple(x.track_id if hasattr(x, 'track_id') else x.tid for x in res)
                    if k == 0: ids = cur
                    elif k == 40 and cur != ids: n += 1
            return n
        self.assertLessEqual(swaps(lambda: Tracker2(gate=3)), swaps(lambda: Tracker(gate=3)))
    def test_close_pair_is_flagged_ambiguous_and_clear_pair_is_not(self):
        r = random.Random(5)
        def run(gap):
            t = Tracker2(gate=3); n = 0
            for k in range(0, 30):
                tt = k * .1; res = t.update([(r.gauss(0, .2), r.gauss(0, .2), 'cone'), (gap + r.gauss(0, .2), r.gauss(0, .2), 'cone')], tt)
                n += sum(x.ambiguous for x in res)
            return n
        self.assertGreater(run(.5), 10); self.assertEqual(run(6.0), 0)
    def test_fast_crossing_resolved_by_motion_prediction(self):
        t = Tracker2(gate=3); first = None
        for k in range(0, 41):
            tt = k * .1; res = t.update([(-2 + 8 * tt, 0., 'cone'), (2 - 8 * tt, .3, 'cone')], tt)
            if k == 0: first = [x.tid for x in res]
        self.assertEqual([x.tid for x in res], first)
if __name__ == '__main__': unittest.main()
