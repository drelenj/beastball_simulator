"""Split judgement ratings (PRISM_JSPLIT=1).  What each of DreLen's judgement ratings does in the engine (every strength [P]):
  Playmaking     prism_field_v0.noisy_rank  : the passer's choice among his pass options (rank noise, held .6 s) and the carrier's valuation of 'pass' (below).
  Finishing      judge_opts (here)          : the carrier's valuation of 'shoot' and 'carry' (expected points x (1 + FIN_SIG x (1-Finishing) x z), held .6 s) - a poor finisher mis-values his own chances.
  Marking        prism_field_v0.judge_target: which intercept option a pursuing defender picks (v3 menu, noise and habit scale with 1-Marking).
  Zone Reads     prism_field_v0 (targets)   : a defender not in pursuit of the carrier holds a position he reads with a held offset ZR_SIG x (1-Zone Reads).
  Goalkeeping    prism_keeper_v0.RT         : a Keeper's decision cadence, option count and plan-point noise come from Goalkeeping.
  Carrier Duel   pose_engine_v0.decide      : the carrier's choice among juke / spin / stiff-arm / truck / none under a closing defender - noise on the option values = CD_SIG x (1-Carrier Duel).
  Defender Duel  c3_contain / c3_region     : the defender's choice between containing and driving (and high or low hold) is flipped with probability DD_ERR x (1-Defender Duel), held 1 s.
  In-Air Ball Pursuit, Live Ball Pursuit    offball_actions_v0 : how well a player chooses WHERE to meet a passed ball / a loose ground ball (intercept option noise, both sides), and whether to commit to it.
"""
import os, math, random, zlib
import prism_ratings_v0 as PR
FIN_SIG = float(os.environ.get('PRISM_FIN_SIG', '.6')); DD_ERR = float(os.environ.get('PRISM_DD_ERR', '.5'))
def install(CO, S):
    Match = CO.match.Match
    def held(pid, key, now, win=.6): return random.Random(zlib.crc32(('%s|%s|%d|%s' % (getattr(S, 'seed', 1), pid, int(now / win), key)).encode())).gauss(0., 1.)
    def judge_opts(self, p, opts):
        rt = S.RT(p.id) if getattr(S, 'RT', None) else PR.NEUTRAL; now = self.s.now / 1000.; out = dict(opts)
        for k in ('shoot', 'carry', 'pass'):
            if k in out and out[k] > 0:
                R = PR.rj(rt, 'playmaking' if k == 'pass' else 'finishing'); out[k] = out[k] * max(0., 1. + FIN_SIG * (1. - R) * held(p.id, 'o' + k, now))
        self.stats['jopts_n'] = self.stats.get('jopts_n', 0) + 1
        return out
    Match.judge_opts = judge_opts
    def duel_flip(self, d, car, tag):
        rt = S.RT(d.id) if getattr(S, 'RT', None) else PR.NEUTRAL; DDr = PR.rj(rt, 'defender_duel'); now = self.s.now / 1000.
        u = (random.Random(zlib.crc32(('%s|%s|%s|%d|%s' % (getattr(S, 'seed', 1), d.id, car.id, int(now), tag)).encode())).random())
        return u < DD_ERR * (1. - DDr)
    o_contain = Match.c3_contain; o_region = Match.c3_region
    def c3_contain(self, d, car):
        r = o_contain(self, d, car)
        if duel_flip(self, d, car, 'c'): self.stats['dd_flips'] = self.stats.get('dd_flips', 0) + 1; return not r
        return r
    def c3_region(self, d, c, now_ms):
        r = o_region(self, d, c, now_ms)
        if duel_flip(self, d, c, 'r'):
            self.stats['dd_flips'] = self.stats.get('dd_flips', 0) + 1; reg, why = r; return ('lower' if reg == 'upper' else 'upper'), 'duel_misread'
        return r
    Match.c3_contain = c3_contain; Match.c3_region = c3_region
