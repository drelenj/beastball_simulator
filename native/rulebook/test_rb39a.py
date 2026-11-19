"""RB-3.9a PROVISIONAL (owner CANON ruling 18 Nov 2026 evening): scrimmage set formation, native-rb/3."""
import math
import pytest
from .test_rb36 import rb3
from .test_rb34 import live
from .port import RulebookPort
from . import formation as F
from native import cognition as C
from native.throw_speed import release_speed


def scrim(p, team='A', x=50., y=30., reason='turnover', tackled=None, tackler=None):
    s, e = p.m.s, p.m.e
    r = e.award(team, x, y, reason, fresh=True, normalize=False)
    if tackled: r.rs.update(snapper=tackled, tackler=tackler)
    assert e.rb_form_restart()
    return s, e, s.restart


def field(s, team): return [q for q in s.players.values() if q.active and q.team == team and q.role == 'field' and q.eligible(s.now)]


def check(s, r):
    f = r.rs['formation']; sg = s.attack_sign(r.team); x0 = r.x
    assert r.y == 50. and r.taker_spot == (x0, 50.) and s.ball.y == 50.
    rec = s.players[f['receiver']]; assert (rec.x, rec.y) == (x0 - sg * f['depth'], 50.)
    sn = s.players[f['snapper']]; assert (sn.x, sn.y) == (x0, 50.) and sn.team == r.team
    for q in s.players.values():
        if not q.active or q.role == 'archer' or q.id == sn.id: continue
        if q.team == r.team: assert sg * (q.x - x0) <= -F.OFFENSE_BEHIND_M + 1e-9 or q.id == rec.id
        elif q.id == f['nose']: assert (q.x, q.y) == (x0 + sg * F.NOSE_TACKLE_M, 50.)
        else: assert sg * (q.x - x0) >= f['zone'] + F.DEFENSE_MARGIN_M - 1e-9
    return f


@pytest.mark.parametrize('x,want', [(3., 10.), (50., 50.), (97., 90.), (10., 10.), (90., 90.)])
def test_spot_y50_and_x_clamped(x, want):
    p = rb3(); live(p); s, e, r = scrim(p, x=x, y=12., reason='minor_count_plus')   # no 40 m normalisation
    assert (r.x, r.y) == (want, 50.); check(s, r)


def test_first_tackle_scrimmage_has_one_nose_tackle_and_everybody_else_outside_the_zone():
    p = rb3(); s, e, a, t = live(p)
    tackled = field(s, 'A')[0].id; tackler = field(s, 'B')[0].id
    s, e, r = scrim(p, 'A', 40., 70., 'first_tackle', tackled, tackler)
    f = check(s, r); assert f['nose'] == tackler and f['snapper'] == tackled and f['depth'] == 5 and f['zone'] == 5
    inside = [q.id for q in s.players.values() if q.active and q.role != 'archer' and q.team == 'B'
              and 0 <= s.attack_sign('A') * (q.x - r.x) < f['zone']]
    assert inside == [tackler]


@pytest.mark.parametrize('reason', ['turnover', 'goal'])
def test_no_nose_tackle_after_score_or_turnover_and_snap40_depths(reason):
    p = rb3(); live(p); s, e, r = scrim(p, 'A', 50., 20., reason)
    f = check(s, r); assert f['nose'] is None
    if reason == 'goal': assert r.kind == 'snap40' and f['depth'] == 10 and f['zone'] == 20 and r.x == s.ends['A'] + 40


def test_snapper_is_nearest_eligible_field_player_when_tackled_player_ineligible():
    p = rb3(); s, e, a, t = live(p); mates = field(s, 'A'); bad = mates[0]; bad.disqualified = True
    s, e, r = scrim(p, 'A', 50., 50., 'first_tackle', bad.id, field(s, 'B')[0].id)
    assert r.rs['snapper'] != bad.id and s.players[r.rs['snapper']].role == 'field'


def test_snap_goes_straight_back_to_the_receiver_at_distance_speed_and_stays_on_the_field():
    p = rb3(); s, e, a, t = live(p)
    s, e, r = scrim(p, 'A', 12., 50., 'turnover'); f = check(s, r)
    sn = s.players[f['snapper']]; r.taker = sn.id; assert e.ready(sn.id)
    p.capture(s.now); s.now += 300; v, b = p.view(sn.id, s.now)
    assert v.formation[:2] == (f['snapper'], f['receiver'])
    i, rec = C.decide(v, b)
    assert i.kind == 'restart_pass' and i.target == f['receiver'] and i.aim == f['receiver_xy']
    sg = s.attack_sign('A'); assert sg * (i.aim[0] - r.x) < 0 and 0 < i.aim[0] < 100      # backward, on the field
    assert i.speed == release_speed(f['depth'], v.max_throw_speed) == 12.5
    others = [q for q in s.players.values() if q.active and q.role != 'archer' and q.id != sn.id]
    for q in others[:6]:
        vq, bq = p.view(q.id, s.now); iq, _ = C.decide(vq, bq)
        assert iq.kind == 'restart_position' and iq.aim == f['spots'][q.id]           # everybody holds his spot


def test_watchdog_reports_three_identical_restarts_and_never_intervenes():
    p = rb3(); live(p)
    for k in range(3):
        s, e, r = scrim(p, 'A', 50., 50., 'turnover')
    assert [x['data']['repeats'] for x in e.log if x['event'] == 'restart_repeat_report'] == [3]
    assert s.restart is r and r.kind == 'scrim'


def test_tosses_and_rb2_are_unchanged():
    p = rb3(); live(p); e = p.m.e; r = e.award('A', 30., 0., 'boundary', normalize=False)
    assert r.kind == 'toss' and not e.rb_form_restart() and 'formation' not in r.rs
    q = RulebookPort(1); assert not hasattr(q.m.e, 'rb_form_restart')


def test_determinism_same_code_roster_seed():
    from native.run import run_match
    a, _ = run_match(1, rb3().config, max_steps=2000, port_factory=lambda *x, **k: rb3())
    b, _ = run_match(1, rb3().config, max_steps=2000, port_factory=lambda *x, **k: rb3())
    assert (a['trace_hash'], a['state_hash']) == (b['trace_hash'], b['state_hash'])
