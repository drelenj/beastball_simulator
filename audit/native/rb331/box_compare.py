"""Apply the new observer to the archived seed-1 trajectory for an exact comparison."""
import argparse
import importlib
import json
from pathlib import Path
import subprocess

from audit.native.rb330.check import assert_identity, load
from .benchmark import PARENT
from .match import match

ARCHIVE = Path('audit/native/rb330/evidence')
FIELDS = ('targets','drops','balls_secured','flight_balls_secured','receptions','interceptions','loose_ball_recoveries')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workbook', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    module = importlib.import_module('native.rulebook.planned_rotation')
    src = subprocess.check_output(['git','show',f'{PARENT}:native/rulebook/planned_rotation.py'])
    exec(compile(src,f'{PARENT}:planned_rotation.py','exec'),module.__dict__)
    row, new = match(args.workbook, 'PLANNED', 0, 1, diagnostics=False)
    assert_identity(row,load(ARCHIVE / 'runs/0-1.json.gz'))
    old = load(ARCHIVE / 'boxes/planned-seed01.json')
    reports = []
    for previous, player in zip(old['players'],new['players'],strict=True):
        assert player['player']==previous['player']
        assert player['balls_secured']==player['receptions']+player['interceptions']+player['loose_ball_recoveries']
        assert player['flight_balls_secured']==previous['catches']
        assert player['targets']==previous['targets']
        assert player['drops']<=previous['drops']
        assert player['receptions']+player['drops']<=player['targets']
        reports.append(dict(player=player['player'],name=player['player_name'],team=player['team'],
                            before={k:previous[k] for k in ('targets','catches','drops','interceptions')},
                            after={k:player[k] for k in FIELDS}))
    args.out.write_text(json.dumps(dict(match={k:row[k] for k in ('score','trace_hash','state_hash','config_digest')},
                                      players=reports),indent=2,ensure_ascii=False)+'\n')
    print('Parent seed-1 hashes and flight-only catch totals reproduced for all 44 named players.',flush=True)


if __name__=='__main__':
    main()
