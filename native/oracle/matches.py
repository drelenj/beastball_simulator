"""Pinned roster build recipes for replay and drill."""
from native.nbl_roster import load_canon_nbl
from native.prism_lab import neutral_rosters, TEAMS
from native.rulebook.config import RulebookConfigV3

from .snapshot import Build


def match_build(seed, mode='core', roster=None):
    source = roster or ('neutral-real' if mode == 'core' else 'real')
    rosters = load_canon_nbl(TEAMS) if source == 'real' else neutral_rosters(source == 'neutral-real')
    config = RulebookConfigV3(
        tackles_per_possession=2,
        roster_digests=tuple(rosters[team].digest for team in ('A', 'B')),
        individuation='individuation/2' if mode == 'core' else 'off',
    )
    return Build(seed, config, rosters)
