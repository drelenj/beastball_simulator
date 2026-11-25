from collections import Counter
from dataclasses import replace
from types import SimpleNamespace

import pytest

from native.oracle.matches import match_build
from .fatigue_rotation import GROUP
from .planned_rotation import resting_wave, split_waves
from .tackle_stats import TackleWitness


def planned_port():
    base = match_build(1, roster='control')
    return replace(base, config=replace(base.config, fatigue_rotation=True,
                                       rotation_rhythm='PLANNED')).create(record=False).port


def restart(port, live_ms=None):
    e = port.m.e
    if live_ms is not None:
        e.s.live_ms = live_ms
    e.s.now += 1000
    e.award('A', 42., 50., 'after_score', fresh=True, normalize=False)
    port.rotation.rotate()
    return e.s


def test_uneven_groups_are_balanced_and_wave_backups_are_unique():
    positions = ('PDR', 'STR', 'SCT', 'PFD', 'HNT', 'TRK', 'SEN', 'PFD', 'TRP', 'GRD')
    roster = {str(i): (pos, .8) for i, pos in enumerate(positions)}
    waves = split_waves([SimpleNamespace(id=pid) for pid in roster], roster)
    assert list(map(len, waves)) == [5, 5]
    counts = [Counter(GROUP[roster[p.id][0]] for p in wave) for wave in waves]
    assert all(abs(counts[0][group] - counts[1][group]) <= 1 for group in GROUP.values())
    plan = planned_port().rotation
    for waves in plan.waves.values():
        assert len(set(waves[0] + waves[1])) == 10
        for wave in waves:
            assert len({plan.backups[pid][0] for pid in wave}) == 5


@pytest.mark.parametrize('minute,period,expected', [
    (0, 1, None), (5, 1, None), (6, 1, 0), (9, 1, 0),
    (10, 2, 1), (13, 2, 1), (14, 2, None), (19, 2, None),
    (20, 3, None), (26, 3, 0), (29, 3, 0),
    (30, 4, 1), (33, 4, 1), (34, 4, None), (39, 4, None), (40, 5, None),
])
def test_live_windows_and_period_boundaries(minute, period, expected):
    assert resting_wave(minute * 60_000, 600_000, period) == expected


def test_planned_swaps_at_dead_ball_and_starters_restore_before_second_wave():
    port = planned_port()
    plan = port.rotation
    wave1, wave2 = plan.waves['A']
    s = port.m.s
    s.phase = port.types.Phase.LIVE
    s.live_ms = 360_000
    plan.rotate()
    assert all(s.players[pid].active for pid in wave1 + wave2)
    restart(port)
    assert all(not s.players[pid].active and s.players[plan.backups[pid][0]].active for pid in wave1)
    assert all(s.players[pid].active for pid in wave2)
    restart(port, 600_000)
    assert all(s.players[pid].active for pid in wave1)
    assert all(not s.players[pid].active and s.players[plan.backups[pid][0]].active for pid in wave2)
    restart(port, 840_000)
    assert all(s.players[pid].active for pid in wave1 + wave2)
    assert sum(p.team == 'A' and p.active and p.role != 'archer' for p in s.players.values()) == 12


def test_override_returns_only_when_recovered_and_scheduled():
    port = planned_port()
    s = port.m.s
    pid = port.rotation.waves['A'][0][0]
    player = s.players[pid]
    player.fatigue = .60
    restart(port, 350_000)
    assert not player.active and pid in port.rotation.override_benched
    player.fatigue = .74
    restart(port, 359_000)
    assert not player.active
    player.fatigue = .75
    restart(port, 360_000)
    assert not player.active
    restart(port, 600_000)
    assert player.active and pid not in port.rotation.override_benched
    reasons = {row['data']['reason'] for row in port.m.e.log if row['event'] == 'fatigue_substitution'}
    assert {'energy_override', 'override_return', 'planned_out'} <= reasons


def test_keeper_floor_archer_and_overtime_override():
    port = planned_port()
    s = port.m.s
    keeper = next(p for p in s.players.values() if p.team == 'A' and p.active and p.role == 'keeper')
    archer = next(p for p in s.players.values() if p.team == 'A' and p.active and p.role == 'archer')
    keeper.fatigue = archer.fatigue = .60
    plan = port.rotation
    plan.regulation_ms[keeper.id] = 36 * 60_000 - 1
    restart(port, 40 * 60_000)
    assert keeper.active and archer.active
    assert all(s.players[pid].active for wave in plan.waves['A'] for pid in wave)
    plan.regulation_ms[keeper.id] += 1
    restart(port)
    assert not keeper.active and archer.active


def test_tackle_counts_a_committed_hold_once_and_only_credits_its_grounding():
    player = SimpleNamespace(id='D', native_intent=SimpleNamespace(contact='takedown'))
    carrier = SimpleNamespace(id='C')
    match = SimpleNamespace(c3_contain=lambda *_: False, c3_holds={}, s=SimpleNamespace(now=100))
    watch = TackleWitness(match)
    match.c3_contain(player, carrier)  # A decision with no contact.
    match.c3_holds['D','C'] = {'start': 110.}
    for _ in range(3):
        assert not match.c3_contain(player, carrier)
    match.c3_holds['D','C'] = {'start': 150.}
    match.c3_contain(player, carrier)  # A trial hold never committed.
    match.c3_holds['D','C'] = {'start': 160.}
    player.native_intent.contact = 'wrap'
    match.c3_contain(player, carrier)
    def row(event, at, **data):
        return dict(event=event, t_ms=at, data=dict(actor='D', target='C', **data))
    events = [
        row('c3_hold_start', 110, start_ms=110.), row('c3_hold_end', 131, start_ms=110., end_ms=130.2, cause='carrier_grounded'),
        row('c3_hold_start', 160, start_ms=160.), row('tackle_count', 200),
    ]
    assert list(watch.totals(events)) == [('D', False)]
    events[1:1] = [row('tackle_count', 131)]
    assert list(watch.totals(events)) == [('D', True)]


def test_display_metadata_reaches_json_and_csv():
    from native.rulebook.stats_ledger import StatsLedger, write_csv
    from io import StringIO

    port = planned_port()
    athlete = next(iter(port.m.s.players.values()))
    key = athlete.id.split(':', 1)[1]
    port.roster_display[athlete.team] = ('Named franchise', ((key, 'Player Name', 'PDR'),))
    ledger = StatsLedger(port)
    record = ledger.players[athlete.id].record()
    assert (record['player_name'], record['legacy_position'], record['team_name']) == ('Player Name', 'PDR', 'Named franchise')
    buffer = StringIO()
    write_csv(dict(players=[record], unattributed=[], teams=[]), buffer)
    assert 'Player Name' in buffer.getvalue()
