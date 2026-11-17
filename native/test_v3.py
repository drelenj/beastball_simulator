"""native-v0/3 (FAB-1) conformance. native-v0/2 behaviour is covered by test_rules.py
and must stay byte-identical; these tests cover only what v0/3 changes.
"""
from dataclasses import replace
import math
import pytest
from .config import NativeConfig, NativeConfigV3, config_for, is_v3
from .port import NativePort
from . import cognition as C

V2_DIGEST='f31b44a1eb787f14c9d606be74fa40658c6b7b9772ee1e882b075b856edc3035'


def live(p):
    s=p.m.s;e=p.m.e;T=p.types
    s.now=1000;s.phase=T.Phase.LIVE;s.owner='A';s.ball=T.Ball(mode=T.BallMode.CONTROLLED,x=50,y=50,z=1.58,carrier='A0',control_time=0,scoring=True,last_touch='A')
    s.players['A0'].x=50;s.players['A0'].y=50
    e.hunt_cleared=True;e.native_seen=len(e.log)
    e.possession.step(0,{'A0':'A'},(50,50),[{'kind':'live'}],(50,50));e.possession.step(1000,{'A0':'A'},(50,50),[],(50,50))
    return p

@pytest.fixture
def port3():
    return live(NativePort(1,NativeConfigV3()))

@pytest.fixture
def port2():
    return live(NativePort(1))


