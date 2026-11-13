# EMERGENCE-1: what constrains emergence

Experimental. Nothing here is ACCEPTED. Sources: `SPRINT45_LIMITATIONS.md`, `b1/registry.py`,
`b1/evidence_sprint45/INDEPENDENT_REVIEW.md`, `INDEPENDENT_REVIEW_2.md`, review R8 (`audit/m1/HP-002_SPRINT45_REVIEW_R8.md`).
A searched parameter can only change what an athlete is allowed to choose. Everything below is chosen
for the athlete, or fixed, so no search in this sprint can discover a tactic that depends on it.

## Engine-owned choices (Codex is moving these four behind athlete intents on `b1/emergence-ownership-enablers`; deliberately left unchanged here)

| # | Choice | Where | How it limits emergence |
|---|---|---|---|
| 1 | Keeper save planner | `core_src/match.py: c4c_keepers` (called from `b1/matchport.py: _keeper_motor` under a `keeper_save` intent) | The dive/step plan reads the true ball flight. A Keeper style (stay, come out, commit early) cannot emerge; only whether a save is attempted is athlete-owned. |
| 2 | Restart taker and spot | `core_src/match.py: targets_dead`; `b1/matchport.py: _ready` (3 s fallback), `_restart_receiver` | Who takes a restart, where everyone stands, and a forced pass into space after 3 s are engine procedure. Set-piece tactics and quick restarts cannot emerge. |
| 3 | Archer platform movement | `core_src/match.py: update_archers` | The Archer follows the true ball along the platform. Archer positioning cannot be searched, and it uses true state at physics level. |
| 4 | Wind-up refusal | `core_src/match.py: c3_withhold` (inside `make_pass` / `make_shot` preparation) | The engine refuses a commanded wind-up when the arms are pinned. Whether to try a release under contact is not the athlete's choice. |

## Other engine-owned behaviour and fixed values

| # | Item | Where | How it limits emergence |
|---|---|---|---|
| 5 | Contact micro-behaviour (grip, hold, strip, escape effort) | `core_src/match.py: c3_run` and the C3 kernel | "Tackling" in B1 is only the choice to close on the carrier. Tackle technique and timing cannot emerge. |
| 6 | Substitutions and rotation | `core_src/match.py: auto_substitutions` (P4 wrapper in `pocket4_proto.py`) | No bench or fatigue management can emerge; line-ups change under the athletes. |
| 7 | Pass admission speed fixed at 27 m/s, vertical 2 m/s, no loft choice | `b1/matchport.py: submit` (line ~279, Base A admission) and `b1/runtime.py: PhysicalExecutionPort._release_due` (60 degree bound, `MAX_MOVING_RELEASE_CORRECTION_DEG`) | Short soft passes, lobs and through balls do not exist. Passing styles are limited to who and when, which caps what any pass weight can achieve (SPRINT-45 seed 1: 22 of 59 released passes reached a teammate). |
| 8 | Two fixed shot corners | `b1/cognition.py: decide` (shoot option, 50 +/- 3.6) and `b1/matchport.py: _ball_motor` | Shot placement cannot be searched. |
| 9 | Exact delayed public signals: every player's immunity, direct holder, passive team, contested flag, restart taker | `b1/matchport.py: capture` (snapshot keys `immune`, `rules`, `restart`) and `deliver` | Athletes know these without seeing them (R8 F3). Tactics that rely on hiding or on misreading possession cannot emerge; results may overstate coordination. |
| 10 | Pass call is the only communication | `b1/matchport.py: submit` (`self.calls`), `b1/cognition.py` (`receive`) | No plan layer (M2 not started). Any multi-step combination must arise from independent reactions. |
| 11 | Touch source under-detects contests | `b1/matchport.py: _feed_rules` (carrier, engine CONTESTED mode, `touch` events) | Contested possession (R-04, R-22) is rarer than the rule implies, so possession-based signals favour the carrier's team. |
| 12 | Provisional RST-1 spot at the field centre; ZR-C / ZR-T enforcement untested; R-15 recorded only | `b1/matchport.py: _feed_rules` (`m.e.award(..., 50., 50., ...)`) | Zone-clock and Keeper-protection pressure are weak or mis-placed; a search may farm or ignore them (log as EXPLOIT-CANDIDATE, do not patch). |
| 13 | Hand-set option values from Base A | `b1/core.py: decide` (`carry_value` 10 when an opponent is within 5.8 m, else 2; pass value at most about 7) | Under pressure the carrier always carries unless a searched weight overrides it. These are accepted M1 code and must not be changed; they bias every emergent style toward carrying. |
| 14 | Profile 2 x 120 s, ruleset 1.0.2 on the B1 instance | `b1/matchport.py: MatchPort.__init__` (`P.SETTINGS`) | Fatigue, rotation and late-game effects of a 4 x 600 s match are absent; the search proxy is shorter still. |
| 15 | Ball sensed as a body; no scanning policy; exact proprioception | `b1/matchport.py: capture`, `deliver` | Perception-driven styles (scanning, deception) cannot emerge. |
| 16 | Parameters are per team (or per role), not per athlete | `b1/emergence/params.py` | No specialisation between field players can emerge. |
