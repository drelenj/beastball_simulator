# TACTICS-0: attribute step spec (for Codex)
Claude (Fable), 2026-11-15. Branch `claude/tactics-0`. Written against Native v0/3 (`claude/native-v0-3-handoff-69stxd` @ 8613280).
Status: **DESIGN COMPLETE**. Not IMPLEMENTED, not TESTED, not ACCEPTED.

## OWNER BRIEFING
1. **Accomplished.** A specification for turning a roster's ratings and body measurements into engine parameters, with 16 conformance tests. Exactly one mapping is canon: a speed rating of 1.0 is 44.704 m/s. Every other mapping is labelled PLACEHOLDER.
2. **What the simulator can do now.** Native v0/3 gives every athlete the same body (2.55 m, 230 kg, 27 m/s top speed) and the same 0.70 on every skill, and reads no roster. No tactic can differ by personnel yet.
3. **Unimplemented or unproven.** All of this. The placeholders are first values, mostly taken from earlier project notes; none is calibrated against play. Several ratings may turn out to change nothing in the present engine; the spec makes Codex report that and not hide it.
4. **Blocking.** Nothing blocks Codex from starting. Three questions are open with placeholders in place (Q-ATTR-1 to Q-ATTR-3).
5. **Recommended action.** Relay this file to Codex. Decide Q-ATTR-1 (the speed curve below 1.0) first: it moves every athlete's top speed.

## 1. Purpose and scope
Native v0/3 sets every athlete from two constants (`NativeConfig.ratings = 0.70` and `NativeConfig.body_standards`) in `native/port.py`. This step replaces those constants with values computed per athlete from a supplied roster.

In scope: the roster input, the mapping, the engine and view changes it forces, versioning, and tests. Out of scope: tuning any mapping, fatigue, injuries, rating development, scoring, and the playbook (`TACTIC_INTERFACE.md`).

## 2. Input
**Scale (owner amendment, 14 Nov 2026 22:42).** The input scale is the usual ranges, not the roster CSVs. These ranges are the **design envelope and are PLACEHOLDER, not canon**:

| Quantity | Scale | Typical professional |
| --- | --- | --- |
| Every rating | 0 to 1 | 0.60 to 1.00 |
| Height | metres | about 2.40 to 2.95 |
| Mass | kilograms | about 155 to 285 |

Canon: a speed rating of 1.0 is 44.704 m/s (about 100 mph).

**Columns.** One row per athlete. The Ala and Xenar roster files were not read for this spec, so the names below come from the project's player generator (`player_gen_v1.py`, `RATINGS`). The loader takes an alias map from file header to these names, and Codex confirms the map against any real file.

| Column | Required | Notes |
| --- | --- | --- |
| `id` | yes | Unique within the team |
| `role` | yes | `field`, `keeper` or `archer`. A fixed role by canon |
| `speed`, `agility`, `strength`, `balance`, `stamina`, `tackling`, `blocking`, `contact_resistance`, `ball_handling`, `catching`, `awareness`, `throw_power`, `throw_accuracy`, `jump` | yes | 0 to 1 |
| `keeper_skill`, `archery_accuracy` | yes | 0 to 1. Used for that role; stored for every athlete |
| `height_m`, `mass_kg` | yes | |
| `reach_m` | no | If absent, derived (section 4) |
| `durability`, `injury`, `kick_power`, `kick_accuracy` | no | Accepted and **not consumed** (section 4) |
| `name`, `position`, `archetype`, `overall` and any other label | no | **Never read.** Position and archetype are provisional labels, not canon |

**Validation.**
- A rating outside 0 to 1, a missing required column, a non-positive mass or a duplicate id rejects the roster with a message naming the row and column.
- A rating inside 0 to 1 but outside 0.60 to 1.00, or a body outside the envelope, is accepted and counted in a warning. The envelope is a description, not a rule.
- Height must also satisfy the engine's own limits (1.4 to 3.6576 m in `core_src/types.py`).
- Roster shape by canon: 22 athletes, at least 10 field athletes, at least one Keeper and one Archer plus one reserve of each. A field athlete is never placed in the Keeper or Archer role by this step.
- A column not in the table and not in the alias map is an error, so a typing mistake cannot silently drop a rating.

