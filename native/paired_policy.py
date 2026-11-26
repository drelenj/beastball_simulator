"""RB-3.32 behavioral experiments. Inputs are observer-local beliefs and own body."""
from math import exp, hypot, sqrt

from . import cognition_rb3 as rb

GRAVITY = 9.81
REACTION_RELATIVE_SPEED_MPS = 4.
MIN_HOLD_HEIGHT_M = .45


def enabled(view, name):
    return name in getattr(view, 'paired_fixes', ())


def opponents(view, tracks):
    return tuple(t for t in tracks if t.team not in (view.team, 'ball') and
                 t.role in ('field', 'keeper') and t.entity not in view.signals.immune)


def arrival_clearance(view, aim, speed, height, defenders, wait_ms=0):
    """Minimum anticipated horizontal separation from reachable defender discs.

    Use the low-arc projectile estimate; reach growth represents a possible
    change of direction from current velocity. Height is not credited as
    clearance, since the defense can also jump.
    """
    dx, dy = aim[0]-view.x, aim[1]-view.y
    distance = hypot(dx, dy)
    if distance < .05 or speed <= 0.:
        return -1.
    sx, sy = dx/distance, dy/distance
    hand = .62 * view.body.height if view.body else 1.6
    dz = height-hand
    v2 = speed*speed
    det = v2*v2-GRAVITY*(GRAVITY*distance*distance+2*dz*v2)
    if det < 0.:
        return -1.
    tan = (GRAVITY*distance*distance+2*dz*v2)/(distance*(v2+sqrt(det)))
    planar = speed / sqrt(1+tan*tan)
    # First-order flight time with the public quadratic drag coefficient.
    material = getattr(view,'ball_material',None)
    drag = material[0] if material else .015
    flight = distance / planar * (1+.5*drag*distance)
    windup = rb.release_time_s(view) + wait_ms / 1000
    rating = dict(view.registry_ratings)
    focus, instinct = rating.get('focus',.7), rating.get('instinct',.7)
    sizes = dict(getattr(view, 'body_reach', ()))
    fallback = view.body.reach if view.body else rb.ACQ_DEFAULT_REACH_M
    uncertainty = .12 + .40*(1-focus) + .30*(1-instinct)
    closest = 10.-uncertainty
    for other in defenders:
        age = max(0., (view.delivered_ms-other.captured_ms)/1000)
        radius = sizes.get(other.entity, fallback) + rb.ACQ_RADIUS_M + rb.ACQ_EXTRA_M
        radius += rb.LANE_MARGIN_M + uncertainty + age*(.35 + .65*(1-instinct) + .5*(1-focus))
        px, py = other.x-view.x+other.vx*windup, other.y-view.y+other.vy*windup
        vx, vy = dx-other.vx*flight, dy-other.vy*flight
        fraction = max(0.,min(1.,(px*vx+py*vy)/max(1e-9,vx*vx+vy*vy)))
        for f in (max(0.,fraction-.16),fraction,min(1.,fraction+.16)):
            elapsed = windup + flight*f
            reachable = radius + .5 * rb.TYPICAL_ACCEL * elapsed*elapsed
            margin = hypot(px-f*vx,py-f*vy)-reachable
            closest = min(closest,margin)
    return closest


def fresh_ball_holder(view, belief, tracks):
    course = belief.ball_course
    reaction = view.core_decision_ms * (1+.4*(.70-dict(view.registry_ratings).get('reaction',.7)))
    if enabled(view,"frame_freshness"):
        reaction = view.ladder_data[0]
    if (course is None or not 0 <= view.delivered_ms-course.captured_ms <= reaction
            or course.z < MIN_HOLD_HEIGHT_M):
        return None
    candidates = sorted(
        (hypot(t.x-course.x,t.y-course.y), t.entity)
        for t in tracks if t.role in ('field','keeper') and t.captured_ms == course.captured_ms
        and hypot(t.vx-course.vx,t.vy-course.vy) <= REACTION_RELATIVE_SPEED_MPS
    )
    if candidates and candidates[0][0] <= 1.6:
        gap, entity = candidates[0]
        if len(candidates)==1 or candidates[1][0]-gap >= .25:
            return entity
    return None


def stretch_available(view, defenders):
    if not view.body or view.role!='field' or not getattr(view,'rb3_carrier_moves_enabled',False):
        return False
    goal_x = 100.-view.own_goal_x
    # Physics controls extension. The option requires a plausible hand route
    # at the current height and an imminent contact in the perceived scene.
    handling = dict(view.own_skills).get('ball_handling',.7)
    extension = view.body.reach * (.9-.18*(1-handling))
    hand_height = .62*view.body.height
    return ((enabled(view,"stretch_range") or view.zone_elapsed_ms + 300 < 5000) and abs(goal_x-view.x) <= extension-.11 and
            hypot(view.y-50., hand_height) < view.goal_radius-.11 and
            (enabled(view,"stretch_range") or any(rb.time_to_contact(view,t) < .28 for t in defenders)))


