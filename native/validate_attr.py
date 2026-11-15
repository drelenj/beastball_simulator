"""Budgeted ATTR-1 full-match validation."""
from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
import json
from pathlib import Path
import subprocess
import time
import traceback

from .config import AttrConfig,config_for
from .roster import load_csv
from .run import run_match

ROOT=Path(__file__).resolve().parent/'evidence'/'attr1'
BUDGET=ROOT/'FULL_MATCH_BUDGET.json'


def _load():
    rosters={team:load_csv(ROOT/'rosters'/f'team-{team}.csv',team) for team in ('A','B')}
    config=AttrConfig(roster_digests=tuple(rosters[t].digest for t in ('A','B')))
    return rosters,config


BASELINE_HASHES={
    'native-v0/2':('3840682e22692e597bc1419aa298337201e86db2d35f7208c5c9e50e9a99a142','411abb0a4bab0b812bc5e2e010f03d22f726ff32fdcebcb7df6c3a5beac8aec9'),
    'native-v0/3':('cacf24053a2fdfdcfecf64c376690651029c8094dd6488b864069b3c3baa74d2','d688fcbb46b20830bc2ecbda35486bbee5720b8b7cf911f3403f12a9f13d0012'),
}


def one(job):
    seed,label,version=job;started=time.perf_counter()
    try:
        if version=='attr-map/1':rosters,config=_load()
        else:rosters,config=None,config_for(version)
        result,port=run_match(seed,config,rosters=rosters)
        port.assert_invariants();engine=port.m.e
        assert result['status']=='final' and result['live_ms']>=2400000
        assert result['restart_completion_ratio']==1 and result['invariants']=='passed'
        assert not any(i.kind=='kick' for i in port.intents)
        intent_ids={i.intent_id for i in port.intents}
        assert all(c.intent.intent_id in intent_ids for c in port.command_log)
        if version in BASELINE_HASHES:
            assert seed==1 and (result['trace_hash'],result['state_hash'])==BASELINE_HASHES[version]
        events=Counter(row['event'] for row in engine.log)
        summary=dict(status='passed',seed=seed,label=label,config_digest=result['config_digest'],
                     roster_digests=dict(zip(('A','B'),config.roster_digests)) if version=='attr-map/1' else {},trace_hash=result['trace_hash'],
                     state_hash=result['state_hash'],runtime_s=round(time.perf_counter()-started,3),score=result['score'],
                     live_ms=result['live_ms'],restart_completion_ratio=result['restart_completion_ratio'],
                     events={key:events[key] for key in ('goal','foul','discipline','tackle_count','arrow_release','freeze','boundary','restart_awarded','restart_release','match_complete')},
                     decisions=result['decisions_total'],all_commands_have_intents=True,no_kicks=True)
        path=ROOT/f'{label}.json';path.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
        summary['evidence']=str(path)
        return summary
    except Exception as error:
        result=dict(status='failed',seed=seed,label=label,error=repr(error),traceback=traceback.format_exc(),runtime_s=round(time.perf_counter()-started,3))
        (ROOT/f'{label}-failure.json').write_text(json.dumps(result,indent=2)+'\n');return result


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--seeds',nargs='+',type=int,required=True)
    parser.add_argument('--label',required=True);parser.add_argument('--workers',type=int,default=1)
    parser.add_argument('--config-version',choices=('native-v0/2','native-v0/3','attr-map/1'),default='attr-map/1')
    args=parser.parse_args();budget=json.loads(BUDGET.read_text());source=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    assert len(budget['attempts'])+len(args.seeds)<=budget['cap']
    reserved=[];jobs=[]
    for index,seed in enumerate(args.seeds):
        label=f'{args.label}-seed{seed}-{index}';jobs.append((seed,label,args.config_version))
        row=dict(id=len(budget['attempts'])+1,profile=args.config_version,seed=seed,label=label,status='reserved',commit=source)
        budget['attempts'].append(row);reserved.append(row)
    BUDGET.write_text(json.dumps(budget,indent=2)+'\n')
    if args.workers==1:results=[one(job) for job in jobs]
    else:
        with ProcessPoolExecutor(args.workers) as pool:results=list(pool.map(one,jobs))
    for row,result in zip(reserved,results):row.update(result)
    BUDGET.write_text(json.dumps(budget,indent=2)+'\n')
    print(json.dumps({'results':results},sort_keys=True),flush=True)
    if any(r['status']!='passed' for r in results):raise SystemExit(1)


if __name__=='__main__':main()
