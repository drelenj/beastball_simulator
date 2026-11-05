#!/usr/bin/env python3
"""Pocket 4.0 prototype: Pocket 2.0 (untouched) + the systems built this week, as a hook layer.  RAW CALIBRATION: nothing here is tuned, only connected.

    python3 pocket4_proto.py                         # two generated teams, full regulation game
    python3 pocket4_proto.py --a rosterA.csv --b rosterB.csv    # name,position,overall
    python3 pocket4_proto.py --short                  # 2 x 120 s (Pocket's default length)
    python3 pocket4_proto.py --off throw,jump         # switch systems off to compare (see SYSTEMS)

WIRED (each can be switched off with --off):
  roster    ROSTER   player_gen_v1: name/position/overall -> height, mass, 20 ratings.  Pocket's roster-override mechanism carries them in.
  throw     THROW    every non-forced release: Throw Power caps the speed (whole-body chain, readiness, run loss), Throw Accuracy sets the error (running, fatigue, grip), ball shape matters.
                     'kick' releases (Pocket's long pass) go through the kicking model (punt: Kick Power / Kick Accuracy, drop + strike time).  Pocket's own aim error is switched off (this replaces it).
  pose      POSE     release delay = chain + carry-pose transition: 'tucked' (0.35 s to loaded) if an opponent is within 8 m, else 'exposed' (0.10 s).  Replaces Pocket's fixed 250 ms scaling.
  shape     SHAPE    ball shape (sphere / prolate1.25 / 1.5 / 1.8): catch capacity divided by catch_multiplier; grip quality in throws and kicks.
  condition CONDITION per-player Condition2: fatigue valve (Stamina), wear valve (Durability), injury strain / stochastic events (Injury rating).  Its reserve drives Pocket's fatigue field (Pocket's own
                     fatigue is switched off); every 3 s the athlete's speed / acceleration / braking / turning follow the capability table at his current reserve and injury.  Tackle groundings load the wear
                     and strain model.  An athlete whose status reaches 'out' is taken off through Pocket's own injury and substitution path.
  jump      JUMP     any athlete can leave the ground for a ball above his standing reach (Pocket's sphere), if it is reachable, he has the time (reaction, crouch), and the jump gets him there 0.10 s
                     sooner than staying down (airborne_contest_v1 rules).  Jump rating x 1.3 m of lift, fatigue-scaled.  Pocket's own airborne motion and catch kernel do the rest.
  windup    WINDUP   defenders near a shot line have their hands set at the release (the wind-up is visible; Keeper-style read).
  foot      FOOT     foot-play legality monitor on every kick (ready / live / spent) and on bounces; Pocket's 'self_recontact' foul is waived for a legal foot sequence.  Controllers do not dribble or juggle yet.

NOT WIRED: ball carry poses as strip resistance (anatomy retention), per-part holds, airborne contest with body blocks, kick/dribble as decisions, season layer.  See POCKET4_PROTO_NOTES.md.
"""
import sys, os, math, random, json, time, zlib, copy, importlib.util, argparse
# PRISM_I=1: the individual layer's vetted configuration in one switch (each flag can still be overridden explicitly; read before the modules below import).
if os.environ.get('PRISM_I', '0') == '1':
    for _k, _v in (('PRISM_FIELD', '1'), ('PRISM_DEF', '1'), ('PRISM_BOUNDED', '1'), ('PRISM_MANEUVERS', '1')): os.environ.setdefault(_k, _v)
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
for p_ in (HERE, '/home/claude/next/p23/v37pkg'):
    if p_ not in sys.path: sys.path.append(p_)
import throwing_v1 as T, kicking_v1 as K, ball_handling_v1 as BH, foot_rule_v1 as FR, player_gen_v1 as G
import condition_layer_v2 as C2, pocket_capability_v37 as CAP
import positional_tendencies_v1 as PT
import restarts_v1 as RS
import prism_archer_v0 as PRISM
import prism_field_v0 as PFIELD
import prism_ratings_v0 as PRAT
import rules_v03 as RV03
import block_option_v0 as BLK
import bounce_option_v0 as BNC
import pose_engine_v0 as PMAN

SYSTEMS = ('roster', 'rotation', 'tendencies', 'restarts', 'archerfix', 'arrowlead', 'throw', 'pose', 'shape', 'condition', 'jump', 'windup', 'foot')
INJ_TH = 1.35       # injury thresholds x this (fatigue still follows LOAD_REF); 1.0 = layer default
INJ_HAZ = .25       # baseline random-injury hazard x this
LOAD_REF = 1.6      # injury loads are measured against LOAD_REF x his Pocket limit (Pocket controllers use the limit constantly; see notes)
ROT = dict(out=.60, back=.75, target_min=32., game_min=40., slack_s=60., min_rest_s=120., max_swaps=2, break_swaps=4)   # rotation policy (DreLen, 29 Oct)
JUMP_RISE_MAX = 1.3; JUMP_MARGIN = .9; JUMP_PEN = .10
class State:
    tend = {}                         # one per process; set before a match is created
    on = set(SYSTEMS); shape = 'sphere'; extras = {}; names = {}; seed = 1
    last = None
S = State()


