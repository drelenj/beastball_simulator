# Reproducing RB-3.36

Use CPython 3.13.5 and the same workbook and dependencies as RB-3.35. Import the workbook using the [RB-3.34 command](../rb334/README.md). The expected workbook hash is 47b48af7a19035428d517582370fa1782b542980c783edf3dfb20619cf437fba.

```bash
python3.13 -m audit.native.rb333.match T3 /tmp/rb334-ratings.xlsx /tmp/T3-1.json.gz --seed 1
python3.13 -m audit.native.rb336.tables audit/native/rb336/evidence audit/native/rb335/evidence /tmp/rb336-tables.md
cmp /tmp/rb336-tables.md audit/native/rb336/TABLES.md
python3.13 -m pytest -q b1 native
python3.13 -m native.rulebook.scoring_audit --legacy
```

- Every per-game file contains the named box as JSON and CSV text. The renderer reuses all five B4 records and checks B4 seed 1 against a new replay. It also checks the T3 repeat, excluding measured CPU and sampled profiling data.
- Possession duration is elapsed time between consecutive possession starts. It includes ordinary restart time. It excludes possessions ending at a period boundary and the last possession, where the next start would include an intermission or is absent.
- Tackle shares use the possession spanning an observed grounding at the stated count. An offensive minor or procedural penalty can increase the count without a grounding. RB-3.35 recorded tackle 1 times and explicitly labelled second-tackle ends. Its inferred tackle 2 share uses those endings.
- A held end-line flight counts when the same carrier's ball crossed the end plane between recorded physics steps and remained held after adjudication. Carrier exits are attributed to a collision in the previous 500 ms or to no recent contact. The other turnover, receiving and save measures use the [RB-3.35 definitions](../rb335/README.md).
- Reach readiness counts one possible hand contact per athlete per ball course. The release team distinguishes a catch from an interception attempt. A successful acquire must lead to control. A counted deflection is a committed hand touch, which can be a failed secure attempt in the catch/interception denominator. Passive body blocks never pay a reactive delay.
- Wraps and takedowns count once per selected contact episode. A renewal on the same target retains the original deadline. Success means an adjudicated grounding. Loose-ball pursuit pays at the start of a pursuit using a delivered loose-ball signal. Own passes, own carries and ordinary running pay no cost.
- The B4 raw records predate the reaction observer. The B4 field cost is zero by configuration, with the measured success split unavailable. C0 and C1 supply the comparison without any field unset cost.
- Set speed is 0.40 seconds times the athlete's effective braking. The Agility table uses opening roster bodies. In-game thresholds follow any effective braking changes. The Keeper retains the existing 0.10 s unset time and the field readiness code reads the same time as unset_s. The old Keeper assumption key remains for historical configurations.
