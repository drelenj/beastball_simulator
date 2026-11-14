"""Native rule conformance. Test names are mapped in RULE_TO_TEST_MATRIX.json."""
from dataclasses import replace
import ast
import math
from pathlib import Path
import pytest
from b1.possession import PossessionTracker, RulesConfig
from .config import NativeConfig
from .port import NativePort, body
from . import cognition as C
from .geometry import goal_section,whole_ball_crossed,net_volume,body_out

@pytest.fixture
def port():
    p=NativePort(1);s=p.m.s;e=p.m.e;T=p.types
    s.now=1000;s.phase=T.Phase.LIVE;s.owner='A';s.ball=T.Ball(mode=T.BallMode.CONTROLLED,x=50,y=50,z=1.58,carrier='A0',control_time=0,scoring=True,last_touch='A')
    s.players['A0'].x=50;s.players['A0'].y=50
    e.hunt_cleared=True;e.native_seen=len(e.log)
    e.possession.step(0,{'A0':'A'},(50,50),[{'kind':'live'}],(50,50));e.possession.step(1000,{'A0':'A'},(50,50),[],(50,50))
    return p


def test_structure_configuration_and_effective_readback(port):
    assert port.verify_effective()['period_seconds']==600
    assert port.m.s.regulation_periods==4 and port.m.e.play_ms==30000
    assert sum(p.active for p in port.m.s.players.values())==24
    assert all(len([p for p in port.m.s.players.values() if p.team==t])==22 for t in ('A','B'))
    assert port.config.m2=='null' and not port.communication.model.enabled
    for p in port.m.s.players.values():
        for k in ('strength','passing','catching','awareness','keeper_skill','archery_accuracy'):assert getattr(p.a,k)==.70
    with pytest.raises(ValueError):replace(port.config,period_seconds=60)
    port.m.e.play_ms=45000
    with pytest.raises(AssertionError):port.verify_effective()


def test_hunt_each_period_any_field_claim_and_false_start_retake(port):
    e,s=port.m.e,port.m.s;e.begin_hunt();assert s.phase==port.types.Phase.OPENING
    s.players['A9'].x=50;s.players['A9'].y=50
    e.acquire('A9');assert not e.hunt_claims
    assert any(r['event']=='hunt_retake' for r in e.log)
    port.capture(s.now);s.now+=300
    v,b=port.view('A9',s.now);i,_=C.decide(v,b);assert i.kind=='hunt_claim'
    assert port.submit(i)['status']=='accepted';assert e.hunt_claims['A']=='A9'
    for period in (1,2,3,4,5):
        s.period=period;s.score={'A':0,'B':0};e.end_period()
        assert s.phase==port.types.Phase.OPENING and not e.hunt_claims


def test_first_overtime_is_whole_300s_and_later_is_sudden_death(port):
    e,s=port.m.e,port.m.s;s.period=4;s.score={'A':4,'B':4};e.end_period()
    assert s.period==5 and s.game_ms==300000 and s.phase==port.types.Phase.OPENING
    e.add_score('A',2,'release');assert s.phase!=port.types.Phase.FINAL
    e.elapse(1000);assert s.game_ms==299000
    s.score={'A':6,'B':6};s.game_ms=0;e.end_period()
    assert s.period==6 and s.phase==port.types.Phase.OPENING

@pytest.mark.parametrize('points,kind',[(2,'release'),(1,'half_goal')])
def test_sudden_death_ends_on_any_score(port,points,kind):
    e,s=port.m.e,port.m.s;s.period=6;s.score={'A':8,'B':8}
    e.add_score('A',points,kind)
    assert s.phase==port.types.Phase.FINAL and s.result['winner']=='A'


def test_geometry_goal_semicircle_whole_ball_quadrant_and_platform(port):
    assert goal_section(50,2.8,.1) and not goal_section(50,2.91,.1)
    assert not goal_section(53,1,.1)
    assert whole_ball_crossed(-.11,.1075,0) and not whole_ball_crossed(-.10,.1075,0)
    assert net_volume(2,50,2) and not net_volume(2.5,50,2)
    assert port.geom.zone(20,50,20) is None
    assert port.geom.zone(19.999,50,20)==0
    for p in port.m.s.players.values():
        if p.role=='archer':assert (p.x,p.y,p.z) in ((-5.,50.,5.),(105.,50.,5.))


