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


def reaction_deadline(now, previous, interval):
    """Keep the deliberate clock's phase across physics ticks.

    Restart the clock after a missed interval, for example after a freeze.
    """
    if previous is None or now - previous >= interval:
        return now + interval
    return previous + interval


class MatchDriver:
    """Resumable Native clock, with an optional caller-supplied decision observer."""

    def __init__(self, port):
        self.port = port
        self.next_dec = {}
        self.reaction_due = {}
        self.next_sense = self.steps = 0
        self.last_progress = self.last_live_ms = self.last_live_at = 0

    @property
    def final(self):
        return self.port.m.s.phase == self.port.types.Phase.FINAL

    def advance(self, select=None, *, prepared=None, progress=None):
        """Advance one tick. A prepared turn resumes after its view was delivered."""
        port = self.port
        m, s = port.m, port.m.s
        if self.final:
            raise ValueError('match is already final')
        if prepared is None and getattr(port, 'intermission_pending', False):
            port.advance_intermission()
            self.last_live_at = s.now
            return
        now = s.now
        if prepared is None:
            if now >= self.next_sense:
                port.capture(now)
                self.next_sense = now + port.config.sense_ms
            ids = port.active_ids()
        else:
            view, belief, remaining = prepared
            ids = (view.athlete, *remaining)
        next_dec, reaction_due = self.next_dec, self.reaction_due
        learned_values = getattr(port,'learned_values',None)
        for index, pid in enumerate(ids):
            if prepared is not None and index == 0:
                view, belief, _ = prepared
            else:
                if now < next_dec.get(pid, 0):
                    continue
                view, belief = port.view(pid, now)
                if view is None:
                    continue
            if select is None:
                if learned_values is None or not view.holds_ball:
                    intent, record = cognition.decide(view, belief)
                else:
                    intent, record = cognition.decide(view, belief, learned_values=learned_values)
            else:
                intent, record = select(view, belief, tuple(ids[index + 1:]))
            admission = port.submit(intent)
            if admission['status'] == 'rejected':
                port.feedback.setdefault(pid, []).append(
                    (intent.intent_id+'/rejected','rejected_'+admission.get('reason','unknown')+':'+intent.kind,now))
            if port.individuation:
                from .prism_registry import commit_owner
                parent = record.get('prism_agent', view.role)
                port.prism_agents[parent] += 1
                child = commit_owner(intent, core=port.prism_core)
                if child and (child != 'takedown' or view.own_hold_target is None) and admission['status'] == 'accepted':
                    port.prism_commits.append(dict(athlete=pid, action=intent.kind, parent=parent,
                                                  commit_ms=now, subagent=child, intent_id=intent.intent_id))
            if port.prism_core and child not in ('evasion', 'takedown'):
                reaction = dict(view.individual_ratings).get('reaction', .70)
                interval = port.config.decision_ms * (1 + .4 * (.70 - reaction))
                due = reaction_deadline(now, reaction_due.get(pid), interval)
                reaction_due[pid] = next_dec[pid] = due
            else:
                reaction_due.pop(pid, None)
                next_dec[pid] = now + port.prism_decision_interval_ms(pid, intent)
        m.pending_break = []
        port.step()
        self.steps += 1
        if progress and s.live_ms-self.last_progress >= 60000:
            self.last_progress = s.live_ms
            progress(dict(seed=port.seed, period=s.period, live_ms=s.live_ms,
                          now=s.now, steps=self.steps, score=dict(s.score)))
        if s.now <= now and not self.final:
            raise RuntimeError('clock stalled')
        if getattr(port, 'intermission_pending', False):
            self.last_live_at = s.now
        if s.live_ms > self.last_live_ms:
            self.last_live_ms, self.last_live_at = s.live_ms, s.now
        elif not self.final and s.now-self.last_live_at > port.config.dead_stall_limit_ms:
            raise RuntimeError('restart stall: '+json.dumps({
                'now':s.now,'live_ms':s.live_ms,'restart':asdict(s.restart) if s.restart else None,
                'record':getattr(s.restart,'native_id',None),
                'players':{p.id:{'x':p.x,'y':p.y,'target':p.target,'role':p.role,'posture':p.posture,
                                 'launch':getattr(p,'c4c_launch',None),
                                 'intent':getattr(getattr(p,'native_intent',None),'kind',None)}
                           for p in s.players.values() if p.active},
                'pending':{pid:pend['cmd'].intent.kind for pid,pend in port.pending.items()}},sort_keys=True))
        if s.now > 100000000:
            raise RuntimeError('unbounded match / sudden death: no artificial winner supplied')

    def play(self, max_steps=None, progress=None):
        while not self.final:
            self.advance(progress=progress)
            if max_steps and self.steps >= max_steps:
                break

    def result(self, runtime_s=0.):
        port, steps = self.port, self.steps
        seed = port.seed
        m = port.m
        s, e = m.s, m.e
        trace = port.trace.copy()
        if s.phase==port.types.Phase.FINAL:
            for rid,status in list(e.restart_results.items()):
                if status=='pending':e.restart_results[rid]='match_end'
        trace.update(digest([asdict(o) for o in port.outcomes]).encode())
        trace.update(digest(e.log).encode())
        state=dict(config_digest=port.behavior_digest,public_rules=asdict(e.possession.public()),restart_results=dict(e.restart_results),now=s.now,period=s.period,phase=s.phase.value,game_ms=s.game_ms,play_ms=s.possession_ms,
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
                    result=s.result,trace_hash=trace.hexdigest(),state_hash=digest(state),steps=steps,
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
                    runtime_s=round(runtime_s,3))
        if port.individuation:
            result['prism_agents'] = dict(port.prism_agents)
            result['prism_sources'] = port.prism_sources
            result['prism_commits'] = port.prism_commits
        return result


def run_match(seed=1,config=None,policies=None,plumbing=True,max_steps=None,progress=None,port_factory=None,rosters=None):
    started = time.perf_counter()
    factory = port_factory or NativePort
    port = factory(seed,config,policies,plumbing,rosters=rosters) if rosters is not None else factory(seed,config,policies,plumbing)
    driver = MatchDriver(port)
    driver.play(max_steps, progress)
    return driver.result(time.perf_counter()-started), port


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
