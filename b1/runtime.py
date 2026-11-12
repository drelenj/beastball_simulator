"""Dedicated-worker adapters to accepted PRISM and Pocket 4 kernels."""
import copy
import hashlib
import json
import math
import os
from pathlib import Path
import sys
from .core import AthleteView, BeliefState, Contact, MotorCommand

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT

ALL_FEATURE_ENV = (
    'PLAT', 'RULESET', 'ARCH_RMIN', 'ARCH_RMAX', 'ARCH_NEAR',
    'KEEPER_STEP_FRAC', 'NET_R', 'KEEPER_FT', 'PRISM_KEEPER',
    'CATCH_V2', 'PRISM_CATCHERS', 'PRISM_JSPLIT', 'PRISM_I',
    'PRISM_FIELD', 'PRISM_DEF', 'PRISM_BOUNDED', 'PRISM_MANEUVERS',
    'PRISM_OFFBALL', 'PRISM_TEAMVIEW', 'PRISM_FREEVIEW', 'PRISM_OFFACT',
    'PRISM', 'HAND_FIGHT', 'RULES_V03', 'RV03_SCRIM', 'RV03_NOKICK',
    'BLOCK_OPTION', 'BOUNCE_OPTION', 'THROW_SPLIT',
)


def digest(v):
    return hashlib.sha256(json.dumps(v, sort_keys=True, separators=(',', ':'),
                                     allow_nan=False).encode()).hexdigest()


def forbidden(*args, **kwargs):
    raise RuntimeError('legacy tactical controller reached')


class PhysicalExecutionPort:
    def __init__(self, seed):
        # Only call in a dedicated process: the inherited loader installs classes.
        sys.path.insert(0, str(REPO))
        # Reproduce the accepted B0-P4-DEFAULT feature profile without importing
        # any external evidence-packet helper.
        for key in ALL_FEATURE_ENV:
            os.environ.pop(key, None)
        import pocket4_proto as X
        P = X.install(X.load_pocket())
        over, extras, names = X.make_rosters(seed=seed)
        self.roster_overrides, self.roster_extras, self.roster_names = over, extras, names
        X.S.tend = {pid: X.PT.Tend(n['position'] if n['position'] in X.PT.POSITIONS else 'TRK', n.get('report_arch', '')) for pid, n in names.items()}
        X.S.on = set(X.SYSTEMS)
        X.S.shape, X.S.extras, X.S.names, X.S.seed, X.S.prism_r = 'sphere', extras, names, seed, None
        P.ROSTER_OVERRIDES = P.validate_roster(over) and over
        self.m = P.CORE.match.Match(P.configuration(dict(P.SETTINGS), seed, copy.deepcopy(P.CALIBRATION)))
        self.types = P.CORE.types
        s = self.m.s
        s.phase, s.now, s.owner = self.types.Phase.LIVE, 1000, 'A'
        s.restart = s.recovery = s.reconstruction = s.advantage = s.penalty = None
        s.opening_touched = True
        s.opening_deadline = None
        for p in s.players.values():
            p.active = False
        a = s.players['A0']
        a.active = True
        a.x, a.y, a.z, a.vx, a.vy, a.vz = 40., 50., 0., 0., 0., 0.
        a.facing = (1., 0.)
        a.next_action = 0
        # Scenario entities are real engine bodies, and perception projects
        # only this authoritative state into PRISM's sensor interface.
        teammate, defender = s.players['A1'], s.players['B0']
        teammate.active = defender.active = True
        teammate.x, teammate.y, teammate.z = 55., 50., 0.
        teammate.vx = teammate.vy = teammate.vz = 0.
        defender.x, defender.y, defender.z = 47., 55., 0.
        defender.vx = defender.vy = defender.vz = 0.
        s.ball = self.types.Ball(mode=self.types.BallMode.CONTROLLED, carrier=a.id, control_time=0, last_touch='A', scoring=True)
        self.m.e.follow_carrier()
        for name in ('carrier_decision', 'arrow_decisions', 'route_receiver', 'c4c2_targets', 'step'):
            setattr(self.m, name, forbidden)
        for policy in self.m.pol.values():
            for name in ('targets', 'pass_choice', 'pass_ranked'):
                setattr(policy, name, forbidden)
        self.pending = None
        self.records = []

    def advance(self, until_ms):
        s = self.m.s
        if until_ms < s.now or until_ms-s.now > 10000:
            raise ValueError('invalid bounded advance')
        while s.now < until_ms:
            if self.pending and s.now >= self.pending.release_ms:
                c = self.pending
                a = s.players[c.intent.athlete]
                if not self.m.e.eligible(a) or s.ball.carrier != a.id:
                    self.records.append({'kind':'outcome', 'command_id':c.command_id, 'status':'interrupted', 'time_ms':s.now})
                else:
                    ok = self.m.e.release(a.id, c.desired_velocity, 'pass', c.intent.target, False)
                    self.records.append({'kind':'outcome', 'command_id':c.command_id, 'status':'released' if ok else 'rejected', 'time_ms':s.now,
                                         'ball_velocity':[s.ball.vx,s.ball.vy,s.ball.vz]})
                self.pending = None
            dt = min(10, until_ms-s.now)
            if self.pending:
                dt = min(dt, self.pending.release_ms-s.now)
            events = self.m.advance_ball(dt, {})
            if events:
                self.records.append({'kind':'kernel_event','time_ms':s.now,
                                     'events':events,'carrier':s.ball.carrier,
                                     'ball_mode':str(s.ball.mode)})
            s.now += dt
            self.records.append({'kind':'physical_sample', 'time_ms':s.now,
                                 'ball':[s.ball.x,s.ball.y,s.ball.z],
                                 'velocity':[s.ball.vx,s.ball.vy,s.ball.vz]})
        return tuple(self.records)


