# RB-3.12 evidence (PROVISIONAL, claude/rb-3-12-carrier-valuation; code fdc8c69; baseline RB-3.11 dcf2119)

## OWNER BRIEFING
1. Accomplished: E-3 snap corridor (IMPLEMENTED, TESTED), B-5 carrier valuation (IMPLEMENTED, TESTED), Part 1 zone-exit rules (IMPLEMENTED, TESTED). Full suite 543 passed; native-v0/2, v0/3, rb/2 hashes identical to 185b557 (3000 steps, seeds 1 and 3).
2. Can do now: first touch of the snap is the designated receiver (50/50 scrimmages; was 20/50); carriers carry when unpressured and pass when pressured; defenders and attackers with no reason in a zone leave at once; scenario exit times equal pure-physics exit times (2.78/2.4/2.0/1.5/0.9 s at depths 1/5/10/15/19; was 4.4-5.1 s).
3. Unproven / worse: open-play pass completion fell sharply (0.78-0.82 -> 0.42-0.45); interceptions on passes 541 of 1178 (513 of 3686 before). Passes fell by two thirds, hold time rose 0.8 -> 1.8 s, tackles up 222-294 -> 273-341, scrimmage chain: post-snap the receiver is tackled in 481 of 490 second tackles with median gain -1.4 m (more backward). Not tuned.
4. Blocking: owner questions Q-RB312-1..7.
5. Recommended: decide Q-RB312-7 (pass valuation retune) and Q-RB312-1 (penalty amount) before further work.

## Before/after (RB-3.11 -> RB-3.12), seeds real 1/3/5, control 1
| metric | RB-3.11 | RB-3.12 |
|---|---|---|
| score real1 | 21-33 | 28-58 |
| score real3 | 16-52 | 29-64 |
| score real5 | 34-40 | 27-63 |
| score control1 | 11-25 | 22-36 |
| carry goals (1/3/5/c) | 1/7/3/1 | 9/11/9/4 |
| open-play completion | .783/.818/.798/.81 | .453/.45/.416/.418 |
| share ending in attempt | .177/.201/.198/.127 | .315/.304/.307/.255 |
| zone_residence calls | 0/4/0/1 | 0/0/1/1 |
| snap completion | .993/1/.985/.986 | .988/.981/.992/.982 |
Full tables: measure.json style output in this directory's runs and diag_output*.txt.

## Per-match (RB-3.12) trace_hash / state_hash
- real1 28-58 steps 39123: 69b4b7b0b355914fa8f1206179fb695ebc4be8e5d34b5511542d6b24cb044e0e / 4dae9c78b72e85d95c2977ab6cc4daefd27ee3213c373fd098514e5f6e64e7d4
- real3 29-64 steps 39157: 1991ab2bf38e0aeee1ef1455825d2c02472f9b13a04cb6a22418feeb56547bad / 9412704e8f536ec7860cf636097c620323b3ba2d4f8c3247d41253a9eabebfee
- real5 27-63 steps 40019: 28486bbfdf32d616af261d56e7998baf0a9e5deeb25088c9b51bae38a4f43372 / a010d66054ae47f65f24852b6734d2daa871164ed6c73f427c2e24d53ba541a0
- control1 22-36 steps 40449: 51e31c8fadb046ef6231498f7015091830ac404def776ba06bd1e7a5f488b772 / 52e9f2f359b522d9e26592d9eab41798dfaf8e6f5b68c5622b233ab6a8f0fe24
Raw logs: native/evidence/rb312/runs/{real,control}/raw-*.json. Diagnosis: diag_output.txt (holds, pass_ctx, snap_chain, RB-3.12 then RB-3.11 snap chain).
