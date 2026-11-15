"""TACTICS-0 source of truth (Claude, 2026-11-15).

Everything in audit/tactics/tactics_0.json and the generated sections of
TACTICS_0.md and PERSONNEL_PROFILES.md is rendered from this module by build.py.
These are HYPOTHESES about ways to play. Nothing here is implemented, tested,
tuned or claimed to be good. Pure data: no simulator import.
"""

SCHEMA_VERSION = 'tactics-0/1'
TARGET = 'native-v0/3 (claude/native-v0-3-handoff-69stxd @ 8613280)'

RATINGS = ('speed', 'agility', 'strength', 'balance', 'stamina', 'tackling', 'blocking',
           'contact_resistance', 'ball_handling', 'catching', 'awareness', 'throw_power',
           'throw_accuracy', 'jump', 'keeper_skill', 'archery_accuracy')
BODY = ('height_m', 'mass_kg')

ENVELOPE = {
    'status': 'PLACEHOLDER design envelope (owner amendment of 14 Nov 2026 22:42), not canon',
    'rating_scale': [0.0, 1.0],
    'professional_band': [0.60, 1.00],
    'height_m': [2.40, 2.95],
    'mass_kg': [155.0, 285.0],
    'canon': {'speed_rating_1.0_mps': 44.704},
    'note': 'The only canon number is speed 1.0 = 44.704 m/s. Every band in this file is written '
            'against this envelope and moves if the envelope moves.',
}

CLASSES = {
    'EXPRESSIBLE NOW': 'Native v0/3 can run it today with no code change. In practice this means the '
                       'parameter is one of the 16 team-wide PolicyParams fields, with the same value for '
                       'every teammate.',
    'NEEDS COORDINATION': 'The engine mechanics, intent kinds and view fields exist in Native v0/3, but the '
                          'athlete does not hold the value: it differs by slot, replaces a constant in '
                          'cognition, or only works if teammates hold the same plan. Needs the pre-match '
                          'playbook of TACTIC_INTERFACE.md and cognition that reads it. No physics or rules change.',
    'NEEDS ENGINE WORK': 'Needs something the engine, port or rules layer does not provide in Native v0/3: '
                         'ratings and bodies per athlete (ATTRIBUTE_STEP_SPEC.md), athlete-chosen release speed, '
                         'voluntary off-ball contact, or a public signal missing from the view.',
}
NOW, COORD, ENGINE = 'EXPRESSIBLE NOW', 'NEEDS COORDINATION', 'NEEDS ENGINE WORK'

CONTACT = ['contain', 'wrap', 'takedown']


def P(meaning, typ, rng, cls, reason, route=None, joint=False, d5=False, unit=None):
    return dict(meaning=meaning, type=typ, range=rng, unit=unit, **{'class': cls}, route=route,
                reason=reason, joint=joint, needs_attribute_step_to_matter=d5)


W3 = {'keys': ['run_through', 'dodge', 'brace'], 'each': [0, 1], 'sum': 1}
W4 = {'keys': ['carry', 'close', 'mid', 'deep'], 'each': [0, 1], 'sum': 1}
WA = {'keys': ['carrier', 'receiver_near_goal', 'other'], 'each': [0, 1]}

