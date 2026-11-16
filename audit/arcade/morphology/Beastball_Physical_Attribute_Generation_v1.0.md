# Beastball Physical Attribute Generation — v1.0

**Status:** LOCKED design specification (November 16, 2026)  
**Scope:** Natural physical attribute generation for professional Beastball athletes; common athlete data for Arcade and PRISM.  
**Validation status:** Numerical rules approved; population testing and PRISM/Arcade empirical calibration remain pending.

## 1. Governing principles

1. All nine physical attributes use a universal **absolute** rating scale, independent of the athlete's height, mass, physique, or ancestry. Equal ratings mean equal standardized capabilities.
2. Height, mass, arm span, and physique influence the **probability of generating** an absolute rating. They do not change the definition of that rating.
3. Height and physique establish a rating distribution **before** ancestry modifies it. Tribal modifiers shift the expected distribution center, **not** an already sampled rating.
4. Neutral tribal affinities have no positive or negative modifier. Overlapping ancestry bonuses never stack on one attribute.
5. Physical dimensions remain mechanically consequential: reach, leverage, momentum, inertia, collision geometry, and other anatomical effects can produce different game outcomes even when standardized attribute ratings match.
6. Arcade and PRISM consume the same canonical athlete profile and must respect the same rating definitions. Arcade approximates outcomes; PRISM resolves physical/anatomical interactions. Do not double-count physical-size effects or contradict absolute rating targets.
7. These v1.0 parameters are locked as the current design and may be revised explicitly in a later version.

## 2. Nine natural physical attributes

| Attribute | Absolute definition / measurement concept |
|---|---|
| Speed | Maximum running velocity under standardized conditions |
| Strength | Maximum absolute force production |
| Jumping | Vertical displacement from ground to the bottoms of the feet; **not** total reach |
| Acceleration | Rate of increase in running velocity under standardized conditions |
| Agility | Ability to redirect movement, assessed under standardized movement conditions |
| Balance | Ability to maintain and recover stability under standardized disturbances |
| Throw Power | Maximum ball-release capability, calibrated through release velocity |
| Stamina | Resistance to fatigue under standardized exertion |
| Durability | Resistance to injury under standardized physical stresses |

**Jumping example:** If two athletes have Jumping 90, they have equivalent standardized vertical foot displacement. Their different standing reaches still produce different maximum reachable heights: `maximum_reach ≈ standing_reach + vertical_jump`.

### Rating scale

| Rating | Interpretation |
|---|---|
| 40 | Regular Ndagï citizen (population reference) |
| 55 | Minimum league quality (scale reference) |
| 65 | **Hard minimum for generated professional natural ratings** |
| 70 | League-level quality |
| 78 | Borderline starter |
| 85 | Solid starter |
| 93 | All-League |
| 100 | Greatest of all time |

The **natural** rating of a generated professional athlete is always an integer in **[65, 100]**. Effective in-game ratings can fall below 65 due to fatigue, injury, or other gameplay effects, and remain bounded by the effective 0–100 scale. The scale references at 40 and 55 are not possible natural outputs of this professional generator.

## 3. Generation order and formula

For each attribute `a`:

```text
mu[a] = 78 + height_shift[a](height_inches)
           + physique_shift[a](physique)
           + ancestry_shift[a](inherited_affinity_profile)

natural_rating[a] ~ DiscreteTruncatedNormal(
    center=mu[a], standard_deviation=7, minimum=65, maximum=100
)
```

**Locked numerical parameters:** reference center **78**, standard deviation **7**, bounded/truncated normal distribution, natural rating range **65–100**.

**Discrete sampling convention for implementation:** sample a continuous normal distribution conditioned to the interval **[64.5, 100.5)**, round to the nearest integer, and return 65–100. Equivalently, sample integer `k` with probability proportional to `Φ((k+0.5−mu)/7) − Φ((k−0.5−mu)/7)` for `k = 65,…,100`, normalized across that range. This convention avoids artificial endpoint piles from clipping an unrestricted sample. It specifies a practical discretization of the locked truncated-normal design; exact seeded implementation details remain an engineering choice.

The center `mu` is the **untruncated distribution parameter**. Near the bounds, the realized expected rating is not exactly `mu`, and a +5 shift in `mu` need not increase the observed mean by exactly 5. Every integer in 65–100 retains nonzero probability for every athlete; no ancestry or physique creates a hard attribute cap below 100.

The nine attributes are conceptually related, but **cross-attribute correlations have not yet been numerically specified**. An initial implementation may sample each marginal independently for baseline testing; do not describe independence as a permanently locked biological rule.

## 4. Height probability modifiers — LOCKED

All values are shifts to `mu`, relative to a **7′6″ / 90-inch** reference athlete. Column order follows the nine canonical attributes. Negative numbers are *generation probability shifts*, **not** runtime penalties or hard caps.

