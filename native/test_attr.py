from dataclasses import replace
import csv
import math
import random
from concurrent.futures import ProcessPoolExecutor

import pytest

from .config import AttrConfig,NativeConfig,NativeConfigV3
from .port import NativePort
from .roster import (
    RATINGS,RosterError,acceleration,braking,engine_order,load_csv,load_rows,
    mapped_values,max_throw_speed,sensor_noise_scale,speed_mps,throw_error_base_deg,turning,
)
from .run import run_match
from .attr_sensitivity import run as sensitivity_run


def rows(prefix='p',labels=False):
    result=[]
    roles=['field']*18+['keeper']*2+['archer']*2
    for i,role in enumerate(roles):
        row={k:.7 for k in RATINGS}
        row.update(id=f'{prefix}{i}',role=role,height_m=2.55,mass_kg=230.)
        if labels:row.update(name='Name '+str(i),position='DO NOT READ',archetype='DO NOT READ',overall=.99)
        result.append(row)
    return result


def rosters(prefix='p'):
    return {team:load_rows(rows(prefix+team),team) for team in ('A','B')}


def config(rs):
    return AttrConfig(roster_digests=tuple(rs[t].digest for t in ('A','B')))


def test_at1_at2_speed_curve_and_measured_top_speed():
    assert speed_mps(0)==0
    assert speed_mps(.6)==pytest.approx(26.8224)
    assert speed_mps(.8)==pytest.approx(35.7632)
    assert speed_mps(1)==pytest.approx(44.704)
    raw=rows();raw[0]['speed']=raw[0]['agility']=1.;rs={t:load_rows(raw,t) for t in ('A','B')}
    p=NativePort(1,config(rs),rosters=rs);s=p.m.s;q=s.players['A:p0']
    s.phase=p.types.Phase.LIVE;s.ball.carrier=q.id;s.ball.mode=p.types.BallMode.CONTROLLED
    q.x,q.y=0.,-100.;q.target=(500.,-100.)
    for other in s.players.values():
        if other is not q:other.active=False
    travelled=0.
    for _ in range(1200):
        before=q.x;p.m.move_players(100,{q.id:(500.,-100.)});travelled+=max(0,q.x-before)
        # Lab treadmill removes the match boundary while preserving velocity.
        if q.x>100:q.x=0.;q.target=(500.,-100.)
    assert travelled>400 and q.speed==pytest.approx(44.704,rel=.005)


@pytest.mark.parametrize('rating',[0,.4,.6,.8,1.])
def test_at4_mapping_table(rating):
    assert speed_mps(rating)==pytest.approx(44.704*rating)
    assert acceleration(rating,rating)==pytest.approx(12.5*rating)
    assert braking(rating)==pytest.approx(16.875*rating)
    assert turning(rating)==pytest.approx(16.25*rating)
    x=min(1,max(0,(rating-.4)/.6))
    assert max_throw_speed(rating)==pytest.approx(134.1*(.5+.5*x))
    assert throw_error_base_deg(rating)==pytest.approx(max(.15,3*(1-x)))
    assert sensor_noise_scale(rating)==pytest.approx(2-1.25*rating)


def test_at5_monotone_and_at6_independence():
    grid=[i/20 for i in range(21)]
    increasing=(speed_mps,braking,turning,max_throw_speed)
    decreasing=(throw_error_base_deg,sensor_noise_scale)
    for fn in increasing:
        values=[fn(x) for x in grid];assert values==sorted(values)
    for fn in decreasing:
        values=[fn(x) for x in grid];assert values==sorted(values,reverse=True)
    base=load_rows(rows(),'A').athletes[0]
    for rating in RATINGS:
        raw=rows();raw[0][rating]=.8
        changed=load_rows(raw,'A').athletes[0]
        before=mapped_values(base);after=mapped_values(changed)
        diff={k for k in before if before[k]!=after[k]}
        expected={
          'speed':{'maximum_speed'},'agility':{'agility','braking','turning'},
          'strength':{'strength'},'balance':{'balance'},'stamina':{'endurance'},'tackling':{'tackling'},
          'blocking':{'blocking'},'contact_resistance':{'contact_resistance'},
          'ball_handling':{'ball_handling'},'catching':{'catching'},'awareness':{'awareness'},
          'throw_power':set(),'throw_accuracy':{'passing'},'jump':{'jump_height'},
          'keeper_skill':{'keeper_skill'},'archery_accuracy':{'archery_accuracy'},
        }[rating]
        assert diff==expected,(rating,diff)
        if rating=='throw_power':assert max_throw_speed(dict(changed.values)[rating])!=max_throw_speed(dict(base.values)[rating])
        if rating=='throw_accuracy':assert throw_error_base_deg(dict(changed.values)[rating])!=throw_error_base_deg(dict(base.values)[rating])
        if rating=='awareness':assert sensor_noise_scale(dict(changed.values)[rating])!=sensor_noise_scale(dict(base.values)[rating])


