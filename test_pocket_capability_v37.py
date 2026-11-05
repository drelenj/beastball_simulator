"""Tests for the Pocket capability table/lookup (no simulator needed).  Run: python -m unittest -q test_pocket_capability_v37"""
import json, unittest
from pathlib import Path
import pocket_capability_v37 as p
ROWS = json.load(open(Path(__file__).resolve().parent / 'results_v37' / 'capability_table_v37.json'))


class Table(unittest.TestCase):
    def test_grid_points_reproduce_the_simulator(self):
        for r in ROWS:
            if r['region'] or r['role'] != 'field': continue
            c = p.capability(r['rating'], r['reserve'])
            self.assertAlmostEqual(c['top_mph'], r['top_mph'], places=2); self.assertAlmostEqual(c['t10_s'], r['t10'], places=2)

    def test_anchor_values(self):
        c = p.capability(1.0); self.assertEqual((c['top_mph'], c['stop25_m']), (100.0, 8.3))
        self.assertAlmostEqual(p.capability(.6)['top_mph'], 80., delta=.01)

    def test_monotone_in_rating_and_reserve(self):
        for res in (1., .5, 0.):
            s = [p.capability(r / 100, res)['top_mph'] for r in range(60, 101, 5)]; self.assertEqual(s, sorted(s))
            t = [p.capability(r / 100, res)['t10_s'] for r in range(60, 101, 5)]; self.assertEqual(t, sorted(t, reverse=True))
        for r in (.6, .75, 1.):
            s = [p.capability(r, x / 10)['top_mph'] for x in range(0, 11)]; self.assertEqual(s, sorted(s))

    def test_injury_slower_than_rested_and_worse_with_severity(self):
        for reg in ('hamstring', 'groin', 'knee', 'ankle', 'general'):
            a, b, c = (p.capability(.8, 1., reg, s)['top_mph'] for s in (0., .5, 1.)); self.assertTrue(a > b > c, msg=reg)

    def test_fatigue_and_injury_compound(self):
        self.assertLess(p.capability(.8, .5, 'knee', .5)['top_mph'], min(p.capability(.8, .5)['top_mph'], p.capability(.8, 1., 'knee', .5)['top_mph']))

    def test_flags_and_failures(self):
        self.assertIn('rating clamped to 0.6', p.capability(.5)['notes'])
        self.assertIsNone(p.capability(.8, 1., 'ankle', 1.)['stop25_m'])        # the simulator cannot stop this athlete from 25 m/s

    def test_keeper_close_to_field(self):
        for r in (.6, .8, 1.): self.assertAlmostEqual(p.capability(r, 1., role='keeper')['top_mph'], p.capability(r)['top_mph'], delta=2.)


if __name__ == '__main__':
    unittest.main()
