"""Use the RB-3.14 evidence runner with the corrected RB/3 control body."""
from native.evidence.rb314.tools import soak_driver3
from native.roster import rb3_control_rosters


def main():
    soak_driver3.control_rosters = rb3_control_rosters
    soak_driver3.main()


if __name__ == '__main__':
    main()
