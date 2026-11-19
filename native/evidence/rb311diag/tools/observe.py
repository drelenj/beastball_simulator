"""RB-3.7 read-only observer re-run (diagnosis instrumentation only).

Re-runs a soak match exactly as tools/soak_driver3.py does (native/run.py::run_match, same
config, same roster, same carry-attempt wrapper) and records, outside the engine log, the
positions needed to answer the offense diagnosis. Nothing is written into the match state,
the engine log, the RNG or the intents, so trace and state hashes must equal the soak's
(checked and recorded in the output).

python3 native/evidence/rb37/tools/observe.py --block real --seed 1 --out native/evidence/rb37/observe
"""
import argparse, gzip, json, math, sys, time
from pathlib import Path

import os; REPO = os.environ.get('BB_REPO', '/home/claude/wt310')
sys.path.insert(0, REPO); sys.path.insert(0, str(Path(__file__).parent))
from native.run import run_match                      # noqa: E402
from native.rulebook.config import RulebookConfigV3   # noqa: E402
from native.rulebook.port import RulebookPort         # noqa: E402
from native.nbl_roster import load_canon_nbl          # noqa: E402
from native import cognition as C                     # noqa: E402
from soak_driver3 import control_rosters              # noqa: E402

SNAP = {'restart_release', 'control', 'release', 'tackle_count', 'c3_grounding', 'boundary', 'rb_quota_reset',
        'freeze', 'goal', 'keeper_contact', 'carry_outcome', 'strip', 'restart_awarded', 'frame_contact'}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--block', required=True); ap.add_argument('--seed', type=int, required=True)
    ap.add_argument('--out', required=True); a = ap.parse_args()
    rosters = control_rosters() if a.block == 'control' else load_canon_nbl(('Garvian Guardians', 'Ala Apex'))
    cfg = RulebookConfigV3(roster_digests=tuple(rosters[t].digest for t in ('A', 'B')))
    p = RulebookPort(a.seed, cfg, rosters=rosters); s, e = p.m.s, p.m.e
    carry = []; old = e.rb_carry_attempt; carry_starts = []

    def count(holder, *args, **kw):                   # identical to soak_driver3
        result = old(holder, *args, **kw)
        if result:
            carry.append((p.m.s.now, holder.team))
            carry_starts.append(dict(t_ms=s.now, live_ms=s.live_ms, player=holder.id, team=holder.team, players=positions(),
                                     ball=[round(s.ball.x, 2), round(s.ball.y, 2)], ends=dict(s.ends)))
        return result
    e.rb_carry_attempt = count
    snaps = []; track = []; decisions = []; seen = [0]; flight = []

    def positions():
        return [(q.id, q.team, q.role[0], round(q.x, 2), round(q.y, 2), int(q.frozen(s.now)))
                for q in s.players.values() if q.active and q.role != 'archer']

    ostep = p.step

    def step():
        ostep()
        log = e.log
        for i in range(seen[0], len(log)):
            r = log[i]
            if r['event'] in SNAP:
                snaps.append(dict(id=r['id'], event=r['event'], t_ms=r['t_ms'], live_ms=r['live_ms'], players=positions(),
                                  ball=[round(s.ball.x, 2), round(s.ball.y, 2)], ends=dict(s.ends)))
        seen[0] = len(log)
        b = s.ball
        if b.carrier is None and b.mode.value in ('passed', 'loose', 'shot') and s.phase.value == 'live':
            tg = s.players.get(b.intended) if getattr(b, 'intended', None) else None
            flight.append((s.live_ms, b.version, b.mode.value[0], round(b.x, 2), round(b.y, 2), round(b.z, 2), b.last_releaser,
                           b.intended, round(tg.x, 2) if tg else None, round(tg.y, 2) if tg else None,
                           round(tg.a.reach, 2) if tg else None))
        c = s.ball.carrier
        if c and s.phase.value == 'live':
            q = s.players[c]; track.append((s.live_ms, c, round(q.x, 2), round(q.y, 2), s.ends[q.team]))
    p.step = step
    odec = C.decide

    def decide(v, b):
        out = odec(v, b)
        if v.holds_ball and v.signals.phase == 'live' and v.restart is None:
            i, rec = out
            opts = sorted(rec.get('options') or [], key=lambda o: -o[3] if isinstance(o[3], (int, float)) else 0)[:6]
            decisions.append((s.live_ms, v.athlete, round(v.x, 2), round(v.y, 2), i.kind, i.aim, [(o[0], o[3]) for o in opts], v.zone_elapsed_ms))
        return out
    C.decide = decide
    started = time.monotonic()
    r, _ = run_match(a.seed, cfg, rosters=rosters, port_factory=lambda *x, **k: p)
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    name = f'{a.block}-seed{a.seed:02d}'
    with gzip.open(out / f'observe-{name}.json.gz', 'wt') as f:
        json.dump(dict(name=name, trace_hash=r['trace_hash'], state_hash=r['state_hash'], score=r['score'], log_len=len(e.log),
                       snaps=snaps, carry_starts=carry_starts, carrier_track=track, ball_flight=flight, carrier_decisions=decisions, runtime_s=round(time.monotonic() - started, 1)), f)
    print(json.dumps(dict(name=name, trace_hash=r['trace_hash'], state_hash=r['state_hash'], score=r['score'])), flush=True)


if __name__ == '__main__':
    main()
