"""RB-3.6 PROVISIONAL defender baseline (owner, 18 Nov 2026): within defender_mark_distance_m of an
opposing field player or within defender_ball_leash_m of the ball; freeze-recovery retreat; zone exit
and re-entry; marking assignment. Cognition only, native-rb/3 views only."""
import json
from dataclasses import replace
import pytest
from .port import RulebookPort
from .config import RulebookConfigV3
from .test_rb33 import control_rosters
from .test_rb34 import live
from .test_rb35 import tick, setup, player
from native import cognition as C
from native import cognition_rb3 as R


def rb3(**kw):
    rosters=control_rosters()
    return RulebookPort(1,RulebookConfigV3(roster_digests=tuple(rosters[t].digest for t in ('A','B')),**kw),rosters=rosters)


def defender_view(p,pid):
    s=p.m.s;p.capture(s.now);s.now+=300;v,b=p.view(pid,s.now)
    sig=replace(v.signals,passive_team='B',phase='live')
    return replace(v,signals=sig,restart=None,pending_command_id=None),b


def T(eid,team,x,y,now):return C.Track(eid,team,'field' if eid!=C.BALL else 'ball',x,y,0.,0.,now)


def scene(v,b,me,others,ball):
    tracks=tuple(T(e,t,x,y,v.delivered_ms) for e,t,x,y in others)+(T(C.BALL,'ball',*ball,v.delivered_ms),)
    v=replace(v,x=me[0],y=me[1],tracks=tracks,holds_ball=False);b=replace(b,tracks=tracks,own_feedback=(),last_ball=None)
    return v,b


def scan(v):return C.ActionIntent('i','d',v.athlete,'scan',None,(v.x,v.y),None,None,v.delivered_ms)


def test_config_names_and_defaults():
    f=RulebookConfigV3.__dataclass_fields__
    assert f['defender_mark_distance_m'].default==5.0 and f['defender_ball_leash_m'].default==25.0 and f['defender_baseline'].default is True
    assert 'defender_carrier_leash_m' not in f
    with pytest.raises(ValueError):rb3(defender_ball_leash_m=0.)
    assert rb3(defender_ball_leash_m=15.).config.digest!=rb3().config.digest


def test_rb3_view_carries_the_instruction_and_rb2_does_not():
    p=rb3(defender_ball_leash_m=35.);s,e,a,t=live(p);v,b=defender_view(p,a)
    assert v.defender_baseline==(True,5.0,35.0)
    blob=json.loads(json.dumps(C.view_to_json(v,b)));v2,b2=p.view_from_json(blob);assert v2.defender_baseline==(True,5.0,35.0)
    q=RulebookPort(1);q.capture(q.m.s.now);q.m.s.now+=300;w,_=q.view('A0',q.m.s.now)
    assert w.defender_baseline is None and w.own_zone_exit_ms_ago is None and w.own_recovery_from_x is None


def test_neither_condition_moves_to_the_nearer_one():
    p=rb3();s,e,a,t=live(p);d=next(q.id for q in s.players.values() if q.team=='A' and q.role=='field' and q.active)
    v,b=defender_view(p,d)
    # attacker 9 m away (4 m to mark), ball 40 m away (15 m to leash): mark
    v1,b1=scene(v,b,(50.,50.),[('B:1','B',59.,50.)],(90.,50.))
    i,r=R.defender_baseline(v1,b1,scan(v1),{});assert i.kind=='mark' and i.target=='B:1' and r['rb36']['cost_m']==4.0
    assert abs(((i.aim[0]-59.)**2+(i.aim[1]-50.)**2)**.5-3.5)<1e-3          # goal side, inside 5 m
    # attacker 40 m away, ball 30 m away: leash (5 m to go)
    v2,b2=scene(v,b,(50.,50.),[('B:1','B',90.,50.)],(80.,50.))
    i,r=R.defender_baseline(v2,b2,scan(v2),{});assert i.kind=='position' and r['rb36']['anchor']==C.BALL
    assert abs(((i.aim[0]-80.)**2+(i.aim[1]-50.)**2)**.5-22.5)<1e-3


def test_satisfied_defender_keeps_his_intent_unless_the_aim_breaks_both():
    p=rb3();s,e,a,t=live(p);d=next(q.id for q in s.players.values() if q.team=='A' and q.role=='field' and q.active)
    v,b=defender_view(p,d);v,b=scene(v,b,(50.,50.),[('B:1','B',53.,50.)],(70.,50.))
    keep=replace(scan(v),kind='support',aim=(52.,51.));assert R.defender_baseline(v,b,keep,{})[0]==keep
    away=replace(scan(v),kind='position',aim=(10.,90.));i,_=R.defender_baseline(v,b,away,{})
    assert i.aim!=(10.,90.) and R._satisfies(i.aim,[x for x in b.tracks if x.team=='B'],(70.,50.),5.,25.)


