"""RB-3.4 PROVISIONAL owner rulings (17 Nov 2026): arrow legality judged at release;
dead-ball arrows inert and not charged; passive possession only (loose ball included);
frozen players are obstacles with a thaw contact buffer; RB/3 cognition adjustments."""
import pytest
from dataclasses import replace
from collections import Counter
from .port import RulebookPort
from .config import RulebookConfigV3
from .test_rb33 import control_rosters
from native import cognition as C
from native import cognition_rb3 as R


def rb3(buffer=1000):
    rosters=control_rosters()
    cfg=RulebookConfigV3(roster_digests=tuple(rosters[t].digest for t in ('A','B')),thaw_contact_buffer_ms=buffer)
    return RulebookPort(1,cfg,rosters=rosters)


def live(p,ball_status='carried'):
    s,e=p.m.s,p.m.e;T=p.types
    s.now=max(s.now,60000);s.phase=T.Phase.LIVE;e.hunt_cleared=True;e.rb_period_start_open=False;e.rb_hunt_running=True
    s.owner='B';e.possession.pp='B';e.possession.tc='B' if ball_status=='carried' else None;e.rb.possession='B'
    for q in s.players.values():
        if q.role!='archer':q.x,q.y,q.vx,q.vy=80.,90.,0.,0.
    t=next(q for q in s.players.values() if q.team=='B' and q.role=='field' and q.active)
    t.x,t.y=50.,50.
    carrier=next(q for q in s.players.values() if q.team=='B' and q.role=='field' and q.active and q is not t)
    if ball_status=='carried':
        carrier.x,carrier.y=60.,80.;s.ball=T.Ball(mode=T.BallMode.CONTROLLED,x=60.,y=80.,z=1.5,carrier=carrier.id,control_time=0,scoring=True,last_touch='B')
    else:
        s.ball=T.Ball(mode=T.BallMode.LOOSE,x=60.,y=80.,z=.1075,last_touch='B')
    e.native_seen=len(e.log)
    archer=next(q for q in s.players.values() if q.team=='A' and q.role=='archer' and q.active)
    return s,e,archer.id,t


def fly(p,steps=10):
    for _ in range(steps):
        for ev in p.m.advance_arrows(100):p.m.e.dispatch(ev)
        if not any(a.live for a in p.m.s.arrows):break


def fouls(e,reason=None):
    return [r for r in e.log if r['event']=='foul' and (reason is None or r['data'].get('reason')==reason)]


def test_config_carries_the_thaw_buffer_and_profiles_are_separate():
    assert RulebookConfigV3.__dataclass_fields__['thaw_contact_buffer_ms'].default==1000
    with pytest.raises(ValueError):rb3(-1)
    assert rb3().config.digest!=rb3(1500).config.digest


# ---- ruling 1: legality judged at release
def test_legal_at_release_then_target_enters_zone_is_late_inert_but_spent():
    p=rb3();s,e,a,t=live(p)
    assert e.shoot_arrow(a,t.id,(1,0,0)) and e.rb.quotas['A']['arrows']==1
    t.x,t.y=95.,50.                      # into a Keeper Zone before the arrow arrives
    ar=s.arrows[-1];ar.x,ar.y,ar.z=96.,50.,1.5;ar.vx,ar.vy,ar.vz=-250.,0.,0.
    fly(p)
    assert not t.frozen(s.now) and not fouls(e) and e.rb.quotas['A']['arrows']==1
    out=[r['data'] for r in e.log if r['event']=='arrow_outcome']
    assert out and out[-1]['outcome']=='inert' and out[-1]['late_reason']=='zone'


@pytest.mark.parametrize('late',['frozen','immune'])
def test_legal_at_release_then_target_frozen_or_immune_on_arrival_is_inert(late):
    p=rb3();s,e,a,t=live(p)
    assert e.shoot_arrow(a,t.id,(1,0,0))
    if late=='frozen':t.freeze_until=s.now+3000;t.immune_until=s.now+13000
    else:t.freeze_until=s.now-10;t.immune_until=s.now+5000
    ar=s.arrows[-1];ar.x,ar.y,ar.z=52.,50.,1.5;ar.vx,ar.vy,ar.vz=-250.,0.,0.
    before=t.freeze_until;fly(p)
    assert t.freeze_until==before and not fouls(e) and e.rb.quotas['A']['arrows']==1


@pytest.mark.parametrize('case,failed',[('zone',['in_zone']),('frozen',['target_frozen','target_immune']),
                                        ('immune',['target_immune']),('not_pp',['possession']),('teammate',['stale_target','possession'])])