# ---- Archer platform study (env knobs; all default to stock Pocket 2.0 behaviour) ----------------------------------------------------------
PLAT = os.environ.get('PLAT', '0') == '1'                      # fixed elevated platform behind own goal facing the opposing goal (static x,y)
PLAT_H = float(os.environ.get('PLAT_H', '10'))                 # platform height, m (test input, not canon)
PLAT_SET = float(os.environ.get('PLAT_SET', '5'))              # setback behind the goal plane, m
RULESET = os.environ.get('RULESET', '1.0.1')                   # 1.0.2 = freezes count on any eligible target, not only the carrier
ARCH_RMIN = float(os.environ.get('ARCH_RMIN', '10')); ARCH_RMAX = float(os.environ.get('ARCH_RMAX', '70'))   # legal 3D range
ARCH_NEAR = float(os.environ.get('ARCH_NEAR', '9'))            # 1.0.2 structure policy: candidate must be within this of the carrier
QUIVER_POSS = os.environ.get('QUIVER_POSS', '0') == '1'      # both quivers refill (5 loaded, spent reset) at every change of possession
FREEZE_CAP = int(os.environ.get('FREEZE_CAP', '0'))            # freezes allowed against a team per possession (0 = no cap)
KSTEP = float(os.environ.get('KEEPER_STEP_FRAC', '.5'))      # Keeper stays on his feet only if the ball passes within this fraction of his hand reach (engine default .95); lower = dives sooner
NET_R = float(os.environ.get('NET_R', '6'))                  # net semicircle radius, m (engine 6 = 12 m wide x 6 m high; 3 = 6 x 3)
KEEPER_FT = float(os.environ.get('KEEPER_FT', '0'))          # both Keepers' height in feet (9-12); 0 = engine default
CV2 = os.environ.get('CATCH_V2', '0') == '1'                    # catch model v2: one model for all, threshold energy capacity, PRISM readiness
JSP = os.environ.get('PRISM_JSPLIT', '0') == '1'                # v0.7: the split judgement ratings act
KPK = os.environ.get('PRISM_KEEPER', '0') == '1'                # v0.5: Keepers perceive the free ball through PRISM
def _fmt(v): return repr(float(v)) if float(v) != int(float(v)) else str(int(float(v)))
def patch_source(path):
    """Pocket 2.0 hard-codes archery range, ruleset and the archery-zone reload test in its embedded sources; patch a temp copy when a study knob is set."""
    if not (PLAT or RULESET != '1.0.1' or ARCH_RMIN != 10 or ARCH_RMAX != 70 or ARCH_NEAR != 9 or KSTEP != .95 or NET_R != 6 or KEEPER_FT != 0 or KPK or CV2 or JSP): return path
    import tempfile
    t = open(path, encoding='utf-8').read()
    reps = [("10<=d<=70", f"{_fmt(ARCH_RMIN)}<=d<={_fmt(ARCH_RMAX)}"),
            ("10<=math.dist(origin,(c.x,c.y,.55*c.a.height))<=70", f"{_fmt(ARCH_RMIN)}<=math.dist(origin,(c.x,c.y,.55*c.a.height))<={_fmt(ARCH_RMAX)}"),
            ("norm(c.x-carrier.x,c.y-carrier.y)<=9 and not", f"norm(c.x-carrier.x,c.y-carrier.y)<={_fmt(ARCH_NEAR)} and not"),
            ("'ruleset':'1.0.1',", f"'ruleset':'{RULESET}',"),
            ("if need*need+dz*dz<=(.95*R)**2:pick=('step'", f"if need*need+dz*dz<=({_fmt(KSTEP)}*R)**2:pick=('step'"),
            ("service=(-10<=p.y<=-5)if low else(105<=p.y<=110)", "service=True if getattr(self,'platform',False) else ((-10<=p.y<=-5)if low else(105<=p.y<=110))"),
            ("(archer.y<=-5 if s.ends[t]==0 else archer.y>=105)", "(True if getattr(self,'platform',False) else (archer.y<=-5 if s.ends[t]==0 else archer.y>=105))")]
    if NET_R != 6:
        reps += [("norm(y-50,z)+r<=6+1e-7", f"norm(y-50,z)+r<={_fmt(NET_R)}+1e-7"),
                 ("6-b.radius<=norm(yy-50,zz)<=6+self.assume['frame_thickness']+b.radius", f"{_fmt(NET_R)}-b.radius<=norm(yy-50,zz)<={_fmt(NET_R)}+self.assume['frame_thickness']+b.radius")]
    if JSP: reps += [("best=max(opts,key=lambda k:(opts[k],k=='continue'))", "opts=self.judge_opts(p,opts);best=max(opts,key=lambda k:(opts[k],k=='continue'))"),
                     ("    best = max(options, key=lambda key: (options[key], key == 'shoot'))", "    options = self.judge_opts(p, options)\n    best = max(options, key=lambda key: (options[key], key == 'shoot'))")]   # the second is the decision Pocket 2.0 actually runs
    if KEEPER_FT != 0: reps += [('"keeper_height_m": 0.0,', f'"keeper_height_m": {round(KEEPER_FT*0.3048,4)!r},'), ("'keeper_height_m': 0.0}", f"'keeper_height_m': {round(KEEPER_FT*0.3048,4)!r}}}")]
    if CV2:
        reps += [("tau=A['catch_reaction_s']*(1.3-.6*p.a.awareness);fset=lo", "tau=self.catch_tau(p,A['catch_reaction_s']*(1.3-.6*p.a.awareness));fset=lo"),
                 ("skill=p.a.keeper_skill if p.role=='keeper'else p.a.catching", "skill=p.a.catching"),
                 ("capacity=A['catch_arrest_force_N']*A['catch_hand_travel_m']*(.4+.9*skill)*max(0.,1-miss*miss)", "capacity=self.catch_capacity(skill,miss)"),
                 ("secure=1/(1+(energy/capacity)**2)if capacity>1e-9 else 0.", "secure=self.catch_secure(energy,capacity)"),
                 ("return[Event('acquire',q.id,data={'ball_point':point(g),'c1_contact':True,**({'c4c_kind':'catch'}if self.c4c and q.role=='keeper'else{})},at=at)for g,w,_,q,good,_ in cands if good and int(g*ms)==at and(q is p or g!=f or abs(w-near)<1e-9)]", "return self.hc_acquire(cands,at,f,near,p,ms,point)"),
                 ("(1.1 if p.role=='keeper'else.9)", ".9"), ("(1.1 if q.role=='keeper'else.9)", ".9"), ("return p.a.reach*1.1", "return p.a.reach*.9")]
    if KPK:
        reps += [("react=1000*(A['keeper_reaction_s']*(1.3-.6*p.a.awareness)+(A['keeper_unset_s']if sp>A['keeper_set_mps']else 0.))", "react=self.kp_react(p,A,sp,1000*(A['keeper_reaction_s']*(1.3-.6*p.a.awareness)+(A['keeper_unset_s']if sp>A['keeper_set_mps']else 0.)),t_obs)"),
                 ("   if b.carrier is None and b.mode!=BallMode.CONTESTED:\n    seen=getattr(p,'c4c_seen',None)\n", "   if b.carrier is None and b.mode!=BallMode.CONTESTED and self.kp_aware(p):\n    seen=getattr(p,'c4c_seen',None)\n"),
                 ("if seen is None or seen[0]!=b.version:", "if(seen is None or seen[0]!=b.version)and self.kp_noticed(p,b,seen):"),
                 ("t_obs=max([t for t in(b.release_time,getattr(b,'course_time',-1))if t is not None and prev<t<=s.now]or[s.now])", "t_obs=self.kp_tobs(p,max([t for t in(b.release_time,getattr(b,'course_time',-1))if t is not None and prev<t<=s.now]or[s.now]))"),
                 ("s.now>=seen[2]-1e-9 and pl is None:", "s.now>=seen[2]-1e-9 and pl is None and self.kp_ready(p,b,seen):"),
                 ("if b.carrier is None and seen is not None and seen[0]==b.version and pl is None:out.append(seen[2])", "if b.carrier is None and seen is not None and seen[0]==b.version and pl is None:out.append(self.kp_wake(p,seen))"),
                 ("path=self.c4c_path(b);cross=self.c4c_threat(p,path)", "path=self.c4c_path(self.kp_ball(p,b,seen));cross=self.kp_cross(p,self.c4c_threat(p,path))")]
    for a, b in reps:
        if a not in t: raise RuntimeError('patch anchor missing: ' + a)
        t = t.replace(a, b)
    d = tempfile.mkdtemp(prefix='pk_'); out = os.path.join(d, 'Pocket20_patched.py'); open(out, 'w', encoding='utf-8').write(t); return out

def load_pocket(path=None):
    path = path or next((os.path.join(d, f) for d in (HERE, os.path.dirname(HERE)) for f in ('Beastball Pocket 2 0(1).py', 'Beastball_Pocket_2_0.py') if os.path.exists(os.path.join(d, f))), None)
    if path is None: raise FileNotFoundError('Pocket 2.0 source not found next to this file')
    path = patch_source(path)
    spec = importlib.util.spec_from_file_location('pocket20', path); m = importlib.util.module_from_spec(spec); sys.modules['pocket20'] = m
    argv = sys.argv; sys.argv = ['x']
    try: spec.loader.exec_module(m)
    finally: sys.argv = argv
    return m

