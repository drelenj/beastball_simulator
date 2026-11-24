"""PRISM I option evaluation from athlete observations only.

All option values in this module are PROVISIONAL - TO BE REPLACED BY ORACLE DRILL.
The caller supplies a seed for this athlete and decision, never engine state.
"""
from dataclasses import dataclass, replace
from hashlib import blake2s
from math import hypot

from . import cognition as C, cognition_rb3 as RB
from .throw_speed import release_speed

VERSION = 'individuation/2'
FOCUS_BASE_CAPACITY = 20
FOCUS_BASE_RETENTION_MS = 2000
# PROVISIONAL - TO BE REPLACED BY ORACLE DRILL.
ERROR_WIDTH = .75
SHOT_VALUE_OFFSET = -1.40
EVADE_PRESSURE_VALUE = 2.5
GOAL_CARRY_VALUE = 1.0
AREA_DISTANCE_WEIGHT = .045
AREA_INSIDE_VALUE = .85
BLOCK_DISTANCE_M = 3.
BLOCK_VALUE = .8
PASS_WAIT_COST = .22
PASS_ARC_COST = .25
PASS_BOUNCE_COST = .65
PASS_LANE_GAIN = .12
PASS_WAIT_VELOCITY_MPS = 1.6
KEEPER_SET_VALUE, KEEPER_SAVE_VALUE = 1., 1.15
KEEPER_SAVE_TIME_VALUE = .6
KEEPER_SHIFT_COST = .3
ARCHER_WAIT_VALUE = .65
PURSUIT_INTERCEPT_COST = .12
ANTICIPATION_RANGE = .25
STRETCH_BELIEVED_RANGE_MARGIN = .45
STRETCH_VALUE = 13.
GRIP_VALUE = .3
GRIP_SPEED_WEIGHT = .06
LATE_REFLEX_CLOSE_M = 2.5
LATE_REFLEX_MAX_AGE_S = .6
DODGE_RANGE_M = 1.6
WRAP_TACKLE_DISTANCE_M = 2.2
WRAP_TACKLE_VALUE = .35


@dataclass(frozen=True)
class Option:
    intent: C.ActionIntent
    value: float
    owner: str
    label: str


class Menu:
    """Fresh deterministic draws of symmetric error for each valued option."""

    def __init__(self, view, selector=None):
        self.ratings = dict(view.registry_ratings)
        self.seed = view.core_entropy
        self.records = []
        self.selector = selector

    def choose(self, name, options):
        if not options:
            raise ValueError(f'{name}: no feasible option')
        # Define the stream by the decision stage. Option enumeration comes
        # from sorted athlete tracks and fixed candidate grids.
        if len(options) == 1:
            ranked = [(options[0].value, 0, options[0])]
        else:
            entropy = blake2s(f'{self.seed}/{name}'.encode(), digest_size=8 * min(4, len(options))).digest()
            stream = int.from_bytes(entropy, 'little')
            ranked = []
            for index, option in enumerate(options):
                if index and index % 4 == 0:
                    stream = int.from_bytes(blake2s(entropy + index.to_bytes(2, 'big')).digest(), 'little')
                unit = ((stream & ((1 << 64) - 1)) >> 11) / (1 << 53)
                stream >>= 64
                spread = ERROR_WIDTH * (1 - self.ratings.get(option.owner, .7))
                ranked.append((option.value + spread * (2 * unit - 1), -index, option))
        chosen = self.selector(name, tuple(options)) if self.selector is not None else None
        if chosen is not None and not 0 <= chosen < len(options):
            raise ValueError(f'{name}: option index {chosen} is outside the menu')
        best = max(ranked)[2] if chosen is None else options[chosen]
        self.records.append({
            'stage': name,
            'owner': best.owner,
            'choice': best.label,
            'options': [(option.label, option.owner, option.value, believed)
                        for believed, _, option in ranked],
        })
        return best


def displayed(view):
    """The historical candidate builders run with their fixed provisional values."""
    return replace(view, registry_ratings=(), individual_ratings=())


def proposed(base, kind, target=None, aim=None, **kwargs):
    return replace(base, kind=kind, target=target, aim=aim, contact=None, **kwargs)


