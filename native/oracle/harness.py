"""Offline scenario execution and one-decision interventions."""
from dataclasses import dataclass
from hashlib import sha256

from native import cognition, prism_core
from native.port import digest


@dataclass(frozen=True)
class Force:
    athlete: str
    stage: str
    index: int
    decision: str | None = None
    turn: int = 1
    prefix: tuple[tuple[str, int], ...] = ()


class Decision:
    """Force one option from a surfaced menu, preserving downstream choices."""

    def __init__(self, force=None):
        self.force = force
        self.turns = 0
        self.applied = False
        self.intent = None
        self.option = None

    def __call__(self, view, belief, remaining):
        force = self.force
        if self.applied or force is None or view.athlete != force.athlete:
            return cognition.decide(view, belief)
        self.turns += 1
        if force.decision is not None:
            selected = view.observation_id + '/decision' == force.decision
        else:
            selected = self.turns == force.turn
        if not selected:
            return cognition.decide(view, belief)
        if view.core_entropy is None:
            raise ValueError('forcing requires a CORE menu')

        prefix = iter(force.prefix)
        committed = next(prefix, None)

        def choose(stage, options):
            nonlocal committed
            if committed is not None:
                name, index = committed
                if name != stage or not 0 <= index < len(options):
                    raise ValueError('captured commitment no longer matches its menu')
                committed = next(prefix, None)
                return index
            if stage == force.stage and not self.applied:
                if not 0 <= force.index < len(options):
                    raise ValueError('option outside the surfaced menu')
                self.applied = True
                self.option = options[force.index]
                return force.index

        intent, record = prism_core.decide(view, belief, selector=choose)
        if not self.applied:
            raise ValueError(f'decision did not expose stage {force.stage!r}')
        self.intent = intent
        return intent, record


def branch_seed(moment, option, index):
    return int.from_bytes(sha256(f'oracle/1/{moment}/{option}/{index}'.encode()).digest()[:8], 'big')


def reseed(driver, seed):
    """Resample future draws, keeping the already delivered beliefs and state."""
    port = driver.port
    engine = port.m.e
    port.seed = seed
    for namespace, streams in (('motion', port.m.rng), ('sensor', port.streams)):
        for name, rng in streams.items():
            rng.seed(f'oracle/{seed}/{namespace}/{name}')
    if hasattr(engine, 'rb_coin'):
        engine.rb_coin.seed(f'oracle/{seed}/coin')
    if port.communication is not None:
        port.communication.seed = f'oracle/{seed}/mesh'


class EventHorizon:
    def __init__(self, port, team, stop, actor=None):
        self.port = port
        self.team = team
        self.stop = stop
        self.actor = actor
        self.possession_team = port.m.e.possession.pp or port.m.s.owner or team
        ball = port.m.s.ball
        self.flight = ({'passed':'pass','shot':'shot'}.get(ball.mode.value)
                       if actor is None or actor == ball.last_releaser else None)
        self.pass_result = self.shot_result = self.tackle_result = None

    def consume(self, events, intent):
        team, actor = self.team, self.actor
        for row in events:
            kind, data = row['event'], row['data']
            if kind == 'release':
                release_kind = data.get('kind')
                if self.flight is not None:
                    self.end_flight('missed')
                pending = (release_kind == 'pass' and self.pass_result is None
                           or release_kind == 'shot' and self.shot_result is None)
                if (actor is None or actor == data.get('player')) and pending:
                    self.flight = release_kind
                    if release_kind == 'shot' and self.stop == 'shot_taken':
                        return 'shot_taken'
            elif self.flight is not None:
                if kind == 'control':
                    catcher = self.port.m.s.players[data['player']]
                    self.end_flight('caught' if self.flight == 'pass' and catcher.team == team else 'missed')
                elif kind == 'goal':
                    self.end_flight('scored' if data['team'] == team else 'missed')
                elif kind in ('boundary', 'restart_awarded', 'period_end'):
                    self.end_flight('missed')
            if kind == 'c3_grounding' and data.get('counted'):
                if intent is None or data.get('player') == intent.target or data.get('credited') == actor:
                    self.tackle_result = 'grounded'
                    if self.stop in ('takedown','takedown_action'):
                        return 'takedown'
            if kind in ('goal','foul_award'):
                if self.stop == 'score' or self.stop == 'possession' and kind == 'goal':
                    return 'score'
                if self.stop == 'finishing' and intent and intent.kind == 'stretch':
                    return 'stretch_scored'
            if self.stop == 'possession' and kind == 'restart_awarded' and data.get('team') != self.possession_team:
                return 'turnover'
            if self.stop == 'possession' and kind == 'period_end':
                return 'end_period'
            if self.stop == 'finishing' and intent and intent.kind == 'stretch' and kind == 'stretch_end':
                if data.get('carrier') == actor:
                    return 'stretch_ended'
        if self.stop == 'pass_caught' and self.pass_result == 'caught':
            return 'pass_caught'
        if self.stop == 'pass_missed' and self.pass_result == 'missed':
            return 'pass_missed'
        if self.stop == 'passing' and self.pass_result:
            return 'pass_' + self.pass_result
        if self.stop == 'finishing' and self.shot_result:
            return 'shot_' + self.shot_result

    def end_flight(self, outcome):
        if self.flight == 'pass':
            self.pass_result = outcome
        else:
            self.shot_result = outcome
        self.flight = None

    def after_step(self, intent, outcomes, commands):
        port = self.port
        state = port.m.s
        ball = state.ball
        if (self.flight is not None and ball.mode == port.types.BallMode.LOOSE
                and ball.z <= ball.radius and not (ball.vx or ball.vy or ball.vz)):
            flight = self.flight
            self.end_flight('missed')
            if flight == 'pass' and self.stop in ('passing','pass_missed'):
                return 'pass_missed'
            if flight == 'shot' and self.stop == 'finishing':
                return 'shot_missed'
        if self.stop == 'possession' and port.m.e.possession.pp not in (None, self.possession_team):
            return 'turnover'
        if self.stop == 'takedown_action' and intent is not None:
            if (self.actor, intent.target) not in port.m.c3_holds:
                self.tackle_result = self.tackle_result or 'hold_ended'
                return 'hold_ended'
        if self.stop == 'evasion_action' and intent is not None:
            if state.ball.carrier != self.actor:
                return 'control_lost'
            if state.now >= intent.decided_ms + port.prism_decision_interval_ms(self.actor,intent):
                return 'maneuver_complete'
        if self.stop in ('passing','finishing') and intent is not None:
            command = intent.intent_id + '/command'
            failed = next((o.status for o in outcomes if o.command_id == command and o.status != 'released'), None)
            if failed:
                return failed
            if self.flight is None and intent.kind in ('shoot','pass','stretch'):
                if not any(c.command_id == command for c in commands):
                    return 'unadmitted'
        if state.phase == port.types.Phase.FINAL:
            return 'match_final'


