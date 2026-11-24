"""Exercise each decision hook on serialized views without an engine in scope."""
from dataclasses import replace
import json

from native import cognition as C, prism_lab as lab, prism_registry as P

names = sorted((set(lab.R.INERT_RATINGS) | set(P.NEW_RATINGS) | {'awareness', 'agility'})
               - set(P.ALIASES))
for name in names:
    tested = 0
    for seed in lab.SEEDS:
        view, belief, _, _ = lab.scene(seed, name, .9)
        encoded = json.loads(json.dumps(C.view_to_json(view, belief)))
        restored = C.view_from_json(encoded)
        assert C.decide(view, belief) == C.decide(*restored), (name, seed)
        assert lab.probe(name, .9, seed) == lab.probe(name, .9, seed), (name, seed)
        tested += 1
    print(name, tested)