def finish(menu, view, base, tracks):
    goal_x = 100. - view.own_goal_x
    stretch = (view.role == 'field' and view.body and getattr(view, 'rb3_carrier_moves_enabled', False) and
               abs(goal_x-view.x) <= view.body.reach + STRETCH_BELIEVED_RANGE_MARGIN and abs(view.y-50.) < view.goal_radius)
    if stretch:
        hands = proposed(base, 'stretch', aim=(goal_x, view.y))
        alternatives = [Option(hands, STRETCH_VALUE, 'finishing', 'stretch')]
        if base.kind == 'shoot':
            alternatives.append(Option(base, STRETCH_VALUE-1., 'finishing', 'throw'))
        base = menu.choose('scoring_technique', alternatives).intent
    if base.kind == 'stretch':
        # Aim inside the existing goal mouth. The motor limits hand reach.
        options = [Option(replace(base, aim=(base.aim[0], y)), -abs(y-view.y), 'finishing', f'stretch:{y:.2f}')
                   for y in (50., max(48., min(52., view.y)))]
        return menu.choose('finishing', options).intent
    keeper = next((t for t in tracks if t.team != view.team and t.role == 'keeper'), None)
    speed = RB.shot_speed(view)
    gx = base.aim[0]
    t = RB.release_time_s(view) + abs(gx - view.x) / max(1., speed)
    ky = keeper.y + keeper.vy * t if keeper else 50.
    kz = .62 * dict(getattr(view, 'body_height', ())).get(keeper.entity, 2.39) if keeper else 1.5
    plan = RB.shot_plan(view, tracks)
    if plan is None:
        return base
    field = [t for t in tracks if t.role == 'field' and t.team != view.team]
    margin = plan['margin'] if keeper else -abs(base.aim[1]-50.) * .05
    options = [Option(replace(base, speed=speed, height=plan['z']), margin, 'finishing', 'selected_lane')]
    # Reuse the historical radial envelope. Reach is a common offset for all
    # candidates and cannot bias their rank by athlete rating.
    reach = RB.keeper_lateral_reach(view, keeper) if keeper else 0.
    for dy, z in ((-2.4, .4), (2.4, .4), (0., 2.0), (0., 1.2)):
        y = 50. + dy
        if hypot(dy, z) > view.goal_radius - RB.SHOT_BALL_R_M - RB.SHOT_EDGE_M:
            continue
        if field and RB.lane_margin(view, Aim(gx, y), field, speed) < 0:
            continue
        if (gx, y) == base.aim and z == plan['z']:
            continue
        value = (hypot(y - ky, z - kz) - reach) if keeper else -abs(dy)*.05
        options.append(Option(replace(base, aim=(gx, y), height=z, speed=speed),
                              value, 'finishing', f'shot:{dy}:{z}'))
    return menu.choose('finishing', options).intent


@dataclass(frozen=True)
class Aim:
    x: float
    y: float


