"""EMERGENCE-1 tests: parameters, positioning, boundary, determinism.
Run: python3 -m pytest -q b1/emergence/test_emergence.py
"""
import ast
import dataclasses
import inspect
import json
import math
from pathlib import Path
import unittest

from .. import cognition as C
from .params import BOUNDS, DEFAULT, NAMES, PolicyParams
from .positioning import choose_position

ROOT = Path(__file__).resolve().parents[2]
J = lambda v: json.dumps(v, sort_keys=True, default=lambda o: dataclasses.asdict(o))
T = lambda e, team, x, y, role='field', ms=1400: C.Track(e, team, role, x, y, 0., 0., ms)


def mk(tracks, pp='A', policy=DEFAULT, x=50., y=50.):
    sig = C.Signals('live', 1, 100000, 30000, 0, 0, None, None, False, passive_team=pp)
    v = C.AthleteView(observation_id='o', athlete='A0', team='A', role='field', slot=0, delivered_ms=1500, x=x, y=y,
                      holds_ball=False, attack_sign=1, own_goal_x=0., tracks=tuple(tracks), signals=sig, policy=policy)
    return v, C.BeliefState('b', 'o', tuple(tracks), (), 2000, None)


class Params(unittest.TestCase):
    def test_bounds_validation_and_size(self):
        self.assertTrue(10 <= len(NAMES) <= 16)
        for name, (lo, hi, default, doc) in BOUNDS.items():
            self.assertTrue(lo <= default <= hi and doc)
            self.assertEqual(getattr(DEFAULT, name), default)
            for bad in (lo - .01, hi + .01, float('nan'), 'x', True):
                with self.assertRaises(ValueError):
                    PolicyParams(**{name: bad})
        with self.assertRaises(ValueError):
            PolicyParams.from_dict({'formation': 1.})
        with self.assertRaises(dataclasses.FrozenInstanceError):
            DEFAULT.bias_pass = 1.
        self.assertEqual(PolicyParams.from_dict(DEFAULT.as_dict()), DEFAULT)

    def test_modules_are_pure(self):
        for f, allowed in (('params.py', {'dataclasses'}), ('positioning.py', {'math'})):
            mods = set()
            for n in ast.walk(ast.parse((ROOT / 'b1/emergence' / f).read_text())):
                if isinstance(n, ast.Import):
                    mods |= {a.name for a in n.names}
                elif isinstance(n, ast.ImportFrom):
                    mods.add(n.module)
            self.assertEqual(mods, allowed, f)


class Positioning(unittest.TestCase):
    def test_home_slot_grid_is_not_used_by_decisions(self):
        src = inspect.getsource(C.decide) + inspect.getsource(C._position)
        self.assertNotIn('home_position(', src)
        self.assertNotIn("'home'", src)
        self.assertNotIn('.slot', src)
        self.assertNotIn('slot', inspect.getsource(choose_position))

    def test_weights_drive_the_choice_view_change_changes_decision(self):
        ball = T(C.BALL, 'ball', 70, 50, 'ball')
        carrier = T('B3', 'B', 70.5, 50)
        zero = PolicyParams(**{n: 0. for n in NAMES if n.startswith('pos_')})
        toward = dataclasses.replace(zero, pos_ball_def=3.)
        away = dataclasses.replace(zero, pos_ball_def=-3.)
        far = [T('A1', 'A', 20, 20), T('A2', 'A', 20, 80)]     # two teammates already nearer are irrelevant to positioning
        pos = lambda pol, tr: next(o for o in C.decide(*mk(tr, 'B', pol))[1]['options'] if o[0] == 'position')[2]
        self.assertEqual(tuple(pos(zero, [ball, carrier] + far)), (50., 50.))            # all weights zero: stay
        self.assertGreater(pos(toward, [ball, carrier] + far)[0], 50.)            # pulled to the believed ball
        self.assertLess(pos(away, [ball, carrier] + far)[0], 50.)                 # pushed away
        ball2, carrier2 = T(C.BALL, 'ball', 30, 50, 'ball'), T('B3', 'B', 29.5, 50)
        self.assertLess(pos(toward, [ball2, carrier2] + far)[0], 50.)             # the view changed, the decision follows

    def test_positioning_uses_public_possession_signal_for_mode(self):
        ball, mate, opp = T(C.BALL, 'ball', 60, 50, 'ball'), T('A4', 'A', 60.4, 50), T('B2', 'B', 40, 40)
        only_goal = PolicyParams(**{**{n: 0. for n in NAMES if n.startswith('pos_')}, 'pos_goal_att': 3., 'pos_goal_def': 3.})
        rec = lambda pp: next(o for o in C.decide(*mk([ball, mate, opp], pp, only_goal))[1]['options'] if o[0] == 'position')
        self.assertEqual(rec('A')[1], 'att')
        self.assertGreater(rec('A')[2][0], 50.)        # in possession: toward the goal attacked (x = 100)

    def test_bias_and_risk_parameters_change_ball_decisions(self):
        tracks = [T('A1', 'A', 68, 50), T('B1', 'B', 59, 51.5)]
        def holding(pol, x=50.):
            v, b = mk(tracks, 'A', pol, x=x)
            return C.decide(dataclasses.replace(v, holds_ball=True), b)
        base_opts = {o[0] for o in holding(DEFAULT)[1]['options']}
        self.assertIn('pass', base_opts)
        self.assertNotIn('pass', {o[0] for o in holding(PolicyParams(pass_min_clearance=6.))[1]['options']})
        self.assertEqual(holding(PolicyParams(bias_pass=6., pass_min_clearance=0.))[0].kind, 'pass')
        self.assertNotIn('shoot', {o[0] for o in holding(PolicyParams(shot_range=8.), x=70.)[1]['options']})
        self.assertIn('shoot', {o[0] for o in holding(PolicyParams(shot_range=60.), x=70.)[1]['options']})
        self.assertEqual(holding(DEFAULT)[1]['policy'], DEFAULT.as_dict())           # parameters logged in every decision

    def test_choose_position_reads_only_its_arguments(self):
        a = choose_position(50., 50., 0., 1, 20., (60., 50.), None, 'def', ((40., 40.),), ((55., 55.),), DEFAULT)
        b = choose_position(50., 50., 0., 1, 20., (60., 50.), None, 'def', ((40., 40.),), ((55., 55.),), DEFAULT)
        self.assertEqual(a, b)
        self.assertEqual(set(inspect.signature(choose_position).parameters),
                         {'x', 'y', 'own_goal_x', 'attack_sign', 'zone_radius', 'ball_xy', 'carrier_xy', 'mode', 'mates', 'opps', 'p'})


