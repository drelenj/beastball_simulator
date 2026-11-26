"""RB-3.35 belief planning and final contact authorization."""
from dataclasses import dataclass, replace
from math import hypot

from .cognition import Track, registry_rating
from . import prism_registry, geometry

LOST_POSSESSION_VALUE = 0.0


@dataclass(frozen=True)
class PlanningTrack(Track):
    observation: Track
    instinct_gain: float
    anticipation_gain: float


def projected(track, view, t_ahead_s=0.):
    raw = track.observation if isinstance(track, PlanningTrack) else track
    age = max(0., (view.delivered_ms-raw.captured_ms)/1000)
    if isinstance(track, PlanningTrack):
        instinct, anticipation = track.instinct_gain, track.anticipation_gain
    else:
        instinct = prism_registry.forecast_factor(registry_rating(view, 'instinct'))
        anticipation = prism_registry.forecast_factor(registry_rating(view, 'anticipation'))
    elapsed = age*instinct + t_ahead_s*anticipation
    return tuple(max(0., min(100., coordinate + velocity*elapsed))
                 for coordinate, velocity in ((raw.x,raw.vx),(raw.y,raw.vy)))


def planning_belief(view, belief):
    instincts = prism_registry.forecast_factor(registry_rating(view,'instinct'))
    anticipation = prism_registry.forecast_factor(registry_rating(view,'anticipation'))
    tracks = tuple(PlanningTrack(t.entity,t.team,t.role,*projected(t,view),t.vx,t.vy,t.captured_ms,t,instincts,anticipation)
                   for t in belief.tracks)
    by_id = {t.entity:t for t in tracks}
    return replace(view, tracks=tuple(by_id.get(t.entity,t) for t in view.tracks)), replace(belief, tracks=tracks)


def boundary_risk(view, aim):
    """Conservative stopping envelope over the next planned movement segment."""
    body = view.body
    if body is None or aim is None:
        return False
    x,y = aim
    radius = .38  # Minimum body radius when the view has no measured radius.
    braking = max(.1, body.braking)
    stop_x = view.x + body.vx*abs(body.vx)/(2*braking)
    stop_y = view.y + body.vy*abs(body.vy)/(2*braking)
    if min(y, stop_y) <= radius or max(y, stop_y) >= 100.-radius:
        return True
    if min(x, stop_x) <= radius or max(x, stop_x) >= 100.-radius:
        return not all(geometry.goal_section(at,.62*body.height,.1075,view.goal_radius)
                       for at in (view.y,y,stop_y))
    return False


def gate_contact(view, belief, intent):
    from .paired_policy import fresh_ball_holder
    if intent.contact not in ('wrap','takedown'):
        return intent
    tracks = tuple(t for t in belief.tracks if 0 <= view.delivered_ms-t.captured_ms <= belief.max_track_age_ms)
    holder = fresh_ball_holder(view,belief,tracks)
    if holder == view.release_cue or view.recognized_ball not in ('held',None):
        holder = None
    if holder is not None and intent.target == holder:
        return intent
    course = belief.ball_course
    if course is not None:
        return replace(intent,kind='pursue',target=None,aim=projected_course(course,view),contact=None,technique=None)
    if intent.target and intent.aim:
        return replace(intent,kind='mark',contact=None,technique=None)
    return replace(intent,kind='scan',target=None,aim=None,contact=None,technique=None)


def projected_course(course, view, t_ahead_s=0.):
    track = Track('BALL','ball','ball',course.x,course.y,course.vx,course.vy,course.captured_ms)
    return projected(track,view,t_ahead_s)
