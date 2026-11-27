# Reproducing RB-3.37

Use CPython 3.13.5 and the [RB-3.34 workbook and dependencies](../rb334/README.md).

```bash
python3.13 -m audit.native.rb333.match L1 /tmp/rb334-ratings.xlsx /tmp/L1-0-1.json.gz --pair 0 --seed 1
python3.13 -m audit.native.rb337.tables audit/native/rb337/evidence audit/native/rb336/evidence /tmp/rb337-tables.md
cmp /tmp/rb337-tables.md audit/native/rb337/TABLES.md
python3.13 -m audit.native.rb337.check
python3.13 -m pytest -q b1 native
```

Pair 0 is Garvian Guardians–Ala Apex, seeds 1–5. Pair 1 is Yukïma Cowhands–Isu’Kari Sirenwings, seeds 1–3. L0 replays five archived T3 games to populate the extra observer fields and checks each against the saved score, trace, state and config digest. Raw result files embed JSON and CSV named box scores.

- A fumble is a possession ending with the ledger's fumble reason. The observer links it to the ledger's attributed athlete and the matching forced release or handoff event. A grip at release or hold-end witness in the same tick identifies wrap/takedown. The most recent collision within 100 ms identifies a no-grip collision where neither grip nor a more specific cause is witnessed. Up to 1 ms of forward tolerance accounts for the fractional witness time. Other covers unresolved or unrelated events.
- The engine ledger gives strip and reception-drop turnovers separate treatment. They appear in supplemental rows so the strict fumble causes still reconcile exactly. A drop requires an intended receiver touch followed by opposing control before the receiver secures the pass, plus a possession change. Ball Handling bands use the attributed roster rating at kickoff. Unknown marks unavailable athlete attribution.
- Juke and spin success means the athlete retained the ball for 500 live ms after an admitted move. Stiff-arm success means a recorded positive impulse. Truck success means a recorded broken contact. These measures describe the observed outcomes and have different denominators.
- Body-outs use the nearest line to the recorded boundary point. Self-run means no collision involving the carrier in the previous 500 ms. Possession durations, save rates, first-tackle shares and other inherited measures follow the [RB-3.36 definitions](../rb336/README.md).