def test_two_defenders_do_not_mark_the_same_attacker_when_another_is_free():
    p=rb3();s,e,a,t=live(p);d=next(q.id for q in s.players.values() if q.team=='A' and q.role=='field' and q.active)
    v,b=defender_view(p,d)
    v,b=scene(v,b,(50.,50.),[('B:1','B',58.,50.),('B:2','B',50.,60.),('A:9','A',59.,51.)],(95.,10.))
    i,_=R.defender_baseline(v,b,scan(v),{});assert i.kind=='mark' and i.target=='B:2'
    v3,b3=scene(v,b,(50.,50.),[('B:1','B',58.,50.),('A:9','A',59.,51.)],(95.,10.))
    i,_=R.defender_baseline(v3,b3,scan(v3),{});assert i.target=='B:1'                 # nobody else to mark


def test_freeze_recovery_feedback_retreats_and_the_port_accepts_it():
    p=rb3();s,e,a,t=live(p);q=next(x for x in s.players.values() if x.team=='A' and x.role=='field' and x.active)
    q.x,q.y=8.,40.;q.rb_recover=(8.,40.,s.now-5000)                  # thawed, recovery not done, in own zone
    v,b=defender_view(p,q.id);assert v.own_recovery_from_x==8.0
    i,r=R.defender_baseline(v,b,scan(v),{})
    assert r['rb36']=='freeze_recovery_retreat' and i.kind=='position' and i.aim==(round(8.-3.6,3),40.)
    behind=replace(v,x=4.,y=40.);k,r2=R.defender_baseline(behind,b,replace(scan(v),kind='position',aim=(25.,40.)),{})
    assert r2['rb36']=='freeze_recovery_exit_behind_line' and k.aim[0]<=8.-3.3+1e-6 and ((k.aim[0])**2+(k.aim[1]-50.)**2)**.5>20.
    fb=replace(b,own_feedback=(('x','rejected_freeze_recovery:position',v.delivered_ms),))
    j,_=R.defender_baseline(replace(v,own_recovery_from_x=None),fb,scan(v),{});assert j.aim[0]<v.x   # feedback-only fallback
    i=replace(i,decided_ms=s.now,period=s.period);assert p.submit(i)['status']=='accepted'
    fwd=replace(i,aim=(q.x+5.,q.y));assert p.submit(fwd)=={'status':'rejected','reason':'freeze_recovery'}


def test_existing_zone_exit_by_3s_is_kept_and_attackers_untouched():
    p=rb3();s,e,a,t=live(p);d=next(q.id for q in s.players.values() if q.team=='A' and q.role=='field' and q.active)
    v,b=defender_view(p,d);v,b=scene(v,b,(8.,50.),[],(9.,50.))                # ball near: leash holds
    v=replace(v,zone_elapsed_ms=3000);i,_=C.decide(v,b)
    assert i.kind=='position' and ((i.aim[0]-0.)**2+(i.aim[1]-50.)**2)**.5>20.     # leaves the zone
    att=replace(v,signals=replace(v.signals,passive_team='A'),zone_elapsed_ms=0)
    base=scan(att);assert R.defender_baseline(att,b,base,{})==(base,{})


def test_no_reentry_within_3s_unless_a_condition_holds_at_the_aim():
    p=rb3();s,e,a,t=live(p);d=next(q.id for q in s.players.values() if q.team=='A' and q.role=='field' and q.active)
    v,b=defender_view(p,d);v,b=scene(v,b,(24.,50.),[('B:1','B',27.,50.)],(60.,50.))
    v=replace(v,own_zone_exit_ms_ago=1000)
    into=replace(scan(v),kind='support',aim=(12.,50.))                         # satisfies nothing at the aim
    i,r=R.defender_baseline(v,b,into,{});assert r.get('rb36_reentry_block') or not C.in_own_zone('A',*i.aim,v)
    assert not C.in_own_zone('A',*i.aim,v)
    v2,b2=scene(v,b,(24.,50.),[('B:1','B',14.,50.)],(60.,50.));v2=replace(v2,own_zone_exit_ms_ago=1000)
    i,r=R.defender_baseline(v2,b2,scan(v2),{})                               # re-entry allowed: marking holds there
    assert i.target=='B:1' and C.in_own_zone('A',*i.aim,v2) and not r.get('rb36_reentry_block')


def test_switch_off_and_decisions_ignore_hidden_state():
    p=rb3(defender_baseline=False);s,e,a,t=live(p);d=next(q.id for q in s.players.values() if q.team=='A' and q.role=='field' and q.active)
    v,b=defender_view(p,d);v,b=scene(v,b,(50.,50.),[('B:1','B',59.,50.)],(90.,50.))
    assert R.defender_baseline(v,b,scan(v),{})==(scan(v),{})
    p=rb3();s,e,a,t=live(p);v,b=defender_view(p,d);v,b=scene(v,b,(50.,50.),[('B:1','B',59.,50.)],(90.,50.))
    before=C.decide(v,b)
    for q in s.players.values():q.x=q.y=-500.;q.rb_recover=None
    s.ball.x=s.ball.y=999.;e.rb35={}
    assert C.decide(v,b)==before


def test_live_time_baseline_share_is_measured():
    p=rb3();s,e,a=setup(p);player(s,'A',6.,50.)
    tick(p,100,10);s.game_ms=0;e.end_period()
    row=[r for r in e.log if r['event']=='zone_time_summary'][-1]['data']['teams']
    assert row['A']['baseline_satisfied_ms']<=row['A']['defender_ms'] and 'share_baseline_satisfied' in row['A'] and row['players']