CATALOG = {
    # ---------------------------------------------------------------- ball carrier
    'carrier.bias_pass': P('Added to the value of every pass option.', 'number', [-6, 6], NOW,
                           'Is PolicyParams.bias_pass.', 'PolicyParams.bias_pass'),
    'carrier.bias_shoot': P('Added to the value of the shoot option.', 'number', [-6, 6], NOW,
                            'Is PolicyParams.bias_shoot.', 'PolicyParams.bias_shoot'),
    'carrier.pass_min_clearance_m': P('Pass options whose believed lane clearance is below this are dropped.',
                                      'number', [0, 6], NOW, 'Is PolicyParams.pass_min_clearance.',
                                      'PolicyParams.pass_min_clearance', unit='m'),
    'carrier.shot_range_max_m': P('Largest believed distance to goal at which a throw at goal is an option.',
                                  'number', [8, 60], NOW, 'Is PolicyParams.shot_range.',
                                  'PolicyParams.shot_range', unit='m'),
    'carrier.shot_range_min_m': P('Smallest believed distance to goal at which a throw at goal is an option.',
                                  'number', [0, 40], COORD,
                                  'v0/3 cognition has no minimum-distance filter on the shoot option; the '
                                  'playbook value must be read in cognition.', unit='m'),
    'carrier.finish_pref': P('Preference weights over scoring methods: carry in, close throw (under 10 m), '
                             'mid throw (10 to 20 m), deep throw (20 m or more).', 'weights', W4, COORD,
                             'v0/3 values one shoot option and one carry option with no distance bands; the '
                             'bands need playbook weights in cognition. Release distance is the athlete\'s own '
                             'believed distance.', d5=True),
    'carrier.shot_speed_frac': P('Release speed of a throw at goal as a fraction of the thrower\'s own maximum.',
                                 'number', [0.3, 1.0], ENGINE,
                                 'v0/3 releases every pass and shot at min(27, max) m/s and 1.6 m height (R10 F-4). '
                                 'Athlete-chosen release speed and a per-athlete maximum from throw_power are '
                                 'engine and attribute-step work.', d5=True),
    'carrier.pass_len_band_m': P('Preferred believed pass length.', 'band', [4, 60], ENGINE,
                                 'v0/3 pass options are fixed to a believed 4 to 34 m at 27 m/s. Bands beyond 34 m, '
                                 'or needing a faster ball, depend on athlete-chosen release speed. A band inside '
                                 '4 to 34 m would need only the playbook.', d5=True, unit='m'),
    'carrier.touch_time_max_s': P('Longest time a ball holder outside the Keeper Zone keeps the ball before '
                                  'passing or throwing. 30 means no limit.', 'number', [0.5, 30], COORD,
                                  'v0/3 has no own-possession timer. Needs an own-action memory of when I gained '
                                  'the ball (own knowledge) and a playbook threshold.', unit='s'),
    'carrier.contact_response': P('Preference weights among run through, dodge and brace when a tackler is '
                                  'believed to be arriving.', 'weights', W3, COORD,
                                  'The three intents exist in v0/3 but are chosen from constants '
                                  '(THREAT_HORIZON_S, DODGE_MIN_S, BRACE_LOAD). The playbook must replace them.',
                                  d5=True),
    'carrier.first_tackle_bank_m': P('While the tackle count is 0, the carrier accepts contact only inside this '
                                     'distance of the attacked goal; farther out he prefers to dodge or pass. '
                                     '100 means anywhere.', 'number', [0, 100], ENGINE,
                                     'Needs the public tackle count in the athlete\'s view. v0/3 Signals carry no '
                                     'tackle count.', unit='m'),
    'carrier.dribble_use': P('When the one dribble per possession is used.', 'enum',
                             ['none', 'escape', 'advance'], COORD,
                             'The dribble intent exists; v0/3 uses it only when no teammate is believed visible. '
                             'A playbook rule must choose it.'),
    # ---------------------------------------------------------------- tempo and clock
    'tempo.shot_window_s': P('Seconds into the 30 s play clock in which the team prefers to take its scoring '
                             'attempt.', 'band', [0, 30], COORD,
                             'The possession clock is a public signal in the view. v0/3 has only a fixed +5 shoot '
                             'value in the first 5 s. Needs playbook values.', unit='s'),
    'tempo.must_shoot_remaining_s': P('With this much play clock left, the ball holder attempts to score from '
                                      'where he is.', 'number', [0, 10], COORD,
                                      'Same public clock; no such rule in v0/3 cognition.', unit='s'),
    'tempo.snap_delay_s': P('Seconds the snapper waits inside the legal 10 s snap window, when leading and '
                            'otherwise.', 'object', {'keys': ['leading', 'otherwise'], 'each': [0, 8]}, COORD,
                            'v0/3 releases as soon as a legal throw exists. Score is public. Assumes waiting '
                            'inside the legal window is not delay of game (Q-TAC-4).', unit='s'),
    'tempo.hold_own_half_until_remaining_s': P('The team keeps the ball in its own half until this much play '
                                               'clock remains. 30 means it does not hold.', 'number', [0, 30], COORD,
                                               'A position and hold rule from the public clock; needs the playbook. '
                                               'Its purpose (no legal arrow target outside the Archer\'s own half) '
                                               'rests on a ratified rule that v0/3 does not enforce.',
                                               joint=True, unit='s'),
    'off.first_action_max_s': P('After gaining a live ball, longest time before the first forward pass or carry.',
                                'number', [0.5, 10], COORD,
                                'Needs an own-action memory of when I gained the ball and a playbook threshold.',
                                unit='s'),
    'off.short_field_trigger_m': P('If possession is gained within this distance of the attacked goal, the team '
                                   'attempts to score at once. 0 means never.', 'number', [0, 100], COORD,
                                   'Own believed position and a playbook threshold.', unit='m'),
    # ---------------------------------------------------------------- off-ball positioning weights
    'pos.ball_att': P('In possession: pull toward the believed ball.', 'number', [-3, 3], NOW,
                      'Is PolicyParams.pos_ball_att.', 'PolicyParams.pos_ball_att'),
    'pos.ball_def': P('Out of possession: pull toward the believed ball.', 'number', [-3, 3], NOW,
                      'Is PolicyParams.pos_ball_def.', 'PolicyParams.pos_ball_def'),
    'pos.goal_att': P('In possession: pull toward the attacked goal.', 'number', [-3, 3], NOW,
                      'Is PolicyParams.pos_goal_att.', 'PolicyParams.pos_goal_att'),
    'pos.goal_def': P('Out of possession: pull toward own goal.', 'number', [-3, 3], NOW,
                      'Is PolicyParams.pos_goal_def.', 'PolicyParams.pos_goal_def'),
    'pos.spread': P('Prefer distance from the nearest believed teammate.', 'number', [-3, 3], NOW,
                    'Is PolicyParams.pos_spread.', 'PolicyParams.pos_spread'),
    'pos.opp_att': P('In possession: prefer distance from the nearest believed opponent.', 'number', [-3, 3], NOW,
                     'Is PolicyParams.pos_opp_att.', 'PolicyParams.pos_opp_att'),
    'pos.opp_def': P('Out of possession: prefer closeness to the nearest believed opponent.', 'number', [-3, 3],
                     NOW, 'Is PolicyParams.pos_opp_def.', 'PolicyParams.pos_opp_def'),
    'pos.lane': P('In possession: prefer an open believed lane from the carrier.', 'number', [-3, 3], NOW,
                  'Is PolicyParams.pos_lane.', 'PolicyParams.pos_lane'),
    'pos.edge_zone': P('Penalty for standing near a field edge or inside either Keeper Zone.', 'number', [0, 3],
                       NOW, 'Is PolicyParams.pos_edge_zone.', 'PolicyParams.pos_edge_zone'),
    # ---------------------------------------------------------------- Keeper Zone handling (offence)
    'zone.entry_mode': P('How attackers use the attacked Keeper Zone.', 'enum',
                         ['avoid', 'rebound_only', 'late_only', 'drive', 'rotation'], COORD,
                         'v0/3 has one behaviour (a position penalty for zones). A mode needs the playbook.'),
    'zone.dwell_max_s': P('An attacker leaves the zone when his own residence reaches this. Canon limit is 5 s.',
                          'number', [0, 4.5], COORD,
                          'v0/3 leaves at a fixed 3.0 s. Own residence time is already in the view; the playbook '
                          'must supply the threshold.', unit='s'),
    'zone.occupancy_target': P('Number of attackers the team tries to keep inside the zone in settled offence.',
                               'integer', [0, 6], COORD,
                               'Each athlete can count believed teammates inside, but who goes in next is a shared '
                               'arrangement held in the playbook.', joint=True),
    'zone.min_outside_s': P('Self-imposed minimum time outside before the same attacker re-enters.', 'number',
                            [0, 5], COORD,
                            'Own knowledge and a playbook value. Canon states no minimum time outside (Q-TAC-1).',
                            unit='s'),
    'zone.entry_stagger_s': P('Offset between the entries of paired attackers in a rotation.', 'number', [0, 5],
                              COORD, 'A timing agreement between teammates with no live channel: each acts on his '
                              'own belief of the partner leaving.', joint=True, unit='s'),
    'block.wedge': P('Lead blockers make legal off-ball contact (shoulder, push; no grip) ahead of the carrier.',
                     'boolean', None, ENGINE,
                     'Native has no voluntary off-ball contact intents (Q-HAND-1). Without them the wedge is only '
                     'bodies in the way.', joint=True, d5=True),
    'screen.arrow_screen': P('A screener stands between the Archer platform and a paired thrower.', 'boolean',
                             None, COORD,
                             'Position only, held in the playbook and paired with one teammate. Rests on '
                             'arrow-body collision, which the engine has. Effect unmeasured.', joint=True),
    # ---------------------------------------------------------------- defence
    'def.bias_press': P('Added to the value of closing on the believed carrier.', 'number', [-6, 6], NOW,
                        'Is PolicyParams.bias_press.', 'PolicyParams.bias_press'),
    'def.bias_pursue': P('Added to the value of pursuing a loose ball.', 'number', [-6, 6], NOW,
                         'Is PolicyParams.bias_pursue.', 'PolicyParams.bias_pursue'),
    'def.scheme': P('Shape of the defence.', 'enum',
                    ['arc_shell', 'man', 'wall', 'contain_funnel', 'man_press', 'deep_shell', 'lane_gamble',
                     'zone_trap'], COORD,
                    'A scheme is the set of slot anchors and marking rules below; it exists only if every teammate '
                    'holds the same chart.', joint=True),
    'def.pressers_max': P('How many defenders close on the carrier at once.', 'integer', [1, 4], COORD,
                          'v0/3 lets the two believed-nearest press (a constant).'),
    'def.press_line_m': P('The carrier is engaged only when he is within this distance of the defending goal. '
                          '100 means everywhere.', 'number', [0, 100], COORD,
                          'Own believed positions and a playbook value; no such line in v0/3.', unit='m'),
    'def.commit_gap_m': P('Believed gap at which a pressing defender commits to contact.', 'number', [1, 10],
                          COORD, 'TACKLE_COMMIT_M = 6.0 is a constant in v0/3.', unit='m'),
    'def.contain_gap_m': P('Gap a containing defender keeps to the carrier.', 'band', [1, 10], COORD,
                           'Containing without contact is a position choice; needs the playbook.', unit='m'),
    'def.takedown_line_m': P('A takedown is chosen only when the carrier is within this distance of the '
                             'defending goal. 100 means anywhere.', 'number', [0, 100], COORD,
                             'Own believed positions and a playbook value.', unit='m'),
    'def.contact_by_area': P('Contact a defender chooses by area: beyond the takedown line (midfield), inside it '
                             'but outside the zone (arc), inside the own Keeper Zone (zone).', 'object',
                             {'keys': ['midfield', 'arc', 'zone'], 'enum': CONTACT}, COORD,
                             'Wrap and takedown intents exist in v0/3; the area is the athlete\'s own believed '
                             'position.', d5=True),
    'def.contact_at_count1': P('Contact chosen once the offence has used its first tackle.', 'enum',
                               ['same_as_area', 'takedown'], ENGINE,
                               'Needs the public tackle count in the athlete\'s view. v0/3 Signals carry none.'),
    'def.holdup_drive': P('Direction a wrapping defender drives the carrier.', 'enum', ['none', 'into_zone'],
                          COORD, 'The aim of a wrapping defender is his own intent. Whether a wrap can move or '
                          'hold a carrier is engine physics as built, unmeasured.', d5=True),
    # ---------------------------------------------------------------- Archer
    'archer.eagerness': P('Added to the value of every draw-and-release option.', 'number', [-3, 3], NOW,
                          'Is PolicyParams.archer_eager.', 'PolicyParams.archer_eager'),
    'archer.target_priority': P('Relative value of legal targets: the believed carrier, the receiver nearest the '
                                'goal, any other legal attacker.', 'weights', WA, COORD,
                                'v0/3 uses constants (carrier 3.0, others 1.6 minus 0.04 per metre from the ball). '
                                'The Archer is one athlete, so no teammate is involved.', d5=True),
    # ---------------------------------------------------------------- Keeper
    'keeper.depth_m': P('How far off the goal line the Keeper sets.', 'band', [1, 8], COORD,
                        'v0/3 Keeper depth is clamp(0.25 x distance, 1, 4), a constant rule.', unit='m'),
    'keeper.distribution': P('What the Keeper does with a secured ball.', 'enum', ['short', 'long_outlet'], COORD,
                             'Target choice needs the slot chart. A long outlet beyond 34 m also depends on '
                             'carrier.pass_len_band_m.', joint=True),
    # ---------------------------------------------------------------- restarts and Hunt
    'restart.scrim_play': P('Set play at a Contact Scrimmage with the ball.', 'enum',
                            ['default', 'quick_swing', 'wedge_snap', 'zone_stack', 'safe_reset', 'go_routes'],
                            COORD, 'v0/3 throws to a believed teammate 4 to 34 m away and two teammates make '
                            'themselves throwable. A named play is a shared arrangement.', joint=True),
    'restart.snap40_play': P('Set play at the 40 m scrimmage after conceding.', 'enum',
                             ['default', 'quick_swing', 'wedge_snap', 'zone_stack', 'safe_reset', 'go_routes'],
                             COORD, 'As restart.scrim_play.', joint=True),
    'restart.toss_play': P('Set play at a toss-in.', 'enum', ['short_toss', 'line_toss'], COORD,
                           'As restart.scrim_play. A tossed ball cannot score until another player controls it.',
                           joint=True),
    'restart.def_alignment': P('Defensive alignment at an opponent restart.', 'enum',
                               ['shell', 'man_up', 'ring', 'gate', 'wall'], COORD,
                               'Slot anchors relative to the restraining line; shared chart.', joint=True),
    'restart.taker_slot': P('Slot that prefers to take 40 m scrimmages and toss-ins. The snapper after a tackle '
                            'is fixed by rule.', 'slot_or_nearest', None, COORD,
                            'v0/3 claim goes to the believed-nearest teammate. A slot preference needs the others '
                            'to hold back.', joint=True),
    'hunt.contestant_slot': P('Slot whose holder claims the Hunt.', 'slot', None, COORD,
                              'v0/3 admits a claim from any field player. Naming one slot needs the others to '
                              'abstain. It matters only once athletes differ.', joint=True, d5=True),
    'hunt.win_action': P('What the contestant does on winning the ball.', 'enum', ['carry_out', 'tip_out'], COORD,
                         'An individual choice of the contestant; needs the playbook.'),
    # ---------------------------------------------------------------- personnel
    'slot.anchor': P('Where a slot stands in each situation (offence, defence, own restart, opponent restart, '
                     'Hunt), relative to ball, field or goal.', 'anchor', None, COORD,
                     'v0/3 has no slots or anchors (native/README: no positional role or formation grid). Each '
                     'athlete needs its own slot and anchor in a playbook, and the shape exists only if all '
                     'teammates hold the same chart.', joint=True),
    'slot.requires': P('Minimum rating and body bands for a slot.', 'bands', None, ENGINE,
                       'Native v0/3 gives every athlete rating 0.70 and one body and reads no roster '
                       '(ATTRIBUTE_STEP_SPEC.md).', d5=True),
    'slot.prefers': P('Weights used to rank candidates for a slot.', 'weights_open', None, ENGINE,
                      'As slot.requires.', d5=True),
    'assignment.rule': P('Pre-match rule that fills slots from a supplied roster by rating band.', 'rule', None,
                         ENGINE, 'A step outside the engine, but there is nothing to assign until rosters carry '
                         'ratings, and the harness has no per-athlete playbook input.', d5=True),
    'subs.policy': P('Use of substitutions.', 'enum', ['cover_only'], NOW,
                     'As built: substitutes only cover exclusions and disqualifications. TACTICS-0 keeps the same '
                     'ten field starters in every phase.', 'native default'),
}
SLOT_KEYS = ('slot.anchor', 'slot.requires', 'slot.prefers', 'assignment.rule')
TEAM_KEYS = tuple(k for k in CATALOG if k not in SLOT_KEYS)

