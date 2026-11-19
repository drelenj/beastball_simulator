"""RB-3.9a PROVISIONAL (owner CANON ruling 18 Nov 2026 evening), native-rb/3 only.

Scrimmage set formation for every scrimmage and snap40 (tosses unchanged):
- Spot: y = 50; x clamped to [SPOT_MIN_X, SPOT_MAX_X] (10 m from either end line; field length 100 m).
- Snapper at the spot: the tackled player if he is an eligible field player of the team, else the
  eligible field player nearest the spot (tie-break by id).
- Designated receiver directly behind on y = 50, RECEIVER_DEPTH_M (5 m; 10 m on snap40).
- Neutral zone from the ball line toward the defense, NEUTRAL_ZONE_M deep (5 m; 20 m on snap40).
  Nobody in it at the snap except the nose tackle.
- Nose tackle (scrimmage awarded with a tackler, i.e. a first-tackle scrimmage or its retake): the
  tackler stands NOSE_TACKLE_M (2 m) in front of the ball on y = 50.
- Offense behind the ball line (at least 1 m); defense outside the neutral zone (0.5 m beyond it).
  Each player keeps his own y; only x moves, by the smallest amount needed.
Placement is procedural (engine), applied once per restart at the end of the step that awarded it.
Log only: 'scrimmage_formation' per formation and 'restart_repeat_report' when the same restart kind
is formed at the same spot 3 times in a row without a change of passive possession (never intervenes).
"""
import math

FIELD_LENGTH = 100.
SPOT_MIN_X, SPOT_MAX_X = 10., FIELD_LENGTH - 10.
RECEIVER_DEPTH_M = {'scrim': 5., 'snap40': 10.}
NEUTRAL_ZONE_M = {'scrim': 5., 'snap40': 20.}
NOSE_TACKLE_M = 2.
OFFENSE_BEHIND_M = 1.
DEFENSE_MARGIN_M = .5
WATCHDOG_REPEATS = 3


def install(co, cfg):
    if cfg.version != 'native-rb/3':
        return
    E = co.engine.Engine

    def eligible_field(s, p, team):
        return p is not None and p.active and p.team == team and p.role == 'field' and p.eligible(s.now)

    def place(self, p, x, y, spots):
        p.x = max(.6, min(FIELD_LENGTH - .6, x)); p.y = y; p.vx = p.vy = 0.; p.target = (p.x, p.y)
        port = getattr(self, 'rb_port', None)
        if port is not None: port.move[p.id] = (p.x, p.y)
        spots[p.id] = (round(p.x, 3), round(p.y, 3))

    def form(self):
        s = self.s; r = s.restart
        if r is None or r.kind not in RECEIVER_DEPTH_M or r.rs.get('formation') or s.phase.value != 'dead':
            return False
        team = r.team; other = s.other(team); sg = s.attack_sign(team)
        x0 = max(SPOT_MIN_X, min(SPOT_MAX_X, r.x)) if r.kind == 'scrim' else r.x
        r.x, r.y = x0, 50.; r.taker_spot = (x0, 50.); s.ball.x, s.ball.y = x0, 50.
        depth, zone = RECEIVER_DEPTH_M[r.kind], NEUTRAL_ZONE_M[r.kind]
        P = s.players
        sid = r.rs.get('snapper')
        if not eligible_field(s, P.get(sid), team):
            pool = [p for p in P.values() if eligible_field(s, p, team)]
            sid = min(pool, key=lambda p: (math.hypot(p.x - x0, p.y - 50.), p.id)).id if pool else None
        r.rs['snapper'] = sid
        rx = x0 - sg * depth
        pool = [p for p in P.values() if eligible_field(s, p, team) and p.id != sid]
        rid = min(pool, key=lambda p: (math.hypot(p.x - rx, p.y - 50.), p.id)).id if pool else None
        tid = r.rs.get('tackler') if r.kind == 'scrim' else None
        nid = tid if eligible_field(s, P.get(tid), other) else None
        spots = {}
        for p in sorted(P.values(), key=lambda p: p.id):
            if not p.active or p.role == 'archer':
                continue
            if p.id == sid: place(self, p, x0, 50., spots)
            elif p.id == rid: place(self, p, rx, 50., spots)
            elif p.id == nid: place(self, p, x0 + sg * NOSE_TACKLE_M, 50., spots)
            elif p.team == team:
                if sg * (p.x - x0) > -OFFENSE_BEHIND_M: place(self, p, x0 - sg * OFFENSE_BEHIND_M, p.y, spots)
                else: place(self, p, p.x, p.y, spots)
            else:
                if sg * (p.x - x0) < zone + DEFENSE_MARGIN_M: place(self, p, x0 + sg * (zone + DEFENSE_MARGIN_M), p.y, spots)
                else: place(self, p, p.x, p.y, spots)
        r.rs['formation'] = dict(snapper=sid, receiver=rid, receiver_xy=(rx, 50.), depth=depth, zone=zone, nose=nid, line_x=x0, spots=spots)
        self.emit('scrimmage_formation', 'RB-3.9', restart_id=r.native_id, kind=r.kind, reason=r.reason, team=team,
                  spot=[x0, 50.], snapper=sid, receiver=rid, receiver_spot=[rx, 50.], nose=nid, neutral_zone_m=zone)
        key = (r.kind, team, round(x0, 1)); wd = self.__dict__.setdefault('rb39_watchdog', dict(key=None, n=0, pp=None))
        wd['n'] = wd['n'] + 1 if key == wd['key'] and wd['pp'] == self.possession.pp else 1
        wd['key'], wd['pp'] = key, self.possession.pp
        if wd['n'] == WATCHDOG_REPEATS:
            self.emit('restart_repeat_report', 'RB-3.9-report', kind=r.kind, team=team, spot=[x0, 50.], repeats=wd['n'])
        return True
    E.rb_form_restart = form
