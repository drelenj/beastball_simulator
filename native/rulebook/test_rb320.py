"""RB-3.20 PROVISIONAL, native-rb/3: Part 1 exact ball-ground contact (defect fix); Part 2 tactics tidy (A4 horizon, B1 handoffs)."""
import math
from dataclasses import replace
import pytest
from native import cognition as C
from native import cognition_rb3 as R
from native.rulebook import ball_ground as BG
from native.evidence.rb320.ball_scenario import trial
from .test_rb36 import rb3, defender_view, T
from .test_rb34 import live

E = .7745966692


# ---------------------------------------------------------------- Part 1
class _B: pass


def test_contact_solves_the_instant_and_applies_the_stated_restitution_there():
    b = _B(); r = .1075; b.radius = r
    pre = (0., 50., .4, 10., 0., -4.)
    g, dt = 9.81, .1
    # end of an un-fixed step (as advance_ball integrates it, drag ignored for the expectation)
    b.x, b.y, b.z, b.vx, b.vy, b.vz = 1., 50., .4 - .4 - .5 * g * dt * dt, 10., 0., -4. - g * dt
    m = _B(); m.assume = dict(gravity=g, ball_restitution=E, ball_drag=0.)
    tc = (-4. + math.sqrt(16. + 2 * g * (.4 - r))) / g
    assert 0 < tc < dt
    assert BG.contact(m, b, dt, pre) is True
    vzc = -4. - g * tc; vz1 = -vzc * E; tau = dt - tc
    assert abs(b.vz - (vz1 - g * tau)) < 1e-9 and abs(b.z - (r + vz1 * tau - .5 * g * tau * tau)) < 1e-9
    assert abs(b.vx - 10. * .76) < 1e-9 and abs(b.x - (10. * tc + 7.6 * tau)) < 1e-9
    # the rolling branch at the contact instant when |vz| <= 2
    pre2 = (0., 50., .15, 10., 0., -1.)
    b.x, b.y, b.z, b.vx, b.vy, b.vz = 1., 50., 0., 10., 0., -1.98
    assert BG.contact(m, b, dt, pre2) is False and b.vz == 0 and b.z == r and 0 < b.vx < 10.


def test_a_ball_already_on_the_surface_keeps_the_original_rules():
    b = _B(); r = .1075; b.radius = r; m = _B(); m.assume = dict(gravity=9.81, ball_restitution=E, ball_drag=.015)
    b.x, b.y, b.z, b.vx, b.vy, b.vz = 1., 50., .09, 10., 0., -.98
    assert BG.contact(m, b, .1, (0., 50., r, 10., 0., 0.)) is False
    assert b.vz == 0 and abs(b.vx - 10. * .7) < 1e-12 and b.z == r


@pytest.mark.parametrize('speed', [20., 35., 50.])
def test_engine_bounces_keep_the_stated_restitution_with_the_fix_and_exceed_it_without(speed):
    on = trial(speed, 'pass_angle', fix=True); off = trial(speed, 'pass_angle', fix=False)
    e_on = [b['e_from_apex'] for b in on['bounces'][1:]]
    e_off = [b['e_from_apex'] for b in off['bounces'][1:]]
    assert e_on and all(abs(x - E) < .006 for x in e_on), e_on
    assert e_off and max(e_off) > .85, e_off                  # control: the un-fixed step inflates the restitution


def test_the_free_ball_forecast_uses_the_same_contact_rule():
    p = rb3(); s, e, a, t = live(p); g = p.geom
    class Ball: pass
    b = Ball(); b.x, b.y, b.z, b.vx, b.vy, b.vz, b.radius = 10., 50., 1.5, 20., 0., 0., .1075
    path = g.predict_path(b, 9.81, .015, E, horizon=4., step=.05)
    zs = [z for _, _, _, z in path]
    apex = [zs[i] for i in range(1, len(zs) - 1) if zs[i] >= zs[i - 1] and zs[i] > zs[i + 1] and zs[i] > .2]
    assert len(apex) >= 2 and abs(((apex[1] - .1075) / (apex[0] - .1075)) ** .5 - E) < .05
    p0 = rb3(rb320_exact_bounce=False); s0, *_ = live(p0); b0 = Ball(); b0.x, b0.y, b0.z, b0.vx, b0.vy, b0.vz, b0.radius = 10., 50., 1.5, 20., 0., 0., .1075
    zs0 = [z for _, _, _, z in p0.geom.predict_path(b0, 9.81, .015, E, horizon=4., step=.05)]
    apex0 = [zs0[i] for i in range(1, len(zs0) - 1) if zs0[i] >= zs0[i - 1] and zs0[i] > zs0[i + 1] and zs0[i] > .2]
    assert ((apex0[1] - .1075) / (apex0[0] - .1075)) ** .5 > ((apex[1] - .1075) / (apex[0] - .1075)) ** .5


def test_fix_flag_is_in_the_effective_config_only_when_on():
    from .config import RulebookConfigV3
    from .test_rb33 import control_rosters
    d = tuple(control_rosters()[t].digest for t in ('A', 'B'))
    assert RulebookConfigV3(roster_digests=d).record()['rb320_exact_bounce'] is True
    assert 'rb320_exact_bounce' not in RulebookConfigV3(roster_digests=d, rb320_exact_bounce=False).record()


def test_free_ball_scenario_is_deterministic():
    assert trial(35., 'level') == trial(35., 'level')
