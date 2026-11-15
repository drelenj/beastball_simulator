"""One command: python -m native.run --seed 1 --out result.json"""
import argparse
from collections import Counter
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import time
from .port import NativePort, digest
from . import cognition


def run_match(seed=1,config=None,policies=None,plumbing=True,max_steps=None,progress=None,rosters=None):
    started=time.perf_counter();port=NativePort(seed,config,policies,plumbing,rosters)
    m,s,e=port.m,port.m.s,port.m.e
    next_dec={};next_sense=0;steps=0;last_progress=0;last_live_ms=0;last_live_at=0
    while s.phase!=port.types.Phase.FINAL:
        now=s.now
        if now>=next_sense:port.capture(now);next_sense=now+port.config.sense_ms
        for pid in port.active_ids():
            if now<next_dec.get(pid,0):continue
            view,belief=port.view(pid,now)
            if view is None:continue
            intent,record=cognition.decide(view,belief)
            admission=port.submit(intent)
            if admission['status']=='rejected':
                port.feedback.setdefault(pid,[]).append((intent.intent_id+'/rejected','rejected_'+admission.get('reason','unknown')+':'+intent.kind,now))
            next_dec[pid]=now+port.config.decision_ms
        m.pending_break=[] # breaks/timeouts deferred; no legacy intermission injection
        port.step();steps+=1
        if max_steps and steps>=max_steps:break
        if progress and s.live_ms-last_progress>=60000:
            last_progress=s.live_ms;progress(dict(seed=seed,period=s.period,live_ms=s.live_ms,now=s.now,steps=steps,score=dict(s.score)))
        if s.now-now<=0 and s.phase!=port.types.Phase.FINAL:raise RuntimeError('clock stalled')
        if s.live_ms>last_live_ms:last_live_ms=s.live_ms;last_live_at=s.now
        elif s.phase!=port.types.Phase.FINAL and s.now-last_live_at>port.config.dead_stall_limit_ms:
            raise RuntimeError('restart stall: '+json.dumps({'now':s.now,'live_ms':s.live_ms,'restart':asdict(s.restart) if s.restart else None,'record':getattr(s.restart,'native_id',None),'players':{p.id:{'x':p.x,'y':p.y,'target':p.target,'role':p.role,'posture':p.posture,'launch':getattr(p,'c4c_launch',None),'intent':getattr(getattr(p,'native_intent',None),'kind',None)} for p in s.players.values() if p.active},'pending':{pid:pend['cmd'].intent.kind for pid,pend in port.pending.items()}},sort_keys=True))
        if s.now>100000000:raise RuntimeError('unbounded match / sudden death: no artificial winner supplied')
    if s.phase==port.types.Phase.FINAL:
        for rid,status in list(e.restart_results.items()):
            if status=='pending':e.restart_results[rid]='match_end'
    port.trace.update(digest([asdict(o) for o in port.outcomes]).encode())
    port.trace.update(digest(e.log).encode())
    state=dict(config_digest=port.config.digest,public_rules=asdict(e.possession.public()),restart_results=dict(e.restart_results),now=s.now,period=s.period,phase=s.phase.value,game_ms=s.game_ms,play_ms=s.possession_ms,
               score=dict(s.score),ball=asdict(s.ball),players={p.id:asdict(p) for p in s.players.values()})
    # Dynamic instance attrs (motor commitments) have separate execution records;
    # canonical dataclass state excludes Python object addresses.
    pending=sum(v=='pending' for v in e.restart_results.values())
    if s.phase==port.types.Phase.FINAL and pending:
        for rid,status in list(e.restart_results.items()):
            if status=='pending':e.restart_results[rid]='match_end'
        pending=0
    released=sum(v=='released' for v in e.restart_results.values());total=len(e.restart_results)
    result=dict(seed=seed,status='final' if s.phase==port.types.Phase.FINAL else 'partial',config=port.config.record(),
                config_digest=port.config.digest,effective=port.verify_effective(),score=dict(s.score),period=s.period,
                result=s.result,trace_hash=port.trace.hexdigest(),state_hash=digest(state),steps=steps,
                live_ms=s.live_ms,end_ms=s.now,policy_params={t:p.as_dict() for t,p in port.policies.items()},
                outcomes_by_status=dict(Counter(o.status for o in port.outcomes)),
                rules={'ledger_by_row':dict(Counter(row['row'] for row in e.possession_history+e.possession.ledger))},
                decisions_total=len(port.intents),decisions_by_kind=dict(port.decisions),
                restart_awarded=total,restart_released=released,restart_closed=total-pending,
                restart_completion_ratio=(total-pending)/total if total else 1.,restart_release_ratio=released/total if total else 1.,
                restart_statuses=dict(Counter(e.restart_results.values())),invariants='passed',
                restart_metric=port.restart_metric.summary(e.restart_results),contact_intents=dict(Counter(i.contact for i in port.intents if i.contact)),
                foul_reasons=dict(Counter(row['data'].get('reason') for row in e.log if row['event']=='foul')),
                engine_events=dict(Counter(row['event'] for row in e.log)),team_stats={t:dict(c) for t,c in e.native_stats.items()},
                release_distances={t:{str(d):{'attempts':n,'goals':e.release_successes[t].get(d,0),'success_rate':e.release_successes[t].get(d,0)/n} for d,n in e.release_attempts[t].items()} for t in ('A','B')},
                rules_ledger=dict(Counter(row['row'] for row in e.possession_history+e.possession.ledger)),
                runtime_s=round(time.perf_counter()-started,3))
    return result,port


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--seed',type=int,default=1);ap.add_argument('--out');ap.add_argument('--max-steps',type=int);ap.add_argument('--progress',action='store_true');ap.add_argument('--plumbing-absent',action='store_true')
    ap.add_argument('--config-version',default='native-v0/2',choices=('native-v0/2','native-v0/3','attr-map/1'));ap.add_argument('--arrow-speed-ratio',type=float)
    ap.add_argument('--roster-a');ap.add_argument('--roster-b')
    a=ap.parse_args()
    config=None
    rosters=None
    if a.config_version=='attr-map/1':
        if not a.roster_a or not a.roster_b:ap.error('attr-map/1 requires --roster-a and --roster-b')
        from .roster import load_csv
        rosters={t:load_csv(path,t) for t,path in (('A',a.roster_a),('B',a.roster_b))}
        from .config import AttrConfig
        config=AttrConfig(roster_digests=tuple(rosters[t].digest for t in ('A','B')))
    elif a.config_version!='native-v0/2' or a.arrow_speed_ratio is not None:
        from .config import config_for
        config=config_for(a.config_version,**({'arrow_speed_ratio':a.arrow_speed_ratio} if a.arrow_speed_ratio is not None else {}))
    r,_=run_match(a.seed,config,plumbing=not a.plumbing_absent,max_steps=a.max_steps,rosters=rosters,
                  progress=(lambda row:print(json.dumps(row),flush=True)) if a.progress else None)
    if a.out:Path(a.out).parent.mkdir(parents=True,exist_ok=True);Path(a.out).write_text(json.dumps(r,indent=2,sort_keys=True)+'\n')
    print(json.dumps(r,sort_keys=True))

if __name__=='__main__':main()
