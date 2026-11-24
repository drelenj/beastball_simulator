"""Compare 100 ms fixed-tick cadence with carried Reaction deadlines."""
import csv
from math import ceil
import sys

from native.run import reaction_deadline


def sweep():
    for rating in (.4, .5, .6, .7, .8, .9, 1., .783):
        interval = 500 * (1 + .4 * (.70 - rating))
        clock = now = 0
        for _ in range(10_000):
            clock = reaction_deadline(now, clock, interval)
            now = 100 * ceil((clock - 1e-6) / 100)
        yield rating, round(interval,10), 100 * ceil(interval / 100), now / 10_000


if __name__ == '__main__':
    writer = csv.writer(sys.stdout, lineterminator='\n')
    writer.writerow(('reaction','target_ms','before_ms','after_ms'))
    writer.writerows(sweep())
