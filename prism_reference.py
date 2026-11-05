"""PRISM v0.1.2 isolated reference mathematics; not connected to game engine.
All constants are provisional and all coordinates in meters.
"""
from dataclasses import dataclass
from math import exp, hypot, atan2, degrees
import random


def clamp(x, lo=0.0, hi=1.0): return max(lo, min(hi, x))

def cone_probability(error_deg, vision, clarity, fovea=15.0):
    theta = 60 + 60 * clamp(vision)
    e = abs(error_deg)
    if e <= fovea: return 1.0
    if e >= theta: return 0.0
    t = (e-fovea)/(theta-fovea)
    # k increases with Clarity: high Clarity retains central/peripheral detail
    # then falls more abruptly at the edge. The edge always reaches zero.
    k = 1 + 2*clamp(clarity)
    return 1 - t**k

def radar_probability(distance, radius, speed, blockers=0, crowd=0):
    """One pulse: hearing/spatial-cue abstraction, NOT visual sensing.
    Distance, motion and crowd terms are provisional engineering choices.
    """
    if distance > radius or radius <= 0: return 0.0
    range_factor = 0.2 + 0.8*(1-distance/radius)
    motion_factor = 0.1 + 0.9*(1-exp(-max(0.0,speed)/4.0))
    obstruction = 0.7**max(0,blockers)
    masking = 1/(1+0.1*max(0,crowd))
    return clamp(range_factor*motion_factor*obstruction*masking)

@dataclass
class Contact:
    track_id: int
    x: float
    y: float
    time: float
    confidence: float
    source: str
    identity: str | None = None

class Tracker:
    """Nearest-neighbor gating, one-to-one association; IDs are local tracks.
    Does not consume true simulator player IDs. Ambiguous crossings remain
    unresolved rather than granting ground-truth identity.
    """
    def __init__(self, gate=3.0, tau=2.0):
        self.gate, self.tau = gate, tau
        self.tracks = {}
        self.next_id = 1
    def update(self, observations, now):
        # observations: (x, y, source), without player ID
        candidates=[]
        for oi,(x,y,src) in enumerate(observations):
            for tid,t in self.tracks.items():
                age=max(0,now-t.time)
                gate=self.gate+age*1.0
                d=hypot(x-t.x,y-t.y)
                if d<=gate: candidates.append((d,oi,tid))
        matches={}; used=set()
        for d,oi,tid in sorted(candidates):
            if oi not in matches and tid not in used:
                matches[oi]=tid; used.add(tid)
        result=[]
        for oi,(x,y,src) in enumerate(observations):
            tid=matches.get(oi)
            if tid is None:
                tid=self.next_id;self.next_id+=1
            self.tracks[tid]=Contact(tid,x,y,now,1.0,src,
                self.tracks[tid].identity if tid in self.tracks else None)
            result.append(self.tracks[tid])
        return result
    def belief(self, now):
        return [Contact(t.track_id,t.x,t.y,t.time,
            t.confidence*exp(-max(0,now-t.time)/self.tau),t.source,t.identity)
            for t in self.tracks.values()]

def detect_radar(rng, distance, radius, speed, blockers=0, crowd=0):
    return rng.random()<radar_probability(distance,radius,speed,blockers,crowd)
