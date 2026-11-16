# Beastball Morphology Generator v1.0

**Status:** LOCKED / approved 2026-11-15–16.  
**Scope:** Probabilistic generation of professional Beastball athlete ancestry, height, physique, mass, arm span, and standing reach. Intended for arcade Beastball and PRISM. This is a specification, not a claim of empirical anatomical validation.

## 1. Ancestry

Eligible manifested ancestries: **Ly’Kun, Dryqona, Yubu, Shynän, Psolari, Vygari, Fefmial**. Faèlyk and Yuwïtu are excluded from this generator.

- Pureblood: **65%**.
- Mixed ancestry: **35%**, comprising dual **28%**, tri **5.95%**, quad **1.05%** of all players.
- Previously approved detailed ancestry-combination weights are part of the ancestry-generation specification and must be preserved when integrating this morphology model. They are **not reproduced here** because this document does not have the authoritative combination table.
- Ancestry probabilities are sampling probabilities, not enforced roster quotas.

## 2. Height distribution by tribe

Height is sampled from a **normal distribution truncated to the tribal bounds**. All heights below are in inches for computation.

| Tribe | Minimum | Maximum | Underlying normal mean | Underlying SD |
|---|---:|---:|---:|---:|
| Ly’Kun | 72 (6′0″) | 108 (9′0″) | 90 (7′6″) | 9 |
| Dryqona | 96 (8′0″) | 144 (12′0″) | 102 (8′6″) | 12 |
| Yubu | 72 | 108 | 90 | 9 |
| Shynän | 72 | 96 (8′0″) | 90 | 9 |
| Psolari | 72 | 108 | 90 | 9 |
| Vygari | 72 | 108 | 90 | 9 |
| Fefmial | 72 | 84 (7′0″) | 90 | 9 |

The *underlying* mean is not necessarily the actual mean after truncation. Dryqona's chosen parameters were intended to place the professional population near 9′0″; validate the realized mean in testing rather than assuming it is exactly 9′0″.

## 3. Nine universal physiques

Physique is a combination of **mass category** and **arm-span category**.

| Mass category | Short arms | Moderate arms | Long arms |
|---|---|---|---|
| Light | Compact | Lean | Lanky |
| Moderate | Stocky | Athletic | Rangy |
| Heavy | Bulky | Powerful | Hulking |

### Universal mass calibration

At reference height **72 in (6′0″)**, sample reference mass uniformly within the selected mass interval:

| Mass category | Reference mass at 72 in |
|---|---|
| Light | 185–215 lb |
| Moderate | 215–245 lb |
| Heavy | 245–275 lb |

Scale to actual height **H** (inches):

`mass_lb = reference_mass_lb * (H / 72)^3`

### Universal arm-span calibration

Sample an arm-span ratio uniformly within the selected interval:

| Arm category | Arm-span / height ratio |
|---|---|
| Short | 0.94–1.00 |
| Moderate | 1.00–1.07 |
| Long | 1.07–1.15 |

`arm_span_in = H * arm_span_ratio`

Boundary overlap is inconsequential for continuous sampling. Uniform sampling within category intervals is the implementation default; the approved bounds themselves are canonical.

## 4. Locked tribal physique distributions

All values are percentages of athletes *within the indicated tribe*. Rows are mass categories; columns are arm-span categories. Joint values are products of the approved mass and reach marginals.

### Ly’Kun

- Mass: Light **33⅓%**, Moderate **33⅓%**, Heavy **33⅓%**.
- Arms: Short **33⅓%**, Moderate **33⅓%**, Long **33⅓%**.
- Each of the nine physiques: **1/9 = 11.111…%**.

### Dryqona

- Mass: Light **5%**, Moderate **30%**, Heavy **65%**.
- Arms: Short **10%**, Moderate **30%**, Long **60%**.

| Mass | Short | Moderate | Long |
|---|---:|---:|---:|
| Light | Compact 0.5% | Lean 1.5% | Lanky 3% |
| Moderate | Stocky 3% | Athletic 9% | Rangy 18% |
| Heavy | Bulky 6.5% | Powerful 19.5% | Hulking 39% |

### Yubu

- Mass: Light **10%**, Moderate **45%**, Heavy **45%**.
- Arms: Short **10%**, Moderate **45%**, Long **45%**.

| Mass | Short | Moderate | Long |
|---|---:|---:|---:|
| Light | Compact 1% | Lean 4.5% | Lanky 4.5% |
| Moderate | Stocky 4.5% | Athletic 20.25% | Rangy 20.25% |
| Heavy | Bulky 4.5% | Powerful 20.25% | Hulking 20.25% |

### Shynän

- Mass: Light **60%**, Moderate **30%**, Heavy **10%**.
- Arms: Short **5%**, Moderate **15%**, Long **80%**.

| Mass | Short | Moderate | Long |
|---|---:|---:|---:|
| Light | Compact 3% | Lean 9% | Lanky 48% |
| Moderate | Stocky 1.5% | Athletic 4.5% | Rangy 24% |
| Heavy | Bulky 0.5% | Powerful 1.5% | Hulking 8% |

### Psolari

