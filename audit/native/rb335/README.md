# RB-3.35 reproduction

Use CPython 3.13.5 and the same NumPy, openpyxl and pytest dependencies as RB-3.34. The RB-3.34 workbook export command is in [the RB-3.34 README](../rb334/README.md).

```bash
python3.13 -m audit.native.rb333.match B4 /tmp/rb334-ratings.xlsx /tmp/B4-1.json.gz --seed 1 --turnover-diagnostics
python3.13 -m audit.native.rb335.tables audit/native/rb335/evidence audit/native/rb334/evidence /tmp/rb335-tables.md
cmp /tmp/rb335-tables.md audit/native/rb335/TABLES.md
python3.13 -m pytest -q b1 native
python3.13 -m native.rulebook.scoring_audit --legacy
```

The raw JSON includes the named box scores in the structured box field and in the box_csv field. The A6 replays add observations absent from the saved A6 boxes. The renderer checks each replay against its matching saved seed's score, trace, state and config digest.

## Measures

- The intended receiver's location is sampled at actual reception or the first observed physics step crossing the plane through the intended aim perpendicular to the planned pass. Passes terminated before either observation have no arrival measurement. The sample is a step-resolution measurement and includes no estimate from future or hidden observations in the policy.
- A carrier exit is marked after contact if the carrier had a recorded collision within the last 500 ms. This is temporal attribution. Play continuing means the same attached ball crossed a sideline between physics ticks and the same carrier still held it after adjudication.
- Capture-time observations keep original timestamps for freshness rules and growth of uncertainty. The projected planning copy replaces the former remembered position drift in B arms. It leaves frame contents immutable.
- Scrimmages per possession counts formation events for both scrim and snap40. First tackles count possessions spanning a logged count-to-one grounding.
- The box Keeper rate counts the scorer's saved-shot and shot-faced events. The event rate independently marks a save for a Keeper touch on a projected on-target shot that did not score, divided by shots faced in the reconstructed flights.
- An issued contact counts the selected wrap or takedown before the final evidence gate. Accepted contact counts submitted commands that ingress accepted. The episode measure groups renewals as in RB-3.34. A6 has no issuing-path tags and therefore has a dash for those rows.
- The paired SE comes from the standard deviation of seed-matched differences divided by the square root of the number of available pairs. A tilde marks differences within two paired SEs. This comparison covers one pairing and five seeds.
