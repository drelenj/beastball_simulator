import unittest, random
import pose_maneuvers_v0 as M
def run(c, ms): c.step(ms); return c
def starts(c): return [e for e in c.log if e[1] == 'start']
class TLadder(unittest.TestCase):
    def test_adjacent_steps_only(self):
        c = M.Carrier('loaded'); c.request_pose('braced'); run(c, 4 * M.STEP_MS)
        self.assertEqual([e[2] for e in c.log if e[1] == 'pose'], ['extended', 'exposed', 'tucked', 'braced'])
    def test_loaded_to_exposed_costs_two_steps(self):
        c = M.Carrier('loaded'); c.request_pose('exposed'); run(c, 299); self.assertEqual(c.pose, 'extended'); run(c, 1); self.assertEqual(c.pose, 'exposed')
    def test_strip_resistance_order(self):
        v = [M.STRIP_RESIST[p] for p in M.POSES]; self.assertEqual(v, sorted(v))
        c = M.Carrier('tucked'); c.request_pose('exposed'); run(c, 10); self.assertLess(c.strip_resistance(), M.STRIP_RESIST['exposed'])
class TEligibility(unittest.TestCase):
    def _go(self, pose, kind):
        c = M.Carrier(pose); prep = c.start_maneuver(kind); run(c, 3000); return c, prep
    def test_juke_from_loaded_goes_via_extended_at_015s(self):
        c, prep = self._go('loaded', 'juke'); st = starts(c)[0]; self.assertEqual(prep, 150)
        self.assertEqual([e[2] for e in c.log if e[1] == 'pose'][:1], ['extended']); self.assertGreaterEqual(st[0], 150 + M.TELL_MS['juke'])
    def test_spin_from_loaded_needs_exposed_030s(self):
        c, prep = self._go('loaded', 'spin'); self.assertEqual(prep, 300); self.assertEqual([e[2] for e in c.log if e[1] == 'pose'][:2], ['extended', 'exposed'])
    def test_spin_from_extended_is_not_enough(self):
        c, prep = self._go('extended', 'spin'); self.assertEqual(prep, 150); self.assertIn(('pose', 'exposed'), [(e[1], e[2]) for e in c.log])
    def test_stiffarm_never_braced_goes_via_tucked(self):
        c, prep = self._go('braced', 'stiffarm'); self.assertEqual(prep, 150); self.assertEqual([e[2] for e in c.log if e[1] == 'pose'][0], 'tucked')
    def test_juke_from_braced_goes_via_tucked(self):
        c, prep = self._go('braced', 'juke'); self.assertEqual([e[2] for e in c.log if e[1] == 'pose'][0], 'tucked')
    def test_no_prep_when_already_allowed(self):
        for kind, pose in (('juke', 'exposed'), ('spin', 'braced'), ('stiffarm', 'tucked'), ('truck', 'braced')):
            c = M.Carrier(pose); self.assertEqual(c.start_maneuver(kind), 0); run(c, M.TELL_MS[kind] + 1); self.assertEqual(c.active, kind)
    def test_maneuver_pose_sets_exclude_forbidden(self):
        self.assertNotIn('braced', M.ALLOWED['stiffarm']); self.assertNotIn('loaded', M.ALLOWED['juke']); self.assertNotIn('extended', M.ALLOWED['spin'])