def test_boundary_contact_and_airborne_proxy(port):
    p=port.m.s.players['A0'];p.x=p.radius;p.y=50;p.posture='upright'
    assert body_out(p)
    p.posture='airborne';assert not body_out(p)


def test_flat_goals_carry_distance_and_keeper_cannot_score(port):
    e,s=port.m.e,port.m.s;s.ball.x=101;s.ball.y=50;s.ball.z=1.5
    s.ball.native_release_point=(70,50)
    assert e.goal('B',50,1.5)
    assert s.score['A']==2 and e.native_stats['A']['goals']==1
    assert any(r['data'].get('method')=='carry' for r in e.log)
    s.phase=port.types.Phase.LIVE;s.ball=port.types.Ball(mode=port.types.BallMode.SHOT,x=101,y=50,z=1.5,scoring=True,last_releaser='A10')
    assert e.goal('B',50,1.5) is False and s.score['A']==2
    s.phase=port.types.Phase.LIVE;s.ball.x=-1;s.ball.scoring=True
    assert e.goal('A',50,1.5) and s.score['B']==2


def test_clock_stops_dead_carries_first_tackle_and_expiry_turnover(port):
    e,s=port.m.e,port.m.s;s.possession_ms=23456
    e.award('A',50,50,'first_tackle');s.tackle_count=1
    g=s.game_ms;e.elapse(1000);assert s.game_ms==g and s.possession_ms==22456
    s.possession_ms=10000;e.award('A',50,50,'first_tackle');e.elapse(1000);assert s.possession_ms==10000
    s.phase=port.types.Phase.LIVE;s.restart=None;s.owner='A';s.possession_ms=0;s.ball.x=75;s.ball.mode=port.types.BallMode.LOOSE;s.ball.carrier=None
    e.clock_expiry();assert s.restart.team=='B' and s.restart.x==60 and s.tackle_count==0 and s.possession_ms==30000


def test_only_shots_get_clock_flight_exception(port):
    e,s=port.m.e,port.m.s;s.ball.carrier=None;s.ball.z=2;s.possession_ms=0
    s.ball.mode=port.types.BallMode.PASS;e.clock_expiry();assert s.phase==port.types.Phase.DEAD
    s.phase=port.types.Phase.LIVE;s.restart=None;s.owner='A';s.possession_ms=0;s.ball.mode=port.types.BallMode.SHOT;s.ball.z=2
    e.clock_expiry();assert s.phase==port.types.Phase.FLIGHT


def test_shot_release_at_expiry_precedes_clock(port):
    s,e=port.m.s,port.m.e;s.possession_ms=0
    assert e.release('A0',(25,0,2),'shot')
    e.clock_expiry();assert s.phase==port.types.Phase.FLIGHT


def test_first_tackle_snapper_tackler_reset10_second_turnover(port):
    e,s=port.m.e,port.m.s;s.ball.x=96;s.ball.y=20
    assert e.tackle('B0','A0',witnessed=True)
    assert s.restart.kind=='scrim' and s.restart.x==90 and s.tackle_count==1
    assert s.restart.rs['snapper']=='A0' and s.restart.rs['tackler']=='B0'
    s.phase=port.types.Phase.LIVE;s.ball.carrier='A0';s.ball.mode=port.types.BallMode.CONTROLLED;s.players['A0'].posture='upright';s.ball.x=75
    assert e.tackle('B0','A0',witnessed=True)
    assert s.restart.team=='B' and s.restart.x==60 and s.tackle_count==0

