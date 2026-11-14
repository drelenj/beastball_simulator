"""Named match profiles for B1 matches: ONE place that says which rules and mechanics are ON.

`experiment-v1` is the profile the owner wants simulated (2026-11-13: "they should be simming the most
up to date ruleset and mechanics"): the RULES_FLOW v0.3 bundle (flat scoring, 5 m marking, discipline ladder,
always 12 on the field, 25 arrows / 5 freezes per possession, no kicking) plus the newer
catch model and off-ball hand fighting.  Contact Scrimmage is NOT in it yet: B1 has no scrimmage-restart behaviour
(snapper/tackler), so with it on the match stalls in restart_pending (measured: 59 restarts awarded, 2 released in 600 s).
`experiment-v1-scrim` is the full bundle and is the target for that work; do not run experiments under it until it passes.  `legacy-b0` reproduces the earlier B1 matches (SPRINT-45 evidence).
The effective values are read back from the built match and asserted; a mismatch raises, never silently differs.
"""
import hashlib
import json
import os

PROFILES = {
    'legacy-b0': {'env': {}, 'expect_pocket': {'inner_points': 3, 'release_points': 2, 'outside_points': 1,
                                                'carry_value': 4, 'marking_distance': 3.0}},
    'experiment-v1': {
        'env': {'RULES_V03': '1', 'RV03_FLAT': '1', 'RV03_MARK': '1', 'RV03_SCRIM': '0', 'RV03_NOKICK': '1',
                'CATCH_V2': '1', 'HAND_FIGHT': '1',
                'PRISM_CATCHERS': '0'},   # CATCH_V2 would otherwise install legacy prism_keeper_v0: a second Keeper decider (B1 owns Keeper intents), and slow
        'expect_pocket': {'inner_points': 2, 'release_points': 2, 'outside_points': 2,
                          'carry_value': 2, 'marking_distance': 5.0},
    },
}
PROFILES['experiment-v1-scrim'] = {'env': dict(PROFILES['experiment-v1']['env'], RV03_SCRIM='1'),
                                    'expect_pocket': PROFILES['experiment-v1']['expect_pocket']}
DEFAULT = 'experiment-v1'
_APPLIED = [None]


def apply(name):
    """Set the profile's environment. Call after the feature environment was cleared and before pocket4_proto is imported."""
    if name not in PROFILES:
        raise ValueError('unknown match profile %r (known: %s)' % (name, sorted(PROFILES)))
    if _APPLIED[0] not in (None, name):
        raise RuntimeError('profile %s already applied in this process; flags are read once at import, so use one process per profile' % _APPLIED[0])
    _APPLIED[0] = name
    for k, v in PROFILES[name]['env'].items():
        os.environ[k] = v
    return PROFILES[name]


def verify(name, match):
    """Read the effective values back from the built match; raise on any mismatch. Returns the record written to results."""
    prof = PROFILES[name]
    pocket = match.cfg['pocket']
    eff = {k: pocket.get(k) for k in prof['expect_pocket']}
    bad = {k: (eff[k], v) for k, v in prof['expect_pocket'].items() if eff[k] != v}
    envs = {k: os.environ.get(k) for k in prof['env']}
    bad.update({k: (envs[k], v) for k, v in prof['env'].items() if envs[k] != v})
    if bad:
        raise RuntimeError('match profile %s not in effect (got, expected): %s' % (name, bad))
    rec = {'name': name, 'env': envs, 'pocket': eff, 'ruleset': match.cfg.get('ruleset')}
    rec['digest'] = hashlib.sha256(json.dumps(rec, sort_keys=True).encode()).hexdigest()
    return rec