class P4:
    """per-match state"""
    def __init__(self, match):
        self.m = match; self.shape = T.SHAPES[S.shape]; self.cond = {}; self.stats = Counter(); self.jumps = {}; self.pending = {}; self.foot = {}; self.last_ms = 0
        self.last_cap = {}; self.base = {}; self.injured_log = []; self.foot_log = []; self.holder = None; self.jump_log = []; self.mins = Counter(); self.off = Counter(); self.last_live = 0; self.rot_log = []; self.exit = {}; self.pos_acc = {}

def install(P):
    CO = P.CORE; Match, Engine, BallMode, Phase = CO.match.Match, CO.engine.Engine, CO.types.BallMode, CO.types.Phase
    P.geo = CO.geometry
    orig = dict(auto=Match.auto_substitutions, init=Match.__init__, step=Match.step, aim=Match.aim_error, make_pass=Match.make_pass, make_shot=Match.make_shot)
    clamp, norm, unit, distance = CO.geometry.clamp, CO.geometry.norm, CO.geometry.unit, CO.geometry.distance

    def ex(p): return S.extras.get(p.id) or dict(throw_power=.7, throw_accuracy=p.a.passing, kick_power=.7, kick_accuracy=p.a.kicking, jump=.6, stamina=p.a.endurance, durability=.7, injury=.7, speed=.8)

    def thrower(self, p, kind):
        e = ex(p); c = self.p4.cond.get(p.id)
        pw, ac, tc = (e['throw_power'], e['throw_accuracy'], p.a.passing) if kind != 'kick' else (e['kick_power'], e['kick_accuracy'], e['kick_accuracy'])
        if T.SPLIT and kind != 'kick' and p.id in T.RATINGS: pw, ac, tc = (T.rating_x(r) for r in T.RATINGS[p.id])
        return T.Thrower(height=p.a.height, power=pw, accuracy=ac, touch=tc,
                         vel=(p.vx, p.vy), top=self.p4.base.get(p.id, {}).get('top', p.a.maximum_speed), reserve=(c.reserve if c else p.fatigue), damage=(c.damage if c else {}))

    def pose(self, p):
        z = getattr(self, 'pm', None)
        if z is not None and z.fsm is not None and z.car == p.id: return z.fsm.pose      # PRISM_MANEUVERS: the carrier's own pose FSM
        near = min((distance(p, q) for q in self.s.players.values() if q.team != p.team and q.active and q.role != 'archer'), default=99.)
        return 'tucked' if near < 8. else 'exposed'

    # ---------------------------------------------------------------- init
    def init(self, config=None):
        orig['init'](self, config)
        self.p4 = P4(self); S.last = self; a = self.assume
        if 'condition' in S.on: a['fatigue_rate'] = 0.                            # the Condition layer owns fatigue
        for p in self.s.players.values():
            e = S.extras.get(p.id)
            if e is None: continue
            self.p4.base[p.id] = dict(top=p.a.maximum_speed, acc=p.a.acceleration, brk=p.a.braking, turn=p.a.turning)
            if 'condition' in S.on:
                self.p4.cond[p.id] = C2.Condition2(p.id, rating=max(.6, e['speed']), stamina=e['stamina'], role=p.role if p.role == 'keeper' else 'field', durability=e['durability'], injury=e['injury'], seed=S.seed * 1009 + zlib.crc32(p.id.encode()))
                cc = self.p4.cond[p.id]; _th = cc.th; cc.th = (lambda kind, _th=_th: _th(kind) * INJ_TH); cc.rested = dict(cc.rested, top=p.a.maximum_speed, acceleration=LOAD_REF * p.a.acceleration, braking=LOAD_REF * p.a.braking, turning=LOAD_REF * p.a.turning)   # loads are measured against his own Pocket limits
        if 'shape' in S.on:
            mult = BH.catch_multiplier(self.p4.shape, .7)
            a['catch_arrest_force_N'] = a['catch_arrest_force_N'] / mult
        eng = self.e; eng.p4 = self.p4; eng.match = self
        o_release, o_restart, o_grounded, o_strike = eng.release, eng.restart_release, eng.grounded, eng.strike

        def release(pid, velocity, kind='pass', target=None, forced=False):
            if forced or 'throw' not in S.on: return o_release(pid, velocity, kind, target, forced)
            p = self.s.players[pid]; sp = math.sqrt(sum(v * v for v in velocity)) or 1e-9; d = tuple(v / sp for v in velocity); t = thrower(self, p, kind); shape = self.p4.shape
            if kind == 'kick':
                v, info = K.kick(t, shape, d, sp, self.rng['ball'], 'punt'); self.p4.stats['kicks'] += 1
                if 'foot' in S.on: foot_event(self, pid, 'foot')
            else:
                v, info = T.sample_release(t, d, sp, shape, self.rng['ball']); self.p4.stats[kind + '_releases'] += 1
                if info.get('shortfall', 0) > .5: self.p4.stats['power_limited'] += 1
            lim = self.e.pocket.get('ball_limit', 40) - 1e-6; vs = math.sqrt(sum(c * c for c in v))
            if vs > lim: v = tuple(c * lim / vs for c in v)
            ok = o_release(pid, v, kind, target, forced)
            if ok and kind == 'shot' and 'windup' in S.on: windup_read(self, p, v)
            return ok
        def restart_release(taker, velocity, target=None, method='hand'):
            if 'throw' in S.on:
                p = self.s.players[taker]; sp = math.sqrt(sum(v * v for v in velocity)) or 1e-9; d = tuple(v / sp for v in velocity)
                v, _ = T.sample_release(thrower(self, p, 'pass'), d, sp, self.p4.shape, self.rng['ball']); vs = math.sqrt(sum(c * c for c in v)); lim = self.e.pocket.get('ball_limit', 40) - 1e-6
                velocity = tuple(c * lim / vs for c in v) if vs > lim else v
            return o_restart(taker, velocity, target, method)
        def grounded(pid):
            c = self.p4.cond.get(pid)
            if c: c.hit(.7, 'lower'); self.p4.stats['groundings'] += 1
            return o_grounded(pid)
        def strike(pid, velocity, kind='kick'):
            b = self.s.ball
            if 'foot' in S.on and b.last_releaser == pid and legal_foot(self, pid):
                b.last_releaser = None; self.p4.stats['self_recontact_waived'] += 1
            return o_strike(pid, velocity, kind)
        eng.release, eng.restart_release, eng.grounded, eng.strike = release, restart_release, grounded, strike

    # ---------------------------------------------------------------- foot rule monitor
    def foot_event(self, pid, kind):
        r = self.p4.foot.setdefault(pid, FR.FootRule())
        if self.p4.holder is not None and self.p4.holder != pid: self.p4.foot.pop(self.p4.holder, None); r = self.p4.foot.setdefault(pid, FR.FootRule())
        self.p4.holder = pid; ok = r.event(kind)
        if not ok: self.p4.foot_log.append(('second_ground_kick', pid, self.s.now)); self.p4.stats['foot_fouls'] += 1
        return ok
    def legal_foot(self, pid):
        r = self.p4.foot.get(pid); return r is not None and r.state == 'live'

    # ---------------------------------------------------------------- wind-up read for shot lanes
    def windup_read(self, p, v):
        """defenders within 3 m of the shot line and under 30 m of the shooter have their hands set"""
        b = self.s.ball; sp = math.hypot(v[0], v[1]) or 1e-9; ux, uy = v[0] / sp, v[1] / sp; n = 0
        for q in self.s.players.values():
            if q.team == p.team or not q.active or q.role == 'archer': continue
            dx, dy = q.x - b.x, q.y - b.y; al = dx * ux + dy * uy; la = abs(-dx * uy + dy * ux)
            if 0 < al < 30 and la < 3.: self.hands_set[q.id] = True; n += 1
        self.p4.stats['windup_reads'] += n

    # ---------------------------------------------------------------- jump planner
    def plan_jumps(self):
        s = self.s; b = s.ball
        if b.carrier is not None or b.mode not in (BallMode.PASS, BallMode.SHOT, BallMode.KICK, BallMode.LOOSE) or s.phase not in (Phase.LIVE, Phase.FLIGHT, Phase.AWARD): return
        g = self.assume['gravity']; path = CO.geometry.predict_path(b, g, self.assume['ball_drag'], horizon=1.4, step=.05); now = s.now
        tcc = (now - getattr(b, 'release_time', 0)) / 1000.
        for p in s.players.values():
            if not p.active or p.role == 'archer' or p.posture != 'upright' or p.z > .02 or not self.e.eligible(p) or b.last_releaser == p.id or p.id in self.p4.pending: continue
            e = S.extras.get(p.id)
            if e is None: continue
            c = self.p4.cond.get(p.id); res = c.reserve if c else p.fatigue
            rise = JUMP_RISE_MAX * e['jump'] * T.fatigue_factor(res)
            if rise < .15: continue
            dly = max(0., (.35 - .20 * p.a.awareness) - tcc - (.4 if b.intended == p.id else 0.))
            u = min(1., p.speed / max(1., p.a.maximum_speed)); crouch = .20 + (.08 - .20) * u
            top0 = .62 * p.a.height + .9 * p.a.reach; acc = p.a.acceleration * (.55 + .45 * p.fatigue)
            t_jump = t_ground = None; best = None
            for (t, x, y, z) in path[1:]:
                if t <= dly + .05: continue
                dev = math.hypot(x - (p.x + p.vx * t), y - (p.y + p.vy * t))
                L = z - (top0 - .30)
                if L <= .05:
                    if dev <= .9 * p.a.reach + .5 * acc * max(0., t - dly) ** 2 and t_ground is None: t_ground = t
                    continue
                if L > JUMP_MARGIN * rise: continue
                vz0 = math.sqrt(2 * g * min(rise, L + .08)); t_to = t - vz0 / g
                if t_to < dly + crouch: continue
                if dev <= .9 * p.a.reach * .7 + .5 * acc * max(0., t_to - dly) ** 2 and t_jump is None: t_jump = t; best = (t_to, vz0, z)
            if t_jump is None: continue
            if t_ground is not None and t_ground <= t_jump + JUMP_PEN: continue
            self.p4.pending[p.id] = (now + int(1000 * best[0]), best[1]); self.p4.stats['jumps_planned'] += 1; self.p4.jump_log.append((now, p.id, round(best[2], 2), round(best[1], 2)))
    def fire_jumps(self, ms):
        s = self.s
        for pid, (t_to, vz0) in list(self.p4.pending.items()):
            p = s.players[pid]
            if not p.active or p.posture in ('grounded',) or s.ball.carrier is not None and False: self.p4.pending.pop(pid); continue
            if t_to <= s.now + ms:
                p.vz = vz0; p.posture = 'airborne'; self.p4.pending.pop(pid); self.p4.stats['jumps'] += 1

    # ---------------------------------------------------------------- condition
    def condition_post(self, ms):
        s = self.s; dt = ms / 1000.
        if dt <= 0: return
        for p in s.players.values():
            c = self.p4.cond.get(p.id)
            if c is None: continue
            if not p.active:
                if not p.injured: c.rest(dt, bench=True)      # the bench recovers wear and fatigue
                continue
            base = self.p4.base.get(p.id)
            if c.prev is not None and base is not None and dt > 0:     # the engine teleports / zeroes velocity at tackles, restarts and period changes: that is not athletic load
                pvx, pvy = c.prev; ax, ay = (p.vx - pvx) / dt, (p.vy - pvy) / dt
                psp = math.hypot(pvx, pvy); lat = abs(-ax * pvy + ay * pvx) / psp if psp > .5 else 0.
                if lat > LOAD_REF * base['turn'] or math.hypot(ax, ay) > 1.6 * LOAD_REF * max(base['acc'], base['brk']) or p.posture != 'upright' or s.phase != Phase.LIVE:
                    c.prev = None; self.p4.stats['load_discontinuity'] += 1
            c.step(dt, p, None, carrying=(s.ball.carrier == p.id))
            p.fatigue = clamp(c.reserve, .15, 1.)
        if s.now - self.p4.last_ms >= 3000:
            self.p4.last_ms = s.now
            for p in s.players.values():
                c = self.p4.cond.get(p.id); base = self.p4.base.get(p.id)
                if c is None or base is None or not p.active: continue
                region, sev = c.loco_injury(); sev = min(1., sev)
                role = 'keeper' if p.role == 'keeper' else 'field'
                try:
                    cap = CAP.capability(max(.6, S.extras[p.id]['speed']), c.reserve, region if role == 'field' else '', sev if role == 'field' else 0., role); ref = CAP.capability(max(.6, S.extras[p.id]['speed']), 1., '', 0., role)
                except Exception: continue
                if cap['top_mph'] and ref['top_mph']:
                    f = cap['top_mph'] / ref['top_mph']; p.a.maximum_speed = base['top'] * f
                if cap['t10_s'] and ref['t10_s']: p.a.acceleration = base['acc'] * ref['t10_s'] / cap['t10_s'] ** 1.0
                if cap['stop25_m'] and ref['stop25_m']: p.a.braking = base['brk'] * ref['stop25_m'] / cap['stop25_m']
                if cap['cut90_25_s'] and ref['cut90_25_s']: p.a.turning = base['turn'] * ref['cut90_25_s'] / cap['cut90_25_s']
                if c.status() == 'out' and p.active and p.role == 'field' and p.id not in [x[0] for x in self.p4.injured_log]:
                    self.p4.injured_log.append((p.id, s.now, c.status(), {k: round(v, 2) for k, v in c.damage.items() if v > 0}, dict(c.cause)))
                    self.p4.stats['injuries'] += 1
                    try: self.e.injury(p.id)
                    except Exception as ex_: self.p4.stats['injury_call_failed'] += 1

    # ---------------------------------------------------------------- lineup rotation
    def is_starter(pid): return int(pid[1:]) < 10
    def pace_max_ms(self):
        return ROT['target_min'] / ROT['game_min'] * self.s.live_ms + 1000. * ROT['slack_s']
    def do_sub(self, o, n, why):
        s = self.s
        o.active = False; n.active = True; n.role = o.role; n.slot = o.slot; n.zone_ms = list(o.zone_ms); n.outside_ms = list(o.outside_ms)
        self.e.slot_inherit(o, n); n.freeze_until = max(n.freeze_until, o.freeze_until); n.keeper_hold_ms = o.keeper_hold_ms
        n.x, n.y = o.x, o.y; n.vx = n.vy = 0.; n.posture = 'upright'; n.z = 0.; n.next_action = max(n.next_action, s.now + 300)
        self.p4.exit[o.id] = (s.live_ms, why)
        self.e.emit('substitution', '14.1-14.3', out=o.id, incoming=n.id, role=n.role, freeze_until=n.freeze_until)
        self.p4.rot_log.append((s.live_ms, o.id, n.id, why, round(self.p4.cond[o.id].reserve if o.id in self.p4.cond else o.fatigue, 2), round(self.p4.cond[n.id].reserve if n.id in self.p4.cond else n.fatigue, 2)))
        self.p4.stats['rot_' + why] += 1
    def rested_long_enough(self, q):
        t, why = self.p4.exit.get(q.id, (-10 ** 9, ''))
        return why != 'pace' or self.s.live_ms - t >= 1000. * ROT['min_rest_s']
    def reinstate_specialists(self):
        s = self.s
        for team in ('A', 'B'):
            for slot, role in ((10, 'keeper'), (11, 'archer')):
                sp = s.players[f'{team}{slot}']
                if sp.active or not sp.available or sp.injured or sp.disqualified or sp.exclusion_ms > 0: continue
                stand = next((p for p in s.players.values() if p.team == team and p.active and p.role == role and p.id != sp.id), None)
                if stand is None or stand.frozen(s.now): continue
                do_sub(self, stand, sp, 'specialist_back'); stand.role = 'field'; sp.role = role
    def rot_reserve(self, p):
        c = self.p4.cond.get(p.id); return c.reserve if c else p.fatigue
    def rotate(self):
        s = self.s; budget = ROT['break_swaps'] if s.phase == Phase.BREAK else ROT['max_swaps']; over = pace_max_ms(self)
        for team in ('A', 'B'):
            held = {getattr(self, 'restart_taker', None), (s.restart.taker if s.restart else None)}      # the player who is to take the restart stays on
            field = [p for p in s.players.values() if p.team == team and p.active and p.role == 'field' and s.ball.carrier != p.id and p.id not in held and not p.frozen(s.now) and p.exclusion_ms <= 0]
            bench = [p for p in s.players.values() if p.team == team and not p.active and p.available and not p.injured and not p.disqualified and p.exclusion_ms <= 0 and p.role == 'field']
            if not bench: continue
            swaps = 0; R = lambda p: rot_reserve(self, p); M = self.p4.mins
            # 1. tired players, and starters ahead of their minutes pace, come off
            need = [p for p in field if R(p) <= ROT['out'] or (is_starter(p.id) and M[p.id] > over)]
            need.sort(key=lambda p: (R(p) > ROT['out'], R(p)))
            for o in need:
                if swaps >= budget or not bench: break
                ok = [q for q in bench if R(q) >= ROT['back'] and (not is_starter(q.id) or (M[q.id] <= over and rested_long_enough(self, q)))]
                if is_starter(o.id) and R(o) > ROT['out']: ok = [q for q in ok if not is_starter(q.id)]      # a pace rest is covered by a non-starter
                if not ok: ok = [q for q in bench if R(q) > R(o) + .15 and R(q) > ROT['out']] if R(o) <= ROT['out'] else []
                if not ok: continue
                n = max(ok, key=lambda q: (is_starter(q.id) and R(o) <= ROT['out'], R(q)))
                do_sub(self, o, n, 'tired' if R(o) <= ROT['out'] else 'pace'); bench.remove(n); field.remove(o); swaps += 1
            # 2. rested starters (>= back) who are under pace come back for a non-starter on the field
            for n in sorted([q for q in bench if is_starter(q.id) and R(q) >= ROT['back'] and M[q.id] <= over and rested_long_enough(self, q)], key=lambda q: M[q.id]):
                if swaps >= budget: break
                subs = [p for p in field if not is_starter(p.id)]
                if not subs: break
                o = min(subs, key=lambda p: R(p)); do_sub(self, o, n, 'return'); field.remove(o); swaps += 1
    def auto_substitutions(self):
        s = self.s
        if getattr(self, 'p4', None) is None or 'rotation' not in S.on: return orig['auto'](self)
        if s.phase not in (Phase.LIVE, Phase.DEAD, Phase.AWARD, Phase.BREAK): return
        for team in ('A', 'B'):          # Pocket's slot refill after an injury or exclusion, kept; its fatigue-based rotation is replaced
            low = s.ends[team] == 0; gatex = 75 if low else 25
            bench = [p for p in s.players.values() if p.team == team and not p.active and p.available and not p.injured and not p.disqualified and p.exclusion_ms <= 0]
            debt = sum(d['permanent'] or d['remaining'] > 0 for d in self.e.debts if d['team'] == team)
            activefield = [p for p in s.players.values() if p.team == team and p.active and p.role == 'field']
            if len(activefield) < 10 - debt and bench:
                p = max(bench, key=lambda p: (is_starter(p.id) and rot_reserve(self, p) >= ROT['back'], rot_reserve(self, p)))
                p.role = 'field'; p.x = gatex; p.y = .1 if low else 99.9; p.active = True; self.e.slot_fill(p); self.e.emit('slot_return', '14.3;15.4', player=p.id)
        if s.phase in (Phase.DEAD, Phase.BREAK): reinstate_specialists(self); rotate(self)

    def step(self):
        p4 = getattr(self, 'p4', None)
        if p4 is None: return orig['step'](self)
        t0 = self.s.now
        if 'jump' in S.on:
            plan_jumps(self); fire_jumps(self, self.dt)
        orig['step'](self)
        if 'condition' in S.on: condition_post(self, max(0, self.s.now - t0))
        s_ = self.s
        if s_.phase == Phase.LIVE and s_.ball.carrier is not None and S.tend:
            ct = s_.players[s_.ball.carrier].team
            for p in s_.players.values():
                if not p.active or p.role != 'field': continue
                T = S.tend.get(p.id)
                if T is None: continue
                sg = s_.attack_sign(p.team); u = sg * (p.x - s_.ends[p.team]); st = 'att' if ct == p.team else 'def'
                if st == 'att' and s_.ball.carrier == p.id: st = 'carry'
                a = self.p4.pos_acc.setdefault((T.pos, st), [0, 0., 0., 0.]); a[0] += 1; a[1] += u; a[2] += abs(p.y - 50); a[3] += s_.ball.x * 0 + sg * (s_.ball.x - s_.ends[p.team]) - u
        dl = self.s.live_ms - self.p4.last_live; self.p4.last_live = self.s.live_ms
        if dl > 0:
            for p in self.s.players.values():
                if p.active: self.p4.mins[p.id] += dl
                elif p.available and not p.injured: self.p4.off[p.id] += dl
        if 'rotation' in S.on:
            for p in self.s.players.values():
                if not p.active and p.id in self.p4.cond: p.fatigue = clamp(self.p4.cond[p.id].reserve, .15, 1.)

    # ---------------------------------------------------------------- release delay by pose
    def with_delay(fn, kind_default):
        def wrapped(self, p, *args, **kw):
            execute = kw.get('execute', args[-1] if args and isinstance(args[-1], bool) else False)
            if execute or 'pose' not in S.on or getattr(self, 'p4', None) is None: return fn(self, p, *args, **kw)
            kind = (args[1] if len(args) > 1 and isinstance(args[1], str) else kw.get('kind', kind_default))
            t = thrower(self, p, kind); pz = pose(self, p); d = (T.release_delay(t, self.p4.shape, pz) if kind != 'kick' else K.kick_delay(t, self.p4.shape, pz, 'punt'))
            bh = p.a.ball_handling; saved = self.assume['pass_release_ms']
            factor = (1.35 - .5 * bh) if fn.__name__ == 'make_pass' else (1.6 - .5 * p.a.kicking)
            self.assume['pass_release_ms'] = 1000. * d / factor
            try: out = fn(self, p, *args, **kw)
            finally: self.assume['pass_release_ms'] = saved
            self.p4.stats['pose_' + pz] += 1
            return out
        wrapped.__name__ = fn.__name__; return wrapped

    Match.__init__ = init; Match.step = step; Match.auto_substitutions = auto_substitutions
    PT.install(CO, S)
    RS.install(CO, S)
    # Pocket 2.0 arrow_decisions loop: its early `return`s (interval, ammunition, carrier on its own team...) end the whole function, so when team A is
    # processed first and holds the ball, team B's Archer is never evaluated - it can never fire.  Evaluate each team on its own.
    Match = CO.match.Match; o_ad = Match.arrow_decisions
    def arrow_decisions(self):
        if 'archerfix' not in S.on or self.no_archery: return o_ad(self)
        s = self.s
        arch = {tm: next((p for p in s.players.values() if p.team == tm and p.active and p.role == 'archer'), None) for tm in ('A', 'B')}
        for tm in ('A', 'B'):
            other = arch['B' if tm == 'A' else 'A']
            if other is not None: other.active = False
            hook = getattr(S, 'ad_hook', None); undo = hook(self, tm) if hook else None     # PRISM drive mode: the archer sees its belief of the field
            try: o_ad(self)
            finally:
                if undo: undo()
                if other is not None: other.active = True
    Match.arrow_decisions = arrow_decisions

    # ---- platform archer: static x,y behind the own goal, elevated, facing the opposing goal -----------------------------------------------
    S.fz = Counter(); S.fz_stat = Counter()
    if PLAT:
        Engine.platform = True
        o_lane = Engine.archer_in_lane; Engine.archer_in_lane = lambda self, p: True
        def update_archers(self, ms):
            s = self.s
            for p in s.players.values():
                if not p.active or p.role != 'archer': continue
                low = s.ends[p.team] == 0
                if not hasattr(p, '_h0'): p._h0 = p.a.height; p.a.height = (PLAT_H + .72 * p._h0) / .72   # arrow origin z = H + .72 x body height; archers are not in the contact set
                p.x = -PLAT_SET if low else 100 + PLAT_SET; p.y = 50.; p.vx = p.vy = 0.
                if not p.eligible(s.now): continue
                q = s.quivers[p.team]
                if q.loaded == 0 and q.spent < q.allocation and q.reload_until < 0: self.e.reload(p.id)
        Match.update_archers = update_archers
    if QUIVER_POSS:
        o_no2 = Engine.new_owner
        def new_owner_q(self, team, reason):
            changed = self.s.owner != team
            r = o_no2(self, team, reason)
            if changed:
                for t, q in self.s.quivers.items():
                    q.spent = 0; q.loaded = 5; q.reload_until = -1; S.fz_stat['quiver_refills'] += 1
            return r
        Engine.new_owner = new_owner_q
    S.fz_diag = Counter()
    if os.environ.get('FZ_DIAG', '0') == '1':
        o_fzd = Engine.freeze
        def freeze_diag(self, pid, arrow=None, panel=True, direct=True, in_range=True):
            st = self.s; p = st.players[pid]; c = S.fz_diag; c['calls'] += 1
            broad = self.config.get('ruleset', '1.0.1') == '1.0.2'
            if st.phase == Phase.FLIGHT or not self.live(): c['not_live_phase_%s' % st.phase.value] += 1
            else:
                if not panel: c['not_panel'] += 1
                if not direct: c['not_direct'] += 1
                if not in_range: c['out_of_range'] += 1
                if not self.eligible(p): c['ineligible'] += 1
                if p.role == 'keeper' and self.zone(p.x, p.y) == st.own_zone(p.team): c['protected_keeper'] += 1
                if not (st.now > p.immune_until): c['immune'] += 1
                if not (broad or st.ball.carrier == pid): c['not_carrier_rule'] += 1
            r = o_fzd(self, pid, arrow, panel, direct, in_range); c['frozen' if r else 'inert'] += 1; return r
        Engine.freeze = freeze_diag
    if FREEZE_CAP > 0:
        o_no = Engine.new_owner; o_fz = Engine.freeze
        def new_owner(self, team, reason):
            if self.s.owner != team: S.fz.clear()
            return o_no(self, team, reason)
        def freeze(self, pid, arrow=None, panel=True, direct=True, in_range=True):
            tm = self.s.players[pid].team
            if S.fz[tm] >= FREEZE_CAP:
                if self.live(): self.emit('freeze_cap', 'proto:freeze_cap', player=pid, arrow=arrow); S.fz_stat['capped'] += 1
                return False
            ok = o_fz(self, pid, arrow, panel, direct, in_range)
            if ok: S.fz[tm] += 1
            return ok
        Engine.new_owner = new_owner; Engine.freeze = freeze
    # Optional arrow-speed override (m/s). Default 0 = stock Pocket 2.0 (30 m/s limit). Canon decision pending:
    # at stock speed arrows essentially never freeze anyone; see ARCHER_NOTES.md.
    ARROW_V = float(os.environ.get('ARROW_V', '0') or 0)
    if ARROW_V > 0:
        o_ad2 = Match.arrow_decisions
        def arrow_decisions_v(self):
            self.cfg['pocket']['arrow_limit'] = ARROW_V; self.e.pocket['arrow_limit'] = ARROW_V
            for p in self.s.players.values():
                if p.role == 'archer': p.a.archery_release_speed = ARROW_V
            return o_ad2(self)
        Match.arrow_decisions = arrow_decisions_v
    # Drag-aware arrow lead (flag `arrowlead`).  Pocket 2.0 leads a moving target with a drag-FREE flight time and only corrects drag along the
    # archer->target line, so the (decelerating) arrow arrives late and lands behind a sideways runner.  Here the launch vector is re-solved against the
    # real dragged flight time (8 lead iterations, each re-aiming gravity drop), then the engine's own aim noise is applied.  Falls back to the engine aim
    # if no solution.  Same arc (low/high) the engine's obstacle check picked.
    Engine = CO.engine.Engine; geo = CO.geometry; o_sa = Engine.shoot_arrow
    S.arrow_stats = Counter(); S.arng = random.Random(4242)
    def real_flight(o, launch, dist_h, g, k, dt=.005):
        vx, vy, vz = launch; x = y = 0.; z = o[2]; t = 0.; d = math.exp(-k * dt)
        while t < 6:
            x += vx * dt; y += vy * dt; z += vz * dt - .5 * g * dt * dt; vx *= d; vy *= d; vz = (vz - g * dt) * d; t += dt
            if math.hypot(x, y) >= dist_h: return t, z
        return None, z
    def shoot_arrow(self, pid, target, velocity, origin=None):
        if 'arrowlead' not in S.on or target == 'ball' or origin is None: return o_sa(self, pid, target, velocity, origin)
        s = self.s; p = s.players[pid]; t = s.players[target]; A = getattr(self, 'assume', None) or {}
        g = A.get('gravity', 9.81); k = A.get('arrow_drag', .06); speed = math.sqrt(sum(v * v for v in velocity))
        o = origin; tz = t.z + .55 * t.a.height; ox_el = math.atan2(velocity[2], math.hypot(velocity[0], velocity[1]))
        d0 = math.dist((o[0], o[1]), (t.x, t.y)); best = None
        for high in (False, True):
            T = None; zaim = tz; ok = True; sol = None
            first = geo.ballistic(o, (t.x, t.y, zaim), speed, g, high)
            if not first: continue
            T = first[1]
            for _ in range(8):
                tx, ty = t.x + t.vx * T, t.y + t.vy * T; dh = math.hypot(tx - o[0], ty - o[1]); zaim = tz
                for _ in range(6):
                    sol = geo.ballistic(o, (tx, ty, zaim), speed, g, high)
                    if not sol: ok = False; break
                    Tn, zarr = real_flight(o, sol[0], dh, g, k)
                    if Tn is None: ok = False; break
                    zaim += tz - zarr
                if not ok: break
                T = Tn
            if not ok or not sol: continue
            el = math.atan2(sol[0][2], math.hypot(sol[0][0], sol[0][1]))
            if best is None or abs(el - ox_el) < best[0]: best = (abs(el - ox_el), sol[0], T, high)
        if best is None: S.arrow_stats['fallback'] += 1; return o_sa(self, pid, target, velocity, origin)
        _, (vx, vy, vz), T, high = best
        sig = (.0008 + .009 * (1 - p.a.archery_accuracy)) * A.get('arrow_error_scale', 1.)
        az = math.atan2(vy, vx) + S.arng.gauss(0, sig); el = math.atan2(vz, math.hypot(vx, vy)) + S.arng.gauss(0, sig)
        noisy = (speed * math.cos(el) * math.cos(az), speed * math.cos(el) * math.sin(az), speed * math.sin(el))
        ar = o_sa(self, pid, target, noisy, origin)
        if ar:
            S.arrow_stats['aware'] += 1
            self.emit('arrow_lead', 'proto:drag_aware_lead', arrow=ar.id, real_flight=round(T, 3), range=round(d0, 1), high=high, speed=round(speed, 1))
        return ar
    Engine.shoot_arrow = shoot_arrow
    Match.aim_error = lambda self, vel, skill: vel if ('throw' in S.on and getattr(self, 'p4', None)) else orig['aim'](self, vel, skill)
    Match.make_pass = with_delay(orig['make_pass'], 'pass'); Match.make_shot = with_delay(orig['make_shot'], 'shot')
    if T.SPLIT:   # throw split: the thrower picks the ball speed (flight time target), within what his Throw Power allows; no cap
        PASS_FLIGHT_S = float(os.environ.get('PASS_FLIGHT_S', '0.9')); SHOT_FLIGHT_S = float(os.environ.get('SHOT_FLIGHT_S', '0.4')); SHOT_MIN = float(os.environ.get('SHOT_MIN_SPEED', '45'))
        o_plan, o_shot2, o_init2 = Match.plan_pass, Match.make_shot, Match.__init__
        def plan_pass2(self, origin, passer, q, kind, lag=0., speed=None):
            if speed is None:
                vmax = T.v_rel_max(thrower(self, passer, 'pass')) * .98; d = norm(q.x - origin[0], q.y - origin[1]); base = self.cfg['pocket']['pass_speed' if kind == 'pass' else 'ball_speed']
                speed = min(vmax, max(base, d / PASS_FLIGHT_S))
            return o_plan(self, origin, passer, q, kind, lag, speed)
        def make_shot2(self, p, execute=False):
            if not execute: return o_shot2(self, p, execute)
            pc = self.cfg['pocket']; old = pc['ball_speed']; d = abs(self.s.attack_goal(p.team) - p.x); vmax = T.v_rel_max(thrower(self, p, 'shot')) * .98
            pc['ball_speed'] = min(vmax, max(SHOT_MIN, d / SHOT_FLIGHT_S))
            try: return o_shot2(self, p, execute)
            finally: pc['ball_speed'] = old
        def init2(self, config=None):
            o_init2(self, config); self.e.pocket['ball_limit'] = self.cfg['pocket']['ball_limit'] = 1e9
        Match.plan_pass, Match.make_shot, Match.__init__ = plan_pass2, make_shot2, init2
    if os.environ.get('PRISM_FIELD', '0') == '1': PFIELD.install(CO, S, lambda: S.seed)   # v0.2: ball carrier perceives opponents
    if os.environ.get('PRISM_MANEUVERS', '0') == '1': PMAN.install(CO, S, lambda: S.seed)   # v0.3: carry poses + evasion maneuvers on the carrier
    if os.environ.get('PRISM', '0') == '1': PRISM.install(CO, S, lambda: S.seed)   # shadow mode: logs beliefs, changes no decision
    if CV2: import catch_v2 as CATCH2; CATCH2.install(CO, S)
    if JSP: import judge_split_v0 as JSPLIT; JSPLIT.install(CO, S)   # v0.7: Finishing / Defender Duel (the rest of the split sits in the field, keeper and maneuver modules)
    if os.environ.get('HAND_FIGHT', '0') == '1': import hand_fight_v0 as HFIGHT; HFIGHT.install(CO, S)   # off-ball hand fighting (needs CATCH_V2 for the pillar logit)
    if os.environ.get('PRISM_OFFACT', '0') == '1': import offball_actions_v0 as OFFACT; OFFACT.install(CO, S)   # v0.7: the five off-ball actions (installs after the field layer so it wraps its targets)
    if KPK or (CV2 and os.environ.get('PRISM_CATCHERS', '1') == '1'): import prism_keeper_v0 as PKEEP; PKEEP.install(CO, S, lambda: S.seed)   # v0.5: Keepers perceive the free ball
    if os.environ.get('KP_TRACE'): import kp_trace; kp_trace.install(CO)
    RV03.install(P)
    RV03.install_nokick(P)
    BLK.install(P)
    BNC.install(P)
    return P

