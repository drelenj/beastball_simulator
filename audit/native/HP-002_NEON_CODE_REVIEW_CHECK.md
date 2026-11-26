# Lead check of the third reviewer's (Neon) code review of RB-3.31 (aef4650), 26 Nov 2026

Claude (lead reviewer). Each claim checked against the source in the review bundle.

| # | Claim | Checked | Where |
|---|---|---|---|
| 1 | Every pass flies 0.4 s (speed = distance / 0.4) | CONFIRMED | native/throw_speed.py |
| 2 | NativePort never sets the receiver's pass signal for open-play passes (catch head start unused) | CONFIRMED (only the retired controller and restart releases set it) | core_src/match.py:71, 862, 2251, 2484; no hit in native/ |
| 3 | Hidden second movement clock: new targets accepted only every ~306 ms | CONFIRMED (native does not override it) | core_src/match.py:1300-1301 |
| 4 | Keeper decisions run on the 500 ms clock, after 200 ms sensing + 200 ms latency | CONFIRMED (goalkeeping has no Reflex owner) | native/prism_registry.py:84-93; native/config.py:45-47 |
| 5 | Takedown commitment offered on any pressed opponent within 2.2 m, without checking he is the believed carrier | CONFIRMED | native/prism_core.py:283-291 |
| 6 | Body touching the end line counts out of bounds even inside the goal mouth; the end-line exemption uses the 3 m radius, but a ball at hand height only fits a narrower chord | CONFIRMED (body_out has no goal-mouth exemption) | native/geometry.py:14-17; native/port.py:762-766; native/cognition_rb3.py:443-451; scoring.py:67 |
| 7 | Stretch is offered only when no shot option exists | CONFIRMED | native/prism_core.py:250-256 |
| 8 | PRISM CORE fixes the kernel's awareness and contact-resistance slots at 0.70 | CONFIRMED (intentional, documented in code) | native/port.py:108-113 |
Not checked: speed-multiplier mismatch (cognition_rb3.py:195, 638), strength column in diagnosis.json.

Classification: items 1-5, 7 and 8 are ENGINEERING / BEHAVIORAL (lead). Item 6 needs an owner ruling on the goal-mouth boundary.
