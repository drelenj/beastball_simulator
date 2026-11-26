"""native-v0/3 (FAB-1) athlete decisions added on top of the v0/2 decision set.

Pure module: inputs are the athlete's immutable view and own belief only.
  FAB-1b  contact decisions. A defender chooses to stay with the carrier (wrap)
          or to wrap and bring him down (takedown). A carrier chooses to run
          through, brace or dodge. The engine keeps reach, legality, grip,
          balance and grounding; nothing here decides an outcome.
  FAB-1c  restart decisions. Who claims a restart, where the taker throws and
          where the other athletes stand, from believed positions.
Every constant below is PRIMITIVE and unsearched: a functional default, not a
tactic and not a quality claim. Rule constants are public rule knowledge.
"""
from dataclasses import replace
from math import hypot
from . import cognition as C

# ---- PRIMITIVE, unsearched decision constants ------------------------------
TACKLE_COMMIT_M = 6.0        # believed gap at which a pressing defender commits to a takedown
TACKLE_LEAD_S = .5           # longest believed lead on the carrier's track
THREAT_HORIZON_S = .9        # carrier considers opponents believed to arrive within this time
DODGE_MIN_S = .3             # less warning than this: no room to dodge
DODGE_STEP_M = 6.            # lateral / forward size of a dodge aim
BRACE_LOAD = .7              # own balance load above which a held carrier braces
TRACK_FRESH_MS = 1000        # a believed position older than this is not used for a throw
CLAIM_BACKOFF_MS_PER_M = 25  # own distance to the spot delays an athlete's own claim
CLAIM_WIDEN_MS = 600         # every such interval one more believed-closer teammate is tolerated
PASS_MIN_M, PASS_MAX_M = 4., 34.   # same believed-distance window as the v0/2 pass options
SUPPORT_NEAR_M, SUPPORT_FAR_M = 5., 20.
# ---- public rule knowledge (RULES_FLOW v0.3 / D-5 timings as built) --------
TOSS_MIN_WAIT_MS, TOSS_WINDOW_MS, SNAP_WINDOW_MS = 1500, 5500, 10000
TOSS_CLEARANCE_M = 3.
RELEASE_MS = 250


def _clamp(v, lo, hi):
    return lo if v < lo else hi if v > hi else v


def _intent(view, belief, kind, aim=None, target=None, contact=None, options=None, why=None):
    did = view.observation_id + '/decision'
    intent = C.ActionIntent(did + '/intent', did, view.athlete, kind, target, aim, None, None,
                            view.delivered_ms, speed=(min(80.,.5*view.max_throw_speed) if view.cognition=='native-rb/3' else min(27., view.max_throw_speed)), height=1.6,
                            contact=contact, record_id=view.restart[0] if view.restart else None,
                            period=view.signals.period)
    record = {'decision_id': did, 'owner': view.athlete, 'role': view.role,
              'observation_id': view.observation_id, 'belief_revision': belief.revision,
              'selected': [kind, target, aim, contact],
              'options': [list(o) for o in (options or [(kind, target, aim, 0.)])],
              'selection_rule': 'max(value, kind, target)', 'path': why, 'cognition': 'native-v0/3'}
    return intent, record


def _fresh(view, belief, age=2000):
    return tuple(t for t in belief.tracks if 0 <= view.delivered_ms - t.captured_ms <= age)