# ======================================================================================== roster + running
def annotate(nm, slots, team):
    for slot, a in slots:
        arch, margin, _ = PT.classify(a['position'], a['ratings']); d = nm[f'{team}{slot}']; d['report_arch'] = arch; d['arch_margin'] = margin

def make_rosters(rows_a=None, rows_b=None, seed=1):
    """returns ROSTER_OVERRIDES dict, extras, names"""
    rng = random.Random(seed)
    def gen_rows(team):
        base = [('QB', 3), ('RB', 2), ('WR', 3), ('TE', 1), ('OL', 3), ('LB', 3), ('CB', 3), ('S', 2), ('K', 1), ('A', 1)]
        rows = []; n = 0
        for pos, k in base:
            for i in range(k):
                n += 1; rows.append(dict(name=f'{team} {pos}{i + 1}', position=pos, overall=round(rng.uniform(62, 86), 1)))
        return rows
    over, extras, names = {}, {}, {}
    for team, rows in (('A', rows_a or gen_rows('A')), ('B', rows_b or gen_rows('B'))):
        sl = G.build_team(rows); o, e, n = G.to_pocket_overrides(sl, team); annotate(n, sl, team); over.update(o); extras.update(e); names.update(n)
    return over, extras, names

def rosters_from_generated(path_a, path_b):
    """Pre-generated attribute sheets (columns as in *_generated.csv: ratings 0-100, height_m, mass_kg, role starter|bench, archetype).  Order in the file: starters (ten field, keeper, archer) then bench.
    Bench keeper/archer cannot be used by Pocket's field-slot bench, so those slots are filled with 'Reserve' utility players at 0.60."""
    import csv
    RK = ('speed', 'agility', 'strength', 'balance', 'stamina', 'durability', 'injury', 'tackling', 'blocking', 'contact_resistance', 'ball_handling', 'catching', 'awareness', 'throw_power', 'throw_accuracy', 'kick_power', 'kick_accuracy', 'jump', 'keeper_skill', 'archery_accuracy')
    over, extras, names = {}, {}, {}
    for team, path in (('A', path_a), ('B', path_b)):
        ath = []
        for r in csv.DictReader(open(path, newline='', encoding='utf-8')):
            arch = r['archetype']; role = 'keeper' if arch == 'keeper' else 'archer' if arch == 'archer' else 'field'
            ath.append(dict(name=r['name'], position=r['position'], archetype=arch, role=role, overall=float(r['overall']) / 100., height_m=float(r['height_m']), mass_kg=float(r['mass_kg']), reach_m=(float(r['reach_m']) if r.get('reach_m') not in (None, '') else None),
                            ratings={k: float(r[k]) / 100. for k in RK}, notes=[], starter=(r.get('role') == 'starter')))
        starters = [a for a in ath if a['starter']]; bench = [a for a in ath if not a['starter']]
        field = [a for a in starters if a['role'] == 'field']; keeper = next(a for a in starters if a['role'] == 'keeper'); archer = next(a for a in starters if a['role'] == 'archer')
        bf = [a for a in bench if a['role'] == 'field']; n = 0
        while len(bf) < 10: n += 1; bf.append(G.generate(f'Reserve {team}{n}', 'utility', .60))
        slots = [(i, field[i]) for i in range(10)] + [(10, keeper), (11, archer)] + [(12 + i, bf[i]) for i in range(10)]
        o, e, nm = G.to_pocket_overrides(slots, team); annotate(nm, slots, team); over.update(o); extras.update(e); names.update(nm)
    return over, extras, names

