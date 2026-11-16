# Beastball — Ancestry Generation Guideline
**Version:** 1.0  |  **Status:** Approved working specification  |  **Scope:** Professional NBL/MBL roster generation

## 1. Purpose and governing principle
Generate professional Beastball athletes with **probabilistic weighted random sampling**, not deterministic quotas. All probabilities below describe the target distribution over many independent generated athletes and seasons. A 500-athlete season need not contain exactly 175 pureblood Ly’Kun or five quad-bloods. Do not force the realized population to match the target percentages. The same ancestry record is shared by the arcade game and the PRISM physical simulator.

Ancestry affects the **future morphology and physical-capability distributions**, not an automatic overall-rating bonus. This document specifies ancestry only; it does **not** assign height, mass, speed, strength, or other physical ratings.

## 2. Eligible tribes and exclusions
Eligible: **Ly’Kun, Dryqona, Yubu, Shynän, Psolari, Vygari, Fefmial**. **Faèlyk and Yuwïtu are excluded** from this generator. Yuwïtu are off-world villains in current lore. No athlete can have more than **four** listed tribal ancestries. For generation, **manifested ancestry = genealogical ancestry**; there are no dormant bloodlines or separate inheritance weights. All ancestries in a profile are equally recognized, without fractional shares or automatic trait averaging.

## 3. Primary number-of-tribes distribution
| Distinct tribes in athlete | Population probability | Conditional share of mixed-bloods |
|---|---:|---:|
| 1 | 65.00% | — |
| 2 | 28.00% | 80% |
| 3 | 5.95% | 17% |
| 4 | 1.05% | 3% |
| **Total** | **100.00%** | **100% among mixed-bloods** |

Thus purebloods = 65%; mixed-bloods = 35%. The 35% mixed population consists of 28% dual-blood, 5.95% tri-blood, and 1.05% quad-blood athletes (all figures expressed as percentage points of all professionals).

## 4. Pureblood profiles (one tribe)
| Tribe | Probability among all professionals |
|---|---:|
| Ly’Kun | 35.00% |
| Dryqona | 17.00% |
| Yubu | 5.50% |
| Shynän | 5.50% |
| Psolari | 1.10% |
| Vygari | 0.50% |
| Fefmial | 0.40% |
| **Total** | **65.00%** |

## 5. Dual-blood profiles (exactly two tribes)
| Ancestry combination | Probability among all professionals |
|---|---:|
| Ly’Kun / Dryqona | 6.00% |
| Ly’Kun / Yubu | 3.00% |
| Ly’Kun / Shynän | 2.50% |
| Ly’Kun / Psolari | 1.50% |
| Ly’Kun / Vygari | 1.00% |
| Ly’Kun / Fefmial | 1.00% |
| Dryqona / Yubu | 1.00% |
| Dryqona / Shynän | 1.00% |
| Dryqona / Psolari | 0.50% |
| Dryqona / Vygari | 0.30% |
| Dryqona / Fefmial | 0.20% |
| Yubu / Shynän | 1.00% |
| Yubu / Psolari | 1.00% |
| Yubu / Vygari | 1.00% |
| Yubu / Fefmial | 1.00% |
| Shynän / Psolari | 1.00% |
| Shynän / Vygari | 1.00% |
| Shynän / Fefmial | 1.00% |
| Psolari / Vygari | 1.40% |
| Psolari / Fefmial | 1.00% |
| Vygari / Fefmial | 0.60% |
| **Total** | **28.00%** |

## 6. Tri-blood profiles (exactly three tribes)
The three approved high-level groupings are: Ly’Kun + Dryqona + one other = **1.55%**; Ly’Kun without Dryqona + two others = **2.60%**; Dryqona without Ly’Kun + two others = **1.80%**. No tri-blood professional profile without both Ly’Kun and Dryqona is assigned probability in the current table; this is a **professional-selection modeling assumption**, not a biological impossibility.

