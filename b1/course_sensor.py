"""Provisional 3-D visual course sensor; visibility and latency come from PRISM.

Altitude is noisy; velocity is estimated from successive detections, never truth.
An independent stream leaves PRISM's existing random draws unchanged.
"""
import math
import random
from .emergence_intents import BallCourseBelief


class CourseSensor:
    def __init__(self, seed):
        self.rng = random.Random(str(seed) + '/course-z')
        self.queue, self.previous, self.delivered = [], None, None

    def capture(self, now, latency, ball, prism):
        # PRISM may not have delivered this capture yet. Read its queued noisy
        # observation, rather than using authoritative horizontal coordinates.
        obs = next((q for q in reversed(prism.queue)
                    if q[1] == prism.key('BALL') and abs(q[4]*1000-now) < .01), None)
        if obs is None:
            return
        z = max(.11, ball.z + self.rng.gauss(0, .08))
        x, y = obs[2:4]
        old = self.previous
        velocity = (0., 0., 0.)
        if old and 0 < now-old[0] <= 1000:
            dt = (now-old[0])/1000.
            velocity = tuple((v-o)/dt for v, o in zip((x,y,z), old[1:]))
        self.previous = (now, x, y, z)
        self.queue.append((now+latency, now, x, y, z, *velocity))

    def deliver(self, now, pid):
        for due, captured, x, y, z, vx, vy, vz in self.queue:
            if due <= now:
                self.delivered = BallCourseBelief(
                    f'course/{pid}/{captured}', captured, now, x,y,z,vx,vy,vz)
        self.queue = [q for q in self.queue if q[0] > now]
        return self.delivered
