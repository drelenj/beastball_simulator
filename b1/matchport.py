"""SPRINT-30 N-athlete runtime: sensors, command ingress and motor hooks on the
real B0 engine. The B0 Match.step is used only as the physics/rules stepper;
every legacy tactical hook is replaced by a B1 command reader or a trap.
"""
import copy
import hashlib
import math
import os
import sys
from collections import Counter
from dataclasses import asdict

from .cognition import (AthleteView, BeliefState, MotorCommand, PhysicalOutcome,
                        Signals, Track, BALL, decide, receive_outcome)
from .runtime import ALL_FEATURE_ENV, REPO, digest

LOCOMOTION = ('carry', 'pursue', 'press', 'mark', 'support', 'home', 'scan',
              'search', 'keeper_set', 'keeper_save')
PASSIVE = ('retain', 'archer_hold', 'restart_wait', 'no_action')
LEGACY_TRAPS = ('c4c2_decide', 'pocket_decide')
LEGACY_CLASS_TRAPS = ('carrier_decision', 'arrow_decisions', 'c4c2_decide', 'c4c2_targets',
                      'route_receiver', 'c4c2_inbound', 'penalty_targets')


def forbidden(*a, **k):
    raise RuntimeError('legacy tactical controller reached')


class MatchPort:
    def __init__(self, seed, scenario=None):
        sys.path.insert(0, str(REPO))
        for key in ALL_FEATURE_ENV:
            os.environ.pop(key, None)
        import pocket4_proto as X
        import prism_ratings_v0
        P = X.install(X.load_pocket())
        over, extras, names = X.make_rosters(seed=seed)
        X.S.tend = {pid: X.PT.Tend(n['position'] if n['position'] in X.PT.POSITIONS else 'TRK',
                                   n.get('report_arch', '')) for pid, n in names.items()}
        X.S.on = set(X.SYSTEMS)
        X.S.shape, X.S.extras, X.S.names, X.S.seed, X.S.prism_r = 'sphere', extras, names, seed, None
        P.ROSTER_OVERRIDES = P.validate_roster(over) and over
        self.m = m = P.CORE.match.Match(P.configuration(dict(P.SETTINGS), seed, copy.deepcopy(P.CALIBRATION)))
        self.types, self.geom = P.CORE.types, P.CORE.geometry
        self.seed, self.ratings = seed, prism_ratings_v0.assign(over, names)
        self.settings = {k: P.SETTINGS[k] for k in ('period_seconds', 'periods', 'overtime_seconds', 'play_clock')}
        self.ruleset = m.cfg.get('ruleset', '1.0.1')
        self.move, self.pending, self.save_mode, self.restart_choice = {}, {}, {}, {}
        self.outcomes, self.feedback, self.flight, self.n_out = [], {}, None, 0
        self.sensors, self.gaze, self.last_ball, self.public = {}, {}, {}, {}
        self.log_seen, self.hook_calls = 0, Counter()
        self._orig_keepers = type(m).c4c_keepers
        self._orig_ready = m.e.ready
        # ---- B1 hooks: instance attributes shadow every legacy tactical entry point
        m.carrier_decision = self._ball_motor
        m.arrow_decisions = self._archer_motor
        m.c4c_keepers = self._keeper_motor
        m.c4c2_targets = m.route_receiver = lambda targets: None
        m.c4c2_inbound = lambda *a, **k: None
        m.penalty_targets = self._targets
        m.e.ready = self._ready
        # class-level traps: the legacy tactical functions themselves are unreachable
        cls, pcls = type(m), type(next(iter(m.pol.values())))
        self.legacy = {n: getattr(cls, n) for n in LEGACY_CLASS_TRAPS if hasattr(cls, n)}
        for name in LEGACY_CLASS_TRAPS:
            setattr(cls, name, forbidden)
        for name in ('targets', 'pass_choice', 'pass_ranked'):
            setattr(pcls, name, forbidden)
        for name in LEGACY_TRAPS:
            setattr(m, name, forbidden)
        for team, pol in m.pol.items():
            pol.targets = lambda s, team=team: self._targets(team)
            pol.pass_choice = self._restart_receiver
            pol.pass_ranked = lambda s, p: []      # OWN-5: no receiver replacement
        if scenario in ('g1', 'g1_close'):
            self._g1((47., 50.6) if scenario == 'g1_close' else (49., 56.))

    # ------------------------------------------------------------ scenario (G1)
    def _g1(self, defender):
        s, T = self.m.s, self.types
        s.phase, s.now, s.owner = T.Phase.LIVE, 1000, 'A'
        s.restart = s.recovery = s.reconstruction = s.advantage = s.penalty = None
        s.opening_touched, s.opening_deadline = True, None
        for p in s.players.values():
            p.active = False
        for pid, (x, y) in {'A0': (40., 50.), 'A1': (56., 47.), 'B0': defender}.items():
            p = s.players[pid]
            p.active, p.x, p.y, p.z, p.vx, p.vy, p.vz = True, x, y, 0., 0., 0., 0.
            p.facing = (1., 0.) if p.team == 'A' else (-1., 0.)
            p.next_action = p.next_decision = 0
            p.target = (x, y)
        s.ball = T.Ball(mode=T.BallMode.CONTROLLED, carrier='A0', control_time=0, last_touch='A', scoring=True)
        self.m.e.follow_carrier()
        self.m.auto_substitutions = lambda: None
        self.m.no_archery = True

    # ------------------------------------------------------------ sensing
    def active_ids(self):
        return sorted(p.id for p in self.m.s.players.values() if p.active and p.available)

    def sensor(self, pid):
        if pid not in self.sensors:
            from prism_archer_v0 import ArcherPrism
            p = self.m.s.players[pid]
            r = self.ratings[pid]
            pr = ArcherPrism(f'b1s30-{self.seed}-{pid}', r['awareness'], p.a.decision_speed, {'vel_mode': 'lsq'})
            pr.apply_ratings(r)
            self.sensors[pid] = pr
        return self.sensors[pid]

    def capture(self, now_ms):
        s = self.m.s
        b = s.ball
        bodies = [{'id': p.id, 'x': p.x, 'y': p.y, 'z': p.z, 'h': p.a.height, 'r': p.radius,
                   'vx': p.vx, 'vy': p.vy} for p in sorted(s.players.values(), key=lambda p: p.id) if p.active]
        for p in s.players.values():
            self.public[p.id] = (p.team, p.role)
        ball = {'id': BALL, 'x': b.x, 'y': b.y, 'z': max(0., b.z - .1), 'h': .22, 'r': .11, 'vx': b.vx, 'vy': b.vy}
        for pid in self.active_ids():
            a = s.players[pid]
            eye = (a.x, a.y, a.z + .72 * a.a.height)
            self.sensor(pid).tick(now_ms / 1000, eye, math.atan2(a.facing[1], a.facing[0]),
                                  [x for x in bodies if x['id'] != pid] + [ball], self.gaze.get(pid))

    def deliver(self, pid, now_ms):
        s, m = self.m.s, self.m
        pr = self.sensor(pid)
        pr.deliver(now_ms / 1000)
        t = now_ms / 1000
        tracks = []
        for eid in sorted(set(self.public) | {BALL}):
            if eid == pid:
                continue
            bel = pr.bget(eid)
            if bel is None:
                continue
            x, y = bel.at(t)
            vx, vy = bel.vel_at(t)
            team, role = ('ball', 'ball') if eid == BALL else self.public[eid]
            tracks.append(Track(eid, team, role, round(float(x), 3), round(float(y), 3),
                                round(float(vx), 3), round(float(vy), 3), int(bel.t * 1000)))
        tracks = tuple(tracks)
        bt = next((k for k in tracks if k.entity == BALL), None)
        if bt is not None and (pid not in self.last_ball or bt.captured_ms >= self.last_ball[pid][2]):
            self.last_ball[pid] = (bt.x, bt.y, bt.captured_ms)
        a = s.players[pid]
        r = s.restart
        taker = bool(r and (r.taker == pid or getattr(m, 'restart_taker', None) == pid))
        sig = Signals(s.phase.value, s.period, int(s.game_ms), int(s.possession_ms),
                      s.score[a.team], s.score[s.other(a.team)],
                      r.team if r else None, (round(r.x, 2), round(r.y, 2)) if r else None, taker)
        pend = self.pending.get(pid)
        q = s.quivers[a.team] if a.role == 'archer' else None
        oid = f's30/{now_ms:010d}/{pid}/obs'
        view = AthleteView(oid, pid, a.team, a.role, a.slot, now_ms, round(float(a.x), 3), round(float(a.y), 3),
                           s.ball.carrier == pid, int(s.attack_sign(a.team)), float(s.ends[a.team]),
                           tracks, sig, pend['cmd'].command_id if pend else None,
                           pend['cmd'].intent.kind if pend else None, pend.get('due') if pend else None,
                           q.loaded if q else None,
                           (q.last_release if q and q.last_release > 0 else None), a.posture)
        fb = tuple(self.feedback.get(pid, ()))
        self.feedback[pid] = []
        belief = BeliefState(oid + '/belief', oid, tracks, fb, int(round(pr.P['memory_s'] * 1000)),
                             self.last_ball.get(pid))
        return view, belief

    # ------------------------------------------------------------ ingress
    def submit(self, intent):
        s = self.m.s
        pid, kind = intent.athlete, intent.kind
        p = s.players.get(pid)
        if p is None or not p.active or intent.decided_ms != s.now:
            return {'status': 'rejected', 'reason': 'invalid_actor_or_time'}
        self.gaze[pid] = intent.gaze
        pend = self.pending.get(pid)
        if kind == 'continue_current':
            if pend and intent.related_command_id == pend['cmd'].command_id:
                return {'status': 'accepted', 'outcome': 'continuing', 'command_id': pend['cmd'].command_id}
            return {'status': 'rejected', 'reason': 'stale_pending_command'}
        if kind in PASSIVE:
            if p.role == 'keeper':
                self.save_mode[pid] = False
            return {'status': 'accepted', 'outcome': kind}
        if kind in LOCOMOTION:
            if intent.aim is None:
                return {'status': 'rejected', 'reason': 'no_aim'}
            cmd = MotorCommand(intent.intent_id + '/command', intent, s.now, None, 'locomotion')
            self.move[pid] = (float(intent.aim[0]), float(intent.aim[1]))
            self.save_mode[pid] = kind == 'keeper_save'
            return {'status': 'accepted', 'command': cmd}
        if kind in ('pass', 'shoot', 'restart_pass', 'draw_release'):
            if pend:
                return {'status': 'rejected', 'reason': 'resource_busy'}
            if kind in ('pass', 'shoot') and s.ball.carrier != pid:
                return {'status': 'rejected', 'reason': 'infeasible'}
            if kind != 'shoot' and (intent.target not in s.players or not s.players[intent.target].active):
                return {'status': 'rejected', 'reason': 'unknown_target'}
            cmd = MotorCommand(intent.intent_id + '/command', intent, s.now, None,
                               'bow' if kind == 'draw_release' else 'ball')
            self.pending[pid] = {'cmd': cmd, 'started': False, 'due': None}
            if kind == 'restart_pass':
                self.restart_choice[pid] = intent.target
            if kind in ('pass', 'shoot'):
                self.move[pid] = (float(p.x), float(p.y))
            return {'status': 'accepted', 'command': cmd}
        return {'status': 'rejected', 'reason': 'unknown_kind'}

    def _outcome(self, cmd, status, entity=None, feedback=True):
        s = self.m.s
        self.n_out += 1
        o = PhysicalOutcome(f's30/{s.now:010d}/physics/{self.n_out:08d}/outcome',
                            cmd.command_id if cmd else None, status, s.now, entity)
        self.outcomes.append(o)
        if feedback and cmd is not None:
            oid, st, ms = receive_outcome(o)
            self.feedback.setdefault(cmd.intent.athlete, []).append((oid, st + ':' + cmd.intent.kind, ms))
        return o

    def _resolve(self, pid, status):
        pend = self.pending.pop(pid, None)
        if pend:
            self._outcome(pend['cmd'], status)
        return pend

    # ------------------------------------------------------------ motor hooks
    def _targets(self, team=None):
        s = self.m.s
        return {pid: xy for pid, xy in sorted(self.move.items())
                if s.players[pid].active and s.players[pid].role != 'archer'
                and (team is None or s.players[pid].team == team)}

    def _ready(self, taker):
        """PROVISIONAL: the restart is declared ready once the taker has chosen."""
        r = self.m.s.restart
        if taker in self.restart_choice or (r and self.m.s.now - r.created_at > 3000):
            return self._orig_ready(taker)

    def _restart_receiver(self, s, p):
        q = s.players.get(self.restart_choice.get(p.id))
        return q if q is not None and self.m.e.eligible(q) else None

    def _ball_motor(self):
        """Replaces Match.carrier_decision: executes B1 ball commands only."""
        self.hook_calls['ball_motor'] += 1
        m = self.m
        s, b = m.s, m.s.ball
        for pid in list(m.pending_ball_actions):
            if pid != b.carrier or (m.c3 and m.c3_prep.get(pid, -1) < b.control_time):
                m.pending_ball_actions.pop(pid)
                self._resolve(pid, 'interrupted')
        for pid, pend in list(self.pending.items()):
            k = pend['cmd'].intent.kind
            if k in ('pass', 'shoot') and pid != b.carrier:
                self._resolve(pid, 'interrupted')
        if not b.carrier:
            return
        p = s.players[b.carrier]
        pend = self.pending.get(p.id)
        if pend is None or pend['cmd'].intent.kind not in ('pass', 'shoot'):
            return
        if not m.e.eligible(p) or s.now < p.next_action:
            return
        intent = pend['cmd'].intent
        if p.id in m.pending_ball_actions:
            due = m.pending_ball_actions[p.id][0]
            if s.now < due:
                return
            m.pending_ball_actions.pop(p.id)
            if intent.kind == 'shoot':
                gx = s.attack_goal(p.team)
                skill = (p.a.kicking + p.a.ball_handling) / 2
                target = (gx + s.attack_sign(p.team) * .3, float(intent.aim[1]), 2.8 + .3 * skill)
                rho, factor, extra = m.c3_release_state(p, 'shot')
                vel = m.c3_perturb(m.ball_velocity((b.x, b.y, b.z), target, skill, 'shot', factor), extra)
                ok = m.e.release(p.id, vel, 'shot')
                if ok:
                    m.stats['shot_attempts'] += 1
                    p.next_action = s.now + 500
            else:
                q = s.players[intent.target]
                ok = False
                if m.e.eligible(q):
                    m.make_pass(p, q, 'pass', True)
                    ok = s.ball.carrier != p.id
            self._resolve(p.id, 'released' if ok else 'release_failed')
            if ok:
                self.flight = {'command': pend['cmd'], 'kind': intent.kind, 'passer': p.id,
                               'target': intent.target, 'team': p.team, 'score': dict(s.score)}
            return
        if not pend['started']:
            if s.phase not in (self.types.Phase.LIVE, self.types.Phase.PENALTY):
                return
            if intent.kind == 'shoot':
                m.make_shot(p)
            else:
                m.make_pass(p, s.players[intent.target], 'pass')
            if p.id in m.pending_ball_actions:
                pend['started'], pend['due'] = True, m.pending_ball_actions[p.id][0]
            else:
                self._resolve(p.id, 'rejected_not_prepared')
        else:
            self._resolve(p.id, 'interrupted')

    def _archer_motor(self):
        """Replaces Match.arrow_decisions: executes B1 draw_release commands."""
        self.hook_calls['archer_motor'] += 1
        m = self.m
        s = m.s
        for pid, pend in sorted(self.pending.items()):
            intent = pend['cmd'].intent
            if intent.kind != 'draw_release':
                continue
            p = s.players[pid]
            if m.no_archery or not m.e.live() or s.owner is None or not p.eligible(s.now) or not p.active:
                m.pending_draw.pop(p.team, None)
                self._resolve(pid, 'interrupted')
                continue
            q = s.quivers[p.team]
            if q.loaded == 0 or q.spent >= q.allocation:
                self._resolve(pid, 'rejected_no_arrow')
                continue
            if not pend['started']:
                due = s.now + int(math.ceil(m.assume['bow_draw_ms'] * (1.4 - .5 * p.a.archery_accuracy) / m.dt) * m.dt)
                pend['started'], pend['due'] = True, due
                m.pending_draw[p.team] = (due, intent.target)
                m.e.emit('arrow_draw', 'assumption:draw_time', player=p.id, target=intent.target, ready=due)
                continue
            if s.now < pend['due']:
                continue
            m.pending_draw.pop(p.team, None)
            origin = (p.x, p.y, .72 * p.a.height)
            age = (s.now - intent.decided_ms) / 1000
            bx, by = intent.aim[0] + intent.aim_vel[0] * age, intent.aim[1] + intent.aim_vel[1] * age
            speed = min(m.cfg.get('pocket', {}).get('arrow_limit', 30), p.a.archery_release_speed)
            target, ans = (bx, by, 1.4), None
            for _ in range(3):
                ans = self.geom.ballistic(origin, target, speed, m.assume['gravity'], False)
                if ans is None:
                    break
                tt = ans[1]
                target = (bx + intent.aim_vel[0] * tt, by + intent.aim_vel[1] * tt, 1.4)
            if ans is None:
                self._resolve(pid, 'rejected_out_of_range')
                continue
            sigma = (.0008 + .009 * (1 - p.a.archery_accuracy)) * m.assume['arrow_error_scale']
            yaw, pitch = m.rng['arrow'].gauss(0, sigma), m.rng['arrow'].gauss(0, sigma)
            vx, vy, vz = ans[0]
            az, el = math.atan2(vy, vx) + yaw, math.atan2(vz, math.hypot(vx, vy)) + pitch
            vel = (speed * math.cos(el) * math.cos(az), speed * math.cos(el) * math.sin(az), speed * math.sin(el))
            ar = m.e.shoot_arrow(p.id, intent.target, vel, origin)
            m.last_arrow_decision[p.team] = s.now
            self._resolve(pid, 'arrow_released' if ar else 'rejected_by_engine')

    def _keeper_motor(self, targets):
        """Replaces Match.c4c_keepers. PROVISIONAL: the B0 C4c save planner runs
        for a Keeper only while that Keeper holds a B1 keeper_save intent."""
        self.hook_calls['keeper_motor'] += 1
        m = self.m
        s, b = m.s, m.s.ball
        keepers = [p for p in s.players.values() if p.active and p.role == 'keeper']
        masked = []
        for p in keepers:
            if not self.save_mode.get(p.id) and getattr(p, 'c4c_launch', None) is None:
                p.c4c_seen = (b.version, s.now, float('inf'), False)
                p.c4c_plan = None
                masked.append(p)
        self._orig_keepers(m, targets)
        for p in masked:
            p.c4c_seen = None
        for p in keepers:
            plan = getattr(p, 'c4c_plan', None)
            saving = self.save_mode.get(p.id) and plan is not None and plan.get('kind') != 'no_threat'
            if saving:
                if not p.__dict__.get('_s30_plan') is plan:
                    p._s30_plan = plan
                    self._outcome(None, 'keeper_save_plan:' + str(plan.get('kind')), p.id, feedback=False)
                continue
            if p.id in self.move and b.carrier != p.id and getattr(p, 'c4c_launch', None) is None:
                targets[p.id] = self.move[p.id]
                p.next_decision = min(p.next_decision, s.now)

    # ------------------------------------------------------------ world outcomes
    def collect(self):
        m = self.m
        s = m.s
        log = m.e.log
        for rec in log[self.log_seen:]:
            ev = rec['event']
            if ev == 'restart_release':
                taker = rec['data'].get('player') or rec['data'].get('taker')
                for pid in [k for k, v in self.pending.items() if v['cmd'].intent.kind == 'restart_pass']:
                    self._resolve(pid, 'released' if pid == taker or taker is None else 'interrupted')
                self.restart_choice.clear()
            f = self.flight
            if f is None:
                continue
            c = rec['carrier']
            if rec['score'] != f['score']:
                scored = [t for t in rec['score'] if rec['score'][t] != f['score'][t]]
                self._outcome(f['command'], ('goal_for:' if f['team'] in scored else 'goal_against:') + f['kind'],
                              None, feedback=False)
                self.flight = None
            elif c is not None and c != f['passer']:
                team = s.players[c].team
                if f['kind'] == 'pass':
                    st = ('pass_completed' if c == f['target'] else 'pass_completed_other') if team == f['team'] else 'pass_intercepted'
                else:
                    st = 'shot_saved' if s.players[c].role == 'keeper' and team != f['team'] else 'shot_recovered'
                self._outcome(f['command'], st, c, feedback=False)
                self.flight = None
            elif ev in ('boundary', 'restart_awarded', 'period_end'):
                self._outcome(f['command'], f['kind'] + '_dead:' + ev, None, feedback=False)
                self.flight = None
        self.log_seen = len(log)
        # a restart choice is void once play is live again
        if s.phase == self.types.Phase.LIVE and self.restart_choice:
            for pid in [k for k, v in self.pending.items() if v['cmd'].intent.kind == 'restart_pass']:
                self._resolve(pid, 'interrupted')
            self.restart_choice.clear()
        for pid in [k for k in self.pending if not s.players[k].active]:
            self._resolve(pid, 'interrupted')