def test_illegal_at_release_is_archery_target_with_diagnosis_and_spends(case,failed):
    p=rb3();s,e,a,t=live(p);target=t.id
    if case=='zone':t.x,t.y=95.,50.
    if case=='frozen':t.freeze_until=s.now+2000;t.immune_until=s.now+12000
    if case=='immune':t.immune_until=s.now+2000
    if case=='not_pp':e.possession.pp='A'
    if case=='teammate':target=next(q.id for q in s.players.values() if q.team=='A' and q.role=='field' and q.active)
    assert not e.shoot_arrow(a,target,(1,0,0))
    assert len(fouls(e,'archery_target'))==1 and e.rb.quotas['A']['arrows']==1
    d=[r['data'] for r in e.log if r['event']=='archery_target_diagnosis'][-1]
    assert d['failed']==failed and d['player']==a


# ---- ruling 2: dead-ball arrows
def test_dead_ball_release_is_inert_no_foul_not_charged():
    p=rb3();s,e,a,t=live(p);s.phase=p.types.Phase.DEAD
    assert e.shoot_arrow(a,t.id,(1,0,0)) is False
    assert not fouls(e) and e.rb.quotas['A']['arrows']==0 and not s.arrows
    assert [r['data']['reason'] for r in e.log if r['event']=='arrow_inert']==['dead_ball_release']


def test_arrow_in_flight_when_ball_goes_dead_is_inert_and_refunded():
    p=rb3();s,e,a,t=live(p)
    assert e.shoot_arrow(a,t.id,(1,0,0)) and e.rb.quotas['A']['arrows']==1
    e.award('B',50.,99.,'boundary',fresh=False,normalize=False)          # ball dead, B keeps the ball
    assert s.phase==p.types.Phase.DEAD and not any(x.live for x in s.arrows)
    assert e.rb.quotas['A']['arrows']==0 and not fouls(e)
    d=[r['data'] for r in e.log if r['event']=='arrow_inert'][-1]
    assert d['reason']=='dead_ball_in_flight' and d['refunded']
    fly(p);assert not t.frozen(s.now)                                     # it cannot freeze anyone later


# ---- ruling 3: passive possession only
def test_loose_ball_still_offence_possession_archer_may_shoot_and_freeze():
    p=rb3();s,e,a,t=live(p,'loose')
    assert e.possession.tc is None and e.shoot_arrow(a,t.id,(1,0,0))
    ar=s.arrows[-1];ar.x,ar.y,ar.z=52.,50.,1.5;ar.vx,ar.vy,ar.vz=-250.,0.,0.
    fly(p);assert t.frozen(s.now) and not fouls(e)


def test_cognition_accepts_loose_only_under_rb3():
    p=rb3();s,e,a,t=live(p,'loose');p.capture(s.now);s.now+=300
    v,b=p.view(a,s.now);tr=next(x for x in b.tracks if x.entity==t.id)
    sig=replace(v.signals,passive_team='B',ball_status='loose',phase='live')
    assert v.cognition=='native-rb/3'
    assert C.archer_target_legal(tr,replace(v,signals=sig,hunt_cleared=True),v.delivered_ms)
    for other in ('native-v0/2','native-v0/3'):
        assert not C.archer_target_legal(tr,replace(v,signals=sig,hunt_cleared=True,cognition=other),v.delivered_ms)


def test_archer_recheck_at_release_cancels_when_target_now_believed_protected():
    p=rb3();s,e,a,t=live(p);p.capture(s.now);s.now+=300
    v,b=p.view(a,s.now);tr=next(x for x in b.tracks if x.entity==t.id)
    sig=replace(v.signals,passive_team='B',ball_status='carried',phase='live')
    pend=dict(pending_command_id='cmd',pending_kind='draw_release',pending_target=t.id,pending_release_ms=v.delivered_ms,hunt_cleared=True,signals=sig)
    assert C.decide(replace(v,**pend),b)[0].kind=='release_arrow'
    for change in (dict(signals=replace(sig,immune=(t.id,))),dict(signals=replace(sig,passive_team='A'))):
        assert C.decide(replace(v,**{**pend,**change}),b)[0].kind=='abort_draw'
    zone=tuple(replace(x,x=95.,y=50.) if x.entity==t.id else x for x in b.tracks)
    assert C.decide(replace(v,**pend),replace(b,tracks=zone))[0].kind=='abort_draw'


# ---- ruling 4: frozen players are obstacles; thaw buffer
def test_frozen_player_is_an_obstacle_not_a_foul():
    p=rb3();s,e,a,t=live(p);d=next(q for q in s.players.values() if q.team=='A' and q.role=='field' and q.active)
    t.freeze_until=s.now+3000;t.immune_until=s.now+13000
    assert e.contact_legal(d,t,'block')==(True,'frozen_obstacle')
    assert e.contact_legal(d,t,'tackle')==(False,'frozen_obstacle')
    d.x,d.y=t.x-3.,t.y;old={d.id:(d.x,d.y)};d.x=t.x-.5
    assert not [ev for ev in p.m.player_contacts(100,old) if ev.kind=='foul']