| Height | Speed | Strength | Jumping | Acceleration | Agility | Balance | Throw Power | Stamina | Durability |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 6′0″ (72 in) | −1 | −5 | +1 | +3 | +3 | +2 | −4 | +2 | −2 |
| 7′0″ (84 in) | 0 | −2 | +1 | +1 | +1 | +1 | −1 | +1 | −1 |
| **7′6″ (90 in)** | **0** | **0** | **0** | **0** | **0** | **0** | **0** | **0** | **0** |
| 8′0″ (96 in) | +1 | +1 | 0 | −1 | −1 | 0 | +1 | 0 | +1 |
| 9′0″ (108 in) | +1 | +3 | −1 | −2 | −2 | −1 | +3 | −1 | +2 |
| 10′0″ (120 in) | 0 | +5 | −2 | −3 | −3 | −2 | +5 | −2 | +3 |
| 11′0″ (132 in) | −1 | +7 | −3 | −4 | −4 | −3 | +6 | −3 | +4 |
| 12′0″ (144 in) | −2 | +8 | −4 | −5 | −5 | −4 | +7 | −4 | +5 |

**Interpolation:** For heights between adjacent anchor points `(h0, v0)` and `(h1, v1)`, use continuous piecewise-linear interpolation:

```text
height_shift(h) = v0 + (h - h0) * (v1 - v0) / (h1 - h0)
```

Only heights allowed by the separately locked ancestry/morphology rules should be generated. No height-table extrapolation is needed beyond 72–144 inches.

## 5. Physique probability modifiers — LOCKED

The nine physiques are the cross-product of mass band (Light, Moderate, Heavy) and arm-span band (Short, Moderate, Long). Values shift `mu` and do not directly modify in-game motion.

| Physique | Mass band | Span band | Speed | Strength | Jumping | Acceleration | Agility | Balance | Throw Power | Stamina | Durability |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Compact | Light | Short | +1 | −3 | +2 | +3 | +3 | +3 | −2 | +2 | −2 |
| Lean | Light | Moderate | +3 | −3 | +2 | +3 | +2 | +1 | −2 | +3 | −2 |
| Lanky | Light | Long | +3 | −2 | +3 | +1 | +1 | −1 | +2 | +2 | −2 |
| Stocky | Moderate | Short | −1 | +2 | 0 | +1 | +1 | +3 | 0 | 0 | +2 |
| **Athletic** | Moderate | Moderate | **0** | **0** | **0** | **0** | **0** | **0** | **0** | **0** | **0** |
| Rangy | Moderate | Long | +2 | 0 | +2 | 0 | +1 | −1 | +3 | +1 | 0 |
| Bulky | Heavy | Short | −3 | +4 | −2 | −3 | −2 | +2 | +1 | −2 | +4 |
| Powerful | Heavy | Moderate | −1 | +4 | +1 | −1 | −1 | +1 | +3 | −1 | +3 |
| Hulking | Heavy | Long | −2 | +4 | 0 | −3 | −3 | −2 | +4 | −2 | +3 |

**Interpretation:** Physique describes statistical tendencies in *absolute* capability. For example, Hulking athletes are more likely to generate high absolute Strength, but a Hulking and a Lean athlete who both generate Strength 95 possess the same standardized force-production capability.

The exact mass and wingspan values belong to the morphology generator. Do **not** apply a second raw-mass penalty to this rating formula simply because mass already informed physique. PRISM still uses actual mass and dimensions for physical interactions.

## 6. Locked tribal affinity matrix

`P` = Primary; `S` = Secondary; `—` = Neutral. Every tribe has exactly **2 P, 4 S, 3 neutral**, and no attribute has more than two tribes assigning it P.

| Attribute | Ly’Kun | Shynän | Dryqona | Yubu | Vygari | Fefmial | Psolari |
|---|---|---|---|---|---|---|---|
| Speed | S | **P** | — | — | — | S | — |
| Strength | — | — | **P** | **P** | S | — | S |
| Jumping | **P** | S | S | S | — | S | S |
| Acceleration | S | **P** | — | — | — | S | **P** |
| Agility | S | S | S | — | **P** | **P** | — |
| Balance | S | S | S | S | **P** | **P** | — |
| Throw Power | — | — | S | S | S | — | S |
| Stamina | **P** | S | — | **P** | S | S | S |
| Durability | — | — | **P** | S | S | — | **P** |

Throw Power has no tribal primary affinity; it can still reach 100 through build and individual variation.

## 7. Locked pureblood and hybrid affinity bonuses

| Ancestry count | Primary slots | Primary shift | Secondary slots | Secondary shift | Neutral slots | Total listed shift |
|---|---:|---:|---:|---:|---:|---:|
| Pureblood (1) | 2 | +5 each | 4 | +2 each | 3 | +18 |
| Dual-blood (2) | 2 | +5 each | 5 | +2 each | 2 | +20 |
| Tri-blood (3) | 3 | +4 each | 5 | +2 each | 1 | +22 |
| Quad-blood (4) | 4 | +3 each | 5 | +1 each | 0 | +17 |