@pytest.mark.parametrize('count,side,expected_count,expected_team,expected_x',[(0,'offence',1,'A',45),(1,'offence',0,'B',45),(1,'defence',0,'A',55),(0,'defence',0,'A',55)])
def test_scrimmage_offside_procedural(port,count,side,expected_count,expected_team,expected_x):
    e,s=port.m.e,port.m.s;e.award('A',50,50,'first_tackle');s.tackle_count=count;before=dict(s.score)
    e.offside(side)
    assert s.tackle_count==expected_count and s.restart.team==expected_team and s.restart.x==expected_x
    assert s.score==before


def test_snap_window_missed_costs_count_and_spot(port):
    e,s=port.m.e,port.m.s;e.award('A',50,50,'first_tackle');s.tackle_count=0
    e.elapse(10000)
    assert s.restart.x==45 and s.tackle_count==1

@pytest.mark.parametrize('period,points',[(1,1),(2,1),(3,1),(4,2),(5,2)])
def test_defensive_minor_awards_and_retains(port,period,points):
    e,s=port.m.e,port.m.s;s.period=period;s.tackle_count=0
    e.foul('B0','A0','unintentional_head')
    assert s.score['A']==points and s.restart.team=='A' and s.tackle_count==0
    assert s.players['B0'].minor_count==1


def test_offence_minor_second_is_turnover_and_defence_costs_count(port):
    e,s=port.m.e,port.m.s;e.foul('A0',reason='second_dribble')
    assert s.tackle_count==1 and s.restart.team=='A'
    e.foul('A0',reason='second_dribble');assert s.tackle_count==0 and s.restart.team=='B'
    e.possession.pp='A';s.owner='A';s.tackle_count=1;e.foul('B0',reason='hold')
    assert s.tackle_count==0 and s.restart.team=='A'


def test_discipline_ladder_cover_and_game_time_exclusion(port):
    e,s=port.m.e,port.m.s
    for _ in range(3):e.discipline('A1','minor')
    assert s.players['A1'].exclusion_ms==0
    e.discipline('A1','minor');assert s.players['A1'].exclusion_ms==60000
    port.fill_cover();port.assert_invariants()
    s.phase=port.types.Phase.DEAD;s.restart=e.award('A',50,50,'test');e.elapse(1000)
    assert s.players['A1'].exclusion_ms==60000
    s.phase=port.types.Phase.LIVE;s.restart=None;e.elapse(1000)
    assert s.players['A1'].exclusion_ms==59000
    e.discipline('A1','minor');assert s.players['A1'].disqualified
    e.discipline('B1','major');assert s.players['B1'].exclusion_ms==120000
    port.fill_cover();e.discipline('B1','major');assert s.players['B1'].disqualified


def test_intent_defines_major_not_incidental_head(port):
    e,s=port.m.e,port.m.s
    e.foul('B0','A0','head',major=True,danger=True);assert s.players['B0'].major_count==0
    s.players['B1'].native_intent=C.ActionIntent('i','d','B1','press','A0',None,None,None,s.now,contact='head')
    e.foul('B1','A0','head');assert s.players['B1'].major_count==1


def test_contact_legal_band_grip_and_carrier_joints(port):
    e,s=port.m.e,port.m.s;a,t=s.players['B0'],s.players['A0'];a.x=50;a.y=51;t.x=50;t.y=50
    for surface in ('joint','knee'):assert e.contact_legal(a,t,'tackle',surface)[0]
    s.ball.carrier='A1'
    assert not e.contact_legal(a,t,'grip')[0]
    assert e.contact_legal(a,t,'block','hip')[0]
    assert not e.contact_legal(a,t,'block','head')[0]


def test_keeper_immunity_position_at_contact_and_freeze_in_all_phases(port):
    e,s=port.m.e,port.m.s;k,a=s.players['A10'],s.players['B0'];k.x=3;k.y=50;a.x=4;a.y=50
    assert not e.contact_legal(a,k,'block')[0]
    k.x=21;a.x=22;assert e.contact_legal(a,k,'block')[0]
    for phase in (port.types.Phase.LIVE,port.types.Phase.OPENING,port.types.Phase.DEAD):
        s.phase=phase;k.x=3;assert not e.freeze(k.id)


