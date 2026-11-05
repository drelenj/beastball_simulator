#!/bin/bash
cd /home/claude/t1_b0
for s in 1 2 3 4 5; do for rep in a b; do
  (python3 tools/t1_capture.py $s reg baseline/b0_claude_env/runs/reg_s${s}_$rep.json 2>&1 | tail -1 >> baseline/b0_claude_env/reg_progress.txt) &
  while [ $(jobs -r | wc -l) -ge 2 ]; do sleep 2; done
done; done; wait; echo ALLDONE >> baseline/b0_claude_env/reg_progress.txt
