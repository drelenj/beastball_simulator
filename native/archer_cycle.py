"""Deterministic draw and aim timing, plus the budget's opportunity cost."""


def cycle_ms(strength, archery_accuracy):
    draw = 1000 * (1 + .6 * (.70 - strength))
    aim = 800 * (1 + .6 * (.70 - archery_accuracy))
    return round(draw), round(aim)


def opportunity_cost(arrows, freezes, horizon_ms, duration_ms, distance):
    """Reserve scarce opportunities using the existing carrier-target value ceiling."""
    available = max(1., horizon_ms / duration_ms)
    scarcity = 1. - min(1., min(arrows, freezes) / available)
    return scarcity * max(0., 3. - .02 * distance)