# ----------------------------------------------------------------------------- anchors
PHASES = ('offence', 'defence', 'restart_own', 'restart_opp', 'hunt')


def arc(goal, rng, bearing, spread='even', note=None):
    """Polar about a goal centre. bearing 0 = straight out from the goal toward midfield, + = right."""
    return dict(type='goal_arc', goal=goal, range_m=list(rng), bearing_deg=list(bearing), spread=spread, note=note)


def ball(du, dv, mirror=False, note=None):
    """Relative to the believed ball. du + = toward the attacked goal. dv = lateral."""
    return dict(type='ball_rel', du_m=list(du), dv_m=list(dv), mirror=mirror, note=note)


def field(u, v, spread='even', note=None):
    """Own frame: u = metres from own goal line, v = lateral from the centre line."""
    return dict(type='field', u_m=list(u), v_m=list(v), spread=spread, note=note)


def mark(target, side, gap, note=None):
    return dict(type='mark', target=target, side=side, gap_m=list(gap), note=note)


def line(du, dv, mirror=False, note=None):
    """Restart: relative to the restraining line (ball line; own 40 m line for the defence at a 40 m scrimmage)."""
    return dict(type='line_rel', du_m=list(du), dv_m=list(dv), mirror=mirror, note=note)


def pair(with_slot, gap, note=None):
    return dict(type='pair', with_slot=with_slot, toward='attacked_goal', gap_m=list(gap),
                min_range_from_goal_m=20.5, note=note)


def cycle(inside_rng, bearing, outside_rng, note=None):
    return dict(type='zone_cycle', goal='attacked', inside_range_m=list(inside_rng), bearing_deg=list(bearing),
                outside_range_m=list(outside_rng), dwell='zone.dwell_max_s', note=note)


def rule(text):
    return dict(type='rule', text=text)


HUNT_BACK = field((25, 40), (-25, 25), note='own half, outside the centre circle')
HUNT_WING = field((38, 45), (7, 14), 'mirror', note='own half, at least 7 m from the centre spot, to take a tip-out')


def slot(sid, count, role, needs, prefers, fail_below, degrade, anchors, what, overrides=None):
    assert set(anchors) == set(PHASES), sid
    return dict(id=sid, count=count, role=role, what=what, requires=needs, prefers=prefers,
                understaffed=dict(mode='failure' if fail_below else 'graceful', fail_below_in_band=fail_below,
                                  effect=degrade),
                anchors=anchors, overrides=overrides or {})


def keeper(needs=None, prefers=None, degrade=None):
    needs = needs or {'keeper_skill': .80, 'catching': .70}
    prefers = prefers or {'keeper_skill': .5, 'catching': .2, 'jump': .15, 'height_m': .15}
    a = rule('Fixed role. Inside the own Keeper Zone at keeper.depth_m off the goal line, on the line from goal '
             'centre to the believed ball.')
    return slot('KEEPER', 1, 'keeper', needs, prefers, 0,
                degrade or 'Graceful: a weaker Keeper concedes more of the throws that reach the goal; no part of '
                'the plan stops working.',
                dict(offence=a, defence=a, restart_own=a, restart_opp=a, hunt=a), 'Goalkeeper (fixed role by canon).')


def archer(needs=None, prefers=None, fail_below=0, degrade=None):
    needs = needs or {'archery_accuracy': .75, 'awareness': .70}
    prefers = prefers or {'archery_accuracy': .7, 'awareness': .3}
    a = rule('Fixed role. On the platform: 5 m high, 5 m behind the own goal plane, centred.')
    return slot('ARCHER', 1, 'archer', needs, prefers, fail_below,
                degrade or 'Graceful: fewer freezes per opposing possession; no part of the plan stops working.',
                dict(offence=a, defence=a, restart_own=a, restart_opp=a,
                     hunt=rule('On the platform; may not draw or fire until the ball has left the centre circle.')),
                'Archer (fixed role by canon).')


def base(**kw):
    """Neutral team values = Native v0/3 defaults where one exists."""
    v = {
        'carrier.bias_pass': 0., 'carrier.bias_shoot': 0., 'carrier.pass_min_clearance_m': 0.,
        'carrier.shot_range_max_m': 32., 'carrier.shot_range_min_m': 0.,
        'carrier.finish_pref': dict(carry=.30, close=.30, mid=.25, deep=.15),
        'carrier.shot_speed_frac': .9, 'carrier.pass_len_band_m': [4, 34], 'carrier.touch_time_max_s': 30.,
        'carrier.contact_response': dict(run_through=.5, dodge=.3, brace=.2),
        'carrier.first_tackle_bank_m': 100., 'carrier.dribble_use': 'none',
        'tempo.shot_window_s': [0, 26], 'tempo.must_shoot_remaining_s': 4.,
        'tempo.snap_delay_s': dict(leading=0., otherwise=0.), 'tempo.hold_own_half_until_remaining_s': 30.,
        'off.first_action_max_s': 10., 'off.short_field_trigger_m': 0.,
        'pos.ball_att': .6, 'pos.ball_def': 1.2, 'pos.goal_att': 1., 'pos.goal_def': 1., 'pos.spread': 1.,
        'pos.opp_att': .6, 'pos.opp_def': .6, 'pos.lane': .8, 'pos.edge_zone': 1.,
        'zone.entry_mode': 'late_only', 'zone.dwell_max_s': 3.0, 'zone.occupancy_target': 1,
        'zone.min_outside_s': 1.0, 'zone.entry_stagger_s': 0., 'block.wedge': False, 'screen.arrow_screen': False,
        'def.bias_press': 0., 'def.bias_pursue': 0., 'def.scheme': 'arc_shell', 'def.pressers_max': 2,
        'def.press_line_m': 100., 'def.commit_gap_m': 6., 'def.contain_gap_m': [5, 7], 'def.takedown_line_m': 100.,
        'def.contact_by_area': dict(midfield='takedown', arc='takedown', zone='takedown'),
        'def.contact_at_count1': 'same_as_area', 'def.holdup_drive': 'none',
        'archer.eagerness': 0., 'archer.target_priority': dict(carrier=1., receiver_near_goal=.5, other=.3),
        'keeper.depth_m': [1.5, 4], 'keeper.distribution': 'short',
        'restart.scrim_play': 'default', 'restart.snap40_play': 'default', 'restart.toss_play': 'short_toss',
        'restart.def_alignment': 'shell', 'restart.taker_slot': 'nearest',
        'hunt.contestant_slot': None, 'hunt.win_action': 'tip_out', 'subs.policy': 'cover_only',
    }
    for k, val in kw.items():
        key = k.replace('__', '.')
        assert key in v, key
        v[key] = val
    return v


PLAYS = {
    'default': 'As built in Native v0/3: the taker throws to a believed teammate 4 to 34 m from the spot.',
    'quick_swing': 'The taker throws 6 to 8 m back and to one side to a named handler slot, who starts the '
                   'normal offence. All teammates start behind the ball line.',
    'wedge_snap': 'The taker throws 5 m straight back to a RAM. The PLOWs stand 0.8 to 1.5 m behind the ball line '
                  'in a V and move on the release. All teammates start behind the ball line.',
    'zone_stack': 'The taker throws 7 m back to a HUB. DARTs stand wide on the ball line and enter the zone on the '
                  'release, in their rotation order.',
    'safe_reset': 'The taker throws 8 m back to a METRONOME and the team re-forms its passing diamond. The taker '
                  'waits tempo.snap_delay_s inside the legal window first.',
    'go_routes': 'The taker throws 7 m back to a CANNON. BOLTs stand on the ball line at wide, centre, wide and '
                 'sprint on the release; the CANNON throws long into the space ahead of one of them.',
    'short_toss': 'The thrower tosses 6 to 10 m infield to the nearest named handler slot. The thrower may not '
                  'recover the ball himself and the ball cannot score until another player controls it.',
    'line_toss': 'The thrower tosses up the boundary to a BOLT running into space. Same toss-in limits.',
    'def:shell': 'All field defenders stand 5.5 m or more on their own side of the restraining line, between ball '
                 'and goal.',
    'def:man_up': 'Each field defender stands 5.5 m on his own side of the restraining line, opposite one attacker, '
                  'and closes on the release.',
    'def:ring': 'RINGs stand on the 21 to 25 m arc if the spot is outside it, otherwise 5.5 m behind the line; '
                'SHADOWs 5.5 m behind the line opposite the likely receivers.',
    'def:gate': 'CLAMPs and GATEs take their arc posts if the spot is outside the zone, otherwise 5.5 m behind the '
                'line; DENYs opposite the likely receivers at 5.5 m.',
    'def:wall': 'RAMs and PLOWs stand shoulder to shoulder 5.5 m behind the restraining line; FLANKs and TAILs '
                'outside them.',
}
RESTART_RULES = [
    'After a tackle the tackled carrier is the snapper and the tackler stands opposite him or 5 m behind (canon); '
    'no play names them.',
    'Everyone else starts on his own side of the ball line (offside rule).',
    'At a 40 m scrimmage after a score every athlete starts at or behind his own 40 m line.',
    'No defender stands within 5 m of an opponent before the ball is live (5 m marking), so every defensive anchor '
    'is 5.5 m or more behind the restraining line.',
    'The snap is released inside the 10 s window; a toss within 4 s of ready, with opponents 3 m clear.',
]

