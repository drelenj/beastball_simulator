"""Read-only release, admission and carry witnesses for the diagnosis."""
from collections import defaultdict
from dataclasses import replace
from math import atan2, cos, degrees, hypot, pi, sin
from types import SimpleNamespace

from native import cognition_rb3 as rb
from native.individuation import visual_half_angle
from native.prism_registry import radar_radius


def release_geometry(view, aim, origin, speed, velocity, opponents, now):
    if aim is None or speed <= 0:
        return {}
    sx, sy, _ = origin
    dx, dy = aim[0] - sx, aim[1] - sy
    distance = hypot(dx, dy)
    intended_angle = atan2(dy, dx)
    actual_angle = atan2(velocity[1], velocity[0])
    yaw = (actual_angle - intended_angle + pi) % (2*pi) - pi
    true_reaches = tuple((p.entity, p.reach - rb.ACQ_RADIUS_M - rb.ACQ_EXTRA_M) for p in opponents)
    if view is None:
        return dict(distance=distance, yaw_deg=degrees(yaw))
    actual_view = replace(view, x=sx, y=sy, body_reach=true_reaches,
                          paired_fixes=tuple(s for s in view.paired_fixes if s!='projected_beliefs'))
    believed = [t for t in view.tracks if t.team not in (view.team, 'ball') and t.role in ('field', 'keeper')
                and t.entity not in view.signals.immune]
    t_release = max(0., (now - view.delivered_ms)/1000)
    # Recent delivered tracks may already be extrapolated by CORE. Treat their
    # positions as the last actionable belief, with a release-time delay.
    target = SimpleNamespace(x=aim[0], y=aim[1])
    actual = SimpleNamespace(x=sx + distance*cos(actual_angle), y=sy + distance*sin(actual_angle))
    return dict(distance=distance, yaw_deg=degrees(yaw),
                believed_margin=rb.lane_margin(view, target, believed, speed, t_release),
                true_margin=rb.lane_margin(actual_view, target, opponents, speed, 0.),
                thrown_margin=rb.lane_margin(actual_view, actual, opponents, speed, 0.),
                believed_pressure=rb.is_pressured(view, [t for t in believed if t.role=='field']),
                true_pressure=any(rb.time_to_contact(actual_view,t) < rb.PRESSURE_T_S
                                  for t in opponents if t.role=='field'))