def run(driver, *, prepared=None, force=None, team=None, stop='possession', max_ms=30_000,
        seed=None, diagnostic=None):
    if max_ms <= 0:
        raise ValueError('max_ms must be positive')
    if stop not in ('possession','time','passing','finishing','takedown_action','evasion_action','pass_caught',
                    'pass_missed','shot_taken','takedown','score'):
        raise ValueError(f'unknown stop condition {stop}')
    port, first_step = driver.port, driver.steps
    state, engine = port.m.s, port.m.e
    actor = force.athlete if force else None
    team = team or (state.players[actor].team if actor else engine.possession.pp or state.owner or 'A')
    if team not in ('A','B'):
        raise ValueError('team must be A or B')
    if seed is not None:
        reseed(driver, seed)
        if prepared:
            view, belief, remaining = prepared
            if view.core_entropy is not None:
                from dataclasses import replace
                view = replace(view, core_entropy=f'{seed}/{view.athlete}/{view.delivered_ms}')
            prepared = view, belief, remaining

    start_ms, start_score = state.now, dict(state.score)
    log_start, outcome_start, command_start = len(engine.log), len(port.outcomes), len(port.command_log)
    observer = EventHorizon(port, team, stop, actor)
    action = EventHorizon(port, team, diagnostic, actor) if diagnostic else None
    action_reason = action_ms = None
    decision = Decision(force)
    initial_log = log_start
    reason = None
    while state.now - start_ms < max_ms and not driver.final:
        driver.advance(decision if force and not decision.applied else None, prepared=prepared)
        prepared = None
        new_events = engine.log[log_start:]
        reason = observer.consume(new_events, decision.intent)
        log_start = len(engine.log)
        if action is not None and action_reason is None:
            action_reason = (action.consume(new_events, decision.intent)
                             or action.after_step(decision.intent, port.outcomes[outcome_start:],
                                                  port.command_log[command_start:]))
            if action_reason is not None:
                action_ms = state.now - start_ms
        if reason is None:
            reason = observer.after_step(decision.intent, port.outcomes[outcome_start:],
                                         port.command_log[command_start:])
        if reason is not None:
            break
    if force and not decision.applied:
        raise ValueError('forced decision was never reached')
    events = engine.log[initial_log:]
    trace = port.trace.copy()
    trace.update(digest(events).encode())
    other = state.other(team)
    result = {'end_reason': reason or ('match_final' if driver.final else 'time_limit'),
            'points_for': state.score[team] - start_score[team],
            'points_against': state.score[other] - start_score[other],
            'events': events, 'steps': driver.steps - first_step, 'elapsed_ms': state.now - start_ms,
            'trace_hash': trace.hexdigest(),
            'pass_result': observer.pass_result, 'shot_result': observer.shot_result,
            'tackle_result': observer.tackle_result,
            'forced_intent': decision.intent.kind if decision.intent else None}
    if action is not None:
        result['action_outcome'] = {'reason':action_reason or 'unresolved_at_possession_end',
                                    'elapsed_ms':action_ms,'pass':action.pass_result,
                                    'shot':action.shot_result,'tackle':action.tackle_result}
    return result