def test_archer_illegal_release_spends_ammo_abort_does_not_and_platform_ballistic(port):
    e,s=port.m.e,port.m.s;before=s.quivers['B'].spent
    assert e.shoot_arrow('B11','A10',(20,0,0)) is False
    assert s.quivers['B'].spent==before+1
    assert s.players['B11'].minor_count==1
    a=s.players['A11'];origin=(a.x,a.y,a.z+.72*a.a.height)
    assert port.geom.ballistic(origin,(50,50,1.6),29.) is not None
    before=s.quivers['A'].spent;i=C.ActionIntent('abort','d','A11','abort_draw',None,None,None,None,s.now)
    port.submit(i);assert s.quivers['A'].spent==before


def test_freeze_cap_and_five_plus_ten_seconds(port):
    e,s=port.m.e,port.m.s
    for i in range(6):
        p=s.players[f'B{i}'];p.x=40;p.y=50+i;p.immune_until=0
        ok=e.freeze(p.id)
        assert bool(ok)==(i<5)
        if ok:assert p.freeze_until==s.now+5000 and p.immune_until==s.now+15000


def test_dribble_second_foul_reset_stoppage_and_other_touch(port):
    e,s=port.m.e,port.m.s
    assert e.release('A0',(15,0,1),'dribble');assert e.dribbles['A0']==1
    s.ball.carrier='A0';s.ball.mode=port.types.BallMode.CONTROLLED
    assert not e.release('A0',(15,0,1),'dribble');assert s.tackle_count==1
    assert not e.dribbles
    s.phase=port.types.Phase.LIVE;s.ball.carrier='A0';s.ball.mode=port.types.BallMode.CONTROLLED
    e.dribbles={'A0':1};e.touch('B0');assert not e.dribbles
    with pytest.raises(AssertionError):e.release('A0',(1,0,0),'kick')


def test_toss_crossing_arc_slide_clearance_ready_no_self_no_direct_score(port):
    e,s=port.m.e,port.m.s;r=e.award('A',0,50,'boundary',normalize=False)
    assert r.kind=='toss' and r.x==0 and abs(r.y-50)==20 and r.clearance==3
    assert r.taker_spot[0]<0
    p=s.players['A0'];p.x,p.y=r.taker_spot
    assert not e.ready(p.id);s.now+=1500
    assert e.ready(p.id)
    for q in s.players.values():
        if q.team=='B':q.x=80;q.y=80
    assert e.restart_release(p.id,(15,0,1),'A1')
    assert not s.ball.scoring
    assert not e.acquire(p.id)


def test_exact_goal_catch_and_boundary_secure_ties(port):
    s,e,T=port.m.s,port.m.e,port.types
    s.ball=T.Ball(mode=T.BallMode.SHOT,x=101,y=50,z=1.5,scoring=True,last_releaser='A0')
    e.batch([T.Event('acquire','B1'),T.Event('goal',data={'defending':'B','y':50,'z':1.5})])
    assert s.score['A']==2
    s.phase=T.Phase.LIVE;s.ball=T.Ball(mode=T.BallMode.PASS,x=50,y=101,z=1,last_touch='A')
    e.batch([T.Event('acquire','A1'),T.Event('boundary',data={'x':50,'y':100})])
    assert s.phase==T.Phase.DEAD and s.restart.team=='B'


def test_information_boundary_and_all_commands_from_pure_decide(port):
    port.capture(port.m.s.now);now=port.m.s.now+300;port.m.s.now=now
    v,b=port.view('A0',now);before=C.decide(v,b)
    port.m.s.players['B0'].x=-9999;port.m.s.ball.z=9999
    assert C.decide(v,b)==before
    assert len(v.policy.as_dict())==16
    assert 'home' not in C._base_decide.__code__.co_consts
    modules={n.module for n in ast.walk(ast.parse(Path(C.__file__).read_text())) if isinstance(n,ast.ImportFrom)}
    assert not any(x and ('port' in x or 'engine' in x) for x in modules)
    i,_=before;assert port.submit(i)['status']=='accepted'
    assert all(cmd.command_id.startswith(cmd.intent.intent_id) for cmd in port.command_log)


