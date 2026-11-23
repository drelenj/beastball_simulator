# Review: RB-3.22 reconcile, Codex checkpoint, RB-3.23 individuation (23 Nov 2026)

Claude (lead reviewer). Status: verification TESTED; nothing ACCEPTED (owner only).

## Reproduced independently
- Talent soak (40 matches, codex/rb-3-22-reconciled @ 629660c, native/evidence/rb322-codex/talent): recomputed from raw logs. Scores, margins, win counts and score SDs match Codex's table exactly.

| Mode | Median team | Ala mean margin (SE) | Ala wins |
|---|---|---|---|
| Default | 84.5 | +32.1 (6.9) | 9/10 |
| Technical neutral | 86.5 | +1.9 (10.0) | 5/10 |
| Physical neutral | 88.5 | +34.1 (5.5) | 10/10 |
| Both neutral | 90.0 | +29.2 (5.4) | 10/10 |

- RB-3.23 engine 32ef9da, real seed 1:
  - compatibility: 57-76, 32,528 steps, trace 44399b08...c072, state 046ea55b...865d (= RB-3.21/3.22 gate).
  - individuation enabled: 67-123, 34,354 steps, trace da8e4230...219d, state 291c0baf...0d14 (= Codex fixture).

## Findings
1. Talent gap: with equal technical and physical ratings Ala still leads by 29 (SE 5). Bodies (height, mass, reach) and OVR starter selection carry most of the gap; Garvian's better physical ratings only offset it when technical placeholders are equal. Real technical ratings alone will not close it. Next: decompose the body effect.
2. Physics (read-only, Codex): keeper saves need no superhuman movement; achieved top speed equals rating x 44.704 m/s. Closes E-4; S-3 mostly closed (open: save rate by shot placement).
3. RB-3.23 is opt-in; default identity holds. With fallbacks (PRISM ratings at 0.70, Keeper Skill/Archery/Stamina activated from existing values) seed 1 margin moves from +19 to +56 for Ala. One match only.
4. Lead's own spec errors (Technical Ratings Spec draft v0):
   - Its eight mental ratings ignore the owner's canon PRISM set (Vision, Awareness, Clarity, Reaction, Anticipation, Focus, Instinct, Judgment, Motor Control; Touch; judgment split into Playmaking, Finishing, Marking, Zone Reads, Goalkeeping, In-Air and Live Ball Pursuit, Carrier and Defender Duel; league average 0.70).
   - "Finishing" as shot technique collides with PRISM Finishing (judgment).
   - "Shooting is zero" and "Throw Power unused" came from legacy core_src; Native reads throw_accuracy for all throws and throw_power for max throw speed (native/port.py). `kicking` is inert legacy storage.
   - ratings-0.1 workbook headers do not match the loader's explicit headers ("<Name> (rating)").
5. Codex validation (7cd3f47): agree - rating-consumers.json is stale; selected-action and outcome effects unmeasured for 18 ratings.

## Recommended
Realign the spec to PRISM canon and regenerate ratings-0.2 with loader headers, PRISM centred at 70; then run RB-3.23 in explicit mode. Owner: whether Composure, Discipline, Aggression and Work rate become new canon ratings (recommended: no, for now).