def passing(menu, view, base, tracks):
    receiver = next((t for t in tracks if t.entity == base.target and t.team == view.team), None)
    distance = hypot(base.aim[0] - view.x, base.aim[1] - view.y)
    nominal = release_speed(distance, view.max_throw_speed)
    choices = [Option(replace(base, speed=nominal), 1., 'passing', 'direct')]
    if receiver is None:
        return menu.choose('passing', choices).intent
    opponents = [t for t in tracks if t.team not in (view.team, 'ball') and t.role == 'field']
    if not opponents:
        return menu.choose('passing', choices).intent
    interval = round(view.core_decision_ms * (1. + .4 * (.7 - menu.ratings.get('reaction', .7))))
    release = RB.release_time_s(view)
    nominal_margin = RB.lane_margin(view, Aim(*base.aim), opponents, nominal, release)
    for label, wait, factor, height, cost in (
            ('fast', 0, 1.20, 1.6, PASS_ARC_COST),
            ('loft', 0, .88, 2.4, PASS_ARC_COST),
            ('bounce', 0, 1.10, .1075, PASS_BOUNCE_COST),
            ('wait', interval // 2, 1., 1.6, PASS_WAIT_COST)):
        if wait and hypot(receiver.vx, receiver.vy) < PASS_WAIT_VELOCITY_MPS:
            continue
        aim = tuple(min(98., max(2., a + vel * wait / 1000))
                    for a, vel in zip(base.aim, (receiver.vx, receiver.vy)))
        if label == 'bounce':
            aim = ((view.x + 2 * aim[0]) / 3, (view.y + 2 * aim[1]) / 3)
        if not C.in_own_zone(view.team, view.x, view.y, view) and C.in_own_zone(view.team, *aim, view):
            continue
        speed = min(view.max_throw_speed, nominal * factor)
        margin = RB.lane_margin(view, Aim(*aim), opponents, speed, release + wait / 1000)
        if margin < 0.:
            continue
        lane_gain = min(4., margin - nominal_margin)
        intent = replace(base, aim=aim, speed=speed, height=height, wait_ms=wait,
                         technique='bounce' if label == 'bounce' else label)
        choices.append(Option(intent, 1. + PASS_LANE_GAIN * lane_gain - cost, 'passing', label))
    return menu.choose('passing', choices).intent


def evade(menu, view, base, threat, near_held):
    owner = 'evasion'
    if threat is None:
        options = [Option(replace(base, contact='run_through'), 1. - view.own_balance_load, owner, 'run_through'),
                   Option(replace(base, aim=(view.x, view.y), contact='brace'), .35, owner, 'brace')]
        return menu.choose(owner, options).intent
    d = hypot(threat.x - view.x, threat.y - view.y)
    side = -1. if threat.y >= view.y else 1.
    aim = (min(99., max(1., view.x + view.attack_sign * 3.)),
           min(97., max(3., view.y + side * 4.)))
    options = [Option(replace(base, contact='run_through'), 1. - view.own_balance_load, owner, 'run_through')]
    options += [Option(replace(base, aim=aim, contact='dodge', technique=technique),
                       1.05 - abs(d - preferred) * .25, owner, technique)
                for technique, preferred in (('juke', 2.), ('spin', 1.), ('hurdle', 3.))]
    old_motion = view.core_motion
    if old_motion and old_motion[1] in ('juke', 'spin', 'hurdle'):
        _, technique, old_aim, started = old_motion
        reflex = menu.ratings.get('reflex', .7)
        age = (view.delivered_ms - started) / 1000.
        own_vx, own_vy = (view.body.vx,view.body.vy) if view.body else (0.,0.)
        closing = ((own_vx-threat.vx)*(threat.x-view.x) + (own_vy-threat.vy)*(threat.y-view.y))/max(.01,d)
        if (old_aim and old_aim != aim and 0 < age <= LATE_REFLEX_MAX_AGE_S
                and d <= LATE_REFLEX_CLOSE_M and closing > 0. and d/closing >= .55-.35*reflex):
            blended = tuple(old + reflex * (new - old) for old, new in zip(old_aim, aim))
            options.append(Option(replace(base, aim=blended, contact='dodge', technique=technique),
                                  1.15, owner, 'late_dodge_adjustment'))
    if view.body and getattr(view, 'rb3_carrier_moves_enabled', False) and threat.role == 'field':
        if d <= view.body.reach + .35:
            options.append(Option(proposed(base,'stiff_arm',threat.entity,aim, technique='stiff_arm'),
                                  1.05 if near_held else .84, owner, 'stiff_arm'))
        if view.attack_sign * (threat.x - view.x) > 0.:
            options.append(Option(proposed(base,'truck',threat.entity,(threat.x,threat.y),technique='truck'),
                                  .7 + .05 * hypot(view.body.vx,view.body.vy), owner, 'truck'))
    return menu.choose(owner, options).intent


def carrier(menu, view, belief, tracks, base, record):
    near = min((t for t in tracks if t.role == 'field' and t.team != view.team
                and t.entity not in view.signals.immune),
               key=lambda t: (hypot(t.x - view.x, t.y - view.y), t.entity), default=None)
    gap = hypot(near.x - view.x, near.y - view.y) if near else 99.
    choices = []
    for kind, target, aim, value in record['options']:
        if kind not in ('carry', 'pass', 'handoff', 'shoot', 'retain'):
            continue
        if kind == 'pass' and aim and not C.in_own_zone(view.team, view.x, view.y, view) and C.in_own_zone(view.team,*aim,view):
            continue
        intent = proposed(base, kind, target, aim)
        value += SHOT_VALUE_OFFSET if kind == 'shoot' else 0.
        choices.append(Option(intent, value, 'playmaking', f'{kind}:{target or ""}'))
        if kind == 'carry':
            direct, _ = RB.carrier_to_goal(displayed(view), belief, intent, {})
            if direct != intent:
                choices.append(Option(direct, value + GOAL_CARRY_VALUE, 'playmaking', 'carry_goal'))
        if kind == 'carry' and (gap < 4. or view.own_held):
            choices.append(Option(replace(intent, technique='evade'), value + EVADE_PRESSURE_VALUE * max(0.,1-gap/4.),
                                  'playmaking', 'evade'))
    goal = 100. - view.own_goal_x
    if (view.role == 'field' and view.body and getattr(view,'rb3_carrier_moves_enabled',False)
            and abs(goal-view.x) <= view.body.reach + STRETCH_BELIEVED_RANGE_MARGIN and abs(view.y-50.) < view.goal_radius
            and not any(choice.intent.kind == 'shoot' for choice in choices)):
        choices.append(Option(proposed(base,'stretch',aim=(goal,view.y)),STRETCH_VALUE,
                              'playmaking','commit_scoring_attempt'))
    if not choices:
        choices.append(Option(proposed(base, 'retain'), 0., 'playmaking', 'retain'))
    picked = menu.choose('carrier', choices).intent
    # Preserve the existing evidence-only zone exit policy.
    picked, _ = RB.zone_behavior(displayed(view), belief, picked, {})
    if picked.kind == 'pass':
        return passing(menu, view, picked, tracks)
    if picked.kind in ('shoot', 'stretch'):
        return finish(menu, view, picked, tracks)
    if picked.kind == 'carry' and (picked.technique == 'evade' or view.own_held):
        return evade(menu, view, picked, near if gap < 4. else None, bool(view.own_held))
    return picked


def defender(menu, view, belief, tracks, base, record):
    opps = [t for t in tracks if t.team not in (view.team, 'ball') and t.role == 'field']
    nearest = min(opps, key=lambda t: (hypot(t.x-view.x,t.y-view.y),t.entity), default=None)
    dist = hypot(nearest.x-view.x,nearest.y-view.y) if nearest else 25.
    inside = C.in_own_zone(view.team,view.x,view.y,view)
    area = C.position_from_belief(view, view.x, True)
    options = [Option(proposed(base,'position',aim=area),
                      .5 + AREA_DISTANCE_WEIGHT * dist + (AREA_INSIDE_VALUE if inside else 0.),
                      'zone_coverage','area')]
    own_hold = view.own_hold_target
    for kind, target, aim, value in record['options']:
        if kind in ('mark','press','receive','pursue'):
            options.append(Option(proposed(base,kind,target,aim),value,'defending',kind))
        if kind == 'press' and target:
            options.append(Option(replace(proposed(base,kind,target,aim),contact='wrap'),value + .2,'defending','wrap'))
            opponent = next((t for t in opps if t.entity == target), None)
            if opponent and hypot(opponent.x-view.x, opponent.y-view.y) < WRAP_TACKLE_DISTANCE_M:
                options.append(Option(replace(proposed(base,'tackle',target,aim),contact='takedown'),
                                      value + WRAP_TACKLE_VALUE,'defending','commit_takedown'))
    carrier_id = (record.get('believed_carrier') or (None,))[0]
    if nearest and nearest.entity != carrier_id and dist <= BLOCK_DISTANCE_M and getattr(view,'rb3_handoff_block_enabled',False):
        options.append(Option(proposed(base,'block',nearest.entity,(view.own_goal_x,50.)),BLOCK_VALUE,'defending','block'))
    held = next((t for t in opps if t.entity == own_hold),None)
    if held:
        options = []
        for style in ('wrap','takedown'):
            for grip in ('upper','lower'):
                value = .9 + (1. - view.own_balance_load if style == 'takedown' else view.own_balance_load)
                running = hypot(held.vx, held.vy)
                value += GRIP_SPEED_WEIGHT * running if grip == 'lower' else GRIP_VALUE
                options.append(Option(replace(proposed(base,'tackle',held.entity,(held.x,held.y)),
                                              contact=style, technique=grip),value,'takedown',f'{style}:{grip}'))
        return menu.choose('takedown',options).intent, 'defending'
    selected = menu.choose('defense',options)
    result, _ = RB.defender_baseline(displayed(view),belief,selected.intent,{})
    return result, selected.owner


def keeper_options(menu, view, base):
    original = base.auxiliary
    center = (view.own_goal_x + view.attack_sign * 2., 50.)
    if original.kind == 'save':
        window = (original.intercept_window_ms[1]-view.delivered_ms)/1000.
        poised = replace(original, kind='position', target=center, course=())
        options = [Option(base, KEEPER_SAVE_VALUE + KEEPER_SAVE_TIME_VALUE * min(window,.6), 'goalkeeping','save'),
                   Option(replace(base, auxiliary=poised), KEEPER_SET_VALUE,'goalkeeping','set')]
    elif original.kind == 'position':
        resting = replace(original, kind='hold', target=(view.x,view.y))
        gap = hypot(original.target[0]-view.x,original.target[1]-view.y)
        options = [Option(base, KEEPER_SET_VALUE, 'goalkeeping','position'),
                   Option(replace(base, auxiliary=resting),KEEPER_SET_VALUE-KEEPER_SHIFT_COST*min(3.,gap),
                          'goalkeeping','hold')]
    else:
        options = [Option(base,KEEPER_SET_VALUE,'goalkeeping','hold')]
    return menu.choose('keeper', options).intent


def future_course(belief, rating):
    course = belief.ball_course
    if course is None:
        return belief
    factor = 1. - ANTICIPATION_RANGE * (.70-rating)
    return replace(belief, ball_course=replace(course, vy=course.vy * factor, vz=course.vz * factor))


def decide(view, belief, *, selector=None):
    if view.observation_id != belief.observation_id:
        raise ValueError('belief/view provenance mismatch')
    baseline = displayed(view)
    if (view.restart or view.hunt and not view.hunt_cleared or view.bench_role or
            view.signals.phase != 'live' or getattr(view, 'snap_hold', False)):
        from . import cognition_v3
        return RB.adjust(baseline, belief, *cognition_v3.decide(baseline, belief))
    menu = Menu(view, selector)
    if view.pending_command_id or view.role == 'keeper' and not view.holds_ball:
        forecast = belief
        course = belief.ball_course
        if view.role == 'keeper' and course and course.vx * view.attack_sign < 0:
            forecast = future_course(belief, menu.ratings.get('anticipation',.7))
        base, record = C.decide_v2(baseline,forecast)
        if view.role == 'keeper' and base.auxiliary:
            base = keeper_options(menu,view,base)
        if view.role == 'archer' and base.kind == 'release_arrow':
            base = menu.choose('archer_release', [
                Option(base,1.,'disruption','release'),
                Option(replace(base,kind='continue_current'),ARCHER_WAIT_VALUE,'disruption','wait')]).intent
        return base, dict(record, core_menus=menu.records, prism_agent={'keeper':'goalkeeping','archer':'disruption'}.get(view.role,'playmaking'))
    base, record = C._base_decide(baseline,belief,compact=True)
    base = replace(base,period=view.signals.period)
    tracks = tuple(t for t in belief.tracks if 0 <= view.delivered_ms-t.captured_ms <= belief.max_track_age_ms)
    if view.holds_ball:
        intent, agent = carrier(menu,view,belief,tracks,base,record), 'playmaking'
    elif view.role == 'archer':
        eligible = {t.entity:t for t in tracks}
        options = [Option(proposed(base,k,t,a),value,'disruption',f'{k}:{t or ""}')
                   for k,t,a,value in record['options'] if k != 'draw_release' or getattr(view,'freezes_left',1)]
        intent = menu.choose('archer',options).intent
        if intent.target in eligible:
            target = eligible[intent.target]
            intent = replace(intent,aim_vel=(target.vx,target.vy))
        agent = 'disruption'
    elif record.get('believed_carrier') is None:
        agent = 'in_air_ball_pursuit' if belief.ball_course and belief.ball_course.z > .45 else 'live_ball_pursuit'
        options = []
        for k,t,a,v in record['options']:
            if k == 'pursue' and a and belief.ball_course:
                trust = 1. - ANTICIPATION_RANGE * (.7 - menu.ratings.get('anticipation',.7))
                course = belief.ball_course
                a = (course.x + (a[0]-course.x)*trust, course.y + (a[1]-course.y)*trust)
            options.append(Option(proposed(base,k,t,a),v,agent,k))
            if k == 'pursue' and a and belief.ball_course and agent == 'in_air_ball_pursuit':
                course = future_course(belief,menu.ratings.get('anticipation',.7)).ball_course
                flight = min(.8, RB.flight_horizon(course))
                landing = (max(1.,min(99.,course.x + flight * course.vx)),
                           max(1.,min(99.,course.y + flight * course.vy)))
                options.append(Option(proposed(base,k,t,landing),v-PURSUIT_INTERCEPT_COST,agent,'landing'))
        improved = base
        if base.kind not in ('pursue', 'receive'):
            improved, _ = RB.missed_ball_pursuit(baseline,belief,base,{})
        if improved != base:
            options.append(Option(improved,4.,agent,'intercept'))
        intent = menu.choose(agent,options).intent
    elif view.signals.passive_team != view.team:
        intent, agent = defender(menu,view,belief,tracks,base,record)
    else:
        agent = 'playmaking'
        choices = [Option(proposed(base,k,t,a),v,agent,k) for k,t,a,v in record['options']]
        blocked, _ = RB.choose_block(baseline,belief,base,record)
        if blocked != base:
            choices.append(Option(blocked,1.3,agent,'block'))
        intent = menu.choose('support',choices).intent
    if not view.holds_ball and view.role == 'field':
        # Transit and pursuit still obey the same existing zone exit policy.
        intent, _ = RB.zone_behavior(baseline,belief,intent,{})
    return intent, dict(record, core_menus=menu.records, prism_agent=agent,
                        final_selection=[intent.kind,intent.target,intent.aim,intent.contact])