# ----------------------------------------------------------------------------- the eight styles
T = []

# ============================================================== 1 ARC
T.append(dict(
    id='ARC', name='Arc Siege', tags=['deep_throws'],
    idea='Keep every attacker outside the Keeper Zone on the 21 to 24 m arc, move the ball by quick passes, and '
         'score with hard throws released from 20 m or more. The bet is that a fast, accurate deep throw beats a '
         'Keeper who has no help, because defenders may not wait inside the zone without an attacker to mark.',
    formation='3 GUN on the arc, 3 SCREEN paired goal-side of them, 2 FEED behind, 2 SAFETY held back',
    slots=[
        slot('GUN', 3, 'field', {'throw_power': .85, 'throw_accuracy': .80, 'catching': .70},
             {'throw_power': .4, 'throw_accuracy': .4, 'catching': .1, 'height_m': .1}, 2,
             'FAILURE below two in band: a slower or less accurate deep throw gives the Keeper time and the '
             'style has no other scoring route. With two of three in band one arc sector goes unused (graceful).',
             dict(offence=arc('attacked', (21, 24), (-55, 55)),
                  defence=arc('own', (21, 24), (-40, 40)),
                  restart_own=line((-10, -6), (-16, 16), note='spread behind the ball, ready to run to the arc'),
                  restart_opp=line((-8, -5.5), (-12, 12)),
                  hunt=HUNT_BACK),
             'Deep thrower: catches on the arc and throws at goal from 20 m or more.'),
        slot('FEED', 2, 'field', {'throw_accuracy': .80, 'awareness': .75, 'ball_handling': .70},
             {'throw_accuracy': .4, 'awareness': .4, 'ball_handling': .2}, 0,
             'Graceful: circulation slows, ball holders keep the ball longer than the Archer needs between '
             'arrows, and more freezes are taken.',
             dict(offence=arc('attacked', (28, 32), (8, 20), 'mirror'),
                  defence=arc('own', (27, 31), (10, 25), 'mirror'),
                  restart_own=line((-8, -6), (3.2, 8), True, note='takes the quick_swing throw'),
                  restart_opp=line((-10, -7), (3.2, 8), True),
                  hunt=HUNT_WING),
             'Distributor: stands behind the arc and moves the ball from side to side.'),
        slot('SCREEN', 3, 'field', {'blocking': .75, 'strength': .70, 'mass_kg': 220.},
             {'blocking': .3, 'strength': .3, 'mass_kg': .2, 'height_m': .2}, 0,
             'Graceful: a smaller or weaker screener hides less of the thrower from the Archer and gives the '
             'marker an easier path to the release.',
             dict(offence=pair('GUN', (1.5, 2.5), note='between the paired GUN and the goal, never inside the zone'),
                  defence=arc('own', (21, 23), (-60, 60)),
                  restart_own=line((-3, -0.8), (-10, 10), note='on the ball line, first to the arc'),
                  restart_opp=line((-6.5, -5.5), (-10, 10)),
                  hunt=HUNT_BACK),
             'Screener: stands goal-side of a GUN, in the marker\'s path and on the Archer\'s sight line.'),
        slot('SAFETY', 2, 'field', {'speed': .85, 'tackling': .70},
             {'speed': .5, 'tackling': .3, 'awareness': .2}, 0,
             'Graceful: a slower SAFETY concedes more runs after a saved or missed throw.',
             dict(offence=field((45, 58), (4.8, 12), 'mirror', note='stays back against the break'),
                  defence=mark('carrier', 'goal_side', (0, 6), note='the two who close on the carrier'),
                  restart_own=line((-22, -14), (4, 10), True),
                  restart_opp=line((-16, -10), (4, 10), True),
                  hunt=rule('The faster SAFETY is the contestant; the other stands 12 m behind the centre spot.')),
             'Last line in attack, ball pressure in defence, Hunt contestant.'),
        keeper(), archer(),
    ],
    team=base(carrier__bias_pass=1.5, carrier__bias_shoot=3., carrier__pass_min_clearance_m=2.,
              carrier__shot_range_max_m=27., carrier__shot_range_min_m=20.,
              carrier__finish_pref=dict(carry=.10, close=.05, mid=.15, deep=.70),
              carrier__shot_speed_frac=1.0, carrier__pass_len_band_m=[8, 30], carrier__touch_time_max_s=1.5,
              carrier__contact_response=dict(run_through=.2, dodge=.6, brace=.2),
              tempo__shot_window_s=[8, 22], tempo__must_shoot_remaining_s=5.,
              pos__ball_att=.3, pos__spread=1.5, pos__lane=1.5, pos__edge_zone=3.,
              zone__entry_mode='rebound_only', zone__dwell_max_s=2.0, zone__occupancy_target=0,
              screen__arrow_screen=True, def__scheme='arc_shell', def__press_line_m=45.,
              restart__scrim_play='quick_swing', restart__snap40_play='quick_swing',
              restart__taker_slot='FEED', hunt__contestant_slot='SAFETY'),
    signature={'shots_released_20m_plus_share': ['>=', .60], 'attacker_zone_seconds_per_possession': ['<=', 2.0],
               'ball_holder_touch_time_s_median': ['<=', 1.8]},
    strengths=['Never puts an attacker on the 5 s zone limit.',
               'Keeps the defence out of the zone by rule: a defender may stay there only within 5 m of an attacker.',
               'Deep throws are the highest-valued throws on the provisional scale (4).'],
    weaknesses=['Every attacker is a legal arrow target for the whole possession.',
                'Needs two rare players: high throw power and high accuracy together.',
                'A saved or missed throw is a live ball with eight attackers 70 m or more from their own goal.',
                'Under the flat scoring now in force a deep goal is worth no more than a close one.'],
    canon=['No attacker waits inside the zone; a rebound chase leaves within 2 s (limit 5 s).',
           'Screens are stationary bodies; any contact stays in the legal band (below the neck, above the hip, '
           'no grip).',
           'No pass or carry goes back into the own Keeper Zone (ZR-C, ZR-T).'],
))

# ============================================================== 2 WAVE
T.append(dict(
    id='WAVE', name='Zone Waves', tags=['keeper_zone_5s_exploit'],
    idea='The 5 s limit is counted per attacker and "at a time", so the team rotates attackers through the '
         'Keeper Zone in short visits of 3.5 s and always has fresh ones inside. Attackers inside the zone are not '
         'legal arrow targets, and they finish with close and mid throws or a carry.',
    formation='2 HUB outside the arc, 4 DART in two alternating pairs, 2 PIVOT alternating at the goal front, '
              '2 ANCHOR held back',
    slots=[
        slot('HUB', 2, 'field', {'awareness': .85, 'throw_accuracy': .75, 'ball_handling': .70},
             {'awareness': .4, 'throw_accuracy': .4, 'ball_handling': .2}, 1,
             'FAILURE with none in band: entries are fed late or to the wrong man and attackers burn their 5 s '
             'without the ball. With one in band the feed comes from one side only (graceful).',
             dict(offence=arc('attacked', (24, 30), (12, 30), 'mirror'),
                  defence=mark('nearest_unmarked_opponent', 'goal_side', (1.5, 3)),
                  restart_own=line((-8, -6), (2.4, 6), True, note='takes the zone_stack throw'),
                  restart_opp=line((-7, -5.5), (4, 10), True),
                  hunt=HUNT_WING),
             'Feeder: holds the ball outside the arc and passes to attackers as they enter.'),
        slot('DART', 4, 'field', {'agility': .85, 'speed': .75, 'catching': .70},
             {'agility': .35, 'speed': .25, 'catching': .25, 'throw_accuracy': .15}, 2,
             'FAILURE below two in band: there is no pair quick enough to get in and out inside 3.5 s; either the '
             'zone empties or residence turnovers rise. With two or three the weaker pair makes shorter, '
             'shallower visits (graceful).',
             dict(offence=cycle((6, 13), (-60, 60), (21, 24), note='two pairs; one pair inside while the other is out'),
                  defence=mark('nearest_unmarked_opponent', 'goal_side', (1.5, 3)),
                  restart_own=line((-1.5, -0.8), (-22, 22), note='wide on the ball line'),
                  restart_opp=line((-6.5, -5.5), (-20, 20)),
                  hunt=HUNT_BACK),
             'In-and-out runner: enters the zone, receives, finishes or leaves before 3.5 s.'),
        slot('PIVOT', 2, 'field', {'strength': .80, 'balance': .75, 'catching': .70},
             {'strength': .3, 'balance': .3, 'catching': .2, 'height_m': .2}, 0,
             'Graceful: a lighter or shorter PIVOT is moved off his spot and the team loses the target at the '
             'goal front; DARTs still rotate.',
             dict(offence=cycle((8, 14), (-25, 25), (21, 23), note='the two PIVOTs alternate: one inside, one out'),
                  defence=mark('nearest_unmarked_opponent', 'goal_side', (1.5, 3)),
                  restart_own=line((-2, -0.8), (1.6, 4), True),
                  restart_opp=line((-6.5, -5.5), (1.6, 4), True),
                  hunt=HUNT_BACK),
             'Target at the goal front: receives with his back to goal, turns and throws or hands off.'),
        slot('ANCHOR', 2, 'field', {'speed': .80, 'tackling': .70},
             {'speed': .5, 'tackling': .3, 'awareness': .2}, 0,
             'Graceful: a slower ANCHOR concedes more runs after a save.',
             dict(offence=field((45, 55), (4.8, 12), 'mirror'),
                  defence=mark('carrier', 'goal_side', (0, 6)),
                  restart_own=line((-22, -14), (4, 10), True),
                  restart_opp=line((-16, -10), (4, 10), True),
                  hunt=rule('The faster ANCHOR is the contestant; the other stands 12 m behind the centre spot.')),
             'Last line in attack, ball pressure in defence, Hunt contestant.'),
        keeper(), archer(),
    ],
    team=base(carrier__bias_pass=1., carrier__bias_shoot=1., carrier__shot_range_max_m=18.,
              carrier__finish_pref=dict(carry=.20, close=.50, mid=.25, deep=.05),
              carrier__shot_speed_frac=.8, carrier__pass_len_band_m=[6, 22], carrier__touch_time_max_s=2.5,
              carrier__contact_response=dict(run_through=.2, dodge=.6, brace=.2),
              tempo__shot_window_s=[6, 20], pos__goal_att=2., pos__lane=1.2, pos__edge_zone=0.,
              zone__entry_mode='rotation', zone__dwell_max_s=3.5, zone__occupancy_target=3,
              zone__min_outside_s=1.0, zone__entry_stagger_s=1.75,
              def__scheme='man', def__pressers_max=1, def__press_line_m=40.,
              restart__scrim_play='zone_stack', restart__snap40_play='quick_swing', restart__def_alignment='man_up',
              restart__taker_slot='HUB', hunt__contestant_slot='ANCHOR'),
    signature={'shots_released_inside_zone_share': ['>=', .65], 'attackers_in_zone_mean_settled': ['between', [2, 3]],
               'attacker_zone_dwell_s_p95': ['<=', 4.0], 'zone_residence_turnovers_per_possession': ['<=', .05]},
    strengths=['Finishers are sheltered from the Archer while inside the zone.',
               'Close and mid throws give the Keeper the least time.',
               'Defenders who follow an attacker in must leave again when he leaves, or become unmarked.'],
    weaknesses=['The rotation is a timing agreement with no live channel; each athlete acts on his own belief of '
                'where his partner is.',
                'Only 1.5 s of margin on the limit: any hold-up inside the zone risks a turnover.',
                'Close and mid throws are the lowest-valued throws on the provisional scale (2 and 3).',
                'HUBs outside the arc remain arrow targets.'],
    canon=['Every visit ends at 3.5 s, inside the 5 s limit; expiry would be a turnover.',
           'Reads the Rulebook wording "at most 5 seconds at a time" as a fresh 5 s on re-entry. Canon states no '
           'minimum time outside; the plan imposes 1.0 s on itself (PLACEHOLDER, Q-TAC-1).',
           'No contact on the Keeper inside his zone.'],
))