class CommandIngress:
    def __init__(self, port): self.port = port

    def submit_batch(self, intents):
        """Canonical ingestion from one snapshot; atomic single-resource bundles.

        M1 supports only ball_control_release. Other resource requests fail at
        the typed boundary. A second uncommitted request is explicitly rejected;
        the general queued-bundle implementation is not claimed by this slice.
        """
        ids = [i.intent_id for i in intents]
        if len(ids) != len(set(ids)):
            raise ValueError('duplicate intent identity')
        return tuple((i.intent_id,self.submit(i)) for i in sorted(intents,key=lambda i:(i.decided_ms,i.intent_id)))

    def submit(self, intent):
        p = self.port
        s = p.m.s
        if intent.athlete != 'A0' or intent.decided_ms != s.now:
            return {'status':'rejected', 'reason':'invalid_actor_or_time'}
        if intent.kind == 'retain':
            return {'status':'accepted', 'outcome':'retained', 'intent_id':intent.intent_id}
        if intent.kind == 'no_action':
            return {'status':'accepted', 'outcome':'no_action', 'intent_id':intent.intent_id}
        if intent.kind != 'pass' or intent.aim is None or s.ball.carrier != intent.athlete:
            return {'status':'rejected', 'reason':'infeasible'}
        if p.pending:
            return {'status':'rejected', 'reason':'resource_busy'}
        a = s.players[intent.athlete]
        dx, dy = intent.aim[0]-a.x, intent.aim[1]-a.y
        length = math.hypot(dx,dy)
        if length < 1e-9:
            return {'status':'rejected', 'reason':'zero_aim'}
        # Historical desired pass speed; Pocket 4 release performs its sampler.
        speed = float(p.m.cfg['pocket']['pass_speed'])
        velocity = (dx/length*speed, dy/length*speed, 2.)
        delay = math.ceil(p.m.assume['pass_release_ms']*(1.35-.5*a.a.ball_handling))
        c = MotorCommand(intent.intent_id+'/command', intent, s.now, s.now+delay, velocity)
        p.pending = c
        return {'status':'accepted', 'command':c}


class ObservationProjector:
    def __init__(self, seed, athlete, prism_ratings):
        from prism_archer_v0 import ArcherPrism
        self.prism = ArcherPrism(f'b1-{seed}-A0', prism_ratings['awareness'],
                                 athlete.a.decision_speed, {'vel_mode':'lsq'})
        self.prism.apply_ratings(prism_ratings)
        self.teams = {}
        self.athlete_id = athlete.id

    def capture(self, time_ms, physical_state):
        athlete = physical_state.players[self.athlete_id]
        bodies = []
        for p in sorted(physical_state.players.values(), key=lambda p:p.id):
            if not p.active or p.id == athlete.id:
                continue
            self.teams[p.id] = p.team
            bodies.append({'id':p.id,'x':p.x,'y':p.y,'z':p.z,
                           'h':p.a.height,'r':p.radius,'vx':p.vx,'vy':p.vy})
        facing = math.atan2(athlete.facing[1], athlete.facing[0])
        eye = (athlete.x, athlete.y, athlete.z + .72*athlete.a.height)
        self.prism.tick(time_ms/1000, eye, facing, bodies, None)

    def deliver(self, time_ms, physical_state, own_feedback=()):
        self.prism.deliver(time_ms/1000)
        contacts = tuple(Contact(pid, self.teams[pid], *b.at(time_ms/1000), int(b.t*1000))
                         for pid in sorted(self.teams) if (b := self.prism.bget(pid)) is not None)
        oid = f'm1/{time_ms:016d}/A0/perception/0'
        athlete = physical_state.players[self.athlete_id]
        holds_ball = physical_state.ball.carrier == athlete.id
        view = AthleteView(oid,athlete.id,athlete.team,time_ms,
                           float(athlete.x),float(athlete.y),holds_ball,contacts)
        return view, BeliefState(oid+'/belief',oid,contacts,tuple(own_feedback),
                                 int(round(self.prism.P['memory_s']*1000)))