def run(P, over, extras, names, off=(), shape='sphere', seed=1, short=False, progress=False):
    C2.cl.BASE_HAZ = 1.7e-4 * INJ_HAZ
    S.tend = {pid: PT.Tend(n['position'] if n['position'] in PT.POSITIONS else 'TRK', n.get('report_arch', '')) for pid, n in names.items()}
    S.on = (set(SYSTEMS) - set(off)) | {o for o in off if o.startswith(('tend_no', 'rs_no'))}; S.shape = shape; S.extras = extras if 'roster' in S.on or True else {}; S.names = names; S.seed = seed; S.prism_r = PRAT.assign(over, names) if os.environ.get('PRISM_FIELD', '0') == '1' else None
    st = RV03.settings(dict(P.SETTINGS)); st['save_events'] = False
    if not short: st.update(period_seconds=600, periods=4)
    # Pocket's settings for the new speed scale: nominal player speed is only a default; the roster overrides carry real speeds.
    P.ROSTER_OVERRIDES = P.validate_roster(over) and over
    t = time.time(); result, log = P.run_match(st, seed=seed, progress=progress); el = time.time() - t
    return result, log, el

def box(result, log, names, S_=S):
    sc = result['score']; per = result['measures_final']['finishing'] if 'measures_final' in result else {}
    ev = Counter(e['event'] for e in log)
    lines = [f"Score A {sc['A']} - B {sc['B']}   ({result['result'].get('method')}, winner {result['result'].get('winner')})", f"periods {result['period']}  live {result['live_s']:.0f}s  dead {result['dead_s']:.0f}s  active fraction {result['active_fraction']:.2f}"]
    rel = Counter(); comp = Counter()
    for e in log:
        if e['event'] == 'release': rel[(e['data']['player'][0], e['data'].get('kind'))] += 1
    lines.append('releases ' + ', '.join(f'{k[0]} {k[1]}: {v}' for k, v in sorted(rel.items())))
    for team in 'AB':
        f = per.get(team, {})
        lines.append(f"{team}: possessions {f.get('possessions')}, finish attempts {f.get('finish_attempts')}, shots {f.get('shots')}, carry intents {f.get('carry_intents')}, goals from attempts {f.get('goals_from_finish_attempts')}, points/possession {f.get('points_per_possession')}")
    keys = ('control', 'possession_change', 'tackle_count', 'strip', 'grounded', 'touch', 'goal', 'foul', 'freeze', 'injury', 'substitution', 'pass_plan', 'release', 'boundary', 'strike')
    lines.append('events ' + ', '.join(f'{k} {ev.get(k, 0)}' for k in keys))
    return '\n'.join(lines)

