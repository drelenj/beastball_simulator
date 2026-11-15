# OWNER BRIEFING

1. Accomplished: ATTR-1 is IMPLEMENTED and TESTED on `codex/attribute-1`. Canon proportional speed, roster-backed bodies and skills, per-athlete throwing limits, awareness-scaled sensor noise, own-attribute views, public tackle count, fixed 250 m/s arrows, validation, digests, and evidence are integrated.
2. Native can do now: load two strict 22-athlete rosters, preserve each athlete's fixed field/Keeper/Archer role, run deterministic full matches with different bodies and skills, and expose only an athlete's own private attributes through his view. v0/2 and v0/3 still replay exactly without rosters.
3. Unimplemented or unproven: cognition still chooses the existing primitive 27 m/s release; fatigue/injury/development are out of scope; stamina, Keeper skill, and Archer accuracy are presently INERT. Current checked-in generated CSV exports need the documented adapter because they lack canonical IDs and use incompatible scales/role semantics.
4. Blocking: nothing. One pre-fix seed exposed exhaustion of both fixed-role Archers. It is fixed as a documented PLACEHOLDER rules-authority forfeit; owner canon may later select a different outcome.
5. Recommended action: Claude independently reviews the mapping, view boundary, fixed-role exhaustion placeholder, and replay evidence; DreLen then decides acceptance. Do not tune these mappings from these results.

ATTR-1 was DESIGN COMPLETE when received. It is now IMPLEMENTED and TESTED. It is not ACCEPTED until DreLen accepts it. No quality, balance, tactics, or emergence claim is made.

## Engineering evidence

- Base: `8613280d145cfd56e11fa4f6249ab31dfaaa34fe`
- Main implementation: `6e5608f`
- Deterministic roster/harness: `7b0734c`
- Preservation harness: `9ae57d2`
- Fixed-role exhaustion repair: `7386917`
- Config: `attr-map/1`, digest `97b69081a3c486adc3887e7374db41fc48656cc384802620247b7d87ddd8d182`
- Roster A: `4627c96e61b12abb299dadcc22ffba539c1c444d3a04bd27ddd85f036807efb1`
- Roster B: `b9aa7873dd59a789f5b695519b53856c55a8c5daeb2568031d5f8f1f9f987587`
- Post-repair test suite: `266 passed, 23 subtests passed`.
- Frozen B0: 427 recorded blobs verified. `b1/core.py`, `b1/runtime.py`, and `b1/g1.py` are byte-identical to the base.

## Full-match evidence

| Profile | Seed | Outcome | Live ms | Restarts | Trace | State | Runtime s |
|---|---:|---|---:|---:|---|---|---:|
| native-v0/2 | 1 | final | 2,400,000 | 1.0 | `3840682e2269…` | `411abb0a4bab…` | 176.194 |
| native-v0/3 | 1 | final | 2,400,000 | 1.0 | `cacf24053a2f…` | `d688fcbb46b2…` | 164.141 |
| attr-map/1 | 1 parallel | final 18–25 | 2,400,000 | 1.0 | `7eca62c747fe…` | `1f40dcba1d63…` | 278.929 |
| attr-map/1 | 2 parallel | final 18–22 | 2,400,000 | 1.0 | `2c90ce85279e…` | `2329686cdc13…` | 277.546 |
| attr-map/1 | 3 pre-fix | failed: fixed-role cover exhausted | — | — | — | — | 287.155 |
| attr-map/1 | 3 fixed | final forfeit 5–0 | 2,563,042 | 1.0 | `2bcad949bc43…` | `0f91a131be16…` | 163.765 |
| attr-map/1 | 1 serial | final 18–25 | 2,400,000 | 1.0 | `7eca62c747fe…` | `1f40dcba1d63…` | 157.361 |

Budget: 7 of 12 full matches used; no further batches started. All six completed matches had invariant status passed, no kick intents, and command-to-intent provenance. The repaired seed 3 ended after entering overtime when B exhausted both fixed-role Archers; it did not crash or stall.

ATTR seed event counts:

| Seed | goals | fouls / discipline | tackles | arrows | freezes | boundaries | restarts awarded / released |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 14 | 18 / 18 | 61 | 194 | 50 | 227 | 358 / 347 |
| 2 | 15 | 22 / 22 | 75 | 175 | 37 | 240 | 378 / 362 |
| 3 fixed | 11 | 25 / 25 | 81 | 192 | 45 | 246 | 391 / 376 |

The restart completion metric is closed restarts / awarded restarts, hence 1.0 even where the release count is lower because a score, boundary, replacement restart, or match end can close a restart without release.

## Reproduction

```bash
git switch codex/attribute-1
.venv/bin/python -m pytest -q b1 native
.venv/bin/python -m native.generate_attr_rosters
.venv/bin/python -m native.validate_attr --config-version native-v0/2 --seeds 1 --label preserve-v02 --workers 1
.venv/bin/python -m native.validate_attr --config-version native-v0/3 --seeds 1 --label preserve-v03 --workers 1
.venv/bin/python -m native.validate_attr --config-version attr-map/1 --seeds 1 2 3 --label attr-parallel --workers 3
.venv/bin/python -m native.run --config-version attr-map/1 --roster-a native/evidence/attr1/rosters/team-A.csv --roster-b native/evidence/attr1/rosters/team-B.csv --seed 1 --out /tmp/attr-seed1-serial.json
```

The validator is budget-enforcing and will refuse runs once 12 recorded attempts exist. For a clean independent reproduction, use a fresh checkout so the committed evidence ledger starts at its recorded state rather than appending duplicate attempts.

## Placeholders and owner questions

`QUESTIONS_FOR_OWNER.md` records Q-ATTR-1 through Q-ATTR-7. The material open canon item is Q-ATTR-7: when both fixed-role Keepers or Archers are unavailable, the current smallest safe outcome is a `no_fixed_role_cover` forfeit. The generator adapter, uniform-error translation, body-envelope warnings, acceleration effect, and inert mappings are also explicit there. The complete speed-literal disposition is in `ATTR1_SPEED_AUDIT.md`; AT-1 through AT-14 map to tests in `ATTR1_CONFORMANCE_MATRIX.md`.
