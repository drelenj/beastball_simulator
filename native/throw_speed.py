"""Release speed chosen by distance (RB-3.9, native-rb/3 only). Pure.

speed = clamp(distance / FLIGHT_TIME_S, MIN_SPEED_MPS, cap), cap = the athlete's existing RB/3
ceiling min(80, 0.5 x max throw speed). FLIGHT_TIME_S = 0.4 s leaves the receiver time to set his
hands (the engine's hands-set model, core_src/match.py:2176): in an isolated test every pass from
3 m to 30 m at this speed was caught, while 58 m/s passes of 6 m or less were not.
PRIMITIVE constants, unsearched.
"""
from math import hypot

FLIGHT_TIME_S = 0.4
MIN_SPEED_MPS = 10.


def cap_for(max_throw_speed):
    return min(80., .5 * max_throw_speed)


def release_speed(distance, max_throw_speed):
    return round(min(cap_for(max_throw_speed), max(MIN_SPEED_MPS, distance / FLIGHT_TIME_S)), 3)


def flight_time(distance, speed):
    """Horizontal flight time at the chosen speed (drag and arc ignored: under 3% at these ranges)."""
    return distance / max(speed, 1e-6)


def distance(a, b):
    return hypot(b[0] - a[0], b[1] - a[1])
