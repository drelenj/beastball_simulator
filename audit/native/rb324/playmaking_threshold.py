"""Measure selection under a deliberately close shot versus carry decision."""
import argparse
from collections import Counter
from dataclasses import replace
import json
from pathlib import Path

from native import cognition as C, prism_lab as lab

parser = argparse.ArgumentParser()
parser.add_argument('--out', type=Path, required=True)
args = parser.parse_args()
trials = []
for seed in lab.SEEDS:
    neutral, belief, _, draw = lab.scene(seed, 'playmaking', .7)
    _, record = C.decide(neutral, belief)
    values = {kind: value for kind, _, _, value in record['options']}
    # Force a near tie without perturbing it across paired levels.
    offset = values['carry'] - values['shoot'] + draw.uniform(-.28, .28)
    policy = replace(neutral.policy, bias_shoot=neutral.policy.bias_shoot + offset)
    decisions = {}
    for level in lab.LEVELS:
        view = replace(neutral, policy=policy, registry_ratings=(('playmaking', level),))
        intent, _ = C.decide(view, belief)
        decisions[str(level)] = intent.kind
    trials.append(dict(seed=seed, offset=offset, decisions=decisions))
counts = {str(level): dict(Counter(row['decisions'][str(level)] for row in trials)) for level in lab.LEVELS}
flips = {str(level): sum(row['decisions'][str(level)] != row['decisions']['0.7'] for row in trials)
         for level in lab.LEVELS}
args.out.write_text(json.dumps(dict(counts=counts, changes_from_0_70=flips, cases=trials), indent=2) + '\n')