def clear_field(port,keep=()):
    """Park every non-archer athlete far from the test lane."""
    for i,q in enumerate(port.m.active_field()):
        if q.id not in keep:
            q.x=3.+2.*(i//2);q.y=97. if q.team=='A' else 3.;q.vx=q.vy=0.
            q.target=(q.x,q.y);port.move[q.id]=(q.x,q.y)


# ---------------------------------------------------------------- FAB-1a
def test_v2_config_digest_is_frozen_and_default():
    assert NativeConfig().digest==V2_DIGEST and NativeConfig().version=='native-v0/2'
    assert config_for().digest==V2_DIGEST and not is_v3(NativeConfig())
    assert 'arrow_speed_ratio' not in NativeConfig().record()
    assert NativePort(1).config.version=='native-v0/2'


def test_v3_arrow_speed_is_a_ratio_of_fastest_player_and_has_no_cap():
    c=NativeConfigV3();assert c.version=='native-v0/3' and is_v3(c) and c.digest!=V2_DIGEST
    assert c.fastest_player_speed==27. and c.arrow_speed==250.
    assert c.arrow_speed_ratio==pytest.approx(250/27) and c.arrow_speed_cap is None
    assert dict(c.body_standards)['archery_release_speed']==250.
    assert dict(c.pocket_settings)['arrow_speed']==250. and 'arrow_limit' not in dict(c.pocket_settings)
    # trivially changeable: one number
    d=config_for('native-v0/3',arrow_speed_ratio=5.59);assert d.arrow_speed==pytest.approx(150.93)
    assert dict(d.body_standards)['archery_release_speed']==d.arrow_speed and d.digest!=c.digest
    with pytest.raises(ValueError):NativeConfigV3(arrow_speed_cap=30.)
    with pytest.raises(ValueError):NativeConfigV3(arrow_speed_ratio=0.)
    with pytest.raises(ValueError):NativeConfigV3(period_seconds=60)
    with pytest.raises(ValueError):NativeConfigV3(version='native-v0/2')
    with pytest.raises(ValueError):NativeConfigV3(pocket_settings=NativeConfig().pocket_settings)


def test_v3_effective_readback_and_archer_release_speed(port3):
    assert port3.arrow_speed==250. and port3.verify_effective()['pocket_settings']['arrow_speed']==250.
    assert all(p.a.archery_release_speed==250. for p in port3.m.s.players.values())
    assert NativePort(1).arrow_speed==29.


def legal_target(port,x=50.,y=50.):
    s=port.m.s;t=s.players['A0'];t.x=x;t.y=y;t.vx=t.vy=0.;s.ball.x=x;s.ball.y=y
    port.m.e.native_sync();return t


def test_v3_no_speed_foul_at_250_and_v2_cap_retained(port3,port2):
    for port,expect in ((port3,True),(port2,False)):
        e,s=port.m.e,port.m.s;legal_target(port);minors=s.players['B11'].minor_count
        ar=e.shoot_arrow('B11','A0',(-250.,0.,0.))
        assert bool(ar) is expect
        assert s.players['B11'].minor_count==minors+(0 if expect else 1)
    assert not any(r['event']=='foul' and r['data'].get('reason')=='arrow_speed' for r in port3.m.e.log)
    assert any(r['event']=='foul' and r['data'].get('reason')=='arrow_speed' for r in port2.m.e.log)
    # still no cap far above canon speed
    legal_target(port3);assert port3.m.e.shoot_arrow('B11','A0',(-900.,0.,0.))


def fly(port,arrow_xyz,velocity,step_ms):
    m=port.m;T=port.types
    ar=T.Arrow(99,'B','B11','A0',*arrow_xyz,*velocity,arrow_xyz,m.s.now);m.s.arrows[:]=[ar]
    events=[]
    for _ in range(0,400,step_ms):
        events+=m.advance_arrows(step_ms)
        if events or not ar.live:break
    return ar,events


@pytest.mark.parametrize('distance',[0.3,3.,12.4,24.9,25.1,37.,49.9,60.])
@pytest.mark.parametrize('lateral',[0.,.3])
def test_v3_arrow_swept_collision_does_not_tunnel(port3,distance,lateral):
    """A 250 m/s arrow covers 25 m per 100 ms step; a body anywhere along the
    swept segment (including across step boundaries) must be struck."""
    clear_field(port3,('A0',));t=port3.m.s.players['A0'];t.x=20.;t.y=50.+lateral;t.z=0.
    port3.m.s.ball.carrier='A0'
    ar,events=fly(port3,(20.+distance,50.,1.5),(-250.,0.,0.),100)
    assert [(e.kind,e.target) for e in events]==[('impact','A0')]
    assert abs(ar.x-20.)<=t.radius+.05 and events[0].data['panel']


def test_v3_arrow_swept_collision_respects_radius_height_and_order(port3):
    clear_field(port3,('A0','A1'));s=port3.m.s;t=s.players['A0'];u=s.players['A1'];s.ball.carrier='A0'
    t.x,t.y,t.z=20.,50.,0.;u.x,u.y,u.z=5.,95.,0.
    miss=t.radius+.045+.02
    ar,events=fly(port3,(40.,50.+miss,1.5),(-250.,0.,0.),100);assert not events          # just outside the body
    ar,events=fly(port3,(40.,50.,t.a.height+.3),(-250.,0.,5.),100);assert not events        # above the head
    u.x,u.y=30.,50.                                                                         # nearer body is hit first
    ar,events=fly(port3,(40.,50.,1.5),(-250.,0.,0.),100);assert [e.target for e in events]==['A1']


def test_v3_arrow_hit_is_independent_of_step_length(port3):
    clear_field(port3,('A0',));t=port3.m.s.players['A0'];t.x,t.y,t.z=20.,50.,0.;port3.m.s.ball.carrier='A0'
    hits=[]
    for step in (100,50,10,1):
        ar,events=fly(port3,(71.3,50.2,1.4),(-250.,0.,2.),step)
        assert [e.target for e in events]==['A0'];hits.append((ar.x,ar.y,ar.z))
    # Same body is struck at every step length. The recorded stop point is the
    # closest approach inside the body (coarse steps) or the first sample inside
    # it (fine steps): it may differ by less than one body radius, height by < 1 cm.
    assert all(math.hypot(h[0]-20.,h[1]-50.)<=t.radius+.05 for h in hits)
    assert max(abs(h[2]-hits[-1][2]) for h in hits)<.01


def test_v3_arrow_strikes_loose_ball_and_drag_and_gravity_apply(port3):
    clear_field(port3);s=port3.m.s;T=port3.types
    s.ball=T.Ball(mode=T.BallMode.LOOSE,x=30.,y=50.,z=1.5)
    ar,events=fly(port3,(47.,50.,1.5),(-250.,0.,0.),100)
    assert [e.target for e in events]==['ball']
    s.ball=T.Ball(mode=T.BallMode.LOOSE,x=30.,y=5.,z=.1075)
    ar=T.Arrow(98,'B','B11',None,90.,50.,6.84,-250.,0.,0.,(90.,50.,6.84),s.now);s.arrows[:]=[ar]
    port3.m.advance_arrows(100)
    assert ar.x==pytest.approx(65.) and ar.z==pytest.approx(6.84-.5*9.81*.01)
    assert ar.vx==pytest.approx(-250.*math.exp(-.06*.1)) and ar.vz<0


def test_v3_archer_motor_releases_at_config_speed_and_freezes_static_target(port3):
    """End to end: draw intent -> release intent from decide() -> motor -> flight -> freeze."""
    s,e=port3.m.s,port3.m.e;clear_field(port3,('A0',));p=s.players['B11'];t=legal_target(port3,45.,40.)
    i=C.ActionIntent('draw','d',p.id,'draw_release',t.id,(45.,40.),(0,0),None,s.now)
    assert port3.submit(i)['status']=='accepted'
    s.now+=1000;port3.capture(s.now);s.now+=300;v,b=port3.view(p.id,s.now)
    release,rec=C.decide(v,b);assert release.kind=='release_arrow'
    assert port3.submit(release)['status']=='accepted';port3.archer_motor()
    ar=s.arrows[-1];assert math.sqrt(ar.vx**2+ar.vy**2+ar.vz**2)==pytest.approx(250.)
    for _ in range(10):
        for ev in port3.m.advance_arrows(100):port3.m.e.dispatch(ev)
        if not ar.live:break
    assert t.frozen(s.now) and any(r['event']=='freeze' and r['data']['player']=='A0' for r in e.log)
    assert not any(r['event']=='foul' for r in e.log)


# ---------------------------------------------------------------- FAB-1b
from collections import Counter
from dataclasses import asdict
import ast
import json
from pathlib import Path
from . import cognition_v3 as C3


def intent(port,pid,kind,target=None,aim=None,contact=None,tag='t'):
    s=port.m.s
    return C.ActionIntent(f'{pid}/{tag}/{s.now}/intent',f'{pid}/{tag}/{s.now}',pid,kind,target,aim,None,None,s.now,contact=contact,period=s.period)


def duel(port,defender,carrier=None,steps=40):
    """Carrier A0 runs at defender B0. Contact choices are scripted intents; the
    engine alone decides reach, legality, grip, balance and grounding."""
    s=port.m.s;clear_field(port,('A0','B0'));a,b=s.players['A0'],s.players['B0']
    a.x,a.y,a.vx,a.vy=40.,50.,0.,0.;b.x,b.y=52.,50.;s.ball.x,s.ball.y=40.,50.
    for n in range(steps):
        if n%5==0:
            assert port.submit(intent(port,'A0','carry',None,(90.,50.),carrier,n))['status']=='accepted'
            assert port.submit(intent(port,'B0','tackle' if defender=='takedown' else 'press','A0',(a.x,a.y),defender,n))['status']=='accepted'
        port.step()
        if s.restart:break
    return Counter(r['event'] for r in port.m.e.log)


def test_v3_takedown_intent_grounds_carrier_through_engine_physics(port3):
    ev=duel(port3,'takedown');s=port3.m.s
    assert ev['c3_hold_start']==1 and ev['c3_grounding']==1 and ev['tackle_count']==1
    assert s.restart.reason=='first_tackle' and s.restart.kind=='scrim' and s.tackle_count==1
    assert s.restart.rs['snapper']=='A0' and s.restart.rs['tackler']=='B0'
    g=next(r['data'] for r in port3.m.e.log if r['event']=='c3_grounding')
    assert g['cls']=='tackle_under_hold' and g['manner']=='defence_driven' and g['credited']=='B0'


def test_v3_no_contact_intent_means_no_hold_and_no_takedown(port3):
    ev=duel(port3,None)
    assert ev['c3_collision']>=1          # bodies still meet
    assert not ev['c3_hold_start'] and not ev['tackle_count'] and not ev['c3_grounding']
    assert port3.m.s.restart is None and port3.m.s.ball.carrier=='A0'


def test_v3_wrap_intent_holds_without_driving_down(port3):
    ev=duel(port3,'wrap')
    assert ev['c3_hold_start']>=1 and ev['c3_containment']>=1
    assert not ev['tackle_count'] and not ev['c3_grounding']
    ends=[r['data'] for r in port3.m.e.log if r['event']=='c3_hold_end']
    assert all(e['contained_ms']>0 for e in ends if e['peak_grip']>=.3)


def test_v3_escape_effort_is_the_carriers_own_run_through_intent(port3):
    duel(port3,'takedown','run_through')
    fought=[r['data'] for r in port3.m.e.log if r['event']=='c3_hold_end']
    assert fought and all(e['escape_effort_ms']>0 for e in fought)
    quiet=live(NativePort(1,NativeConfigV3()));duel(quiet,'takedown',None)
    assert all(r['data']['escape_effort_ms']==0 for r in quiet.m.e.log if r['event']=='c3_hold_end')
    braced=live(NativePort(1,NativeConfigV3()));duel(braced,'takedown','brace')
    assert all(r['data']['escape_effort_ms']==0 for r in braced.m.e.log if r['event']=='c3_hold_end')


def test_v3_engine_contact_controllers_read_only_athlete_intents(port3,port2):
    m=port3.m;s=m.s;d,car=s.players['B0'],s.players['A0']
    for contact,auth,contain in ((None,False,True),('wrap',True,True),('takedown',True,False),('head',False,True)):
        d.native_intent=intent(port3,'B0','tackle','A0',(50.,50.),contact)
        assert m.native_wrap_authorized(d,car) is auth and m.c3_contain(d,car) is contain
    d.native_intent=intent(port3,'B0','tackle','A1',(50.,50.),'takedown')     # aimed at somebody else
    assert not m.native_wrap_authorized(d,car)
    for kind,contact,windup,effort in (('carry','run_through',None,1.),('carry','brace',None,0.),('carry','dodge',None,0.),
                                       ('carry',None,None,0.),('pass','run_through',None,0.),('carry','run_through',(0,'pass'),0.)):
        car.native_intent=intent(port3,'A0',kind,None,(60.,50.),contact)
        assert m.c3_escape_effort(car,windup)==effort
    del car.native_intent;assert m.c3_escape_effort(car,None)==0.            # no intent: no effort
    # automatic descent stays off; nothing but an intent can ground a carrier on purpose
    assert m.c3_fix_descent is False and not m.c3_descend(car)
    # native-v0/2 keeps its original controllers
    assert port2.m.c3_fix_contain is False and port2.m.c3_escape_effort(port2.m.s.players['A0'],None)==1.
    assert port2.submit(intent(port2,'B0','tackle','A0',(50.,50.),'takedown'))=={'status':'rejected','reason':'unknown_kind'}


def scene(port,defender_xy=(54.,50.),facing=(-1.,0.)):
    """A0 carries at midfield, A1 in support, B0 the only opponent in view."""
    s=port.m.s;clear_field(port,('A0','A1','B0'));a,b,c=s.players['A0'],s.players['B0'],s.players['A1']
    a.x,a.y=50.,50.;c.x,c.y=44.,58.;b.x,b.y=defender_xy;b.facing=facing;a.facing=(1.,0.)
    s.ball.x,s.ball.y=50.,50.
    port.capture(s.now);s.now+=300
    return port


def test_v3_defender_decision_commits_to_takedown_inside_believed_gap(port3):
    scene(port3);v,b=port3.view('B0',port3.m.s.now);i,rec=C.decide(v,b)
    assert v.cognition=='native-v0/3' and (i.kind,i.contact,i.target)==('tackle','takedown','A0')
    assert rec['contact_selected']=='takedown' and rec['believed_gap']<C3.TACKLE_COMMIT_M
    assert {o[4] for o in rec['contact_options']}=={'wrap','takedown'}
    assert port3.submit(i)['status']=='accepted' and port3.move['B0']==i.aim
    # the same athlete under native-v0/2 keeps the old press/wrap intent
    i2,_=C.decide(replace(v,cognition='native-v0/2'),b);assert (i2.kind,i2.contact)==('press','wrap')


def test_v3_defender_far_from_carrier_only_presses(port3):
    scene(port3,(62.,50.));v,b=port3.view('B0',port3.m.s.now);i,rec=C.decide(v,b)
    assert i.kind=='press' and i.contact=='wrap' and rec['believed_gap']>C3.TACKLE_COMMIT_M


def test_v3_defender_never_tackles_a_carrier_he_does_not_believe_in(port3):
    """No true-state fallback: the true carrier is beside him, but he has no track of him."""
    scene(port3);v,b=port3.view('B0',port3.m.s.now)
    blind=tuple(t for t in v.tracks if t.entity not in ('A0',C.BALL))
    v=replace(v,tracks=blind);b=replace(b,tracks=blind,ball_course=None)
    i,_=C.decide(v,b);assert i.kind!='tackle' and i.contact is None
    # and a protected Keeper is never a takedown target
    scene(port3);v,b=port3.view('B0',port3.m.s.now)
    rec={'believed_carrier':['A0','A']}
    keeper=tuple(replace(t,role='keeper',x=5.,y=50.) if t.entity=='A0' else t for t in b.tracks)
    v=replace(v,signals=replace(v.signals,passive_team='A'))
    out,_=C3.defender_contact(v,replace(b,tracks=keeper),intent(port3,'B0','press','A0',(5.,50.),'wrap'),rec)
    assert out.kind=='press' and out.contact is None


def carrier_view(port,**own):
    v,b=port.view('A0',port.m.s.now)
    return replace(v,**own),b


def test_v3_carrier_decision_dodge_run_through_and_brace(port3):
    base=C.ActionIntent('i','d','A0','carry',None,(60.,50.),None,None,port3.m.s.now)
    scene(port3,(58.,50.));v,b=carrier_view(port3)
    def threat(vx,x=58.,y=50.):
        tr=tuple(replace(t,x=x,y=y,vx=vx,vy=0.) if t.entity=='B0' else t for t in b.tracks)
        return replace(v,tracks=tr),replace(b,tracks=tr)
    # warned in time: dodge to the side the threat is not on (aim leaves the straight line)
    v1,b1=threat(-10.,58.,50.4);i,rec=C3.carrier_contact(v1,b1,base,{})
    assert i.contact=='dodge' and i.aim[1]<50. and rec['believed_threats'][0][1]=='B0'
    # no warning: run through, original aim kept
    v2,b2=threat(-20.,52.,50.);i,rec=C3.carrier_contact(v2,b2,base,{})
    assert i.contact=='run_through' and i.aim==base.aim
    # no believed threat and not held: decision unchanged
    v3,b3=threat(+5.,80.,50.);i,rec=C3.carrier_contact(v3,b3,base,{'x':1})
    assert i is base and rec=={'x':1}
    # held: fights the grip while balance allows, braces when nearly down
    i,rec=C3.carrier_contact(replace(v3,own_held=1,own_balance_load=.2),b3,base,{})
    assert i.contact=='run_through' and rec['own_held']==1
    i,rec=C3.carrier_contact(replace(v3,own_held=1,own_balance_load=.9),b3,base,{})
    assert i.contact=='brace' and i.aim==(round(v.x,3),round(v.y,3))
    # through decide(): only a field carrier who is carrying gets a contact response
    i,_=C.decide(replace(v2,own_held=1),b2)
    assert i.contact in (None,'run_through','brace','dodge') and (i.kind=='carry')==(i.contact is not None)


def test_v3_own_contact_view_fields_are_own_body_only(port3):
    scene(port3);m=port3.m
    m.c3_holds[('B0','A0')]={'actor':'B0','target':'A0','g':.4,'region':'lower'};m.s.players['A0'].bal_src={('hold','B0',True):.35}
    va,_=port3.view('A0',m.s.now);vb,_=port3.view('B0',m.s.now);vc,_=port3.view('A1',m.s.now)
    assert (va.own_held,va.own_balance_load,va.own_hold_target)==(1,.35,None)
    assert (vb.own_held,vb.own_hold_target)==(0,'A0')
    assert (vc.own_held,vc.own_balance_load,vc.own_hold_target)==(0,0.,None)   # nobody else's contact state
    m.c3_holds.clear()
    names={f for f in C.AthleteView.__dataclass_fields__}
    assert {'cognition','own_held','own_balance_load','own_hold_target'}<=names


def test_v3_poison_hidden_state_cannot_change_new_decisions(port3):
    """Decisions depend on the delivered view and belief only."""
    scene(port3);s=port3.m.s
    views={pid:port3.view(pid,s.now) for pid in ('A0','B0','A1')}
    before={pid:C.decide(v,b) for pid,(v,b) in views.items()}
    for p in s.players.values():                       # poison true state after delivery
        p.x=-999.;p.y=-999.;p.vx=77.;p.a.strength=0.;p.a.tackling=1.;p.posture='hidden-sentinel';p.native_intent=None
    s.ball.x=s.ball.y=9999.;s.ball.carrier='B7';port3.m.c3_holds[('B5','A0')]={'actor':'B5','target':'A0','g':1.,'region':'upper'}
    s.tackle_count=1;port3.move.clear()
    assert {pid:C.decide(v,b) for pid,(v,b) in views.items()}==before
    # the view is plain data: it survives a JSON round trip and replays the same decision
    for pid,(v,b) in views.items():
        blob=json.loads(json.dumps(C.view_to_json(v,b)))
        assert C.decide(*C.view_from_json(blob))==before[pid]


def test_v3_poison_hidden_attributes_before_capture_leave_views_identical():
    def build(poison):
        p=scene(live(NativePort(1,NativeConfigV3())));s=p.m.s
        if poison:
            for q in s.players.values():
                q.a.strength=.01;q.a.tackling=.99;q.a.balance=.01;q.fatigue=.2;q.target=(1.,1.);q.next_decision=10**9
                q.native_intent='poison'
            p.move.clear()
        s.now+=200;p.capture(s.now);s.now+=300
        return {pid:p.view(pid,s.now) for pid in ('A0','B0')}
    clean,dirty=build(False),build(True)
    for pid in clean:
        (v1,b1),(v2,b2)=clean[pid],dirty[pid]
        assert asdict(v1)==asdict(v2) and b1==b2 and C.decide(v1,b1)==C.decide(v2,b2)


def test_v3_cognition_module_is_pure(port3):
    tree=ast.parse(Path(C3.__file__).read_text())
    modules={n.module for n in ast.walk(tree) if isinstance(n,ast.ImportFrom)}|{a.name for n in ast.walk(tree) if isinstance(n,ast.Import) for a in n.names}
    assert modules<={'dataclasses','math','cognition',None} and not any(m and ('port' in m or 'engine' in m or 'rules' in m or 'substrate' in m) for m in modules)
    names={n.id for n in ast.walk(tree) if isinstance(n,ast.Name)}|{n.attr for n in ast.walk(tree) if isinstance(n,ast.Attribute)}
    assert not names&{'players','c3_holds','native_intent','quivers','engine','possession','random','rng'}


def drive(port,steps):
    """The run_match loop on a prepared port."""
    s=port.m.s;next_dec={};next_sense=0;P=port.types.Phase
    for _ in range(steps):
        now=s.now
        if s.phase==P.FINAL:break
        if now>=next_sense:port.capture(now);next_sense=now+port.config.sense_ms
        for pid in port.active_ids():
            if now<next_dec.get(pid,0):continue
            v,b=port.view(pid,now)
            if v is None:continue
            i,rec=C.decide(v,b);a=port.submit(i)
            if a['status']=='rejected':port.feedback.setdefault(pid,[]).append((i.intent_id+'/rejected','rejected_'+a.get('reason','unknown')+':'+i.kind,now))
            next_dec[pid]=now+port.config.decision_ms
        port.m.pending_break=[];port.step()


@pytest.fixture(scope='module')
def played():
    """One 3000-step native-v0/3 window of ordinary play (about 5 minutes of match time)."""
    from .run import run_match
    return run_match(1,NativeConfigV3(),max_steps=3000)


def test_v3_play_every_hold_and_tackle_traces_to_a_decide_intent(played):
    result,port=played;log=port.m.e.log
    by_id={i.intent_id:i for i in port.intents}
    assert all(cmd.intent.intent_id in by_id and cmd.command_id.startswith(cmd.intent.intent_id) for cmd in port.command_log)
    timeline={}
    for i in port.intents:timeline.setdefault(i.athlete,[]).append(i)
    def latest(pid,t):
        return next((i for i in reversed(timeline.get(pid,())) if i.decided_ms<=t),None)
    holds=[r for r in log if r['event']=='c3_hold_start'];tackles=[r for r in log if r['event']=='tackle_count']
    assert holds and tackles                                         # coverage: they occur in play
    for r in holds:
        i=latest(r['data']['actor'],r['t_ms'])
        assert i is not None and i.contact in ('wrap','takedown') and i.target==r['data']['target']
    for r in tackles:
        assert any(i.athlete==r['data']['actor'] and i.contact=='takedown' and i.target==r['data']['target']
                   and r['t_ms']-4000<=i.decided_ms<=r['t_ms'] for i in port.intents)
    assert not port.m.stats.get('c3_descents_attempted')             # no automatic descent
    assert result['contact_intents'].keys()<={'wrap','takedown','run_through','brace','dodge'}
    assert not any(i.kind=='kick' for i in port.intents)


# ---------------------------------------------------------------- FAB-1c
from .restart_metric import RestartMetric, travel_ms


def restart_view(port,pid,**changes):
    s=port.m.s;port.capture(s.now);s.now+=300
    v,b=port.view(pid,s.now)
    if changes:v=replace(v,**changes)
    return v,b


def toss(port,x=30.,team='A'):
    e,s=port.m.e,port.m.s;clear_field(port)
    r=e.award(team,x,0.,'boundary',normalize=False);assert r.kind=='toss'
    return r


def put(port,pid,x,y):
    q=port.m.s.players[pid];q.x,q.y=x,y;q.vx=q.vy=0.;q.target=(x,y);port.move[pid]=(x,y);return q


def test_v3_restart_claim_goes_to_the_believed_nearest_not_the_first_to_decide(port3):
    r=toss(port3);tx,ty=r.taker_spot
    put(port3,'A0',80.,60.);put(port3,'A5',32.,6.)                      # A0 decides first, A5 is near
    for q in (port3.m.s.players['A0'],port3.m.s.players['A5']):q.facing=(-1.,-.2)
    far,bf=restart_view(port3,'A0');near,bn=port3.view('A5',port3.m.s.now)
    assert C.decide(far,bf)[0].kind=='restart_position'                 # holds back
    i,rec=C.decide(near,bn);assert i.kind=='restart_claim' and rec['path']=='restart_claim_believed_nearest'
    # v0/2 placeholder: the first athlete to decide claims wherever he is
    assert C.decide(replace(far,cognition='native-v0/2'),bf)[0].kind=='restart_claim'
    # own distance delays an athlete's own claim even when he sees nobody nearer
    alone=tuple(t for t in bf.tracks if t.team!='A')
    early=replace(far,tracks=alone);assert not C3._claim(early,replace(bf,tracks=alone),tx,ty,r.created_at,None)
    late=replace(early,delivered_ms=r.created_at+int(100*C3.CLAIM_BACKOFF_MS_PER_M))
    assert C3._claim(late,replace(bf,tracks=tuple(replace(t,captured_ms=late.delivered_ms) for t in alone)),tx,ty,r.created_at,None)
    # a mandatory snapper is the only claimant
    v=replace(near,restart=near.restart[:8]+('A0',)+near.restart[9:])
    assert C.decide(v,bn)[0].kind=='restart_position'
    assert C.decide(replace(far,restart=v.restart),bf)[0].kind=='restart_claim'
    assert port3.submit(i)['status']=='accepted' and port3.m.s.restart.taker=='A5'


def taker_at_spot(port,r,pid='A5'):
    q=put(port,pid,*r.taker_spot);r.taker=pid;q.facing=(0.,1.) if r.kind=='toss' else (-float(port.m.s.attack_sign(r.team)),0.);return pid


def test_v3_toss_taker_throws_to_a_believed_teammate_at_legal_distance(port3):
    r=toss(port3);taker_at_spot(port3,r)
    put(port3,'A1',r.x+1.2,1.3);put(port3,'A2',r.x+3.,12.);put(port3,'A3',r.x-15.,20.);put(port3,'B0',r.x,9.)
    port3.m.s.now=r.created_at+1400
    v,b=restart_view(port3,'A5');i,rec=C.decide(v,b)
    assert i.kind=='restart_pass' and i.target in ('A2','A3') and rec['path']=='restart_taker_throw'
    targets={o[1] for o in rec['options'] if o[0]=='restart_pass'}
    assert 'A1' not in targets                                           # too close to throw to (v0/2 geometry cause)
    aim=next(t for t in b.tracks if t.entity==i.target);assert i.aim==(round(aim.x,3),round(aim.y,3))
    assert port3.submit(i)['status']=='accepted'                         # geometry admitted
    # v0/2 picked the nearest teammate and was refused on geometry
    i2,_=C.decide(replace(v,cognition='native-v0/2',restart=v.restart[:-1]+(True,)),b)
    assert i2.target=='A1'
    fresh=live(NativePort(1,NativeConfigV3()));r2=toss(fresh);taker_at_spot(fresh,r2);put(fresh,'A1',r2.x+.6,.7)
    assert fresh.submit(replace(i2,decided_ms=fresh.m.s.now,record_id=r2.native_id,aim=(r2.x+.6,.7)))=={'status':'rejected','reason':'geometry'}
    # the throw just refused is not chosen again while another target exists
    refused=replace(b,own_feedback=(('x','rejected_geometry:restart_pass',v.delivered_ms),))
    j,_=C.decide(v,refused);assert j.kind=='restart_pass' and j.target!=i.target


def test_v3_toss_taker_waits_for_legal_release_then_uses_space_placeholder(port3):
    r=toss(port3);taker_at_spot(port3,r);put(port3,'A2',r.x+3.,12.)
    v,b=restart_view(port3,'A5')                                          # before the 1.5 s minimum
    assert C.decide(v,b)[0].kind=='restart_wait'
    put(port3,'B0',r.x+.5,2.);port3.m.s.now=r.created_at+2000              # believed opponent inside 3 m
    v,b=restart_view(port3,'A5');i,rec=C.decide(v,b)
    assert i.kind=='restart_wait' and rec['path']=='restart_taker_waits_for_legal_release'
    put(port3,'B0',r.x+20.,40.);v,b=restart_view(port3,'A5')
    assert C.decide(v,b)[0].kind=='restart_pass'
    # away from the spot the taker first goes to it
    put(port3,'A5',r.x+10.,10.);v,b=restart_view(port3,'A5');i,_=C.decide(v,b)
    assert i.kind=='restart_position' and i.aim==tuple(r.taker_spot)
    # nobody believed available: wait, and only at the last call throw to legal space (PLACEHOLDER)
    taker_at_spot(port3,r);put(port3,'A2',r.x+60.,80.);v,b=restart_view(port3,'A5')
    none=tuple(t for t in b.tracks if t.team!='A');v,b=replace(v,tracks=none),replace(b,tracks=none)
    assert C.decide(v,b)[0].kind=='restart_wait'
    last=replace(v,restart=v.restart[:10]+(v.delivered_ms-C3.TOSS_WINDOW_MS+1000,)+v.restart[11:])
    i,rec=C.decide(last,b);assert i.kind=='restart_pass' and i.target is None and rec['path']=='restart_taker_space_placeholder'
    assert 1.<=i.aim[0]<=99. and 1.<=i.aim[1]<=99.


def test_v3_snap_taker_waits_for_the_set_signal(port3):
    e,s=port3.m.e,port3.m.s;clear_field(port3);r=e.award('A',50.,50.,'turnover',fresh=True,normalize=False)
    assert r.kind=='scrim';taker_at_spot(port3,r);put(port3,'A2',r.x-8.,56.);put(port3,'B0',r.x+6.,50.)
    v,b=restart_view(port3,'A5');assert v.restart[-1] is False
    assert C.decide(v,b)[0].kind=='restart_wait'
    ready=replace(v,restart=v.restart[:-1]+(True,));i,_=C.decide(ready,b)
    assert i.kind=='restart_pass' and i.target=='A2'
    # near the deadline with own team believed onside he snaps anyway (a defender still offside is the defence's risk)
    late=replace(v,restart=v.restart[:10]+(v.delivered_ms-C3.SNAP_WINDOW_MS+1000,False))
    assert C.decide(late,b)[0].kind=='restart_pass'
    off=tuple(replace(t,x=r.x+4.) if t.entity=='A2' else t for t in b.tracks)
    assert C.decide(replace(late,tracks=off),replace(b,tracks=off))[0].kind=='restart_wait'


def test_v3_restart_standing_is_legal_and_available(port3):
    r=toss(port3);taker_at_spot(port3,r)
    put(port3,'B0',r.x+1.,2.);put(port3,'A2',r.x+1.5,1.5);put(port3,'A3',r.x+40.,50.)
    v,b=restart_view(port3,'B0');i,rec=C.decide(v,b)                      # opponent leaves the 3 m clearance
    assert i.kind=='restart_position' and math.hypot(i.aim[0]-r.x,i.aim[1]-r.y)>=C3.TOSS_CLEARANCE_M+1.5
    assert rec['path']=='restart_toss_clearance'
    v,b=port3.view('A2',port3.m.s.now);i,rec=C.decide(v,b)                # too-close teammate makes himself throwable
    assert rec['path']=='restart_support' and C3.PASS_MIN_M<=math.hypot(i.aim[0]-r.x,i.aim[1]-r.y)<=C3.PASS_MAX_M
    # goal-line scrimmage: defenders can stand on the legal side (regression: clamp left them 0.1 m offside)
    e,s=port3.m.e,port3.m.s;clear_field(port3);r=e.award('A',99.5,30.,'turnover',fresh=True,normalize=False)
    put(port3,'B0',90.,30.);v,b=restart_view(port3,'B0');i,_=C.decide(v,b)
    assert i.aim[0]>=r.x-.05
    put(port3,'B0',*i.aim);put(port3,'A5',*r.taker_spot)
    sg=s.attack_sign('A');assert not sg*(s.players['B0'].x-r.x)<-.05
    # the tackler retires five metres to the defending side
    r.rs['tackler']='B1';put(port3,'B1',r.x-1.,31.);v,b=restart_view(port3,'B1');i,rec=C.decide(v,b)
    assert rec['path']=='restart_tackler_retires'


def test_v3_restart_decisions_ignore_hidden_state_and_archers_do_not_take_part(port3):
    r=toss(port3);taker_at_spot(port3,r);put(port3,'A2',r.x+3.,12.);put(port3,'B0',r.x+20.,40.)
    port3.m.s.now=r.created_at+1600;port3.capture(port3.m.s.now);port3.m.s.now+=300;s=port3.m.s
    views={pid:port3.view(pid,s.now) for pid in ('A5','A2','B0','A0')}
    before={pid:C.decide(v,b) for pid,(v,b) in views.items()}
    for p in s.players.values():p.x=p.y=-500.;p.posture='hidden-sentinel'
    s.restart.taker='B9';s.restart.x=1.;s.restart.snap_deadline=0;port3.m.e.restart_results.clear()
    assert {pid:C.decide(v,b) for pid,(v,b) in views.items()}==before
    for pid,(v,b) in views.items():
        assert C.decide(*C.view_from_json(json.loads(json.dumps(C.view_to_json(v,b)))))==before[pid]
    assert all(i.record_id==r.native_id for i,_ in before.values())
    va,ba=views['A0'];arch=replace(va,role='archer');assert C.decide(arch,ba)[0].kind not in ('restart_claim','restart_pass','restart_position')


def test_v3_toss_end_to_end_releases_through_decide_and_engine(port3):
    r=toss(port3);s=port3.m.s
    for i,pid in enumerate(['A0','A1','A2','A3','A5']):put(port3,pid,20.+6*i,10.+7*i)
    for i,pid in enumerate(['B0','B1','B2']):put(port3,pid,40.+5*i,30.+5*i)
    rid=r.native_id;drive(port3,70)
    assert port3.m.e.restart_results[rid]=='released'
    claims=[x for x in port3.intents if x.kind=='restart_claim'];throws=[x for x in port3.intents if x.kind=='restart_pass']
    assert claims and throws and all(x.record_id==rid for x in claims+throws[:1])
    rel=next(x for x in port3.m.e.log if x['event']=='restart_release');assert rel['data']['taker']==throws[0].athlete
    m=port3.restart_metric.summary(port3.m.e.restart_results)['toss']
    assert (m['awarded'],m['released'],m['timeout'],m['eligible'],m['eligible_timeout'])==(1,1,0,1,0)


def test_restart_metric_separates_release_from_timeout_and_is_read_only():
    assert travel_ms(0.,23.76,10.,13.5)==0. and travel_ms(100.,23.76,10.,13.5)>travel_ms(30.,23.76,10.,13.5)>1000
    m=RestartMetric()
    row=lambda kind,reach=True,target=True:dict(kind=kind,reason='r',team='A',created_ms=0,best_travel_ms=1,taker_reachable=reach,target_available=target,claimed_ms=1)
    m.rows={'1/1':row('toss'),'1/2':row('toss'),'1/3':row('toss',reach=False),'1/4':row('scrim'),'1/5':row('scrim',target=False),'1/6':row('snap40')}
    res={'1/1':'released','1/2':'toss_timeout','1/3':'toss_timeout','1/4':'released','1/5':'snap_timeout','1/6':'superseded:offence_minor','1/7':'released'}
    out=m.summary(res)
    assert (out['toss']['awarded'],out['toss']['released'],out['toss']['timeout'])==(3,1,2)
    assert out['toss']['release_rate']==pytest.approx(1/3) and out['toss']['timeout_rate']==pytest.approx(2/3)
    assert (out['toss']['eligible'],out['toss']['eligible_timeout'],out['toss']['not_reachable'])==(2,1,1)
    assert out['toss']['eligible_timeout_rate']==.5 and out['scrim']['eligible_timeout_rate']==0. and out['scrim']['no_target']==1
    assert out['snap40']['superseded']==1 and out['snap40']['release_rate']==0.
    assert out['all']['awarded']==6 and out['all']['released']+out['all']['timeout']+out['all']['superseded']==6 and out['unobserved']==1
    # closure alone is not success: all six are closed, two of them released
    assert sum(v!='pending' for k,v in res.items() if k in m.rows)==6 and out['all']['released']==2
    src=Path(__file__).with_name('restart_metric.py').read_text()
    assert 'import random' not in src and '.rng' not in src and '.emit(' not in src and 'native_sync' not in src


def test_v3_archer_does_not_choose_a_release_the_rules_layer_calls_a_foul(port3,port2):
    for port,expect in ((port3,False),(port2,True)):
        scene(port);v,b=port.view('B11',port.m.s.now)
        t=next(x for x in b.tracks if x.entity=='A0')
        for status,legal in (('carried',True),('pass_in_flight',expect),('loose',False)):
            sig=replace(v.signals,passive_team='A',ball_status=status,phase='live')
            assert C.archer_target_legal(t,replace(v,signals=sig,hunt_cleared=True),v.delivered_ms) is legal


# ------------------------------------------------- V1 / V2 short-window guards
PRISTINE_1500=('1b566e96a97928301efd49c1e7c90080376c071464febf24290cb953eb141776','4bacfbe842b567c6fefaa2829682aae42da99fb5829f7e6a2ebf215f42399a0a')

def test_v2_short_window_replays_pristine_a1b1313_hashes():
    """1500 steps of seed 1 under native-v0/2 hash exactly as on codex/native-v0 @ a1b1313."""
    from .run import run_match
    r,_=run_match(1,max_steps=1500);assert (r['trace_hash'],r['state_hash'])==PRISTINE_1500
    assert r['config_digest']==V2_DIGEST and 'tackle' not in r['decisions_by_kind']


def test_v3_short_window_is_deterministic_and_null_m2_equals_plumbing_absent(played):
    from .run import run_match
    first,_=played;again,_=run_match(1,NativeConfigV3(),max_steps=3000);absent,_=run_match(1,NativeConfigV3(),plumbing=False,max_steps=3000)
    for other in (again,absent):
        assert (other['trace_hash'],other['state_hash'],other['score'])==(first['trace_hash'],first['state_hash'],first['score'])
    assert first['config_digest']==NativeConfigV3().digest and first['config']['version']=='native-v0/3'
    assert first['restart_metric']['all']['awarded']==first['restart_awarded']-first['restart_metric']['unobserved']


# ---------------------------------------------------------------- banded scoring (owner basis, 16 Nov 2026)
from .config import BANDED, throw_band
from .run import scoring_summary


def test_v3_scoring_basis_is_banded_and_flat_is_refused():
    c=NativeConfigV3();assert c.scoring=='banded'
    with pytest.raises(ValueError):NativeConfigV3(scoring='flat')
    assert BANDED=={'carry':5,'throw_under_10m':2,'throw_10_to_20m':3,'throw_20m_plus':4,'half_goal':1,'full_goal_award':3,'own_goal':2}
    assert c.digest!=NativeConfig().digest and NativeConfig().digest==V2_DIGEST   # v0/2 unchanged


@pytest.mark.parametrize('distance,band,points',[(0.,'under_10m',2),(9.99,'under_10m',2),(10.,'10_to_20m',3),
                                                  (19.99,'10_to_20m',3),(20.,'20m_plus',4),(45.,'20m_plus',4)])
def test_v3_throw_bands_by_release_distance(distance,band,points):
    assert throw_band(distance)==band and BANDED['throw_'+band]==points


def test_v3_full_goal_award_is_3_in_period_4_and_half_goal_1_in_period_3(port3):
    e,s=port3.m.e,port3.m.s;P=port3.types.Phase
    s.phase=P.LIVE;s.owner='A';s.tackle_count=0;s.period=4;s.score={'A':0,'B':0}
    s.players['A0'].posture='upright'
    e.foul('B0',reason='hold')
    assert s.score['A']==3 and e.scoring_ledger['points.full_goal_award']==3
    s.phase=P.LIVE;s.owner='A';s.tackle_count=0;s.period=3;s.score={'A':0,'B':0}
    e.foul('B1',reason='hold');assert s.score['A']==1 and e.scoring_ledger['points.half_goal']==1


@pytest.fixture(scope='module')
def banded_window():
    from .run import run_match
    return run_match(1,NativeConfigV3(),max_steps=6000)


def test_v3_banded_ledger_sums_to_match_score_and_reports_per_attempt(banded_window):
    result,port=banded_window
    sc=result['scoring']
    assert sc['basis']=='banded'
    assert sum(result['score'].values())==sc['points']['total']
    for band,row in sc['shots'].items():
        assert row['goals']<=row['attempts'] and row['points']==row['goals']*BANDED['throw_'+band]
        assert row['points_per_attempt']==(round(row['points']/row['attempts'],4) if row['attempts'] else None)
    assert sc['carries']['attempts']>0 and sc['carries']['goals']*BANDED['carry']==sc['carries']['points']
    assert sum(r['attempts'] for r in sc['shots'].values())==sum(v for k,v in port.m.e.scoring_ledger.items() if k.startswith('attempts.shot.'))
