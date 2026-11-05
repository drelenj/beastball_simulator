"""PRISM v0.1.2 integration layer (DreLen decision 31 Oct: radar is an ABSTRACTION of hearing, nonvisual motion cues and spatial intuition).
Provisional parameters only. Builds on Codex's reference mathematics (prism_reference.py): cone_probability (Clarity exponent k = 1 + 2 x Clarity, late drop-off)
and radar_probability.  Adds: the eight-rating perception profile (spec v0.1.1 formulas) and an anonymous-track tracker with motion-predicted gating,
optimal one-to-one assignment and an explicit ambiguity flag for crossing tracks.
"""
import math
from dataclasses import dataclass
import numpy as np
from scipy.optimize import linear_sum_assignment
from prism_reference import cone_probability, radar_probability, clamp   # Codex reference, unchanged

RATINGS = ('vision', 'awareness', 'clarity', 'reaction', 'focus', 'instinct', 'anticipation', 'judgment')

def perception_profile(r):
    """Eight 0-1 ratings -> perception parameters.  Every formula is [P] provisional.  Returns a flat dict of named parameters."""
    g = {k: clamp(r.get(k, .5)) for k in RATINGS}
    V, A, C, R, F, I, N, J = (g[k] for k in RATINGS)
    return {
        'cone_half_angle_deg': 60 + 60 * V, 'cone_reach_m': 40 + 60 * V, 'fovea_deg': 15.0,
        'radar_radius_m': 3 + 12 * A, 'radar_bearing_sigma_deg': 25 - 15 * A,
        'cone_edge_exponent': 1 + 2 * C, 'cone_noise_scale': 1.6 - 1.2 * C,
        'delay_s': .25 * (1.3 - .6 * R), 'attention_delay_mult': .5, 'radar_extra_delay_s': .1,
        'tracked_count': 1 + round(4 * F), 'radar_pulse_period_s': .50 - .35 * F, 'gaze_slew_dps': 120 * (.6 + .8 * F), 'belief_tau_s': 1 + 3 * F, 'identify_delay_s': .15 * (1.5 - F),
        'classify_delay_s': .30 * (1.4 - .8 * I),
        'intent_blend': .7 * N,
        'options_considered': 2 + round(4 * J), 'lookahead_s': .5 + 1.5 * J, 'decision_interval_s': .2 * (1.5 - J),
    }

# which profile parameters each rating is ALLOWED to change (isolation contract)
OWNS = {
    'vision': {'cone_half_angle_deg', 'cone_reach_m'}, 'awareness': {'radar_radius_m', 'radar_bearing_sigma_deg'}, 'clarity': {'cone_edge_exponent', 'cone_noise_scale'},
    'reaction': {'delay_s'}, 'focus': {'tracked_count', 'radar_pulse_period_s', 'gaze_slew_dps', 'belief_tau_s', 'identify_delay_s'},
    'instinct': {'classify_delay_s'}, 'anticipation': {'intent_blend'}, 'judgment': {'options_considered', 'lookahead_s', 'decision_interval_s'}}

@dataclass
class Track:
    tid: int; x: float; y: float; vx: float; vy: float; t: float; n: int = 1; ambiguous: bool = False; source: str = 'cone'; last_cost: float = 0.

class Tracker2:
    """Anonymous tracks.  Gating on the track's PREDICTED position (velocity-extrapolated), optimal one-to-one assignment (Hungarian), and an ambiguity flag:
    an observation is ambiguous when its second-best track is nearly as good as its best.  Never uses true player ids; identity is not a tracker output."""
    def __init__(self, gate=3., gate_growth=1., vel_gain=.5, amb_ratio=1.6, tau=2., max_age=None):
        self.max_age = max_age; self.gate, self.gg, self.vg, self.amb, self.tau = gate, gate_growth, vel_gain, amb_ratio, tau; self.tracks = {}; self.next_id = 1
    def predict(self, tr, now): a = max(0., now - tr.t); return tr.x + tr.vx * a, tr.y + tr.vy * a
    def update(self, obs, now):
        """obs: list of (x, y, source).  Returns the Track each observation was assigned to (same order)."""
        if self.max_age is not None: self.tracks = {k: v for k, v in self.tracks.items() if now - v.t <= self.max_age}
        ids = list(self.tracks); out = [None] * len(obs)
        if obs and ids:
            C = np.full((len(obs), len(ids)), 1e6)
            for i, (x, y, _) in enumerate(obs):
                for j, tid in enumerate(ids):
                    tr = self.tracks[tid]; px, py = self.predict(tr, now); d = math.hypot(x - px, y - py)
                    if d <= self.gate + self.gg * max(0., now - tr.t): C[i, j] = d
            ri, ci = linear_sum_assignment(C)
            for i, j in zip(ri, ci):
                if C[i, j] < 1e6: out[i] = ids[j]
            amb = {}
            for i in range(len(obs)):
                if out[i] is None: continue
                row = sorted(C[i]); best = row[0]; second = row[1] if len(row) > 1 else 1e6
                amb[i] = second < 1e6 and second <= self.amb * max(best, .3)    # a rival track within the gate that is nearly as good
        else: amb = {}
        res = []
        for i, (x, y, src) in enumerate(obs):
            tid = out[i]
            if tid is None:
                tid = self.next_id; self.next_id += 1; self.tracks[tid] = Track(tid, x, y, 0., 0., now, 1, False, src)
            else:
                tr = self.tracks[tid]; dt = max(1e-3, now - tr.t)
                if now > tr.t:
                    nvx, nvy = (x - tr.x) / dt, (y - tr.y) / dt
                    tr.vx, tr.vy = (1 - self.vg) * tr.vx + self.vg * nvx, (1 - self.vg) * tr.vy + self.vg * nvy
                tr.x, tr.y, tr.t, tr.n, tr.source = x, y, now, tr.n + 1, src; tr.ambiguous = amb.get(i, False)
            res.append(self.tracks[tid])
        return res
    def confidence(self, tid, now): tr = self.tracks[tid]; return math.exp(-max(0., now - tr.t) / self.tau) * (.5 if tr.ambiguous else 1.)
