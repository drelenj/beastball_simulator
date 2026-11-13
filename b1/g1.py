"""G1: governed three-athlete M1 scenario and 100-seed condition matrix."""
import argparse
from collections import Counter
from dataclasses import asdict, is_dataclass
import json
import math
import platform
import random
import time
from pathlib import Path

from .core import DecisionConfig, PhysicalOutcome, decide, receive_outcome
from .runtime import CommandIngress, ObservationProjector, PhysicalExecutionPort, digest


CONDITIONS = ('C0_uniform', 'C1_sharp_defender',
              'C2_limited_vision_carrier', 'C3_close_defender',
              'C4_lane_defender', 'C5_lane_defender_sharp')
TERMINALS = ('pass_completed', 'pass_intercepted',
             'pass_incomplete_ball_loose', 'carrier_grounded',
             'carrier_reaches_x_90', 'timeout_8000ms')
FAILURE_CAUSES = ('defender_ball_contact', 'defender_body_contact',
                  'receiver_catch_failure',
                  'belief_aim_error', 'pass_accuracy_failure', 'unknown')


def condition_ratings(condition):
    import prism_ratings_v0
    if condition not in CONDITIONS:
        raise ValueError(f'unknown condition: {condition}')
    carrier = {k:.70 for k in prism_ratings_v0.ALL}
    defender = dict(carrier)
    if condition in ('C1_sharp_defender','C5_lane_defender_sharp'):
        defender['judgment'] = defender['reaction'] = .90
    if condition == 'C2_limited_vision_carrier':
        carrier['vision'], carrier['awareness'] = .40, .50
    return carrier, defender


def _jsonable(value):
    if is_dataclass(value):
        return asdict(value)
    return str(value)


def _failure_cause(endpoint, evidence):
    """Classify only from recorded physical evidence; unknown is admissible."""
    if endpoint not in ('pass_intercepted', 'pass_incomplete_ball_loose',
                        'carrier_grounded'):
        return None, None
    if endpoint == 'carrier_grounded':
        if evidence.get('carrier_grounded_event') and evidence.get('defender_hold'):
            return 'defender_body_contact', 'committed defender hold preceded carrier grounding'
        return 'unknown', 'carrier grounded without a recorded defender causal chain'
    if endpoint == 'pass_intercepted':
        if evidence.get('defender_control'):
            return 'defender_ball_contact', 'authoritative control event awarded B0 the ball'
        return 'unknown', 'interception endpoint lacks a recorded defender control event'
    if evidence.get('defender_touch'):
        return 'defender_ball_contact', 'authoritative B0 touch occurred during the pass'
    if evidence.get('receiver_touch'):
        return 'receiver_catch_failure', 'A1 touched but did not secure the pass'
    near=evidence.get('min_receiver_ball_3d_m')
    if near is not None and near <= evidence.get('receiver_reach_threshold_m',0.):
        return 'receiver_catch_failure', 'ball entered A1 reach envelope without secure control'
    if evidence.get('aim_receiver_error_m') is not None and evidence['aim_receiver_error_m']>1.5:
        return 'belief_aim_error', 'admitted belief aim was more than 1.5 m from A1'
    cross_track=evidence.get('release_cross_track_error_at_aim_m')
    if (cross_track is not None and
            cross_track>evidence.get('receiver_reach_threshold_m',0.)):
        return 'pass_accuracy_failure', (
            'sampled release direction missed the semantic aim reach envelope '
            f'by {cross_track:.3f} m cross-track')
    return 'unknown', 'recorded evidence does not establish a failure cause'


def _point_segment_distance(point, start, end):
    px,py=point; ax,ay=start; bx,by=end
    dx,dy=bx-ax,by-ay
    length2=dx*dx+dy*dy
    if length2<=1e-12:
        return math.hypot(px-ax,py-ay)
    u=max(0.,min(1.,((px-ax)*dx+(py-ay)*dy)/length2))
    return math.hypot(px-(ax+u*dx),py-(ay+u*dy))


def _direction_evidence(origin, aim, velocity):
    if not origin or not aim or not velocity:
        return None,None
    tx,ty=aim[0]-origin[0],aim[1]-origin[1]
    vx,vy=velocity[:2]
    tl,vl=math.hypot(tx,ty),math.hypot(vx,vy)
    if tl<=1e-12 or vl<=1e-12:
        return None,None
    cosine=max(-1.,min(1.,(tx*vx+ty*vy)/(tl*vl)))
    angle=math.degrees(math.acos(cosine))
    cross_track=abs(tx*vy-ty*vx)/vl
    return angle,cross_track


