"""Run original RB-2.1 scoring and F5 witnesses against RB/3 rosters.

RB/3 uses roster-qualified IDs; adapt only ID string literals and the port
constructor, keeping each original test body and assertions intact.
"""
import re
import types
import pytest
from . import test_scoring, test_discipline
from .test_rb3 import fixture
from .port import RulebookPort


def rb3_port(seed=1):
    cfg,rosters=fixture()
    return RulebookPort(seed,cfg,rosters=rosters)


def qualify(value):
    if isinstance(value,types.CodeType):
        return value.replace(co_consts=tuple(qualify(v) for v in value.co_consts))
    if isinstance(value,str) and re.fullmatch(r'[AB]\d+',value):
        team,number=value[0],int(value[1:])
        # The legacy A10/B10 slots are Keepers; the uniform RB/3 test roster
        # numbers its first Keeper p18. Field players retain their number.
        return f'{team}:p{18 if number==10 else number}'
    if isinstance(value,tuple):return tuple(qualify(v) for v in value)
    return value


def adapted(fn):
    namespace=dict(fn.__globals__,RulebookPort=rb3_port)
    return types.FunctionType(qualify(fn.__code__),namespace,fn.__name__,fn.__defaults__,fn.__closure__)


SCORING=[name for name in dir(test_scoring) if name.startswith('test_') and name not in (
    'test_real_release_band_and_goal','test_default_runner_records_complete_banded_scoring_basis')]


@pytest.mark.parametrize('name',SCORING)
def test_original_rb21_scoring_under_rb3(name):
    adapted(getattr(test_scoring,name))()


@pytest.mark.parametrize('distance,points',[(9.999,2),(10,3),(19.999,3),(20,4)])
def test_original_rb21_shot_bands_under_rb3(distance,points):
    adapted(test_scoring.test_real_release_band_and_goal)(distance,points)


def test_original_rb21_defender_hold_under_rb3():
    adapted(test_discipline.test_defender_noncarrier_hold_is_defence_minor_and_offside_no_award)(rb3_port())