## 3. The one canon mapping
> `speed = 1.0` gives `maximum_speed = 44.704 m/s`, exactly.

This is the only rating-to-parameter mapping in this document that is canon. Nothing else below may be presented, logged or reported as canon. (Arrow speed, 250 m/s, is also canon, but it is a constant and no rating maps to it.)

## 4. Mapping table
`r` is the rating named in the row. `clamp(x) = min(1, max(0, x))`. Provenance: **prior** = a placeholder already written in project notes or code; **new** = introduced here as the smallest placeholder.

### 4.1 Speed
| Input | Engine parameter | Formula | Tag |
| --- | --- | --- | --- |
| `speed` at 1.0 | `maximum_speed` | 44.704 m/s | **CANON** |
| `speed` below 1.0 | `maximum_speed` | `22.352 x (1 + r)` m/s, the same line as mph = 50 + 50 r. Gives 35.76 at 0.60, 40.23 at 0.80, 22.35 at 0 | PLACEHOLDER (prior: "Table A" in `player_gen_v1.py`) |

The shape below 1.0 is open (Q-ATTR-1). The alternative is proportional, `44.704 x r`, which gives 26.8 m/s at 0.60, close to today's 27. The two differ by 9 m/s at the bottom of the professional band. A comment in `player_gen_v1.py` calls "nobody slower than 80 mph" canon; this spec does not, because only the 1.0 point was given to me as canon.

### 4.2 Movement
Today's Native value is reproduced at the middle of the professional band (0.80), and the parameter is proportional to the rating: `value = present value x 1.25 x r`.

| Input | Engine parameter | Formula | At 0.60 / 0.80 / 1.00 | Tag |
| --- | --- | --- | --- | --- |
| `speed`, `agility` | `acceleration` | `12.5 x (0.5 speed + 0.5 agility)` m/s² | 7.5 / 10.0 / 12.5 | PLACEHOLDER (new) |
| `agility` | `braking` | `16.875 x r` m/s² | 10.1 / 13.5 / 16.9 | PLACEHOLDER (new) |
| `agility` | `turning` | `16.25 x r` | 9.75 / 13.0 / 16.25 | PLACEHOLDER (new) |
| `jump` | `jump_height` | `1.3 x r` m | 0.78 / 1.04 / 1.30 | PLACEHOLDER (prior: `player_gen_v1.py`) |

Note for the owner: with these values an athlete needs about 4 s and 80 m to reach a top speed of 40 m/s. On a 100 m field the canon top speed would rarely be reached and the speed rating would act mostly through acceleration. Whether that is intended is Q-ATTR-3.

### 4.3 Body
| Input | Engine parameter | Formula | Tag |
| --- | --- | --- | --- |
| `height_m` | `height` | identity. Eye height (0.72 x height) and release height follow in the engine | PLACEHOLDER (identity) |
| `mass_kg` | `mass` | identity. Body radius follows in the engine: `clamp(0.30 + 0.00065 x mass, 0.38, 0.82)` | PLACEHOLDER (identity) |
| `reach_m` | `reach` | the given value; if absent `0.46 x height_m` | PLACEHOLDER (prior: `ATTRIBUTE_BUCKETS_v0.md`) |

The envelope is applied to Keepers and Archers as to field athletes. Older notes give Keepers a larger body range; that is Q-TAC-5.

### 4.4 Skills the engine already stores as 0 to 1
Passed through unchanged. What each does inside the engine is whatever the present physics does with that attribute; this spec does not claim an effect (see test AT-7).

| Input | Engine attribute | Tag |
| --- | --- | --- |
| `strength`, `agility`, `balance`, `contact_resistance`, `tackling`, `blocking`, `ball_handling`, `catching`, `awareness`, `archery_accuracy`, `keeper_skill` | same name | PLACEHOLDER (identity) |
| `stamina` | `endurance` | PLACEHOLDER (identity). **Inert** while fatigue is off in Native |
| `throw_accuracy` | `passing` | PLACEHOLDER (identity) |

