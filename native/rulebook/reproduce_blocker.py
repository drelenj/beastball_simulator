"""Bounded regression for the former RB/native-v0 restart incompatibility."""
import argparse,json,tempfile
from pathlib import Path
from collections import Counter
from native.run import run_match
from .port import RulebookPort

def default_output():return Path(tempfile.gettempdir())/'beastball-rb-restart-blocker.json'

def reproduce(path=None):
 path=Path(path) if path else default_output()
 p=RulebookPort(1);e=p.m.e;s=p.m.s
 try:
  result,_=run_match(1,config=p.config,max_steps=4000,port_factory=lambda *a:p)
  report={'blocked':False,'status':result['status']}
 except RuntimeError as error:
  if not str(error).startswith('restart stall:'):raise
  report={'blocked':True,'error':str(error)}
 calls=e.rb.calls;discipline=[r for r in calls if r['kind']=='discipline']
 report.update(config_digest=p.config.digest,seed=1,max_steps=4000,full_match_attempt=False,live_ms=s.live_ms,physical_ms=s.now,
  events=dict(Counter(r['kind'] for r in calls)),fouls=dict(Counter(r['data'].get('reason') for r in e.log if r['event']=='foul')),
  event_table=dict(breaks=sum(r['kind']=='break' for r in calls),timeouts=sum(r['kind']=='timeout' for r in calls),minors=sum(r['kind_of_foul']=='minor' for r in discipline),majors=sum(r['kind_of_foul']=='major' for r in discipline),exclusions=sum(r['duration_ms']>0 for r in discipline),DQs=sum(r['dq'] for r in discipline),quota_resets=sum(r['kind']=='quota_reset' for r in calls),reviews=sum(r['kind']=='review' for r in calls),injuries=sum(r['kind'] in ('injury','head_evaluation') for r in calls),substitutions=sum(r['kind']=='substitution' for r in calls)),
  shot_bands={team:dict(bands) for team,bands in e.rb_bands.items()})
 report['advanced_past_former_blocker']=s.live_ms>5375
 if not report['blocked']:assert report['advanced_past_former_blocker']
 Path(path).parent.mkdir(parents=True,exist_ok=True);Path(path).write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
 print(json.dumps({k:v for k,v in report.items() if k!='error'},sort_keys=True))
 return report
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--out');args=ap.parse_args();reproduce(args.out)
