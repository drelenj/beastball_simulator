"""Own-body boundary control for Native's surface locomotion."""
from math import hypot

from .geometry import goal_section

FLAGS = ('edge_brake', 'edge_turn', 'edge_aim')
FIELD_M = 100.
MIN_AIM_MARGIN_M = 2.
BRAKE_BUFFER_M = .3
AIM_BUFFER_M = .5


def mouth_path(x, y, dx, dy, goal, radius, hand_height, ball_radius, goal_radius):
    """Test the chord where the leading body edge reaches the attacked line."""
    if goal is None:
        return False
    sign = 1. if goal==FIELD_M else -1.
    forward = sign * dx
    if forward<=0:
        return False
    distance = max(0.,sign*(goal-x)-radius)
    return goal_section(y+dy*distance/forward,hand_height,ball_radius,goal_radius)


def lines(x, y, radius, excluded_goal):
    if excluded_goal!=0.:
        yield x-radius, -1., 0.
    if excluded_goal!=FIELD_M:
        yield FIELD_M-x-radius, 1., 0.
    yield y-radius, 0., -1.
    yield FIELD_M-y-radius, 0., 1.


def clamp_aim(aim, *, x, y, vx, vy, radius, braking, goal, hand_height, ball_radius, goal_radius):
    """Apply per-normal stopping margins and keep the destination inside the playable box."""
    def margin(outward):
        if outward <= 0:
            return MIN_AIM_MARGIN_M
        if braking <= 0:
            return FIELD_M-MIN_AIM_MARGIN_M
        return min(FIELD_M-MIN_AIM_MARGIN_M,
                   max(MIN_AIM_MARGIN_M,radius+outward*outward/(2*braking)+AIM_BUFFER_M))

    tx,ty = aim
    ty = max(margin(-vy),min(FIELD_M-margin(vy),ty))
    exempt = mouth_path(x,y,tx-x,ty-y,goal,radius,hand_height,ball_radius,goal_radius)
    if not exempt or goal==FIELD_M:
        tx = max(margin(-vx),tx)
    if not exempt or goal==0.:
        tx = min(FIELD_M-margin(vx),tx)
    return tx,ty


def view_aim(view, aim):
    body = view.body
    if body is None or view.own_radius is None or view.bench_role or view.signals.phase not in ('live','opening','award','penalty'):
        return aim
    return clamp_aim(aim,x=view.x,y=view.y,vx=body.vx,vy=body.vy,radius=view.own_radius,
                     braking=body.braking,goal=FIELD_M-view.own_goal_x if view.holds_ball else None,
                     hand_height=body.z+.62*body.height,ball_radius=.1075,goal_radius=view.goal_radius)


def propulsion(vx, vy, tx, ty, dt, acceleration, braking, turning, other_turn=0.):
    """Existing fore/aft and lateral limits, applied to the time left after cancellation."""
    speed = hypot(vx,vy)
    dvx,dvy = tx-vx,ty-vy
    accel = acceleration if tx*tx+ty*ty>speed*speed else braking
    if speed<=1.:
        delta = hypot(dvx,dvy)
        factor = min(1.,accel*dt/delta) if delta else 0.
        return dvx*factor,dvy*factor
    hx,hy = vx/speed,vy/speed
    along = max(-braking*dt,min(accel*dt,dvx*hx+dvy*hy))
    side = max(-turning*dt,min(turning*dt,-dvx*hy+dvy*hx))
    if other_turn:
        side = abs(side)*other_turn
    return along*hx-side*hy, along*hy+side*hx


def update(player, dt, tx, ty, acceleration, goal, ball_radius, goal_radius, *, brake, turn):
    """Return true when the edge controller consumed this propulsion step."""
    vx,vy = player.vx,player.vy
    braking,turning = player.a.braking,player.a.turning
    if dt<=0 or not (vx or vy):
        return False
    # Most requests never get close enough to constrain propulsion.
    diameter = 2*(vx*vx+vy*vy)/turning if turn and turning>0 and vx*tx+vy*ty<0 else 0.
    stopping = ((vx*vx+vy*vy)/(2*braking)+BRAKE_BUFFER_M if brake and braking>0 else 0.)
    x,y,radius = player.x,player.y,player.radius
    if min(x,y,FIELD_M-x,FIELD_M-y)-radius>max(diameter,stopping):
        return False

    exempt = goal if mouth_path(x,y,vx,vy,goal,radius,player.hand_height,ball_radius,goal_radius) else None
    edges = tuple(lines(x,y,radius,exempt))
    short = vx*ty-vy*tx
    opposite = 0.
    if diameter and short and any(d<=diameter and (vx*ny-vy*nx)*short>0 for d,nx,ny in edges):
        opposite = -1. if short>0 else 1.
    threats = []
    if stopping:
        for distance,nx,ny in edges:
            outward = vx*nx+vy*ny
            if outward>0 and outward*outward/(2*braking)>=distance-BRAKE_BUFFER_M:
                threats.append((distance,nx,ny,outward))
    if not (threats or opposite):
        return False

    for _,nx,ny,outward in sorted(threats):
        change = min(outward,braking*dt)
        vx -= change*nx
        vy -= change*ny
        dt = max(0.,dt-change/braking)
    dvx,dvy = propulsion(vx,vy,tx,ty,dt,acceleration,braking,turning,opposite)
    for _,nx,ny,_ in threats:
        # Spend the remainder on steering or on propulsion away from the line.
        outward = max(0.,dvx*nx+dvy*ny)
        dvx -= outward*nx
        dvy -= outward*ny
    player.vx,player.vy = vx+dvx,vy+dvy
    return True


def install(port):
    match,state,cfg = port.m,port.m.s,port.config
    brake = 'edge_brake' in cfg.rb333
    turn = 'edge_turn' in cfg.rb333

    def eligible(player):
        return player.active and not any(out==player.id for out,_ in match.pending_sub.values())

    def attack_goal(player):
        return state.attack_goal(player.team) if state.ball.carrier==player.id else None

    def propulsion_step(player,dt,live,tx,ty,acceleration):
        return live and eligible(player) and update(player,dt,tx,ty,acceleration,
            attack_goal(player),state.ball.radius,cfg.goal_radius,brake=brake,turn=turn)

    def target(player, aim):
        if state.phase not in (port.types.Phase.LIVE,port.types.Phase.OPENING,
                               port.types.Phase.AWARD,port.types.Phase.PENALTY) or not eligible(player):
            return aim
        return clamp_aim(aim,x=player.x,y=player.y,vx=player.vx,vy=player.vy,radius=player.radius,
                         braking=player.a.braking,goal=attack_goal(player),hand_height=player.hand_height,
                         ball_radius=state.ball.radius,goal_radius=cfg.goal_radius)

    if brake or turn:
        match.native_edge_update = propulsion_step
    if 'edge_aim' in cfg.rb333:
        match.native_edge_target = target
        match.native_boundary_target = target