### 4.5 Throwing
| Input | Engine parameter | Formula | At 0.60 / 0.80 / 1.00 | Tag |
| --- | --- | --- | --- | --- |
| `throw_power` | per-athlete maximum release speed | `134.1 x (0.5 + 0.5 x)`, `x = clamp((r - 0.4) / 0.6)` m/s | 89.4 / 111.8 / 134.1 | PLACEHOLDER (prior: throw lab v1; the catch kernel already uses 134.1 as the fastest pass) |
| `throw_accuracy` | release direction error (standard deviation) | `max(0.15, 3 x (1 - x)) x release speed / 67` degrees, `x = clamp((r - 0.4) / 0.6)` | at 67 m/s: 2.0 / 1.0 / 0.15 | PLACEHOLDER (prior: throw lab v1) |

Native's throw model is a primitive with a uniform error (Q-THROW-1). Codex maps the standard deviation above onto that model and documents how. The catch kernel already reads `catching` through `(skill - 0.4) / 0.6`; it now receives each athlete's own value.

A larger maximum changes nothing until the athlete chooses his release speed. Today cognition releases every ball at `min(27, max)` m/s and 1.6 m height (R10 F-4). Choosing the speed is cognition work (Claude) that follows this step.

### 4.6 Perception
| Input | Parameter | Formula | Tag |
| --- | --- | --- | --- |
| `awareness` | scale on the athlete's sensor position noise | `2 - 1.25 x r` (1.25 at 0.60, 1.0 at 0.80, 0.75 at 1.00). Latency and cadence unchanged | PLACEHOLDER (new; the sensor constants are themselves placeholders, Q-SENSOR-1) |

### 4.7 Not mapped
| Item | Handling | Reason |
| --- | --- | --- |
| `durability`, `injury` | Not consumed | Native has no injury model and canon says not to invent a random one (RB-1 addendum) |
| `kick_power`, `kick_accuracy` | Not consumed; engine `kicking` stays 0 | No kicking (canon) |
| `judgment` (0.7 in the view), `decision_speed` (0.3), decision interval (500 ms) | Unchanged constants | The envelope has no rating for them |
| Touch (release speed error) | Unchanged constant | The envelope has no rating for it |
| Arrow speed | 250 m/s for every Archer | Canon constant (Q-FAB1-1 answered: fixed, not a ratio) |

## 5. Changes this forces elsewhere
| ID | Change | Why |
| --- | --- | --- |
| E-1 | Roster loader and validation (section 2), one roster per team | Input |
| E-2 | `native/port.py`: when a roster is supplied, set each athlete's attributes from section 4 in place of `cfg.ratings` and `cfg.body_standards` | The step itself |
| E-3 | Arrow speed becomes the constant 250 m/s. v0/3 computes it as a ratio times the fastest athlete's speed (27), which a roster would change | Canon |
| E-4 | Remove the 27 m/s couplings: `pass_speed` 27 and `ball_limit` 40 in the pocket settings become the thrower's own maximum; audit every speed literal in `native/` and the Native paths of `core_src/` and list each as changed or kept | Otherwise throw power cannot matter and stale caps remain |
| E-5 | The athlete's view carries his own mass and his own maximum release speed, exact (SELF-1). It carries no other athlete's attributes | Cognition needs them; IA-001 forbids the rest |
| E-6 | Public tackle count in `Signals` | Needed by two tactic parameters; a scoreboard fact, not hidden state |
| E-7 | A new config version. Its digest covers the roster digest and a mapping version string (`attr-map/1`). native-v0/2 and native-v0/3 stay byte-identical when no roster is supplied | Reproducibility |
| E-8 | Check time-step safety at the new speeds. A 100 ms step moves a 44.7 m/s athlete 4.5 m; two closing athletes 8.9 m | Contact, tackle reach and boundary detection were built at 27 m/s |

