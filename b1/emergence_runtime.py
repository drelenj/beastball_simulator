"""Opt-in Motor Control adapter for Emergence-1 ownership seams.

The accepted M1 runtime and historical engine are not modified. An experiment
worker installs this overlay on one Match instance and supplies callbacks that
return already-delivered beliefs. Missing beliefs never fall back to truth.
"""
import math
import types

from .emergence_intents import (
    ArcherView, AthleteBody, KeeperView, RestartAthleteView,
    RestartDecisionRecord, admit_restart_claims, decide_archer_movement,
    decide_keeper, decide_restart_claim, decide_restart_position,
    plan_keeper_motor,
)


def body_of(p):
    return AthleteBody(
        p.id, p.team, float(p.x), float(p.y), float(p.z),
        float(p.vx), float(p.vy), float(p.vz), float(p.a.height),
        float(p.a.reach), float(p.a.acceleration), float(p.a.braking),
        float(p.a.maximum_speed), float(p.a.jump_height))


class EmergenceOwnershipOverlay:
    """Instance-local hooks; callbacks return already-delivered beliefs."""

    def __init__(self, match, *, keeper_belief, archer_ball_belief,
                 restart_record=None):
        self.match = match
        self.keeper_belief = keeper_belief
        self.archer_ball_belief = archer_ball_belief
        self.restart_record = restart_record or self._record_from_engine
        self.trace = []
        self._installed = False

    def install(self):
        if self._installed:
            raise RuntimeError('emergence ownership overlay already installed')
        m = self.match
        self._legacy = {
            'c4c_keepers':m.c4c_keepers,
            'targets_dead':m.targets_dead,
            'update_archers':m.update_archers,
            'c3_withhold':m.c3_withhold,
        }
        overlay = self
        m.c4c_keepers = types.MethodType(
            lambda match, targets: overlay._keeper_controls(targets), m)
        m.targets_dead = types.MethodType(
            lambda match: overlay._restart_controls(), m)
        m.update_archers = types.MethodType(
            lambda match, ms: overlay._archer_controls(ms), m)
        # Authoritative C3 stall/restraint/tuck timing remains. This removes
        # only the controller's refusal to begin a commanded wind-up.
        m.c3_withhold = types.MethodType(
            lambda match, athlete, kind: False, m)
        self._installed = True
        return self

    def uninstall(self):
        if not self._installed:
            return
        for name, value in self._legacy.items():
            setattr(self.match, name, value)
        self._installed = False

    def _emit(self, kind, **data):
        record = {'kind':kind, **data}
        self.trace.append(record)
        emitter = getattr(getattr(self.match, 'e', None), 'emit', None)
        if emitter is not None:
            emitter('athlete_intent', 'B1-E1', intent_kind=kind, **data)

    def _keeper_controls(self, targets):
        m, s = self.match, self.match.s
        for p in s.players.values():
            if not p.active or p.role != 'keeper':
                continue
            launch = getattr(p, 'c4c_launch', None)
            if launch is not None:
                if p.posture == 'airborne' and s.now < launch['t_land']-.5:
                    continue
                m.c4c_land(p, launch)
            if (not p.eligible(s.now) or p.posture == 'grounded' or
                    s.ball.carrier == p.id):
                continue
            admitted = getattr(p, 'c4c_plan', None)
            if (admitted is not None and admitted.get('kind') == 'approach' and
                    s.now < admitted['launch_at']):
                targets[p.id] = admitted['target']
                p.target = admitted['target']
                p.next_decision = admitted['launch_at']
                continue
            if (admitted is not None and admitted.get('kind') == 'step' and
                    s.now < admitted['until']):
                targets[p.id] = admitted['target']
                p.target = admitted['target']
                p.next_decision = admitted['until']
                continue
            # An approach is revocable only at its declared re-read instant.
            # A completed step may also be replaced by a newly delivered read.
            p.c4c_plan = None
            belief = self.keeper_belief(p.id, s.now)
            position = None
            if belief is not None:
                gx = s.ends[p.team]
                inward = 1. if gx == 0 else -1.
                distance = abs(belief.x-gx)
                depth = max(m.assume['keeper_depth_min_m'],
                            min(m.assume['keeper_depth_max_m'],
                                distance*m.assume['keeper_depth_frac']))
                norm = math.hypot(belief.x-gx, belief.y-50.) or 1.
                position = (gx+inward*depth,
                            50.+(belief.y-50.)*depth/norm)
            view = KeeperView(
                f'e1/{s.now}/{p.id}/keeper-view', s.now, body_of(p),
                float(s.ends[p.team]), position_belief=position)
            intent = decide_keeper(
                view, belief, gravity=m.assume['gravity'],
                drag=m.assume['ball_drag'],
                restitution=m.assume['ball_restitution'])
            command = plan_keeper_motor(
                intent, view.body, now_ms=s.now,
                gravity=m.assume['gravity'],
                pushoff_fraction=m.assume['keeper_pushoff_frac'],
                extension_fraction=m.assume['keeper_extension_frac'],
                launch_min_s=m.assume['keeper_launch_min_s'],
                dive_time_s=m.assume['keeper_dive_time_s'],
                attempt_margin_m=m.assume['keeper_attempt_margin_m'])
            self._emit('keeper', athlete=p.id, intent=intent.kind,
                       belief_revision=intent.belief_revision,
                       command=command.kind, status=command.status)
            if intent.kind == 'save' and command.status == 'accepted':
                # Engine course identity is execution provenance stamped only
                # after the belief-derived save is admitted. Cognition never
                # receives the version.
                p.c4c_seen = (s.ball.version, belief.captured_ms, s.now, False)
            else:
                # No semantic save means no deliberate-save privilege in the
                # catch/contact kernel. Passive body/reflex contacts remain.
                p.c4c_seen = None
            if command.kind in ('hold', 'move', 'step', 'approach'):
                targets[p.id] = command.target
                p.target = command.target
                p.next_decision = command.until_ms or s.now
                if command.kind in ('step', 'approach'):
                    p.c4c_plan = {
                        'kind':command.kind, 'target':command.target,
                        **({'until':command.until_ms} if command.kind == 'step'
                           else {'launch_at':command.until_ms})}
                continue
            if command.kind != 'launch':
                targets[p.id] = (p.x, p.y)
                continue
            vx, vy, vz = command.impulse
            p.vx += vx
            p.vy += vy
            p.vz = vz
            p.posture = 'airborne'
            dive = command.lean >= m.assume['keeper_dive_lean']
            p.c4c_launch = {
                't0':s.now, 't_land':command.land_ms,
                'off':m.c4c_off(p, command.lean, *command.direction),
                'lean':command.lean, 'dir':command.direction, 'dive':dive}

    def _record_from_engine(self, match):
        s, r = match.s, match.s.restart
        if r is None:
            return None
        rs = getattr(r, 'rs', None) or {}
        preferred = rs.get('snapper')
        spot = r.taker_spot or (r.x, r.y)
        created = int(r.created_at)
        # The accepted scrimmage record uses 3.5 s, not the snap40 3.0 s
        # minimum. Other restart kinds have an immediately open claim window.
        fallback = created+(3500 if rs.get('kind') == 'scrim' else 3000)
        return RestartDecisionRecord(
            f'restart/{created}/{r.kind}/{r.team}',
            rs.get('kind', r.kind), r.team, (float(r.x), float(r.y)),
            (float(spot[0]), float(spot[1])), float(r.clearance),
            created, created, fallback, preferred)

    def _restart_controls(self):
        m, s = self.match, self.match.s
        if s.restart is None:
            return {}
        record = self.restart_record(m)
        if record is None:
            return {}
        views = []
        for p in sorted(s.players.values(), key=lambda player:player.id):
            if not p.active or p.role == 'archer':
                continue
            zone_exit = None
            zn = m.e.zone(p.x, p.y)
            if (zn is not None and
                    (p.zone_ms[zn] > 3000 or p.unmarked_ms[zn] > 3000) and
                    not (p.role == 'keeper' and zn == s.own_zone(p.team))):
                gx = 0. if zn == 0 else 100.
                dx, dy = p.x-gx, p.y-50.
                size = math.hypot(dx, dy) or 1.
                zone_exit = (
                    max(1., min(99., gx+dx/size*(s.keeper_zone_radius+2.))),
                    max(1., min(99., 50.+dy/size*(s.keeper_zone_radius+2.))))
            views.append(RestartAthleteView(
                f'e1/{s.now}/{p.id}/restart-view', s.now, p.id, p.team,
                float(p.x), float(p.y), bool(p.eligible(s.now)),
                p.posture, p.role, zone_exit))
        claims = [decide_restart_claim(v, record) for v in views]
        admitted = admit_restart_claims(claims)
        taker = admitted.athlete if admitted is not None else None
        s.restart.taker = taker
        m.restart_taker = None if s.restart.kind == 'recovery' else taker
        targets = {}
        for view in views:
            intent = decide_restart_position(view, record, taker)
            targets[view.athlete] = intent.target
            self._emit('restart_position', athlete=view.athlete,
                       record_id=record.record_id, taker=taker,
                       target=list(intent.target), reason=intent.reason)
        if admitted is not None:
            self._emit('restart_claim', athlete=taker,
                       record_id=record.record_id, reason=admitted.reason)
        return targets

    def _archer_controls(self, ms):
        m, s = self.match, self.match.s
        dt = ms/1000.
        for p in s.players.values():
            if not p.active or p.role != 'archer' or not p.eligible(s.now):
                continue
            low = s.ends[p.team] == 0
            minx, maxx = ((.7, 49.3) if low else (50.7, 99.3))
            q = s.quivers[p.team]
            view = ArcherView(
                f'e1/{s.now}/{p.id}/archer-view', s.now, body_of(p),
                minx, maxx, -5.1 if low else 105.1, q.loaded,
                q.allocation-q.spent, q.reload_until >= 0)
            belief = self.archer_ball_belief(p.id, s.now)
            intent = decide_archer_movement(view, belief)
            tx, ty = intent.target
            dx, dy = tx-p.x, ty-p.y
            distance = math.hypot(dx, dy)
            ux, uy = ((dx/distance, dy/distance) if distance else (0., 0.))
            desired = (min(8., p.a.maximum_speed*.4,
                           math.sqrt(max(0., 2.*p.a.braking*distance)))
                       if intent.kind == 'move' else 0.)
            ax, ay = ux*desired-p.vx, uy*desired-p.vy
            change = math.hypot(ax, ay)
            limit = ((p.a.acceleration if desired > p.speed else p.a.braking)*dt)
            if change:
                scale = min(1., limit/change)
                p.vx += ax*scale
                p.vy += ay*scale
            p.x = max(minx, min(maxx, p.x+p.vx*dt))
            if low:
                p.y = max(-9.3, min(-3.1, p.y+p.vy*dt))
            else:
                p.y = max(103.1, min(109.3, p.y+p.vy*dt))
            if intent.reload:
                m.e.reload(p.id)
            self._emit('archer_movement', athlete=p.id,
                       belief_revision=intent.belief_revision,
                       intent=intent.kind, target=list(intent.target),
                       reload=intent.reload)