def rotation_report(m, names):
    lines = []; M = m.p4.mins
    for team in 'AB':
        ids = [f'{team}{i}' for i in range(22)]
        st = [i for i in ids if int(i[1:]) < 10]
        mins = lambda i: M[i] / 60000.
        lines.append(f"Team {team}: starter field players (slots 0-9) minutes: " + ', '.join(f"{names[i]['name']} {mins(i):.1f}" for i in st))
        lines.append(f"   mean {sum(mins(i) for i in st) / 10:.1f}  min {min(mins(i) for i in st):.1f}  max {max(mins(i) for i in st):.1f}   | Keeper {names[team + '10']['name']} {mins(team + '10'):.1f}   Archer {names[team + '11']['name']} {mins(team + '11'):.1f}")
        lines.append("   bench: " + ', '.join(f"{names[i]['name']} {mins(i):.1f}" for i in ids[12:] if mins(i) > 0))
    sub = Counter(r[3] for r in m.p4.rot_log); lines.append(f"rotation swaps {dict(sub)}  injuries {m.p4.stats['injuries']}")
    return '\n'.join(lines)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--a'); ap.add_argument('--b'); ap.add_argument('--ga'); ap.add_argument('--gb'); ap.add_argument('--seed', type=int, default=1); ap.add_argument('--short', action='store_true'); ap.add_argument('--off', default='')
    ap.add_argument('--shape', default='sphere'); ap.add_argument('--out', default=os.path.join(HERE, 'rebase_results'))
    a = ap.parse_args()
    P = install(load_pocket())
    rows_a = G.read_csv(a.a) if a.a else None; rows_b = G.read_csv(a.b) if a.b else None
    over, extras, names = rosters_from_generated(a.ga, a.gb) if a.ga and a.gb else make_rosters(rows_a, rows_b, a.seed)
    off = [x for x in a.off.split(',') if x]
    result, log, el = run(P, over, extras, names, off, a.shape, a.seed, a.short)
    print(box(result, log, names)); print(rotation_report(S.last, names)); print(f'wall time {el:.1f}s')
    os.makedirs(a.out, exist_ok=True)
    json.dump(dict(score=result['score'], result=result['result'], off=off, shape=a.shape, seed=a.seed, names=names, wall_s=el), open(os.path.join(a.out, f'pocket4_game_seed{a.seed}.json'), 'w'), indent=1, default=str)
    return result, log

if __name__ == '__main__': main()
