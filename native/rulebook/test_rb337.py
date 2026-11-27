from dataclasses import replace

import pytest

from native.port import body
from native.reaction_clock import set_speed
from native.roster import braking, turning, rb3_control_rosters
from .port import RulebookPort
from .test_prism_core import core_port


@pytest.mark.parametrize('scale',[1.5,2.0])
def test_traction_reaches_each_roster_role_and_set_speed(core_port, scale):
    base = core_port[0]
    port = RulebookPort(1,replace(base.config,traction_scale=scale),rosters=rb3_control_rosters())
    for pid,old in base.m.s.players.items():
        trial = port.m.s.players[pid]
        assert trial.a.braking == pytest.approx(braking(old.a.agility,scale))
        assert trial.a.turning == pytest.approx(turning(old.a.agility,scale))
        assert set_speed(trial) == pytest.approx(.40*body(trial).braking)
        assert trial.a.acceleration==old.a.acceleration
        assert trial.a.maximum_speed==old.a.maximum_speed
    assert port.typical_braking==braking(.7,scale)
    assert 'traction_scale' not in base.config.record()
    assert port.config.record()['traction_scale']==scale


def test_invalid_traction_trial_is_rejected(core_port):
    with pytest.raises(ValueError,match='traction_scale'):
        replace(core_port[0].config,traction_scale=1.25)