Follow-ups owned by Claude after this step: cognition that chooses release speed and height, and removal of the `27.` literals in `native/cognition.py` and `native/cognition_v3.py`.

## 6. Conformance tests
None exists yet. "Lab" means a forced scenario with two athletes that differ in one rating only.

| ID | Test | Pass |
| --- | --- | --- |
| AT-1 | Canon speed. Rating 1.0 in, read `maximum_speed`; then a straight-line run to steady speed | Attribute equals 44.704 exactly; measured top speed within 0.5% |
| AT-2 | Speed curve. Ratings 0, 0.60, 0.80 | 22.352, 35.7632, 40.2336; the config record marks the curve as placeholder |
| AT-3 | No roster, no change. Seed 1 under native-v0/2 and native-v0/3 with no roster | Trace and state hashes equal the recorded values for both versions |
| AT-4 | Table test. For every row of section 4, feed 0, 0.40, 0.60, 0.80, 1.00 | The engine parameter equals the formula |
| AT-5 | Monotone. Sweep each rating from 0 to 1 in steps of 0.05 | Each mapped parameter never decreases (the direction error never increases) |
| AT-6 | Independence. Change one rating at a time | Only the parameters mapped from it change |
| AT-7 | Sensitivity audit. For every rating, one lab with a stated expected direction (for example higher tackling, more groundings) over 200 trials at 0.60 against 1.00 | A report per rating: direction as expected, reversed, or no effect. A rating with no effect is reported **INERT**. The test passes when the report is complete; it does not require an effect |
| AT-8 | Body readback. Height, mass, reach | Eye height, body radius and catch reach equal the engine formulas |
| AT-9 | Arrow speed. Two rosters with different fastest athletes | Released arrow speed is 250 m/s in both |
| AT-10 | Validation. A rating of 1.2; a missing column; an unknown column; a duplicate id | Each rejected with the row and column named |
| AT-11 | Labels are not read. Change every `position`, `archetype`, `name` and `overall` value in a roster | Match hashes identical |
| AT-12 | Roster shape. 22 athletes with the reserves canon requires; a roster with no Archer | Accepted; rejected. No field athlete holds a fixed role |
| AT-13 | Determinism. Same roster and seed twice; serial against parallel | Identical hashes; the roster digest is in the trace |
| AT-14 | Information boundary. Inspect every view of a 600 s window | An athlete's view holds his own body and abilities only. Poison: change a teammate's ratings with positions forced equal; the view is unchanged |
| AT-15 | Step safety. Forced head-on contact, tackle reach and boundary crossing at a closing speed of 89 m/s, run at 100 ms and at 20 ms steps | The same outcome at both step lengths |
| AT-16 | Canon label. Read the config record's list of canon mappings | The list is exactly the speed 1.0 point. Every other mapping is marked placeholder |

One functional check, not a conformance test: a 600 s window with a roster drawn from the envelope (the generator in `audit/tactics/tools/roster_tools.py`) completes with all invariants passing. It shows the step runs. It shows nothing about play.

## 7. Open questions (also in `QUESTIONS_FOR_OWNER.md`)
| ID | Question | Placeholder in force |
| --- | --- | --- |
| Q-ATTR-1 | What top speed does a speed rating below 1.0 give? In particular, is 0.60 = 80 mph canon? | mph = 50 + 50 r |
| Q-ATTR-2 | Is throw power 1.0 = 134.1 m/s (three times the top running speed) canon? It is recorded in the 4 Nov attribute notes | Treated as PLACEHOLDER |
| Q-ATTR-3 | How quickly should an athlete reach top speed? | About 4 s at rating 0.80, from today's acceleration |
| Q-TAC-5 | Do Keepers and Archers share the usual body ranges? | Yes |

## 8. What this spec does not claim
- That any placeholder is right, or close.
- That every rating changes play. AT-7 exists to find out which do.
- That the present engine behaves sensibly at 36 to 45 m/s. It was built and reviewed at 27 m/s; AT-15 covers only the step length.
