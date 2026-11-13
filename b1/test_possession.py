"""Tests for b1/possession.py against audit/HP-002_OWNER_DECISIONS_D1_RECORD.md section 3.

Run: python -m pytest -q b1/test_possession.py
Each test name carries the row / decision id it checks.
"""
import ast
from pathlib import Path
import unittest

from .possession import PossessionTracker, PublicRulesState, RulesConfig, UnresolvedOutcome

MID = (50., 50.)
A_ZONE = (5., 50.)         # inside A's own zone (goal x = 0)
B_ZONE = (95., 50.)


def rows(entries, row=None, **match):
    return [e for e in entries if (row is None or e['row'] == row)
            and all(e.get(k) == v for k, v in match.items())]


def hold(t, team, player, start, end, xy=MID, step=50):
    """Player keeps uncontested control from start to end inclusive."""
    out = []
    for ms in range(start, end + 1, step):
        out += t.step(ms, {player: team}, xy)
    return out


def possessed(team='A', player='A1', xy=MID, cfg=RulesConfig()):
    t = PossessionTracker(cfg)
    hold(t, team, player, 0, cfg.direct_possession_threshold_ms, xy)
    assert t.public().passive_team == team
    return t


class PossessionRows(unittest.TestCase):
    def test_R01_opening_no_possession_no_phase_empty_archer_target_set(self):
        t = PossessionTracker()
        t.step(0, {}, MID)
        p = t.public()
        self.assertIsInstance(p, PublicRulesState)
        self.assertEqual((p.passive_team, p.direct_team, p.team_control), (None, None, None))
        self.assertEqual((p.phase('A'), p.phase('B')), ('none', 'none'))
        self.assertFalse(t.freeze_legal('B', 'field', MID))

    def test_R02_secured_timer_runs_possession_unchanged_before_threshold(self):
        t = PossessionTracker()
        e = hold(t, 'A', 'A1', 0, 450)
        p = t.public()
        self.assertEqual(len(rows(e, 'R-02')), 1)
        self.assertEqual((p.uncontested_ms, p.direct_team, p.passive_team), (450, None, None))

    def test_R03_threshold_gives_direct_and_passive_possession(self):
        t = PossessionTracker()
        e = hold(t, 'A', 'A1', 0, 500)
        p = t.public()
        self.assertEqual((p.direct_team, p.direct_holder, p.passive_team, p.team_control, p.ball_status),
                         ('A', 'A1', 'A', 'A', 'carried'))
        self.assertEqual(rows(e, 'R-03', event='direct_possession')[0]['t_ms'], 500)
        self.assertEqual((p.phase('A'), p.phase('B')), ('offense', 'defense'))

    def test_P1_threshold_250_500_1000_flip_exactly_at_threshold_not_before(self):
        for thr in (250, 500, 1000):
            cfg = RulesConfig(direct_possession_threshold_ms=thr)
            t = PossessionTracker(cfg)
            hold(t, 'A', 'A1', 0, thr - 10, step=10)
            self.assertIsNone(t.public().direct_team, thr)
            self.assertIsNone(t.public().passive_team, thr)
            t.step(thr, {'A1': 'A'}, MID)
            self.assertEqual((t.public().direct_team, t.public().passive_team), ('A', 'A'), thr)
        # the three settings disagree at 600 ms of control: the parameter is live
        got = []
        for thr in (250, 500, 1000):
            t = PossessionTracker(RulesConfig(direct_possession_threshold_ms=thr))
            hold(t, 'B', 'B2', 0, 600)
            got.append(t.public().passive_team)
        self.assertEqual(got, ['B', 'B', None])

    def test_R04_C1_contest_lapses_direct_not_passive(self):
        t = possessed()
        e = t.step(550, {'A1': 'A', 'B1': 'B'}, MID)
        p = t.public()
        self.assertEqual(len(rows(e, 'R-04')), 1)
        self.assertEqual((p.contested, p.direct_team, p.uncontested_ms, p.passive_team), (True, None, 0, 'A'))
        t.step(2000, {'A1': 'A', 'B1': 'B'}, MID)       # however long the contest lasts
        self.assertEqual((t.public().passive_team, t.public().uncontested_ms), ('A', 0))

    def test_R05_contest_ends_timer_restarts_at_zero(self):
        t = possessed()
        t.step(550, {'A1': 'A', 'B1': 'B'}, MID)
        e = t.step(600, {'B1': 'B'}, MID)
        self.assertEqual(len(rows(e, 'R-05')), 1)
        self.assertEqual((t.public().contested, t.public().uncontested_ms, t.public().passive_team), (False, 0, 'A'))
        hold(t, 'B', 'B1', 650, 1050)                   # 450 ms after the contest ended
        self.assertEqual(t.public().passive_team, 'A')
        t.step(1100, {'B1': 'B'}, MID)                  # 500 ms after the contest ended
        self.assertEqual(t.public().passive_team, 'B')

    def test_C2_body_contact_alone_does_not_contest(self):
        t = possessed()
        # a tackle on the carrier: the tackler is not in `touching` (not touching the ball)
        e = t.step(550, {'A1': 'A'}, MID)
        p = t.public()
        self.assertEqual(rows(e, 'R-04'), [])
        self.assertEqual((p.contested, p.direct_team, p.uncontested_ms), (False, 'A', 550))

    def test_R06_pass_release_keeps_team_control_and_passive(self):
        t = possessed()
        e = t.step(550, {}, MID, [{'kind': 'pass_release', 'player': 'A1', 'team': 'A'}])
        p = t.public()
        self.assertEqual(len(rows(e, 'R-06')), 1)
        self.assertEqual((p.team_control, p.direct_team, p.passive_team, p.ball_status),
                         ('A', None, 'A', 'pass_in_flight'))

    def test_R07_shot_release_ends_team_control_passive_unchanged(self):
        t = possessed()
        t.step(550, {}, MID, [{'kind': 'shot_release', 'player': 'A1', 'team': 'A'}])
        p = t.public()
        self.assertEqual((p.team_control, p.direct_team, p.passive_team, p.ball_status),
                         (None, None, 'A', 'shot_in_flight'))

    def test_R08_defender_touch_ends_control_resets_zone_clock_passive_unchanged(self):
        t = possessed(xy=A_ZONE)
        hold(t, 'A', 'A1', 550, 2000, A_ZONE)
        self.assertEqual(dict(t.public().zone_clock_ms)['A'], 1500)
        t.step(2050, {}, A_ZONE, [{'kind': 'pass_release', 'player': 'A1', 'team': 'A'}])
        e = t.step(2100, {}, A_ZONE, [{'kind': 'touch', 'player': 'B3', 'team': 'B'}])
        p = t.public()
        self.assertEqual(len(rows(e, 'R-08')), 1)
        self.assertEqual((p.team_control, p.passive_team, p.last_toucher), (None, 'A', 'B3'))
        self.assertEqual(dict(p.zone_clock_ms)['A'], 0)
        self.assertEqual(rows(e, 'R-14')[0]['trigger'], 'defender_touch')

    def test_R09_loose_ball_keeps_passive_possession(self):
        t = possessed()
        e = t.step(550, {}, MID, [{'kind': 'loose'}])
        p = t.public()
        self.assertEqual(len(rows(e, 'R-09')), 1)
        self.assertEqual((p.team_control, p.direct_team, p.passive_team, p.ball_status),
                         (None, None, 'A', 'loose_ground'))

    def test_R10_opponent_uncontested_control_flips_passive_and_resets_clocks(self):
        t = possessed(xy=A_ZONE)
        t.step(600, {}, A_ZONE, [{'kind': 'loose'}])
        e = hold(t, 'B', 'B1', 650, 1100, A_ZONE)
        self.assertEqual(t.public().passive_team, 'A')
        self.assertTrue(dict(t.public().zone_clock_running)['A'])
        e = t.step(1150, {'B1': 'B'}, A_ZONE)
        p = t.public()
        self.assertEqual(len(rows(e, 'R-10')), 1)
        self.assertEqual((p.passive_team, p.direct_team), ('B', 'B'))
        self.assertEqual(dict(p.zone_clock_ms), {'A': 0, 'B': 0})
        self.assertEqual(dict(p.zone_clock_running), {'A': False, 'B': False})
        self.assertEqual(rows(e, 'R-14')[0]['trigger'], 'passive_possession_change')

    def test_R11_ZRC_carrier_crosses_from_outside_into_own_zone(self):
        t = possessed(xy=(30., 50.))                     # A possesses outside own zone
        e = t.step(600, {'A1': 'A'}, (25., 50.), holder_xy=(25., 50.))
        self.assertEqual(rows(e, 'R-11'), [])
        e = t.step(650, {'A1': 'A'}, (19., 50.), holder_xy=(19., 50.))
        v = rows(e, 'R-11')
        self.assertEqual((v[0]['violation'], v[0]['restart'], v[0]['awarded_to'], v[0]['primitive_ball_proxy']),
                         ('ZR-C', 'RST-1', 'B', False))
        e = t.step(700, {'A1': 'A'}, (18., 50.), holder_xy=(18., 50.))
        self.assertEqual(rows(e, 'R-11'), [])            # once per crossing
        # U4-07: control gained inside the zone is not a crossing
        t2 = possessed(xy=A_ZONE)
        self.assertEqual(rows(t2.ledger, 'R-11'), [])

    def test_R12_ZRT_pass_from_outside_into_own_zone_teammate_first_touch(self):
        t = possessed(xy=(30., 50.))
        t.step(550, {}, (30., 50.), [{'kind': 'pass_release', 'player': 'A1', 'team': 'A'}])
        t.step(600, {}, (15., 50.))
        e = t.step(650, {'A2': 'A'}, (10., 50.))
        v = rows(e, 'R-12')
        self.assertEqual((v[0]['violation'], v[0]['awarded_to']), ('ZR-T', 'B'))
        # a defender first: none (U4-06: later teammate touch is not a violation either)
        t = possessed(xy=(30., 50.))
        t.step(550, {}, (30., 50.), [{'kind': 'pass_release', 'player': 'A1', 'team': 'A'}])
        t.step(600, {}, (15., 50.), [{'kind': 'touch', 'player': 'B4', 'team': 'B'}])
        e = t.step(650, {'A2': 'A'}, (10., 50.))
        self.assertEqual(rows(t.ledger, 'R-12'), [])
        # released inside and never left the zone: none
        t = possessed(xy=A_ZONE)
        t.step(550, {}, A_ZONE, [{'kind': 'pass_release', 'player': 'A1', 'team': 'A'}])
        t.step(650, {'A2': 'A'}, (10., 50.))
        self.assertEqual(rows(t.ledger, 'R-12'), [])
        # U4-03: released inside, leaves, returns, teammate first
        t = possessed(xy=A_ZONE)
        t.step(550, {}, A_ZONE, [{'kind': 'pass_release', 'player': 'A1', 'team': 'A'}])
        t.step(600, {}, (25., 50.))
        t.step(650, {'A2': 'A'}, (15., 50.))
        self.assertEqual(len(rows(t.ledger, 'R-12')), 1)

    def test_R13_zone_clock_five_seconds_records_ZR1_once(self):
        t = possessed(xy=A_ZONE)                         # PP = A at 500 ms, ball in A's zone
        e = hold(t, 'A', 'A1', 550, 5450, A_ZONE)
        self.assertEqual(rows(e, 'R-13'), [])
        e = t.step(5500, {'A1': 'A'}, A_ZONE)
        v = rows(e, 'R-13')
        self.assertEqual((v[0]['violation'], v[0]['team'], v[0]['restart'], v[0]['awarded_to'], v[0]['clock_ms']),
                         ('ZR-1', 'A', 'RST-1', 'B', 5000))
        e = hold(t, 'A', 'A1', 5550, 7000, A_ZONE)
        self.assertEqual(rows(e, 'R-13'), [])
        # the other team's possession in A's zone does not run A's clock
        t = possessed('B', 'B1', xy=A_ZONE)
        hold(t, 'B', 'B1', 550, 7000, A_ZONE)
        self.assertEqual(rows(t.ledger, 'R-13'), [])

    def _clock_running(self):
        t = possessed(xy=A_ZONE)
        hold(t, 'A', 'A1', 550, 2000, A_ZONE)
        self.assertEqual(dict(t.public().zone_clock_ms)['A'], 1500)
        return t

    def test_R14_reset_trigger_ball_leaves_zone(self):
        t = self._clock_running()
        e = t.step(2050, {'A1': 'A'}, (25., 50.))
        self.assertEqual(rows(e, 'R-14')[0]['trigger'], 'ball_left_zone')
        self.assertEqual(dict(t.public().zone_clock_ms)['A'], 0)
        t.step(2100, {'A1': 'A'}, A_ZONE)                # re-entry starts from 0
        t.step(2600, {'A1': 'A'}, A_ZONE)
        self.assertEqual(dict(t.public().zone_clock_ms)['A'], 500)

    def test_R14_reset_trigger_passive_possession_change(self):
        t = self._clock_running()
        t.step(2050, {}, A_ZONE, [{'kind': 'loose'}])
        e = hold(t, 'B', 'B1', 2100, 2600, A_ZONE)
        self.assertEqual(t.public().passive_team, 'B')
        self.assertIn('passive_possession_change', [x['trigger'] for x in rows(e, 'R-14')] +
                      [x['trigger'] for x in rows(t.ledger, 'R-14')])
        self.assertEqual(dict(t.public().zone_clock_running)['A'], False)

    def test_R14_reset_trigger_defender_touch_restarts_from_zero(self):
        t = self._clock_running()
        e = t.step(2050, {'A1': 'A'}, A_ZONE, [{'kind': 'touch', 'player': 'B2', 'team': 'B'}])
        # same instant as the carrier: contested (C-3), which is also a defender touch
        self.assertEqual(rows(e, 'R-14')[0]['trigger'], 'defender_touch')
        t.step(2100, {'A1': 'A'}, A_ZONE)
        self.assertEqual(dict(t.public().zone_clock_ms)['A'], 50)
        self.assertEqual(t.public().passive_team, 'A')

    def test_R14_reset_trigger_restart(self):
        t = self._clock_running()
        e = t.step(2050, {}, A_ZONE, [{'kind': 'restart_awarded', 'team': 'A'}])
        self.assertEqual(rows(e, 'R-14')[0]['trigger'], 'restart')
        self.assertEqual(dict(t.public().zone_clock_running)['A'], False)

    def test_R14_R20_reset_trigger_dead_ball_stopped_until_live(self):
        t = self._clock_running()
        e = t.step(2050, {}, A_ZONE, [{'kind': 'dead'}])
        self.assertEqual(len(rows(e, 'R-20')), 1)
        self.assertEqual(rows(e, 'R-14')[0]['trigger'], 'dead_ball')
        t.step(4000, {}, A_ZONE)
        self.assertEqual((dict(t.public().zone_clock_ms)['A'], dict(t.public().zone_clock_running)['A']), (0, False))
        t.step(4050, {}, A_ZONE, [{'kind': 'live'}])
        t.step(4550, {}, A_ZONE)
        self.assertEqual((dict(t.public().zone_clock_ms)['A'], dict(t.public().zone_clock_running)['A']), (500, True))
        self.assertEqual(t.public().passive_team, 'A')

    def test_R15_R16_keeper_protection_needs_passive_possession_and_position(self):
        t = possessed('A', 'A10', xy=A_ZONE)
        self.assertTrue(t.keeper_protected('A', A_ZONE))             # R-15
        self.assertFalse(t.keeper_protected('A', (25., 50.)))        # R-16 / KP-06, KP-14: outside
        self.assertFalse(t.keeper_protected('B', B_ZONE))            # R-16 / KP-05: team lacks PP
        self.assertFalse(t.keeper_protected('A', (20., 50.)))        # G-3: exactly on the arc is outside
        self.assertTrue(t.keeper_protected('A', (19.999, 50.)))
        self.assertFalse(PossessionTracker().keeper_protected('A', A_ZONE))   # no possession yet

    def test_R17_freeze_legal_ruleset_102(self):
        t = possessed()
        self.assertTrue(t.freeze_legal('B', 'field', MID))           # any eligible player, not only the carrier
        self.assertTrue(t.freeze_legal('A', 'field', A_ZONE))
        self.assertFalse(t.freeze_legal('B', 'keeper', B_ZONE))      # KP-13(b): in own zone, any phase
        self.assertFalse(t.freeze_legal('A', 'keeper', A_ZONE))
        self.assertTrue(t.freeze_legal('B', 'keeper', (79., 50.)))   # KP-03/04: outside own zone
        self.assertTrue(t.freeze_legal('B', 'keeper', (80., 50.)))   # distance exactly R: outside (G-3)
        self.assertFalse(t.freeze_legal('B', 'keeper', (80.001, 50.)))
        self.assertTrue(t.freeze_legal('B', 'keeper', A_ZONE))       # the opponents' zone is not his own
        with self.assertRaises(UnresolvedOutcome):
            t.freeze_legal('B', 'archer', MID)
        with self.assertRaises(UnresolvedOutcome):
            PossessionTracker(RulesConfig(ruleset='1.0.1')).freeze_legal('B', 'field', MID)

    def test_R18_out_of_play_keeps_passive_until_restart_awards_it(self):
        t = possessed()
        e = t.step(550, {}, (50., 101.), [{'kind': 'out_of_play'}])
        self.assertEqual(len(rows(e, 'R-18')), 1)
        self.assertEqual((t.public().passive_team, t.public().ball_status), ('A', 'out_of_play'))
        t.step(900, {}, (50., 100.))
        self.assertEqual(t.public().passive_team, 'A')
        t.step(950, {}, (50., 100.), [{'kind': 'restart_awarded', 'team': 'B'}])
        self.assertEqual((t.public().passive_team, t.public().ball_status), ('B', 'restart_pending'))

    def test_P3_awarded_restart_sets_passive_before_any_direct_possession(self):
        t = PossessionTracker()
        t.step(0, {}, MID, [{'kind': 'restart_awarded', 'team': 'B'}])
        self.assertEqual((t.public().passive_team, t.public().direct_team), ('B', None))

    def test_R19_RST1_restart_passive_to_opponent_clock_zero_and_stopped(self):
        t = possessed(xy=A_ZONE)
        hold(t, 'A', 'A1', 550, 5500, A_ZONE)
        self.assertEqual(len(rows(t.ledger, 'R-13')), 1)
        e = t.step(5550, {}, MID, [{'kind': 'restart_awarded', 'team': 'B', 'rst1': True}])
        p = t.public()
        self.assertEqual(len(rows(e, 'R-19')), 1)
        self.assertEqual(p.passive_team, 'B')
        self.assertEqual((dict(p.zone_clock_ms), dict(p.zone_clock_running)),
                         ({'A': 0, 'B': 0}, {'A': False, 'B': False}))

    def test_R21_keeper_catch_passive_stays_with_shooter_until_threshold(self):
        t = possessed('A', 'A1', xy=(70., 50.))
        t.step(550, {}, (70., 50.), [{'kind': 'shot_release', 'player': 'A1', 'team': 'A'}])
        hold(t, 'B', 'B10', 600, 1050, B_ZONE)           # Keeper holds for 450 ms
        self.assertEqual(t.public().passive_team, 'A')
        self.assertFalse(t.keeper_protected('B', B_ZONE))
        t.step(1100, {'B10': 'B'}, B_ZONE)               # 500 ms
        self.assertEqual(t.public().passive_team, 'B')
        self.assertTrue(t.keeper_protected('B', B_ZONE))
        self.assertEqual(dict(t.public().zone_clock_ms)['B'], 0)

    def test_R22_C3_same_instant_touches_contested_no_first_touch_violation(self):
        t = possessed(xy=(30., 50.))
        t.step(550, {}, (30., 50.), [{'kind': 'pass_release', 'player': 'A1', 'team': 'A'}])
        e = t.step(650, {}, (10., 50.), [{'kind': 'touch', 'player': 'A2', 'team': 'A'},
                                         {'kind': 'touch', 'player': 'B2', 'team': 'B'}])
        p = t.public()
        self.assertEqual(len(rows(e, 'R-22')), 1)
        self.assertEqual((p.contested, p.passive_team), (True, 'A'))
        self.assertEqual(rows(t.ledger, 'R-12'), [])
        t.step(700, {'A2': 'A'}, (10., 50.))             # later teammate control: still no ZR-T
        self.assertEqual(rows(t.ledger, 'R-12'), [])

    def test_unknown_event_is_unresolved_not_invented(self):
        with self.assertRaises(UnresolvedOutcome):
            PossessionTracker().step(0, {}, MID, [{'kind': 'hand_fight'}])

    def test_module_is_pure_imports(self):
        tree = ast.parse((Path(__file__).parent / 'possession.py').read_text())
        mods = set()
        for n in ast.walk(tree):
            if isinstance(n, ast.Import):
                mods |= {a.name for a in n.names}
            elif isinstance(n, ast.ImportFrom):
                mods.add(n.module)
        self.assertTrue(mods <= {'dataclasses', 'math', 'typing'}, mods)

    def test_determinism_same_inputs_same_ledger_and_state(self):
        def run():
            t = possessed(xy=A_ZONE)
            hold(t, 'A', 'A1', 550, 3000, A_ZONE)
            t.step(3050, {'A1': 'A', 'B1': 'B'}, A_ZONE)
            t.step(3100, {}, A_ZONE, [{'kind': 'loose'}])
            hold(t, 'B', 'B1', 3150, 4000, A_ZONE)
            t.step(4050, {}, (50., 101.), [{'kind': 'out_of_play'}])
            t.step(4100, {}, MID, [{'kind': 'restart_awarded', 'team': 'A'}])
            return t.ledger, t.public()
        a, b = run(), run()
        self.assertEqual(a, b)
        self.assertGreater(len(a[0]), 8)


if __name__ == '__main__':
    unittest.main()
