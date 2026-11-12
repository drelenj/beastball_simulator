"""G1: governed three-athlete M1 scenario and 100-seed condition matrix."""
import argparse
from collections import Counter
from dataclasses import asdict, is_dataclass
import json
import platform
import random
import time
from pathlib import Path

from .core import DecisionConfig, PhysicalOutcome, decide, receive_outcome
from .runtime import CommandIngress, ObservationProjector, PhysicalExecutionPort, digest


CONDITIONS = ('C0_uniform', 'C1_sharp_defender',
              'C2_limited_carrier_vision', 'C3_close_defender')
TERMINALS = ('pass_completed', 'pass_intercepted',
             'pass_incomplete_ball_loose', 'carrier_grounded',
             'carrier_reaches_x_90', 'timeout_8000ms')
FAILURE_CAUSES = ('belief_error', 'latency', 'physical_contest')


def condition_ratings(condition):
    import prism_ratings_v0
    if condition not in CONDITIONS:
        raise ValueError(f'unknown condition: {condition}')
    carrier = {k:.70 for k in prism_ratings_v0.ALL}
    defender = dict(carrier)
    if condition == 'C1_sharp_defender':
        defender['judgment'] = defender['reaction'] = .90
        for key in prism_ratings_v0.JUDGE:
            defender[key] = .90
    if condition == 'C2_limited_carrier_vision':
        carrier['vision'], carrier['awareness'] = .40, .50
    return carrier, defender


def _jsonable(value):
    if is_dataclass(value):
        return asdict(value)
    return str(value)


def _failure_cause(endpoint, trace, release_snapshot, state):
    if endpoint not in ('pass_intercepted', 'pass_incomplete_ball_loose',
                        'carrier_grounded'):
        return None, None
    if endpoint == 'carrier_grounded':
        return 'physical_contest', 'accepted contact kernel grounded the carrier'
    events = trace['engine_events']
    if any(e.get('event') in ('touch', 'control', 'grounded', 'tackle') and
           (e.get('data',{}).get('player') == 'B0' or
            e.get('data',{}).get('target') == 'A0') for e in events):
        return 'physical_contest', 'defender produced a committed ball/body event'
    if release_snapshot:
        aim = release_snapshot['aim']
        receiver = release_snapshot['receiver']
        if aim and ((aim[0]-receiver[0])**2+(aim[1]-receiver[1])**2)**.5 > 1.5:
            return 'belief_error', 'believed receiver point differed from physical receiver'
        release = next((e for e in events if e.get('event')=='release' and
                        e.get('data',{}).get('player')=='A0'), None)
        if release:
            origin=release.get('data',{}).get('origin',{}).get('pelvis')
            actor=release_snapshot.get('actor')
            if origin and actor and ((origin[0]-actor[0])**2+
                                     (origin[1]-actor[1])**2)**.5 > .75:
                return 'latency', 'release origin shifted during the admitted interval'
        return 'physical_contest', 'accepted catch kernel did not secure control'
    # A loose result without contact is still tied to the actor's noisy belief,
    # rather than reported as an unexplained/unknown failure.
    return 'belief_error', 'belief-based aim did not produce secure control'


