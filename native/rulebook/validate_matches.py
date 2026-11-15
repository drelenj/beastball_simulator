"""Budgeted full-match validation; workers return summaries, not live engine objects."""
import argparse,json,time,subprocess,traceback
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
from collections import Counter
from .run import run_match

EVIDENCE=Path(__file__).with_name('evidence')

def match(job):
 seed,label=job;start=time.perf_counter()
 try:
  r,p=run_match(seed,progress=lambda row:print(json.dumps(dict(validation=label,**row)),flush=True))
  p.assert_invariants();e=p.m.e
  assert r['status']=='final' and r['live_ms']>=2400000
  ids={i.intent_id for i in p.intents}
  assert all(c.intent.intent_id in ids for c in p.command_log)
  assert not any(i.kind=='kick' for i in p.intents)
  assert not any('kick' in str(row.get('data',{}).get('kind','')) for row in e.log if row['event'] in ('release','restart_release'))
  assert r['restart_completion_ratio']==1 and r['invariants']=='passed'
  calls=e.rb.calls;d=[x for x in calls if x['kind']=='discipline'];counts=Counter(x['kind'] for x in calls)
  r['validation']=dict(status='passed',label=label,all_commands_have_intents=True,no_kicks=True,
   events=dict(breaks=counts['break'],timeouts=counts['timeout'],minors=sum(x['kind_of_foul']=='minor' for x in d),majors=sum(x['kind_of_foul']=='major' for x in d),exclusions=sum(x['duration_ms']>0 for x in d),DQs=sum(x['dq'] for x in d),quota_resets=counts['quota_reset'],reviews=counts['review'],injuries=counts['injury']+counts['head_evaluation'],substitutions=counts['substitution']))
  path=EVIDENCE/f'full-{label}.json';path.write_text(json.dumps(r,indent=2,sort_keys=True)+'\n')
  return dict(status='passed',seed=seed,label=label,trace_hash=r['trace_hash'],state_hash=r['state_hash'],config_digest=r['config_digest'],runtime_s=round(time.perf_counter()-start,3),live_ms=r['live_ms'],score=r['score'],restart_completion_ratio=r['restart_completion_ratio'],events=r['validation']['events'],bands=r['rulebook']['bands'],evidence=str(path.relative_to(EVIDENCE.parent.parent.parent)))
 except Exception as error:
  result=dict(status='failed',seed=seed,label=label,error=repr(error),traceback=traceback.format_exc(),runtime_s=round(time.perf_counter()-start,3))
  (EVIDENCE/f'full-{label}-failure.json').write_text(json.dumps(result,indent=2)+'\n');return result

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--seeds',type=int,nargs='+',required=True);parser.add_argument('--label',required=True);parser.add_argument('--workers',type=int,default=1);parser.add_argument('--serial-replay',action='store_true')
 a=parser.parse_args();path=EVIDENCE/'FULL_MATCH_BUDGET.json';budget=json.loads(path.read_text())
 replay_seed=a.seeds[0]
 seeds=([replay_seed] if a.serial_replay else [])+a.seeds
 assert len(budget['attempts'])+len(seeds)<=budget['cap']
 source=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();jobs=[];rows=[]
 for n,seed in enumerate(seeds):
  label=f'{a.label}-seed{seed}-{n}';jobs.append((seed,label));row=dict(id=len(budget['attempts'])+1,profile='native-rb/1',seed=seed,label=label,purpose='RB functional validation',status='reserved',commit=source);budget['attempts'].append(row);rows.append(row)
 path.write_text(json.dumps(budget,indent=2)+'\n')
 if a.workers==1:results=[match(job) for job in jobs]
 else:
  with ProcessPoolExecutor(a.workers) as pool:
   if a.serial_replay:
    futures=[pool.submit(match,job) for job in jobs[1:]]
    results=[match(jobs[0])]+[f.result() for f in futures]
   else:results=list(pool.map(match,jobs))
 for row,result in zip(rows,results):row.update(result)
 path.write_text(json.dumps(budget,indent=2)+'\n')
 print(json.dumps(dict(validation_results=results),sort_keys=True),flush=True)
 if any(r['status']!='passed' for r in results):raise SystemExit(1)
 if a.serial_replay:
  replay=next(r for r in results[1:] if r['seed']==replay_seed)
  assert (results[0]['trace_hash'],results[0]['state_hash'])==(replay['trace_hash'],replay['state_hash'])
  print(json.dumps(dict(serial_parallel_replay='passed',seed=replay_seed)),flush=True)
if __name__=='__main__':main()
