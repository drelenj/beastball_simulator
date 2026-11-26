"""Read-only diagnostics for the A6 comparison."""
from bisect import bisect_right
from collections import Counter, defaultdict, deque
from math import hypot
from random import Random

from native import cognition, paired_policy

SAMPLE_SEED = 334
NEAR_GOAL_M = 20.
SETTLE_WINDOW_MS = 500


class Diagnostics:
    def __init__(self, driver, witness):
        self.witness = witness
        port = driver.port
        self.port = port
        state, engine = port.m.s, port.m.e
        self.mix = Counter()
        self.settle_history = defaultdict(deque)
        self.shots = {}
        self.commits = {}
        decisions = {}
        advance, submit, release = driver.advance, port.submit, engine.release

        def select(view, belief, _remaining):
            learned = getattr(port, 'learned_values', None)
            intent, record = (cognition.decide(view, belief, learned_values=learned)
                              if learned is not None and view.holds_ball else cognition.decide(view, belief))
            menus = {menu['stage']: menu['choice'] for menu in record.get('core_menus', ())}
            if 'carrier' in menus and hypot(100.-view.own_goal_x-view.x, 50.-view.y) <= NEAR_GOAL_M:
                choice = menus['carrier'].split(':', 1)[0]
                category = {'shoot':'shot', 'carry_mouth':'route_carry',
                            'commit_scoring_attempt':'stretch'}.get(choice, 'continuation')
                self.mix[category] += 1
            if view.role == 'keeper':
                decisions[view.athlete] = (menus.get('keeper'), intent.auxiliary)
            elif intent.contact == 'takedown':
                course = belief.ball_course
                tracks = tuple(t for t in belief.tracks
                               if 0 <= view.delivered_ms-t.captured_ms <= belief.max_track_age_ms)
                decisions[view.athlete] = (
                    paired_policy.fresh_ball_holder(view, belief, tracks),
                    view.delivered_ms-course.captured_ms if course else None,
                    view.release_cue,
                )
            return intent, record

        def observed_submit(intent):
            actual = state.ball.carrier
            result = submit(intent)
            if result['status'] != 'accepted':
                return result
            if state.players[intent.athlete].role == 'keeper':
                choice, auxiliary = decisions.get(intent.athlete, (None, None))
                history = self.settle_history[intent.athlete]
                if choice != 'settle' or auxiliary is None:
                    history.clear()
                else:
                    history.append((state.now, auxiliary.target))
                    while len(history) > 1 and history[1][0] <= state.now-SETTLE_WINDOW_MS:
                        history.popleft()
            if intent.contact == 'takedown' and intent.target and actual != intent.target:
                believed, age, cue = decisions.get(intent.athlete, (None, None, None))
                self.commits[(intent.athlete, intent.target, intent.decided_ms)] = dict(
                    true_holder=actual, believed_holder=believed, frame_age_ms=age,
                    release_cue_active=cue is not None, release_cue_target=cue,
                    ball_mode=state.ball.mode.value, event_position=len(engine.log))
            return result

        def observed_release(pid, velocity, kind='pass', *args, **kwargs):
            start = len(engine.log)
            result = release(pid, velocity, kind, *args, **kwargs)
            if result and kind == 'shot':
                team = state.players[pid].team
                keeper = next((p for p in state.players.values()
                               if p.active and p.role=='keeper' and p.team != team), None)
                row = next((row for row in engine.log[start:] if row['event']=='release'), None)
                if keeper is not None and row:
                    history = self.settle_history[keeper.id]
                    now = row['t_ms']
                    # Settle target commands hold their value until the next accepted command.
                    current = history[-1][1] if history and now-history[-1][0] <= port.config.decision_ms*2 else None
                    past = next((target for time,target in reversed(history)
                                 if time <= now-SETTLE_WINDOW_MS), None)
                    self.shots[row['id']] = dict(
                        keeper=keeper.id, t_ms=now, speed_mps=keeper.speed,
                        settle_target=current,
                        settle_distance_m=hypot(keeper.x-current[0], keeper.y-current[1]) if current else None,
                        settle_speed_mps=hypot(current[0]-past[0], current[1]-past[1])*2 if current and past else None)
            return result

        def observed_advance(*, progress=None):
            return advance(select, progress=progress)

        driver.advance = observed_advance
        port.submit = observed_submit
        engine.release = observed_release

    def result(self, observed):
        log = self.port.m.e.log
        releases = [row for row in log if row['event'] in ('release','restart_release')]
        transports = [row for row in log if row['event'] in
                      ('release','restart_release','handoff_complete','control','restart_awarded','period_end')]
        release_ids = [r['id'] for r in releases]
        transport_ids = [r['id'] for r in transports]
        episodes = []
        for episode in observed['tackles']:
            if episode['targeted_actual_carrier']:
                continue
            key = (episode['player'], episode['target'], episode['start_ms'])
            probe = self.commits[key].copy()
            at = probe.pop('event_position')
            index = bisect_right(release_ids, at)
            release = releases[index-1] if index else None
            index = bisect_right(transport_ids, at)
            transport = transports[index-1] if index else None
            elapsed = episode['start_ms']-release['t_ms'] if release else None
            event = transport['event'] if transport else None
            if event == 'handoff_complete' and transport['data'].get('giver') == episode['target']:
                cause = 'handoff'
            elif (event in ('release','restart_release') and probe['true_holder'] is None
                  and transport['data'].get('player') == episode['target']
                  and probe['ball_mode'] in ('passed','shot')):
                cause = 'release in flight'
            elif probe['believed_holder'] == episode['target'] and probe['frame_age_ms'] > 0:
                cause = 'stale belief'
            else:
                cause = 'other'
            episodes.append(episode | probe | dict(since_release_ms=elapsed, cause=cause))
        sample = sorted(Random(SAMPLE_SEED).sample(episodes, min(20,len(episodes))),
                        key=lambda row: (row['start_ms'], row['player']))
        return dict(rb334={
            'keeper_set_mps': self.port.m.assume['keeper_set_mps'],
            'keeper_at_shot': [self.shots[shot['release_id']] for shot in observed['shots']
                               if shot['release_id'] in self.shots],
            'shots_faced': sum(shot['keeper'] is not None for shot in observed['shots']),
            'near_goal_mix': dict(self.mix),
            'phantom_causes': dict(Counter(row['cause'] for row in episodes)),
            'phantom_sample': sample,
        })