# ============================================================ FAB-1b contact
def defender_contact(view, belief, intent, record):
    """A pressing defender owns the choice between wrap (stay with him) and takedown."""
    carrier = record.get('believed_carrier')
    if not carrier or carrier[1] == view.team or carrier[0] == 'me':
        return replace(intent, contact=None), record
    c = next((t for t in _fresh(view, belief) if t.entity == carrier[0]), None)
    if c is None or C.keeper_protected(c, view):
        return replace(intent, contact=None), record
    gap = hypot(c.x - view.x, c.y - view.y)
    top = view.body.maximum_speed if view.body else 27.
    lead = min(TACKLE_LEAD_S, gap / max(1., top))
    if 'projected_beliefs' in getattr(view,'paired_fixes',()):
        meet = tuple(round(_clamp(coord,.6,99.4),3) for coord in C.project_track(c,view,lead))
    else:
        meet = (round(_clamp(c.x + c.vx * lead, .6, 99.4), 3), round(_clamp(c.y + c.vy * lead, .6, 99.4), 3))
    # values: a takedown is worth more than staying with him once the believed gap is inside the commit range
    options = [('press', c.entity, intent.aim, 1., 'wrap'),
               ('tackle', c.entity, meet, round(1. + (TACKLE_COMMIT_M + C.owned_effect(view, 'defending', 1., 'defender_duel', 'defending') - gap), 6), 'takedown')]
    if view.own_hold_target == c.entity:          # own hands are on him (own action knowledge)
        options[1] = ('tackle', c.entity, meet, round(2. + TACKLE_COMMIT_M, 6), 'takedown')
        if view.registry_ratings:
            threshold = C.PRISM.TAKEDOWN_LOAD_THRESHOLD - C.owned_effect(
                view, 'takedown', C.PRISM.TAKEDOWN_LOAD_RANGE)
            options[1] = ('tackle', c.entity, meet, round(1. + view.own_balance_load - threshold, 6), 'takedown')
    kind, target, aim, value, contact = max(options, key=lambda o: (o[3], o[0]))
    record = dict(record, contact_options=[list(o) for o in options], contact_selected=contact,
                  believed_gap=round(gap, 3), cognition='native-v0/3')
    return replace(intent, kind=kind, target=target, aim=aim, contact=contact), record


def carrier_contact(view, belief, intent, record):
    """A field carrier who is carrying owns his response to contact: run through, brace or dodge."""
    now = view.delivered_ms
    vx, vy = (view.body.vx, view.body.vy) if view.body else (0., 0.)
    threats = []
    for o in _fresh(view, belief, 700):
        if o.team in (view.team, 'ball') or o.role == 'archer':
            continue
        dx, dy = o.x - view.x, o.y - view.y
        d = hypot(dx, dy)
        closing = -((o.vx - vx) * dx + (o.vy - vy) * dy) / d if d > 0 else 0.
        gap = max(0., d - 1.2)
        eta = 0. if gap <= 0 else gap / closing if closing > .5 else 99.
        if eta <= THREAT_HORIZON_S:
            threats.append((round(eta, 3), o.entity, dx, dy))
    threats.sort()
    if view.own_held <= 0 and not threats:
        return intent, record
    options = []
    if view.own_held > 0:
        # held: fight the grip while balance allows, otherwise protect the ball and accept the tackle
        options.append(('carry', None, intent.aim, round(1. - view.own_balance_load + C.owned_effect(view, 'evasion', .5, 'carrier_duel'), 6), 'run_through'))
        options.append(('carry', None, (round(view.x, 3), round(view.y, 3)), round(1. - BRACE_LOAD, 6), 'brace'))
    else:
        eta, who, dx, dy = threats[0]
        imminent = [t for t in threats if t[0] < DODGE_MIN_S]
        options.append(('carry', None, intent.aim, 1., 'run_through'))
        if eta >= DODGE_MIN_S - C.owned_effect(view, 'evasion', .15, 'carrier_duel') and intent.aim:
            ax, ay = intent.aim[0] - view.x, intent.aim[1] - view.y
            n = hypot(ax, ay) or 1.
            ux, uy = ax / n, ay / n
            side = 1. if (-uy) * dx + ux * dy < 0 else -1.     # step to the side the threat is not on
            aim = (round(_clamp(view.x + ux * DODGE_STEP_M - uy * side * DODGE_STEP_M, 1., 99.), 3),
                   round(_clamp(view.y + uy * DODGE_STEP_M + ux * side * DODGE_STEP_M, 3., 97.), 3))
            options.append(('carry', None, aim, 2., 'dodge'))
        if len(imminent) >= 2:
            options.append(('carry', None, (round(view.x, 3), round(view.y, 3)), 1.5, 'brace'))
    kind, target, aim, value, contact = max(options, key=lambda o: (o[3], o[4]))
    record = dict(record, contact_options=[list(o) for o in options], contact_selected=contact,
                  believed_threats=[list(t[:2]) for t in threats], own_held=view.own_held,
                  own_balance_load=round(view.own_balance_load, 4), cognition='native-v0/3')
    return replace(intent, aim=aim, contact=contact), record


