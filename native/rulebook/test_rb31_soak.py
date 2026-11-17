from types import SimpleNamespace
from collections import Counter
from .rb31_soak import measure


def test_terminal_attempt_is_not_any_attempt_during_possession():
    players={'A:0':SimpleNamespace(team='A'),'B:0':SimpleNamespace(team='B')}
    ledger=[{'t_ms':0,'event':'passive_possession','team':'A'},
            {'t_ms':20,'event':'passive_possession','team':'B'},
            {'t_ms':40,'event':'passive_possession','team':'A'}]
    attempts=[{'t_ms':5,'team':'A','shot_attempt':True},
              {'t_ms':10,'team':'A','shot_attempt':False},
              {'t_ms':30,'team':'B','shot_attempt':True}]
    e=SimpleNamespace(possession_history=[],possession=SimpleNamespace(ledger=ledger),rb_attempts=attempts,
        log=[],s=SimpleNamespace(players=players),rb=SimpleNamespace(calls=[]),
        rb_bands={'A':Counter(),'B':Counter()},restart_results={})
    result=measure(SimpleNamespace(m=SimpleNamespace(e=e)),[])
    assert result['possessions']['A']=={'count':2,'with_attempt':1,'ending_in_attempt':0,'share_ending_in_attempt':0.}
    assert result['possessions']['B']=={'count':1,'with_attempt':1,'ending_in_attempt':1,'share_ending_in_attempt':1.}
