"""RB-3.22: ACCEPTED RB-3.21 baseline as the RB/3 default; roster talent source option (diagnosis only)."""
import io, subprocess
import pytest
from native.nbl_roster import (load_nbl_workbook, load_canon_nbl, PHYSICAL, TECHNICAL_OVR, NEUTRAL_TECHNICAL)
from native.roster import RosterError
from .config import RulebookConfigV3
from .test_rb33 import control_rosters

TEAMS = ('Garvian Guardians', 'Ala Apex')
BODY = ('height_m', 'mass_kg', 'reach_m', 'standing_reach_m')


def digests():
    return tuple(control_rosters()[t].digest for t in ('A', 'B'))


def test_everything_is_on_by_default_and_each_flag_switches_off():
    c = RulebookConfigV3(roster_digests=digests())
    assert (c.rb3_carrier_moves_enabled, c.rb3_handoff_block_enabled, c.rb319_ball_in_play_enabled,
            c.rb320_exact_bounce, c.rb321_ball_material_enabled, c.carry_release_radius_m) == (True, True, True, True, True, 3.0)
    rec = c.record()
    for k in ('rb3_carrier_moves_enabled', 'rb3_handoff_block_enabled', 'rb319_ball_in_play_enabled', 'rb320_exact_bounce',
              'rb321_ball_material_enabled', 'carry_release_radius_m'):
        assert k in rec
    assert 'rb322_technical_source' not in rec and 'rb322_physical_source' not in rec       # defaults leave the record as RB-3.21's
    # the RB-3.21 soak gate ran with exactly these overrides on the old defaults: the effective record is the same
    gate = RulebookConfigV3(roster_digests=digests(), rb3_carrier_moves_enabled=True, rb3_handoff_block_enabled=True, rb319_ball_in_play_enabled=True)
    assert gate.digest == c.digest
    off = RulebookConfigV3(roster_digests=digests(), rb3_carrier_moves_enabled=False, rb3_handoff_block_enabled=False,
                           rb319_ball_in_play_enabled=False, rb320_exact_bounce=False, rb321_ball_material_enabled=False, carry_release_radius_m=0.)
    assert not any(k in off.record() for k in ('rb3_carrier_moves_enabled', 'rb3_handoff_block_enabled', 'rb319_ball_in_play_enabled',
                                                'rb320_exact_bounce', 'rb321_ball_material_enabled', 'carry_release_radius_m'))


def test_talent_source_values_are_validated_and_recorded_when_not_default():
    with pytest.raises(ValueError):
        RulebookConfigV3(roster_digests=digests(), rb322_technical_source='skill')
    rec = RulebookConfigV3(roster_digests=digests(), rb322_technical_source='neutral', rb322_physical_source='neutral').record()
    assert rec['rb322_technical_source'] == 'neutral' and rec['rb322_physical_source'] == 'neutral'
    with pytest.raises(RosterError):
        load_canon_nbl(TEAMS, technical='skill')


def _workbook():
    path = 'audit/arcade/morphology/NBL_2026-27_Opening_Night_Rosters_CANON_OVR_morphology_physical.xlsx'
    return subprocess.check_output(['git', 'show', '81f92e3:' + path])


def _league_means(blob):
    from openpyxl import load_workbook
    sheet = load_workbook(io.BytesIO(blob), read_only=True, data_only=True)['All 712 Players']; lines = sheet.values
    cols = {n: i for i, n in enumerate(next(lines))}
    vals = {k: [] for k in PHYSICAL}
    for line in lines:
        if line[cols['Player ID']] is None: continue
        for k, h in PHYSICAL.items(): vals[k].append(float(line[cols[h]]) / 100.)
    return {k: sum(v) / len(v) for k, v in vals.items()}, len(vals['speed'])


def test_neutral_modes_set_the_values_exactly_and_keep_players_and_bodies():
    pytest.importorskip('openpyxl')
    blob = _workbook()
    base = load_nbl_workbook(io.BytesIO(blob), TEAMS)
    tech = load_nbl_workbook(io.BytesIO(blob), TEAMS, technical='neutral')
    phys = load_nbl_workbook(io.BytesIO(blob), TEAMS, physical='neutral')
    means, n = _league_means(blob)
    assert n == 712
    for side in ('A', 'B'):
        ids = [a.source_id for a in base[side].athletes]
        assert [a.source_id for a in tech[side].athletes] == ids == [a.source_id for a in phys[side].athletes]   # same starters (by OVR)
        for b0, bt, bp in zip(base[side].athletes, tech[side].athletes, phys[side].athletes):
            for k in TECHNICAL_OVR:
                assert bt.get(k) == NEUTRAL_TECHNICAL and bp.get(k) == b0.get(k)
            for k in PHYSICAL:
                assert bp.get(k) == pytest.approx(means[k], abs=1e-12) and bt.get(k) == b0.get(k)
            for k in BODY:
                assert bt.get(k) == b0.get(k) == bp.get(k)
            assert bp.get('contact_resistance') == bp.get('balance')
        assert tech[side].digest != base[side].digest and phys[side].digest != base[side].digest
    assert len({round(a.get('ball_handling'), 6) for a in base['A'].athletes}) > 1                # control: OVR varies by player


def test_talent_source_loading_is_deterministic():
    pytest.importorskip('openpyxl')
    a = load_canon_nbl(TEAMS, technical='neutral', physical='neutral'); b = load_canon_nbl(TEAMS, technical='neutral', physical='neutral')
    assert a['A'].digest == b['A'].digest and a['B'].digest == b['B'].digest
    assert load_canon_nbl(TEAMS)['A'].digest == load_nbl_workbook(io.BytesIO(_workbook()), TEAMS)['A'].digest


GATE = ('44399b0853ac8a4a87ac7e7c336bd4932219b7969630838c616d6cc458fbc072', '046ea55bb1756364ecfdf0f91576ed16cb4052259b7284883e519c61c5f6865d')
RB316 = ('93b1f57e268ee6c436fae47109e4e2987cfdf7024df5575b6405e119c5ed32d7', 'b9962ddfb23dbc96551258ea6c2132565804d22ec1b0c87295e3f3ff37d59854')


def _real_seed1(**overrides):
    from native.run import run_match
    from .port import RulebookPort
    rosters = load_canon_nbl(TEAMS)
    cfg = RulebookConfigV3(tackles_per_possession=2,
                           roster_digests=tuple(rosters[t].digest for t in ('A', 'B')), **overrides)
    r, _ = run_match(1, cfg, max_steps=200000, rosters=rosters, port_factory=RulebookPort)
    return r['trace_hash'], r['state_hash']


def test_real_seed_1_with_recorded_tackle_limit_reproduces_the_rb321_soak_gate():
    pytest.importorskip('openpyxl')
    assert _real_seed1() == GATE


def test_all_off_by_explicit_overrides_reproduces_rb316():
    pytest.importorskip('openpyxl')
    assert _real_seed1(rb3_carrier_moves_enabled=False, rb3_handoff_block_enabled=False, rb319_ball_in_play_enabled=False,
                       rb320_exact_bounce=False, rb321_ball_material_enabled=False, carry_release_radius_m=0.) == RB316
