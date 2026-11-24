"""Flatten paired trial results into a reviewer-friendly table."""
import argparse
import csv
import json
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('raw', type=Path)
parser.add_argument('csv', type=Path)
args = parser.parse_args()
results = json.loads(args.raw.read_text())
with args.csv.open('w', newline='') as stream:
    writer = csv.writer(stream, lineterminator='\n')
    writer.writerow(('rating', 'level', 'paired_seeds', 'engine_quantity_mean',
                     'changes_from_0.70', 'outcomes_compared', 'evidence_scope'))
    for rating, levels in results.items():
        for level in levels:
            mean = level['metric_mean']
            writer.writerow((rating, level['level'], level['seeds'],
                             round(mean, 8) if mean is not None else '',
                             level['changed'], level['compared'], level['scope']))
