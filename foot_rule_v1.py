"""Foot-play legality v1 (DreLen, Oct 29): unlimited foot contact between a player's first contact with the ball and the ball hitting the playing field.
After the ball has hit the field following his first contact, he may not use his feet again (hands to pick it up are fine) until legality resets.
RESET: another player touches the ball, a dead ball, any play reset (score, period start or end).
Per-player state machine for the player in possession of the ball:
  ready   : has not touched the ball since the last reset.          any contact (hand or foot) -> live
  live    : ball has been in his play since his first contact and has not touched the field.   foot: legal and stays live (unlimited);  hand: legal, stays live;  field: -> spent
  spent   : the ball touched the field after his first contact.     foot: FOUL ('second_ground_kick');  hand (pick up): legal;  stays spent until reset
A ball that bounced BEFORE his first contact (a bouncing pass) does not count: the field only matters once he is live.
RULED (DreLen, Oct 29): a 'drop kick' is a kick off the drop before the ball grounds (a volley / punt).  The traditional bounce-kick (kick as the dropped ball bounces) is NOT an exception: it is a second foot contact after the field and is a foul.  A pickup after the ball grounds leaves the player spent until a reset.  Stalling is left to defensive play.
"""
class Foul(Exception): pass
class FootRule:
    def __init__(self): self.state = 'ready'; self.log = []
    def event(self, kind):
        """kind: 'foot', 'hand', 'field' (ball touches the playing field), 'other' (another player touches it), 'dead', 'reset'.  Returns True if legal; False for a foul."""
        s = self.state; ok = True
        if kind in ('other', 'dead', 'reset'): self.state = 'ready'
        elif kind in ('foot', 'hand'):
            if s == 'ready': self.state = 'live'
            elif s == 'spent' and kind == 'foot': ok = False
        elif kind == 'field':
            if s == 'live': self.state = 'spent'
        else: raise ValueError(kind)
        self.log.append((kind, s, self.state, ok)); return ok
def run(seq):
    r = FootRule(); return [(k, r.event(k)) for k in seq], r.state
