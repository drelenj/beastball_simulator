"""Read-only agreement, gauge and versioned held-out value tables."""
from collections import Counter, defaultdict
from dataclasses import replace
from itertools import combinations
from math import sqrt
from statistics import mean

from native import prism_core

from .harness import branch_seed
from .mine import winner


def rank_agreement(options):
    """Kendall tau-b, undefined for menus tied on either side throughout."""
    concordant = discordant = tied_hand = tied_rollout = 0
    for a,b in combinations(options,2):
        h, r = a['hand_value']-b['hand_value'], a['mean']-b['mean']
        if h and r:
            if h*r>0:
                concordant += 1
            else:
                discordant += 1
        elif h:
            tied_rollout += 1
        elif r:
            tied_hand += 1
    denom = sqrt((concordant+discordant+tied_hand)*(concordant+discordant+tied_rollout))
    return (concordant-discordant)/denom if denom else None


def agreement(grades):
    stages = defaultdict(list)
    flags = []
    shot_offset = []
    for grade in grades:
        opts = grade['options']
        if len(opts) < 2:
            continue
        hand = max(opts,key=lambda o:o['hand_value'])
        best = max(o['mean'] for o in opts)
        gap = best-hand['mean']
        tau = rank_agreement(opts)
        tied = sum(o['mean'] == best for o in opts)
        stages[grade['stage']].append((tau, gap, tied))
        # Margin in observed points, not a comparison of mismatched units.
        if gap >= 1.:
            flags.append({'moment':grade['moment'],'stage':grade['stage'],'hand_best':hand['label'],
                          'rollout_best':[o['label'] for o in opts if o['mean']==best],'points_lost':gap})
        if grade['stage'] == 'carrier' and any(o['kind']=='shoot' for o in opts):
            no_offset = max(opts,key=lambda o:o['hand_value']-(prism_core.SHOT_VALUE_OFFSET if o['kind']=='shoot' else 0.))
            shot_offset.append({'moment':grade['moment'],'with':hand['label'],'without':no_offset['label'],
                                'regret_with':gap,'regret_without':best-no_offset['mean']})
    report = {}
    for stage, rows in stages.items():
        agreement_values = [tau for tau,_,_ in rows if tau is not None]
        unique = [gap for _,gap,tied in rows if tied==1]
        report[stage] = {'multi_option_moments':len(rows),'rank_defined':len(agreement_values),
                         'mean_kendall_tau_b':mean(agreement_values) if agreement_values else None,
                         'hand_best_in_rollout_best':mean(gap==0 for _,gap,_ in rows),
                         'unique_rollout_best':len(unique),
                         'hand_best_in_unique_rollout_best':mean(gap==0 for gap in unique) if unique else None,
                         'mean_points_lost':mean(gap for _,gap,_ in rows)}
    return {'by_stage':report,'flagged':flags,'shot_offset':{
        'value':prism_core.SHOT_VALUE_OFFSET,
        'moments_with_shots':len(shot_offset),
        'selection_changes':sum(row['with']!=row['without'] for row in shot_offset),
        'mean_regret_with':mean(row['regret_with'] for row in shot_offset) if shot_offset else None,
        'mean_regret_without':mean(row['regret_without'] for row in shot_offset) if shot_offset else None,
        'per_moment':shot_offset}}


def gauge(view,belief,grade,samples=20):
    baseline = dict(view.registry_ratings)
    rows = []
    for level in (.4,.7,1.):
        ratings = baseline | {'playmaking':level}
        for index in range(samples):
            seed = branch_seed(grade['moment'],'gauge',index)
            actor = replace(view,registry_ratings=tuple(ratings.items()),core_entropy=str(seed))
            _,record = prism_core.decide(actor,belief)
            menu = next(row for row in record['core_menus'] if row['stage']=='carrier')
            if [o[0] for o in menu['options']] != [o['label'] for o in grade['options']]:
                raise AssertionError('Playmaking rating changed the option set')
            chosen = winner(menu)
            selected = grade['options'][chosen]
            rows.append({'moment':grade['moment'],'level':level,'index':index,'seed':seed,
                         'choice_index':chosen,'choice':selected['label'],
                         'true_regret':max(o['mean'] for o in grade['options'])-selected['mean'],
                         'belief_regret':max(o['hand_value'] for o in grade['options'])-selected['hand_value'],
                         'perceived_regret':max(o[3] for o in menu['options'])-menu['options'][chosen][3]})
    return rows


