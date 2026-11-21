"""Draft workbook fields do not replace the current gameplay ratings."""
import io

import pytest

from native.nbl_roster import STAGED_HEADERS, load_nbl_workbook
from native.roster import RosterError
from native.run import run_match

from .config import RulebookConfigV3
from .port import RulebookPort
from .test_rb322 import TEAMS, _workbook


def _with_ratings(value):
    openpyxl = pytest.importorskip('openpyxl')
    workbook = openpyxl.load_workbook(io.BytesIO(_workbook()))
    sheet = workbook['All 712 Players']
    first = sheet.max_column + 1
    for column, label in enumerate(STAGED_HEADERS.values(), start=first):
        sheet.cell(1, column, label)
        for row in range(2, sheet.max_row + 1):
            sheet.cell(row, column, value)
    edited = io.BytesIO()
    workbook.save(edited)
    edited.seek(0)
    return edited


def _config(rosters, **kwargs):
    return RulebookConfigV3(roster_digests=tuple(rosters[t].digest for t in ('A', 'B')), **kwargs)


def test_optional_columns_are_stored_with_ovr_fallback_and_do_not_change_gameplay():
    pytest.importorskip('openpyxl')
    baseline = load_nbl_workbook(io.BytesIO(_workbook()), TEAMS)
    staged = load_nbl_workbook(_with_ratings(93), TEAMS)
    for side in baseline:
        for old, new in zip(baseline[side].athletes, staged[side].athletes, strict=True):
            assert set(old.staged_rating_defaults) == set(STAGED_HEADERS)
            assert all(v == old.get('tackling') for _, v in old.staged_ratings)
            assert dict(new.staged_ratings) == dict.fromkeys(STAGED_HEADERS, .93)
            assert not new.staged_rating_defaults
            assert old.record() == new.record()
        assert baseline[side].digest == staged[side].digest
    results = [run_match(1, _config(r), max_steps=300, rosters=r, port_factory=RulebookPort)[0]
               for r in (baseline, staged)]
    for key in ('trace_hash', 'state_hash', 'config_digest'):
        assert results[0][key] == results[1][key]


def test_optional_column_uses_workbook_row_and_label_in_validation_error():
    with pytest.raises(RosterError, match=r'row \d+ column Tackling: rating 101'):
        load_nbl_workbook(_with_ratings(101), TEAMS)


def test_throw_power_flag_supplies_raw_engine_input_without_changing_the_existing_cap():
    pytest.importorskip('openpyxl')
    rosters = load_nbl_workbook(io.BytesIO(_workbook()), TEAMS)
    off = RulebookPort(1, _config(rosters), rosters=rosters)
    on = RulebookPort(1, _config(rosters, rb3_stage_throw_power=True), rosters=rosters)
    assert 'rb3_stage_throw_power' not in off.config.record()
    assert on.config.record()['rb3_stage_throw_power'] is True
    raw = {f'{t}:{a.source_id}': a.get('throw_power')
           for t, roster in rosters.items() for a in roster.athletes}
    for player_id, p in off.m.s.players.items():
        q = on.m.s.players[player_id]
        assert not hasattr(p.a, 'raw_throw_power')
        assert q.a.raw_throw_power == raw[player_id]
        assert p.native_max_throw_speed == q.native_max_throw_speed
        assert p.a.finishing == p.a.long_shot == q.a.finishing == q.a.long_shot == 0.
