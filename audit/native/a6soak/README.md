# A6 soak runner (written by Claude, lead reviewer)

Data collection only. Code under test: `codex/rb-3-34-carry-value` @ 9d4de6d, config A6
(digest c6dfe491...bd44 for Garvian-Ala), CPython 3.13. 210 games in `schedule.json`: 100 balanced league
pairings (every team 7-8 different opponents) x seeds 1 and 2, plus Garvian Guardians-Ala Apex seeds 1-10.
Each game writes `games/<id>.json.gz` (score, hashes, named box score, events, passes, boundary and Keeper
records). A crash writes `games/<id>.failed` with the traceback and the lane moves on.
Diagnostics observer off (verified: preflight reproduces the RB-3.34 A6 seed-1 hashes exactly).

    PYTHONPATH=$PWD python3.13 -m audit.native.a6soak.run preflight audit/native/a6soak audit/native/a6soak/ratings-0.4.xlsx
    bash audit/native/a6soak/soak.sh 0      # lane 0
    bash audit/native/a6soak/soak.sh 1      # lane 1 (second terminal)
    PYTHONPATH=$PWD python3.13 -m audit.native.a6soak.run status audit/native/a6soak
