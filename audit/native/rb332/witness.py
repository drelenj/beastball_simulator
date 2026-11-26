"""Privileged, read-only diagnosis. Forecasts still receive only saved athlete views."""
from dataclasses import replace
from math import atan2, degrees, hypot, pi

from audit.native.rb331.witness import Witness
from b1.emergence_intents import KeeperIntent, plan_keeper_motor
from native import paired_policy as policy, cognition_rb3 as rb
from native.port import body
from native.geometry import body_out
from native.prism_motion import reflex_gain
from native.rulebook.ball_material import params, path


def keeper_envelope(origin, velocity, gx, model, radius, runner, delay, assumptions):
    course = path((*origin,*velocity), model, radius, 4., .010)
    for index,(a,b) in enumerate(zip(course,course[1:]),1):
        if (a[1]-gx)*(b[1]-gx)>0 or a[1]==b[1]:
            continue
        f = (gx-a[1])/(b[1]-a[1])
        crossing = tuple(x+f*(y-x) for x,y in zip(a,b))
        t,_,y,z = crossing
        if hypot(y-50,z)+radius > assumptions['goal_radius']:
            return None
        answer = dict(flight_s=t,y=y,z=z,needed_m=hypot(gx-runner.x,y-runner.y),
                      lateral_m=abs(y-runner.y),reachable=False)
        if t <= delay:
            return answer
        moves = tuple((time-delay,x,y,z) for time,x,y,z in (*course[:index],crossing) if time>delay)
        start = replace(runner,x=runner.x+runner.vx*delay,y=runner.y+runner.vy*delay)
        intent = KeeperIntent('reach-audit',runner.athlete,'save',0,None,target=(gx,y),course=((0.,*origin),*moves))
        command = plan_keeper_motor(intent,start,now_ms=0,attempt_margin_m=0.,match_lean=True,
            reach_factor=assumptions['reach_factor'],gravity=assumptions['gravity'],pushoff_fraction=assumptions['keeper_pushoff_frac'],
            extension_fraction=assumptions['keeper_extension_frac'],launch_min_s=assumptions['keeper_launch_min_s'],
            dive_time_s=assumptions['keeper_dive_time_s'],dive_hand_fraction=assumptions['keeper_dive_hand_frac'])
        answer.update(reachable=command.kind in ('step','launch','approach'),ideal_action=command.kind)
        return answer
    return None


