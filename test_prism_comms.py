"""Tests for the PRISM communication interfaces (inert in Phase I; pathway rules when active)."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import prism_comms_v0 as C, prism_archer_v0 as A

def ok(c, m): print(('PASS ' if c else 'FAIL ') + m); assert c, m
def mk(): return A.ArcherPrism(1, .6, .5)
def warn(sender='G1', origin=(0., 0.), channel='voice', **kw): return C.Message(sender, 'warning', channel, 1.0, origin, dict(about='S9', x=40., y=10., vx=-5., vy=0., t_obs=.9), **kw)

C.COMMS_ACTIVE = False
a = mk()
ok(a.send_message('warning', 'voice', {}, (0, 0), 0) is None and a.receive_message(warn(), (5, 0), 'G2', 1.5) is False and a.update_beliefs(2.) == 0 and not a.inbox and not a.comm_bel, 'inactive: nothing sent, received or stored')
C.COMMS_ACTIVE = True
a = mk()
ok(a.receive_message(warn(), (10, 0), 'G2', 1.0) and a.update_beliefs(1.1) == 0 and a.update_beliefs(1.5) == 1, 'active: message heard, arrives after channel latency (0.35 s), then becomes a communicated belief')
ok(a.comm_bel['S9']['src'] == C.COMMUNICATED and 0 < a.comm_bel['S9']['w'] < 1, 'communicated belief is flagged and weighted below private certainty')
b = mk(); ok(b.receive_message(warn(), (60, 0), 'R1', 1.0) is False and b.comm_stats.get('missed') == 1, 'out of voice range: no pathway, not received')
n = mk(); ok(n.receive_message(warn(loudness=1.), (10, 0), 'R1', 1.0, crowd_noise=20.) is False, 'loud crowd drowns a normal call')
g = mk(); ok(g.receive_message(warn(channel='gesture'), (20, 0), 'R1', 1.0, has_los=False) is False, 'gesture needs line of sight')
o = mk(); ok(o.receive_message(warn(to=('G2',)), (12, 0), 'OPP_ARCHER', 1.0), 'an opponent in range overhears a call addressed to a teammate')
# fusion: fresher private wins; stale private loses to a fresher communicated report
a.update_beliefs(2.0)
f1 = a.fused('S9', 2.0, private=(41., 10., -5., 0., 1.5)); ok(f1['src'] == C.PRIVATE, 'fresher private belief wins')
f2 = a.fused('S9', 2.0, private=(45., 10., -5., 0., .2)); ok(f2['src'] == C.COMMUNICATED, 'stale private belief yields to a fresher communicated one')
# a lie is just a message: receiver cannot see truthful flag in its belief
lie = C.Message('R3', 'deception', 'voice', 1.0, (0., 0.), dict(about='S9', x=0., y=0., t_obs=1.0), truthful=False)
d = mk(); d.receive_message(lie, (8, 0), 'G2', 1.0); d.update_beliefs(2.0)
ok('truthful' not in d.comm_bel['S9'], 'deception is indistinguishable in the receiver belief (ground truth is metrics-only)')
# trust matters
t1 = mk(); t1.trust['G1'] = .95; t2 = mk(); t2.trust['G1'] = .2
for q in (t1, t2): q.receive_message(warn(), (10, 0), 'G2', 1.0); q.update_beliefs(2.0)
ok(t1.comm_bel['S9']['w'] > t2.comm_bel['S9']['w'], 'higher trust in the sender gives a heavier belief')
C.COMMS_ACTIVE = False
print('ALL PASS')