**Inheritance rules:**

1. Purebloods receive both primaries, four secondaries, and three neutrals from their tribe's locked matrix.
2. Each contributing tribe in a hybrid passes down **one of its two primary affinities**.
3. Duplicate primary selections must be resolved **without stacking**. Where possible, the duplicating tribe can contribute its other primary; a final deterministic/seeded tie-break procedure remains to be specified.
4. Fill the specified number of secondary slots using affinities supported by the contributing tribes, favoring attributes with support from more contributing ancestries and seeded tie-breaking.
5. A primary overrides a secondary on the same attribute; never sum overlapping ancestry shifts.
6. All nine attribute slots must satisfy the exact profile counts in the table above.
7. Neutral means zero ancestry shift, **not** a penalty.

**Open implementation detail, not a new canon decision:** Some ancestry combinations may not yield the target primary-slot count using a naive one-primary-per-tribe selection if primaries overlap. The final duplicate-resolution and secondary-allocation algorithm must be designed, exhaustively tested across valid ancestry combinations, and flagged for canon review if any combination cannot satisfy all locked constraints. Do not silently violate either the one-per-tribe inheritance rule or the target profile counts.

## 8. Arcade / PRISM interoperability contract

### Shared canonical athlete profile

At minimum, both engines should receive:

```text
athlete_id
ancestry_tribes (1–4)
height_inches
mass_lb
arm_span_inches
standing_reach_inches
physique
natural_attributes: {
  speed, strength, jumping, acceleration, agility,
  balance, throw_power, stamina, durability
}
```

This is a conceptual data contract, not a finalized code schema.

### Absolute performance invariants

- **Speed:** Two Speed-90 athletes have the same standardized maximum running velocity. Their acceleration histories, fatigue, and contact outcomes may differ.
- **Jumping:** Two Jumping-90 athletes have the same standardized vertical **foot** displacement. Standing reach is added separately for maximum reachable height.
- **Strength:** Two Strength-90 athletes have the same standardized maximum absolute force production. Leverage, contact geometry, body mass, and momentum can change tackle outcomes.
- **Acceleration:** Equal ratings mean equal standardized acceleration performance, not merely equal muscle force; PRISM must be calibrated accordingly.
- **Agility, Balance, Stamina, Durability:** Equal ratings imply equal performance on their defined standardized assessments; differences in game situations can emerge from anatomy and external conditions.
- **Throw Power:** Equal ratings mean equivalent standardized release capability; trajectory, release position, and reach may differ.

**No double-counting:** Never (a) penalize an athlete's generated Speed/Acceleration rating for size and then (b) apply a contradictory generic size penalty that prevents the same rated standardized performance in PRISM. Actual anatomy must still affect geometry and interactions; the calibration task is to preserve both truths.

## 9. Reproducibility and acceptance tests

**Required generator tests**

1. Fixed-seed repeatability for full athlete records and population summaries.
2. Every natural attribute is an integer 65–100; no effective-rating restriction is incorrectly applied to natural ratings.
3. All seven pureblood matrices meet 2/4/3; each valid hybrid meets its locked slot counts and bonus values.
4. No duplicated primary or secondary shift stacks on the same attribute.
5. All supported heights interpolate continuously; table anchors reproduce exact values.
6. All nine physiques reproduce the table exactly.
7. Neutral ancestry produces zero shift.
8. Truncated-normal probabilities normalize to 1; no clipping-induced endpoint spikes.
9. Rating 100 has nonzero probability for every valid build and ancestry, even if extremely rare.
10. Population reports stratify by height, physique, tribe, and ancestry count; include mean, median, percentiles, 85+, 93+, and 100 frequencies for each attribute.

**Required cross-engine tests**

1. Identical standardized ratings yield comparable physical targets in Arcade and PRISM across body sizes.
2. Reach and jumping remain distinct, including equal-jump/different-reach cases.
3. Mass and geometry retain their effects on contact and movement without duplicating rating-generation adjustments.
4. Compare athlete rankings and distributions for sprints, acceleration, jumping, cutting, throwing, contact, fatigue, and injury-related stress tests.
5. Record and investigate discrepancies rather than altering locked canon silently.

**Validation note:** These are acceptance requirements, not claims that tests have passed. Numerical coefficients are design-locked but not yet empirically validated against the current PRISM implementation.

## 10. Explicitly unresolved / deferred

- Exact hybrid duplicate-primary resolution and secondary allocation algorithm, including impossible-combination handling.
- Numerically specified correlation structure between the nine natural attributes.
- Empirical Arcade–PRISM calibration, physical benchmark mapping from rating 0–100 to real units, and pass/fail tolerances.
- Population-level tuning if the locked reference center 78, SD 7, or table shifts produce undesirable rarity rates.
- Detailed interaction of activated magikal abilities with effective in-game attributes; these are **not** automatically baked into baseline natural ratings.

Any future modification to locked coefficients, matrix entries, slot counts, or absolute definitions requires an explicit versioned design revision.
