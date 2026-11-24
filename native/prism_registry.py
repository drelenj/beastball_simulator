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
        if course is not None and course.z > .45:
            return 'in_air_ball_pursuit'
        if not any(t.role != 'ball' and hypot(t.x - ball.x, t.y - ball.y) < 1.8
                   for t in belief.tracks):
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