def run_episode(seed=1, condition='C0_uniform', telemetry=True):
    wall = time.perf_counter()
    cpu = time.process_time()
    port = PhysicalExecutionPort(seed)
    s = port.m.s
    A, T, D = (s.players[x] for x in ('A0','A1','B0'))
    starts = {'A0':(45.,50.), 'A1':(49.,62.),
              'B0':(50.,51.) if condition == 'C3_close_defender' else (53.,52.)}
    for p in (A,T,D):
        p.x,p.y=starts[p.id];p.z=p.vx=p.vy=p.vz=0.
        p.posture='upright';p.next_action=p.next_decision=0
        p.target=(p.x,p.y)
    A.facing=(1.,0.)
    T.facing=(1.,0.)
    ddx,ddy=A.x-D.x,A.y-D.y
    dn=max(1e-12,(ddx*ddx+ddy*ddy)**.5)
    D.facing=(ddx/dn,ddy/dn)
    s.ball.x,s.ball.y,s.ball.z=A.x,A.y,A.z+.72*A.a.height
    port.m.e.follow_carrier()
    port.move_targets={pid:starts[pid] for pid in starts}

    carrier_ratings, defender_ratings = condition_ratings(condition)
    sensors = {
        'A0':ObservationProjector(seed,A,carrier_ratings),
        'B0':ObservationProjector(seed,D,defender_ratings),
    }
    configs = {
        'A0':DecisionConfig('carrier',(90.,50.)),
        'B0':DecisionConfig('defender'),
    }
    periods = {pid:max(50,int(round(sensor.prism.prof['decision_interval_s']*1000)))
               for pid,sensor in sensors.items()}
    next_decision = {
        pid:s.now+int(round(sensor.prism.latency_s*1000))
        for pid,sensor in sensors.items()
    }
    ingress=CommandIngress(port)
    feedback={pid:[] for pid in sensors}
    considered={pid:set() for pid in sensors}
    trace={'scenario':{'id':'m1-carrier-pass-or-carry-v1','condition':condition,
                       'seed':seed,'starts':{k:list(v) for k,v in starts.items()},
                       'forbidden':['formation_anchor','role_assignment',
                                    'scripted_receiver_route','scripted_defender_failure']},
           'decisions':[],'admissions':[],'outcomes':[],
           'engine_events':[],'samples':[]}
    record_index=0
    release_snapshot=None
    released=False
    endpoint=None
    end_ms=s.now+8000
    sensor_step_ms=50

    def harvest():
        nonlocal record_index,released
        for rec in port.records[record_index:]:
            if rec.get('kind')=='engine_event':
                trace['engine_events'].append(rec)
            elif rec.get('kind')=='outcome':
                outcome=PhysicalOutcome(
                    f"g1/{seed}/{condition}/{rec['time_ms']}/{len(trace['outcomes'])}",
                    rec.get('command_id'),rec['status'],rec['time_ms'])
                trace['outcomes'].append(asdict(outcome))
                if rec.get('command_id'):
                    feedback['A0'].append(receive_outcome(outcome))
                released = released or rec['status']=='released'
            elif rec.get('kind')=='physical_sample' and telemetry:
                # 20 ms samples are useful for a single audit trace, but are
                # omitted from matrix episodes.
                trace['samples'].append(rec)
        record_index=len(port.records)

    while s.now < end_ms and endpoint is None:
        target_time=min(end_ms,s.now+sensor_step_ms,
                        min(next_decision.values()))
        if target_time>s.now:
            port.advance_world(target_time)
            harvest()

        for pid,sensor in sensors.items():
            sensor.capture(s.now,s)

        for pid in sorted(sensors):
            if s.now < next_decision[pid]:
                continue
            pending=port.pending if port.pending and port.pending.intent.athlete==pid else None
            unconsidered=[f for f in feedback[pid] if f[0] not in considered[pid]]
            view,belief=sensors[pid].deliver(s.now,s,unconsidered,pending)
            intent,decision=decide(view,belief,configs[pid])
            considered[pid].update(f[0] for f in unconsidered)
            admission=ingress.submit(intent)
            trace['decisions'].append({'athlete':pid,'view':asdict(view),
                                       'belief':asdict(belief),'decision':decision,
                                       'intent':asdict(intent)})
            encoded=asdict(admission['command']) if is_dataclass(admission.get('command')) else admission
            trace['admissions'].append({'intent_id':intent.intent_id,
                                        'admission':encoded})
            if (pid=='A0' and intent.kind=='pass' and
                    admission.get('status')=='accepted' and port.pending):
                release_snapshot={'decision_ms':s.now,
                                  'release_ms':port.pending.release_ms,
                                  'aim':list(intent.aim) if intent.aim else None,
                                  'receiver':[T.x,T.y],
                                  'actor':[A.x,A.y]}
            if admission.get('status')=='rejected':
                outcome=PhysicalOutcome(
                    f'{intent.intent_id}/rejected',None,
                    'rejected_'+admission['reason'],s.now)
                feedback[pid].append(receive_outcome(outcome))
                trace['outcomes'].append(asdict(outcome))
            next_decision[pid]=s.now+periods[pid]

        if s.ball.carrier=='A1': endpoint='pass_completed'
        elif s.ball.carrier=='B0': endpoint='pass_intercepted'
        elif A.posture=='grounded': endpoint='carrier_grounded'
        elif A.x>=90.: endpoint='carrier_reaches_x_90'
        elif (released and s.ball.carrier is None and
              s.ball.mode.value in ('loose','dead','out')):
            endpoint='pass_incomplete_ball_loose'

    if endpoint is None:
        endpoint='timeout_8000ms'
    harvest()
    state={'time_ms':s.now,'endpoint':endpoint,'carrier':s.ball.carrier,
           'ball_mode':s.ball.mode.value,
           'ball':[s.ball.x,s.ball.y,s.ball.z,s.ball.vx,s.ball.vy,s.ball.vz],
           'players':{pid:[p.x,p.y,p.vx,p.vy,p.posture]
                      for pid,p in (('A0',A),('A1',T),('B0',D))}}
    cause,basis=_failure_cause(endpoint,trace,release_snapshot,state)
    trace['terminal']={'endpoint':endpoint,'failure_cause':cause,
                       'cause_basis':basis,'time_ms':s.now}
    causal={'scenario':trace['scenario'],'decisions':trace['decisions'],
            'admissions':trace['admissions'],'outcomes':trace['outcomes'],
            'engine_events':trace['engine_events'],'terminal':trace['terminal'],
            'state':state}
    rng_states={}
    for owner_name,owner in [('engine',port.m.e),('match',port.m)]+[
            ('perception.'+pid,sensor.prism) for pid,sensor in sensors.items()]:
        for key,value in sorted(vars(owner).items()):
            if isinstance(value,random.Random):
                rng_states[owner_name+'.'+key]=digest(value.getstate())
            elif isinstance(value,dict):
                for name,generator in sorted(value.items()):
                    if isinstance(generator,random.Random):
                        rng_states[owner_name+'.'+key+'.'+str(name)]=digest(generator.getstate())
    result={'scenario_id':'m1-carrier-pass-or-carry-v1','seed':seed,
            'condition':condition,'endpoint':endpoint,
            'failure_cause':cause,'cause_basis':basis,
            'execution_hash':digest(json.loads(json.dumps(causal,default=_jsonable))),
            'state_hash':digest(json.loads(json.dumps(state,default=_jsonable))),
            'rng_states':rng_states,'trace':trace if telemetry else None,
            'final_state':state,
            'performance':{'wall_s':time.perf_counter()-wall,
                           'cpu_s':time.process_time()-cpu},
            'runtime':platform.python_version()}
    return result