class TContact(unittest.TestCase):
    def test_contact_during_transition_keeps_last_completed_pose_and_clears_maneuver(self):
        c = M.Carrier('loaded'); c.start_maneuver('spin'); run(c, 200)          # extended reached at 150, midway to exposed
        self.assertEqual(c.pose, 'extended'); self.assertTrue(c.in_transition); c.on_contact(); run(c, 1000)
        self.assertEqual(c.pose, 'extended'); self.assertIsNone(c.active); self.assertEqual(starts(c), [])
    def test_contact_during_tell_cancels(self):
        c = M.Carrier('exposed'); c.start_maneuver('juke'); run(c, 100); self.assertEqual(c.tell(), 'juke'); c.on_contact(); run(c, 1000); self.assertEqual(starts(c), [])
    def test_contact_during_execution_interrupts(self):
        c = M.Carrier('braced'); c.start_maneuver('truck'); run(c, M.TELL_MS['truck'] + 50); self.assertEqual(c.active, 'truck'); c.on_contact()
        self.assertIsNone(c.active); self.assertIn('interrupted', [e[1] for e in c.log]); self.assertNotIn('done', [e[1] for e in c.log])
    def test_pose_cannot_change_during_tell_or_execution(self):
        c = M.Carrier('exposed'); c.start_maneuver('juke'); run(c, 50); self.assertFalse(c.request_pose('braced')); run(c, M.TELL_MS['juke']); self.assertFalse(c.request_pose('braced'))
class TThrow(unittest.TestCase):
    def test_pinned_arms_block_throw_and_throw_poses(self):
        c = M.Carrier('loaded'); c.pinned = True; self.assertFalse(c.can_throw()); c2 = M.Carrier('tucked'); c2.pinned = True; self.assertFalse(c2.request_pose('extended'))
    def test_throw_ready_times(self):
        c = M.Carrier('braced'); self.assertEqual(c.throw_ready_ms('full'), 600); self.assertEqual(c.throw_ready_ms('touch'), 450)
        self.assertEqual(M.Carrier('extended').throw_ready_ms('touch'), 0)
    def test_touch_pass_penalty_is_power_not_accuracy(self):
        self.assertEqual(M.POWER_TOUCH, .6); self.assertAlmostEqual(M.touch_sigma_mult(1.0), 1.0); self.assertGreater(M.touch_sigma_mult(0.3), M.touch_sigma_mult(0.9)); self.assertLess(M.touch_sigma_mult(0.9), 1.03)
class TInvariants(unittest.TestCase):
    def test_random_play_never_breaks_rules(self):
        r = random.Random(7)
        for trial in range(300):
            c = M.Carrier(r.choice(M.POSES)); prev = c.pose
            for _ in range(60):
                a = r.random()
                if a < .25: c.start_maneuver(r.choice(list(M.ALLOWED)))
                elif a < .45: c.request_pose(r.choice(M.POSES))
                elif a < .55: c.on_contact()
                elif a < .6: c.pinned = r.random() < .5
                c.step(r.randint(1, 120))
                if c.active: self.assertIn(c.pose, M.ALLOWED[c.active]); self.assertFalse(c.in_transition)
                prev = c.pose
    def test_reversing_goal_mid_step_stays_adjacent(self):
        c = M.Carrier('loaded'); c.request_pose('braced'); c.step(50); c.request_pose('loaded'); c.step(2000)
        self.assertEqual([e[2] for e in c.log if e[1] == 'pose'], ['extended', 'loaded']); self.assertEqual(c.pose, 'loaded')
    def test_every_pose_change_is_one_adjacent_step(self):
        r = random.Random(11)
        for trial in range(200):
            c = M.Carrier(r.choice(M.POSES)); cur = c.pose
            for _ in range(50):
                x = r.random()
                if x < .3: c.start_maneuver(r.choice(list(M.ALLOWED)))
                elif x < .5: c.request_pose(r.choice(M.POSES))
                elif x < .6: c.on_contact()
                c.step(r.randint(1, 150))
            for e in c.log:
                if e[1] == 'pose': self.assertEqual(M.steps_between(cur, e[2]), 1); cur = e[2]
    def test_determinism(self):
        def play():
            r = random.Random(3); c = M.Carrier('loaded')
            for _ in range(80):
                x = r.random()
                if x < .4: c.start_maneuver(r.choice(list(M.ALLOWED)))
                elif x < .5: c.on_contact()
                c.step(r.randint(1, 100))
            return c.log
        self.assertEqual(play(), play())
if __name__ == '__main__': unittest.main()
