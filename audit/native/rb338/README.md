# Reproducing RB-3.38

Use CPython 3.13.5 and the ratings 0.4 workbook from the [RB-3.34 reproduction guide](../rb334/README.md). The workbook SHA-256 is `47b48af7a19035428d517582370fa1782b542980c783edf3dfb20619cf437fba`.

```bash
python3.13 -m audit.native.rb333.match R3 /tmp/rb334-ratings.xlsx /tmp/R3-0-1.json.gz --pair 0 --seed 1
python3.13 -m audit.native.rb338.tables audit/native/rb338/evidence audit/native/rb337/evidence /tmp/rb338-tables.md /tmp/rb338-episodes.json
cmp /tmp/rb338-tables.md audit/native/rb338/TABLES.md
cmp /tmp/rb338-episodes.json audit/native/rb338/SAMPLED_BODY_OUTS.json
python3.13 -m audit.native.rb338.check
python3.13 -m pytest -q b1 native
```

Pair 0 is Garvian Guardians–Ala Apex, seeds 1–5. Pair 1 is Yukïma Cowhands–Isu’Kari Sirenwings, seeds 1–3. Run each pair and seed for R0, R1, R2 and R3. R0 replays the saved L0 matches to add release timestamps and two-second body-out traces. Each result embeds named JSON and CSV box scores. The historical fingerprints use the [RB-3.37 commands](../rb337/README.md) and compare with that archive.

## Reading the Archer records

- Attempts include illegal forfeitures. Released arrows are projectiles. Net charges subtract in-flight refunds. Hits count geometric contacts with players regardless of the strike panel or immunity ruling. Freeze counts distinguish carriers at the freeze event.
- End-of-period remaining budgets use the final outgoing period's resource counts after its in-flight refunds. R0 and R1 report the active possession quota at each boundary.
- Release intervals pair legal projectiles from the same Archer. The elapsed match clock includes dead play and breaks. The live clock excludes them. Tables average the within-game quantiles.
- The cycle snapshots effective Strength and Archery Accuracy when the draw begins. A target change keeps the original draw deadline and restarts only the aim, with release gated by the updated deadline and a fresh athlete intent. Actual releases can follow the minimum deadline when the athlete next decides. An abort spends nothing. The legacy turn-change rule still retires projectiles without refund. Period and match scopes preserve dead-ball in-flight refunds.

## Reading the body-out records

- Every body-out has a rolling two-second history, including time before the athlete gained the ball. Physics samples bracket committed engine intervals and omit rejected speculative integrations. Decision samples retain perception and selection evidence. Between decisions, the latest believed line distance and nearest defender are carried forward with their decision timestamp. The true body state and nearest defender are sampled independently.
- `clamp_checks` records calls and both aims. `selected_aim_clamped` identifies when one of their changed outputs equals the selected aim. The admitted locomotion target and engine body position are recorded separately.
- The observer gives precedence to frozen/grounded state, then to an active wrap or hold or a collision in the preceding 150 ms, then to an admitted maneuver, then to whether the exit target is inside the field. Contact push is a timing-based classification, with the nearest relevant collision detail supplied in the episode. An aim on the line is counted outside. The classes describe witnessed conditions.
- The sample uses a fixed seed, with five complete episode histories from each arm. The per-game archives retain every body-out, and the aggregation reconciles its count against the boundary event list.