class Witness:
    def __init__(self, port, rosters):
        self.port = port
        self.views = {}
        self.delivered = defaultdict(set)
        self.release = {}
        self.freeze_targets = {}
        self.committing_grip = {}
        self.commit_target = {}
        self.carries = []
        self.active_carry = None
        self.admissions = defaultdict(list)
        self.skills = {f'{team}:{p.source_id}': dict(p.values) for team, roster in rosters.items()
                       for p in roster.athletes}
        engine, state = port.m.e, port.m.s
        old_view, old_submit = port.view, port.submit
        old_release, old_restart = engine.release, engine.restart_release
        old_carry, old_follow = engine.rb_carry_attempt, engine.follow_carrier
        old_freeze, old_emit = engine.freeze, engine.emit

        def view(pid, now, *args, **kwargs):
            v, belief = old_view(pid, now, *args, **kwargs)
            if v is not None and v.role != 'archer':
                self.views[pid] = v
                self.delivered[pid].update(t.entity for t in v.tracks)
                frame = next((f for f in reversed(port.frames.get(pid, ()))
                              if f.captured_ms <= now-port.config.latency_ms), None)
                if frame is not None:
                    self.delivered[pid].update(t.entity for t in frame.tracks)
            return v, belief

        def submit(intent):
            outcome = old_submit(intent)
            if outcome['status'] == 'accepted' and intent.athlete in state.players:
                self.admissions[intent.athlete].append(intent)
                if intent.contact == 'takedown':
                    actor = state.players[intent.athlete]
                    target = state.players.get(intent.target)
                    if target:
                        self.commit_target[intent.intent_id] = (state.ball.carrier == target.id,
                                                                hypot(actor.x-target.x,actor.y-target.y))
                    hold = port.m.c3_holds.get((intent.athlete,intent.target))
                    if hold:
                        self.committing_grip[intent.intent_id] = hold['g']
            return outcome

        def releasing(method, pid, velocity, kind, args, kwargs):
            prior = len(engine.log)
            p = state.players[pid]
            rivals = (q for q in state.players.values() if q.team != p.team and q.role != 'archer' and q.active)
            opponents = tuple((q.id,q.role,q.x,q.y,q.vx,q.vy,q.a.reach+q.radius+.2,q.eligible(state.now)) for q in rivals)
            facing = p.facing
            body_xy = p.x,p.y
            view = self.views.get(pid)
            command = port.pending.get(pid, {}).get('cmd')
            keeper = next((q for q in opponents if q[1]=='keeper'), None)
            result = method(pid, velocity, *args, **kwargs)
            if result and kind != 'loose':
                event = 'restart_release' if kind == 'restart' else 'release'
                for row in engine.log[prior:]:
                    if row['event'] == event:
                        aim = command.intent.aim if command else None
                        release_snapshot = (tuple(row['ball']), facing, view, opponents, keeper, body_xy)
                        self.release[row['id']] = (release_snapshot, aim,
                            frozenset(self.delivered[pid]) if kind != 'shot' else (), state.attack_goal(p.team))
                        break
            return result

        def release(pid, velocity, kind='pass', *args, **kwargs):
            return releasing(old_release, pid, velocity, kind, (kind,*args), kwargs)

        def restart(pid, velocity, *args, **kwargs):
            return releasing(old_restart, pid, velocity, 'restart', args, kwargs)

        def carry(holder, *args, **kwargs):
            previous = self.active_carry
            result = old_carry(holder, *args, **kwargs)
            if result:
                if previous:
                    previous['closing_id'] = len(engine.log)
                goal = state.attack_goal(holder.team)
                distance = hypot(goal-holder.x, holder.y-50.)
                self.active_carry = dict(player=holder.id, team=holder.team, start_ms=state.now,
                    after_id=len(engine.log), start_distance=distance, plane=abs(goal-holder.x),
                    ball_plane=abs(goal-state.ball.x), goal_x=goal)
                self.carries.append(self.active_carry)
            return result

        def follow():
            result = old_follow()
            c = self.active_carry
            if c and state.ball.carrier == c['player']:
                holder = state.players[c['player']]
                c['plane'] = min(c['plane'], abs(c['goal_x']-holder.x))
                c['ball_plane'] = min(c['ball_plane'], abs(c['goal_x']-state.ball.x))
            return result

        def emit(event, rule, **data):
            was = len(engine.log)
            result = old_emit(event, rule, **data)
            c = self.active_carry
            if c and len(engine.log) > was:
                player = c['player']
                if (event in ('goal','boundary','period_end','restart_awarded')
                    or event in ('release','freeze') and data.get('player') == player
                    or event in ('tackle_count','strip') and data.get('target') == player
                    or event == 'control' and data.get('player') != player):
                    c['closing_id'] = was+1
                    self.active_carry = None
            return result

        def freeze(pid, *args, **kwargs):
            prior = len(engine.log)
            ball = state.ball
            command = port.pending.get(ball.carrier, {}).get('cmd')
            marked_receiver = (command.intent.target if command and command.intent.kind == 'pass'
                               else ball.intended if ball.mode == port.types.BallMode.PASS else None)
            result = old_freeze(pid, *args, **kwargs)
            if result:
                for row in engine.log[prior:]:
                    if row['event'] == 'freeze':
                        self.freeze_targets[row['id']] = marked_receiver
                        break
            return result

        port.view, port.submit = view, submit
        engine.freeze, engine.emit = freeze, emit
        engine.release, engine.restart_release = release, restart
        engine.rb_carry_attempt, engine.follow_carrier = carry, follow

    def interception(self, flight, player):
        row = dict(t_ms=flight['t_ms'], release_id=flight['id'], player=player, origin=flight['data'].get('player', flight['data'].get('taker')),
                   restart=flight['event']=='restart_release')
        if flight['id'] not in self.release:
            return row
        (origin,facing,view,rivals,_,body_xy), aim, ever, _ = self.release[flight['id']]
        velocity = flight['data']['velocity']
        if aim is None:
            target = next((t for t in (view.tracks if view else ()) if t.entity == flight['data'].get('target')), None)
            aim = (target.x,target.y) if target else None
        opponents = [SimpleNamespace(entity=pid,role=role,x=x,y=y,vx=vx,vy=vy,reach=reach)
                     for pid,role,x,y,vx,vy,reach,eligible in rivals if eligible]
        speed = hypot(*velocity[:2])
        row.update(release_geometry(view, aim, origin, speed, velocity, opponents, flight['t_ms']))
        candidate = next((p for p in rivals if p[0]==player), None)
        row.update(perceived=any(t.entity==player for t in view.tracks) if view else None,
                   ever_perceived=player in ever, passing=self.skills[row['origin']].get('passing'),
                   playmaking=self.skills[row['origin']].get('playmaking'), vision=self.skills[row['origin']].get('vision'))
        if candidate:
            dx,dy=candidate[2]-body_xy[0],candidate[3]-body_xy[1]
            angle=(atan2(dy,dx)-atan2(facing[1],facing[0])+pi)%(2*pi)-pi
            row.update(in_cone=abs(angle)<=visual_half_angle(row['vision']),
                       in_radar=hypot(dx,dy)<=radar_radius(self.skills[row['origin']]['awareness']))
        return row
