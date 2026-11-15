"""Bounded RB replay check; never starts a full match."""
import json,multiprocessing
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from .run import run_match

def window(plumbing=True):
 r,_=run_match(1,max_steps=100,plumbing=plumbing)
 return {k:r[k] for k in ('status','seed','live_ms','trace_hash','state_hash','config_digest')}

def main():
 serial=window()
 with ProcessPoolExecutor(2,mp_context=multiprocessing.get_context('spawn')) as pool:
  parallel=list(pool.map(window,[True,True]))
 absent=window(False)
 assert serial==parallel[0]==parallel[1]==absent
 result=dict(status='passed',scope='100 physical steps only; not full-match V2',serial=serial,parallel=parallel,plumbing_absent=absent,full_matches=0)
 Path('native/rulebook/evidence/short-replay.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
 print(json.dumps(result))
if __name__=='__main__':main()