class TrialWitness(Witness):
    def __init__(self, port, rosters, details):
        super().__init__(port,rosters)
        self.motion = {}
        self.admitted_view = {}
        self.keeper = {}
        self.boundary_states = {}
        self.details = details
        engine = port.m.e
        state = port.m.s
        release, boundary, submit = engine.release, engine.boundary, port.submit

        def observed_submit(intent):
            result = submit(intent)
            if details and intent.kind == 'pass' and result['status']=='accepted':
                self.admitted_view[intent.intent_id] = self.views.get(intent.athlete)
            return result

        def observed_release(pid, velocity, kind='pass', *args, **kwargs):
            before = len(engine.log)
            command = port.pending.get(pid,{}).get('cmd')
            keeper = None
            if details and kind=='shot':
                team = state.players[pid].team
                p = next((q for q in state.players.values() if q.active and q.role=='keeper' and q.team!=team),None)
                if p is not None:
                    model = port.m.assume
                    reflex = model['keeper_reaction_s']*(1.3-.6*p.a.awareness)*reflex_gain(p)
                    if 'keeper_interrupt' in getattr(port.config,'rb333',()):
                        reflex = model['keeper_reaction_s']*reflex_gain(p)
                    if p.speed>model['keeper_set_mps']:
                        reflex += model['keeper_unset_s']
                    keeper = (body(p,True),p.a.standing_reach_m,reflex,p.native_registry['reflex'],
                              port.m.c4c_reach(p)/p.a.reach)
            result = release(pid,velocity,kind,*args,**kwargs)
            if result and (command or keeper):
                for row in engine.log[before:]:
                    if row['event']=='release':
                        if command and details:
                            intent = command.intent
                            self.motion[row['id']] = intent, self.admitted_view.pop(intent.intent_id,None)
                        if keeper:
                            self.keeper[row['id']] = keeper
                        break
            return result

        def observed_boundary(x=None, y=None, carrier=None):
            before = len(engine.log)
            ball = state.ball
            held = carrier or ball.carrier
            probe = dict(mode_before=ball.mode.value, last_releaser=ball.last_releaser)
            if held:
                athlete = state.players[held]
                view = self.views.get(held)
                intent = getattr(athlete,'native_intent',None)
                probe.update(held_by=held,body_out=bool(carrier) or body_out(athlete),
                             body_xy=(athlete.x,athlete.y),
                             actual_velocity=(athlete.vx,athlete.vy),admitted_aim=intent.aim if intent else None)
                if view:
                    probe.update(believed_boundary_m=min(view.x,100-view.x,view.y,100-view.y),
                                 believed_pressure=rb.is_pressured(view,policy.opponents(view,view.tracks)))
            result = boundary(x,y,carrier)
            for row in engine.log[before:]:
                if row['event']=='boundary':
                    self.boundary_states[row['id']] = probe
                    break
            return result

        engine.release = observed_release
        if details:
            engine.boundary = observed_boundary
        port.submit = observed_submit

    def interception(self, flight, player):
        result = super().interception(flight,player)
        if not self.details or flight['id'] not in self.release or flight['id'] not in self.motion:
            return result
        intent,view = self.motion[flight['id']]
        aim = intent.aim
        if view is not None and aim is not None:
            actual_speed = min(view.max_throw_speed,intent.speed)
            clearance = policy.arrival_clearance(view,aim,actual_speed,intent.height,
                policy.opponents(view,view.tracks),intent.wait_ms)
            result['arrival_margin'] = clearance
        return result

    def detail(self, shots):
        log = self.port.m.e.log
        cfg = self.port.config
        physical = dict(self.port.m.assume,goal_radius=cfg.goal_radius)
        boundary = []
        flight = None
        deflected = False
        loose_from = None
        for row in log:
            event,data = row['event'],row['data']
            if event in ('release','restart_release'):
                flight,deflected = row,False
                loose_from = 'forced_release' if data.get('forced') else None
            elif event in ('strip','handoff_fumble'):
                loose_from = event
            elif event in ('touch','arrow_geometry_impact') and flight:
                if event=='touch' or data.get('target')=='ball':
                    deflected = True
            elif event=='boundary':
                probe = self.boundary_states.get(row['id'],{})
                kind = ('carrier' if data.get('carrier') or probe.get('body_out') else
                        'held_ball' if probe.get('held_by') else 'deflection' if deflected else (
                    'pass' if flight and flight['data'].get('kind','pass')=='pass' else
                    'shot' if flight and flight['data'].get('kind')=='shot' else 'loose_ball'))
                record = dict(kind=kind, crossing=data['crossing'],t_ms=row['t_ms'],
                              player=data.get('carrier'),event_id=row['id'])
                if kind=='loose_ball':
                    record['loose_from'] = loose_from or 'unclassified'
                record.update(probe)
                if flight and flight['id'] in self.release:
                    (origin,_,_,_,_,_),aim,_,_ = self.release[flight['id']]
                    record.update(intended=flight['data'].get('target'), aim=aim)
                    if aim:
                        dx,dy = aim[0]-origin[0],aim[1]-origin[1]
                        vx,vy,_ = flight['data']['velocity']
                        record['yaw_deg'] = degrees((atan2(vy,vx)-atan2(dy,dx)+pi)%(2*pi)-pi)
                        record['aim_inside'] = all(0.<=c<=100. for c in aim)
                        points = path((*origin,*flight['data']['velocity']),params(cfg),self.port.m.s.ball.radius,3.,.02)
                        record['first_ground_xy'] = next((r[1:3] for r in points if r[3]<=self.port.m.s.ball.radius+1e-5),None)
                boundary.append(record)
                flight,deflected,loose_from = None,False,None
            elif event in ('control','goal','restart_awarded','period_end'):
                flight,deflected,loose_from = None,False,None
        reached = []
        for shot in shots:
            if not shot['on_target'] or shot['release_id'] not in self.keeper:
                continue
            rid = shot['release_id']
            runner, standing, reaction, reflex, factor = self.keeper[rid]
            (origin,_,_,_,_,_),_,_,gx = self.release[rid]
            velocity = log[rid-1]['data']['velocity']
            trajectory = origin, velocity, gx, params(cfg), self.port.m.s.ball.radius, runner
            limits = physical | dict(reach_factor=factor)
            result = keeper_envelope(*trajectory,reaction,limits)
            if result is None:
                reached.append(dict(release_id=rid,keeper=runner.athlete,status='unobstructed_projection_miss'))
                continue
            start = shot['t_ms']
            end = start+1000*result['flight_s']
            saves = [i for i in self.admissions[runner.athlete] if start<=i.decided_ms<=end and
                     i.auxiliary is not None and i.auxiliary.kind=='save']
            timing = saves[0].decided_ms-start if saves else None
            target_y = None
            if saves:
                decision = saves[0].auxiliary
                if decision.target:
                    target_y = decision.target[1]
                elif decision.course:
                    target_y = min(decision.course,key=lambda point:abs(point[1]-runner.x))[2]
            side = target_y-runner.y if target_y is not None else None
            if shot['save']:
                cause = 'save'
            elif not result['reachable']:
                cause = 'unreachable'
            elif shot['keeper_touch']:
                cause = 'touch_without_save'
            elif timing is None:
                cause = 'no_commit'
            elif not keeper_envelope(*trajectory,max(reaction,timing/1000),limits)['reachable']:
                cause = 'late_commit'
            elif side is not None and side*(result['y']-runner.y)<0:
                cause = 'wrong_side'
            else:
                cause = 'no_contact_after_commit'
            reached.append(result | dict(release_id=rid,keeper=runner.athlete,x=runner.x,y_at_release=runner.y,
                        arm_reach_m=runner.reach,standing_reach_m=standing,jump_m=runner.jump_height,
                        reflex=reflex,reaction_s=reaction,commit_ms=timing,believed_target_y=target_y,cause=cause))
        return boundary,reached