# ============================================================ FAB-1c restarts
def _spot_side(x, y):
    """Unit vector from a boundary spot into the field."""
    return (1., 0.) if x <= 0 else (-1., 0.) if x >= 100 else (0., 1.) if y <= 0 else (0., -1.) if y >= 100 else (0., 0.)


def _throw_options(view, belief, kind, x, y):
    now = view.delivered_ms
    fresh = _fresh(view, belief, TRACK_FRESH_MS)
    opps = [t for t in fresh if t.team not in (view.team, 'ball') and t.role != 'archer']
    spot_in_zone = C.in_own_zone(view.team, x, y, view)
    out = []
    for c in sorted((t for t in fresh if t.team == view.team and t.role != 'archer'), key=lambda t: t.entity):
        d = hypot(c.x - x, c.y - y)
        if not PASS_MIN_M <= d <= PASS_MAX_M:
            continue
        if not .6 <= c.x <= 99.4 or not .6 <= c.y <= 99.4:
            continue
        if not spot_in_zone and C.in_own_zone(view.team, c.x, c.y, view):
            continue
        clearance = C._lane_clearance(x, y, c.x, c.y, opps)
        value = min(clearance, 6.) - .03 * d - .0005 * (now - c.captured_ms)
        out.append(('restart_pass', c.entity, (round(c.x, 3), round(c.y, 3)), round(value, 6)))
    return out, opps


def _distance_speed(view, intent):
    """RB-3.19 A1: restart throws use the shared distance-based release speed (native/throw_speed.py)."""
    from .throw_speed import release_speed
    from dataclasses import replace as _r
    return _r(intent, speed=release_speed(hypot(intent.aim[0] - view.x, intent.aim[1] - view.y), view.max_throw_speed))


def _taker(view, belief, kind, team, x, y, tx, ty, created, ready):
    now = view.delivered_ms
    elapsed = now - created
    window = TOSS_WINDOW_MS if kind == 'toss' else SNAP_WINDOW_MS
    if view.pending_command_id is not None:
        return _intent(view, belief, 'continue_current', why='restart_taker_pending')
    if hypot(view.x - tx, view.y - ty) > .6:
        return _intent(view, belief, 'restart_position', (tx, ty), why='restart_taker_to_spot')
    options, opps = _throw_options(view, belief, kind, x, y)
    safe_only = view.cognition == 'native-rb/3' and 'A1' in getattr(view, 'rb319', '')
    if safe_only:                      # RB-3.19 A1: the passes' release-time lane check; speed by distance (below)
        from . import cognition_rb3 as R3
        from .throw_speed import release_speed
        tracks = {t.entity: t for t in _fresh(view, belief, TRACK_FRESH_MS)}
        fopps = [t for t in opps if t.role != 'archer']
        t_rel = R3.release_time_s(view)
        options = [o for o in options if R3.lane_margin(view, tracks[o[1]], fopps,
                                                         release_speed(hypot(o[2][0] - view.x, o[2][1] - view.y), view.max_throw_speed), t_rel) >= 0]
    latest = belief.own_feedback[-1] if belief.own_feedback else None
    if latest and latest[1].startswith('rejected_') and latest[1].endswith(':restart_pass') and len(options) > 1:
        options.remove(max(options, key=lambda o: (o[3], o[1])))     # the throw just refused: try another
    last_call = window - elapsed <= 1500
    if kind == 'toss':
        clear = not any(hypot(o.x - x, o.y - y) < TOSS_CLEARANCE_M for o in opps)
        legal_now = elapsed >= TOSS_MIN_WAIT_MS - RELEASE_MS and (clear or last_call)
    else:
        sg = view.attack_sign
        line = 40. if kind == 'snap40' else None
        def onside(t):
            if kind == 'snap40':
                return abs(t.x - view.own_goal_x) <= 40.
            return sg * (t.x - x) <= 0.
        mates_set = all(onside(t) for t in _fresh(view, belief, TRACK_FRESH_MS)
                        if t.team == view.team and t.role != 'archer')
        legal_now = bool(ready) or (last_call and mates_set)
    if not legal_now:
        return _intent(view, belief, 'restart_wait', options=[('restart_wait', None, None, 0.)] + options,
                       why='restart_taker_waits_for_legal_release')
    if not options:
        if not last_call and not safe_only:
            return _intent(view, belief, 'restart_wait', why='restart_taker_no_believed_target')
        ux, uy = _spot_side(x, y)
        if kind != 'toss':
            ux, uy = -view.attack_sign, 0.
        # PLACEHOLDER: no believed legal teammate before the deadline: throw to legal space.
        aim = (round(_clamp(x + ux * 8., 1., 99.), 3), round(_clamp(y + uy * 8., 1., 99.), 3))
        if safe_only:                  # RB-3.19 A1: an in-field space aim (toward the middle of the field), distance-based speed
            cx, cy = 50. - x, 50. - y
            cl = hypot(cx, cy) or 1.
            aim = (round(_clamp(x + cx / cl * 8., 2., 98.), 3), round(_clamp(y + cy / cl * 8., 2., 98.), 3))
        i, r = _intent(view, belief, 'restart_pass', aim, None, why='restart_taker_space_placeholder')
        return (_distance_speed(view, i), r) if safe_only else (i, r)
    chosen = max(options, key=lambda o: (o[3], o[1]))
    i, r = _intent(view, belief, chosen[0], chosen[2], chosen[1],
                   options=[('restart_wait', None, None, 0.)] + options, why='restart_taker_throw')
    return (_distance_speed(view, i), r) if safe_only else (i, r)


