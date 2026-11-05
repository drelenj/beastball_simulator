# Restored historical fixtures — provenance record
Restored unchanged on 2026-11-05 with DreLen's approval (T1 completion addendum, decision 1). Commit 2abe497 is untouched: these files are added in a separate commit on top of it. No historical expected output was regenerated.

| Restored path | SHA-256 | Source |
|---|---|---|
| `LOCOMOTION_1_0_MANIFEST.json` | 13ffd74dc2fdaf1912c588d4954889b1aebded388b369214d06f8bdd6dbf9927 | `Beastball_Locomotion_1_0_Frozen.zip` (root), dated 2026-10-28 21:56 |
| `results_v37/capability_table_v37.json` | 8b6f00b148bf98e766ec57682970ec694318c9c1da6af1071eeb3fac390cf789 | same archive, dated 2026-10-28 21:45 |
| `baseline_v30_shipped/beastball_v30_results.csv` | df1b4b9209e0c9c9c16ff342f5bee732d8f77f74c6aef25ce80469ccdfb47464 | same archive, dated 2026-10-28 21:34 |

Source archive: `Beastball_Locomotion_1_0_Frozen.zip`, sha256 9220813602b5033bce7599f5e26755026e66d9a30801f1868e86c7f133e276a0 (the Locomotion 1.0 freeze package, built 2026-10-28 in an earlier Claude session).

## Verification evidence
- `capability_table_v37.json` matches the hash recorded inside `LOCOMOTION_1_0_MANIFEST.json`; the manifest's other 8 file hashes all match the files in commit 2abe497.
- Running `build_pocket_capability_v37.py` on this JSON (in a throwaway copy) reproduced `pocket_capability_v37.py` byte-for-byte (sha256 dad0b9828112c5a33286a0bb40b2d8d8c1388ac8cb74761c214ecfa24e6fd160).
- `beastball_v30_results.csv` is byte-identical in eight independent archives: `Beastball_v3_1_Work_Handoff.zip` (uploaded by DreLen) and the v3.1, v3.2, v3.3.1, v3.4, v3.5, v3.6 and v3.7 deliverable archives, plus the Frozen archive.
- With these three files present, `test_beastball_locomotion_v31.py` (OK, 5 expected failures), `test_locomotion_freeze_1_0.py` (OK) and `test_pocket_capability_v37.py` (OK) pass.
- Check yourself: `sha256sum -c` against the table above, or `git diff 2abe497 --stat` (shows only these three files plus this record).
