"""Ratings 0.4 rotation and possession evidence, compact per match."""
import argparse
from collections import Counter
import gzip
import json
from pathlib import Path
from time import process_time

from audit.native.rb327.match import PAIRS as RB327_PAIRS
from native.nbl_roster import load_nbl_workbook
from native.oracle.snapshot import Build
from native.rulebook.config import RulebookConfigV3
from native.rulebook.fatigue_rotation import PLANNED_RATE_SCALE, RHYTHMS
from native.rulebook.stats_ledger import write_csv
from .witness import TrialWitness
from audit.native.rb331.events import analyze
from audit.native.rb331.summarize import diagnose
from audit.native.rb330.check import load, assert_identity


TRIAL_SCALE = .58
FIXES = ('pass_clearance','carry_finish','fresh_takedown','boundary_guard')
ARMS = {'off': (), **{name:(name,) for name in FIXES}, 'combined': FIXES, 'archive': ()}

PAIRS = (RB327_PAIRS[0], ('Yukïma Cowhands','Isu’Kari Sirenwings'),
         ('Mbuya Ïmu Moonhawks','Ala Apex'), *RB327_PAIRS[1:])


def match(book, variant, pair, seed, steps=None, stats=True, scale=TRIAL_SCALE, diagnostics=True, arm='off'):
    teams=PAIRS[pair]
    rosters=load_nbl_workbook(book,teams,technical='explicit')
    cfg=RulebookConfigV3(roster_digests=tuple(rosters[t].digest for t in 'AB'),
                        rb322_technical_source='explicit',individuation='individuation/2',
                        fatigue_rotation=True,rotation_rhythm=variant,planned_rate_scale=scale,
                        **{'rb332_'+flag:True for flag in ARMS[arm]})
    start=process_time()
    driver=Build(seed,cfg,rosters).create(record=False)
    if stats:
        driver.enable_stats()
    witness = TrialWitness(driver.port, rosters, arm in ('off','archive')) if stats and diagnostics else None
    driver.play(steps)
    result=driver.result()
    cpu=process_time()-start
    box=result.get('box_score')
    row={key:result[key] for key in ('score','config_digest','trace_hash','state_hash','status',
                                    'restart_completion_ratio','invariants','live_ms','steps','team_stats')}
    row.update(seed=seed,variant=variant,pair=pair,teams=teams,arm=arm,
               planned_rate_scale=scale if variant == 'PLANNED' else None, cpu_s=cpu,
               cpu_ms_per_step=cpu*1000/result['steps'])
    if box:
        row.update(possessions=box['possessions'], scores=box['scores'])
        row['team_lines']=box['teams']
        row['rotations']=result['fatigue_substitutions']
        row['plan']=result.get('rotation_plan')
        means={}
        for t in 'AB':
            rank={pid:overall for pid,_,overall in rosters[t].rotation_candidates}
            starters=[rank[p['player'].split(':',1)[1]]
                      for p in box['players'] if p['team']==t and p['starter']]
            means[t]=sum(starters)/len(starters)
        row['starter_ovr']=means
        row['participation']=[{key:p[key] for key in ('player','team','role','starter','live_ms','regulation_ms','stints_ms')}
                              for p in box['players']]
    if witness is not None:
        diagnostic = analyze(witness, box)
        row['diagnosis'] = diagnostic
        if arm == 'archive':
            archived = load(Path(f'audit/native/rb331/evidence/runs/{pair}-{seed}.json.gz'))
            assert_identity(row, archived)
            flags=[]
            for r in diagnostic['interceptions']:
                if not r['restart'] and r.get('believed_margin',-1)>=0>r.get('true_margin',0):
                    flags.append({key:r.get(key) for key in ('release_id','origin','player','believed_margin','true_margin','arrival_margin')})
            row = {k:row[k] for k in ('pair','seed','score','trace_hash','state_hash','config_digest')} | dict(flags=flags)
        else:
            if arm == 'off':
                row['boundary'],row['keeper_reach'] = witness.detail(diagnostic['shots'])
            if steps is None:
                row['measures'] = diagnose([row])
                row['measures']['carries']['stretch_ends'] = Counter(
                    r.get('reason') or 'unspecified' for r in diagnostic['stretches'] if r['event']=='stretch_end')
                row.pop('diagnosis')
                row.pop('possessions')
                row.pop('scores')
    return row,box


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workbook',type=Path,required=True)
    parser.add_argument('--variant',choices=(*RHYTHMS,'PLANNED'),default='PLANNED')
    parser.add_argument('--pair',type=int,choices=range(len(PAIRS)),default=0)
    parser.add_argument('--seed',type=int,required=True)
    parser.add_argument('--steps',type=int)
    parser.add_argument('--scale',type=float)
    parser.add_argument('--arm',choices=ARMS,default='off')
    parser.add_argument('--no-diagnosis',action='store_true')
    parser.add_argument('--stats-off',action='store_true')
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--box',type=Path)
    args=parser.parse_args()
    scale = args.scale if args.scale is not None else PLANNED_RATE_SCALE if args.arm=='archive' else TRIAL_SCALE
    row,box=match(args.workbook,args.variant,args.pair,args.seed,args.steps,not args.stats_off,scale,not args.no_diagnosis,args.arm)
    data=json.dumps(row,separators=(',',':'),ensure_ascii=False).encode()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    scratch=args.out.with_suffix('.tmp')
    scratch.write_bytes(gzip.compress(data,mtime=0) if args.out.suffix=='.gz' else data+b'\n')
    if args.box:
        args.box.parent.mkdir(parents=True,exist_ok=True)
        args.box.with_suffix('.json').write_text(json.dumps(box,indent=2,ensure_ascii=False)+'\n')
        with args.box.with_suffix('.csv').open('w',newline='') as stream:
            write_csv(box,stream)
    scratch.replace(args.out)
    print(args.out,row['score'],row.get('steps'),row.get('cpu_ms_per_step'),flush=True)


if __name__=='__main__':
    main()
