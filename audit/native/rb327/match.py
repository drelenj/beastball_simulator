"""Measure a full or bounded RB-3.27 match using the ordinary match driver."""
import argparse
from dataclasses import replace
from hashlib import sha256
import json
from pathlib import Path
from time import process_time

from native.nbl_roster import load_nbl_workbook
from native.oracle.matches import match_build
from native.oracle.snapshot import Build
from native.rulebook.config import RulebookConfigV3
from native.rulebook.rb31_soak import measure

PAIRS = (
    ('Garvian Guardians','Ala Apex'),
    ('Ala Marauders','Kasuf Bloodravens'),
    ('Dōmyu Dominators','Güunlekia Serpents'),
    ('Hina’sola Hunters','Isu’Kari Sirenwings'),
    ('Kalundu Shockwave','Khemara Sunscourge'),
    ('Ndomiri Sentinels','Zafiren Tidewings'),
)


def real_build(seed, pair, workbook):
    roster = load_nbl_workbook(workbook, PAIRS[pair], technical='explicit')
    config = RulebookConfigV3(roster_digests=tuple(roster[t].digest for t in ('A','B')),
                              individuation='individuation/2', rb322_technical_source='explicit')
    return Build(seed,config,roster)


def execute(build, steps=None):
    start = process_time()
    driver = build.create(record=False)
    port = driver.port
    attempts = []
    original = port.m.e.rb_carry_attempt

    def observed(holder,*args,**kwargs):
        result = original(holder,*args,**kwargs)
        if result:
            attempts.append((port.m.s.now,holder.team))
        return result

    port.m.e.rb_carry_attempt = observed
    driver.play(steps)
    result = driver.result()
    result['cpu_ms_per_step'] = (process_time()-start)*1000/result['steps']
    result.pop('prism_commits',None)
    result.update(measure(port,attempts))
    result['selected'] = {t:[{'id':a.source_id,'role':a.role} for a in r.athletes]
                          for t,r in build.rosters.items()}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seed',type=int,required=True)
    parser.add_argument('--pair',type=int,choices=range(len(PAIRS)),default=0)
    parser.add_argument('--workbook',type=Path)
    parser.add_argument('--roster',choices=('neutral-real','control','real'),default='neutral-real')
    parser.add_argument('--steps',type=int)
    parser.add_argument('--values',type=Path)
    parser.add_argument('--out',type=Path,required=True)
    args = parser.parse_args()
    build = real_build(args.seed,args.pair,args.workbook) if args.workbook else match_build(args.seed,roster=args.roster)
    if args.values:
        build = replace(build,config=build.config.with_drill_values(args.values))
    result = execute(build,args.steps)
    if args.workbook:
        result['teams'] = PAIRS[args.pair]
        result['workbook_sha256'] = sha256(args.workbook.read_bytes()).hexdigest()
    args.out.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')


if __name__ == '__main__':
    main()
