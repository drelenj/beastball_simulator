"""Summarize the four RB-3.17 smoke runs from their durable raw logs."""
import argparse
from collections import Counter
import gzip
import json
from pathlib import Path

from .scoring_audit import match_metrics


def summarize(root):
    result = {}
    for flag in ('off', 'on'):
        runs = match_metrics(Path(root) / flag, [('real', 1), ('real', 3)])
        for row in runs:
            path = Path(row['raw_log'])
            if not path.exists():
                continue
            open_log = gzip.open if path.suffix == '.gz' else open
            with open_log(path, 'rt') as stream:
                log = json.load(stream)['log']
            counts = Counter(event['event'] for event in log)
            durations = [event['data']['duration_ms'] for event in log if event['event'] == 'block_shed']
            row['handoffs'] = {kind: counts['handoff_' + event] for kind, event in
                               [('attempted', 'start'), ('complete', 'complete'), ('fumbled', 'fumble')]}
            row['blocks'] = dict(engaged=counts['block_engaged'], shed=len(durations),
                                 mean_duration_ms=sum(durations) / len(durations) if durations else None)
            pass_count = sum(row['passes'].values())
            row['pass_interception_rate'] = row['passes'].get('opponent', 0) / pass_count if pass_count else None
        result[flag] = runs
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('root', help='directory with on/real and off/real logs')
    print(json.dumps(summarize(parser.parse_args().root), indent=2))


if __name__ == '__main__':
    main()
