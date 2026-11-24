"""Build the versioned, machine-readable PRISM consumer index."""
import json
from pathlib import Path

from native.prism_registry import ALIASES

# tuple: name, layer, owner, status, confirmed consumer names
ROWS = [
    ('vision', 'perception', 'visual cone', 'hooked', 'native.port.NativePort.capture', 'native.individuation.visual_half_angle'),
    ('awareness', 'perception', 'radar radius', 'hooked', 'native.port.NativePort.capture', 'native.prism_registry.radar_radius'),
    ('clarity', 'perception', 'sighting precision and ball recognition', 'hooked', 'native.port.NativePort.capture', 'native.prism_registry.recognize'),
    ('focus', 'recognition', 'track capacity, retention and drift', 'hooked', 'native.port.NativePort.view', 'native.prism_registry.remembered_position'),
    ('reaction', 'recognition', 'deliberate decision cadence', 'hooked', 'native.port.NativePort.decision_interval_ms'),
    ('instinct', 'inference', 'current estimate from observed history', 'hooked', 'native.prism_registry.filter_velocity', 'native.prism_registry.remembered_position'),
    ('anticipation', 'inference', 'future ball course', 'partial', 'native.cognition._base_decide', 'native.cognition.decide_v2', 'native.cognition_rb3.missed_ball_pursuit'),
    ('playmaking', 'agent', 'offense', 'hooked', 'native.cognition._base_decide', 'native.cognition_rb3.pass_value', 'native.cognition_rb3._attacker_zone', 'native.cognition_rb3.choose_block'),
    ('defending', 'agent', 'individual defense', 'partial', 'native.cognition._base_decide', 'native.cognition_v3.defender_contact'),
    ('zone_coverage', 'agent', 'area defense', 'partial', 'native.prism_registry.select_agent', 'native.cognition_rb3._defender_zone'),
    ('goalkeeping', 'agent', 'Keeper position and push-off', 'hooked', 'native.cognition.decide_v2', 'native.port.NativePort.keeper_motor'),
    ('disruption', 'agent', 'Archer draw, hold and target preference', 'hooked', 'native.cognition._base_decide', 'native.cognition.decide_v2'),
    ('in_air_ball_pursuit', 'agent', 'airborne loose ball', 'hooked', 'native.cognition._base_decide', 'native.cognition_rb3.missed_ball_pursuit'),
    ('live_ball_pursuit', 'agent', 'ground-level loose ball', 'hooked', 'native.cognition._base_decide', 'native.cognition_rb3.missed_ball_pursuit'),
    ('passing', 'sub-agent', 'committed pass speed and height', 'partial', 'native.cognition_rb3.committed_delivery'),
    ('finishing', 'sub-agent', 'committed shot aim', 'hooked', 'native.cognition_rb3.finishing_aim'),
    ('evasion', 'sub-agent', 'maneuver and grip escape', 'partial', 'native.cognition_v3.carrier_contact', 'core_src.match.Match.c3_holds_kick'),
    ('takedown', 'sub-agent', 'drive or maintain own established wrap', 'partial', 'native.cognition_v3.defender_contact'),
    ('reflex', 'motor control', 'catch and save preparation and contact cadence', 'partial', 'native.port.NativePort.reflex_catch_ready_at', 'native.port.NativePort.prism_decision_interval_ms', 'native.port.NativePort.keeper_motor'),
    ('speed', 'execution', 'speed limit', 'hooked', 'native.roster.mapped_values', 'core_src.match.Match.c3_move'),
    ('acceleration', 'execution', 'propulsion acceleration', 'hooked', 'native.roster.mapped_values', 'core_src.match.Match.c3_move'),
    ('agility', 'execution', 'braking, turning and aim precision', 'hooked', 'native.roster.mapped_values', 'native.individuation.movement_aim'),
    ('strength', 'execution', 'contact forces', 'hooked', 'native.rulebook.handoff_block.block_power', 'core_src.match.Match.c3_move'),
    ('balance', 'execution', 'recovery and balance resistance', 'hooked', 'core_src.match.Match.c3_move', 'core_src.match.Match.c3_recover'),
    ('stamina', 'execution', 'fatigue', 'hooked', 'core_src.match.Match.c3_move'),
    ('jump', 'execution', 'jump height', 'hooked', 'native.roster.mapped_values', 'native.port.NativePort.keeper_motor'),
    ('throw_accuracy', 'execution', 'throw yaw', 'hooked', 'native.port.NativePort.ball_motor'),
    ('touch', 'execution', 'throw pitch', 'hooked', 'native.port.NativePort.ball_motor', 'native.individuation.delivery_velocity'),
    ('throw_power', 'execution', 'throw speed ceiling', 'hooked', 'native.port.NativePort._submit_intent'),
    ('ball_handling', 'execution', 'wind-up and post-secure strip resistance', 'hooked', 'native.port.NativePort.own_release_ms', 'core_src.match.Match.c3_move'),
    ('catching', 'execution', 'catch energy arrest through secure control', 'hooked', 'core_src.match.Match.catch_contacts'),
    ('tackling', 'execution', 'grip mechanics', 'hooked', 'core_src.match.Match.c3_holds_kick'),
    ('blocking', 'execution', 'block impedance', 'hooked', 'native.rulebook.handoff_block.block_power'),
    ('archery_accuracy', 'execution', 'arrow yaw', 'hooked', 'native.rulebook.port.RulebookPort.archer_motor'),
    ('durability', 'staged', 'injury susceptibility', 'new'),
    ('injury', 'staged', 'injury', 'new'),
    ('juke', 'maneuver', 'Juke', 'new'),
    ('spin', 'maneuver', 'Spin', 'new'),
    ('hurdle', 'maneuver', 'Hurdle', 'new'),
    ('stiff_arm', 'maneuver', 'Stiff-arm', 'new'),
    ('truck', 'maneuver', 'Truck', 'new'),
    ('stretch', 'maneuver', 'Stretch (owner approval pending)', 'new'),
]
ratings = {name: dict(layer=layer, owner=owner, status=status, consumers=consumers)
           for name, layer, owner, status, *consumers in ROWS}
for alias, owner in ALIASES.items():
    ratings[alias] = dict(layer='loader', owner=owner, status='alias',
                          consumers=['native.prism_registry.roster_ratings'])
ratings['legacy_passing'] = dict(layer='substrate', owner='throw_accuracy', status='alias',
                                 consumers=['native.roster.mapped_values'])
ratings['kicking'] = dict(layer='legacy', owner='compatibility only', status='partial', consumers=[])
data = dict(version='RB-3.24', parent='d1845d022625ddaf6d0f9d5ddc5e60179c63be34',
            scope='Native RB/3 with individuation enabled.',
            aliases=ALIASES, ratings=ratings)
Path('audit/native/rb323/rating-consumers.json').write_text(json.dumps(data, indent=2, sort_keys=True) + '\n')
