# Owner canon update, 15 November 2026

Authority: DreLen, relayed directly in the RB-1 implementation conversation.

REVOKED: the minor foul "Marking inside 5 m before the ball is live" and its witness/sanction/tests. It was a Claude proposal, not owner canon. It duplicated offside, tackler alignment (opposite or5m behind) and3m toss-in clearance. Remove it without replacement.

UNCHANGED: Keeper Zone defenders may remain indefinitely while within5m of an attacker. Keep marking_distance=5 for that. Retain snap-readiness ordering before admission checks.

Owner engineering direction: a dead-ball foul forcing a retake must resolve by correction or warning, without repeated exclusions while the game clock is stopped. Keep the dead-progress watchdog. Verify a repeated-foul restart, then bounded seed1 progress beyond5.375 live seconds, then remaining execution/review scenarios and full RB validation within20 attempts.

Implementation evidence is in RB1_REPORT.md, the conformance matrix and manifest. It is not additional canon; owner acceptance is not implied.
