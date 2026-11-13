# SPRINT-45 independent review 2 (reviewer did not write the code)

Time-boxed (~4 min), read-only. Scope: the five fix claims in `2c352f8..HEAD` (05c6c73, 0a8a211, f59f6c0, c77d8da). Not an acceptance. Full suite NOT run.

## Commands run (exact output)
- `python3 -m pytest -q b1/test_sprint45.py -W ignore | tail -3` -> `9 passed in 25.96s`
- `python3 -m pytest -q b1/test_sprint.py -W ignore -k "OWN1 or primitives or OWN5 or BR1" | tail -3` -> `4 passed, 26 deselected in 7.61s`
- Probe `MatchPort(3).deliver('A0', 0)` before any capture -> `RuntimeError: no delayed snapshot for A0: deliver() never falls back to live state`

## Claims
| # | Verdict | Basis |
|---|---|---|
| 1 | CONFIRMED (with residue) | matchport.py:163-164 `_snap_for` requires `ms <= due` and `pid in sn['self']`; :199-201 raises on None. Role/slot from `me[3]`/`me[4]` (:211,:218), own goal from `snap['ends']` (:203), attack_sign derived from it (:219). Old L1/L2/L3 fallbacks are gone. Residue below. |
| 2 | CONFIRMED | test_sprint.py:397-398 `lim.read_text()` unconditional; `SPRINT45_LIMITATIONS.md` exists at repo root; test passes non-vacuously. |
| 3 | CONFIRMED | test_sprint.py:241 `s.ends = {'A':100,'B':0}`, :242-243 role/slot flipped for every player, after `capture` (:228-229), before `deliver`. Still one instant, one seed pair; `p.active`, `p.team`, ratings, `port.public`, `port.calls`, `port.rules` are not poisoned. |
| 4 | PARTIAL | Enforcement exists: matchport.py:548-557 `m.e.award(s.other(offender), 50., 50., 'b1_'+violation)`, only when `self.enforce` and phase LIVE. Test (test_sprint45.py:124-139) monkeypatches `port.rules.step` with a fake ZR-1 row and calls `_feed_rules([])`: it proves the wiring and the disabled branch, not that a real zone violation arises in play and is enforced end to end. Only ZR-1 is exercised; ZR-C/ZR-T untested. Restart spot is hard-coded field centre (code says PROVISIONAL). A violation occurring outside LIVE is silently dropped with no ledger note. |
| 5 | PARTIAL | Code present: cognition.py:345 `scan` aim = `(view.x, view.y)`; :336-342 `receive` projects onto believed ball path when `carrier is None` and speed > 3, t clamped [0,1.5]; :217-219 `released:pass`/`released:shoot` forces `holds_ball=False`. Gaps: (a) no test found for any of the three (grep of both test files for `released`/`scan`/receive tests: none); (b) feedback is cleared on every deliver (matchport.py:230-231), so the override lasts exactly one delivery; if the delayed snapshot still shows the athlete as carrier at the next delivery, `holds_ball` goes stale-true again; (c) `released:restart_pass` is emitted (matchport.py:301, :574) but not in the override tuple. (b) was not reproduced by a probe. |

## Claim 1: every remaining non-snapshot read inside `deliver` (matchport.py:170-234)
- :172-173 `self.sensor(pid)`, `pr.deliver`, `pr.bget`, `pr.latency_s`, `pr.P['memory_s']` (:232) - own sensor / own ability. OK.
- :176, :183 `self.public[eid]` (team, role of every player) - NOT delayed: rewritten from live state at every capture (:140-141), so a track's role label is as fresh as the latest capture, not one latency old. Team is static; role is a minor LEAK if roles change (substitution/role swap). Not poisoned by the OWN-1 test (poison happens after capture, `public` already filled).
- :189-190 `self.last_ball` - own memory. OK.
- :191 `a = s.players[pid]`; only `a.team` is used (:203,:204,:206,:209,:215,:218) - static identity. OK. No `a.x/y/role/slot/posture` left.
- :171 `m = self.m` - assigned, never used (dead local).
- :210 `self.pending.get(pid)` - own-action knowledge. OK.
- :216 `self.own_release.get(pid)` - own-action memory. OK.
- :226 `self.ratings[pid]['judgment']` - own ability. OK.
- :227 `self.rules.cfg.keeper_zone_radius` - static rules config. OK.
- :230-231 `self.feedback` - own outcome feedback (read and cleared). OK, see 5(b).
- Stale comment at :192-194 still says team/role/slot/attack direction are read live; only team is.
- Delayed but OMNISCIENT (via snapshot, unchanged from review 1 L4): `snap['immune']` (every player's true immunity/frozen), `rs.direct_holder`, `rs.passive_team`, `rs.contested`, `snap['carrier']` -> `holds_ball`, `snap['quiver']`, `snap['calls']`. Delivered regardless of line of sight.

## First-review findings still OPEN
- OWN-5 FAIL: engine-owned choices remain. `c4c_keepers` save planner wrapped (matchport.py:77, :82, :465 "PROVISIONAL"), `e.ready` wrapped (:78, :86), restart taker / clearance (`targets_dead`), `c3_withhold`. Not touched by these commits.
- BR-3 FAIL as written: `decide(view, belief)` still two arguments (cognition.py:203); `BeliefState` assembled by the runtime (matchport.py:232-233).
- Omniscient delayed public signals (old L4): open, see above.
- Ingress true-state rejections (old (g)): open. matchport.py:267 true carrier check -> `infeasible`; :269 true target existence/activity -> `unknown_target`; reason fed back into belief (:642-645).
- OWN-4, OWN-6, OWN-7, BR-4, BR-5, BR-7 WEAK verdicts: not re-examined, no evidence of change.
- R-15 still `recorded_only` (matchport.py:528-530).
- `test_frozen_B0_file_identity` (23 missing files): not re-run here; status unknown.

## Not verified
- Full `b1` suite; whether the previously failing B0 identity test still fails.
- Any end-to-end run showing a genuine ZR violation enforced, or receiver behaviour improving completion rates.
- `git diff` of `b1/test_sprint45.py` beyond the zone test; evidence/report files in f59f6c0 and c77d8da.
- Reachability of the `RuntimeError` in `deliver` during a real run (callers presumably gate on `ready()`, :166-168; call sites not read).
