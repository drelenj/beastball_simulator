from dataclasses import replace
from io import StringIO

import pytest

from native.oracle.matches import match_build
from .fatigue_rotation import parameters, reserve_after
from .stats_ledger import write_csv


def test_observer_reconciles_and_preserves_hashes():
    build = match_build(13, roster='control')
    bare = build.create(record=False)
    watched = build.create(record=False)
    watched.enable_stats()
    bare.play(360)
    watched.play(360)
    a, b = bare.result(), watched.result()
    for key in ('trace_hash','state_hash','config_digest','score'):
        assert a[key]==b[key]
    box = b['box_score']
    assert len(box['players'])==44 and len(box['teams'])==2
    for row in box['players']:
        assert sum(row['stints_ms'])==row['live_ms']
        assert row['above_80pct_ms']<=row['live_ms']
        assert row['distance_m']>=0
    assert sum(r['points'] for r in box['teams'])==sum(a['score'].values())
    output=StringIO()
    write_csv(box,output)
    assert output.getvalue().count('TEAM TOTAL')==2


@pytest.mark.parametrize('profile,scale,minimum',[('R2',.5,0),('R3',.33,0),('R2M',.5,2),('R3M',.33,2)])
def test_rotation_variants_scale_only_drain_and_bench(profile,scale,minimum):
    base, variant=parameters(),parameters(profile)
    expected=base|{'sprint_drain':base['sprint_drain']*scale,
                   'bench_recovery':base['bench_recovery']*scale,
                   'min_complete_possessions':minimum}
    assert variant==expected
    for intensity in (0.,.5):
        assert reserve_after(.6,.7,intensity,60.,rate_scale=scale)==reserve_after(.6,.7,intensity,60.)


def test_minimum_stint_blocks_starter_return_and_fatigue_swap():
    base=match_build(1,roster='control')
    build=replace(base,config=replace(base.config,fatigue_rotation=True,rotation_rhythm='R2M'))
    port=build.create(record=False).port
    e=port.m.e
    starter=next(p for p in e.s.players.values() if p.active and p.team=='A' and p.role=='field')
    starter.fatigue=.6
    e.award('A',42.,50.,'after_score',fresh=True,normalize=False)
    port.rotation.rotate()
    assert not starter.active
    reserve=next(p for p in e.s.players.values() if p.active and p.team=='A' and p.slot==starter.slot)
    starter.fatigue=.75
    reserve.fatigue=.6
    e.s.now+=1000
    e.award('B',42.,50.,'after_score',fresh=True,normalize=False)
    port.rotation.rotate()
    assert reserve.active and not starter.active
    e.s.now+=1000
    e.award('A',42.,50.,'after_score',fresh=True,normalize=False)
    port.rotation.rotate()
    assert starter.active and not reserve.active
