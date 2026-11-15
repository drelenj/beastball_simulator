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
        if q.id not in keep:q.x=5.+.01*i;q.y=95.;q.vx=q.vy=0.


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
