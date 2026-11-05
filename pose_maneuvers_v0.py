"""Carry-pose and maneuver state machine (spec v0.1.1).  Pure standard library, integer milliseconds, deterministic.
Poses ladder (adjacent steps only): loaded - extended - exposed - tucked - braced.  Every number marked [P] is provisional; eligibility rules are [C] (DreLen, 31 Oct).
"""
POSES = ('loaded', 'extended', 'exposed', 'tucked', 'braced')
IDX = {p: i for i, p in enumerate(POSES)}
STEP_MS = 150                                                    # [P] one adjacent-pose transition
ALLOWED = {'juke': {'exposed', 'extended', 'tucked'},             # [C] from Loaded -> Extended first; Braced -> Tucked first
           'spin': {'exposed', 'tucked', 'braced'},               # [C] at least Exposed; Extended alone is not enough
           'stiffarm': {'exposed', 'tucked'},                     # [C] never Braced (off arm busy)
           'truck': {'tucked', 'braced'}}                         # [P]
EXEC_MS = {'juke': 250, 'spin': 350, 'stiffarm': 400, 'truck': 300}   # [P] execution time
TELL_MS = {'juke': 200, 'spin': 200, 'stiffarm': 200, 'truck': 250}   # [P] visible cue window before execution
STRIP_RESIST = {'braced': 1.0, 'tucked': .8, 'exposed': .45, 'extended': .3, 'loaded': .25}   # [P]
POWER_TOUCH = .6                                                  # [P] Extended touch pass power multiplier
def touch_sigma_mult(accuracy): return 1. + .25 * (1. - max(0., min(1., accuracy)))   # [P] negligible at high accuracy

def steps_between(a, b): return abs(IDX[a] - IDX[b])
def nearest_allowed(pose, kind):
    """Allowed pose needing the fewest transition steps from `pose` (ties: toward the more secure side)."""
    return min(sorted(ALLOWED[kind], key=lambda p: -IDX[p]), key=lambda p: steps_between(pose, p))

class Carrier:
    """States: idle | transitioning | tell | executing.  A maneuver begins ONLY when no transition is in progress and the pose is allowed."""
    def __init__(self, pose='tucked'):
        assert pose in IDX; self.pose = pose; self.goal = pose; self.step_left = 0; self.step_to = pose; self.pending = None     # pending maneuver kind (waits for pose)
        self.tell_left = 0; self.exec_left = 0; self.active = None; self.pinned = False; self.log = []; self.t = 0
    # ---- queries
    @property
    def in_transition(self): return self.step_left > 0
    def tell(self): return self.pending if self.tell_left > 0 else None             # what an observer could read right now
    def strip_resistance(self):
        r = STRIP_RESIST[self.pose]
        if self.in_transition: r = min(r, STRIP_RESIST[self._next_pose()]) * .8       # [P] mid-transition: weaker of the two poses, x0.8
        return r
    def can_throw(self): return (not self.pinned) and self.pose in ('loaded', 'extended') and not self.in_transition
    def throw_ready_ms(self, kind='full'):
        tgt = 'loaded' if kind == 'full' else 'extended'; return steps_between(self.pose, tgt) * STEP_MS
    # ---- commands
    def _next_pose(self):
        return self.step_to if self.step_left > 0 else self.pose
    def _begin_step(self):
        a, b = IDX[self.pose], IDX[self.goal]
        if a != b: self.step_to = POSES[a + (1 if b > a else -1)]; self.step_left = STEP_MS
    def request_pose(self, target):
        if self.active or self.tell_left > 0: return False                           # no pose change during a maneuver or its tell
        if self.pinned and target in ('loaded', 'extended'): return False            # a high wrap pins the arms: cannot get to a throw
        self.goal = target
        if self.pose != self.goal and not self.in_transition: self._begin_step()
        return True
    def start_maneuver(self, kind):
        """Returns the minimum preparation time (ms) before the tell can begin."""
        if self.active or self.pending: return None
        self.pending = kind
        if self.pose not in ALLOWED[kind]:
            self.request_pose_force(nearest_allowed(self.pose, kind))
        elif not self.in_transition: self._begin_tell()
        return steps_between(self.pose, self.goal) * STEP_MS + max(0, self.step_left - STEP_MS if self.in_transition else 0)
    def request_pose_force(self, target):
        if self.pinned and target in ('loaded', 'extended'): self.pending = None; return
        self.goal = target
        if self.pose != self.goal and not self.in_transition: self._begin_step()
    def _begin_tell(self): self.tell_left = TELL_MS[self.pending]; self.log.append((self.t, 'tell', self.pending))
    def on_contact(self, kind='tackle'):
        """Contact interrupts: a transition in progress is aborted (pose stays the last COMPLETED pose); a pending maneuver or its tell is cancelled; an executing maneuver ends interrupted."""
        ev = 'abort_transition' if self.in_transition else ('cancel_tell' if self.tell_left > 0 else ('interrupt' if self.active else ('cancel_pending' if self.pending else None)))
        self.step_left = 0; self.goal = self.pose; self.tell_left = 0
        if self.active: self.log.append((self.t, 'interrupted', self.active)); self.active = None; self.exec_left = 0
        if ev: self.log.append((self.t, ev, self.pending)); 
        self.pending = None
    # ---- time
    def step(self, dt_ms):
        for _ in range(int(dt_ms)):
            self.t += 1
            if self.step_left > 0:
                self.step_left -= 1
                if self.step_left == 0:
                    self.pose = self.step_to; self.log.append((self.t, 'pose', self.pose))
                    if self.pose != self.goal: self._begin_step()
                    elif self.pending and self.pose in ALLOWED[self.pending]: self._begin_tell()
            elif self.tell_left > 0:
                self.tell_left -= 1
                if self.tell_left == 0:
                    assert self.pose in ALLOWED[self.pending] and not self.in_transition
                    self.active = self.pending; self.pending = None; self.exec_left = EXEC_MS[self.active]; self.log.append((self.t, 'start', self.active))
            elif self.active:
                self.exec_left -= 1
                if self.exec_left == 0: self.log.append((self.t, 'done', self.active)); self.active = None
