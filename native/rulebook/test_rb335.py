from dataclasses import replace

from b1.emergence_intents import BallCourseBelief
from native.cognition import ActionIntent, Track
from native.turnovers import boundary_risk, gate_contact, planning_belief, projected
from .test_rb332 import scene
from .test_prism_core import core_port


def test_projection_does_not_double_advance_or_change_capture(core_port):
    _, view, belief = scene(core_port)
    view = replace(view,paired_fixes=('projected_beliefs',),
                   registry_ratings=(('instinct',1.),('anticipation',1.)))
    track = Track('r','B','field',85.,50.,20.,-10.,view.delivered_ms-200)
    live_view, live_belief = planning_belief(view,replace(belief,tracks=(track,)))
    planned = live_belief.tracks[0]
    assert (planned.x,planned.y,planned.captured_ms)==(89.,48.,track.captured_ms)
    assert projected(planned,live_view,.8)==(100.,40.)
    assert (track.x,track.y)==(85.,50.)


def test_final_gate_requires_matching_observation_and_respects_release_cue(core_port):
    _, view, belief = scene(core_port)
    capture = view.delivered_ms-250
    track = Track('r','B','field',55.,50.,0.,0.,capture)
    course = BallCourseBelief('p',capture,view.delivered_ms,55.5,50.,1.4,0.,0.,0.)
    belief = replace(belief,tracks=(track,),ball_course=course)
    view = replace(view,paired_fixes=('frame_freshness','takedown_gate'),ladder_data=(400,),
                   recognized_ball='held')
    intent = ActionIntent('x','x',view.athlete,'tackle','r',(55.,50.),None,None,
                          view.delivered_ms,contact='takedown')
    assert gate_contact(view,belief,intent) is intent
    rejected = gate_contact(replace(view,release_cue='r'),belief,intent)
    assert rejected.kind=='pursue' and rejected.contact is None
    assert gate_contact(view,replace(belief,ball_course=None),intent).kind=='mark'


def test_carrier_stopping_envelope_reads_velocity_and_goal_mouth(core_port):
    _, view, _ = scene(core_port)
    body = replace(view.body,vx=0.,vy=-12.,braking=9.)
    assert boundary_risk(replace(view,y=5.,body=body),(50.,7.))
    assert not boundary_risk(replace(view,y=15.,body=body),(50.,17.))
    body = replace(body,vx=12.,vy=0.)
    assert not boundary_risk(replace(view,x=97.,y=50.,body=body),(101.,50.))
    assert boundary_risk(replace(view,x=97.,y=42.,body=body),(101.,42.))


def test_swept_held_side_crossing_and_unchanged_end_line(core_port):
    from .port import RulebookPort
    from native.roster import rb3_control_rosters
    old,_ = core_port
    for switches in ((),('sideline_held_ball',)):
        port = RulebookPort(1,replace(old.config,rb333=switches),rosters=rb3_control_rosters())
        match,state = port.m,port.m.s
        state.phase = port.types.Phase.LIVE
        p = state.players['A:0']
        p.x,p.y = 50.,1.
        for x,y,expected in ((50.,-.2,None if switches else 'boundary'),
                             (100.2,49.,'goal'),(100.2,40.,'boundary')):
            state.ball = port.types.Ball(mode=port.types.BallMode.CONTROLLED,carrier=p.id,
                                         x=min(x,99.),y=max(y,.2),z=1.4)
            def follow():
                state.ball.x,state.ball.y = x,y
            match.e.follow_carrier = follow
            kinds = [e.kind for e in match.advance_ball(100,{})]
            assert kinds==([expected] if expected else [])


def test_keeper_plant_requires_visible_ball_holder_windup(core_port):
    from b1.emergence_intents import KeeperIntent
    from native.prism_core import Menu, keeper_options

    _, view, belief = scene(core_port)
    at = view.delivered_ms-250
    rival = Track('r','B','field',21.,53.,2.,0.,at)
    course = BallCourseBelief('p',at,view.delivered_ms,21.5,53.,1.4,2.,0.,0.)
    belief = replace(belief,tracks=(rival,),ball_course=course)
    view = replace(view,role='keeper',x=2.,y=48.,own_goal_x=0.,attack_sign=1,
                   recognized_ball='held',ball_course=course,
                   signals=replace(view.signals,direct_team='B'),
                   paired_fixes=('keeper_plant','keeper_settle','frame_freshness'),ladder_data=(400,))
    aux = KeeperIntent('k',view.athlete,'position',view.delivered_ms,None,target=(4.,50.))
    base = ActionIntent('x','x',view.athlete,'keeper_control',None,None,None,None,
                        view.delivered_ms,auxiliary=aux)
    planted = replace(view,visible_windups=('r',))
    assert keeper_options(Menu(planted),planted,base,belief).auxiliary.target==(2.,48.)
    assert keeper_options(Menu(view),view,base,belief).auxiliary.target!=(2.,48.)
