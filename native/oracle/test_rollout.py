from pathlib import Path

from native import cognition
from native.oracle.analysis import agreement, fit, gauge, gauge_summary
from native.oracle.harness import Force, branch_seed, run
from native.oracle.mine import features
from native.oracle.rollout import grade, menus
from native.oracle.scenes import scene
from native.oracle.snapshot import capture, restore

EXAMPLE = Path(__file__).with_name('scenes')/'carrier_cut.json'


def prepared_scene():
    build, driver = scene(EXAMPLE)
    snapshots = []

    def select(view, belief, tail):
        if view.athlete == 'A:0':
            turn = view,belief,tail
            snapshots.extend(capture(build,driver,prepared=turn,compact=mode) for mode in (False,True))
        return cognition.decide(view,belief)

    driver.advance(select)
    return snapshots


def test_compact_branch_has_same_physical_result_after_reseed():
    outcomes = []
    for snapshot in prepared_scene():
        driver, prepared = restore(snapshot, record=False)
        result = run(driver,prepared=prepared,force=Force('A:0','carrier',0),
                     stop='possession',seed=branch_seed('compact',0,0))
        outcomes.append({k:v for k,v in result.items() if k!='trace_hash'})
    assert outcomes[0] == outcomes[1]


def test_options_use_distinct_repeatable_branch_seeds_and_cover_gauge():
    snapshot = prepared_scene()[1]
    graded = grade(snapshot,'scene','carrier',samples=2)
    again = grade(snapshot,'scene','carrier',samples=2)
    extract = lambda row: [[(r['seed'],r['score'],r['trace_hash']) for r in o['samples']] for o in row['options']]
    assert extract(graded) == extract(again)
    assert len({r[0] for option in extract(graded) for r in option}) == graded['rollouts']

    _, (view,belief,_) = restore(snapshot)
    _,_,candidates = menus(view,belief)
    _,measured = features(view,belief,candidates[0][1],'carrier')
    row = {'moment':'scene','seed':1,'features':measured}
    fitted = fit([row],[graded])
    assert fitted['schema'] == 'oracle-drill-v0/1'
    assert fitted['tables']['points_by_field_position']['train']==graded['rollouts']
    assert agreement([graded])['by_stage']['carrier']['multi_option_moments']==1
    ratings = gauge_summary(gauge(view,belief,graded,samples=2))
    assert ratings['1.0']['mean_belief_regret']==0.
    assert all(v['mean_perceived_regret']==0. for v in ratings.values())