def near_goal_routes(view, defenders, zone_time_ms):
    """Direct and single-bend routes ranked in expected five-point carries."""
    gx = 100.-view.own_goal_x
    if not view.body or view.role!='field' or hypot(gx-view.x,50.-view.y)>20.:
        return None
    routes = []
    reaches = [(rival,rb.opp_reach(view,rival)) for rival in defenders]
    for y, bend in ((49.,0.),(50.,0.),(51.,0.),(50.,-2.),(50.,2.)):
        end = (gx-.35*view.attack_sign,y)
        start = (view.x,view.y)
        mid = ((start[0]+end[0])*.5, max(1.,min(99.,(start[1]+end[1])*.5+bend)))
        points = (start,mid,end)
        path = sum(hypot(b[0]-a[0],b[1]-a[1]) for a,b in zip(points,points[1:]))
        if path < .05:
            continue
        norm = max(.05,hypot(end[0]-start[0],end[1]-start[1]))
        direction = ((end[0]-start[0])/norm,(end[1]-start[1])/norm)
        acceleration = max(.1,view.body.acceleration)
        top = max(1.,view.body.maximum_speed)
        along = max(-top,min(top,view.body.vx*direction[0]+view.body.vy*direction[1]))
        ramp = (top*top-along*along)/(2*acceleration)
        duration = ((sqrt(along*along+2*acceleration*path)-along)/acceleration if path<=ramp
                    else (top-along)/acceleration+(path-ramp)/top)
        slack = 2.
        for index,(a,b) in enumerate(zip(points,points[1:])):
            for fraction in (.25,.60,1.):
                x,y_at = (a[0]+fraction*(b[0]-a[0]),a[1]+fraction*(b[1]-a[1]))
                eta = duration*(index+fraction)/2
                for rival, reach in reaches:
                    slack = min(slack,rb.typical_time_to(rival,x,y_at,reach,view)-eta)
        needed = max(0.,duration-(5000-zone_time_ms)/1000)
        # Smoothed stopped-short probability, with time exposure even
        # when the latest belief admits a clear route.
        probability = exp(-duration/3.-2*needed) / (1+exp(-max(-20.,min(20.,3*slack))))
        routes.append((end if not bend or hypot(mid[0]-start[0],mid[1]-start[1])<2. else mid,
                       (view.ladder_data[1] if enabled(view,"carry_seven") or enabled(view,"carry_value") else 5)*probability,duration))
    return routes


def shot_points(view, plan, *, scoring_table=False):
    if plan is None:
        return 0.
    distance = hypot(plan['aim'][0]-view.x,50.-view.y)
    band = 5 if distance<3 else 2 if distance<10 else 3 if distance<20 else 4
    if scoring_table:
        from .ladder import release_points
        band = release_points(view, distance)
    margin = min(4.,max(0.,plan['margin']))
    return band * (.28+.11*margin) * exp(-distance/45.)


def continuation_points(utility, *, carry_scale=1.):
    return (1.55 * carry_scale) / (1+exp(-max(-20.,min(20.,(utility-3.)/2.))))


def boundary_aim(view, aim):
    """Steer a held ball away from an edge before the body reaches it.

    Retain the carrier's lateral route. A finish near the attacked end is
    exempt only when the observed body motion and aimed route meet the
    whole-ball mouth. Braking distance is based on own motion and ability.
    """
    if view.body is None:
        return aim
    x,y = aim
    body = view.body
    brake = max(.1,body.braking)
    sx = view.attack_sign
    goal_x = 100.-view.own_goal_x
    forward = max(0.,body.vx*sx)
    ball_r = .1075
    held_offset = .35+.35*body.reach
    hand = .62*body.height
    depth = abs(goal_x-view.x)
    time_to_edge = max(0.,depth-held_offset+ball_r)/max(.5,forward)
    crossings = (view.y, y, view.y+body.vy*min(.5,time_to_edge))
    mouth = all(hypot(offset-50.,hand) <= view.goal_radius-ball_r for offset in crossings)
    end_margin = min(20.,max(rb.BOUNDARY_MARGIN_M,held_offset+.2+forward*forward/(2*brake)))
    if not mouth and (depth<=end_margin+1. or abs(goal_x-x)<end_margin):
        x = min(x,100.-end_margin) if sx>0 else max(x,end_margin)
    ownward = max(0.,-body.vx*sx)
    own_margin = min(20.,max(rb.BOUNDARY_MARGIN_M,.5+ownward*ownward/(2*brake)))
    x = max(x,own_margin) if sx>0 else min(x,100.-own_margin)
    low = min(20.,max(rb.BOUNDARY_MARGIN_M,.5+max(0.,-body.vy)**2/(2*brake)))
    high = min(20.,max(rb.BOUNDARY_MARGIN_M,.5+max(0.,body.vy)**2/(2*brake)))
    return (round(x,3),round(max(low,min(100.-high,y)),3))