# ============================================================== 3 RAM
T.append(dict(
    id='RAM', name='Carry Train', tags=['carries'],
    idea='One power carrier runs behind a wedge of blockers and the team spends its one free tackle on purpose, '
         'close to goal. From the scrimmage that follows, a second wedge run from 10 to 20 m carries the ball '
         'over the goal plane in under 5 s.',
    formation='2 RAM (carrier and relief), 4 PLOW in a V ahead of the ball, 2 FLANK wide, 2 TAIL behind',
    slots=[
        slot('RAM', 2, 'field', {'strength': .85, 'balance': .75, 'ball_handling': .70, 'mass_kg': 220.},
             {'strength': .25, 'balance': .25, 'ball_handling': .15, 'contact_resistance': .15, 'mass_kg': .2}, 1,
             'FAILURE with none in band: a carrier who goes down on first contact uses both tackles before the '
             'arc. With one in band there is no relief carrier (graceful).',
             dict(offence=ball((-6, 0), (-1, 1), note='one carries; the other trails 4 to 6 m behind as relief'),
                  defence=arc('own', (24, 28), (4.8, 12), 'mirror'),
                  restart_own=line((-6, -4), (-1, 1), note='takes the wedge_snap throw 5 m behind the ball'),
                  restart_opp=line((-6.5, -5.5), (1.2, 3), True),
                  hunt=rule('One RAM is the contestant and carries the ball out; the other stands 12 m behind '
                            'the centre spot.')),
             'Power carrier: carries into contact and stays up.'),
        slot('PLOW', 4, 'field', {'blocking': .85, 'strength': .75, 'mass_kg': 220.},
             {'blocking': .4, 'strength': .3, 'mass_kg': .3}, 2,
             'FAILURE below two in band: no wedge forms and the carrier meets the first tackler alone. With two '
             'or three the wedge covers one side only (graceful).',
             dict(offence=ball((2, 4.5), (-4, 4), note='V ahead of the carrier, never more than 5 m from him'),
                  defence=arc('own', (24, 28), (-45, 45)),
                  restart_own=line((-1.5, -0.8), (-4, 4), note='on the ball line in a V'),
                  restart_opp=line((-6.5, -5.5), (-8, 8)),
                  hunt=HUNT_WING),
             'Lead blocker: clears the carrier\'s path by legal off-ball contact.'),
        slot('FLANK', 2, 'field', {'speed': .80, 'catching': .75, 'ball_handling': .70},
             {'speed': .4, 'catching': .3, 'ball_handling': .3}, 0,
             'Graceful: without a reliable outlet the carrier has no pass when the wedge stalls.',
             dict(offence=ball((-1, 1), (8, 12), True),
                  defence=mark('nearest_unmarked_opponent', 'goal_side', (1.5, 3)),
                  restart_own=line((-2, -0.8), (10, 14), True),
                  restart_opp=line((-7, -5.5), (12, 18), True),
                  hunt=HUNT_BACK),
             'Wide outlet level with the ball.'),
        slot('TAIL', 2, 'field', {'tackling': .80, 'speed': .70},
             {'tackling': .5, 'speed': .3, 'awareness': .2}, 0,
             'Graceful: loose balls behind the wedge are lost more often.',
             dict(offence=ball((-10, -6), (2.4, 6), True),
                  defence=mark('carrier', 'goal_side', (0, 5)),
                  restart_own=line((-14, -9), (2.4, 6), True),
                  restart_opp=line((-12, -8), (2.4, 6), True),
                  hunt=HUNT_BACK),
             'Trailer: recovers loose balls and is the last line.'),
        keeper(), archer(),
    ],
    team=base(carrier__bias_pass=-4., carrier__bias_shoot=-1., carrier__shot_range_max_m=12.,
              carrier__finish_pref=dict(carry=.75, close=.20, mid=.05, deep=0.),
              carrier__shot_speed_frac=.7, carrier__pass_len_band_m=[4, 12],
              carrier__contact_response=dict(run_through=.7, dodge=.1, brace=.2),
              carrier__first_tackle_bank_m=30., tempo__shot_window_s=[6, 24], tempo__must_shoot_remaining_s=3.,
              pos__ball_att=2., pos__spread=.2, pos__edge_zone=.5,
              zone__entry_mode='drive', zone__dwell_max_s=4.0, zone__occupancy_target=5, block__wedge=True,
              def__bias_press=1., def__scheme='wall', def__press_line_m=35., def__commit_gap_m=5.,
              restart__scrim_play='wedge_snap', restart__snap40_play='wedge_snap', restart__def_alignment='wall',
              restart__taker_slot='TAIL', hunt__contestant_slot='RAM', hunt__win_action='carry_out'),
    signature={'advance_by_carry_share': ['>=', .80], 'passes_per_possession': ['<=', 1.5],
               'carry_goal_share_of_goals': ['>=', .60], 'first_tackles_within_30m_of_goal_share': ['>=', .50]},
    strengths=['A carry goal is the highest-valued score on the provisional scale (5).',
               'Few passes, so few interceptions and drops.',
               'Its turnovers are mostly dead balls (second tackle), which give the opponent no running start.',
               'A first tackle inside 10 m of the goal plane is re-spotted at 10 m with a fresh 5 s after the snap.'],
    weaknesses=['Two tackles end the possession; a defence that grounds the carrier early and far out leaves a '
                'long second run.',
                'The carrier is the Archer\'s first target for the whole run outside the zone.',
                'Lead blocking cannot be expressed in Native v0/3 at all.',
                'Under flat scoring a carry goal is worth no more than a throw.'],
    canon=['Blocks are shoulder and push contact below the neck and above the hip, no grip, never on the Keeper '
           'in his zone; tripping or tackling a player without the ball is a major foul and is not used.',
           'Wedge and carrier leave the zone inside 4 s if the carry stalls.',
           'One dribble per possession is not used.'],
))

