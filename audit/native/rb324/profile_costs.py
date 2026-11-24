"""Break down paired cumulative profile costs for matching 1,500-step windows."""
import argparse
import json
from pathlib import Path
from pstats import Stats

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('profiles', type=Path, nargs=2)
args = parser.parse_args()

names = ('capture', 'view', 'decide', 'select_agent', 'reflex_catch_ready_at',
         'remembered_position', 'filter_velocity', 'catch_contacts', 'c3_step',
         'c3_holds_kick', 'pass_value', 'keeper_motor', 'prism_decision_interval_ms')
for profile in args.profiles:
    stats = Stats(str(profile))
    output = {}
    for path, line, name in stats.stats:
        if name in names and any(part in path for part in ('native/', 'core_src/')):
            primitive, _, inline, cumulative, _ = stats.stats[path, line, name]
            module = path[path.index('core_src/'):] if 'core_src/' in path else path[path.index('native/'):]
            output[f'{module}:{name}'] = (primitive, round(inline, 4), round(cumulative, 4))
    print(json.dumps({'profile': profile.name, 'total_s': stats.total_tt,
                      'columns': ['calls', 'self_s', 'cumulative_s'], 'functions': output}, sort_keys=True))