def run_match(seed=1, scenario=None, max_ms=None, telemetry=True, sample=12, on_view=None):
    """Stepped N-athlete loop. Returns a compact, hashable result."""
    port = MatchPort(seed, scenario)
    m = port.m
    s = m.s
    FINAL = port.types.Phase.FINAL
    start = s.now
    limit = max_ms if max_ms is not None else 16000000
    next_sense, next_dec = s.now, {}
    h = hashlib.sha256()
    counts, by_role, by_kind, admissions = Counter(), Counter(), Counter(), Counter()
    samples, chains, n_dec = [], [], 0
    terminal = None
    while s.phase != FINAL and s.now < limit:
        now = s.now
        if now >= next_sense:
            port.capture(now)
            next_sense = now + 100
        for pid in port.active_ids():
            if pid not in next_dec:
                pr = port.sensor(pid)
                next_dec[pid] = now + int(round(pr.latency_s * 1000))
                continue
            if now < next_dec[pid]:
                continue
            view, belief = port.deliver(pid, now)
            if on_view:
                on_view(port, view, belief)
            intent, rec = decide(view, belief)
            adm = port.submit(intent)
            status = adm['status'] + (':' + adm['reason'] if 'reason' in adm else '')
            if adm['status'] == 'rejected':
                port.feedback.setdefault(pid, []).append(
                    (intent.intent_id + '/outcome/rejected', 'rejected_' + adm['reason'] + ':' + intent.kind, now))
            cmd = adm.get('command')
            row = [rec['decision_id'], intent.kind, intent.target, intent.aim, status,
                   cmd.command_id if cmd else adm.get('command_id')]
            h.update(digest(row).encode())
            n_dec += 1
            counts[pid] += 1
            by_role[view.role] += 1
            by_kind[intent.kind] += 1
            admissions[status] += 1
            if telemetry:
                full = {'view': asdict(view), 'belief': asdict(belief), 'decision': rec,
                        'intent': asdict(intent), 'admission': status,
                        'command': asdict(cmd) if cmd else None}
                if len(samples) < sample or (n_dec % 397 == 0 and len(samples) < sample + 50):
                    samples.append(full)
                if cmd is not None and cmd.resource != 'locomotion' and len(chains) < 260:
                    chains.append({'decision_id': rec['decision_id'], 'observation_id': rec['observation_id'],
                                   'belief_revision': rec['belief_revision'], 'intent_id': intent.intent_id,
                                   'command_id': cmd.command_id, 'kind': intent.kind, 'target': intent.target,
                                   'aim': intent.aim, 'selected': rec['selected'], 'options': rec['options']})
            prof = port.sensor(pid).prof
            next_dec[pid] = now + max(100, int(round(prof['decision_interval_s'] * 1000)))
        m.step()
        port.collect()
        if scenario in ('g1', 'g1_close'):
            done = [o.status for o in port.outcomes if o.status.startswith(('pass_', 'shot_', 'goal_'))]
            b = s.ball
            if done:
                terminal = done[0]
            elif b.carrier and s.players[b.carrier].team == 'B':
                terminal = 'carrier_dispossessed'
            elif b.carrier == 'A0' and s.players['A0'].x >= 90:
                terminal = 'carrier_reaches_x_90'
            elif s.phase != port.types.Phase.LIVE:
                terminal = 'dead_ball:' + s.phase.value
            if terminal:
                break
    port.collect()
    outs = [asdict(o) for o in port.outcomes]
    h.update(digest(outs).encode())
    state = {'now': s.now, 'phase': s.phase.value, 'score': dict(s.score), 'period': s.period,
             'ball': [round(s.ball.x, 6), round(s.ball.y, 6), round(s.ball.z, 6)],
             'players': {p.id: [round(p.x, 6), round(p.y, 6)] for p in sorted(s.players.values(), key=lambda p: p.id) if p.active}}
    events = Counter(r['event'] for r in m.e.log)
    out_kinds = Counter(o.status for o in port.outcomes)
    cmd_ids = {c['command_id'] for c in chains}
    result = {
        'seed': seed, 'scenario': scenario or 'regulation_match_B0_P4_DEFAULT',
        'status': ('final' if s.phase == FINAL else 'scenario_terminal' if terminal else 'time_limit'),
        'terminal': terminal, 'ruleset': port.ruleset, 'settings': port.settings,
        'start_ms': start, 'end_ms': s.now, 'score': dict(s.score), 'period': s.period,
        'result': str(getattr(s, 'result', None)),
        'decisions_total': n_dec, 'decisions_by_athlete': dict(sorted(counts.items())),
        'decisions_by_role': dict(sorted(by_role.items())), 'decisions_by_kind': dict(sorted(by_kind.items())),
        'admissions': dict(sorted(admissions.items())), 'outcomes_by_status': dict(sorted(out_kinds.items())),
        'engine_events': dict(sorted(events.items())), 'hook_calls': dict(port.hook_calls),
        'trace_hash': h.hexdigest(), 'state_hash': digest(state),
        'final_state': state,
    }
    if telemetry:
        result['trace'] = {'sampled_decisions': samples, 'action_chains': chains,
                           'outcomes': [o for o in outs if o['command_id'] in cmd_ids or o['command_id'] is None][:600]}
    return result, port