# ============================================================== 4 ANVIL
T.append(dict(
    id='ANVIL', name="Archer's Anvil", tags=['archer'],
    idea='The field defence does not try to win the ball itself. It contains the carrier in the Archer\'s lane, '
         'outside the Keeper Zone, and lets the Archer spend the full 15 arrows and 5 freezes; defenders then '
         'play the loose ball and break.',
    formation='Archer as the stopper; 3 SHADOW containing the ball, 4 RING on the arc, 3 LID on the receivers',
    slots=[
        archer({'archery_accuracy': .85, 'awareness': .75}, {'archery_accuracy': .7, 'awareness': .3}, 1,
               'FAILURE out of band: the defence has given up tackling in midfield to feed the Archer; an '
               'Archer who misses leaves a carrier nobody is trying to stop.'),
        slot('SHADOW', 3, 'field', {'speed': .85, 'agility': .80, 'awareness': .70},
             {'speed': .35, 'agility': .35, 'awareness': .3}, 2,
             'FAILURE below two in band: a carrier who runs past his shadows reaches the zone, where he cannot be '
             'frozen. With two the weak side is open (graceful).',
             dict(offence=ball((4, 10), (-12, 12)),
                  defence=mark('carrier', 'goal_side', (5, 7),
                               note='stays between carrier and goal without contact, steering him to the middle'),
                  restart_own=line((-9, -6), (-8, 8)),
                  restart_opp=line((-7, -5.5), (-8, 8)),
                  hunt=rule('The fastest SHADOW is the contestant; the others stand 7 m from the centre spot in '
                            'the own half.')),
             'Container: keeps the carrier in front and outside the zone without tackling.'),
        slot('RING', 4, 'field', {'tackling': .80, 'ball_handling': .70, 'speed': .70},
             {'tackling': .4, 'ball_handling': .3, 'speed': .3}, 0,
             'Graceful: more carriers get through the arc and fewer loose balls are picked up.',
             dict(offence=arc('attacked', (22, 30), (-50, 50)),
                  defence=arc('own', (21, 25), (-60, 60), note='takes down anyone who tries to enter the zone'),
                  restart_own=line((-3, -0.8), (-16, 16)),
                  restart_opp=line((-6.5, -5.5), (-16, 16), note='or the arc posts if the spot is outside 25 m'),
                  hunt=HUNT_BACK),
             'Arc guard: tackles at the arc and picks up the ball a frozen carrier drops.'),
        slot('LID', 3, 'field', {'awareness': .80, 'speed': .75},
             {'awareness': .5, 'speed': .5}, 0,
             'Graceful: receivers get free more often and the ball leaves the Archer\'s lane by pass.',
             dict(offence=field((40, 55), (-20, 20), note='stay behind the ball against the break'),
                  defence=mark('receiver_near_goal', 'lateral', (5.5, 7),
                               note='beside the receiver, off the line from the platform to him'),
                  restart_own=line((-18, -10), (-14, 14)),
                  restart_opp=line((-9, -5.5), (-18, 18)),
                  hunt=HUNT_BACK),
             'Receiver cover that stays out of the Archer\'s sight line.'),
        keeper(),
    ],
    team=base(carrier__finish_pref=dict(carry=.30, close=.30, mid=.25, deep=.15), carrier__shot_range_max_m=28.,
              off__first_action_max_s=1.5, pos__ball_def=.6, pos__goal_def=1.8, pos__opp_def=.3,
              def__bias_press=-3., def__bias_pursue=2., def__scheme='contain_funnel', def__pressers_max=3,
              def__commit_gap_m=3., def__contain_gap_m=[5, 7], def__takedown_line_m=25.,
              def__contact_by_area=dict(midfield='contain', arc='takedown', zone='takedown'),
              archer__eagerness=3., archer__target_priority=dict(carrier=1., receiver_near_goal=.7, other=.3),
              restart__def_alignment='ring', restart__taker_slot='RING', hunt__contestant_slot='SHADOW'),
    signature={'freezes_per_opp_possession_vs_neutral_ratio': ['>=', 1.5],
               'opp_turnovers_within_3s_of_freeze_share': ['>=', .30],
               'takedowns_beyond_25m_of_own_goal_share': ['<=', .30]},
    strengths=['Uses the one defender the offence cannot block, tackle or outrun: the arrow flies at 250 m/s.',
               'Each freeze removes an attacker for 5 s of a 30 s clock.',
               'Field defenders stay on their feet and in shape, so few defensive fouls.',
               'As built, a frozen ball holder drops the ball (engine behaviour, not Rulebook text: Q-TAC-2).'],
    weaknesses=['Rests on one athlete. The roster carries two Archers at most.',
                'Attackers inside the zone cannot be frozen.',
                'A quick score arrives before the Archer has released more than a few arrows.',
                'Arrows may not be shot at a player outside the Archer\'s own half (ratified, not built in v0/3).'],
    canon=['The Archer shoots only legal targets: opposing field players whose team has control, outside both '
           'zones, not frozen or immune, in the Archer\'s own half, after the Hunt has cleared; 15 arrows and '
           '5 freezes per opposing possession.',
           'No defender touches a frozen or immune player in breach of the immunity rules (a major foul); RINGs '
           'play the ball, not the man.',
           'Containing is not marking inside 5 m before the ball is live: at restarts SHADOWs stand 5.5 m back.'],
))

# ============================================================== 5 PRESS
T.append(dict(
    id='PRESS', name='High Press', tags=['tackle_count_pressure'],
    idea='Mark every opponent everywhere and take the ball carrier down at first reach, as far from the own goal '
         'as possible. A turnover is scrimmaged where it happens, so winning the ball in the opponent\'s half '
         'starts the next attack close to goal.',
    formation='4 HOUND on and around the ball, 4 MARK on the receivers, 2 SWEEP behind',
    slots=[
        slot('SWEEP', 2, 'field', {'speed': .85, 'tackling': .75, 'awareness': .70},
             {'speed': .5, 'tackling': .3, 'awareness': .2}, 1,
             'FAILURE with none in band: one missed tackle or one long pass is a free run at the Keeper. With '
             'one in band half the field is uncovered (graceful).',
             dict(offence=field((40, 50), (6, 15), 'mirror'),
                  defence=ball((-30, -15), (6, 15), True, note='always 15 m or more goal-side of the ball'),
                  restart_own=line((-22, -14), (4, 10), True),
                  restart_opp=line((-22, -14), (4.8, 12), True),
                  hunt=field((30, 38), (4.8, 12), 'mirror')),
             'Last line: covers the space behind the press.',
             overrides={'def.press_line_m': 45., 'def.commit_gap_m': 5.}),
        slot('HOUND', 4, 'field', {'tackling': .85, 'speed': .80, 'stamina': .70},
             {'speed': .35, 'tackling': .45, 'stamina': .2}, 2,
             'FAILURE below two in band: two go to the ball every time; if they miss or arrive late the press is '
             'open behind them. With two or three the outlets are pressed by weaker tacklers (graceful).',
             dict(offence=ball((3, 12), (-12, 12)),
                  defence=mark('carrier', 'goal_side', (0, 1.5), note='two nearest go to the ball; the others take '
                               'the nearest outlets'),
                  restart_own=line((-3, -0.8), (-12, 12)),
                  restart_opp=line((-6, -5.5), (-10, 10)),
                  hunt=rule('The fastest HOUND is the contestant; two others stand 7 m from the centre spot in '
                            'the own half and close on the release.')),
             'Ball hunter: closes at full speed and tackles at first reach.'),
        slot('MARK', 4, 'field', {'speed': .80, 'agility': .75, 'awareness': .70},
             {'speed': .35, 'agility': .35, 'awareness': .3}, 0,
             'Graceful: receivers get open more often and the carrier has a pass before the tackle arrives.',
             dict(offence=arc('attacked', (21, 28), (-55, 55)),
                  defence=mark('nearest_unmarked_opponent', 'ball_side', (1.5, 3),
                               note='denies the pass by position; never holds a player without the ball'),
                  restart_own=line((-2, -0.8), (-25, 25)),
                  restart_opp=line((-6, -5.5), (-25, 25)),
                  hunt=HUNT_BACK),
             'Tight marker on a receiver.'),
        keeper(), archer(),
    ],
    team=base(carrier__bias_shoot=1., carrier__shot_range_max_m=30.,
              tempo__shot_window_s=[2, 14], off__first_action_max_s=2., off__short_field_trigger_m=45.,
              pos__ball_def=2.5, pos__goal_def=0., pos__opp_def=2.,
              def__bias_press=5., def__bias_pursue=2., def__scheme='man_press', def__commit_gap_m=8.,
              restart__def_alignment='man_up', restart__taker_slot='nearest', hunt__contestant_slot='HOUND',
              hunt__win_action='carry_out'),
    signature={'tackles_in_opponent_half_share': ['>=', .50], 'turnover_win_distance_from_own_goal_m_mean': ['>=', 55.],
               'time_to_first_contact_on_carrier_s_median': ['<=', 4.0]},
    strengths=['Uses the two-tackle rule directly: each takedown is half of a turnover.',
               'A turnover high up the field is scrimmaged there, a short field for the next attack.',
               'Gives a slow-building opponent no time to set its shape.'],
    weaknesses=['Ten players upfield; only two behind the ball.',
                'A defensive minor at tackle count 0 is a half goal (a full goal in period 4 and overtime), and '
                'tackling at first reach invites fouls.',
                'After the first tackle the scrimmage puts every defender back behind the ball line, so the press '
                'has to be rebuilt.',
                'Stamina cannot matter in Native v0/3: fatigue is off.'],
    canon=['Takedowns are on the ball carrier only, below the neck.',
           'MARKs deny by position. Holding or hooking a player without the ball is a minor foul and tackling him '
           'is a major foul; neither is used.',
           'At restarts every defender stands 5.5 m or more behind the restraining line (5 m marking).'],
))

