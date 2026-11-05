"""Labs for the split judgement ratings.  usage: N=24 python3 judge_labs.py [duel finishing playmaking]
 duel        Carrier Duel x Defender Duel: carrier A1 runs at goal, defender B0 pursues; P(carrier stopped within 6 s) in a 2x2 of ratings (.40 / .98)
 finishing   Finishing: carrier 18 m out with a defender 6 m away; how often he shoots rather than carries/passes in 4 s, and goals, at Finishing .40 / .98
 playmaking  Playmaking: carrier mid-field with three team-mates (one clearly open); how often the best-ranked pass option is the open one, at Playmaking .40 / .98"""
import sys, os, math, json, collections
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import offball_scenarios as O
def duel(a):
    cfg, seed = a; p, CO, S, Ty, m, s = O.world(dict(), dict(), cfg['ra'], cfg['rb'], seed)
    s.owner = 'A'; pk = O.park(p, s, ('A0', 'A1', 'B0')); O.hold(p, s); A1, B0 = s.players['A1'], s.players['B0']
    O.place(A1, 35., 50., (1., 0.)); O.place(B0, 55. + (seed % 3), 50. + (seed % 5 - 2) * .6, (-1., 0.))
    s.ball = Ty.Ball(mode=Ty.BallMode.CONTROLLED, carrier='A1', control_time=s.now - 500, last_touch='A'); m.e.follow_carrier()
    import prism_field_v0 as PF; PF.SKIP.clear(); PF.SKIP.update(pk + ['A0'])
    for g in range(60):
        m.step()
        if s.ball.carrier != 'A1' or A1.posture == 'grounded': return a, dict(stopped=1, t=g, x=A1.x)
    return a, dict(stopped=0, t=60, x=A1.x)
def finishing(a):
    cfg, seed = a; p, CO, S, Ty, m, s = O.world(dict(), dict(), cfg['ra'], cfg['rb'], seed)
    s.owner = 'A'; pk = O.park(p, s, ('A0', 'A1', 'B0')); O.hold(p, s); A1, B0 = s.players['A1'], s.players['B0']
    O.place(A1, 82., 46. + (seed % 5), (1., 0.)); O.place(B0, 76., 50., (1., 0.))
    s.ball = Ty.Ball(mode=Ty.BallMode.CONTROLLED, carrier='A1', control_time=s.now - 500, last_touch='A'); m.e.follow_carrier()
    import prism_field_v0 as PF; PF.SKIP.clear(); PF.SKIP.update(pk + ['A0'])
    ch = []
    for g in range(40):
        m.step()
        ch = [e['data'].get('choice') for e in m.e.log if e['event'] == 'controller_decision']
        if 'shoot' in ch or 'pass' in ch or s.ball.carrier != 'A1': break
    return a, dict(shot='shoot' in ch, carry='carry' in ch, goal=any(e['event'] == 'goal' for e in m.e.log))
def playmaking(a):
    cfg, seed = a; p, CO, S, Ty, m, s = O.world(dict(), dict(), cfg['ra'], cfg['rb'], seed)
    s.owner = 'A'; pk = O.park(p, s, ('A0', 'A1', 'A2', 'A3', 'A4', 'B0', 'B1', 'B2')); O.hold(p, s)
    A1 = s.players['A1']; O.place(A1, 50., 50., (1., 0.)); O.place(s.players['A2'], 60., 40., (1., 0.)); O.place(s.players['A3'], 62., 60., (1., 0.)); O.place(s.players['A4'], 58., 50., (1., 0.))
    O.place(s.players['B0'], 59., 41.5, (-1., 0.)); O.place(s.players['B1'], 57., 49., (-1., 0.)); O.place(s.players['B2'], 52., 45., (-1., 0.))
    s.ball = Ty.Ball(mode=Ty.BallMode.CONTROLLED, carrier='A1', control_time=s.now - 500, last_touch='A'); m.e.follow_carrier(); A1.next_decision = s.now + 10 ** 7; O.PARKED.update(('A1',))
    import prism_field_v0 as PF; PF.SKIP.clear(); PF.SKIP.update(pk + ['A0']); best = 0; n = 0
    for g in range(40):
        m.step()
        if g >= 8 and g % 6 == 0:
            r = m.pol['A'].pass_ranked(s, A1)
            if r: n += 1; best += (r[0].id == 'A3')
    return a, dict(n=n, best=best)
LABS = dict(duel=duel, finishing=finishing, playmaking=playmaking)
def lo_hi(k): return {'.40': {k: .40}, '.98': {k: .98}}
if __name__ == '__main__':
    N = int(os.environ.get('N', '24')); which = sys.argv[1:] or list(LABS)
    if 'duel' in which:
        for cd in (.4, .98):
            for dd in (.4, .98):
                res = [duel(({'ra': {'carrier_duel': cd}, 'rb': {'defender_duel': dd}}, sd))[1] for sd in range(1, N + 1)]
                print(f"duel  Carrier Duel {cd:.2f}  Defender Duel {dd:.2f}   P(carrier stopped) {sum(r['stopped'] for r in res)/N:.2f}   mean progress {sum(r['x'] for r in res)/N - 35:.1f} m", flush=True)
    if 'finishing' in which:
        for f in (.4, .98):
            res = [finishing(({'ra': {'finishing': f}, 'rb': None}, sd))[1] for sd in range(1, N + 1)]
            print(f"finishing  Finishing {f:.2f}   shoots {sum(r['shot'] for r in res)}/{N}   carries {sum(r['carry'] for r in res)}/{N}   goals {sum(r['goal'] for r in res)}/{N}", flush=True)
    if 'playmaking' in which:
        for f in (.4, .98):
            res = [playmaking(({'ra': {'playmaking': f}, 'rb': None}, sd))[1] for sd in range(1, N + 1)]
            n = sum(r['n'] for r in res); print(f"playmaking  Playmaking {f:.2f}   best option first {sum(r['best'] for r in res)}/{n} = {sum(r['best'] for r in res)/max(1,n):.2f}", flush=True)
