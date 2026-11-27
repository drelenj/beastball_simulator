# Reproducing RB-3.39

Use CPython 3.13.5 and the ratings 0.4 workbook identified in [RB-3.34](../rb334/README.md). Its SHA-256 is `47b48af7a19035428d517582370fa1782b542980c783edf3dfb20619cf437fba`.

```bash
python3.13 -m audit.native.rb333.match E1 /tmp/rb334-ratings.xlsx /tmp/E1-0-1.json.gz --pair 0 --seed 1
python3.13 -m audit.native.rb339.tables audit/native/rb339/evidence audit/native/rb338/evidence /tmp/rb339-tables.md /tmp/rb339-episodes.json.gz
cmp /tmp/rb339-tables.md audit/native/rb339/TABLES.md
cmp /tmp/rb339-episodes.json.gz audit/native/rb339/SAMPLED_BODY_OUTS.json.gz
python3.13 -m audit.native.rb339.checkpoint /tmp/rb339-checkpoint.md
cmp /tmp/rb339-checkpoint.md audit/native/HP-002_RB339_CHECKPOINT.md
python3.13 -m audit.native.rb339.check
python3.13 -m pytest -q b1 native
```

Pair 0 is Garvian Guardians–Ala Apex, seeds 1–5. Pair 1 is Yukïma Cowhands–Isu’Kari Sirenwings, seeds 1–3. Run both E0 and E1 for each pair and seed. E0 verifies R3 and supplies the two additional perimeter witnesses. The aggregate reuses archived R3 values wherever available. Separate CPU comparisons use the archive and the matched perimeter observer. Per-game gzip archives embed named JSON and CSV box scores. Historical commands follow the [RB-3.37 gate guide](../rb337/README.md) with a T3 seed-1 replay and the E0 R3 seed-1 check.

## Engine controls

- `edge_control` expands to `edge_brake`, `edge_turn` and `edge_aim`. Each part also runs on its own. The current rulebook leaves all three off by default.
- Surface locomotion tests approached boundaries against the athlete's stopping distance. A corner spends the single braking budget on the closest threatened line first. If there is time left in the step, propulsion uses the existing longitudinal and lateral limits with the remainder. Any residual adjustment into a threatened line is removed. Contact impulses and boundary adjudication retain their existing order.
- When the desired motion is more than 90° behind the current heading and a line within twice the turning radius is on the short-turn side, the motor reverses the sign of the lateral turn. Effective braking and turning come from each athlete's Agility-derived body, including the current fatigue treatment.
- The shared aim clamp uses a separate outward component and stopping margin for each line. When the calculated margin cannot fit on the field, it leaves the 2 m minimum at the opposite line. Carrier candidates, boundary-guard aims, maneuver aims and admitted surface locomotion all use the same clamp on E1.
- The attacking carrier has a mouth exemption where the body edge reaches the attacked end-line chord at hand height. Dead-ball movement and a marked substitution departure bypass the edge control. Fixed Archer platforms, unsteerable flights, frozen or grounded slides, and external contact impulses keep their existing physics.

## Observer definitions

The [RB-3.38 body-out observer](../rb338/README.md) records each carrier episode. The line is selected by the nearest marked line to the witnessed crossing; exact corner ties are attributed to the end line. A non-carrier exit is an active field athlete's or Keeper's inside-to-out body-envelope transition in a committed live physics interval. It is an observer count independent of possession adjudication. Near-line takedowns use the actual grounded carrier's body centre within 3 m of any line when the counted tackle is emitted. Attempts and successes for each evasion technique use the [RB-3.37 definitions](../rb337/README.md).
