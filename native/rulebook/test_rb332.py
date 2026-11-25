from dataclasses import replace

from b1.emergence_intents import BallCourseBelief
from native import cognition as c, paired_policy as p, prism_core as core

from .test_prism_core import core_port


def scene(core_port):
    port, athlete = core_port
    port.capture(port.m.s.now-port.config.latency_ms)
    view,belief = port.view(athlete.id,port.m.s.now)
    return port,view,belief


def test_arrival_clearance_anticipates_intercept_and_penalizes_stale_track(core_port):
    port,view,_ = scene(core_port)
    track = c.Track('B:field','B','field',60.,55.,0.,-10.,view.delivered_ms)
    aim = (80.,50.)
    fresh = p.arrival_clearance(view,aim,40.,1.6,(track,))
    stale = p.arrival_clearance(view,aim,40.,1.6,(replace(track,captured_ms=track.captured_ms-800),))
    assert fresh < 0 and stale < fresh
    assert p.arrival_clearance(view,aim,40.,1.6,()) > 0


def test_mouth_route_considers_keeper_and_pressure(core_port):
    _,view,_ = scene(core_port)
    gx = 100.-view.own_goal_x
    view = replace(view,x=gx-view.attack_sign*.7,y=50.)
    rival = c.Track('B:field','B','field',view.x,51.,0.,0.,view.delivered_ms)
    keeper = replace(rival,entity='B:keeper',role='keeper',x=gx,y=50.)
    routes = p.near_goal_routes(view,(),0)
    opposed = p.near_goal_routes(view,(keeper,),0)
    assert routes
    assert max(v for a,v,_ in opposed) < max(v for a,v,_ in routes)
    assert all(0. < a[0] < 100. and abs(a[1]-50.)<3. for a,v,_ in routes)
    assert p.stretch_available(view,(rival,)) and not p.stretch_available(view,())


def test_takedown_requires_recent_observer_ball_course(core_port):
    _,view,belief = scene(core_port)
    at = view.delivered_ms-110
    track = c.Track('B:field','B','field',view.x+1,view.y,3.,0.,at)
    course = BallCourseBelief('evidence',at,view.delivered_ms,track.x+.6,track.y,1.6,3.,0.,0.)
    viewed = replace(view,paired_fixes=('fresh_takedown',),holds_ball=False)
    witnessed = replace(belief,ball_course=course)
    base = c.ActionIntent('test','test',view.athlete,'press',track.entity,(track.x,track.y),None,None,view.delivered_ms)
    record = {'options':[('press',track.entity,base.aim,3.)], 'believed_carrier':[track.entity]}
    assert p.fresh_ball_holder(viewed,witnessed,(track,)) == track.entity
    menu = core.Menu(viewed)
    core.defender(menu,viewed,witnessed,(track,),base,record)
    assert any(row[0]=='commit_takedown' for row in menu.records[-1]['options'])
    for bad in (None,replace(course,captured_ms=at-800),replace(course,vx=35.)):
        stale = replace(belief,ball_course=bad)
        menu = core.Menu(viewed)
        intent,_ = core.defender(menu,viewed,stale,(track,),base,record)
        assert intent.contact is None
        assert all(row[0]!='commit_takedown' for row in menu.records[-1]['options'])