def test_primitive_throw_speed_height_arc_are_intent_owned(port):
    s=port.m.s
    i=C.ActionIntent('i','d','A0','pass','A1',(60.,55.),None,None,s.now,speed=24.,height=2.4)
    assert port.submit(i)['status']=='accepted'
    cmd=port.pending['A0']['cmd'];assert math.isclose(math.sqrt(sum(v*v for v in cmd.desired_velocity)),24.,rel_tol=1e-7)
    # Poisoning a receiver cannot redirect the semantic pass.
    s.players['A1'].x=95;s.players['A1'].y=95;s.now+=250;port.ball_motor()
    assert port.release_log[-1]['height']==2.4 and port.release_log[-1]['target']=='A1'

@pytest.mark.parametrize('violation', ['ZR-1','ZR-C','ZR-T'])
def test_possession_zone_violations_are_enforced_as_rst1(port,violation):
    e,s=port.m.e,port.m.s
    s.ball.carrier='A0';s.ball.mode=port.types.BallMode.CONTROLLED;s.players['A0'].x=25;s.players['A0'].y=50
    s.ball.x=25;s.ball.y=50;e.native_seen=len(e.log)
    if violation=='ZR-C':
        e.possession.carry_inside=False;s.players['A0'].x=10;s.ball.x=10
    elif violation=='ZR-1':
        s.players['A0'].x=10;s.ball.x=10;e.possession.carry_inside=True;e.possession.zone_start['A']=s.now-5000
    else:
        e.possession.passing={'team':'A','passer':'A1','defender_touched':False,'was_outside':True}
        e.possession.dp_team=None;e.possession.unc_team=None;s.ball.x=10;s.players['A0'].x=10
    e.native_sync()
    assert s.restart is not None and s.restart.team=='B' and s.restart.reason==violation
    assert e.possession.pp=='B' and all(v==0 for _,v in e.possession.public().zone_clock_ms)


def test_recovery_arrow_protection_three_metres_two_seconds(port):
    e,s=port.m.e,port.m.s;p=s.players['B0'];p.x=40;p.y=50;p.native_recovery=(40,50,s.now)
    assert not e.freeze(p.id)
    s.now+=2000;assert e.freeze(p.id)


def test_toss_deadline_four_seconds_after_ready(port):
    e,s=port.m.e,port.m.s;r=e.award('A',50,0,'boundary');p=s.players['A0'];p.x,p.y=r.taker_spot
    s.now+=1500;assert e.ready(p.id);ready=r.ready_at
    e.elapse(3999);assert s.restart is r
    e.elapse(1);assert s.restart.team=='B' and s.restart is not r
    assert s.now==ready+4000


def test_formation_independent_of_slot_and_residence_exit_intent(port):
    s=port.m.s;port.capture(s.now);s.now+=300;v,b=port.view('A1',s.now)
    v=replace(v,role='field',x=10.,y=50.,zone_elapsed_ms=3001,restart=None,hunt=False)
    i,_=C.decide(v,b);j,_=C.decide(replace(v,slot=9),b)
    assert (i.kind,i.aim)==(j.kind,j.aim) and i.kind=='position'
    assert math.hypot(i.aim[0],i.aim[1]-50)>20


def test_environment_flags_cannot_enable_a_native_legacy_layer(monkeypatch):
    for key in ('RULES_V03','PRISM_FIELD','PRISM_MANEUVERS','PRISM_OFFACT','PRISM_KEEPER','CATCH_V2','HAND_FIGHT','PLAT','PLAT_H'):
        monkeypatch.setenv(key,'999')
    p=NativePort(12);assert p.config.legacy_layers==() and p.verify_effective()['platform_height']==5


def test_native_view_json_replays_exact_decision(port):
    import json
    s=port.m.s;port.capture(s.now);s.now+=300
    for pid in ('A0','A10','A11'):
        v,b=port.view(pid,s.now)
        v2,b2=C.view_from_json(json.loads(json.dumps(C.view_to_json(v,b))))
        assert C.decide(v,b)==C.decide(v2,b2)


