"""Standalone experimental replay retaining the normal Native match pipeline."""
import argparse
import json
from pathlib import Path

from native.individuation import VERSION
from native.nbl_roster import load_canon_nbl, load_nbl_workbook
from native.run import run_match

from .config import RulebookConfigV3
from .port import RulebookPort


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--compatibility', action='store_true')
    parser.add_argument('--rb324', action='store_true', help='replay the RB-3.24 experimental profile')
    parser.add_argument('--workbook', type=Path)
    parser.add_argument('--drill-values', type=Path)
    parser.add_argument('--fatigue-rotation', action='store_true')
    parser.add_argument('--technical', choices=('ovr', 'neutral', 'explicit'), default='ovr')
    parser.add_argument('--physical', choices=('roster', 'neutral'), default='roster')
    parser.add_argument('--home', default='Garvian Guardians')
    parser.add_argument('--away', default='Ala Apex')
    parser.add_argument('--seed', type=int, default=1)
    parser.add_argument('--max-steps', type=int)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    source = dict(technical=args.technical, physical=args.physical)
    teams = args.home, args.away
    if args.workbook:
        rosters = load_nbl_workbook(args.workbook, teams, **source)
    else:
        rosters = load_canon_nbl(teams, **source)
    cfg = RulebookConfigV3(roster_digests=tuple(rosters[t].digest for t in ('A', 'B')),
                          rb322_technical_source=args.technical, rb322_physical_source=args.physical,
                          fatigue_rotation=args.fatigue_rotation,
                          individuation='off' if args.compatibility else VERSION if args.rb324 else 'individuation/2')
    if args.drill_values:
        cfg = cfg.with_drill_values(args.drill_values)
    result, _ = run_match(args.seed, cfg, max_steps=args.max_steps, rosters=rosters,
                          port_factory=RulebookPort)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')


if __name__ == '__main__':
    main()
