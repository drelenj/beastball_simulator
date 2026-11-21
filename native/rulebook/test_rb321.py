"""RB-3.21 PROVISIONAL, native-rb/3: Beastball ball material (lead targets T-B1..T-B4), the same model in every forecast,
and the RB-3.20 Part 2 revert (A4 1.0 s, RB-3.19 B1 rule) keeping the no-hand-back rule."""
import math
from dataclasses import replace
import pytest
from native.rulebook import ball_material as BM
from native.evidence.rb321.material_scenario import trial, shot, release
from .test_rb36 import rb3, defender_view, T
from .test_rb34 import live


def test_t_b1_level_35_rests_after_38_to_45_m():
    r = trial(35., 'level'); assert r['rest'] and 38. <= r['rest']['x_m'] <= 45., r


def test_t_b2_level_50_rests_within_60_m():
    r = trial(50., 'level'); assert r['rest'] and r['rest']['x_m'] <= 60., r


def test_t_b3_a_58_shot_keeps_90_percent_over_20_m():
    s = shot(); assert s['speed_fraction_at']['20m'] >= .9 and s['speed_fraction_at']['30m'] >= .9, s


def test_t_b4_a_20_pass_at_the_normal_angle_rests_within_25_m():
    r = trial(20., 'pass_angle'); assert r['rest'] and r['rest']['x_m'] <= 25., r


def test_control_the_rb320_ball_fails_the_targets():
    r = trial(35., 'level', rb321_ball_material_enabled=False); assert r['rest'] is None or r['rest']['x_m'] > 45.
    r = trial(20., 'pass_angle', rb321_ball_material_enabled=False); assert r['rest'] is None or r['rest']['x_m'] > 25.


@pytest.mark.parametrize('speed,mode', [(20., 'level'), (20., 'pass_angle'), (35., 'level'), (35., 'pass_angle'), (50., 'level'), (50., 'pass_angle')])
def test_forecasts_agree_with_the_engine_within_20_cm_at_one_second(speed, mode):
    f = trial(speed, mode)['forecast_at_1s']
    assert f['predict_path_err_m'] <= .2 and f['c4c_path_err_m'] <= .2, f


def test_launch_for_reaches_its_target_with_the_material():
    p = rb3(); s, e, T_, v = release(p, 30., 'pass_angle')     # aimed at 12 m, 1.6 m high
    P = BM.params(p.config); st = (2., 50., 1.5, *v)
    while st[0] < 14.:
        prev = st; st, _, _ = BM.fly(st, .002, P, .1075)
    f = (14. - prev[0]) / (st[0] - prev[0]); z = prev[2] + (st[2] - prev[2]) * f
    assert abs(z - 1.6) < .05, z


def test_the_native_keeper_forecasts_with_the_material():
    from native import cognition_rb3 as R3
    from b1 import emergence_intents as E
    p = rb3(); s, e, a, t = live(p); keeper = next(q for q in s.players.values() if q.team == 'B' and q.role == 'keeper' and q.active)
    p.capture(s.now); s.now += 300; v, b = p.view(keeper.id, s.now)
    assert v.ball_material == (p.config.rb321_ball_drag_k, p.config.rb321_ball_bounce_h, p.config.rb321_ball_restitution, p.config.rb321_ball_roll_decel)
    gx = v.own_goal_x; sg = v.attack_sign
    course = E.BallCourseBelief('r', v.delivered_ms, v.delivered_ms, gx + sg * 12., 50., 1.5, -sg * 40., 0., 0.)
    kv = E.KeeperView(v.observation_id, v.delivered_ms, v.body, gx, goal_radius=v.goal_radius)
    ki = R3.keeper_decide(kv, course, v.ball_material)
    assert ki.kind == 'save'
    path = BM.path((course.x, course.y, course.z, course.vx, course.vy, course.vz), v.ball_material, course.radius, 3., .01, -2., 102.)
    assert ki.course == tuple(p_ for p_ in path if p_[0] <= ki.course[-1][0] + 1e-12)
    old = E.decide_keeper(kv, course, gravity=9.81, drag=.015, restitution=.7745966692)
    assert old.course != ki.course                                # control: the b1 forecast uses the old ball


def test_material_is_in_the_effective_config_and_can_be_switched_off():
    from .config import RulebookConfigV3
    from .test_rb33 import control_rosters
    d = tuple(control_rosters()[t].digest for t in ('A', 'B'))
    on = RulebookConfigV3(roster_digests=d).record()
    assert on['rb321_ball_drag_k'] == .0005 and on['rb321_ball_bounce_h'] == .44 and on['rb321_ball_restitution'] == .6 and on['rb321_ball_roll_decel'] == 3.
    off = RulebookConfigV3(roster_digests=d, rb321_ball_material_enabled=False).record()
    assert not any(k.startswith('rb321_') for k in off)


def test_material_scenario_is_deterministic():
    assert trial(35., 'pass_angle') == trial(35., 'pass_angle')
