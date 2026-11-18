"""RB/3 decision adjustments (RB-3.4, owner rulings 17 Nov 2026). PROVISIONAL, pure.

Applied only when view.cognition is 'native-rb/3'. Inputs: the athlete's
view and own belief. A frozen player is known only from the public status light the
athlete can see (view.status_indicators 'red') and his believed position.
- No press or tackle on a believed-frozen player: the intent becomes a 'position'.
- Path planning: if the straight path to a locomotion aim passes a believed-frozen
  player, the athlete aims for a waypoint beside him (steer around).
The Archer's re-check at release is the existing decide path (abort_draw when the
target is no longer believed legal), with 'loose' accepted under RB/3.
Constants are PRIMITIVE and unsearched.
"""
from dataclasses import replace
from math import hypot

CLEARANCE_M = 1.6      # path passing closer than this to a frozen body is re-routed
SIDESTEP_M = 2.2       # waypoint offset beside the frozen body
MOVES = ('position', 'carry', 'pursue', 'press', 'mark', 'support', 'receive', 'search', 'keeper_set', 'restart_position')


def frozen_tracks(view, belief):
    red = {pid for pid, light in getattr(view, 'status_indicators', ()) if light == 'red'}   # RulebookView only
    return [t for t in belief.tracks if t.entity in red and view.delivered_ms - t.captured_ms <= 2000]


def detour(x, y, aim, obstacles):
    ax, ay = aim[0] - x, aim[1] - y
    d2 = ax * ax + ay * ay
    if d2 < 1e-6:
        return aim, None
    best = None
    for o in obstacles:
        f = ((o.x - x) * ax + (o.y - y) * ay) / d2
        if not 0. < f < 1.:
            continue
        gap = hypot(o.x - x - f * ax, o.y - y - f * ay)
        if gap < CLEARANCE_M and (best is None or f < best[0]):
            best = (f, o)
    if best is None:
        return aim, None
    f, o = best
    n = d2 ** .5
    px, py = -ay / n, ax / n                      # unit normal to the path
    side = 1. if (o.x - x) * px + (o.y - y) * py < 0 else -1.   # pass on the side away from him
    wx = min(99.4, max(.6, o.x + side * px * SIDESTEP_M))
    wy = min(99.4, max(.6, o.y + side * py * SIDESTEP_M))
    return (round(wx, 3), round(wy, 3)), o.entity


def adjust(view, belief, intent, record):
    frozen = frozen_tracks(view, belief)
    if not frozen:
        return intent, record
    ids = {t.entity for t in frozen}
    record = dict(record, rb3_frozen_believed=sorted(ids))
    if intent.kind in ('press', 'tackle') and intent.target in ids:
        intent = replace(intent, kind='position', contact=None)
        record['rb3_no_contact_on_frozen'] = intent.target
    if intent.kind in MOVES and intent.aim is not None:
        aim, around = detour(view.x, view.y, intent.aim, frozen)
        if around is not None:
            intent = replace(intent, aim=aim)
            record['rb3_detour_around'] = around
    return intent, record
