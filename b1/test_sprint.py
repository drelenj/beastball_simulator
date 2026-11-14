"""SPRINT-30 boundary, ownership, determinism and integration tests.

Run in its own process:  python -m unittest b1.test_sprint -v
IDs refer to audit/m1 (OWN-1..7, BR-1..7); see b1/sprint30/OWN_BR_CHECKLIST.md.
"""
import ast
import dataclasses
import json
import math
from pathlib import Path
import subprocess
import sys
import unittest

from . import cognition as C
from .preservation import verify_baseline, canonical_hashes, load_inventory

ROOT = Path(__file__).resolve().parents[1]
J = lambda v: json.dumps(v, sort_keys=True, default=lambda o: dataclasses.asdict(o))


def mk_view(tracks, holds=True, role='field', fb=(), pending=None, phase='live', pp='A', immune=(), **kw):
    sig = C.Signals(phase, 1, 100000, 30000, 0, 0, None, None, False, passive_team=pp, immune=tuple(immune))
    v = C.AthleteView(observation_id='o', athlete='A0', team='A', role=role, slot=0, delivered_ms=1500,
                      x=kw.get('x', 40.), y=kw.get('y', 50.), holds_ball=holds, attack_sign=1, own_goal_x=0.,
                      tracks=tuple(tracks), signals=sig, pending_command_id=pending,
                      pending_kind=kw.get('pending_kind', 'pass') if pending else None,
                      pending_target=kw.get('pending_target'), pending_release_ms=1700 if pending else None,
                      arrows_loaded=kw.get('arrows'), last_release_ms=None)
    return v, C.BeliefState('b', 'o', tuple(tracks), tuple(fb), 2000, None)


T = lambda e, team, x, y, role='field', ms=1400, vx=0., vy=0.: C.Track(e, team, role, x, y, vx, vy, ms)


