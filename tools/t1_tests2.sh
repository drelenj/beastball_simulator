#!/bin/bash
# run every test file as a script (unittest/main guards run); one fresh process each; record rc + output tail
cd /home/claude/t1_b0; D=baseline/b0_claude_env/tests2; mkdir -p $D
for f in test_*.py; do
  s=$(date +%s); timeout 1500 python3 $f > $D/${f%.py}.log 2>&1; rc=$?; e=$(date +%s)
  echo "$f rc=$rc secs=$((e-s)) last: $(tail -n 2 $D/${f%.py}.log | tr '\n' ' ' | cut -c1-160)" >> baseline/b0_claude_env/tests2_summary.txt
done; echo ALLDONE >> baseline/b0_claude_env/tests2_summary.txt
