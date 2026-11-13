from dataclasses import replace
from .matchport import run_match, MatchPort
from . import cognition as C


def test_live_truth_poison_cannot_change_delivered_course_or_release_choice():
    _, p = run_match(1, max_ms=6000, telemetry=False)
    now = p.m.s.now
    pid = next(i for i in p.active_ids() if p.m.s.players[i].role == 'keeper')
    v, b = p.deliver(pid, now)
    p.m.s.ball.z, p.m.s.ball.vz = 10000., -10000.
    v2, b2 = p.deliver(pid, now)
    assert v.ball_course == v2.ball_course
    assert C.decide(v,b)[0] == C.decide(v2,b2)[0]
    assert p._course_belief('missing', now) is None


def test_overlay_is_installed_and_course_is_delivered():
    r, p = run_match(1, max_ms=12000, telemetry=False)
    assert {'keeper','archer_movement','restart_position'} <= set(r['ownership_decisions_by_kind'])
    assert any(b is not None for b in p.course_beliefs.values())
    assert not hasattr(p, '_orig_keepers')
    assert p.m.c3_withhold(None, 'pass') is False
    for pid, b in p.course_beliefs.items():
        if b:
            assert b.captured_ms <= b.delivered_ms <= p.m.s.now


def test_release_withholding_is_pure_athlete_choice():
    sig = C.Signals('live',1,1,30000,0,0,None,None,False)
    ts = (C.Track('A1','A','field',58,50,0,0,1400),)
    v = C.AthleteView('o','A0','A','field',0,1500,40,50,True,1,0,ts,sig,
                      ownership_enabled=True,own_restraint=1.,tuck_fraction=1.)
    b = C.BeliefState('b','o',ts)
    assert C.decide(v,b)[0].kind not in ('pass','shoot','restart_pass')
    assert C.decide(replace(v,own_restraint=0.),b)[0].kind == 'pass'