- Mass: Light **10%**, Moderate **65%**, Heavy **25%**.
- Arms: Short **20%**, Moderate **65%**, Long **15%**.

| Mass | Short | Moderate | Long |
|---|---:|---:|---:|
| Light | Compact 2% | Lean 6.5% | Lanky 1.5% |
| Moderate | Stocky 13% | Athletic 42.25% | Rangy 9.75% |
| Heavy | Bulky 5% | Powerful 16.25% | Hulking 3.75% |

Psolari's lore of dense light and layered flesh does not add an extra weight multiplier in this morphology model.

### Vygari

- Mass: Light **5%**, Moderate **30%**, Heavy **65%** (same as Dryqona).
- Arms: Short **33⅓%**, Moderate **33⅓%**, Long **33⅓%**.

| Mass | Short | Moderate | Long |
|---|---:|---:|---:|
| Light | Compact 1⅔% | Lean 1⅔% | Lanky 1⅔% |
| Moderate | Stocky 10% | Athletic 10% | Rangy 10% |
| Heavy | Bulky 21⅔% | Powerful 21⅔% | Hulking 21⅔% |

### Fefmial

- Mass: Light **20%**, Moderate **60%**, Heavy **20%**.
- Arms: Short **20%**, Moderate **60%**, Long **20%**.

| Mass | Short | Moderate | Long |
|---|---:|---:|---:|
| Light | Compact 4% | Lean 12% | Lanky 4% |
| Moderate | Stocky 12% | Athletic 36% | Rangy 12% |
| Heavy | Bulky 4% | Powerful 12% | Hulking 4% |

## 5. Mixed-ancestry inheritance (LOCKED)

### Height

For a mixed athlete, **select a constituent tribe's entire truncated height distribution** using the weights below, then draw height from that selected distribution. Do not average heights or underlying normal parameters.

| Composition | Height-distribution selection weights |
|---|---|
| Pureblood | Own tribe 100% |
| Dual without Dryqona | 50% / 50% |
| Tri without Dryqona | ⅓ / ⅓ / ⅓ |
| Quad without Dryqona | 25% each |
| Dual with Dryqona | Dryqona **70%**, other **30%** |
| Tri with Dryqona | Dryqona **60%**, each other **20%** |
| Quad with Dryqona | Dryqona **55%**, each other **15%** |

This is **Dryqona height dominance**: it increases the chance of Dryqona-like stature without guaranteeing it. The total support of a mixed athlete's possible heights is the union of constituent tribal height ranges (here a contiguous interval). These weights are not blood percentages.

### Physique

Independently of height selection, take the **arithmetic mean of the nine physique probabilities** across all constituent tribes, including Dryqona:

`P(physique=j | ancestry set) = sum(P(physique=j | tribe) for tribe in ancestry_set) / number_of_tribes`

Sample one physique from the resulting nine-category distribution. **Dryqona has no additional dominance in physique selection.** Height and physique ancestry influences are sampled independently.

### Measurements

Once height and physique are drawn, apply the universal mass and arm-span formulas; do not introduce hidden ancestry multipliers. The model does not directly assign speed, strength, agility, endurance, or other physical ratings from physique labels.

## 6. Universal shoulder geometry and standing reach (LOCKED)

All seven tribes and all ancestry combinations use the **same standing-reach approximation**, with no tribe- or physique-specific shoulder correction:

`standing_reach_in = 1.25 * height_in + 0.5 * (arm_span_in - height_in)`

Equivalently:

`standing_reach_in = 0.75 * height_in + 0.5 * arm_span_in`

This is an **approved game/simulation approximation**, not an empirically validated biomechanical equation. It may be calibrated in a later version only through an explicit specification revision.

## 7. Reproducible generation algorithm

1. Seed a deterministic random-number generator.
2. Sample the number and identity of manifested ancestries from the approved ancestry-generation distribution.
3. Select the height-source tribe using Section 5 weights.
4. Sample height from that tribe's truncated normal distribution and bounds.
5. Compute the equally blended nine-physique probability distribution; sample a physique.
6. Sample reference mass from its mass category interval and scale cubically by height.
7. Sample arm-span ratio from its arm category interval and multiply by height.
8. Calculate standing reach using the universal formula.
9. Record seed, ancestry combination, selected height-source tribe, physique, height, mass, arm span, and standing reach for auditing.

### Acceptance checks

- All seven pureblood height samples fall within approved tribal bounds.
- Mixed height-source selection matches the applicable Dryqona/non-Dryqona weights statistically.
- Nine physique probabilities for every pureblood or hybrid sum to 100% at full precision.
- Pureblood and hybrid physique frequencies approach expected probabilities with large seeded samples.
- Mass and arm-span ratios always fall in selected category ranges.
- Standing reach is deterministic from sampled height and arm span.
- Re-running with the same seed and generator version reproduces identical athletes.
- No population quota, hard-coded physical-rating cap, or unapproved ancestry mass multiplier is applied.

## 8. Implementation boundary

This document locks the **morphology** generator, not player performance ratings, role/position assignment, gameplay skill, injury physiology, or PRISM motor mechanics. The previously approved detailed ancestry-combination table must be attached or imported from its authoritative specification to produce the full ancestry population exactly as intended.
