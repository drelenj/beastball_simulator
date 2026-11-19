"""Small deterministic RB/3 fixtures shared by conformance tests."""
from native.roster import RATINGS, load_rows

from .config import RulebookConfigV3
from .port import RulebookPort


def control_rosters():
    roles = ['field'] * 18 + ['keeper'] * 2 + ['archer'] * 2
    rows = []
    for n, role in enumerate(roles):
        row = {key: .7 for key in RATINGS}
        row.update(id=str(n), role=role, height_m=2.39, mass_kg=226.,
                   reach_m=3.05, acceleration=.7)
        rows.append(row)
    return {team: load_rows(rows, team) for team in ('A', 'B')}


def rb3_port(seed=1, rosters=None, **overrides):
    rosters = rosters or control_rosters()
    cfg = RulebookConfigV3(
        roster_digests=tuple(rosters[team].digest for team in ('A', 'B')),
        **overrides,
    )
    return RulebookPort(seed, cfg, rosters=rosters)
