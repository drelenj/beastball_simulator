"""Render match evidence as a compact Markdown table."""
import argparse
import json
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('files', type=Path, nargs='+')
args=parser.parse_args()

print('| Run | Score A–B | Possessions A/B | Terminal attempts A/B | Shots A/B | Open pass completion A/B |')
print('|---|---:|---:|---:|---:|---:|')


def pair(result,metric,format_item=str,delimiter='/'):
    return delimiter.join(format_item(result[metric][team]) for team in ('A','B'))


def percentage(value):
    return '—' if value is None else f'{100*value:.1f}%'


for path in args.files:
    r=json.loads(path.read_text())
    if r.get('status') != 'final':
        print(f'| {path.stem} | {r.get("status","missing")} | — | — | — | — |')
        continue
    print(f'| {path.stem} | {pair(r,"score",delimiter="–")} | '
          f'{pair(r,"possessions",lambda row: str(row["count"]))} | '
          f'{pair(r,"possessions",lambda row: percentage(row["share_ending_in_attempt"]))} | '
          f'{pair(r,"shots")} | {pair(r,"open_passes",lambda row: percentage(row["rate"]))} |')
