"""Fit DRILL v1 using possession returns and evaluate a match-level holdout."""
import argparse
from collections import Counter, defaultdict
from dataclasses import replace
import gzip
import json
from math import sqrt
from pathlib import Path
from statistics import mean, stdev

from native import prism_core
from native.learned_values import FEATURE_VERSION, SCHEMA, STAGES, ValueTable, option_keys, read_model

from .analysis import TABLES, agreement, bin_index, gauge_summary
from .drill_v1 import selection
from .harness import branch_seed
from .mine import winner
from .rollout import menus
from .snapshot import Snapshot, restore

HOLDOUT = (9,10)
PRIOR_TRIALS = 40


def outcome_rows(moment, grade, tables):
    stage = moment['stage']
    for option, values in zip(grade['options'],moment['features'],strict=True):
        kind = option['kind']
        for sample in option['samples']:
            if kind=='pass' and stage in ('carrier','passing'):
                result = sample.get('action_outcome',{}).get('pass',sample.get('pass_result'))
                tables['pass_completion'].append((moment['seed'],values,int(result=='caught')))
            if kind=='carry' and stage=='carrier':
                tables['tackle_risk'].append((moment['seed'],values,int(sample['grounded'])))
            if kind=='shoot' and stage in ('carrier','finishing'):
                result = sample.get('action_outcome',{}).get('shot',sample.get('shot_result'))
                tables['shot_conversion'].append((moment['seed'],values,int(result=='scored')))
            if stage=='carrier':
                tables['points_by_field_position'].append((moment['seed'],values,sample['score']))


def train_table(rows, keys_for):
    training = [(features,value) for seed,features,value in rows if seed not in HOLDOUT]
    testing = [(features,value) for seed,features,value in rows if seed in HOLDOUT]
    if not training:
        raise ValueError('cannot fit an empty table')
    prior = mean(y for _,y in training)
    cells = defaultdict(list)
    for features,value in training:
        for key in keys_for(features):
            cells[key].append(value)
    fitted = {}
    for key in sorted(cells,key=lambda key:(key.count('/'),key)):
        parent = key.rsplit('/',1)[0]
        fallback = fitted.get(parent,{}).get('prediction',prior) if parent != key else prior
        ys = cells[key]
        fitted[key] = {'n':len(ys),'prediction':(sum(ys)+PRIOR_TRIALS*fallback)/(len(ys)+PRIOR_TRIALS)}
    ordered = sorted(fitted)
    model = ValueTable(tuple(ordered),tuple(fitted[key]['prediction'] for key in ordered),prior)
    if not testing:
        raise ValueError('cannot evaluate an empty holdout')
    return {'global_prior':prior,'train':len(training),'held_out':len(testing),'bins':fitted,
            'held_out_mse':mean((model.predict(keys_for(x))-y)**2 for x,y in testing),
            'held_out_prior_mse':mean((prior-y)**2 for _,y in testing),
            'unseen_held_out':sum(keys_for(x)[-1] not in fitted for x,_ in testing)}


def read_grade(grades, row):
    return json.loads(gzip.decompress((grades/f"{row['rank']}.json.gz").read_bytes()))


def take_options(view,belief,row):
    _,_,candidates = menus(view,belief,row['prefix'])
    options = next(opts for stage,opts in candidates if stage==row['stage'])
    if [o.label for o in options] != [o[0] for o in row['menu']['options']]:
        raise ValueError('captured menu differs from the sampled menu')
    return options


def tie_count(grades):
    result = defaultdict(Counter)
    for grade in grades:
        opts = grade['options']
        stage = grade['stage']
        result[stage]['moments'] += 1
        if len(opts) == 1:
            result[stage]['single_choice'] += 1
        elif len({o['mean'] for o in opts}) == 1:
            result[stage]['all_equal_multi_choice'] += 1
        if sum(o['mean']==max(x['mean'] for x in opts) for o in opts)>1:
            result[stage]['best_ties'] += 1
        if len({o['mean'] for o in opts})==1:
            result[stage]['all_equal_including_single_choice'] += 1
    return {stage:dict(counts) for stage,counts in result.items()}