def test_at8_body_readback_and_own_view_only():
    raw=rows();raw[0].update(height_m=2.8,mass_kg=250,reach_m=1.4,throw_power=.8)
    rs={t:load_rows(raw,t) for t in ('A','B')};p=NativePort(2,config(rs),rosters=rs)
    q=p.m.s.players['A:p0'];assert q.a.height==2.8 and q.a.reach==1.4 and q.radius==pytest.approx(.4625)
    assert .72*q.a.height==pytest.approx(2.016) and q.hand_height==pytest.approx(.62*2.8)
    p.capture(0);p.m.s.now=300;v,b=p.view(q.id,300)
    assert v.own_mass_kg==250 and v.max_throw_speed==pytest.approx(111.75)
    assert dict(v.own_skills)['strength']==.7 and v.signals.tackle_count==0
    assert not any(hasattr(t,'mass') or hasattr(t,'maximum_speed') for t in v.tracks)


def test_at9_arrow_speed_fixed_for_different_rosters():
    first=rosters('x');second=rosters('y')
    altered=rows('z');altered[19]['speed']=1.;second={t:load_rows(altered,t) for t in ('A','B')}
    assert NativePort(1,config(first),rosters=first).arrow_speed==250
    assert NativePort(1,config(second),rosters=second).arrow_speed==250


def test_at10_validation_names_row_and_column():
    bad=rows();bad[3]['speed']=1.2
    with pytest.raises(RosterError,match='row 5 column speed'):load_rows(bad,'A')
    bad=rows();del bad[3]['catching']
    with pytest.raises(RosterError,match='row 5 column catching'):load_rows(bad,'A')
    bad=rows();bad[3]['mystery']=1
    with pytest.raises(RosterError,match='row 5 column mystery'):load_rows(bad,'A')
    bad=rows();bad[3]['id']=bad[0]['id']
    with pytest.raises(RosterError,match='row 5 column id'):load_rows(bad,'A')


def test_at11_labels_never_read_and_digest_identical():
    plain=load_rows(rows(),'A');labelled=load_rows(rows(labels=True),'A')
    assert plain.digest==labelled.digest
    changed=rows(labels=True)
    for i,row in enumerate(changed):row.update(name='X'+str(i),position='P'+str(i),archetype='Q'+str(i),overall=i/22)
    assert load_rows(changed,'A').digest==plain.digest


def test_real_generator_export_with_obsolete_kick_rating_is_rejected():
    with pytest.raises(RosterError,match='column kick_power: unknown column'):
        load_csv('Ala_Lady_Reds_generated.csv','A')


def test_at12_shape_and_fixed_roles():
    assert len(load_rows(rows(),'A').athletes)==22
    for mutate,message in [
      (lambda x:x.pop(),'expected 22'),
      (lambda x:[x[i].update(role='keeper') for i in range(9)],'at least 10 field'),
      (lambda x:[r.update(role='field') for r in x if r['role']=='keeper'],'active and reserve keeper'),
      (lambda x:[r.update(role='field') for r in x if r['role']=='archer'],'active and reserve archer'),
    ]:
        bad=rows();mutate(bad)
        with pytest.raises(RosterError,match=message):load_rows(bad,'A')
    rs=rosters();p=NativePort(1,config(rs),rosters=rs);s=p.m.s;e=p.m.e
    e.vacancies.append(('A','keeper',10,3.,50.));s.players['A:pA18'].active=False
    assert all(q.role!='field' for q in s.players.values() if q.team=='A' and not q.active and q.role=='keeper')
    assert p._submit_intent(__import__('native.cognition',fromlist=['ActionIntent']).ActionIntent('i','d','A:pA12','substitute_claim',None,None,None,None,s.now))['status']=='rejected'


