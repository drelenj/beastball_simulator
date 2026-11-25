"""Physical execution of PRISM carrier maneuvers."""
from math import hypot, sqrt

# PROVISIONAL - TO BE REPLACED BY ORACLE DRILL calibration if needed.
DODGE_GAIN = .5
GRIP_SWITCH_RETENTION = .75
STIFF_ARM_IMPULSE_RANGE = .5
TRUCK_DRIVE_RANGE = .5
STRETCH_REACH_RANGE = .18
LATE_RESPONSE_RANGE = .65
SPIN_SPEED_LOSS = .2
HURDLE_JUMP_FRACTION = .36


def maneuver(player, intent, gravity, *, skill=None):
    if intent.aim is None:
        return None
    technique = intent.technique
    if skill is None:
        skill = player.native_registry[technique]
    dx, dy = intent.aim[0]-player.x, intent.aim[1]-player.y
    if technique == 'hurdle':
        player.vz = sqrt(2 * gravity * player.a.jump_height * HURDLE_JUMP_FRACTION * skill)
        if player.vz:
            player.posture = 'airborne'
    elif technique == 'spin':
        loss = 1 - SPIN_SPEED_LOSS * (1 - skill)
        player.vx *= loss
        player.vy *= loss
        dx *= .75 + .25 * skill
    else:
        dy *= 1. + DODGE_GAIN * (skill - .7)
    return (min(99.,max(1.,player.x+dx)),min(99.,max(1.,player.y+dy)))


def reflex_gain(player):
    from .prism_registry import AVERAGE
    return 1. + LATE_RESPONSE_RANGE * (AVERAGE - player.native_registry['reflex'])


def stretch_maximum(player, hand_fraction):
    return player.a.reach * (hand_fraction - STRETCH_REACH_RANGE * (1 - player.a.ball_handling))