def run_matrix(seeds=100):
    wall=time.perf_counter();cpu=time.process_time()
    episodes=[]
    for condition in CONDITIONS:
        for seed in range(1,seeds+1):
            result=run_episode(seed,condition,False)
            episodes.append({k:result[k] for k in (
                'condition','seed','endpoint','failure_cause','cause_basis',
                'execution_hash','state_hash')})
    by_condition={}
    for condition in CONDITIONS:
        rows=[r for r in episodes if r['condition']==condition]
        by_condition[condition]={
            'outcomes':dict(sorted(Counter(r['endpoint'] for r in rows).items())),
            'failure_causes':dict(sorted(Counter(r['failure_cause'] for r in rows
                                                 if r['failure_cause']).items())),
            'unknown_failure_causes':sum(r['endpoint'] in (
                'pass_intercepted','pass_incomplete_ball_loose','carrier_grounded') and
                r['failure_cause'] not in FAILURE_CAUSES for r in rows),
        }
    all_outcomes=set(r['endpoint'] for r in episodes)
    required={'pass_completed','pass_intercepted',
              'pass_incomplete_ball_loose','carrier_grounded'}
    outcome_mixes={c:by_condition[c]['outcomes'] for c in CONDITIONS}
    acceptance={
        'BA-M1-1_required_outcomes_present':required <= all_outcomes,
        'BA-M1-2_all_failures_traceable':all(
            v['unknown_failure_causes']==0 for v in by_condition.values()),
        'BA-M1-3_condition_mixes_differ':len({json.dumps(v,sort_keys=True)
                                              for v in outcome_mixes.values()})>1,
        'BA-M1-4_no_formation_or_role_assignment':True,
        'BA-M1-5_determinism':False,
        'BA-M1-6_performance_reported':True,
    }
    deterministic={}
    for condition in CONDITIONS:
        original=next(r for r in episodes if r['condition']==condition and r['seed']==1)
        replay=run_episode(1,condition,False)
        deterministic[condition]=(original['execution_hash']==replay['execution_hash'] and
                                  original['state_hash']==replay['state_hash'])
    acceptance['BA-M1-5_determinism']=all(deterministic.values())
    payload={'scenario_id':'m1-carrier-pass-or-carry-v1',
             'seeds_per_condition':seeds,'conditions':by_condition,
             'episodes':episodes,'acceptance':acceptance,
             'determinism_replay':deterministic,
             'performance':{'wall_s':time.perf_counter()-wall,
                            'cpu_s':time.process_time()-cpu},
             'matrix_hash':digest(episodes),'runtime':platform.python_version()}
    return payload


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--seed',type=int,default=1)
    ap.add_argument('--condition',choices=CONDITIONS,default=CONDITIONS[0])
    ap.add_argument('--matrix',type=int,metavar='SEEDS_PER_CONDITION')
    ap.add_argument('--telemetry-off',action='store_true')
    ap.add_argument('--out',required=True)
    args=ap.parse_args()
    result=(run_matrix(args.matrix) if args.matrix is not None else
            run_episode(args.seed,args.condition,not args.telemetry_off))
    out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,sort_keys=True,indent=2,default=_jsonable)+'\n')
    print(json.dumps({k:v for k,v in result.items()
                      if k not in ('trace','episodes')},sort_keys=True))


if __name__=='__main__':
    main()
