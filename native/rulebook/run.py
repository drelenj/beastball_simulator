"""RB-1 driver and report. Full matches must be accounted before execution."""
import argparse,json
from collections import Counter
from dataclasses import asdict
from pathlib import Path
from native.run import run_match as native_run
from native.port import digest
from .port import RulebookPort
from .config import RulebookConfig,RulebookConfigV3

def scoring_report(e,cfg):
 band_points={'under10':cfg.release_bands[0][1],'10_to20':cfg.release_bands[1][1],'20plus':cfg.release_bands[2][1]}
 shot_bands={}
 carries={}
 own_goals={}
 for team in ('A','B'):
  shot_bands[team]={}
  for band,value in band_points.items():
   attempts=e.rb_bands[team][band+'_attempts'];goals=e.rb_bands[team][band+'_goals'];points=goals*value
   shot_bands[team][band]=dict(attempts=attempts,goals=goals,points=points,success_rate=goals/attempts if attempts else 0.,points_per_attempt=points/attempts if attempts else 0.)
  attempts=e.rb_bands[team]['carry_attempts'];goals=e.rb_bands[team]['carry_goals'];points=goals*cfg.carry_points
  carries[team]=dict(attempts=attempts,goals=goals,points=points,success_rate=goals/attempts if attempts else 0.,points_per_attempt=points/attempts if attempts else 0.)
  goals=e.rb_bands[team]['own_goals'];own_goals[team]=dict(goals=goals,points=goals*cfg.own_goal_points)
 return shot_bands,carries,own_goals

def run_match(seed=1,config=None,max_steps=None,progress=None,plumbing=True,policies=None,rosters=None):
 r,p=native_run(seed,config or RulebookConfig(),policies=policies,plumbing=plumbing,max_steps=max_steps,progress=progress,port_factory=RulebookPort,rosters=rosters)
 e=p.m.e
 state=asdict(e.rb);state['timeout_triggers']=sorted(e.rb.timeout_triggers);state['injuries']=sorted(e.rb.injuries)
 shot_bands,carries,own_goals=scoring_report(e,p.config)
 counts=dict(Counter(x['kind'] for x in e.rb.calls))
 basis=dict(mode='banded',carry=p.config.carry_points,throws={'under10':p.config.release_bands[0][1],'10_to20':p.config.release_bands[1][1],'20plus':p.config.release_bands[2][1]},half_goal=1,full_goal_award=p.config.full_award_points,own_goal=p.config.own_goal_points,provisional=True)
 r['rulebook']=dict(scoring_basis=basis,authorities=state,events=counts,shot_bands=shot_bands,carry_attempts=carries,own_goals=own_goals,release_ledger=e.rb_attempts,remaining_slots=e.rb_slots,equipment='PLACEHOLDER cylinder torso/thigh panels; lighter Archer kit has no gameplay effect')
 r['trace_hash']=digest([r['trace_hash'],e.rb.calls,e.rb_attempts])
 state_for_hash=state
 if p.config.version=='native-rb/3':
  state_for_hash=dict(state,config=dict(state['config'],roster_digests=('behavior-only','behavior-only')))
 r['state_hash']=digest([r['state_hash'],state_for_hash,e.rb_slots,e.rb_pause,[(q.id,getattr(q,'rb_recover',None)) for q in p.m.s.players.values()]])
 return r,p

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--seed',type=int,default=1);ap.add_argument('--max-steps',type=int);ap.add_argument('--out',required=True)
 ap.add_argument('--nbl-a');ap.add_argument('--nbl-b')
 a=ap.parse_args()
 if bool(a.nbl_a)!=bool(a.nbl_b):ap.error('both --nbl-a and --nbl-b are required together')
 rosters=None;config=RulebookConfig()
 if a.nbl_a:
  from native.nbl_roster import load_canon_nbl
  rosters=load_canon_nbl((a.nbl_a,a.nbl_b))
  config=RulebookConfigV3(roster_digests=tuple(rosters[t].digest for t in ('A','B')))
 r,_=run_match(a.seed,config,a.max_steps,progress=lambda x:print(json.dumps(x),flush=True),rosters=rosters)
 Path(a.out).parent.mkdir(parents=True,exist_ok=True);Path(a.out).write_text(json.dumps(r,indent=2,sort_keys=True)+'\n');print(json.dumps({k:r[k] for k in ('status','trace_hash','state_hash','live_ms')},sort_keys=True))
if __name__=='__main__':main()
