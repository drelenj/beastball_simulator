"""RB-1 driver and report. Full matches must be accounted before execution."""
import argparse,json
from collections import Counter
from dataclasses import asdict
from pathlib import Path
from native.run import run_match as native_run
from native.port import digest
from .port import RulebookPort
from .config import RulebookConfig

def run_match(seed=1,config=None,max_steps=None,progress=None,plumbing=True):
 r,p=native_run(seed,config or RulebookConfig(),plumbing=plumbing,max_steps=max_steps,progress=progress,port_factory=RulebookPort)
 e=p.m.e
 state=asdict(e.rb);state['timeout_triggers']=sorted(e.rb.timeout_triggers);state['injuries']=sorted(e.rb.injuries)
 bands={t:{b:{'attempts':e.rb_bands[t][b+'_attempts'],'goals':e.rb_bands[t][b+'_goals'],'success_rate':e.rb_bands[t][b+'_goals']/max(1,e.rb_bands[t][b+'_attempts'])} for b in ('under10','10_to20','20plus','carry','own')} for t in ('A','B')}
 counts=dict(Counter(x['kind'] for x in e.rb.calls))
 r['rulebook']=dict(authorities=state,events=counts,bands=bands,attempts=e.rb_attempts,remaining_slots=e.rb_slots,equipment='PLACEHOLDER cylinder torso/thigh panels; lighter Archer kit has no gameplay effect')
 r['trace_hash']=digest([r['trace_hash'],e.rb.calls,e.rb_attempts])
 r['state_hash']=digest([r['state_hash'],state,e.rb_slots,e.rb_pause,[(q.id,getattr(q,'rb_recover',None)) for q in p.m.s.players.values()]])
 return r,p

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--seed',type=int,default=1);ap.add_argument('--banded',action='store_true');ap.add_argument('--max-steps',type=int);ap.add_argument('--out',required=True)
 a=ap.parse_args();cfg=RulebookConfig(scoring='banded' if a.banded else 'flat')
 r,_=run_match(a.seed,cfg,a.max_steps,progress=lambda x:print(json.dumps(x),flush=True))
 Path(a.out).parent.mkdir(parents=True,exist_ok=True);Path(a.out).write_text(json.dumps(r,indent=2,sort_keys=True)+'\n');print(json.dumps({k:r[k] for k in ('status','trace_hash','state_hash','live_ms')},sort_keys=True))
if __name__=='__main__':main()
