"""Copy of native/rulebook/reach_run.py (@ 9c37fd4) wired to soak_driver3_swap.py.
Only the import path changes; control rosters are the same rb3_control_rosters.
Run from the repo root: python3 native/evidence/rb316-swap/tools/reach_run_swap.py --block real --seed 1 --outdir <dir> [--swap]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, '/home/user/beastball_simulator')

import soak_driver3_swap  # noqa: E402
from native.roster import rb3_control_rosters  # noqa: E402


def main():
    soak_driver3_swap.control_rosters = rb3_control_rosters
    soak_driver3_swap.main()


if __name__ == '__main__':
    main()