class PureCognition(unittest.TestCase):
    def test_BR1_cognition_imports_no_simulator(self):
        tree = ast.parse((ROOT / 'b1/cognition.py').read_text())
        mods = set()
        for n in ast.walk(tree):
            if isinstance(n, ast.Import):
                mods |= {a.name for a in n.names}
            elif isinstance(n, ast.ImportFrom):
                mods.add(n.module)
        # cognition may import only the stdlib pure modules and Base A's pure b1.core
        self.assertEqual(mods, {'dataclasses', 'math', None})
        rel = [a.name for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.module is None for a in n.names]
        self.assertEqual(rel, ['communication', 'emergence_intents', 'core'])
        core = ast.parse((ROOT / 'b1/core.py').read_text())
        cm = set()
        for n in ast.walk(core):
            if isinstance(n, ast.Import):
                cm |= {a.name for a in n.names}
            elif isinstance(n, ast.ImportFrom):
                cm.add(n.module)
        self.assertEqual(cm, {'dataclasses', 'math'})

    def test_BR2_no_forbidden_symbols(self):
        src = (ROOT / 'b1/cognition.py').read_text()
        for sym in ('s.players', '.ball.', 'with_view', 'Policy', 'pol[', 'SimState', 'engine'):
            self.assertNotIn(sym, src)

    def test_BR5_motor_command_carries_no_belief_or_options(self):
        self.assertEqual([f.name for f in dataclasses.fields(C.MotorCommand)],
                         ['command_id', 'intent', 'start_ms', 'release_ms', 'resource', 'desired_velocity'])
        self.assertNotIn('options', [f.name for f in dataclasses.fields(C.ActionIntent)])

    def test_values_are_immutable(self):
        v, b = mk_view([T('A1', 'A', 55, 50)])
        with self.assertRaises(dataclasses.FrozenInstanceError):
            v.x = 1
        with self.assertRaises(dataclasses.FrozenInstanceError):
            b.tracks = ()

    def test_OWN3_view_change_changes_decision_in_predicted_direction(self):
        base = [T('A1', 'A', 58, 50)]
        i0, r0 = C.decide(*mk_view(base))
        self.assertEqual((i0.kind, i0.target), ('pass', 'A1'))
        v_open = next(o[3] for o in r0['options'] if o[0] == 'pass')
        i1, r1 = C.decide(*mk_view(base + [T('B0', 'B', 49, 50.5)]))   # defender on the lane
        v_block = next(o[3] for o in r1['options'] if o[0] == 'pass')
        self.assertLess(v_block, v_open)
        self.assertNotEqual(i1.kind, 'pass')
        i2, r2 = C.decide(*mk_view(base + [T('B0', 'B', 49, 62)]))     # defender farther off the lane
        self.assertGreater(next(o[3] for o in r2['options'] if o[0] == 'pass'), v_block)

    def test_stale_track_is_not_used(self):
        i, r = C.decide(*mk_view([T('A1', 'A', 58, 50), T('B0', 'B', 49, 50.5, ms=-2000)]))
        self.assertEqual(i.kind, 'pass')
        self.assertEqual(r['stale_track_ids'], ['B0'])

    def test_pending_and_failure_feedback_change_next_decision(self):
        tracks = [T('A1', 'A', 58, 50)]
        self.assertEqual(C.decide(*mk_view(tracks))[0].kind, 'pass')
        i, _ = C.decide(*mk_view(tracks, pending='cmd-9'))
        self.assertEqual((i.kind, i.related_command_id), ('continue_current', 'cmd-9'))
        i, r = C.decide(*mk_view(tracks, fb=[('x', 'interrupted:pass', 1450)]))
        self.assertNotEqual(i.kind, 'pass')
        self.assertEqual(r['considered_feedback'][1], 'interrupted:pass')

    def test_archer_ruleset_102_legality_from_belief(self):
        """D1 R-17 / R-01 / KP: any eligible opponent may be targeted; never a Keeper inside his own
        zone; nothing before the first passive possession; never a visibly immune player."""
        ball = T(C.BALL, 'ball', 60, 40, 'ball')
        kw = dict(holds=False, role='archer', arrows=5, x=25., y=-5.)
        i, _ = C.decide(*mk_view([ball, T('B3', 'B', 60.5, 40), T('B5', 'B', 50, 30)], **kw))
        self.assertEqual((i.kind, i.target), ('draw_release', 'B3'))            # carrier preferred
        i, r = C.decide(*mk_view([ball, T('B5', 'B', 50, 30)], **kw))            # 1.0.2: a non-carrier is legal
        self.assertEqual((i.kind, i.target), ('draw_release', 'B5'))
        self.assertEqual(C.decide(*mk_view([ball, T('B5', 'B', 50, 30)], pp=None, **kw))[0].kind, 'archer_hold')
        self.assertEqual(C.decide(*mk_view([ball, T('B5', 'B', 50, 30)], immune=('B5',), **kw))[0].kind, 'archer_hold')
        inside = T('B10', 'B', 85., 40., 'keeper')       # 18.0 m from (100, 50): inside R = 20
        outside = T('B10', 'B', 70., 30., 'keeper')      # 36 m from goal centre: outside
        self.assertEqual(C.decide(*mk_view([ball, inside], x=40., **{k: v for k, v in kw.items() if k != 'x'}))[0].kind, 'archer_hold')
        i, _ = C.decide(*mk_view([ball, outside], x=40., **{k: v for k, v in kw.items() if k != 'x'}))
        self.assertEqual((i.kind, i.target), ('draw_release', 'B10'))
        self.assertEqual(C.decide(*mk_view([ball, T('B5', 'B', 50, 30)], **dict(kw, arrows=0)))[0].kind, 'archer_hold')
        self.assertEqual(C.decide(*mk_view([ball, T('B5', 'B', 30, 0)], **kw))[0].kind, 'archer_hold')   # believed range < 12 m

    def test_archer_aborts_draw_when_own_belief_says_release_is_illegal(self):
        ball = T(C.BALL, 'ball', 60, 40, 'ball')
        kw = dict(holds=False, role='archer', arrows=5, x=25., y=-5., pending='cmd-7', pending_kind='draw_release', pending_target='B5')
        self.assertEqual(C.decide(*mk_view([ball, T('B5', 'B', 50, 30)], **kw))[0].kind, 'continue_current')
        i, _ = C.decide(*mk_view([ball, T('B5', 'B', 50, 30)], immune=('B5',), **kw))
        self.assertEqual((i.kind, i.related_command_id), ('abort_draw', 'cmd-7'))
        self.assertEqual(C.decide(*mk_view([ball, T('B5', 'B', 50, 30, ms=500)], **kw))[0].kind, 'abort_draw')   # stale track
        self.assertEqual(C.decide(*mk_view([ball], **kw))[0].kind, 'abort_draw')                               # target lost

    def test_KP_protected_keeper_is_not_pressed_view_change_changes_decision(self):
        """R-15/R-16 from the view only: Keeper with the ball inside own zone while his team has PP."""
        mk = lambda kx, pp: C.decide(*mk_view([T(C.BALL, 'ball', kx, 50, 'ball'), T('B10', 'B', kx + .5, 50, 'keeper')],
                                              holds=False, x=kx - 6., pp=pp))[1]['options']
        kinds = lambda opts: {o[0] for o in opts}
        self.assertNotIn('press', kinds(mk(90., 'B')))       # inside zone, his team has PP: protected
        self.assertIn('press', kinds(mk(90., 'A')))          # his team lacks PP: ordinary rules (R-16)
        self.assertIn('press', kinds(mk(70., 'B')))          # outside the zone: ordinary rules (R-16)

    def test_possession_is_seen_only_through_signals_and_perception(self):
        v, b = mk_view([T('A1', 'A', 58, 50)])
        v2 = dataclasses.replace(v, signals=dataclasses.replace(v.signals, pass_call=('A1', 'A0', 44., 52.)), holds_ball=False)
        i, _ = C.decide(v2, b)
        self.assertEqual((i.kind, i.aim), ('receive', (44., 52.)))

    def test_keeper_save_intent_from_perceived_flight_only(self):
        ball = T(C.BALL, 'ball', 20, 50, 'ball', vx=-25., vy=0.)
        v = mk_view([ball], holds=False, role='keeper', x=3., y=50.)
        self.assertEqual(C.decide(*v)[0].kind, 'keeper_save')
        away = T(C.BALL, 'ball', 20, 50, 'ball', vx=25., vy=0.)
        self.assertEqual(C.decide(*mk_view([away], holds=False, role='keeper', x=3., y=50.))[0].kind, 'keeper_set')

    def test_provenance_mismatch_fails_loudly(self):
        v, b = mk_view([])
        with self.assertRaises(ValueError):
            C.decide(v, dataclasses.replace(b, observation_id='other'))


class EngineIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from .matchport import run_match
        cls.run_match = staticmethod(run_match)
        cls.views = []
        cls.match, cls.port = run_match(1, None, 30000, True, sample=60,
                                        on_view=lambda p, v, b: cls.views.append((v, b)) if len(cls.views) < 4000 else None)

    def test_frozen_B0_file_identity(self):
        self.assertGreater(verify_baseline(ROOT, ROOT / 'b1/baseline/B0_2abe497_GIT_BLOBS.json'), 100)

    def test_frozen_B0_git_identity_and_no_modified_inventory_file(self):
        """Independent of the inventory's uncommitted entries: nothing from the
        frozen B0 commit differs, and no present inventory file is modified."""
        import hashlib
        r = subprocess.run(['git', 'diff', '--name-status', '2abe497', '--', '.', ':!b1'],
                           cwd=ROOT, text=True, capture_output=True, timeout=60)
        self.assertEqual(r.returncode, 0, r.stderr)
        changed = [l for l in r.stdout.splitlines() if l and not l.startswith('A\t')]
        self.assertEqual(changed, [])
        inventory = ROOT / 'b1/baseline/B0_2abe497_GIT_BLOBS.json'
        _, exp, _ = load_inventory(inventory)
        self.assertGreater(len(exp), 200)
        self.assertEqual(canonical_hashes(ROOT, inventory), exp)

    def test_G1_three_athletes_decide_and_physics_resolves_the_pass(self):
        r, port = self.run_match(1, 'g1', 9000)
        self.assertEqual(set(r['decisions_by_athlete']), {'A0', 'A1', 'B0'})
        self.assertIn(r['terminal'].split(':')[0], ('pass_completed', 'pass_completed_other', 'pass_intercepted',
                                                    'pass_dead', 'carrier_dispossessed', 'carrier_reaches_x_90', 'dead_ball'))
        if r['terminal'] == 'pass_completed':      # the catch is an engine control event, not asserted by cognition
            self.assertEqual(port.m.s.ball.carrier, 'A1')
            self.assertGreaterEqual(r['engine_events'].get('control', 0), 1)

    def test_G1_terminals_vary_with_seed_and_are_physical(self):
        terms = {s: self.run_match(s, 'g1', 9000, False)[0]['terminal'] for s in range(1, 9)}
        self.assertTrue(all(terms.values()), terms)
        type(self).g1_terminals = terms

    def test_determinism_same_seed_same_hash_in_process(self):
        a = self.run_match(3, 'g1', 9000, False)[0]
        b = self.run_match(3, 'g1', 9000, False)[0]
        self.assertEqual((a['trace_hash'], a['state_hash']), (b['trace_hash'], b['state_hash']))
        m = self.run_match(1, None, 30000, False)[0]
        self.assertEqual((m['trace_hash'], m['state_hash']), (self.match['trace_hash'], self.match['state_hash']))

    def test_determinism_across_processes(self):
        outs = []
        for _ in range(2):
            r = subprocess.run([sys.executable, '-m', 'b1.match_run', '--seed', '2', '--max-ms', '20000', '--telemetry-off'],
                               cwd=ROOT, text=True, capture_output=True, timeout=300)
            self.assertEqual(r.returncode, 0, r.stderr[-2000:])
            d = json.loads(r.stdout.strip().splitlines()[-1])
            outs.append((d['trace_hash'], d['state_hash'], d['decisions_total']))
        self.assertEqual(outs[0], outs[1])
        self.assertGreater(outs[0][2], 500)

    def _twin_ports(self, t=12000):
        a = self.run_match(4, None, t, False)[1]
        b = self.run_match(4, None, t, False)[1]
        self.assertEqual(a.m.s.now, b.m.s.now)
        return a, b

    def test_OWN1_OWN2_hidden_true_state_perturbation_leaves_decisions_identical(self):
        a, b = self._twin_ports()
        now = a.m.s.now
        # (1) hidden attributes poisoned in real engine state BEFORE the sensor capture
        for p in b.m.s.players.values():
            p.a.strength, p.a.tackling, p.a.passing, p.fatigue = .01, .99, .01, .2
            p.minor_count, p.immune_until = 3, now + 5000
        a.capture(now)
        b.capture(now)
        # (2) AFTER capture, with the delivered view fixed, poison every piece of live true
        # state: all bodies (including the deciding athlete and the carrier), the ball and
        # its carrier, phase, clocks, score, restart, quivers.
        s = b.m.s
        for p in s.players.values():
            p.x, p.y, p.vx, p.vy, p.posture = 100. - p.x, 100. - p.y, 20., -20., 'grounded'
        s.ball.x, s.ball.y, s.ball.vx, s.ball.vy = 3., 97., 30., -30.
        s.ball.carrier = 'B7' if s.ball.carrier != 'B7' else 'A3'
        s.phase = b.types.Phase.DEAD if s.phase != b.types.Phase.DEAD else b.types.Phase.LIVE
        s.possession_ms, s.game_ms, s.score = 1, 1, {'A': 99, 'B': 98}
        s.restart = b.types.Restart('B', 5., 5., 'poison', taker='B3')
        s.ends = {'A': 100, 'B': 0}
        for p in s.players.values():
            p.role, p.slot = ('keeper' if p.role == 'field' else 'field'), 7
        for q in s.quivers.values():
            q.loaded, q.last_release = 0, now
        n = 0
        for pid in a.active_ids():
            va, ba = a.deliver(pid, now)
            vb, bel_b = b.deliver(pid, now)
            self.assertEqual(va, vb, pid)
            self.assertEqual(ba, bel_b, pid)
            self.assertEqual(J(C.decide(va, ba)), J(C.decide(vb, bel_b)))
            n += 1
        self.assertEqual(n, len(a.active_ids()))
        self.assertGreaterEqual(n, 20)

    def test_public_signal_change_reaches_view_only_after_latency(self):
        a, b = self._twin_ports()
        now = a.m.s.now
        b.m.s.possession_ms = 1234
        diff = 0
        for k in range(0, 10):
            a.capture(now + 100 * k)
            b.capture(now + 100 * k)
        for pid in a.active_ids():
            diff += a.deliver(pid, now + 900)[0].signals != b.deliver(pid, now + 900)[0].signals
        self.assertEqual(diff, len(a.active_ids()))

    def test_sensor_is_sensitive_observed_world_change_changes_view(self):
        """Counterpart that proves the perturbation test can fail."""
        a, b = self._twin_ports()
        now = a.m.s.now
        for p in b.m.s.players.values():
            if p.active and p.role == 'field':
                p.x, p.y = 100. - p.x, 100. - p.y
        changed = 0
        for k in range(0, 12):
            a.capture(now + 100 * k)
            b.capture(now + 100 * k)
        for pid in a.active_ids():
            va, ba = a.deliver(pid, now + 1100)
            vb, bel_b = b.deliver(pid, now + 1100)
            changed += va.tracks != vb.tracks
        self.assertGreater(changed, 10)

    def test_OWN4_BR6_decisions_reconstruct_from_trace_alone(self):
        samples = json.loads(J(self.match['trace']['sampled_decisions']))
        self.assertGreaterEqual(len(samples), 50)
        for s in samples[:60]:
            view, belief = C.view_from_json(s)
            intent, rec = C.decide(view, belief)
            self.assertEqual(J(rec), J(s['decision']))
            self.assertEqual(J(intent), J(s['intent']))
            self.assertEqual(rec['observation_id'], view.observation_id)
            self.assertTrue(rec['belief_revision'].startswith(rec['observation_id']))
            best = max(rec['options'], key=lambda o: (o[3], o[0], o[1] or ''))
            self.assertEqual(J(best), J(rec['selected']))

    def test_BR4_cognition_runs_in_process_without_simulator(self):
        samples = json.loads(J(self.match['trace']['sampled_decisions']))[:40]
        code = ("import sys,json\nfrom b1 import cognition as C\nimport dataclasses\n"
                "out=[]\nfor s in json.load(sys.stdin):\n v,b=C.view_from_json(s)\n i,r=C.decide(v,b)\n"
                " out.append([r,dataclasses.asdict(i)])\n"
                "bad=[m for m in sys.modules if m.split('.')[0] in ('pocket4_proto','core_src','prism_archer_v0','scipy','numpy') or m in ('b1.matchport','b1.runtime')]\n"
                "print(json.dumps({'out':out,'bad':bad},sort_keys=True))")
        r = subprocess.run([sys.executable, '-c', code], cwd=ROOT, text=True, input=json.dumps(samples),
                           capture_output=True, timeout=60)
        self.assertEqual(r.returncode, 0, r.stderr[-2000:])
        d = json.loads(r.stdout)
        self.assertEqual(d['bad'], [])
        self.assertEqual(J(d['out']), J([[s['decision'], s['intent']] for s in samples]))

    def test_OWN5_motor_never_changes_kind_target_or_receiver(self):
        seen = 0
        runs = [(self.match, self.port)] + [self.run_match(sd, 'g1', 9000) for sd in (1, 2, 3)]
        for r, port in runs:
            chains = r['trace']['action_chains']
            want = {(c['decision_id'].split('/')[2], c['target']) for c in chains if c['kind'] in ('pass', 'restart_pass')}
            shooters = {c['decision_id'].split('/')[2] for c in chains if c['kind'] == 'shoot'}
            archers = {(c['decision_id'].split('/')[2], c['target']) for c in chains if c['kind'] == 'draw_release'}
            plans = 0
            for rec in port.m.e.log:
                d = rec['data']
                if rec['event'] == 'release' and d.get('kind') == 'pass' and not d.get('forced'):
                    self.assertIn((d['player'], d['target']), want)
                    plans += 1
                if rec['event'] == 'release' and d.get('kind') == 'shot':
                    self.assertIn(d['player'], shooters)
                if rec['event'] == 'arrow_draw':
                    self.assertIn((d['player'], d['target']), archers)
            # every engine pass release was checked per command at release time (raises on mismatch)
            self.assertEqual(r['own5_pass_releases_checked'], plans)
            for rr in r['trace']['release_records']:        # pass-release-v1: bound respected
                if rr['status'] == 'released':
                    self.assertLessEqual(rr['correction_angle_deg'], rr['correction_bound_deg'])
                    self.assertEqual(rr['target'], next(c['target'] for c in chains if c['command_id'] == rr['command_id']))
            seen += plans
        self.assertGreaterEqual(seen, 3)

    def test_OWN6_no_decision_before_delivery_and_no_future_data(self):
        self.assertGreater(len(self.views), 1000)
        for v, b in self.views:
            for t in b.tracks:
                self.assertLessEqual(t.captured_ms, v.delivered_ms)
        ids = [v.observation_id for v, _ in self.views]
        self.assertEqual(len(ids), len(set(ids)))

    def test_OWN7_unobserved_body_goes_stale_and_does_not_jump_to_truth(self):
        port = self.run_match(1, 'g1', 1400, False)[1]
        s = port.m.s
        now = s.now
        d = s.players['B0']
        for k in range(0, 6):
            port.capture(now + 100 * k)
        t0 = now + 500
        before = next((t for t in port.deliver('A0', t0)[1].tracks if t.entity == 'B0'), None)
        self.assertIsNotNone(before)             # non-vacuous: A0 was tracking B0
        d.x, d.y = 12., 50.                      # teleported far behind A0 (faces +x at x~40)
        for k in range(1, 9):
            port.capture(t0 + 100 * k)
        view, belief = port.deliver('A0', t0 + 800)
        tr = next((t for t in belief.tracks if t.entity == 'B0'), None)
        self.assertIsNotNone(tr)                 # remembered, not deleted
        self.assertGreater(math.hypot(tr.x - d.x, tr.y - d.y), 5.)       # did not jump to the truth
        self.assertLessEqual(tr.captured_ms, t0)                         # no observation after it left view
        self.assertLess(math.hypot(tr.x - before.x, tr.y - before.y), 8.)

    def test_BR7_legacy_tactical_controller_is_trapped_and_run_completes(self):
        m = self.port.m
        cls, pcls = type(m), type(m.pol['A'])
        for name in ('carrier_decision', 'arrow_decisions', 'c4c2_decide', 'c4c2_targets', 'route_receiver'):
            with self.assertRaisesRegex(RuntimeError, 'legacy tactical controller reached'):
                getattr(cls, name)(m)
        for name in ('targets', 'pass_choice', 'pass_ranked'):
            with self.assertRaisesRegex(RuntimeError, 'legacy tactical controller reached'):
                getattr(pcls, name)(m.pol['A'], m.s)
        with self.assertRaisesRegex(RuntimeError, 'legacy tactical controller reached'):
            m.c4c2_decide(None, 0, False)
        self.assertEqual(m.pol['A'].pass_ranked(m.s, None), [])
        self.assertGreater(self.match['hook_calls']['ball_motor'], 0)
        self.assertGreater(self.match['ownership_decisions_by_kind']['restart_claim'], 0)
        self.assertGreater(self.match['decisions_total'], 2000)
        self.assertEqual(set(self.match['decisions_by_role']), {'archer', 'field', 'keeper'})

    def test_causal_ids_link_decision_command_outcome(self):
        tr = self.match['trace']
        cmds = {c['command_id']: c for c in tr['action_chains']}
        linked = [o for o in tr['outcomes'] if o['command_id'] in cmds]
        self.assertGreater(len(linked), 0)
        for c in cmds.values():
            self.assertTrue(c['command_id'].startswith(c['intent_id']))
            self.assertTrue(c['intent_id'].startswith(c['decision_id']))
            self.assertTrue(c['decision_id'].startswith(c['observation_id']))

    def test_primitives_are_registered_and_listed(self):
        from .registry import PRIMITIVES
        self.assertGreaterEqual(len(PRIMITIVES), 15)
        lim = ROOT / 'SPRINT45_LIMITATIONS.md'
        text = lim.read_text()               # must exist: no vacuous pass
        for key in PRIMITIVES:
            self.assertIn(key, text)


if __name__ == '__main__':
    unittest.main()
