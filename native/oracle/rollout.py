"""Counterfactual grading of every option at a captured decision."""
from collections import Counter
from math import sqrt
from statistics import mean, stdev
from time import process_time

from native import prism_core

from .harness import Force, branch_seed, run
from .snapshot import restore

SUBAGENTS = {'passing':'passing','finishing':'finishing','scoring_technique':'finishing',
             'takedown':'takedown_action','evasion':'evasion_action'}


def menus(view, belief, prefix=()):
    """Read the production option objects, keeping the delivered belief fixed."""
    candidates = []
    selector = iter(prefix)

    def observe(stage, options):
        candidates.append((stage,options))
        chosen = next(selector,None)
        if chosen is not None:
            name,index = chosen
            if name != stage:
                raise ValueError('prior commitment stage mismatch')
            return index

    intent, record = prism_core.decide(view,belief,selector=observe)
    return intent, record, candidates


def describe(snapshot, stage, prefix=()):
    _, prepared = restore(snapshot,record=False)
    if prepared is None:
        raise ValueError('the snapshot must name a prepared decision')
    view,belief,_ = prepared
    _,_,candidates = menus(view,belief,prefix)
    return next((options for name,options in candidates if name == stage),())


def grade(snapshot, moment, stage, *, prefix=None, samples=20, driver=None,
          possession_returns=False):
    """Return matched option data and each deterministic rollout result."""
    if samples < 1:
        raise ValueError('samples must be positive')
    start = process_time()
    driver,prepared = restore(snapshot,driver,record=False)
    if prepared is None:
        raise ValueError('the snapshot must name a prepared decision')
    view,belief,_ = prepared
    actor = view.athlete
    _,record,candidates = menus(view,belief,prefix or ())
    options = next((opts for name,opts in candidates if name == stage),())
    if not options:
        raise ValueError(f'no {stage} menu in moment {moment}')
    if prefix is None:
        prefix = []
        for row in record['core_menus']:
            if row['stage'] == stage:
                break
            index = max(range(len(row['options'])),key=lambda i:(row['options'][i][3],-i))
            prefix.append((row['stage'],index))
    action = SUBAGENTS.get(stage)
    stop = 'possession' if possession_returns else action or 'possession'
    max_ms = 120_000 if possession_returns else 65_000 if stop == 'possession' else 5_000
    scored = []
    for option_index, option in enumerate(options):
        runs = []
        for index in range(samples):
            iteration = process_time()
            driver,prepared = restore(snapshot,driver,record=False)
            seed = branch_seed(moment,option_index,index)
            result = run(driver, prepared=prepared,force=Force(actor,stage,option_index,prefix=prefix),
                         team=view.team,stop=stop,max_ms=max_ms,seed=seed,
                         diagnostic=action if possession_returns else None)
            row = {key:value for key,value in result.items() if key != 'events'}
            row['event_counts'] = dict(Counter(event['event'] for event in result['events']))
            row['grounded'] = any(event['event'] == 'c3_grounding' and event['data'].get('counted')
                                  and event['data'].get('player') == actor for event in result['events'])
            if stop == 'possession':
                # Pass and shot features are scored on this first chosen action,
                # independently of subsequent offensive attempts.
                row['first_choice_pass'] = result['pass_result'] if result['forced_intent'] == 'pass' else None
                row['first_choice_shot'] = result['shot_result'] if result['forced_intent'] == 'shoot' else None
            row.update(index=index,seed=seed,score=result['points_for']-result['points_against'],
                       cpu_s=process_time()-iteration)
            runs.append(row)
        scores = [row['score'] for row in runs]
        scored.append({'index':option_index,'label':option.label,'owner':option.owner,
                       'hand_value':option.value,'kind':option.intent.kind,'target':option.intent.target,
                       'mean':mean(scores),'standard_error':stdev(scores)/sqrt(samples) if samples>1 else None,
                       'end_reasons':dict(Counter(row['end_reason'] for row in runs)),
                       'cpu_s_per_rollout':mean(row['cpu_s'] for row in runs),'samples':runs})
    return {'moment':moment,'actor':actor,'stage':stage,'horizon':stop,'rollouts':samples*len(options),
            'options':scored,'cpu_s_per_decision':process_time()-start}
