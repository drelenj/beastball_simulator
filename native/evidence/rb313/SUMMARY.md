# RB-3.13 evidence (PROVISIONAL, claude/rb-3-13-pass-safety; code 6bf5c0e; baseline RB-3.12 0091755)

## OWNER BRIEFING
1. Accomplished (IMPLEMENTED, TESTED): pressure by time-to-contact; safe pass lanes (opponents advanced by velocity, reach+0.5 m, margin in the value); carry free run by closing time; commitment off when pressured; zone-clock penalty 6*(1-t_left/2); owner's gated clock read (only teammates in fresh tracks; no unwired path found, every carrier path goes through carrier_options); no arrows during the snap hold (cognition gate + engine inert/refunded/no-foul). Full suite 554 passed (11 new in test_rb313.py, 15 in test_rb312.py updated where they encoded the replaced rules); hashes of native-v0/2, v0/3, rb/2 identical to 185b557.
2. Can do now: pass completion up (0.42-0.45 -> 0.59-0.63); intercept rate 44-50% -> 27-30%; second tackle on the receiver 40% (was 40%: 116/286 before, 40-56 of 150-197 now, about 27%); no arrow is released during a hold (0 in both RB-3.12 and RB-3.13 logs by the log window measure; the engine now makes one inert).
3. WORSE or unproven: carrying collapsed (carry attempts about 65-78 vs 140-177; carry goals 3/3/1/5 vs 9/11/9/4), scores lower, possessions per team 165 (below RB-3.11 ~214), completion still under the 0.75 aim, median interception distance not improved. Not tuned.
4. Blocking: BEHAVIORAL questions for Claude in QUESTIONS_FOR_CLAUDE.md. No new owner questions.
5. Recommended: lead decides questions 1, 2 and 4 (reach estimate, release-point sample, free-run speed model) before more work.

## Before/after (RB-3.12 -> RB-3.13), real 1/3/5, control 1
| metric | RB-3.12 | RB-3.13 |
|---|---|---|
| scores | 28-58, 29-64, 27-63, 22-36 | 14-36, 14-39, 23-28, 26-40 |
| open-play completion | .453/.45/.416/.418 | .617/.588/.599/.629 |
| passes (released) | 329/307/291/251 | 193/211/187/221 |
| intercepted | 146/141/146/108 (44-50%) | 56/63/53/59 (27-30%) |
| median intercept distance m | 2.55/2.52/2.87/3.06 | 1.95/2.46/1.87/1.75 |
| median completed pass m | 8.3/8.7/11.4/12.3 | 9.9/8.1/8.4/6.6 |
| second tackles on receiver | 116/286, 114/266, 142/335, 154/353 | 40/150, 46/173, 56/197, 63/260 |
| possessions per team | 267/256.5/270/259 | 165/165.5/164.5/167.5 |
| share ending in attempt | .315/.304/.307/.255 | .246/.305/.264/.257 |
| carry attempts | 177/161/167/140 | 64/78/68/78 |
| carry goals | 9/11/9/4 | 3/3/1/5 |
| arrows released during holds | 0/0/0/0 | 0/0/0/0 |
| receiver freezes after snap | 20/15/15/27 | 29/21/21/21 |
| freezes / wasted (not carrier) | 110/81, 123/100, 125/101, 156/120 | 151/96, 133/94, 137/101, 127/92 |
Tables: diag_extra.txt, diag_output.txt (holds, pass_ctx, snap_chain), measure via tools/measure.py. (The lead's quoted 481/490 differs from my definition: second tackle = count_to 2 within 300 events of the snap.)

## Constants: see the table at the top of the B-5 section of native/cognition_rb3.py.
## Per-match hashes (trace / state)
- real1 14-36 steps 32899: d85b699dfee3d3e6ac1a5e3b1854efef8fdd6906a623aa1eccc0a3cb1902d30c / eef92b5627a4a9355917308c3c1279432c22c33f1f54c8aeab0e6579a87d7dd8
- real3 14-39 steps 33849: 6a0d8fb099400d53ee12c80312649b3a2df6480ee21795ed2e930cc08114cd48 / a8e65c5a32bba3bcae6297f148a7de16fdcf16de6d6084e4f636d265e82eaba9
- real5 23-28 steps 34045: f20a87fb2d641bc8a0f31b50391ba33ee161e07a6d35e8ea5e8bc9177f11cbd3 / 2eada7cb2627efcc34cd5e7abd948e6c926506728ebc5e748ac31d5c272173a7
- control1 26-40 steps 35242: 59627eb2247ff8ca7c849ea58b372559b63cb3e91c64801d8b7de8c49f33df01 / e3ec7595cec8ab810e9be56bc7f23b41db4f2c009aaac4a52d3d17c10393ffae
Raw logs: native/evidence/rb313/runs/{real,control}/raw-*.json