@pytest.mark.parametrize('buffer',[1000,2500])
def test_immune_contact_only_inside_thaw_buffer(buffer):
    p=rb3(buffer);s,e,a,t=live(p);d=next(q for q in s.players.values() if q.team=='A' and q.role=='field' and q.active)
    d.x,d.y=t.x-1.,t.y;d.facing=(1.,0.);t.facing=(-1.,0.)
    t.freeze_until=s.now-1;t.immune_until=s.now+9999            # thawed 1 ms ago; arrow immunity 10 s
    assert e.contact_legal(d,t,'block')==(False,'immune_contact')
    s.now=t.freeze_until+buffer-1;assert e.contact_legal(d,t,'block')[1]=='immune_contact'
    s.now=t.freeze_until+buffer;assert e.contact_legal(d,t,'block')[1]!='immune_contact'
    assert s.now<=t.immune_until                                 # still arrow-immune, no contact protection


def test_foul_class_frozen_victim_not_major_thaw_buffer_victim_major():
    p=rb3();s,e,a,t=live(p);d=next(q for q in s.players.values() if q.team=='A' and q.role=='field' and q.active)
    t.freeze_until=s.now+3000;t.immune_until=s.now+13000
    e.foul(d.id,t.id,'holding');assert fouls(e)[-1]['data']['major'] is False
    p=rb3();s,e,a,t=live(p);d=next(q for q in s.players.values() if q.team=='A' and q.role=='field' and q.active)
    t.freeze_until=s.now-200;t.immune_until=s.now+9800
    e.foul(d.id,t.id,'holding');assert fouls(e)[-1]['data']['major'] is True


def test_rb2_keeps_the_previous_contact_rules():
    """Documents today's behaviour (RB/2): frozen contact is a foul and immune_contact lasts the
    whole immunity window (10 s after thaw), both major."""
    p=RulebookPort(1);s,e,a,t=live(p);d=next(q for q in s.players.values() if q.team=='A' and q.role=='field' and q.active)
    d.x,d.y=t.x-1.,t.y;t.freeze_until=s.now+3000;t.immune_until=s.now+13000
    assert e.contact_legal(d,t,'block')==(False,'frozen_contact')
    s.now=t.freeze_until+9000;assert e.contact_legal(d,t,'block')==(False,'immune_contact')


# ---- RB/3 cognition: frozen obstacles in path planning
def test_detour_steers_around_a_frozen_body_and_leaves_clear_paths_alone():
    T=C.Track
    o=T('B4','B','field',50.,50.,0.,0.,0)
    aim,who=R.detour(40.,50.,(60.,50.),[o]);assert who=='B4' and abs(aim[1]-50.)>=R.SIDESTEP_M-1e-6
    aim2,who2=R.detour(40.,50.,(60.,60.),[T('B4','B','field',50.,45.,0.,0.,0)]);assert who2 is None and aim2==(60.,60.)


def test_no_press_or_tackle_on_a_believed_frozen_player():
    p=rb3();s,e,a,t=live(p);p.capture(s.now);s.now+=300
    d=next(q for q in s.players.values() if q.team=='A' and q.role=='field' and q.active)
    v,b=p.view(d.id,s.now)
    v=replace(v,status_indicators=((t.id,'red'),))
    b=replace(b,tracks=b.tracks+(C.Track(t.id,'B','field',t.x,t.y,0.,0.,v.delivered_ms),) if not any(x.entity==t.id for x in b.tracks) else b.tracks)
    i=C.ActionIntent('i','d',d.id,'tackle',t.id,(t.x,t.y),None,None,v.delivered_ms,contact='takedown')
    out,rec=R.adjust(v,b,i,{})
    assert out.kind=='position' and out.contact is None and rec['rb3_no_contact_on_frozen']==t.id


# ---- diagnosis fields
def test_zone_unmarked_diagnosis_fields():
    p=rb3();s,e,a,t=live(p);d=next(q for q in s.players.values() if q.team=='A' and q.role=='field' and q.active)
    e.foul(d.id,reason='zone_unmarked')
    z=[r['data'] for r in e.log if r['event']=='zone_unmarked_diagnosis'][-1]
    assert z['actor']==d.id and z['actor_role']=='field' and z['eligible_field_defenders']>=1 and z['short_after_dqs'] is False and z['team_dqs']==0
