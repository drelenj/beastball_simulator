"""Bounded, stepped single-athlete B1 decision loop in an isolated worker."""
import argparse
from dataclasses import asdict, is_dataclass
import json
import platform
import time
from pathlib import Path
from .core import decide, PhysicalOutcome, receive_outcome
from .runtime import PhysicalExecutionPort, CommandIngress, ObservationProjector, digest


def run(seed=1, case='pass', telemetry=True):
    wall = time.perf_counter()
    cpu = time.process_time()
    port = PhysicalExecutionPort(seed)
    setup = time.perf_counter()-wall
    import prism_ratings_v0
    ratings = prism_ratings_v0.assign(port.roster_overrides,
                                      port.roster_names)['A0']
    athlete = port.m.s.players['A0']
    sensor = ObservationProjector(seed, athlete, ratings)
    if case == 'retain':
        defender = port.m.s.players['B0']
        defender.x, defender.y = 47., 50.8
    elif case not in ('pass','interrupted'):
        raise ValueError('unknown M1 case')

    # Scenario config applies to authoritative entities before observation.
    scenario = {'actor':'A0','teammate':'A1','defender':'B0',
                'positions':{p.id:[p.x,p.y,p.z] for p in (athlete,port.m.s.players['A1'],port.m.s.players['B0'])},
                'case':case}
    profile = sensor.prism.prof
    decision_period = max(100, int(round(profile['decision_interval_s']*1000)))
    next_decision = 1000 + int(round(sensor.prism.latency_s*1000))
    ingress = CommandIngress(port)
    decisions, admissions, outcomes = [], [], []
    feedback_pending, feedback_log = [], []
    released_command = None
    observed_contacts = set()

    def collect_physical_outcomes():
        nonlocal released_command
        for rec in port.records:
            if rec.get('kind') == 'outcome' and rec.get('status') == 'released':
                released_command = rec.get('command_id')
            if rec.get('kind') == 'outcome' and rec.get('command_id') and not any(o.command_id == rec['command_id'] for o in outcomes):
                outcome=PhysicalOutcome(f"m1/physics/{rec['time_ms']:020d}/A0/{len(outcomes):010d}/outcome",rec['command_id'],rec['status'],rec['time_ms'])
                outcomes.append(outcome)
                delivered=receive_outcome(outcome)
                feedback_pending.append(delivered); feedback_log.append(delivered)
            if rec.get('kind') == 'kernel_event' and released_command:
                for event in rec.get('events',()):
                    field=(lambda name,default=None: event.get(name,default) if isinstance(event,dict) else getattr(event,name,default))
                    actor=field('actor')
                    event_kind=field('kind')
                    key=(released_command,actor,event_kind)
                    if event_kind not in ('acquire','touch') or key in observed_contacts:
                        continue
                    observed_contacts.add(key)
                    status='caught' if rec.get('carrier') == actor else 'physical_contact'
                    outcome=PhysicalOutcome(f"m1/physics/{rec['time_ms']:020d}/{actor}/{len(outcomes):010d}/outcome",
                                            released_command,status,rec['time_ms'],actor)
                    outcomes.append(outcome)
                    # Contact at a remote receiver is a world event. It does not
                    # enter the thrower's private own-action feedback channel.
    start_ms, end_ms = 1000, 2400
    for now_ms in range(start_ms,end_ms+1,100):
        if now_ms > port.m.s.now:
            port.advance(now_ms)
            collect_physical_outcomes()
        sensor.capture(now_ms,port.m.s)
        if now_ms < next_decision:
            continue
        view,belief = sensor.deliver(now_ms,port.m.s,feedback_pending,port.pending)
        intent,decision = decide(view,belief)
        decisions.append({'view':view,'belief':belief,'decision':decision,'intent':intent})
        feedback_pending.clear()
        admission=ingress.submit_batch([intent])[0][1]
        admissions.append({'intent_id':intent.intent_id,'admission':admission})
        if admission.get('status') == 'accepted' and intent.kind == 'retain':
            retained=PhysicalOutcome(f'{intent.intent_id}/outcome/retained',None,'retained',now_ms)
            outcomes.append(retained)
            delivered=receive_outcome(retained)
            feedback_pending.append(delivered); feedback_log.append(delivered)
        if admission.get('status') == 'rejected':
            rejected=PhysicalOutcome(f"{intent.intent_id}/outcome/rejected",None,
                                     'rejected_'+admission['reason'],now_ms)
            outcomes.append(rejected)
            delivered=receive_outcome(rejected)
            feedback_pending.append(delivered); feedback_log.append(delivered)
        if case == 'interrupted' and admission.get('status') == 'accepted' and intent.kind == 'pass' and port.pending:
            athlete.freeze_until = port.pending.release_ms+1
            case = 'interrupted_pending'
        next_decision = now_ms+decision_period

    if port.m.s.now < end_ms:
        port.advance(end_ms)
    # Include final release/contact events in the athlete's own feedback.
    collect_physical_outcomes()
    state={'time_ms':port.m.s.now,'ball':vars(port.m.s.ball),
           'players':{pid:{'x':p.x,'y':p.y,'z':p.z,'vx':p.vx,'vy':p.vy,'active':p.active}
                      for pid,p in sorted(port.m.s.players.items()) if p.active}}
    import random
    rng_states={}
    for owner_name,owner in [('engine',port.m.e),('match',port.m),('perception',sensor.prism)]:
        for key,value in sorted(vars(owner).items()):
            if isinstance(value,random.Random): rng_states[owner_name+'.'+key]=digest(value.getstate())
            elif isinstance(value,dict):
                for name,generator in sorted(value.items()):
                    if isinstance(generator,random.Random): rng_states[owner_name+'.'+key+'.'+name]=digest(generator.getstate())
    encode=lambda o:asdict(o) if is_dataclass(o) else str(o)
    decision_times=[d['view'].delivered_ms for d in decisions]
    actual_period=(decision_times[1]-decision_times[0]) if len(decision_times)>1 else None
    causal=json.loads(json.dumps({'scenario':scenario,'timing':{'start_ms':start_ms,'end_ms':end_ms,
                              'sensor_ms':100,'nominal_decision_period_ms':decision_period,
                              'effective_decision_period_ms':actual_period,
                              'first_ready_ms':1000+int(round(sensor.prism.latency_s*1000)),
                              'first_decision_ms':decision_times[0] if decision_times else None,
                              'decision_times_ms':decision_times},
                              'decisions':decisions,'admissions':admissions,'events':port.records,
                              'outcomes':outcomes,'athlete_feedback':feedback_log},default=encode))
    return {'seed':seed,'case':scenario['case'],'execution_hash':digest(causal),
            'state_hash':digest(json.loads(json.dumps(state,default=encode))),
            'rng_states':rng_states,'trace':causal if telemetry else None,
            'decision_count':len(decisions),'performance':{'setup_wall_s':setup,
                'total_wall_s':time.perf_counter()-wall,'cpu_s':time.process_time()-cpu},
            'runtime':platform.python_version(),'status':'bounded_scenario_completed'}


if __name__ == '__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--seed',type=int,default=1)
    ap.add_argument('--case',choices=['pass','retain','interrupted'],default='pass')
    ap.add_argument('--out',required=True)
    ap.add_argument('--telemetry-off',action='store_true')
    a=ap.parse_args()
    result=run(a.seed,a.case,not a.telemetry_off)
    Path(a.out).parent.mkdir(parents=True,exist_ok=True)
    Path(a.out).write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='trace'},sort_keys=True))
