"""RB-3.24 boundary tests. Fixtures use the same port as regulation matches."""
import ast
from dataclasses import replace
from pathlib import Path

import pytest

from native import cognition as C, prism_registry as P
from native import prism_lab as LAB
from native.roster import load_rows, RosterError, rb3_control_rosters
from .port import RulebookPort
from .test_individuation import config


def rows():
    return [dict(a.values, id=a.source_id, role=a.role)
            for a in rb3_control_rosters()['A'].athletes]


@pytest.mark.parametrize('name', P.NEW_RATINGS)
def test_loader_accepts_normalized_explicit_new_rating(name):
    raw = rows()
    raw[0][name] = .43
    assert load_rows(raw, 'A').athletes[0].get(name) == .43
    raw[0][name] = -1
    with pytest.raises(RosterError, match=name):
        load_rows(raw, 'A')


def test_alias_precedence_and_phase1_inactive_storage():
    values = dict(marking=.42, judgment=.9, contact_resistance=.83,
                  carrier_duel=.9, defending=.61)
    effective = P.effective_ratings(values)
    assert effective['defending'] == .61 and effective['evasion'] == .9
    del values['defending']
    assert P.effective_ratings(values)['defending'] == .42
    raw = rows()
    raw[0].update(passing=.92, reflex=.97)
    rs = rb3_control_rosters()
    a = RulebookPort(1, config(rs, False), rosters=rs)
    rs['A'] = load_rows(raw, 'A')
    b = RulebookPort(1, config(rs, False), rosters=rs)
    assert a.behavior_digest == b.behavior_digest
    assert a.config.digest != b.config.digest


@pytest.fixture
def sensor_port():
    r = rb3_control_rosters()
    port = RulebookPort(2, config(r), rosters=r)
    state = port.m.s
    me = next(p for p in state.players.values() if p.active and p.role == 'field')
    opponent = next(p for p in state.players.values() if p.active and p.team != me.team and p.role == 'field')
    for player in state.players.values():
        player.active = player in (me, opponent)
    me.x, me.y, me.facing = 50., 50., (1., 0.)
    opponent.x, opponent.y = 65., 52.
    state.ball.carrier = None
    state.ball.x, state.ball.y, state.ball.z = 55., 48., 2.
    return port, me, opponent


def test_delivered_view_and_reflex_do_not_read_later_opponent_state(sensor_port):
    port, me, opponent = sensor_port
    port.capture(0)
    now = port.config.latency_ms
    port.m.s.now = now
    view, belief = port.view(me.id, now)
    assert opponent.id in dict(view.body_height)
    original = C.decide(view, belief)
    ready = port.reflex_catch_ready_at(me)
    assert ready == pytest.approx(now + 1000 * P.reflex_seconds(.7))
    opponent.native_registry['defending'] = 1.
    opponent.x, opponent.a.height = 99., 3.2
    port.m.s.ball.x, port.m.s.ball.z = 0., 100.
    again, after = port.view(me.id, now)
    assert view.body_height == again.body_height
    assert view.registry_ratings == again.registry_ratings
    assert view.tracks == again.tracks and view.ball_course == again.ball_course
    assert original == C.decide(view, belief)
    assert port.reflex_catch_ready_at(me) == ready


@pytest.mark.parametrize('name', ('vision', 'awareness', 'clarity', 'focus', 'reaction',
                                  'instinct', 'anticipation', 'playmaking', 'defending',
                                  'zone_coverage', 'goalkeeping', 'disruption',
                                  'in_air_ball_pursuit', 'live_ball_pursuit', 'passing',
                                  'finishing', 'evasion', 'takedown', 'reflex', 'agility'))
def test_hook_probe_is_deterministic_and_has_no_world_parameter(name):
    # Probe functions execute without a port, engine, roster of other players or global RNG.
    assert LAB.probe(name, .8, 4) == LAB.probe(name, .8, 4)


def test_registry_module_has_no_live_state_dependencies():
    tree = ast.parse(Path(P.__file__).read_text())
    assert {node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)} == {'math'}
    assert not {node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)} & {
        'players', 'engine', 'quivers', 'm', 'rng'}


def test_reaction_and_reflex_have_separate_clocks(sensor_port):
    port, me, _ = sensor_port
    intent = C.ActionIntent('i', 'd', me.id, 'carry', None, (60., 50.), None, None, 0)
    deliberate = port.prism_decision_interval_ms(me.id, intent)
    me.native_registry['reflex'] = .95
    assert port.prism_decision_interval_ms(me.id, intent) == deliberate
    evade = replace(intent, contact='dodge')
    interval = port.prism_decision_interval_ms(me.id, evade)
    me.native_individual['reaction'] = .95
    assert port.prism_decision_interval_ms(me.id, evade) == interval
    assert port.prism_decision_interval_ms(me.id, intent) < deliberate
