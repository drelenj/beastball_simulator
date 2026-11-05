"""Bounce throws (DreLen, 3 Nov): a player throws the ball to a spot on the playing surface and the ball's own physics (gravity, drag, bounce, roll) does the rest.
Three uses, all the same primitive: DRIBBLE (throw ahead of yourself and play it again, once per possession), SKIP PASS (bounce to a teammate), BOUNCE SHOT (angle into goal off the surface).
The planner uses the engine's own predict_path (same bounce rule as the match).  Nothing here decides an outcome: the ball flies, bounces, is contested and caught by the existing physics.
Rule: a player's re-touch of his own release is normally a self_recontact foul; after a dribble throw that has touched the ground he may play it once (per possession spell).
Switch BOUNCE_OPTION (default 1); per-team genes in BG: dribble_rate, skip_rate, bounce_shot_rate (all 0 = off).
"""
import math, os, random, types
BG = {t: dict(dribble_rate=0., skip_rate=0., bounce_shot_rate=0.) for t in 'AB'}
ST = {'flag_pass': {}, 'flag_shot': {}, 'drib': {}, 'used': set(), 'stats': {}}
def cnt(k, n=1): ST['stats'][k] = ST['stats'].get(k, 0) + n
def reset():
    ST['flag_pass'].clear(); ST['flag_shot'].clear(); ST['drib'].clear(); ST['used'].clear(); ST['stats'].clear()

