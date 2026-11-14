"""Match-profile tests: the default profile is the up-to-date ruleset, it is verified from the built match, and it does not stall."""
import json, subprocess, sys, unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def run(profile, ms):
    out = subprocess.run([sys.executable, '-W', 'ignore', '-m', 'b1.match_run', '--seed', '1', '--max-ms', str(ms), '--profile', profile],
                         cwd=REPO, capture_output=True, text=True, timeout=600).stdout
    return json.loads([l for l in out.splitlines() if l.startswith('{')][-1])


class ProfileTests(unittest.TestCase):
    def test_default_is_experiment_v1_and_effective(self):
        from b1 import profile as P
        self.assertEqual(P.DEFAULT, 'experiment-v1')
        r = run('experiment-v1', 20000)
        self.assertEqual(r['profile']['pocket'], {'inner_points': 2, 'release_points': 2, 'outside_points': 2, 'carry_value': 2, 'marking_distance': 5.0})
        for k in ('RULES_V03', 'RV03_FLAT', 'RV03_MARK', 'RV03_NOKICK', 'CATCH_V2', 'HAND_FIGHT'):
            self.assertEqual(r['profile']['env'][k], '1', k)
        self.assertEqual(r['profile']['env']['PRISM_CATCHERS'], '0')   # no legacy second Keeper decider
        self.assertEqual(r['profile']['env']['RV03_SCRIM'], '0')       # known gap: B1 has no scrimmage-restart behaviour

    def test_legacy_profile_reproduces_sprint45_values(self):
        r = run('legacy-b0', 20000)
        self.assertEqual(r['profile']['pocket'], {'inner_points': 3, 'release_points': 2, 'outside_points': 1, 'carry_value': 4, 'marking_distance': 3.0})
        self.assertEqual(r['profile']['env'], {})

    def test_default_profile_does_not_stall_on_restarts(self):
        r = run('experiment-v1', 240000)
        led = r['rules']['ledger_by_event']
        self.assertGreater(led['restart_awarded'], 5)
        self.assertGreaterEqual(led.get('restart_release', 0) / led['restart_awarded'], 0.25, led)

    def test_one_profile_per_process(self):
        from b1 import profile as P
        P._APPLIED[0] = None
        P.apply('legacy-b0')
        with self.assertRaises(RuntimeError):
            P.apply('experiment-v1')
        P._APPLIED[0] = None

    def test_unknown_profile_rejected(self):
        from b1 import profile as P
        with self.assertRaises(ValueError):
            P.apply('nope')


if __name__ == '__main__':
    unittest.main()
