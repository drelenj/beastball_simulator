#!/bin/bash
cd /home/claude/t1_b0
for f in test_*.py; do
  timeout 1500 python3 tools/t1_run_tests.py $f baseline/b0_claude_env/tests/${f%.py}.json >> baseline/b0_claude_env/tests_progress.txt 2>&1 || echo "$f TIMEOUT_OR_CRASH rc=$?" >> baseline/b0_claude_env/tests_progress.txt
done; echo ALLDONE >> baseline/b0_claude_env/tests_progress.txt
