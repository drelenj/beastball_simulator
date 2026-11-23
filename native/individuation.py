"""RB-3.23 experimental transfer functions. No world queries or random draws."""
from math import atan2, cos, hypot, radians, sin

from .roster import INERT_RATINGS

DRAFT_RATINGS = INERT_RATINGS
VERSION = 'individuation/1'


def rating(view, name):
    return next((value for key, value in view.individual_ratings if key == name), .70)


def effect(view, name, slope):
    """A bounded linear deviation around the legacy .70 reference."""
    return slope * (rating(view, name) - .70) if view.individual_ratings else 0.


def visual_half_angle(vision):
    return radians(90 + 30 * vision)


def cognitive_interval_ms(base, reaction):
    return round(base * (1.3 - .4 * reaction))


def movement_aim(x, y, aim, control):
    """Quantize steering angle. Body propulsion and collision remain unchanged."""
    dx, dy = aim[0] - x, aim[1] - y
    distance = hypot(dx, dy)
    quantum = radians(6 * (1 - control))
    if not quantum or not distance:
        return aim
    angle = round(atan2(dy, dx) / quantum) * quantum
    return (min(99.99, max(.01, x + distance * cos(angle))),
            min(99.99, max(.01, y + distance * sin(angle))))


def delivery_velocity(velocity, touch, draw):
    """Bound vertical allocation error, conserving the admitted release speed."""
    vx, vy, vz = velocity
    h = hypot(vx, vy)
    if not h:
        return velocity
    speed = hypot(h, vz)
    pitch = atan2(vz, h) + radians(2 * (1 - touch) * draw)
    return (vx / h * cos(pitch) * speed, vy / h * cos(pitch) * speed, sin(pitch) * speed)


def yaw_velocity(velocity, error_deg):
    vx, vy, vz = velocity
    error = radians(error_deg)
    return vx * cos(error) - vy * sin(error), vx * sin(error) + vy * cos(error), vz
