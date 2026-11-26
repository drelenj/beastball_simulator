"""RB-3.33 optional movement and passing models."""
from math import sqrt
from .geometry import goal_section

SWITCHES = frozenset(('frame_freshness','arrival_lane','movement_clock','mouth_boundary','braking',
    'keeper_interrupt','keeper_deadline','keeper_menu','keeper_settle','cadence','field_interrupt',
    'abort_wrap','pass_signal','pass_speed','carry_seven','carry_value','stretch_range','planning_speed','fast_cadence'))


def freeze_tuple(value):
    return tuple(map(freeze_tuple,value)) if isinstance(value,(tuple,list)) else value


def release_points(view,distance):
    _,carry,bands,radius = view.ladder_data[:4]
    if distance<radius:
        return carry
    return next(points for upper,points in bands if upper is None or distance<upper)


def catch_capacity(skill,miss,mass):
    fraction=max(0.,min(1.,(skill-.4)/.6))
    return (400+(2.5*.5*mass*134.1**2-400)*fraction**3.6)*max(0.,1-miss*miss)


def pass_target(view,receiver,distance):
    teammates,mass=view.ladder_data[4:]
    skill=dict(teammates).get(receiver,.7)
    safe=sqrt(2*catch_capacity(skill,.4,mass)*(1/9)**(1/8)/mass)
    return min(safe,80.,.5*view.max_throw_speed,max(35.,2*31.2928,distance/.25))


def brake_target(p,aim,radius):
    x,y=aim
    def clamp(value,velocity,margin):
        distance=velocity*velocity/(2*max(.1,p.a.braking))
        return max(margin+(distance if velocity<0 else 0.),min(100-margin-(distance if velocity>0 else 0.),value))
    if not all(goal_section(yy,p.hand_height,.1075,radius) for yy in (p.y,y)):
        x=clamp(x,p.vx,.55+.35*p.a.reach)
    return x,clamp(y,p.vy,p.radius+.2)


def release_listeners(port,giver,kind,target,aim):
    """Event dispatch selects listeners. No player locations enter the interrupt payload."""
    state=port.m.s
    flags=port.config.rb333
    dx,dy=aim[0]-giver.x,aim[1]-giver.y
    listeners={}
    for p in state.players.values():
        if not p.active or p.id==giver.id or p.role=='archer':
            continue
        intent=getattr(p,'native_intent',None)
        if kind=='shoot' and p.team!=giver.team and p.role=='keeper' and 'keeper_interrupt' in flags:
            listeners[p.id]='shot'
        elif 'field_interrupt' in flags:
            if intent and intent.target==giver.id and intent.contact in ('wrap','takedown'):
                listeners[p.id]='release_from_wrap'
            elif kind=='pass':
                f=max(0.,min(1.,((p.x-giver.x)*dx+(p.y-giver.y)*dy)/max(.0001,dx*dx+dy*dy)))
                if p.id==target or p.team!=giver.team and (p.x-giver.x-f*dx)**2+(p.y-giver.y-f*dy)**2<=225.:
                    listeners[p.id]='pass'
    return listeners