def _claim(view, belief, tx, ty, created, snapper):
    """Claim when I believe I am the nearest teammate. An athlete cannot see every
    teammate, so he also holds back in proportion to his own distance: the nearer
    an athlete is, the sooner he may claim (no knowledge of others needed)."""
    if snapper == view.athlete:
        return True
    own = hypot(view.x - tx, view.y - ty)
    if view.delivered_ms - created < own * CLAIM_BACKOFF_MS_PER_M:
        return False
    closer = sum(1 for t in _fresh(view, belief) if t.team == view.team and t.role == 'field'
                 and hypot(t.x - tx, t.y - ty) < own - .5)
    return closer <= max(0, view.delivered_ms - created) // CLAIM_WIDEN_MS


def _stand(view, belief, kind, team, x, y, tx, ty, taker, tackler):
    """Where an athlete who is not the taker stands: legal first, then available."""
    mine = team == view.team
    sg = view.attack_sign if mine else -view.attack_sign      # the restarting team's attack sign
    px, py = view.x, view.y
    why = 'restart_stand'
    if kind == 'snap40':
        px = min(px, 39.5) if view.own_goal_x == 0 else max(px, 60.5)
    elif kind == 'toss':
        dx, dy = px - x, py - y
        d = hypot(dx, dy)
        if not mine and d < TOSS_CLEARANCE_M + 1.5:
            ux, uy = (dx / d, dy / d) if d > .01 else _spot_side(x, y)
            px, py = x + ux * (TOSS_CLEARANCE_M + 2.), y + uy * (TOSS_CLEARANCE_M + 2.)
            why = 'restart_toss_clearance'
    elif view.athlete == tackler:
        px, py = x + sg * 5.5, y
        why = 'restart_tackler_retires'
    else:
        if mine and sg * (px - x) > -.5: px = x - sg * .8
        if not mine and sg * (px - x) < .5: px = x + sg * .8
    if mine and view.role == 'field' and view.athlete != taker:
        # PRIMITIVE availability: the two believed-nearest teammates who are not the taker
        # stand at a throwable distance from the spot (legal side), so a legal target exists.
        mates = sorted((hypot(t.x - x, t.y - y), t.entity) for t in _fresh(view, belief)
                       if t.team == view.team and t.role == 'field' and t.entity != taker)
        own = hypot(view.x - x, view.y - y)
        rank = sum(1 for d, _ in mates if d < own)
        if rank < 2 and not SUPPORT_NEAR_M <= hypot(px - x, py - y) <= SUPPORT_FAR_M:
            if kind == 'toss':
                ux, uy = _spot_side(x, y)
            else:
                ux, uy = -sg, 0.                          # behind the ball line / inside own 40
            lat = 6. if rank == 0 else -6.
            px, py = x + ux * 8. - uy * lat, y + uy * 8. + ux * lat
            if not 3. <= py <= 97.: py = y + uy * 8. - ux * lat
            if not 3. <= px <= 97.: px = x + ux * 8. + uy * lat
            why = 'restart_support'
    if taker and hypot(px - tx, py - ty) < 2.:
        py = ty + (2. if view.athlete < taker else -2.)       # physical room for the taker
    aim = (round(_clamp(px, .01, 99.99), 3), round(_clamp(py, .01, 99.99), 3))   # same legal extent as v0/2
    return _intent(view, belief, 'restart_position', aim, why=why)


