"""Run isolated RB-3.24 hook ablations from the pinned parent checkout."""
import argparse
import inspect
import json
from pathlib import Path
from textwrap import dedent

from native import cognition as C, cognition_rb3 as R, port as N, substrate
from native.rulebook import port as B
from native.prism_lab import neutral_rosters
from native.rulebook.config import RulebookConfigV3
from native.rulebook.rb31_soak import measure
from native.run import run_match


LAYERS = {
    'perception': ('vision', 'radar', 'clarity', 'recognition_error'),
    'recognition': ('focus', 'reaction'),
    'inference': ('instinct', 'anticipation'),
    'strategy': ('strategy',),
    'motor': ('reflex_catch', 'reflex_save', 'reflex_cadence', 'steering'),
    'execution': ('fatigue', 'touch', 'archery'),
}


def patch(host, method, edits):
    original = getattr(host, method)
    source = dedent(inspect.getsource(original))
    if isinstance(host, type):
        source = source.replace("super()", f"super({host.__name__}, self)")
    for old, new in edits:
        if source.count(old) != 1:
            raise ValueError(f'{method}: expected one anchor {old!r}')
        source = source.replace(old, new)
    scope = {}
    exec(compile(source, inspect.getsourcefile(original), 'exec'), original.__globals__, scope)
    setattr(host, method, scope[method])


def install(active):
    for module in (C, R, N, B, substrate):
        module.RB325 = active
    patch(N.NativePort, 'capture', [
        ("if individual else math.radians(120)", "if individual and 'vision' in RB325 else math.radians(120)"),
        ("if individual else .04", "if individual and 'clarity' in RB325 else .04"),
        ("if individual else 2.", "if individual and 'radar' in RB325 else 2."),
        ("sigma=z_noise if individual", "sigma=z_noise if individual and 'clarity' in RB325"),
        ("if old and len(old) == 7:", "if old and len(old) == 7 and 'instinct' in RB325:"),
        ("if course and individual else None", "if course and individual and 'recognition_error' in RB325 else None"),
    ])
    patch(N.NativePort, 'view', [
        ('if self.individuation:\n        focus', "if self.individuation and 'focus' in RB325:\n        focus"),
        ('p.native_individual[\'instinct\'], f.captured_ms', "p.native_individual['instinct'] if 'instinct' in RB325 else 0., f.captured_ms"),
        ('if self.individuation else (),\n                       registry_ratings=', "if 'strategy' in RB325 else (),\n                       registry_ratings="),
        ('items()) if self.individuation else (),\n                       recognized_ball', "items()) if 'strategy' in RB325 else (),\n                       recognized_ball"),
    ])
    patch(N.NativePort, 'decision_interval_ms', [
        ('if not self.individuation:', "if 'reaction' not in RB325:")])
    patch(N.NativePort, 'prism_decision_interval_ms', [
        ('if self.individuation and', "if 'reflex_cadence' in RB325 and")])
    patch(N.NativePort, '_submit_intent', [
        ("if self.individuation and kind != 'restart_position'", "if 'steering' in RB325 and kind != 'restart_position'")])
    patch(N.NativePort, 'ball_motor', [
        ("if self.individuation and i.kind != 'restart_pass'", "if 'touch' in RB325 and i.kind != 'restart_pass'")])
    patch(N.NativePort, 'keeper_motor', [
        ("(0. if self.individuation else", "(0. if 'reflex_save' in RB325 else"),
        ("(self.individuation and self.reflex_catch_ready_at", "('reflex_save' in RB325 and self.reflex_catch_ready_at"),
        ("if self.individuation else 1.", "if 'strategy' in RB325 else 1."),
    ])
    patch(B.RulebookPort, 'archer_motor', [
        ('if self.individuation:', "if 'archery' in RB325:")])
    patch(B.RulebookPort, 'capture', [
        ("if self.individuation and not hasattr", "if 'strategy' in RB325 and not hasattr"),
        ("if self.individuation:\n            self.visible_bodies", "if 'strategy' in RB325:\n            self.visible_bodies"),
        ("if self.individuation:\n        self.visible_bodies", "if 'strategy' in RB325:\n        self.visible_bodies"),
    ])
    patch(B.RulebookPort, 'view', [
        ('if not self.individuation and covered', "if 'strategy' not in RB325 and covered"),
        ('if self.individuation:\n            sizes', "if 'strategy' in RB325:\n            sizes"),
    ])
    patch(substrate, 'build_core', [
        ("== 'individuation/1':", "== 'individuation/1' and 'reflex_catch' in RB325:")])
    N.build_core = substrate.build_core
    patch(C, 'decide_v2', [
        ('if view.registry_ratings and course:', "if 'anticipation' in RB325 and course:"),
        ("registry_rating(view, 'anticipation'))", "dict(view.registry_ratings).get('anticipation', .7))"),
    ])
    patch(C, '_base_decide', [
        ("if view.registry_ratings else 1.\n                aim", "if 'anticipation' in RB325 else 1.\n                aim"),
        ("if view.registry_ratings:\n                t_lead *=", "if 'anticipation' in RB325:\n                t_lead *="),
        ("if course and view.prism_agent == 'in_air_ball_pursuit':", "if course and course.z > .45:"),
    ])
    patch(R, 'missed_ball_pursuit', [
        ("if view.registry_ratings:\n        trust", "if 'anticipation' in RB325:\n        trust"),
    ])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('case')
    parser.add_argument('seed', type=int)
    parser.add_argument('out', type=Path)
    parser.add_argument('--steps', type=int)
    args = parser.parse_args()
    active = set(LAYERS.get(args.case, (args.case,)))
    if args.case.startswith('without-'):
        missing = args.case.removeprefix('without-')
        active = {hook for hooks in LAYERS.values() for hook in hooks} - set(LAYERS.get(missing, (missing,)))
    if args.case == 'inference':
        active.add('remembered')
    if args.case not in ('off', 'on'):
        install(active)
    rosters = neutral_rosters(True)
    cfg = RulebookConfigV3(roster_digests=tuple(rosters[t].digest for t in ('A','B')),
                           individuation='off' if args.case == 'off' else 'individuation/1')
    if args.case not in ('on', 'off') and 'fatigue' not in active:
        object.__setattr__(cfg, 'physical_assumptions', tuple(
            (k, 0. if k == 'fatigue_rate' else v) for k, v in cfg.physical_assumptions))
    from metrics import add_metrics, observe_carries
    port = B.RulebookPort(args.seed, cfg, rosters=rosters)
    carries = observe_carries(port)
    result, port = run_match(args.seed, cfg, rosters=rosters, port_factory=lambda *a, **k: port, max_steps=args.steps)
    result.pop('prism_commits', None)
    add_metrics(result, port, carries)
    args.out.write_text(json.dumps(dict(case=args.case, hooks=sorted(active), **result), indent=2) + '\n')


if __name__ == '__main__':
    main()