def fit(old, new, grades, out, artifact):
    selected, strata, fingerprints = selection(old,new)
    outcome_data, expected = defaultdict(list), defaultdict(list)
    about, held_out = [], []
    driver = None
    all_grades = []
    for source,row in selected:
        grade = read_grade(grades,row)
        if grade['horizon'] != 'possession':
            raise ValueError('fit requires possession returns')
        all_grades.append(grade)
        outcome_rows(row,grade,outcome_data)
        stage = row['stage']
        if stage in STAGES:
            driver, turn = restore(Snapshot.load(source/row['snapshot']),driver,record=False)
            view,belief,_ = turn
            options = take_options(view,belief,row)
            keys = option_keys(stage,view,belief,options)
            for key,option in zip(keys,grade['options'],strict=True):
                expected[stage].extend((row['seed'],key,sample['score']) for sample in option['samples'])
            if row['seed'] in HOLDOUT:
                held_out.append((view,belief,row,grade))
        about.append({**row,'source':'rb326' if source==old else 'rb327'})
    tables = {}
    for name,axes in TABLES.items():
        def keys_for(values):
            return ('/'.join(str(bin_index(values.get(axis),edges)) for axis,edges in axes),)

        tables[name] = train_table(outcome_data[name],keys_for) | {'axes':axes}
    points = {name:train_table(expected[name],tuple) for name in STAGES}
    data = {
        'schema':SCHEMA,'feature_version':FEATURE_VERSION,
        'expected_points':points,'tables':tables,'train_seeds':list(range(1,9)),
        'holdout_seeds':HOLDOUT,'target':'net points through the end of the current possession',
        'smoothing_prior_trials':PRIOR_TRIALS,
        'provenance':{'match_fingerprints':fingerprints,'strata':strata,'rollouts_per_option':20},
    }
    artifact.parent.mkdir(parents=True,exist_ok=True)
    artifact.write_text(json.dumps(data,sort_keys=True,indent=2)+'\n')
    model = read_model(artifact)
    rows = [trial for view,belief,moment,grade in held_out
            for trial in learned_gauge(model,view,belief,moment,grade)]
    reports = {stage:gauge_result([row for row in rows if row['stage']==stage]) for stage in STAGES}
    summary = {'counts':dict(Counter(row['stage'] for row in about)),
               'strata':strata,'artifact_sha256':model.digest,
               'rollouts':sum(g['rollouts'] for g in all_grades),
               'cpu_s':sum(g['cpu_s_per_decision'] for g in all_grades),
               'possession_ends':dict(Counter(s['end_reason'] for g in all_grades
                                              for o in g['options'] for s in o['samples'])),
               'action_diagnostic':dict(Counter(s['action_outcome']['reason'] for g in all_grades
                                                for o in g['options'] for s in o['samples']
                                                if 'action_outcome' in s)),
               'gauge':reports,'agreement':agreement(all_grades)}
    out.mkdir(parents=True,exist_ok=True)
    (out/'summary.json').write_text(json.dumps(summary,sort_keys=True,indent=2)+'\n')
    for name,items in (('moments',about),('grades',all_grades),('gauge',rows)):
        with gzip.open(out/f'{name}.jsonl.gz','wt',compresslevel=3) as stream:
            for item in items:
                stream.write(json.dumps(item,separators=(',',':'))+'\n')
    return summary


def learned_gauge(model, view, belief, moment, grade):
    stage = moment['stage']
    owner = 'playmaking' if stage=='carrier' else 'finishing'
    ratings = dict(view.registry_ratings)
    true_best = max(option['mean'] for option in grade['options'])
    for level in (.40,.70,1.0):
        for index in range(20):
            seed = branch_seed(grade['moment'],'gauge-v1',index)
            actor = replace(view,registry_ratings=tuple((ratings|{owner:level}).items()),core_entropy=str(seed))
            committed = iter(moment['prefix'])

            def prior_choice(name,options):
                previous = next(committed,None)
                if previous is not None:
                    previous_stage, previous_index = previous
                    if name != previous_stage:
                        raise AssertionError('Gauge did not reach the sampled commitment')
                    return previous_index

            _, record = prism_core.decide(actor,belief,learned_values=model,selector=prior_choice)
            menu = next(current for current in record['core_menus'] if current['stage']==stage)
            if [r[0] for r in menu['options']] != [o['label'] for o in grade['options']]:
                raise AssertionError('learned values changed menu feasibility')
            choice = winner(menu)
            yield {'moment':grade['moment'],'stage':stage,'level':level,'index':index,'seed':seed,
                   'choice':menu['options'][choice][0],
                   'true_regret':true_best-grade['options'][choice]['mean'],
                   'belief_regret':max(r[2] for r in menu['options'])-menu['options'][choice][2],
                   'perceived_regret':max(r[3] for r in menu['options'])-menu['options'][choice][3]}


def gauge_result(rows):
    pairs = defaultdict(dict)
    for row in rows:
        pairs[row['moment'],row['index']][row['level']] = row['true_regret']
    moment_deltas = defaultdict(list)
    for (moment,_),paired in pairs.items():
        moment_deltas[moment].append(paired[1.]-paired[.4])
    deltas = [mean(values) for values in moment_deltas.values()]
    se = stdev(deltas)/sqrt(len(deltas))
    stats = gauge_summary(rows)
    means = [stats[str(r)]['mean_true_regret'] for r in (.4,.7,1.)]
    passed = means[0]>=means[1]>=means[2] and mean(deltas)<0 and -mean(deltas)>=2*se
    return {'levels':stats,'paired_high_minus_low':mean(deltas),'paired_standard_error':se,
            'pairing_unit':'mean of 20 seed pairs within a moment','pass':passed}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--old',type=Path,required=True)
    parser.add_argument('--new',type=Path,required=True)
    parser.add_argument('--grades',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--artifact',type=Path)
    parser.add_argument('--original-only',action='store_true')
    args = parser.parse_args()
    if args.original_only:
        original,_,_ = selection(args.old,args.new,True)
        before = []
        with gzip.open('audit/native/rb326/evidence/grades.jsonl.gz','rt') as stream:
            before.extend(json.loads(line) for line in stream)
        now = [read_grade(args.grades,row) for _,row in original]
        args.out.mkdir(parents=True,exist_ok=True)
        (args.out/'original.json').write_text(json.dumps({
            'before':tie_count(before),'after':tie_count(now),'agreement':agreement(now),
            'rollouts':sum(g['rollouts'] for g in now),
            'cpu_s':sum(g['cpu_s_per_decision'] for g in now),
        },sort_keys=True,indent=2)+'\n')
    else:
        if args.artifact is None:
            parser.error('--artifact is required for a full fit')
        fit(args.old,args.new,args.grades,args.out,args.artifact)


if __name__=='__main__':
    main()