| Ancestry combination | Probability among all professionals |
|---|---:|
| Ly’Kun / Dryqona / Yubu | 0.65% |
| Ly’Kun / Dryqona / Shynän | 0.55% |
| Ly’Kun / Dryqona / Psolari | 0.10% |
| Ly’Kun / Dryqona / Vygari | 0.10% |
| Ly’Kun / Dryqona / Fefmial | 0.15% |
| Ly’Kun / Yubu / Shynän | 0.70% |
| Ly’Kun / Yubu / Psolari | 0.35% |
| Ly’Kun / Yubu / Vygari | 0.25% |
| Ly’Kun / Yubu / Fefmial | 0.20% |
| Ly’Kun / Shynän / Psolari | 0.35% |
| Ly’Kun / Shynän / Vygari | 0.25% |
| Ly’Kun / Shynän / Fefmial | 0.20% |
| Ly’Kun / Psolari / Vygari | 0.10% |
| Ly’Kun / Psolari / Fefmial | 0.10% |
| Ly’Kun / Vygari / Fefmial | 0.10% |
| Dryqona / Yubu / Shynän | 0.50% |
| Dryqona / Yubu / Psolari | 0.25% |
| Dryqona / Yubu / Vygari | 0.15% |
| Dryqona / Yubu / Fefmial | 0.10% |
| Dryqona / Shynän / Psolari | 0.25% |
| Dryqona / Shynän / Vygari | 0.15% |
| Dryqona / Shynän / Fefmial | 0.15% |
| Dryqona / Psolari / Vygari | 0.10% |
| Dryqona / Psolari / Fefmial | 0.10% |
| Dryqona / Vygari / Fefmial | 0.05% |
| **Total** | **5.95%** |

## 7. Quad-blood profiles (exactly four tribes)
Every professional quad-blood contains Ly’Kun or Dryqona or both. Approved group totals: both = **0.45%**; Ly’Kun only = **0.40%**; Dryqona only = **0.20%**. These are selection weights, not claims that other quad-bloods cannot exist in the wider world.

| Ancestry combination | Probability among all professionals |
|---|---:|
| Ly’Kun / Dryqona / Yubu / Shynän | 0.20% |
| Ly’Kun / Dryqona / Yubu / Psolari | 0.10% |
| Ly’Kun / Dryqona / Shynän / Psolari | 0.10% |
| Ly’Kun / Dryqona / Yubu / Vygari | 0.05% |
| Ly’Kun / Yubu / Shynän / Psolari | 0.15% |
| Ly’Kun / Yubu / Shynän / Vygari | 0.10% |
| Ly’Kun / Yubu / Shynän / Fefmial | 0.05% |
| Ly’Kun / Shynän / Psolari / Vygari | 0.05% |
| Ly’Kun / Shynän / Psolari / Fefmial | 0.05% |
| Dryqona / Yubu / Shynän / Psolari | 0.10% |
| Dryqona / Yubu / Shynän / Vygari | 0.05% |
| Dryqona / Yubu / Shynän / Fefmial | 0.05% |
| **Total** | **1.05%** |

## 8. Verified marginal ancestry targets
These **overlap** because a mixed-blood athlete contributes to each of their listed tribal ancestry totals. Therefore these percentages must **not** be summed as disjoint player shares.

| Tribe | Pureblood | Dual | Tri | Quad | Any ancestry |
|---|---:|---:|---:|---:|---:|
| Ly’Kun | 35.00% | 15.00% | 4.15% | 0.85% | 55.00% |
| Dryqona | 17.00% | 9.00% | 3.35% | 0.65% | 30.00% |
| Yubu | 5.50% | 8.00% | 3.15% | 0.85% | 17.50% |
| Shynän | 5.50% | 7.50% | 3.10% | 0.90% | 17.00% |
| Psolari | 1.10% | 6.40% | 1.70% | 0.55% | 9.75% |
| Vygari | 0.50% | 5.30% | 1.25% | 0.25% | 7.30% |
| Fefmial | 0.40% | 4.80% | 1.15% | 0.15% | 6.50% |