def test_engine_and_ingress_use_thrower_maximum():
    raw=rows();raw[0]['throw_power']=.6;rs={t:load_rows(raw,t) for t in ('A','B')};p=NativePort(1,config(rs),rosters=rs)
    s,e=p.m.s,p.m.e;q=s.players['A:p0'];s.phase=p.types.Phase.LIVE
    s.ball=p.types.Ball(mode=p.types.BallMode.CONTROLLED,carrier=q.id,x=q.x,y=q.y,z=q.hand_height)
    assert q.native_max_throw_speed==pytest.approx(89.4)
    assert not e.release(q.id,(90,0,0),'pass')


def test_at14_teammate_rating_poison_does_not_enter_equal_position_view():
    base=rosters();raw=rows('pA');raw[1]['strength']=1.;changed={'A':load_rows(raw,'A'),'B':base['B']}
    p1=NativePort(5,config(base),rosters=base);p2=NativePort(5,config(changed),rosters=changed)
    for ports in (p1,p2):
        for q in ports.m.s.players.values():q.x,q.y=20+q.slot,40
        ports.capture(0);ports.m.s.now=300
    v1,_=p1.view('A:pA0',300);v2,_=p2.view('A:pA0',300)
    assert v1==v2


def _window(args):
    seed,raw=args;rs={t:load_rows(raw,t) for t in ('A','B')}
    result,_=run_match(seed,config(rs),rosters=rs,max_steps=100)
    return result['trace_hash'],result['state_hash'],result['config_digest']


def test_at13_short_serial_parallel_determinism_and_digest_in_trace():
    raw=rows();a=_window((7,raw));b=_window((7,raw));assert a==b
    with ProcessPoolExecutor(2) as pool:parallel=list(pool.map(_window,[(7,raw),(7,raw)]))
    assert parallel==[a,a]
    changed=rows();changed[0]['strength']=.8
    assert _window((7,changed))[0]!=a[0]


def test_e8_fast_closing_sweep_detects_contact_and_boundary_endpoint():
    raw=rows();raw[0]['speed']=raw[1]['speed']=1.;rs={t:load_rows(raw,t) for t in ('A','B')};p=NativePort(1,config(rs),rosters=rs)
    s=p.m.s;a=s.players['A:p0'];b=s.players['B:p0'];s.phase=p.types.Phase.LIVE
    a.x,a.y,a.vx=45,50,44.704;b.x,b.y,b.vx=55,50,-44.704
    events=p.m.player_contacts(100,{a.id:(45,50,0),b.id:(55,50,0)})
    # C3 swept kernel may adjudicate in c3_step; it must at least retain the pair
    # as a physical collision rather than tunnel through in a full step.
    p.m.c3_step(100,{a.id:(80,50),b.id:(20,50)})
    assert a.x<=b.x or p.m.stats['c3_collisions']>0
    a.x,a.y,a.vx=99,20,44.704;p.m.move_players(100,{a.id:(200,20)})
    assert a.x>100


def test_at7_sensitivity_audit_200_paired_trials_per_rating():
    base_b=load_rows(rows('b'),'B')
    def factory(team_a):
        rs={'A':team_a,'B':base_b};return NativePort(9,config(rs),rosters=rs)
    report=sensitivity_run(factory)
    assert len(report)==len(RATINGS) and all(r['trials']==200 and r['passes'] for r in report)
    assert {r['rating'] for r in report if r['observed']=='INERT'}=={'stamina','keeper_skill','archery_accuracy'}