def test_native_direct_possession_threshold_is_enforced_in_real_port(port):
    e,s=port.m.e,port.m.s;s.ball.carrier=None;s.ball.mode=port.types.BallMode.LOOSE;s.ball.x=50;s.ball.y=50;s.ball.last_releaser=None
    p=s.players['B0'];p.x=50;p.y=50;s.now=2000
    assert e.acquire(p.id)
    assert e.possession.pp=='A'
    s.now=2499;e.native_sync();assert e.possession.pp=='A'
    s.now=2500;e.native_sync();assert e.possession.pp=='B' and e.possession.dp_holder=='B0'


def test_native_body_contact_does_not_contest_but_joint_ball_touch_does(port):
    e,s=port.m.e,port.m.s
    e.emit('engagement','test',actor='B0',target='A0',kind='block');e.native_sync()
    assert not e.possession.contested
    s.ball.carrier=None;s.players['B0'].x=50;s.players['B0'].y=50
    e.joint_control(['A0','B0']);e.native_sync()
    assert e.possession.contested and e.possession.pp=='A' and e.possession.dp_holder is None


def test_forfeit_only_below_twelve_currently_available(port):
    e,s=port.m.e,port.m.s
    for i in range(10):e.discipline(f'A{i}','dq');port.fill_cover()
    assert s.phase!=port.types.Phase.FINAL and sum(p.team=='A' and p.active for p in s.players.values())==12
    e.discipline('A10','dq')
    assert s.phase==port.types.Phase.FINAL and s.result['method']=='forfeit'


def test_final_transition_needs_no_time_advance(monkeypatch):
    from . import run
    def finish(port):port.m.e.complete('regulation','A')
    monkeypatch.setattr(NativePort,'step',finish)
    r,_=run.run_match(1)
    assert r['status']=='final'


def test_noncarry_goal_release_distance_attempts_and_success(port):
    e,s=port.m.e,port.m.s
    assert e.release('A0',(27,0,2),'shot')
    origin=s.ball.native_release_point;distance=math.hypot(100-origin[0],origin[1]-50)
    s.ball.x=101;s.ball.y=50;s.ball.z=1.6
    assert e.goal('B',50,1.6)
    goal=next(r for r in reversed(e.log) if r['event']=='goal')
    assert math.isclose(goal['data']['release_distance'],distance)
    assert e.release_attempts['A'][int(distance)]==e.release_successes['A'][int(distance)]==1


def test_m2_null_absent_short_replay_and_harness_pairs():
    from .run import run_match
    from .emergence.harness import paired_jobs
    from .emergence.params import DEFAULT
    a,_=run_match(3,plumbing=True,max_steps=400)
    b,_=run_match(3,plumbing=False,max_steps=400)
    assert (a['trace_hash'],a['state_hash'])==(b['trace_hash'],b['state_hash'])
    jobs=paired_jobs([9001,9002],600,'A',DEFAULT,'B',DEFAULT)
    assert len(jobs)==4 and jobs[0]['label_A']==jobs[1]['label_B']


def test_zone_residence_enforced_marked_defender_and_keeper_exempt(port):
    s,e=port.m.s,port.m.e
    for i,p in enumerate(s.players.values()):
        if p.active and p.role=='field':p.x=40+(i%5)*4;p.y=10+(i%4)*20;p.target=(p.x,p.y);p.vx=p.vy=0
    s.players['A0'].x=50;s.players['A0'].y=50;s.players['A0'].target=(50,50)
    s.ball.x=50;s.ball.y=50
    a,b=s.players['A2'],s.players['B1'];a.x=79;a.y=50;a.target=(79,50);b.x=80.5;b.y=50;b.target=(80.5,50)
    start=s.live_ms
    while s.live_ms-start<6000:port.step()
    assert s.owner=='A' and e.native_stats['B']['minor_fouls']==0
    # Put an attacker alone inside attacked zone; the expiry must turn over.
    a.x=90;a.y=50;a.target=(90,50);b.x=50;b.y=10;b.target=(50,10)
    start=s.live_ms
    while s.live_ms-start<6000 and s.phase==port.types.Phase.LIVE:port.step()
    assert s.restart is not None and s.restart.team=='B' and s.restart.reason=='zone_residence'