# ============================================================== 6 COUNT
T.append(dict(
    id='COUNT', name='Long Count', tags=['clock_control'],
    idea='Keep the ball for most of the 30 s clock with short, safe passes and take one attempt in the last few '
         'seconds, so the match has fewer possessions. The ball is held in the own half, where no arrow may be '
         'shot, until 12 s remain.',
    formation='3 METRONOME around the ball, 4 LINK in a diamond, 3 REST behind the ball',
    slots=[
        slot('METRONOME', 3, 'field', {'ball_handling': .85, 'throw_accuracy': .75, 'awareness': .75},
             {'ball_handling': .35, 'throw_accuracy': .35, 'awareness': .3}, 2,
             'FAILURE below two in band: a 20 s possession is 8 or more passes; with weak handlers one of them '
             'is lost. With two the third handler is a risk the others pass around (graceful).',
             dict(offence=ball((-8, -3), (-10, 10), note='the handlers stay within one short pass of the ball'),
                  defence=arc('own', (28, 32), (-30, 30)),
                  restart_own=line((-9, -7), (-6, 6), note='takes the safe_reset throw'),
                  restart_opp=line((-10, -7), (-10, 10)),
                  hunt=HUNT_WING),
             'Handler: receives, protects and moves the ball without risk.'),
        slot('LINK', 4, 'field', {'catching': .80, 'agility': .70, 'awareness': .70},
             {'catching': .4, 'agility': .3, 'awareness': .3}, 0,
             'Graceful: more passes are dropped or cut out, in proportion.',
             dict(offence=ball((-2, 10), (8, 15), True),
                  defence=arc('own', (21, 24), (-60, 60)),
                  restart_own=line((-4, -0.8), (8, 15), True),
                  restart_opp=line((-6.5, -5.5), (-18, 18)),
                  hunt=HUNT_BACK),
             'Receiver 8 to 15 m from the ball, always showing an open lane.'),
        slot('REST', 3, 'field', {'tackling': .75, 'speed': .75},
             {'tackling': .4, 'speed': .4, 'awareness': .2}, 0,
             'Graceful: a lost ball is more often a goal against.',
             dict(offence=ball((-25, -15), (-15, 15)),
                  defence=arc('own', (21, 24), (-25, 25)),
                  restart_own=line((-25, -15), (-15, 15)),
                  restart_opp=line((-9, -5.5), (-10, 10)),
                  hunt=rule('The fastest REST is the contestant; the others stand 12 m or more behind the '
                            'centre spot.')),
             'Stays behind the ball in attack so a lost ball meets defenders.'),
        keeper(), archer(),
    ],
    team=base(carrier__bias_pass=3., carrier__bias_shoot=-3., carrier__pass_min_clearance_m=4.,
              carrier__shot_range_max_m=24.,
              carrier__finish_pref=dict(carry=.10, close=.30, mid=.30, deep=.30),
              carrier__pass_len_band_m=[6, 15], carrier__touch_time_max_s=3.,
              carrier__contact_response=dict(run_through=.1, dodge=.7, brace=.2),
              tempo__shot_window_s=[22, 27], tempo__must_shoot_remaining_s=3.,
              tempo__snap_delay_s=dict(leading=8., otherwise=2.), tempo__hold_own_half_until_remaining_s=12.,
              pos__goal_att=.2, pos__goal_def=2., pos__ball_def=.6, pos__spread=2., pos__opp_att=1.5, pos__lane=2.,
              zone__entry_mode='late_only', def__bias_press=-1., def__scheme='deep_shell', def__pressers_max=1,
              def__press_line_m=30., def__commit_gap_m=4., def__takedown_line_m=30.,
              def__contact_by_area=dict(midfield='contain', arc='takedown', zone='takedown'),
              restart__scrim_play='safe_reset', restart__snap40_play='safe_reset',
              restart__taker_slot='METRONOME', hunt__contestant_slot='REST'),
    signature={'own_possession_duration_s_mean_unturned': ['>=', 20.], 'passes_per_possession': ['>=', 5.],
               'shots_with_8s_or_less_left_share': ['>=', .60], 'live_ball_turnovers_per_possession': ['<=', .15]},
    strengths=['Fewer possessions in the match; a lead is harder to overturn.',
               'No legal arrow target while the ball and the team are in their own half (ratified rule).',
               'Three players always behind the ball.'],
    weaknesses=['Gains nothing per possession by itself: it changes how many possessions there are, not what '
                'each is worth.',
                'One attempt per possession, taken against a set defence with the clock nearly out.',
                'The longest exposure to the Archer of any style once it crosses halfway.',
                'May not retreat into its own Keeper Zone (ZR-C, ZR-T), so pressure can pin it at the arc.',
                'Play-clock expiry is a turnover.'],
    canon=['The attempt is released before the 30 s clock expires; a throw released as the clock expires counts.',
           'The snap is always inside the 10 s window. Waiting 8 s inside it is assumed legal; "delay of game" is '
           'a minor foul after a warning and its boundary is not stated (PLACEHOLDER, Q-TAC-4).',
           'No pass or carry goes back into the own Keeper Zone; a ball in the own zone leaves within 5 s (ZR-1).'],
))

# ============================================================== 7 STRIKE
T.append(dict(
    id='STRIKE', name='First Strike', tags=['transition', 'restart_plays'],
    idea='Score within 8 s of gaining the ball, before the defence is set and before the Archer has released '
         'more than a few arrows. Three sprinters stay high even in defence, and every restart and every gain of '
         'possession starts with a long pass to one of them.',
    formation='3 BOLT high, 2 CANNON as long passers, 5 HALF who defend seven-strong with the CANNONs',
    slots=[
        slot('BOLT', 3, 'field', {'speed': .90, 'catching': .75},
             {'speed': .5, 'catching': .3, 'agility': .2}, 2,
             'FAILURE below two in band: a runner who is caught from behind, or who drops a fast long pass, turns '
             'the plan into three players missing from the defence. With two one channel is unused (graceful).',
             dict(offence=arc('attacked', (25, 35), (-50, 50), note='the point each BOLT sprints to on a gain'),
                  defence=field((45, 60), (-25, 25), note='stays high; legal, there is no offside in live play'),
                  restart_own=line((-1.5, -0.8), (-22, 22), note='on the ball line: wide, centre, wide'),
                  restart_opp=line((-12, -5.5), (-25, 25), note='the shallowest legal position'),
                  hunt=rule('The fastest BOLT is the contestant and tips the ball out to a CANNON; the other two '
                            'stand 7 m from the centre spot in the own half and sprint on the release.')),
             'Sprinter: stays high and runs onto long passes.'),
        slot('CANNON', 2, 'field', {'throw_power': .85, 'throw_accuracy': .80},
             {'throw_power': .4, 'throw_accuracy': .4, 'awareness': .2}, 1,
             'FAILURE with none in band: a long pass that is slow or off line is intercepted or run down. With '
             'one in band every break starts from the same player (graceful).',
             dict(offence=ball((-8, -3), (3.2, 8), True),
                  defence=arc('own', (26, 32), (8, 20), 'mirror', note='in the passing lanes; first outlet on a gain'),
                  restart_own=line((-8, -6), (1.6, 4), True, note='takes the go_routes throw'),
                  restart_opp=line((-10, -7), (3.2, 8), True),
                  hunt=HUNT_WING),
             'Long passer: first outlet on every gain and the thrower on every restart.'),
        slot('HALF', 5, 'field', {'tackling': .80, 'speed': .70, 'awareness': .70},
             {'tackling': .4, 'speed': .3, 'awareness': .3}, 0,
             'Graceful: a seven-player defence concedes more, in proportion.',
             dict(offence=ball((-15, -5), (-18, 18)),
                  defence=arc('own', (21, 26), (-60, 60)),
                  restart_own=line((-14, -6), (-18, 18)),
                  restart_opp=line((-7, -5.5), (-18, 18)),
                  hunt=HUNT_BACK),
             'Defender: holds the arc with six others.'),
        keeper({'keeper_skill': .80, 'catching': .70, 'throw_power': .80},
               {'keeper_skill': .4, 'catching': .2, 'jump': .1, 'throw_power': .2, 'height_m': .1},
               'Graceful: without the throw power the Keeper starts breaks with a short pass to a CANNON; '
               'the break starts later.'),
        archer(),
    ],
    team=base(carrier__bias_pass=2., carrier__bias_shoot=2., carrier__shot_range_max_m=30.,
              carrier__finish_pref=dict(carry=.35, close=.35, mid=.20, deep=.10),
              carrier__pass_len_band_m=[20, 50], carrier__touch_time_max_s=2.,
              carrier__contact_response=dict(run_through=.2, dodge=.7, brace=.1), carrier__dribble_use='advance',
              tempo__shot_window_s=[2, 8], off__first_action_max_s=1.5,
              pos__goal_att=3., pos__ball_att=-.5, pos__goal_def=-.5, pos__spread=1.5,
              zone__entry_mode='drive', zone__occupancy_target=2,
              def__bias_press=1., def__bias_pursue=2., def__scheme='lane_gamble', def__press_line_m=40.,
              def__commit_gap_m=7., keeper__distribution='long_outlet',
              restart__scrim_play='go_routes', restart__snap40_play='go_routes', restart__toss_play='line_toss',
              restart__taker_slot='CANNON', hunt__contestant_slot='BOLT'),
    signature={'own_shots_within_8s_of_gain_share': ['>=', .50], 'passes_30m_plus_per_possession': ['>=', .5],
               'bolt_distance_from_own_goal_in_defence_m_mean': ['>=', 45.]},
    strengths=['The defence is not set and the Archer has had little time.',
               'At a 40 m scrimmage after a score the two teams start 20 m apart, a clear runway for a sprinter.',
               'A long pass covers the field faster than any runner.'],
    weaknesses=['Defends with seven.',
                'Needs live turnovers; an opponent whose possessions end in dead balls gives it none.',
                'A fast long pass is hard to catch; the attempt is often a turnover.',
                'Long passes and chosen release speed cannot be expressed in Native v0/3.'],
    canon=['Staying high in live play is legal: offside is judged only at scrimmages, where BOLTs stand on their '
           'own side of the ball line.',
           'At a 40 m scrimmage BOLTs start at or behind their own 40 m line.',
           'One dribble per possession: a BOLT may throw the ball ahead of himself once and replay it; a second '
           'is a minor foul and is not used.',
           'A tossed ball cannot score until another player controls it.'],
))

