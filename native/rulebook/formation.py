"""RB-3.9a PROVISIONAL (owner CANON ruling 18 Nov 2026 evening), native-rb/3 only.

Scrimmage set formation for every scrimmage and snap40 (tosses unchanged):
- Spot: y = 50; x clamped to [SPOT_MIN_X, SPOT_MAX_X] (10 m from either end line; field length 100 m).
- Snapper at the spot: the tackled player if he is an eligible field player of the team, else the
  eligible field player nearest the spot (tie-break by id).
- Designated receiver directly behind on y = 50, RECEIVER_DEPTH_M (5 m; 10 m on snap40).
- Neutral zone from the ball line toward the defense, NEUTRAL_ZONE_M deep (5 m; 20 m on snap40).
  Nobody in it at the snap (RB-3.9 nose-tackle exception withdrawn in RB-3.10).
- RB-3.10 (owner, 18 Nov night): no nose tackle. ALL defenders are outside the neutral zone. The
  tackler (first-tackle scrimmage or its retake) lines up directly across the snapper on y = 50 at the
  near edge of the zone, outside it (interpretation; owner to confirm).
- RB-3.10 hold: nobody moves from the snap until it has travelled SNAP_HOLD_M (5 m) from the spot or
  any player touches it (a dropped or missed catch counts). Applied by the port (see hold_*).
- RB-3.10 receiver: default = the eligible field teammate nearest the receiver spot (tie by id); a team
  may designate any eligible field player (port.receiver_designation[team], a tactic hook).
- RB-3.10 lane: nobody other than snapper and receiver within LANE_HALF_WIDTH_M of y = 50 between them.
- RB-3.10 frozen players are unfrozen at the formation, with no thaw buffer and no freeze immunity.
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
SNAP_HOLD_M = 5.            # RB-3.10: the hold ends when the snap has travelled this far (or on a touch)
LANE_HALF_WIDTH_M = 2.     # RB-3.10: tunable half-width of the clear snap corridor
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
        # RB-3.10: frozen players are unfrozen with no thaw buffer and no immunity
        thawed = []
        for p in sorted(P.values(), key=lambda p: p.id):
            if p.active and p.role != 'archer' and p.frozen(s.now):
                thawed.append(p.id); p.freeze_until = -1; p.immune_until = -1
        # receiver: a team designation (tactic hook) if it names an eligible field player, else nearest
        port = getattr(self, 'rb_port', None); chosen = None; source = 'default_nearest'
        hook = (getattr(port, 'receiver_designation', None) or {}).get(team) if port is not None else None
        if hook is not None:
            want = hook(self.s, r) if callable(hook) else hook
            if want != sid and eligible_field(s, P.get(want), team): chosen, source = want, 'team_designation'
        if chosen is None:
            pool = [p for p in P.values() if eligible_field(s, p, team) and p.id != sid]
            chosen = min(pool, key=lambda p: (math.hypot(p.x - rx, p.y - 50.), p.id)).id if pool else None
        rid = chosen
        tid = r.rs.get('tackler') if r.kind == 'scrim' else None
        tackler = tid if eligible_field(s, P.get(tid), other) else None
        edge = x0 + sg * (zone + DEFENSE_MARGIN_M)
        lo, hi = min(x0, rx) - .5, max(x0, rx) + .5
        spots = {}
        for p in sorted(P.values(), key=lambda p: p.id):
            if not p.active or p.role == 'archer':
                continue
            if p.id == sid: place(self, p, x0, 50., spots); continue
            if p.id == rid: place(self, p, rx, 50., spots); continue
            if p.id == tackler: place(self, p, edge, 50., spots); continue
            if p.team == team: x = x0 - sg * OFFENSE_BEHIND_M if sg * (p.x - x0) > -OFFENSE_BEHIND_M else p.x
            else: x = edge if sg * (p.x - x0) < zone + DEFENSE_MARGIN_M else p.x
            y = p.y
            if lo <= x <= hi and abs(y - 50.) < LANE_HALF_WIDTH_M:          # keep the snap corridor clear
                y = 50. + (LANE_HALF_WIDTH_M if y >= 50. else -LANE_HALF_WIDTH_M)
            place(self, p, x, y, spots)
        r.rs['formation'] = dict(snapper=sid, receiver=rid, receiver_xy=(rx, 50.), depth=depth, zone=zone, nose=None, tackler=tackler,
                                 line_x=x0, spots=spots, receiver_source=source)
        self.emit('scrimmage_formation', 'RB-3.10', restart_id=r.native_id, kind=r.kind, reason=r.reason, team=team,
                  spot=[x0, 50.], snapper=sid, receiver=rid, receiver_source=source, receiver_spot=[rx, 50.], nose=None,
                  tackler=tackler, neutral_zone_m=zone, auto_unfrozen=thawed)
        key = (r.kind, team, round(x0, 1)); wd = self.__dict__.setdefault('rb39_watchdog', dict(key=None, n=0, pp=None))
        wd['n'] = wd['n'] + 1 if key == wd['key'] and wd['pp'] == self.possession.pp else 1
        wd['key'], wd['pp'] = key, self.possession.pp
        if wd['n'] == WATCHDOG_REPEATS:
            self.emit('restart_repeat_report', 'RB-3.9-report', kind=r.kind, team=team, spot=[x0, 50.], repeats=wd['n'])
        return True
    E.rb_form_restart = form
    old_release = E.restart_release

    def restart_release(self, taker, velocity, *a, **kw):
        r = self.s.restart; f = r.rs.get('formation') if r is not None and hasattr(r, 'rs') else None
        ok = old_release(self, taker, velocity, *a, **kw)
        if ok and f:
            self.rb310_hold = dict(origin=(f['line_x'], 50.), restart_id=r.native_id, receiver=f['receiver'], snapper=f['snapper'], receiver_xy=f['receiver_xy'], log_index=len(self.log),
                                   live_ms=self.s.live_ms)
            for p in self.s.players.values():
                if p.active and p.role != 'archer': p.vx = p.vy = 0.
        return ok
    E.restart_release = restart_release

    def hold_step(self, port):
        """RB-3.10 hold: called by the port before each physical step. Pins every player while the
        snap has travelled less than SNAP_HOLD_M and nobody has touched it; then releases both teams."""
        h = getattr(self, 'rb310_hold', None)
        if not h: return False
        s = self.s; b = s.ball
        touched = next((x['event'] for x in self.log[h['log_index']:] if x['event'] in ('touch', 'control', 'keeper_contact', 'contact_rejected')), None)
        travelled = math.hypot(b.x - h['origin'][0], b.y - h['origin'][1])
        why = ('not_live' if s.phase.value != 'live' else 'touch:' + touched if touched else 'carried' if b.carrier
               else 'travelled_5m' if travelled >= SNAP_HOLD_M else None)
        if why:
            self.rb310_hold = None
            self.emit('snap_hold_released', 'RB-3.10', restart_id=h['restart_id'], trigger=why,
                      travelled_m=round(travelled, 2), hold_live_ms=s.live_ms - h['live_ms'])
            return False
        for p in s.players.values():
            if p.active and p.role != 'archer':
                p.target = (p.x, p.y); port.move[p.id] = (p.x, p.y)
        return True
    E.rb_hold_step = hold_step

