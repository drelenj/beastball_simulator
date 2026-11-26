# OWNER BRIEFING

1. **DESIGN COMPLETE.** A6 values carry routes, continuations, shots and stretch separately.
2. **IMPLEMENTED.** A6 uses seven-point carries, the 300 ms decision base and the new valuation. The audit records Keeper motion, near-goal choices and non-carrier takedown commitments.
3. **TESTED.** Five A6 games finished. Seed 1 ended 61–105, compared with 102–98 on A4 and 45–47 on A5. Only seed 1 has matching A4 and A5 games.
4. All requested replay gates passed. The soak runner accepts A6 and the soak awaits owner review.
5. Review the near-goal decision mix and the Keeper and takedown evidence before choosing a larger trial. No gameplay tuning was applied outside the requested formula.

## Implementation

Branch `codex/rb-3-34-carry-value` from `bbd5335ef5233905ff085ea6d5dc09a45fe27d95`. The default-off carry_value switch replaces the carry_seven valuation in A6. The same rulebook seven-point value still applies to scoring.

- Route carry uses seven points times route probability.
- Continuation uses the old 1.55 cap scaled by carry points over the five-point reference, giving a 2.17 cap before decision error.
- Shot uses the rulebook release value, believed lane margin and exponential distance discount. Inside the carry release radius it uses carry points, as prescribed.
- Stretch uses the previous 3.75 baseline scaled by the same carry-point ratio, yielding 5.25.

## Evidence

Across A6 seeds 1–5, average team score was 95.2, average possessions were 155.1 per team, and 28.90% of possessions ended in an attempt. Scores by seed were 61–105, 72–144, 59–100, 79–129, 63–140.

Seed-1 comparison, A6 minus A4 and A5 respectively. Interceptions changed by +2.0 and +7.0 per team. Boundary turnovers changed by +2.0 and -4.0 per team. Points changed by -17.0 and +37.0 per team.

Each single-game interception, boundary and points contrast uses the same descriptive scale as RB-3.33. Differences under 8 interceptions, 6 boundary losses and 38 team points respectively are within single-game noise. Other single-game contrasts stay descriptive.

- A6 minus A4 — within single-game noise.
- A6 minus A5 — within single-game noise.

Seed-1 shot shares of the near-goal carrier menu were 20.00% (A4), 4.76% (A5), 17.53% (A6). The three arms logged 41/98 (A4), 26/64 (A5), 39/77 (A6) Keepers above the set-speed threshold at release, counted per shot faced.

All eight identity replays reproduced their original trace, state and config hashes. The five A6 games completed without an invariant or restart failure. Rates for low-count shot bands and the short keeper histories are descriptive.

The tables contain every RB-3.33 measure, the Keeper speed and settle quantiles, the near-goal selection mix, the cause counts and a 20-episode excerpt. The compressed results contain named box scores, raw shot and outcome measurements, and the fixed-seed samples. Cross-arm comparisons reuse the recorded A4 and A5 match measures. Their diagnostics come from hash-identical replays. Runtime includes the added observer in A6. [Tables](rb334/TABLES.md) · [Raw evidence](rb334/evidence) · [Reproduction commands](rb334/README.md)

A6 recorded 26 carry goals across the five matches, with six stretch starts and five stretch goals. Ala won all five with an average margin of 56.8 points. Those outcomes describe one pairing. The seed-2 boundary ledger counted 69 turnovers, of which 67 could be linked at the exact timestamp of a possession change. The remaining two appear as unclassified in the table and are included in the overall boundary total.

The A6 non-carrier witness recorded 1,338 first commitments in these episodes. The event-based classifier associated 535 with a stale holder belief, 314 with handoff, 11 with the target’s release still in flight, and 478 with other or insufficient evidence. The cause counts are classifications of observed events. They do not establish the athlete’s reason for committing.

## Gates

- a) Full suite on CPython 3.13.5. `819 passed, 23 subtests passed in 589.49s (0:09:49)`.
- b) All six legacy windows matched the golden rows byte for byte.
- c) A6 seed 1 reproduced score, trace, state, effective configuration, named boxes and the diagnostic payload exactly. CPU and profiling samples are measured separately.
- d) Compatibility 57–76, e) CORE 61–80, f) RB-3.28 85–86 and g) RB-3.31 planned 64–96 reproduced the historical score and full hashes. [Full replay fingerprints, lane 1](rb334/evidence/historical-1.json) · [Lane 2](rb334/evidence/historical-2.json)
- h) RB-3.32 combined 99–74. Trace `0045e62d5de38fc85a6c38fd58298284f637bb6d1766ddb7d50cfb159ac22601`. State `b2b6857584bbdc7c486b54f52bd8ebf9c2c89fde8e15893a42c70f5c3be9d9de`.
- i) A0 80–103, A5 45–47 and A6 as recorded below.

- A0 80–103. Trace `8f61716e720f8cd039eaf05d30f5fc1a84e97be1b3712977d4a24665b7892433`. State `2ca4dfd0aa8e660fefb80066ad23c80e3e74dfd9e85e7a099cb89a2807b20d75`. Config `7a92a06d264305cb107e8413b7da4295d5c447c8b56999f2100e43c4944eee5e`.
- A5 45–47. Trace `fd7525653598e77f1bb440847cdd46cb4364d1521dab66832c91681dde5fc194`. State `1a3a61bd1aeaeb769d7ce2ac94abac93a99be2f0f39673c5bb144079cc8ea4a8`. Config `6cc2cb426330db22707aa20877bf6d4a101a63dc815c9f0adf9fd7f4c86147e2`.
- A6-1 61–105. Trace `2437b8084c08d99b954395db42c7b55bdad93402586796a9bdd4ad665dd16aee`. State `e10536f2eb9366ba3d2ea3a8e38a741e93b387bdc15ef3d80dc6f2b53661eeaa`. Config `c6dfe491fdb0dc792a7c4c9c12c803bad5fee1d5173edd874800fe7be1e7bd44`.
