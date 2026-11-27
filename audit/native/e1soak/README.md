# E1 league soak runner (Claude, lead reviewer)

Data collection only. Code under test: `codex/rb-3-39-edge` @ 939606c, config E1 (Garvian-Ala digest f207194a...b3a9),
CPython 3.13. Same 210-game schedule as the A6 soak (`schedule.json`, identical list): 100 balanced league pairings
x seeds 1-2 plus Garvian-Ala seeds 1-10, so games pair one-to-one with the A6 soak records.
Preflight verified by the lead: E1 Garvian-Ala seed 1 = 89-96, trace 8145286b...e0c5, state 175ef33b...fc05c.

    git show 'b284e822fa2f23c820987c795a2d780f16334fc3:audit/arcade/ratings/NBL_2026-27_Opening_Night_Rosters_ratings-0.4_overall-trials.xlsx' > audit/native/e1soak/ratings-0.4.xlsx
    PYTHONPATH=$PWD python3.13 -m audit.native.e1soak.run preflight audit/native/e1soak audit/native/e1soak/ratings-0.4.xlsx
    PYTHONPATH=$PWD python3.13 -m audit.native.e1soak.run play audit/native/e1soak audit/native/e1soak/ratings-0.4.xlsx 0 2 2>&1 | tee -a audit/native/e1soak/lane0.log
    PYTHONPATH=$PWD python3.13 -m audit.native.e1soak.run play audit/native/e1soak audit/native/e1soak/ratings-0.4.xlsx 1 2 2>&1 | tee -a audit/native/e1soak/lane1.log
    PYTHONPATH=$PWD python3.13 -m audit.native.e1soak.run status audit/native/e1soak