def _formation(view, belief, kind, team, x, y, tx, ty, taker, ready, form):
    """RB-3.9a (native-rb/3): set scrimmage formation. The snapper snaps straight back to the
    designated receiver at a distance-chosen speed; everybody else holds the spot he was placed on."""
    from .throw_speed import release_speed
    snapper, receiver, rx, ry, mx, my = form
    hold = (mx, my) if mx is not None else (round(view.x, 3), round(view.y, 3))
    if view.athlete != snapper:
        return _intent(view, belief, 'restart_position', hold, why='formation_hold')
    if taker is None:
        return _intent(view, belief, 'restart_claim', why='formation_snapper_claim')
    if taker != view.athlete:
        return _intent(view, belief, 'restart_position', hold, why='formation_hold')
    if view.pending_command_id is not None:
        return _intent(view, belief, 'continue_current', why='formation_snap_pending')
    if hypot(view.x - tx, view.y - ty) > .6:
        return _intent(view, belief, 'restart_position', (tx, ty), why='formation_snapper_to_spot')
    if not ready or receiver is None:
        return _intent(view, belief, 'restart_wait', why='formation_wait_for_set')
    speed = release_speed(hypot(rx - x, ry - y), view.max_throw_speed)
    i, r = _intent(view, belief, 'restart_pass', (rx, ry), receiver, why='formation_snap')
    return replace(i, speed=speed), dict(r, snap_speed=speed)


def restart_decide(view, belief):
    rid, kind, team, x, y, tx, ty, taker, snapper, tackler, created, ready = view.restart
    form = getattr(view, 'formation', None)
    if view.cognition == 'native-rb/3' and form is not None and kind in ('scrim', 'snap40'):
        return _formation(view, belief, kind, team, x, y, tx, ty, taker, ready, form)
    if (taker is None and team == view.team and (snapper is None or snapper == view.athlete)
            and (view.role == 'field' or snapper == view.athlete)
            and _claim(view, belief, tx, ty, created, snapper)):
        return _intent(view, belief, 'restart_claim', why='restart_claim_believed_nearest')
    if taker == view.athlete:
        return _taker(view, belief, kind, team, x, y, tx, ty, created, ready)
    return _stand(view, belief, kind, team, x, y, tx, ty, taker, tackler)


# ================================================================== decide
def decide(view, belief):
    """native-v0/3: v0/2 decision set with restart and contact decisions replaced."""
    if view.observation_id != belief.observation_id:
        raise ValueError('provenance mismatch')
    if view.restart is not None and view.role != 'archer' and not view.bench_role:
        return restart_decide(view, belief)
    intent, record = C.decide_v2(view, belief)
    if intent.kind == 'press' and (not view.registry_ratings or view.prism_agent in
                                   ('defending', 'zone_coverage') or view.own_hold_target is not None):
        return defender_contact(view, belief, intent, record)
    if intent.kind == 'carry' and view.holds_ball and view.role == 'field' and view.pending_command_id is None:
        return carrier_contact(view, belief, intent, record)
    return intent, record