def test_mandatory_keeper_snapper_can_restart_outside_own_zone(port):
    e,s=port.m.e,port.m.s
    r=e.award('A',50,50,'first_tackle');r.rs['snapper']='A10';s.tackle_count=1
    p=s.players['A10'];p.x=50;p.y=50;p.posture='upright'
    for q in s.players.values():
        if q.active and q.role!='archer' and q.id!=p.id:q.x=40 if q.team=='A' else 60
    assert e.ready(p.id)
    assert e.restart_release(p.id,(20,0,2),'A1')

@pytest.mark.parametrize('threshold',[250,500,1000])
def test_native_port_direct_threshold_sensitivity(threshold):
    p=NativePort(9,replace(NativeConfig(),direct_ms=threshold));s,e=p.m.s,p.m.e
    s.now=2000;s.phase=p.types.Phase.LIVE;e.hunt_cleared=True;e.native_seen=len(e.log)
    e.possession.pp='A';e.possession.live=True;s.owner='A'
    s.ball=p.types.Ball(mode=p.types.BallMode.LOOSE,x=50,y=50,z=.1075)
    s.players['B0'].x=50;s.players['B0'].y=50
    assert e.acquire('B0');assert e.possession.pp=='A'
    s.now+=threshold-1;e.native_sync();assert e.possession.pp=='A'
    s.now+=1;e.native_sync();assert e.possession.pp=='B'


def test_shared_catch_reach_and_heldout_partition(port):
    from .emergence.harness import held_out_jobs
    from .emergence.params import DEFAULT
    k=port.m.s.players['A10']
    assert math.isclose(port.m.c4c_reach(k),.9*k.a.reach)
    assert len(held_out_jobs([1,2],[9001], 'a',DEFAULT,'b',DEFAULT))==2
    with pytest.raises(ValueError):held_out_jobs([1],[1], 'a',DEFAULT,'b',DEFAULT)


def test_native_finality_gate_closes_new_mutators(port):
    e,s=port.m.e,port.m.s;e.complete('regulation','A');score=dict(s.score);now=s.now
    e.add_score('B',2,'release');e.foul('A0','B0','head');e.elapse(1000);e.award('B',50,50,'test')
    assert s.score==score and s.now==now and s.phase==port.types.Phase.FINAL


def test_keeper_touch_cannot_create_own_team_goal(port):
    e,s=port.m.e,port.m.s;s.ball.carrier=None;s.ball.mode=port.types.BallMode.SHOT;s.ball.scoring=True;s.ball.last_releaser='B1'
    e.touch('A10');s.ball.x=101;s.ball.y=50;s.ball.z=1.6
    assert not e.goal('B',50,1.6) and s.score['A']==0


def test_stray_arrow_can_freeze_keeper_outside_own_zone_but_cannot_target_him(port):
    e,s=port.m.e,port.m.s;k=s.players['B10'];k.x=50;k.y=50;k.immune_until=0
    assert not e.shoot_arrow('A11',k.id,(20,0,1))
    s.phase=port.types.Phase.LIVE;s.restart=None
    assert e.freeze(k.id)


def test_incidental_simultaneous_heads_cannot_bypass_major_intent_gate(port):
    e,s,T=port.m.e,port.m.s,port.types
    events=[T.Event('foul','A1','B1',{'reason':'head','major':True,'danger':True}),
            T.Event('foul','B1','A1',{'reason':'head','major':True,'danger':True})]
    e.batch(events)
    assert s.players['A1'].major_count==s.players['B1'].major_count==0
    assert s.players['A1'].minor_count==s.players['B1'].minor_count==1
    assert port.m.assume['c3_region_policy']==0