# ============================================================== 8 LOCK
T.append(dict(
    id='LOCK', name='Zone Lock', tags=['keeper_zone_5s_exploit'],
    idea='Turn the attacker\'s 5 s zone limit into the defence\'s weapon. Leave the middle of the arc open, and '
         'when the carrier enters, wrap him and hold him up inside the zone without grounding him, so his 5 s '
         'runs out and the ball turns over without a tackle being counted.',
    formation='2 CLAMP at the door, 4 GATE on the rest of the arc, 4 DENY on the outlets',
    slots=[
        slot('CLAMP', 2, 'field', {'strength': .85, 'tackling': .80, 'mass_kg': 230.},
             {'strength': .3, 'tackling': .3, 'balance': .2, 'mass_kg': .2}, 2,
             'FAILURE below two in band: a carrier who breaks the wrap is 20 m from goal with no one in front '
             'of him but the Keeper. There is no graceful case: the door needs both jambs.',
             dict(offence=arc('attacked', (21, 25), (8, 20), 'mirror'),
                  defence=arc('own', (20.5, 22), (9, 14), 'mirror',
                              note='either side of the open lane; closes on the carrier as he enters'),
                  restart_own=line((-2, -0.8), (1.6, 4), True),
                  restart_opp=line((-6.5, -5.5), (2, 5), True),
                  hunt=HUNT_BACK),
             'Door jamb: wraps the carrier as he enters and holds him up inside the zone.',
             overrides={'def.holdup_drive': 'into_zone'}),
        slot('GATE', 4, 'field', {'tackling': .80, 'strength': .70, 'speed': .70},
             {'tackling': .4, 'strength': .3, 'speed': .3}, 0,
             'Graceful: more entries are made away from the door, where no hold-up is waiting.',
             dict(offence=arc('attacked', (22, 30), (-55, 55)),
                  defence=arc('own', (20.5, 23), (25, 60), 'mirror',
                              note='two each side; shuts the way out behind a carrier who has entered'),
                  restart_own=line((-3, -0.8), (-16, 16)),
                  restart_opp=line((-6.5, -5.5), (-16, 16)),
                  hunt=rule('The fastest GATE is the contestant; the others stand in the own half 12 m or more '
                            'behind the centre spot.')),
             'Arc guard away from the door.'),
        slot('DENY', 4, 'field', {'speed': .80, 'awareness': .75, 'agility': .70},
             {'speed': .35, 'awareness': .35, 'agility': .3}, 0,
             'Graceful: the held-up carrier finds a pass out more often and the 5 s is not used up.',
             dict(offence=ball((-10, 6), (-18, 18)),
                  defence=mark('nearest_unmarked_opponent', 'ball_side', (1.5, 3),
                               note='on the receivers outside the arc, 24 to 34 m from the own goal'),
                  restart_own=line((-12, -6), (-18, 18)),
                  restart_opp=line((-9, -5.5), (-20, 20)),
                  hunt=HUNT_WING),
             'Outlet cover: takes away the pass out of the zone.'),
        keeper(), archer(),
    ],
    team=base(pos__goal_def=2.5, pos__ball_def=1., pos__opp_def=1.5,
              def__bias_press=-1., def__scheme='zone_trap', def__press_line_m=26., def__commit_gap_m=5.,
              def__takedown_line_m=26.,
              def__contact_by_area=dict(midfield='contain', arc='wrap', zone='wrap'),
              def__contact_at_count1='takedown',
              restart__def_alignment='gate', restart__taker_slot='DENY', hunt__contestant_slot='GATE'),
    signature={'opp_zone_residence_turnovers_per_zone_entry_vs_neutral_ratio': ['>=', 3.0],
               'wrap_share_of_contact_in_own_zone_at_count0': ['>=', .80],
               'takedowns_in_own_zone_at_count0_share': ['<=', .10]},
    strengths=['A residence turnover costs the defence no tackle and gives the offence no scrimmage.',
               'A takedown inside the zone at count 0 would hand the offence a scrimmage near goal with a fresh '
               '5 s; this plan never gives that.',
               'Defenders stay near their goal; little space behind them.'],
    weaknesses=['Does nothing to a team that does not enter the zone.',
                'The carrier needs under 2 s from arc to goal plane; the hold-up must work at once.',
                'Whether a wrap can hold a carrier for seconds in the engine is unmeasured.',
                'The count-1 switch to takedown needs a tackle count the athlete cannot see in Native v0/3.'],
    canon=['A wrap is legal on the ball carrier from below the neck down.',
           'Hands go on the body, not the ball: two opponents holding the ball for 1 s is a held ball, play stops '
           'and the zone clock resets.',
           'Defenders wait outside the zone (20.5 m or more) and enter only with the carrier, within 5 m of him.',
           'No contact on a Keeper in his zone; the plan applies to the ball carrier only.'],
))

IDS = [t['id'] for t in T]

# ----------------------------------------------------------------------------- matchup hypotheses (all 28 pairs)
M = []


def edge(w, l, why):
    M.append(dict(a=w, b=l, predicted_edge=w, reason=why))


def open_(a, b, q):
    M.append(dict(a=a, b=b, predicted_edge=None, reason=q))


edge('ANVIL', 'ARC', 'Arc\'s throwers and feeders stand outside the zone in the Archer\'s half for the whole '
     'possession: up to five freezes on near-stationary targets, and as built a frozen ball holder drops the ball.')
edge('PRESS', 'ARC', 'Arc needs time to set five players on the arc and circulate. The press tackles the first '
     'receiver before the arc forms, and GUN and SCREEN profiles are not chosen for escaping pressure.')
edge('ARC', 'COUNT', 'Count\'s shell waits on the arc and commits late (4 m). In-band GUNs release from 21 to 24 m '
     'over it, and Count\'s long possessions do not lower the quality of Arc\'s attempts.')
edge('ARC', 'LOCK', 'Lock\'s trap needs a zone entry and Arc does not enter. Lock contains outside its takedown '
     'line, so GUNs release unhurried.')
edge('WAVE', 'ANVIL', 'Attackers inside the zone are not legal arrow targets and Wave keeps its finishers there. '
     'Anvil\'s shadows contain without tackling, which gives the rotation time.')
edge('WAVE', 'RAM', 'Ram\'s Wall is staffed by heavy RAM and PLOW profiles. A rotation every 3.5 s makes them '
     'follow attackers in and out of the zone or stand unmarked.')
edge('LOCK', 'WAVE', 'Wave enters the zone by design with 1.5 s of margin. A hold-up of 1.5 s turns a visit into '
     'a residence turnover.')
edge('ANVIL', 'RAM', 'Ram puts the whole possession on one carrier who runs 40 m or more outside the zone: the '
     'Archer\'s first target. As built a freeze makes him drop the ball.')
edge('PRESS', 'RAM', 'Ram wants its free first tackle close to goal. The press forces it far out, leaving a '
     'second run of 50 m or more with no tackle left.')
edge('RAM', 'COUNT', 'Count\'s shell commits late and avoids contact; a wedge reaches the arc at speed and needs '
     'under 2 s inside. Ram\'s Wall tackles hard and a 20 s possession offers it many chances.')
edge('RAM', 'STRIKE', 'Strike defends with seven, so the wedge meets fewer tacklers. Ram\'s turnovers are mostly '
     'dead balls, which deny Strike the live gain it needs.')
edge('RAM', 'LOCK', 'The trap needs about 5 s of hold-up. A wedge-led carry needs under 2 s from arc to goal '
     'plane, and Lock chooses not to ground a carrier in the zone at count 0.')
edge('ANVIL', 'COUNT', 'Once Count crosses halfway it still holds the ball for 10 s or more outside the zone, the '
     'longest exposure of any style. The edge is larger in Native v0/3, which does not enforce the own-half '
     'arrow rule.')
edge('STRIKE', 'ANVIL', 'Strike attempts within 8 s, before the Archer has released more than a few arrows, and '
     'its long passes travel over shadows who are containing, not tackling.')
edge('PRESS', 'COUNT', 'Count\'s short passes are exactly what man pressure contests, and Count may not retreat '
     'into its own zone, so the press compresses it against the arc.')
edge('STRIKE', 'PRESS', 'The press commits eight players upfield man to man. One completed long pass to a BOLT '
     'beats all of them, with two SWEEPs behind.')
edge('COUNT', 'STRIKE', 'Count gives up few live turnovers and keeps three REST players behind the ball, so the '
     'BOLTs waiting high receive little; and Count attacks a seven-player defence.')
edge('LOCK', 'COUNT', 'Count attempts with 3 to 8 s left. A hold-up at the door squeezes it between the zone '
     'limit and the play clock with no time to recycle.')
edge('LOCK', 'STRIKE', 'Lock does not press upfield, so its defenders are at the arc when the long pass arrives. '
     'The break ends in a zone entry against a set trap.')
open_('ARC', 'WAVE', 'Neither method touches the other\'s. Outside finishing against man marking, inside '
      'finishing against an arc shell: no prediction.')
open_('ARC', 'RAM', 'Ram\'s Wall stands at 24 to 28 m, right where GUNs release, but its heavy profiles are slow '
      'to close: no prediction.')
open_('ARC', 'STRIKE', 'Arc attacks ten against seven, but every saved throw is a live ball with BOLTs already '
      'high. Which is larger is the question.')
open_('WAVE', 'PRESS', 'The press may break the rotation before it forms, or its man marking may be dragged in '
      'and out of the zone: no prediction.')
open_('WAVE', 'COUNT', 'Count\'s shell must follow attackers into the zone or leave them free; whether it copes '
      'is not something reasoning settles.')
open_('WAVE', 'STRIKE', 'Wave commits five or six attackers deep, but many of its turnovers are dead balls '
      '(residence): no prediction.')
open_('ANVIL', 'PRESS', 'Two defensive styles with plain offences. The press shortens the field, which also '
      'shortens the Archer\'s time: no prediction.')
open_('ANVIL', 'LOCK', 'Two defensive styles with plain offences: no prediction.')
open_('PRESS', 'LOCK', 'Two defensive styles with plain offences: no prediction.')

assert len(M) == 28 and len({frozenset((m['a'], m['b'])) for m in M}) == 28