class Engine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from ..matchport import run_match
        cls.run_match = staticmethod(run_match)
        cls.P2 = PolicyParams(bias_pass=2., pos_spread=2.5, pos_ball_att=-1., shot_range=45.)
        cls.views = []
        cls.r, cls.port = run_match(5, None, 20000, True, period_seconds=45, policies={'A': cls.P2, 'B': DEFAULT},
                                    on_view=lambda p, v, b: cls.views.append(v))

    def test_params_are_per_team_fixed_and_logged(self):
        self.assertEqual(self.r['policy_params'], {'A': self.P2.as_dict(), 'B': DEFAULT.as_dict()})
        self.assertEqual({v.policy for v in self.views if v.team == 'A'}, {self.P2})
        self.assertEqual({v.policy for v in self.views if v.team == 'B'}, {DEFAULT})
        self.assertNotIn('home', self.r['decisions_by_kind'])
        self.assertGreater(self.r['decisions_by_kind'].get('position', 0), 500)
        self.assertEqual(self.r['settings']['period_seconds'], 45)

    def test_determinism_same_seed_same_params(self):
        again = self.run_match(5, None, 20000, False, period_seconds=45, policies={'A': self.P2, 'B': DEFAULT})[0]
        self.assertEqual((again['trace_hash'], again['state_hash']), (self.r['trace_hash'], self.r['state_hash']))
        other = self.run_match(5, None, 20000, False, period_seconds=45, policies={'A': DEFAULT, 'B': DEFAULT})[0]
        self.assertNotEqual(other['trace_hash'], self.r['trace_hash'])          # params are part of the trace (no effect claim)

    def test_parallel_and_serial_and_order_give_identical_hashes(self):
        from .harness import job, run_jobs
        jobs = [job(s, 10, 'x', self.P2, 'y', DEFAULT) for s in (11, 12, 13, 14)]   # 10 s is the engine minimum period
        serial = run_jobs(jobs, serial=True)
        parallel = run_jobs(list(reversed(jobs)), workers=2)
        self.assertEqual([(r['id'], r['trace_hash'], r['score']) for r in serial],
                         [(r['id'], r['trace_hash'], r['score']) for r in parallel])
        self.assertTrue(all(r['status'] == 'final' and r['proxy'] for r in serial))

    def test_poison_hidden_state_and_other_team_params_do_not_reach_decisions(self):
        mkp = lambda: self.run_match(4, None, 12000, False, policies={'A': self.P2, 'B': DEFAULT})[1]
        a, b = mkp(), mkp()
        now = a.m.s.now
        a.capture(now)
        b.capture(now)
        s = b.m.s
        for p in s.players.values():                       # poison every live body, the ball and its carrier
            p.x, p.y, p.vx, p.vy = 100. - p.x, 100. - p.y, 15., -15.
        s.ball.x, s.ball.y, s.ball.carrier = 3., 97., ('B7' if s.ball.carrier != 'B7' else 'A3')
        n_pos = 0
        for pid in a.active_ids():
            va, ba = a.deliver(pid, now)
            vb, bb = b.deliver(pid, now)
            self.assertEqual(va, vb, pid)
            ia, ra = C.decide(va, ba)
            self.assertEqual(J((ia, ra)), J(C.decide(vb, bb)))
            n_pos += ia.kind == 'position'
        self.assertGreater(n_pos, 5)
        # the other team's parameters never reach an athlete: change B's vector, A's views are unchanged
        c = mkp()
        c.capture(now)
        c.policies = {'A': self.P2, 'B': PolicyParams(bias_press=5.)}
        d = mkp()
        d.capture(now)
        for pid in c.active_ids():
            vc, vd = c.deliver(pid, now)[0], d.deliver(pid, now)[0]
            if pid.startswith('A'):
                self.assertEqual(vc, vd)
            else:
                self.assertNotEqual(vc.policy, vd.policy)

    def test_view_json_roundtrip_keeps_policy(self):
        for s in json.loads(J(self.r['trace']['sampled_decisions']))[:10]:
            view, belief = C.view_from_json(s)
            self.assertEqual(view.policy.as_dict(), self.r['policy_params'][view.team])
            self.assertEqual(J(C.decide(view, belief)[1]), J(s['decision']))


if __name__ == '__main__':
    unittest.main()
