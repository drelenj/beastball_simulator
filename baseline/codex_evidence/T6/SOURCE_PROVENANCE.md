# Source Provenance and Reproduction Record

## 1. Governing baseline

| Item | Identity |
|---|---|
| Historical baseline | `B0-P4-DEFAULT` |
| Accepted source commit | `2abe497ca82588cb2d8c871a7aab61daaae95c12` |
| T1 report SHA-256 | `687cbefd47e233d123d52eaa2fccd4a1f2e207ed717786dc3f2dde143ef11eb6` |
| T1 packet SHA-256 | `2ab7c5581681b10c90aa461b2dd07d0a761aa42d8b3e05b93ed738c524e5c3b0` |
| T2 report SHA-256 | `fd2cf9eeba67081d8c087123ee1dd6bb2aa9a7153b9fb07a71fce35a9c160eee` |
| T2 packet SHA-256 | `a40744b655f5783865434ba1f62da1162fde4ce1404514611a2035339d6b4982` |
| T3 report SHA-256 | `aa8efd9a20942803c18c6d8302b04c92fd77509177163017a5861c8b27adb6b7` |
| T3 packet SHA-256 | `8d9f93436eec5ef19ba6562ec3eb09d9f37ef1f3e7dc8516c92ddb72d09ee61c` |
| T4 report SHA-256 | `606e7a7914b89ffb4efbb351cb002e6fc4a7ea5601c808423eb56144cf80d16f` |
| T4 packet SHA-256 | `634ac16eb6a5c2e4cfa806bc8bab721e510a9c3725ce13759ab64e9630380b82` |
| T5 report SHA-256 | `7b1c9ddcece27ed1e260d2457c4720677989c2b286ba6f91a145456bada9e930` |
| T5 packet SHA-256 | `824b83c1591fc22e6358e76d9d1ef122959547a1c67ecc9f00dccb11461583bb` |

## 2. Evidence inputs

| Input | Use in T6 |
|---|---|
| `HP-001_T2_EVIDENCE_REPORT.md` | patch/wrapper chain, ownership, true-state access, one decision trace, RULES_V03 and legacy-position findings |
| `HP-001_T3_FINAL_PACKET/HP-001_T3_EVIDENCE_REPORT.md` | physical trace coverage, repeatability, tolerances, provenance and gaps |
| `t4_profile/HP-001_T4_EVIDENCE_REPORT.md` | cost ownership, bounded execution, seed-2 Keeper pathology, SIGALRM limitation |
| `t5_runner/HP-001_T5_EVIDENCE_REPORT.md` | runner, manifests, RNG neutrality, telemetry and classification contracts |
| accepted source snapshot under `repo2abe497/` | implementation anchors for mechanism crosswalk |
| Claude `HP-002_reconciliation_spec_DRAFT_r3.md` | parallel architecture, IA-001, C-7, open decisions, proposed validation order |

Claude's r3 was retrieved from the user's current persistent project artifact on
2026-11-08 UTC. It is proposal/audit input; claims not rerun in HP-001 are labeled
accordingly in `HP002_RECONCILIATION.md`.

## 3. Read-only commands used to inspect evidence

From `/workspace/scratch/d09def227e01`:

```bash
python3 -c 'import json; print(json.load(open("repo2abe497/baseline/b0_claude_env/MANIFEST.json"))["commit"])'
sha256sum HP-001_T2_EVIDENCE_REPORT.md \
  HP-001_T3_FINAL_PACKET/HP-001_T3_EVIDENCE_REPORT.md \
  t4_profile/HP-001_T4_EVIDENCE_REPORT.md \
  t5_runner/HP-001_T5_EVIDENCE_REPORT.md

rg -n "def (release|shoot_arrow|arrow_impact|c4c_position|c4c2_targets|move_players|make_pass|make_shot|carrier_decision|arrow_decisions|c3_desired|c3_move|advance_ball|catch_contacts|advance_arrows|route_receiver)" \
  "repo2abe497/Beastball Pocket 2 0(1).py"

rg -n "def (release|step|shoot_arrow|make_shot)" repo2abe497/pocket4_proto.py
rg -n "def " repo2abe497/catch_v2.py repo2abe497/hand_fight_v0.py \
  repo2abe497/pose_engine_v0.py repo2abe497/condition_layer_v2.py \
  repo2abe497/beastball_locomotion_v37.py repo2abe497/locomotion_bridge_v1.py
```

The complete T1–T5 reproduction commands remain in their accepted packets. T6
does not rerun or mutate those experiments because its deliverable is paper
design.

## 4. Packet verification commands

After packet finalization:

```bash
cd /workspace/scratch/d09def227e01
find t6_design -type f -print0 | sort -z | xargs -0 sha256sum
python3 -m zipfile -l HP-001_T6_DESIGN_PACKET.zip
sha256sum HP-001_T6_DESIGN_PACKET.zip
```

`MANIFEST.sha256` covers all packet files except itself. Verification is:

```bash
cd /workspace/scratch/d09def227e01/t6_design
sha256sum -c MANIFEST.sha256
```

## 5. Environment and limitations

- Specification date: 2026-11-08 UTC.
- T6 added documentation only; it did not execute behavioral simulations.
- No cross-platform native environment exists yet, so numeric tolerances remain
  proposed rather than ratified.
- HP-002 quantitative findings were reconciled as external parallel-audit input,
  not independently reproduced in T6.
- No T3A fixtures were created because authorization was limited to paper design.
- No source, accepted evidence, feature default, rule, physics, rating, cognition,
  random stream, or supervisor was changed.
