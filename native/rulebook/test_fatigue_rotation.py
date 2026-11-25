from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

import pytest

from native import cognition
from native.oracle.matches import match_build
from native.oracle.snapshot import capture, restore
from native.rulebook.fatigue_rotation import (KEEPER_REGULATION_MIN_MS, reserve_after,
                                               select_substitute, technique)


def test_sprint_standing_and_bench_curves():
    stamina_levels = (.60, .70, .85, 1.)
    sprint = [[reserve_after(1., stamina, 1., t) for t in (30, 60, 90)]
              for stamina in stamina_levels]
    assert all(a > b > c for a, b, c in sprint)
    assert all(a < b < c < d for a, b, c, d in zip(*sprint))
    for stamina in stamina_levels:
        sprint_threshold = .4 / (1 - reserve_after(1., stamina, 1., 1.))
        assert reserve_after(1., stamina, 1., sprint_threshold) == pytest.approx(.60)
        assert reserve_after(.6, stamina, 0., 75., bench=True) == pytest.approx(.75)
        assert .60 < reserve_after(.6, stamina, 0., 50.) < .75
    assert reserve_after(.8, .70, .50, 50.) == .8
    assert reserve_after(.8, .85, .50, 50.) > .8
    losses = [rating - technique(rating, .60) for rating in (.50, .95)]
    assert losses[0] > losses[1] > 0
    assert technique(.50, .60) < technique(.95, .60)


def test_priority_and_overall_within_tier():
    p = {ident: SimpleNamespace(id=ident) for ident in ('out', 'exact', 'exact2', 'group', 'other')}
    labels = {'out': ('HNT', 95.), 'exact': ('HNT', 53.), 'exact2': ('HNT', 54.),
              'group': ('TRK', 62.), 'other': ('STR', 96.)}
    assert select_substitute(p['out'], list(p.values())[1:], labels) == (p['exact2'], 'position')
    assert select_substitute(p['out'], [p['other'], p['group']], labels) == (p['group'], 'group')
    assert select_substitute(p['out'], [p['other']], labels) == (p['other'], 'overall')


@pytest.fixture(scope='module')
def build():
    parent = match_build(1, roster='control')
    return replace(parent, config=replace(parent.config, fatigue_rotation=True))


def test_rotation_dead_ball_slot_and_specialists(build):
    port = build.create(record=False).port
    e, state = port.m.e, port.m.s
    field, keeper, archer = [next(p for p in state.players.values()
                                  if p.active and p.team == 'A' and p.role == role)
                             for role in ('field', 'keeper', 'archer')]
    slot = field.slot
    for p in (field, keeper, archer):
        p.fatigue = .60
    state.phase = port.types.Phase.LIVE
    port.rotation.rotate()
    assert all(p.active for p in (field, keeper, archer))
    e.award('A', 42., 50., 'after_score', fresh=True, normalize=False)
    port.rotation.rotate()
    assert not field.active and keeper.active and archer.active
    replacement = next(p for p in state.players.values() if p.team == 'A' and p.active and p.slot == slot)
    field.fatigue = .75
    port.rotation.regulation_ms[keeper.id] = KEEPER_REGULATION_MIN_MS - 1
    e.award('A', 46., 50., 'after_score', fresh=True, normalize=False)
    port.rotation.rotate()
    assert field.active and field.slot == slot and not replacement.active and keeper.active
    port.rotation.regulation_ms[keeper.id] += 1
    e.award('A', 48., 50., 'after_score', fresh=True, normalize=False)
    port.rotation.rotate()
    assert not keeper.active and archer.active
    events = [row['data'] for row in e.log if row['event'] == 'fatigue_substitution']
    assert [row['reason'] for row in events] == ['fatigue', 'starter_return', 'fatigue']
    assert events[0]['outgoing_energy'] == .60 and events[1]['incoming_energy'] == .75


def test_fatigue_snapshot_and_roster_metadata_isolation(build):
    first = build.create()
    first.play(120)
    a = capture(build, first)
    second, prepared = restore(a)
    assert prepared is None
    first.play(400)
    second.play(400)
    assert first.result()['trace_hash'] == second.result()['trace_hash']
    assert first.result()['state_hash'] == second.result()['state_hash']
    port = first.port
    port.capture(port.m.s.now)
    later = port.m.s.now + 1000
    pid = next(p.id for p in port.m.s.players.values() if p.active and p.role == 'field')
    view, belief = port.view(pid, later)
    assert view is not None
    baseline = cognition.decide(view, belief)
    port.rotation.roster = {pid: ('PDR', 999.)}
    assert cognition.decide(view, belief) == baseline
    assert 'rotation_candidates' not in repr(view)
    root = Path(__file__).parents[1]
    for path in (*root.glob('cognition*.py'), root / 'prism_core.py', root / 'perception.py'):
        assert 'rotation_candidates' not in path.read_text()


def test_sprint_applies_output_without_reducing_cognition(build):
    port = build.create(record=False).port
    state = port.m.s
    runner = next(p for p in state.players.values() if p.active and p.role == 'field')
    skills = runner.native_registry.copy()
    a = runner.a
    before = (a.braking, a.turning, a.strength, a.jump_height, a.agility, a.catching,
              runner.native_max_throw_speed)
    runner.vx = a.maximum_speed
    active = {p.id for p in state.players.values() if p.active}
    now, live = state.now, state.live_ms
    state.now += 60_000
    state.live_ms += 60_000
    port.rotation.advance(now, live, active)
    assert runner.fatigue == pytest.approx(reserve_after(1., a.endurance, 1., 60.))
    assert all(current < initial for current, initial in zip(
        (a.braking, a.turning, a.strength, a.jump_height, a.agility, a.catching,
         runner.native_max_throw_speed), before))
    assert runner.native_registry == skills
