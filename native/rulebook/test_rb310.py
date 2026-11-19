"""RB-3.10 PROVISIONAL (owner CANON rulings 18 Nov 2026 night), native-rb/3: no nose tackle, snap hold,
receiver designation hook, clear snap lane, auto-unfreeze at the formation."""
import math
import pytest
from .test_rb36 import rb3
from .test_rb34 import live
from .test_rb39a import scrim, field, check
from . import formation as F


def released(p, team='A', x=50., reason='turnover', receiver_move=None):
    s, e, r = scrim(p, team, x, 30., reason); f = r.rs['formation']
    sn = s.players[f['snapper']]; r.taker = sn.id; assert e.ready(sn.id)
    if receiver_move: s.players[f['receiver']].y += receiver_move     # step out of the lane: a missed catch
    sg = s.attack_sign(team); rx, ry = f['receiver_xy']
    v = (-sg * 12.5, 0., 1.)
    assert e.restart_release(sn.id, v, f['receiver'])
    return s, e, r, f


def positions(s): return {q.id: (round(q.x, 3), round(q.y, 3)) for q in s.players.values() if q.active and q.role != 'archer'}


def test_all_defenders_outside_the_zone_including_tackler():
    p = rb3(); s, e, a, t = live(p)
    s, e, r = scrim(p, 'A', 60., 20., 'first_tackle', field(s, 'A')[0].id, field(s, 'B')[0].id)
    f = check(s, r); sg = s.attack_sign('A')
    assert all(sg * (q.x - r.x) >= f['zone'] for q in s.players.values() if q.active and q.role != 'archer' and q.team == 'B')
    assert not hasattr(F, 'NOSE_TACKLE_M')


def test_nobody_moves_during_the_hold_and_both_teams_release_at_5m():
    p = rb3(); live(p); s, e, r, f = released(p, receiver_move=8.)       # ball flies past the receiver: missed catch
    for q in s.players.values():
        if q.active and q.role != 'archer': p.move[q.id] = (q.x + 10., q.y + 10.)   # everybody wants to run
    before = positions(s); held = 0
    while getattr(e, 'rb310_hold', None):
        p.step(); held += 1
        if getattr(e, 'rb310_hold', None): assert positions(s) == before
        assert held < 20
    rel = [x['data'] for x in e.log if x['event'] == 'snap_hold_released'][-1]
    assert rel['trigger'] == 'travelled_5m' and rel['travelled_m'] >= F.SNAP_HOLD_M
    for q in s.players.values():
        if q.active and q.role != 'archer': p.move[q.id] = (q.x + 10., q.y + 10.)
    for _ in range(8): p.step()                                            # motor picks up targets at each athlete's decision time
    assert positions(s) != before                                          # free after the trigger


def test_a_dropped_catch_touch_releases_the_hold():
    p = rb3(); live(p); s, e, r, f = released(p)
    e.emit('touch', 'test', player=f['receiver'], deliberate=False)        # the receiver touches and drops it
    assert not e.rb_hold_step(p) and e.rb310_hold is None
    assert [x['data']['trigger'] for x in e.log if x['event'] == 'snap_hold_released'] == ['touch:touch']


def test_receiver_designation_hook_and_deterministic_default():
    p = rb3(); s, e, a, t = live(p)
    s, e, r = scrim(p, 'A', 50., 30., 'turnover'); d1 = r.rs['formation']['receiver']
    q = rb3(); live(q); _, _, r2 = scrim(q, 'A', 50., 30., 'turnover'); assert r2.rs['formation']['receiver'] == d1
    assert r.rs['formation']['receiver_source'] == 'default_nearest'
    p = rb3(); s, e, a, t = live(p); pick = sorted(x.id for x in field(s, 'A'))[-1]
    p.receiver_designation = {'A': pick}
    s, e, r = scrim(p, 'A', 50., 30., 'turnover'); f = r.rs['formation']
    assert f['receiver'] == pick and f['receiver_source'] == 'team_designation' and (s.players[pick].x, s.players[pick].y) == f['receiver_xy']
    p = rb3(); s, e, a, t = live(p); p.receiver_designation = {'A': lambda st, rr: 'nobody'}
    s, e, r = scrim(p, 'A', 50., 30., 'turnover'); assert r.rs['formation']['receiver_source'] == 'default_nearest'


@pytest.mark.parametrize('kind_reason', ['turnover', 'goal'])
def test_snap_lane_is_clear(kind_reason):
    p = rb3(); s, e, a, t = live(p)
    for i, q in enumerate(field(s, 'A') + field(s, 'B')): q.y = 49. + (i % 3) * .9            # crowd y = 50
    s, e, r = scrim(p, 'A', 50., 30., kind_reason); f = r.rs['formation']
    lo, hi = sorted((r.x, f['receiver_xy'][0]))
    for q in s.players.values():
        if not q.active or q.role == 'archer' or q.id in (f['snapper'], f['receiver']): continue
        assert not (lo - .5 <= q.x <= hi + .5 and abs(q.y - 50.) < F.LANE_HALF_WIDTH_M), q.id


def test_frozen_players_are_unfrozen_with_no_buffer_or_immunity():
    p = rb3(); s, e, a, t = live(p); q = field(s, 'B')[1]; q.x, q.y = 70., 20.
    assert e.freeze(q.id, panel=True) and q.frozen(s.now)
    s, e, r = scrim(p, 'A', 50., 30., 'turnover')
    assert not q.frozen(s.now) and q.freeze_until == -1 and q.immune_until == -1 and not e.rb_thaw_buffer(q)
    d = field(s, 'A')[2]; d.x, d.y = q.x - 1., q.y
    assert e.contact_legal(d, q, 'block')[1] not in ('immune_contact', 'frozen_obstacle')
    ev = [x['data'] for x in e.log if x['event'] == 'scrimmage_formation'][-1]; assert q.id in ev['auto_unfrozen']
    s.phase = p.types.Phase.LIVE; s.restart = None; e.possession.pp = 'A'; q.x, q.y = 70., 20.
    assert e.freeze(q.id, panel=True)                                         # no immunity left


def test_determinism():
    from native.run import run_match
    a, _ = run_match(3, rb3().config, max_steps=2000, port_factory=lambda *x, **k: rb3())
    b, _ = run_match(3, rb3().config, max_steps=2000, port_factory=lambda *x, **k: rb3())
    assert (a['trace_hash'], a['state_hash']) == (b['trace_hash'], b['state_hash'])
