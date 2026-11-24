"""RB-3.24 rating names and athlete-owned decision boundaries."""
from math import hypot

# Ordered legacy sources when a new column is absent. Earlier sources win.
ALIASES = {
    'judgment': 'defending',
    'motor_control': 'agility',
    'keeper_skill': 'goalkeeping',
    'marking': 'defending',
    'zone_reads': 'zone_coverage',
    'defender_duel': 'takedown',
    'carrier_duel': 'evasion',
    'contact_resistance': 'evasion',
}
LEGACY_SOURCES = {
    'defending': ('marking', 'judgment'),
    'zone_coverage': ('zone_reads',),
    'goalkeeping': ('keeper_skill',),
    'evasion': ('carrier_duel', 'contact_resistance'),
    'takedown': ('defender_duel',),
    'agility': ('motor_control',),
}
MANEUVERS = ('juke', 'spin', 'hurdle', 'stiff_arm', 'truck')
NEW_RATINGS = ('defending', 'zone_coverage', 'disruption', 'passing',
               'evasion', 'takedown', 'reflex')
AGENTS = ('playmaking', 'defending', 'zone_coverage', 'goalkeeping',
          'disruption', 'in_air_ball_pursuit', 'live_ball_pursuit')
SUBAGENTS = {
    'pass': 'passing', 'shoot': 'finishing',
    'stiff_arm': 'evasion', 'truck': 'evasion', 'stretch': 'evasion',
}
AVERAGE = .70


def effective_ratings(values, defaults=()):
    """Resolve aliases without mutating the original compatibility roster."""
    explicit = values.keys() - set(defaults)
    resolved = {}
    for name, aliases in LEGACY_SOURCES.items():
        source = name if name in explicit else next((key for key in aliases if key in explicit), None)
        resolved[name] = values[source] if source else values.get(name, AVERAGE)
    return resolved


def roster_ratings(values, defaults, provenance, source_columns):
    names = (*NEW_RATINGS, 'awareness', 'agility')
    ratings = {name: values.get(name, AVERAGE) for name in names}
    ratings.update(effective_ratings(values, defaults))
    sources = dict(provenance or source_columns)
    source = sources.get('awareness')
    if source is not None and not source.startswith('explicit:'):
        ratings['awareness'] = AVERAGE
        sources['awareness'] = '0.70 radar fallback'
    if provenance and sources.get('evasion') == 'alias:contact_resistance' and not dict(
            source_columns).get('contact_resistance', '').startswith('explicit:'):
        # The historical body-balance proxy is not authored Evasion.
        ratings['evasion'] = AVERAGE
        sources['evasion'] = '0.70 default'
    return ratings, sources


def select_agent(view, belief, rating):
    """Choose from delivered tracks, own possession and the player's ratings."""
    if view.role == 'keeper':
        return 'goalkeeping'
    if view.role == 'archer':
        return 'disruption'
    if view.holds_ball:
        return 'playmaking'
    ball = next((t for t in belief.tracks if t.role == 'ball'), None)
    course = belief.ball_course
    if ball is not None:
        read = getattr(view, 'recognized_ball', None)
        if read in ('pass', 'shot') or (read is None and course is not None and course.z > .45):
            return 'in_air_ball_pursuit'
        if read == 'loose' or (read != 'held' and not any(t.role != 'ball' and hypot(t.x - ball.x, t.y - ball.y) < 1.8
                   for t in belief.tracks)):
            return 'live_ball_pursuit'
    if view.signals.passive_team == view.team:
        return 'playmaking'
    return 'zone_coverage' if rating(view, 'zone_coverage') > rating(view, 'defending') else 'defending'


def commit_owner(intent):
    if intent.kind in SUBAGENTS:
        return SUBAGENTS[intent.kind]
    if intent.contact in ('wrap', 'takedown'):
        return 'takedown'
    if intent.contact in ('dodge', 'run_through', 'brace'):
        return 'evasion'
    return None

RADAR_BASE_M, RADAR_RANGE_M = 6., 8.
CLARITY_BASE_SD_M, CLARITY_OFFSET, CLARITY_RANGE = .04, 1.4, .6
RECOGNITION_MAX_ERROR, IN_FLIGHT_Z_M, SHOT_READ_SPEED = .20, .45, 35.
FOCUS_MIN_TRACKS, FOCUS_EXTRA_TRACKS = 4, 8
FOCUS_MIN_MS, FOCUS_EXTRA_MS, FOCUS_DRIFT_MPS = 1400, 600, .5
INSTINCT_CORRECTION, FORECAST_UNCERTAINTY = .6, .25
REFLEX_BASE_S, REFLEX_RANGE_S = .55, .35
PASS_SPEED_RANGE, PASS_ARC_RANGE_M = .20, .8
DISRUPTION_HOLD_WEIGHT, DISRUPTION_CARRIER_WEIGHT = 2., 1.5
TAKEDOWN_LOAD_THRESHOLD, TAKEDOWN_LOAD_RANGE = .5, .8


def radar_radius(awareness):
    return RADAR_BASE_M + RADAR_RANGE_M * awareness


def clarity_sd(clarity):
    return CLARITY_BASE_SD_M * (CLARITY_OFFSET - CLARITY_RANGE * clarity)


def recognize(course, clarity, draw, tracks=()):
    """Classify a delivered sighting. The draw belongs to the sensor stream."""
    if course is None:
        return None
    if any(t.role != 'ball' and hypot(t.x - course.x, t.y - course.y) < 1.8
           and hypot(t.vx - course.vx, t.vy - course.vy) < 3 for t in tracks):
        return 'held'
    if course.z <= IN_FLIGHT_Z_M:
        label = 'loose'
    elif hypot(course.vx, course.vy) >= SHOT_READ_SPEED:
        label = 'shot'
    else:
        label = 'pass'
    if draw < RECOGNITION_MAX_ERROR * (1 - clarity):
        return {'loose': 'pass', 'pass': 'shot', 'shot': 'loose'}[label]
    return label


def memory_limit(focus):
    return round(FOCUS_MIN_TRACKS + FOCUS_EXTRA_TRACKS * focus)


def retention_ms(focus):
    return round(FOCUS_MIN_MS + FOCUS_EXTRA_MS * focus)


def forecast_factor(anticipation):
    """Conservative velocity estimate as forecast uncertainty increases."""
    return 1 - FORECAST_UNCERTAINTY * (1 - anticipation)


def reflex_seconds(reflex):
    return REFLEX_BASE_S - REFLEX_RANGE_S * reflex


def remembered_position(track, now, focus, instinct, observed_ms):
    """Project only a remembered sighting. Its age and identity stay intact."""
    if track.captured_ms >= observed_ms:
        return track.x, track.y
    age = max(0., (now - track.captured_ms) / 1000.)
    error = FOCUS_DRIFT_MPS * (1 - focus) * age
    error *= 1 - INSTINCT_CORRECTION * instinct
    speed = hypot(track.vx, track.vy)
    ux, uy = ((-track.vy / speed, track.vx / speed) if speed else (1., 0.))
    return track.x + track.vx * age + ux * error, track.y + track.vy * age + uy * error


def filter_velocity(previous, measured, instinct):
    corrected = 1 - INSTINCT_CORRECTION * instinct
    return tuple(old + corrected * (new - old) for old, new in zip(previous, measured))


def pass_delivery(distance, ceiling, nominal_speed, passing):
    deviation = passing - AVERAGE
    return min(ceiling, nominal_speed * (1 + PASS_SPEED_RANGE * deviation)), (
        1.6 + PASS_ARC_RANGE_M * deviation * min(1., distance / 25.))