def install(P):
    CO = P.CORE; M = CO.match.Match; E = CO.engine.Engine; G = CO.geometry
    import importlib
    core = importlib.import_module(M.__module__)
    launch_for, predict_path = core.launch_for, core.predict_path
    on = lambda: os.environ.get('BOUNCE_OPTION', '1') == '1'
    def unit_(dx, dy): n = math.hypot(dx, dy) or 1.; return dx / n, dy / n
    def path_of(self, origin, vel):
        b = types.SimpleNamespace(x=origin[0], y=origin[1], z=origin[2], vx=vel[0], vy=vel[1], vz=vel[2], radius=.1075)
        return predict_path(b, self.assume['gravity'], self.assume['ball_drag'], self.assume.get('ball_restitution', .7745966692), horizon=3.2, step=.05)
    def first_ground(path):
        for i, (t, x, y, z) in enumerate(path[1:], 1):
            if z <= .1075 + 1e-6: return i
        return None
    def plan_to_ground(self, origin, spot, speeds=(.5, .65, .8)):
        """launch that lands the ball on spot (a skip/dribble throw); returns (vel, path, i_ground) or None"""
        vmax = self.cfg['pocket']['pass_speed']
        for f in speeds:
            sol = launch_for(origin, (spot[0], spot[1], .2), vmax * f, self.assume['gravity'], self.assume['ball_drag'])
            if sol is None: continue
            path = path_of(self, origin, sol[0]); ig = first_ground(path)
            if ig is not None and math.hypot(path[ig][1] - spot[0], path[ig][2] - spot[1]) < 1.0: return sol[0], path, ig
        return None
    def plan_skip(self, origin, q, hand):
        """bounce pass to receiver q: landing fraction and speed searched so the path after the bounce passes his hands"""
        vmax = self.cfg['pocket']['pass_speed']; d = math.hypot(q.x - origin[0], q.y - origin[1]); best = None
        for f in (.4, .5, .6, .7):
            for sp in (.6, .75, .9):
                T = d / (vmax * sp * .85); aim = (min(99., max(1., q.x + q.vx * T)), min(99., max(1., q.y + q.vy * T)))
                land = (origin[0] + f * (aim[0] - origin[0]), origin[1] + f * (aim[1] - origin[1]))
                sol = launch_for(origin, (land[0], land[1], .2), vmax * sp, self.assume['gravity'], self.assume['ball_drag'])
                if sol is None: continue
                path = path_of(self, origin, sol[0]); ig = first_ground(path)
                if ig is None: continue
                for t, x, y, z in path[ig + 1:]:
                    if .4 <= z <= q.z + q.a.height * .95:
                        m = math.hypot(x - (q.x + q.vx * t), y - (q.y + q.vy * t))
                        if best is None or m < best[0]: best = (m, sol[0], aim, t)
                        break
        return best if best and best[0] < 1.5 else None
    def plan_bounce_shot(self, origin, p, gx, ty):
        sg = self.s.attack_sign(p.team); vmax = self.cfg['pocket']['ball_speed']; best = None
        for f in (.45, .55, .65, .75):
            for sp in (.6, .8, 1.):
                land = (origin[0] + f * (gx - origin[0]), origin[1] + f * (ty - origin[1]))
                sol = launch_for(origin, (land[0], land[1], .2), vmax * sp, self.assume['gravity'], self.assume['ball_drag'])
                if sol is None: continue
                path = path_of(self, origin, sol[0]); ig = first_ground(path)
                if ig is None: continue
                for t, x, y, z in path[ig + 1:]:
                    if sg * (x - gx) >= 0:
                        if .25 <= z <= 2.6 and abs(y - ty) <= 1.2:
                            m = abs(y - ty) + abs(z - 1.2) * .2
                            if best is None or m < best[0]: best = (m, sol[0])
                        break
        return best
    # ---- skip pass: flag at preparation, plan at planning, consumed at execution
    o_pass, o_plan, o_shot, o_cd = M.make_pass, M.plan_pass, M.make_shot, M.carrier_decision
    def rnd(self, tag, p): return random.Random('%s-%s-%d-%s' % (self.cfg.get('seed', 0), p.id, self.s.now, tag)).random()
    def make_pass(self, p, q, kind='pass', execute=False, *a, **k):
        g = BG.get(p.team)
        if on() and g and g['skip_rate'] > 0 and kind == 'pass':
            if not execute and p.id not in ST['flag_pass']:
                gx, gy = q.x - p.x, q.y - p.y; contested = False
                for o in self.s.players.values():
                    if o.team != p.team and o.active and o.role != 'archer':
                        d, _ = G.segment_distance(o.x, o.y, p.x, p.y, q.x, q.y)
                        if d < 2.2: contested = True; break
                if contested and rnd(self, 'skip', p) < g['skip_rate']: ST['flag_pass'][p.id] = True; cnt('skip_flagged')
            res = o_pass(self, p, q, kind, execute, *a, **k)
            if execute: ST['flag_pass'].pop(p.id, None)
            return res
        return o_pass(self, p, q, kind, execute, *a, **k)
    def plan_pass(self, origin, passer, q, kind, lag=0., speed=None):
        if on() and kind == 'pass' and ST['flag_pass'].get(passer.id):
            r = plan_skip(self, origin, q, None)
            if r is not None: cnt('skip_planned'); return (r[1], r[2], r[3])
            cnt('skip_no_plan')
        return o_plan(self, origin, passer, q, kind, lag, speed)
    # ---- bounce shot
    def make_shot(self, p, execute=False):
        g = BG.get(p.team); s = self.s
        if on() and g and g['bounce_shot_rate'] > 0:
            dg = abs(s.attack_goal(p.team) - p.x)
            if not execute and p.id not in ST['flag_shot'] and 5 < dg < 26 and rnd(self, 'bshot', p) < g['bounce_shot_rate']: ST['flag_shot'][p.id] = True; cnt('bshot_flagged')
            if execute and ST['flag_shot'].pop(p.id, None):
                b = s.ball; gx = s.attack_goal(p.team); keeper = next((q for q in s.players.values() if q.team != p.team and q.active and q.role == 'keeper'), None)
                side = -1 if keeper and keeper.y > 50 else 1; skill = (p.a.passing + p.a.ball_handling) / 2
                plan = plan_bounce_shot(self, (b.x, b.y, b.z), p, gx, 50 + side * (2.0 + .6 * skill))
                if plan is not None:
                    rho, factor, extra = self.c3_release_state(p, 'shot'); vel = self.c3_perturb(plan[1], extra)
                    if self.e.release(p.id, vel, 'shot'): self.stats['shot_attempts'] += 1; p.next_action = s.now + 500; cnt('bshot_taken')
                    return
                cnt('bshot_no_plan')
        return o_shot(self, p, execute)
    # ---- dribble: a throw to a spot ahead, replayed once
    def carrier_decision(self):
        s = self.s; b = s.ball; p = s.players.get(b.carrier) if b.carrier else None
        g = BG.get(p.team) if p else None
        if on() and p is not None and g and g['dribble_rate'] > 0 and s.phase == CO.types.Phase.LIVE and p.id not in self.pending_ball_actions and self.e.eligible(p) and s.now >= p.next_action \
                and p.posture == 'upright' and p.role == 'field' and s.now - b.control_time > 500 and p.id not in ST['used'] and p.id not in ST['drib']:
            if rnd(self, 'drib', p) < g['dribble_rate'] * .04:
                hx, hy = (p.vx, p.vy) if math.hypot(p.vx, p.vy) > 2. else (s.attack_sign(p.team), 0.); ux, uy = unit_(hx, hy); d = 5. + 3. * rnd(self, 'dd', p)
                spot = (p.x + ux * d, p.y + uy * d)
                clear = 2. < spot[0] < 98. and 2. < spot[1] < 98. and all(math.hypot(o.x - spot[0], o.y - spot[1]) > 5. and G.segment_distance(o.x, o.y, p.x, p.y, spot[0], spot[1])[0] > 3.
                                                                             for o in s.players.values() if o.team != p.team and o.active and o.role != 'archer')
                if clear:
                    plan = plan_to_ground(self, (b.x, b.y, b.z), spot)
                    if plan is not None and self.e.release(p.id, plan[0], 'loose'):
                        ST['drib'][p.id] = dict(spot=spot, t=s.now, ver=b.version, grounded=False); cnt('dribble_thrown'); self.e.emit('dribble', 'V03:dribble', player=p.id, spot=[round(spot[0], 2), round(spot[1], 2)]); return
        return o_cd(self)
    M.make_pass, M.plan_pass, M.make_shot, M.carrier_decision = make_pass, plan_pass, make_shot, carrier_decision
    # ground contact tracking + the once-per-possession waiver of self_recontact
    o_step = M.step
    def step(self):
        o_step(self)
        if ST['drib']:
            b = self.s.ball
            for pid, d in list(ST['drib'].items()):
                if b.carrier is not None and b.carrier != pid: ST['drib'].pop(pid, None); ST['used'].discard(pid); continue      # another player has it: the spell is over
                if b.carrier == pid and d.get('waived'): ST['used'].add(pid); ST['drib'].pop(pid, None); cnt('dribble_replayed'); self.e.emit('dribble_replayed', 'V03:dribble', player=pid); continue
                if b.z <= .13 and self.s.now > d['t'] + 120 and not d['grounded']:
                    d['grounded'] = True
                    if b.last_releaser == pid: b.last_releaser = None; d['waived'] = True
                if self.s.now > d['t'] + 6000: ST['drib'].pop(pid, None)
    M.step = step
    def wrap(name, who=lambda a: a[0]):
        orig = getattr(E, name)
        def f(self, *a, **k):
            pid = who(a); d = ST['drib'].get(pid); b = self.s.ball
            if on() and d is not None and d['grounded'] and b.last_releaser == pid:
                b.last_releaser = None; ST['used'].add(pid); ST['drib'].pop(pid, None); cnt('dribble_replayed'); self.emit('dribble_replayed', 'V03:dribble', player=pid)
            return orig(self, *a, **k)
        setattr(E, name, f)
    wrap('acquire')
    wrap('c1_reason', lambda a: getattr(a[0], 'actor', None))
    Pol = CO.policies.Policy; o_t = Pol.targets
    def targets(self, s):
        out = o_t(self, s)
        if on() and ST['drib']:
            for pid, d in ST['drib'].items():
                p = s.players.get(pid)
                if p is not None and p.team == self.team and s.ball.carrier is None:
                    # run to where the ball will come down (if still airborne use the spot, once grounded follow the ball)
                    out[pid] = (s.ball.x, s.ball.y) if d['grounded'] else d['spot']
        return out
    Pol.targets = targets
