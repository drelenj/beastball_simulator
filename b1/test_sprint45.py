"""SPRINT-45 Round 2 engine-level tests: rules-state layer on the real engine, rules
signals through the delayed view, belief-driven Archer legality, release contract.
Run:  python -m pytest -q b1/test_sprint45.py
"""
import dataclasses
import inspect
import json
import unittest

from . import cognition as C
from .possession import PossessionTracker, RulesConfig

J = lambda v: json.dumps(v, sort_keys=True, default=lambda o: dataclasses.asdict(o))


class Round2Engine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from .matchport import run_match, MatchPort
        cls.run_match, cls.MatchPort = staticmethod(run_match), MatchPort
        cls.runs = {p1: run_match(1, None, 45000, True, p1_ms=p1) for p1 in (250, 500, 1000)}

    def test_ruleset_102_is_set_for_the_B1_instance_only(self):
        port = self.runs[500][1]
        self.assertEqual(port.m.cfg['ruleset'], '1.0.2')
        self.assertEqual(self.runs[500][0]['ruleset'], '1.0.2')
        import pocket4_proto
        self.assertEqual(pocket4_proto.RULESET, '1.0.1')          # B0 default untouched

    def test_P1_threshold_in_engine_run_250_500_1000(self):
        """Every direct possession in the ledger follows its 'secured' entry by at least the
        configured threshold and by less than threshold + one engine step (100 ms)."""
        for p1, (r, port) in self.runs.items():
            ledger = port.rules.ledger
            gaps, last_secured = [], None
            for e in ledger:
                if e.get('event') == 'secured':
                    last_secured = e['t_ms']
                elif e.get('event') == 'direct_possession' and last_secured is not None:
                    gaps.append(e['t_ms'] - last_secured)
                    last_secured = None
            self.assertGreater(len(gaps), 3, p1)
            self.assertGreaterEqual(min(gaps), p1, (p1, gaps))
            self.assertLessEqual(min(gaps), p1 + 100, (p1, gaps))

    def test_passive_possession_only_changes_after_direct_possession_or_restart_award(self):
        for p1, (r, port) in self.runs.items():
            prev = None
            for e in port.rules.ledger:
                if e.get('event') == 'passive_possession':
                    self.assertIn(prev.get('event'), ('direct_possession', 'restart_awarded'), (p1, prev, e))
                prev = e

    def test_rules_layer_reads_engine_events_not_beliefs(self):
        from . import matchport
        src = inspect.getsource(matchport.MatchPort._feed_rules)
        for sym in ('sensor', 'bget', 'belief', 'tracks', 'snaps', 'gaze', 'last_ball'):
            self.assertNotIn(sym, src)
        psrc = inspect.getsource(PossessionTracker)
        for sym in ('belief', 'AthleteView', 'tracks'):
            self.assertNotIn(sym, psrc)

    def test_possession_signal_reaches_view_only_through_delayed_snapshot(self):
        a = self.run_match(4, None, 12000, False)[1]
        b = self.run_match(4, None, 12000, False)[1]
        now = a.m.s.now
        a.capture(now)
        b.capture(now)
        # poison the authoritative rules state AFTER capture: the delivered view must not move
        b.rules = PossessionTracker(RulesConfig())
        b.calls = {'A': ('A1', 'A2', 1., 1., now + 9999), 'B': ('B1', 'B2', 1., 1., now + 9999)}
        for pid in a.active_ids():
            va, ba = a.deliver(pid, now)
            vb, bb = b.deliver(pid, now)
            self.assertEqual(va, vb, pid)
            self.assertEqual(J(C.decide(va, ba)), J(C.decide(vb, bb)))
        # ...and the changed rules state does reach the view once it has been captured and the latency has passed
        for k in range(1, 10):
            a.capture(now + 100 * k)
            b.capture(now + 100 * k)
        diff = sum(a.deliver(pid, now + 900)[0].signals != b.deliver(pid, now + 900)[0].signals for pid in a.active_ids())
        self.assertEqual(diff, len(a.active_ids()))

    def test_archer_motor_has_no_true_state_interlock_wrong_belief_becomes_engine_foul(self):
        """Failing case for the Round 1 gap: a release at a truly immune target is NOT shielded
        by the motor; the engine adjudicates it."""
        from . import matchport
        self.assertNotIn('immune_until', inspect.getsource(matchport.MatchPort._archer_motor))
        port = self.run_match(4, None, 12000, False)[1]
        m = port.m
        s = m.s
        archer = next(p for p in s.players.values() if p.active and p.role == 'archer' and p.team == 'A')
        target = min((p for p in s.players.values() if p.active and p.role == 'field' and p.team == 'B'),
                     key=lambda p: abs(((p.x - archer.x) ** 2 + (p.y - archer.y) ** 2) ** .5 - 35))
        target.immune_until = s.now + 60000                      # hidden true state
        s.quivers['A'].loaded, s.quivers['A'].reload_until, s.quivers['A'].last_release = 5, -1, -99999
        intent = C.ActionIntent('t/intent', 't', archer.id, 'draw_release', target.id,
                                (target.x, target.y), (0., 0.), None, s.now)
        port.pending.pop(archer.id, None)
        self.assertEqual(port.submit(intent)['status'], 'accepted')
        port.pending[archer.id].update(started=True, due=s.now)
        n0, o0 = len(m.e.log), len(port.outcomes)
        port._archer_motor()
        self.assertEqual([o.status for o in port.outcomes[o0:]], ['rejected_by_engine'])
        self.assertTrue(any(r['event'] in ('foul', 'illegal') or 'archery_target' in str(r['data']) for r in m.e.log[n0:]))
        self.assertTrue(port.feedback[archer.id][-1][1].startswith('rejected_by_engine'))

    def test_release_contract_is_base_A_code_and_geometry_rejection_feeds_back(self):
        from . import matchport, runtime
        src = inspect.getsource(matchport.MatchPort._ball_motor)
        self.assertIn('PhysicalExecutionPort._release_due', src)
        self.assertNotIn('make_pass(p, q, \'pass\', True)', src)
        self.assertNotIn('plan_pass', src)
        self.assertEqual(runtime.MAX_MOVING_RELEASE_CORRECTION_DEG, 60.0)
        rc = self.runs[500][0]['release_contract']
        self.assertGreater(rc['releases_recorded'], 0)
        tracks = (C.Track('A1', 'A', 'field', 58, 50, 0, 0, 1400),)
        sig = C.Signals('live', 1, 1, 30000, 0, 0, None, None, False, passive_team='A')
        v = C.AthleteView('o', 'A0', 'A', 'field', 0, 1500, 40., 50., True, 1, 0., tracks, sig)
        self.assertEqual(C.decide(v, C.BeliefState('b', 'o', tracks))[0].kind, 'pass')
        fb = (('x', 'rejected_geometry:pass', 1450),)
        self.assertNotEqual(C.decide(v, C.BeliefState('b', 'o', tracks, fb))[0].kind, 'pass')

    def test_zone_violation_is_fed_to_B0_restart_and_not_when_disabled(self):
        fake = lambda *a, **k: [{'t_ms': 0, 'row': 'R-13', 'event': 'violation', 'violation': 'ZR-1', 'team': 'A', 'restart': 'RST-1'}]
        for enforce in (False, True):
            port = self.run_match(4, None, 12000, False)[1]
            s = port.m.s
            self.assertEqual(s.phase, port.types.Phase.LIVE)
            port.enforce = enforce
            port.rules.step = fake
            n0 = len(port.m.e.log)
            port._feed_rules([])
            awards = [r for r in port.m.e.log[n0:] if r['event'] == 'restart_awarded']
            if enforce:
                self.assertEqual([(r['data']['team'], r['data']['reason']) for r in awards], [('B', 'b1_ZR-1')])
                self.assertEqual(port.enforced, 1)
            else:
                self.assertEqual(awards, [])

    def test_determinism_with_rules_layer(self):
        a = self.run_match(1, None, 45000, False)[0]
        r = self.runs[500][0]
        self.assertEqual((a['trace_hash'], a['state_hash'], a['rules']), (r['trace_hash'], r['state_hash'], r['rules']))


if __name__ == '__main__':
    unittest.main()