def run_episode(seed=1, condition='C0_uniform', telemetry=True):
    wall = time.perf_counter()
    cpu = time.process_time()
    port = PhysicalExecutionPort(seed)
    s = port.m.s
    A, T, D = (s.players[x] for x in ('A0','A1','B0'))
    defender_start=((50.,51.) if condition=='C3_close_defender' else
                    (47.,56.) if condition in ('C4_lane_defender',
                                                'C5_lane_defender_sharp') else
                    (53.,52.))
    starts = {'A0':(45.,50.), 'A1':(49.,62.), 'B0':defender_start}
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
        'A0':DecisionConfig('carrier',(90.,50.),1.2,1.5),
        'B0':DecisionConfig('defender',None,1.2,0.,
                            defender_ratings['judgment'],
                            condition in ('C4_lane_defender',
                                          'C5_lane_defender_sharp')),
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
    trace={'scenario':{'id':'m1-carrier-pass-or-carry-v2','condition':condition,
                       'seed':seed,'starts':{k:list(v) for k,v in starts.items()},
                       'forbidden':['formation_anchor','role_assignment',
                                    'scripted_receiver_route','scripted_defender_failure']},
           'decisions':[],'admissions':[],'outcomes':[],
           'engine_events':[],'samples':[],
           'flight_evidence':{
               'receiver_touch':False,'defender_touch':False,
               'defender_control':False,'defender_hold':False,
               'carrier_grounded_event':False,
               'min_receiver_ball_3d_m':None,
               'min_defender_ball_3d_m':None,
               'receiver_reach_threshold_m':T.a.reach+T.radius+.2,
               'aim_receiver_error_m':None,
               'release_direction_error_deg':None,
               'release_cross_track_error_at_aim_m':None,
               'release_origin_shift_m':None,
               'moving_release_recomputed':False,
               'correction_angle_deg':None},
           'mechanism_evidence':{
               'defender_decisions_before_release':0,
               'defender_lane_decisions_before_release':0,
               'defender_lane_option_selected_before_release':False,
               'defender_distance_to_pass_lane_at_release_m':None}}
    record_index=0
    release_snapshot=None
    released=False
    endpoint=None
    end_ms=s.now+8000
    sensor_step_ms=50
    previous_relative={}

    def harvest():
        nonlocal record_index,released
        evidence=trace['flight_evidence']
        for rec in port.records[record_index:]:
            if rec.get('kind')=='engine_event':
                trace['engine_events'].append(rec)
                event,data=rec.get('event'),rec.get('data',{})
                if event=='touch' and data.get('player')=='A1': evidence['receiver_touch']=True
                if event=='touch' and data.get('player')=='B0': evidence['defender_touch']=True
                if event=='control' and data.get('player')=='B0': evidence['defender_control']=True
                if event=='c3_hold_start' and data.get('actor')=='B0' and data.get('target')=='A0': evidence['defender_hold']=True
                if event in ('grounded','c3_grounding') and data.get('player')=='A0':
                    evidence['carrier_grounded_event']=True
            elif rec.get('kind')=='outcome':
                outcome=PhysicalOutcome(
                    f"g1/{seed}/{condition}/{rec['time_ms']}/{len(trace['outcomes'])}",
                    rec.get('command_id'),rec['status'],rec['time_ms'])
                encoded_outcome=asdict(outcome)
                for key in ('action_kind','target','release_origin','semantic_aim',
                            'moving_release_recomputed','correction_angle_deg',
                            'correction_bound_deg','admitted_speed_mps',
                            'admitted_horizontal_speed_mps','final_ball_velocity'):
                    if key in rec:
                        encoded_outcome[key]=rec[key]
                trace['outcomes'].append(encoded_outcome)
                if rec.get('command_id'):
                    feedback['A0'].append(receive_outcome(outcome))
                released = released or rec['status']=='released'
                if rec['status']=='released':
                    evidence['moving_release_recomputed']=bool(rec.get('moving_release_recomputed'))
                    evidence['correction_angle_deg']=rec.get('correction_angle_deg')
                    angle,cross_track=_direction_evidence(
                        rec.get('release_origin'),rec.get('semantic_aim'),
                        rec.get('final_ball_velocity'))
                    evidence['release_direction_error_deg']=angle
                    evidence['release_cross_track_error_at_aim_m']=cross_track
                    if rec.get('release_origin') and rec.get('semantic_aim'):
                        trace['mechanism_evidence'][
                            'defender_distance_to_pass_lane_at_release_m']=(
                                _point_segment_distance((D.x,D.y),
                                    rec['release_origin'],rec['semantic_aim']))
                    if release_snapshot and rec.get('release_origin'):
                        ox,oy=rec['release_origin'];ax,ay=release_snapshot['actor']
                        evidence['release_origin_shift_m']=((ox-ax)**2+(oy-ay)**2)**.5
            elif rec.get('kind')=='physical_sample':
                if released and rec.get('players'):
                    bx,by,bz=rec['ball']
                    for pid,key,player in (('A1','min_receiver_ball_3d_m',T),
                                           ('B0','min_defender_ball_3d_m',D)):
                        px,py=rec['players'][pid][:2]
                        rel=(bx-px,by-py,bz-player.hand_height)
                        prior_rel=previous_relative.get(pid)
                        if prior_rel is None:
                            dist=sum(v*v for v in rel)**.5
                        else:
                            delta=tuple(rel[i]-prior_rel[i] for i in range(3))
                            denom=sum(v*v for v in delta)
                            u=(max(0.,min(1.,-sum(prior_rel[i]*delta[i]
                                                 for i in range(3))/denom))
                               if denom>1e-12 else 0.)
                            dist=sum((prior_rel[i]+u*delta[i])**2 for i in range(3))**.5
                        previous_relative[pid]=rel
                        prior=evidence[key]
                        evidence[key]=dist if prior is None else min(prior,dist)
                if telemetry:
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
            if pid=='B0' and not released:
                mechanism=trace['mechanism_evidence']
                mechanism['defender_decisions_before_release']+=1
                if intent.target and intent.target.startswith('lane:'):
                    mechanism['defender_lane_decisions_before_release']+=1
                    mechanism['defender_lane_option_selected_before_release']=True
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
                trace['flight_evidence']['aim_receiver_error_m']=(
                    ((intent.aim[0]-T.x)**2+(intent.aim[1]-T.y)**2)**.5
                    if intent.aim else None)
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
    cause,basis=_failure_cause(endpoint,trace['flight_evidence'])
    trace['terminal']={'endpoint':endpoint,'failure_cause':cause,
                       'cause_basis':basis,'time_ms':s.now}
    causal={'scenario':trace['scenario'],'decisions':trace['decisions'],
            'admissions':trace['admissions'],'outcomes':trace['outcomes'],
            'engine_events':trace['engine_events'],
            'flight_evidence':trace['flight_evidence'],
            'terminal':trace['terminal'],
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
    result={'scenario_id':'m1-carrier-pass-or-carry-v2','seed':seed,
            'condition':condition,'endpoint':endpoint,
            'failure_cause':cause,'cause_basis':basis,
            'execution_hash':digest(json.loads(json.dumps(causal,default=_jsonable))),
            'state_hash':digest(json.loads(json.dumps(state,default=_jsonable))),
            'rng_states':rng_states,'trace':trace if telemetry else None,
            'mechanism_evidence':trace['mechanism_evidence'],
            'final_state':state,
            'performance':{'wall_s':time.perf_counter()-wall,
                           'cpu_s':time.process_time()-cpu},
            'runtime':platform.python_version()}
    return result


def _lane_comparison(episodes):
    names=('C4_lane_defender','C5_lane_defender_sharp')
    rows_by={name:[r for r in episodes if r['condition']==name]
             for name in names}
    mechanism={}
    for name,rows in rows_by.items():
        selected=[r for r in rows if r['mechanism_evidence'][
            'defender_lane_option_selected_before_release']]
        release_distances=[r['mechanism_evidence'][
            'defender_distance_to_pass_lane_at_release_m'] for r in rows
            if r['mechanism_evidence'][
                'defender_distance_to_pass_lane_at_release_m'] is not None]
        selected_distances=[r['mechanism_evidence'][
            'defender_distance_to_pass_lane_at_release_m'] for r in selected
            if r['mechanism_evidence'][
                'defender_distance_to_pass_lane_at_release_m'] is not None]
        intercepted=sum(r['endpoint']=='pass_intercepted' for r in selected)
        mechanism[name]={
            'seed_count':len(rows),
            'lane_option_seed_count':len(selected),
            'lane_option_seed_fraction':len(selected)/len(rows) if rows else 0.,
            'release_lane_distance_sample_count':len(release_distances),
            'mean_defender_distance_to_pass_lane_at_release_m':(
                sum(release_distances)/len(release_distances)
                if release_distances else None),
            'lane_selected_release_distance_sample_count':len(selected_distances),
            'mean_defender_distance_to_pass_lane_when_lane_selected_m':(
                sum(selected_distances)/len(selected_distances)
                if selected_distances else None),
            'interceptions_with_lane_option':intercepted,
            'interception_rate_conditional_on_lane_option':(
                intercepted/len(selected) if selected else None)}
    c4_by={r['seed']:r for r in rows_by[names[0]]}
    c5_by={r['seed']:r for r in rows_by[names[1]]}
    common=sorted(set(c4_by)&set(c5_by))
    endpoint_differences=sum(c4_by[s]['endpoint']!=c5_by[s]['endpoint']
                             for s in common)
    interceptions_gained=sum(c4_by[s]['endpoint']!='pass_intercepted' and
                             c5_by[s]['endpoint']=='pass_intercepted'
                             for s in common)
    interceptions_lost=sum(c4_by[s]['endpoint']=='pass_intercepted' and
                           c5_by[s]['endpoint']!='pass_intercepted'
                           for s in common)
    both_selected=[s for s in common if
                   c4_by[s]['mechanism_evidence'][
                       'defender_lane_option_selected_before_release'] and
                   c5_by[s]['mechanism_evidence'][
                       'defender_lane_option_selected_before_release']]
    matched_c4_interceptions=sum(c4_by[s]['endpoint']=='pass_intercepted'
                                 for s in both_selected)
    matched_c5_interceptions=sum(c5_by[s]['endpoint']=='pass_intercepted'
                                 for s in both_selected)
    matched_gained=sum(c4_by[s]['endpoint']!='pass_intercepted' and
                       c5_by[s]['endpoint']=='pass_intercepted'
                       for s in both_selected)
    matched_lost=sum(c4_by[s]['endpoint']=='pass_intercepted' and
                     c5_by[s]['endpoint']!='pass_intercepted'
                     for s in both_selected)
    discordant=matched_gained+matched_lost
    tail=min(matched_gained,matched_lost)
    mcnemar_p=(min(1.,2*sum(math.comb(discordant,i)
                           for i in range(tail+1))/(2**discordant))
               if discordant else 1.)
    distance_deltas=[]
    selected_distance_deltas=[]
    for seed in common:
        r4,r5=c4_by[seed],c5_by[seed]
        d4=r4['mechanism_evidence'][
            'defender_distance_to_pass_lane_at_release_m']
        d5=r5['mechanism_evidence'][
            'defender_distance_to_pass_lane_at_release_m']
        if d4 is not None and d5 is not None:
            distance_deltas.append(d4-d5)
            if (r4['mechanism_evidence'][
                    'defender_lane_option_selected_before_release'] and
                    r5['mechanism_evidence'][
                    'defender_lane_option_selected_before_release']):
                selected_distance_deltas.append(d4-d5)
    c4m,c5m=mechanism[names[0]],mechanism[names[1]]
    n4,n5=c4m['lane_option_seed_count'],c5m['lane_option_seed_count']
    x4,x5=c4m['interceptions_with_lane_option'],c5m['interceptions_with_lane_option']
    p4=x4/n4 if n4 else 0.;p5=x5/n5 if n5 else 0.
    pooled=(x4+x5)/(n4+n5) if n4+n5 else 0.
    se=math.sqrt(pooled*(1-pooled)*(1/n4+1/n5)) if n4 and n5 else 0.
    z=(p5-p4)/se if se else 0.
    p_value=math.erfc(abs(z)/math.sqrt(2.)) if se else 1.
    enough_matched=len(both_selected)>=100
    mechanism_supported=(
        enough_matched and matched_c5_interceptions>matched_c4_interceptions
        and matched_gained>matched_lost and mcnemar_p<.05)
    return {
        'baseline':names[0],'sharp':names[1],
        'seed_count_per_condition':len(rows_by[names[0]]),
        'paired_endpoint_differences':endpoint_differences,
        'paired_interceptions_gained':interceptions_gained,
        'paired_interceptions_lost':interceptions_lost,
        'baseline_mix':dict(sorted(Counter(r['endpoint']
                                          for r in rows_by[names[0]]).items())),
        'sharp_mix':dict(sorted(Counter(r['endpoint']
                                       for r in rows_by[names[1]]).items())),
        'mechanism':mechanism,
        'conditional_interception_rate_difference_sharp_minus_baseline':p5-p4,
        'conditional_interception_two_proportion_z':z,
        'conditional_interception_two_sided_p_approx':p_value,
        'matched_both_selected':{
            'seed_count':len(both_selected),
            'baseline_interceptions':matched_c4_interceptions,
            'sharp_interceptions':matched_c5_interceptions,
            'sharp_interceptions_gained':matched_gained,
            'sharp_interceptions_lost':matched_lost,
            'exact_two_sided_mcnemar_p':mcnemar_p},
        'mechanism_support_rule':(
            'at least 100 paired seeds where both select the lane; sharp has '
            'more interceptions, more paired gains than losses, and exact '
            'two-sided McNemar p<0.05'),
        'mechanism_support_rule_passed':mechanism_supported,
        'paired_release_lane_distance':{
            'sample_count':len(distance_deltas),
            'sharp_closer_count':sum(d>0 for d in distance_deltas),
            'baseline_closer_count':sum(d<0 for d in distance_deltas),
            'equal_count':sum(d==0 for d in distance_deltas),
            'mean_baseline_minus_sharp_m':(
                sum(distance_deltas)/len(distance_deltas)
                if distance_deltas else None)},
        'paired_release_lane_distance_when_both_selected':{
            'sample_count':len(selected_distance_deltas),
            'sharp_closer_count':sum(d>0 for d in selected_distance_deltas),
            'baseline_closer_count':sum(d<0 for d in selected_distance_deltas),
            'equal_count':sum(d==0 for d in selected_distance_deltas),
            'mean_baseline_minus_sharp_m':(
                sum(selected_distance_deltas)/len(selected_distance_deltas)
                if selected_distance_deltas else None)}}


def run_lane_study(seeds=400, seed_start=101):
    wall=time.perf_counter();cpu=time.process_time()
    episodes=[]
    for condition in ('C4_lane_defender','C5_lane_defender_sharp'):
        for seed in range(seed_start,seed_start+seeds):
            result=run_episode(seed,condition,False)
            episodes.append({k:result[k] for k in (
                'condition','seed','endpoint','failure_cause','cause_basis',
                'execution_hash','state_hash','mechanism_evidence')})
    return {'scenario_id':'m1-defender-lane-mechanism-study-v1',
            'seed_start':seed_start,'seeds_per_condition':seeds,
            'episodes':episodes,'lane_defender_comparison':_lane_comparison(episodes),
            'study_hash':digest(episodes),
            'performance':{'wall_s':time.perf_counter()-wall,
                           'cpu_s':time.process_time()-cpu},
            'runtime':platform.python_version()}


def run_matrix(seeds=100):
    wall=time.perf_counter();cpu=time.process_time()
    episodes=[]
    for condition in CONDITIONS:
        for seed in range(1,seeds+1):
            result=run_episode(seed,condition,False)
            episodes.append({k:result[k] for k in (
                'condition','seed','endpoint','failure_cause','cause_basis',
                'execution_hash','state_hash','mechanism_evidence')})
    by_condition={}
    for condition in CONDITIONS:
        rows=[r for r in episodes if r['condition']==condition]
        by_condition[condition]={
            'outcomes':dict(sorted(Counter(r['endpoint'] for r in rows).items())),
            'failure_causes':dict(sorted(Counter(r['failure_cause'] for r in rows
                                                 if r['failure_cause']).items())),
            'unknown_failure_causes':sum(r['failure_cause']=='unknown' for r in rows),
        }
    all_outcomes=set(r['endpoint'] for r in episodes)
    required={'pass_completed','pass_intercepted',
              'pass_incomplete_ball_loose','carrier_grounded'}
    lane_comparison=_lane_comparison(episodes)
    acceptance={
        'BA-M1-1_required_outcomes_present':required <= all_outcomes,
        'BA-M1-2_all_failures_traceable':all(
            v['unknown_failure_causes']==0 for v in by_condition.values()),
        'BA-M1-3_defender_quality_mechanism_demonstrated':(
            lane_comparison['mechanism_support_rule_passed']),
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
    payload={'scenario_id':'m1-carrier-pass-or-carry-v2',
             'seeds_per_condition':seeds,'conditions':by_condition,
             'episodes':episodes,'acceptance':acceptance,
             'lane_defender_comparison':lane_comparison,
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
    ap.add_argument('--lane-study',type=int,metavar='SEEDS_PER_CONDITION')
    ap.add_argument('--seed-start',type=int,default=101)
    ap.add_argument('--telemetry-off',action='store_true')
    ap.add_argument('--out',required=True)
    args=ap.parse_args()
    if args.matrix is not None and args.lane_study is not None:
        ap.error('--matrix and --lane-study are mutually exclusive')
    result=(run_matrix(args.matrix) if args.matrix is not None else
            run_lane_study(args.lane_study,args.seed_start)
            if args.lane_study is not None else
            run_episode(args.seed,args.condition,not args.telemetry_off))
    out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,sort_keys=True,indent=2,default=_jsonable)+'\n')
    print(json.dumps({k:v for k,v in result.items()
                      if k not in ('trace','episodes')},sort_keys=True))


if __name__=='__main__':
    main()
