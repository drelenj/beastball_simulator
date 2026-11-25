from dataclasses import replace

from audit.native.rb331.events import analyze, shot_on_target
from audit.native.rb331.witness import Witness
from native.oracle.matches import match_build

from .test_rb318 import fixture


def test_release_projection_uses_ball_radius_and_goal_opening():
    p, _, _, _ = fixture()
    radius = p.m.s.ball.radius
    assert shot_on_target((80.,50.,1.5),(50.,0.,0.),100.,p.config,radius)
    assert not shot_on_target((80.,54.,1.5),(50.,0.,0.),100.,p.config,radius)
    assert not shot_on_target((80.,50.,1.5),(-50.,0.,0.),100.,p.config,radius)


def test_diagnosis_observes_without_altering_play():
    build = match_build(1, roster='control')
    build = replace(build,config=replace(build.config,fatigue_rotation=True,rotation_rhythm='PLANNED'))
    baseline = build.create(record=False)
    observed = build.create(record=False)
    baseline.enable_stats()
    observed.enable_stats()
    witness = Witness(observed.port, build.rosters)
    baseline.play(300)
    observed.play(300)
    a,b = baseline.result(), observed.result()
    for key in ('trace_hash','state_hash','score','box_score'):
        assert a[key] == b[key]
    analysis = analyze(witness, b['box_score'])
    assert witness.release and analysis['quota_epochs']


def test_unrelated_freeze_does_not_stop_a_carry_witness():
    p, rosters, carrier, defender = fixture()
    witness = Witness(p, rosters)
    s, e = p.m.s, p.m.e
    goal, sign = s.attack_goal(carrier.team), s.attack_sign(carrier.team)
    carrier.x = goal - sign * 12
    e.follow_carrier()
    e.emit('freeze','fixture',player=defender.id)
    carrier.x = goal - sign * 8
    e.follow_carrier()
    assert witness.carries[-1]['plane'] == 8
    e.emit('freeze','fixture',player=carrier.id)
    carrier.x = goal - sign * 5
    e.follow_carrier()
    assert witness.carries[-1]['plane'] == 8
    assert witness.carries[-1]['closing_id']