Additional verified targets: **55%** have any Ly’Kun ancestry; **45%** have none. **30%** have any Dryqona ancestry; **70%** have none. **8%** possess both Ly’Kun and Dryqona ancestry: **6.00% dual + 1.55% tri + 0.45% quad**. Yubu (**17.5%**) and Shynän (**17.0%**) are close enough that seasonal sampling can reverse which is third-largest in a 400–600-player league. Neither rank nor counts should be hard-enforced.

## 9. Required probabilistic sampling algorithm
**Preferred implementation: one weighted draw over complete profiles.** Every row in Sections 4–7 has a probability expressed as a percentage of **all** professional players. Combine those rows into a single profile table (7 + 21 + 25 + 12 = **65 profiles**), and sample one complete profile per athlete with probability `row_percentage / 100`. This preserves all approved joint distributions, overlaps, and class frequencies in expectation.

Equivalent two-stage implementation: first draw tribe count with probabilities `0.65, 0.28, 0.0595, 0.0105`; then draw a complete profile within the selected class with conditional probability `profile_population_percentage / class_population_percentage`. **Do not** roll tribal membership independently, or roll Ly’Kun and Dryqona separately; that breaks the approved overlaps and class frequencies.

```python
import random

def generate_ancestry(rng: random.Random, profiles):
    """profiles: iterable of (tuple[str, ...], percentage_of_all_players)."""
    choices = [ancestries for ancestries, _ in profiles]
    weights = [percentage for _, percentage in profiles]
    return rng.choices(choices, weights=weights, k=1)[0]

# Example: use a fixed seed for reproducibility, not for predetermined counts.
rng = random.Random(20261116)
# athlete_ancestry = generate_ancestry(rng, APPROVED_PROFILES)
```

Each athlete draw should be independent for the baseline generator. For a 400–600-athlete season, allow random fluctuations; never repair the season by forcing underrepresented combinations into the remaining slots. Optional regional recruitment, league-specific scouting, or team-specific selection layers may be added later, but must be separately documented and must not silently overwrite the baseline distributions.

## 10. Validation and reproducibility
- **Structural checks:** every profile has 1–4 distinct eligible tribes; no excluded tribe; no repeated tribe within a profile; no fractional ancestry proportions.
- **Probability checks:** all row weights are nonnegative; pure/dual/tri/quad totals equal 65/28/5.95/1.05%; grand total equals 100%.
- **Marginal checks:** computed tribe membership totals equal the table in Section 8, and Ly’Kun/Dryqona overlap equals 8%.
- **Season checks:** generate 400–600 athletes using an explicit seed; verify each athlete is valid, but **do not** fail the test because realized counts differ from expected values.
- **Statistical checks:** over many independent seeds and large total sample sizes, verify observed class, profile, and marginal frequencies approach their configured probabilities within statistically justified tolerances. Do not require exact percentages in small seasons.
- **Reproducibility:** store generator version, configuration checksum, PRNG algorithm/version, seed, athlete ID, and selected ancestry tuple. Use the same roster record in arcade and PRISM.

## 11. Scope boundaries and future work
This specification applies to the **combined professional Beastball population** and is not a claim about worldwide Ndagïan demographics. It is not a mandatory quota for individual teams, individual seasons, or the NBL and MBL separately. Cultural identity, if needed, is a separate presentation field and does not change the ancestry tuple. Later specifications will define tribe-conditioned height, mass, anatomy, capability distributions, professional selection, and the mapping from absolute physical capabilities to 0–99 ratings. Exceptional multi-attribute combinations must be rare through the physical model, not because the ancestry profile itself automatically confers excellence.

**Approval provenance:** The overall ancestry targets, 21 dual profiles, tri-blood group totals, detailed tri/quad profile allocations, and four-tribe maximum were approved through the Beastball design conversation. This document consolidates those decisions; it does not introduce new demographic weights.
