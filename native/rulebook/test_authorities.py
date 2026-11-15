from dataclasses import replace
from types import SimpleNamespace
import pytest
from .config import RulebookConfig
from .authorities import Authorities,CREW
from native.config import NativeConfig

@pytest.fixture
def law():return Authorities(RulebookConfig())

def player():return SimpleNamespace(id='A0',team='A',role='field',minor_count=0,major_count=0,active=True,disqualified=False)

def test_legacy_digest_unchanged():
    assert NativeConfig().digest=='f31b44a1eb787f14c9d606be74fa40658c6b7b9772ee1e882b075b856edc3035'
    assert RulebookConfig().digest!=NativeConfig().digest

def test_bands_and_carry_own_awards(law):
    assert law.points(carry=True)==2
    law.config=replace(law.config,scoring='banded')
    assert [law.points(distance=d) for d in (0,9.999,10,19.999,20,100)]==[2,2,3,3,4,4]
    assert law.points(carry=True)==5 and law.points(own=True)==2
    assert law.points(award=True)==1
    law.enter_period(4);assert law.points(award=True)==3

@pytest.mark.parametrize('period,duration',[(2,120000),(3,600000),(4,120000),(5,180000),(6,60000)])
def test_breaks(period,duration,law):
    r=law.enter_period(period);assert r['duration_ms']==duration and r['exchange_ends']

def test_timeout_triggers_and_resources(law):
    law.score('B');law.score('B')
    assert law.timeout('A',False,'B',600000,{'A':0,'B':4}) is None
    r=law.timeout('A',True,'B',600000,{'A':0,'B':4});assert r['duration_ms']==45000
    assert law.timeout('A',True,'B',600000,{'A':0,'B':4}) is None
    law.score('B');assert law.timeout('A',True,'B',600000,{'A':0,'B':6}) is None
    law.enter_period(3);assert law.timeouts=={'A':2,'B':2}
    law.enter_period(4);assert law.timeout('A',True,'A',60000,{'A':0,'B':0})
    law.enter_period(5);assert law.timeouts=={'A':1,'B':1}
    law.enter_period(6);assert law.timeout('A',True,'A',0,{'A':0,'B':0}) is None

def test_discipline_windows_do_not_end_on_score(law):
    p=player();r=law.discipline(p,'major',1000)
    assert not p.active and r['duration_ms']==120000
    law.score('B');assert not law.can_enter(p,120999)
    assert law.can_enter(p,121000)
    law.discipline(p,'major',121000);assert p.disqualified and not law.can_enter(p,999999)
    p=player()
    for i in range(4):law.discipline(p,'minor',0)
    assert not p.active and law.exclusions[p.id]['until']==60000
    law.discipline(p,'minor',60000);assert p.disqualified

def test_quota_and_illegal_arrow(law):
    law.turnover('A')
    for i in range(15):assert law.arrow('B',False)['minor']
    assert law.arrow('B',True)['kind']=='arrow_denied'
    assert law.turnover('A') is None
    law.turnover('B');assert law.quotas['B']['arrows']==0
    assert law.config.arrow_speed==pytest.approx(250.)

def test_review_tolerance_and_stored_evidence_only(law):
    assert len(CREW)==7
    c=law.ruling('goal',recorded_disagreement_m=.05)
    r=law.review('A',c['id'],True);assert not r['reversed'] and law.challenges['A']==0 and law.timeouts['A']==1
    law.enter_period(3);c=law.ruling('boundary',scoring_play=True,recorded_disagreement_m=.05001)
    assert law.review('A',c['id'],True)['reversed'] and law.challenges['A']==1
    c=law.ruling('keeper_immunity',keeper_wrong=True);assert law.review('A',c['id'],True)['reversed']
    c=law.ruling('quota_reset');assert law.review('A',c['id'],True) is None

def test_head_evaluation_next_period_and_injury_no_randomness(law):
    p=player();law.injury(p,head=True);assert not law.can_enter(p,0)
    law.enter_period(2);assert law.can_enter(p,0)
    law.injury(p);assert not law.can_enter(p,0)

def test_each_simultaneous_timeout_trigger_can_be_consumed_once(law):
 law.enter_period(4);law.score('B');law.score('B')
 assert law.timeout('A',True,'A',60000,{'A':0,'B':2})
 assert law.timeout('A',True,'A',60000,{'A':0,'B':2})
 assert law.timeouts['A']==0