def gauge_summary(rows):
    result = {}
    for level in (.4,.7,1.):
        trials = [row for row in rows if row['level']==level]
        result[str(level)] = {'trials':len(trials),'moments':len({r['moment'] for r in trials}),
                             'mean_true_regret':mean(r['true_regret'] for r in trials),
                             'mean_belief_regret':mean(r['belief_regret'] for r in trials),
                             'mean_perceived_regret':mean(r['perceived_regret'] for r in trials),
                             'actions':dict(Counter(r['choice'].split(':')[0] for r in trials))}
    return result


def bin_index(value, edges):
    return None if value is None else sum(value >= edge for edge in edges)


TABLES = {
    'pass_completion': (('lane_margin_m',(0.,1.5,4.)),('attempt_distance_m',(10.,20.)),('pressured',(.5,))),
    'tackle_risk': (('free_run_m',(3.,8.,12.)),),
    'shot_conversion': (('goal_distance_m',(10.,20.,30.)),('lane_margin_m',(0.,1.5,4.)),('keeper_offset_m',(1.,2.))),
    'points_by_field_position': (('field_x_m',(20.,40.,60.,80.)),('field_y_m',(25.,75.))),
}


def training_rows(moments, grades):
    features = {row['moment']:row for row in moments}
    tables = defaultdict(list)
    for grade in grades:
        moment = features[grade['moment']]
        stage = grade['stage']
        for option, values in zip(grade['options'],moment['features'],strict=True):
            for sample in option['samples']:
                seed = moment['seed']
                if option['kind']=='pass' and stage in ('carrier','passing'):
                    label = sample.get('pass_result') == 'caught'
                    tables['pass_completion'].append((seed,values,int(label)))
                if stage=='carrier' and option['kind']=='carry':
                    tables['tackle_risk'].append((seed,values,int(sample['grounded'])))
                if option['kind']=='shoot' and stage in ('carrier','finishing'):
                    label = sample.get('shot_result') == 'scored'
                    tables['shot_conversion'].append((seed,values,int(label)))
                if stage=='carrier':
                    tables['points_by_field_position'].append((seed,values,sample['score']))
    return tables


def fit(moments, grades, holdout_seed=3):
    rows = training_rows(moments,grades)
    tables = {}
    for name,axes in TABLES.items():
        train = [(values,label) for seed,values,label in rows[name] if seed != holdout_seed]
        test = [(values,label) for seed,values,label in rows[name] if seed == holdout_seed]
        if not train:
            tables[name] = {'status':'no_training_data','axes':axes,'held_out':len(test)}
            continue
        prior = mean(label for _,label in train)
        bins = defaultdict(list)

        def key(values):
            return '/'.join(str(bin_index(values.get(axis),edges)) for axis,edges in axes)

        for values,label in train:
            bins[key(values)].append(label)
        fitted = {cell:{'n':len(labels),'prediction':(sum(labels)+5*prior)/(len(labels)+5)}
                  for cell,labels in sorted(bins.items())}
        errors = [(fitted.get(key(values),{}).get('prediction',prior)-label)**2 for values,label in test]
        reference = [(prior-label)**2 for _,label in test]
        tables[name] = {'status':'fit','axes':axes,'global_prior':prior,'train':len(train),'held_out':len(test),
                        'held_out_mse':mean(errors) if errors else None,
                        'held_out_prior_mse':mean(reference) if reference else None,
                        'unseen_held_out':sum(key(values) not in fitted for values,_ in test),'bins':fitted}
    return {'schema':'oracle-drill-v0/1','target':'offline observed outcome','train_seeds':[1,2],
            'holdout_seed':holdout_seed,'smoothing_prior_trials':5,'tables':tables}
