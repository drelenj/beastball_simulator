from dataclasses import replace
from io import BytesIO
import json

import pytest

from native import prism_core
from native.learned_values import FEATURE_VERSION, SCHEMA, read_model
from native.nbl_roster import PHYSICAL, load_nbl_workbook
from native.oracle.fit_v1 import gauge_result, train_table
from native.oracle.harness import EventHorizon
from native.oracle.rollout import menus
from native.oracle.snapshot import restore
from native.oracle.test_rollout import prepared_scene


def fixture_artifact(path):
    data = {'schema':SCHEMA,'feature_version':FEATURE_VERSION,'expected_points':{
        'carrier':{'global_prior':-.2,'bins':{'shoot':{'prediction':1.2},'carry':{'prediction':1.8}}},
        'finishing':{'global_prior':.41,'bins':{}},
    }}
    path.write_text(json.dumps(data))
    return path


def test_values_are_file_pinned_and_no_file_is_read_during_play(tmp_path):
    seed_snapshot = prepared_scene()[0]
    path = fixture_artifact(tmp_path/'drill-v1.json')
    cfg = seed_snapshot.build.config
    assert 'drill_values_sha256' not in cfg.record()
    enabled = cfg.with_drill_values(path)
    assert enabled.digest != cfg.digest
    assert 'drill_values_path' not in enabled.record()
    build = replace(seed_snapshot.build,config=enabled)
    driver = build.create(record=False)
    assert driver.port.learned_values.digest == enabled.drill_values_sha256
    path.write_text('{}')
    with pytest.raises(ValueError,match='sha256'):
        build.create(record=False)
    path.unlink()
    driver.play(35)
    assert driver.steps == 35


def test_learned_choice_is_belief_only_and_replaces_hand_values(tmp_path):
    driver, (view, belief, _) = restore(prepared_scene()[0])
    model = read_model(fixture_artifact(tmp_path/'drill-v1.json'))
    _, prior, _ = menus(view,belief)
    rerun = lambda: prism_core.decide(view,belief,learned_values=model)
    intent, result = rerun()
    menu = result['core_menus'][0]
    assert [o[0] for o in prior['core_menus'][0]['options']] == [o[0] for o in menu['options']]
    assert next(o[2] for o in menu['options'] if o[0]=='shoot:') == pytest.approx(1.2)
    assert next(o[2] for o in menu['options'] if o[0]=='carry:') == pytest.approx(1.8)
    assert intent.kind == 'carry'
    truth = driver.port.m.s
    truth.ball.x = 17
    truth.players['B:0'].x = 98
    assert rerun() == (intent,result)


def test_defender_possession_horizon_starts_with_the_offense():
    driver, _ = restore(prepared_scene()[0])
    defense = EventHorizon(driver.port,'B','possession')
    assert defense.possession_team=='A'
    assert defense.after_step(None,(),()) is None
    assert defense.consume([{'event':'restart_awarded','data':{'team':'A'}}],None) is None
    assert defense.consume([{'event':'restart_awarded','data':{'team':'B'}}],None)=='turnover'


def test_fit_keeps_holdout_away_from_prior_and_cells():
    before = train_table([(1,('pass',),1),(2,('pass',),3),(9,('pass',),50)],tuple)
    after = train_table([(1,('pass',),1),(2,('pass',),3),(10,('pass',),0)],tuple)
    assert before['bins'] == after['bins'] and before['global_prior']==2
    assert before['held_out_mse'] > after['held_out_mse']
    rows = [{'moment':m,'index':i,'level':r,'true_regret':delta*(1.-r),'belief_regret':0.,
             'perceived_regret':0.,'choice':'carry'} for m,delta in [('a',1.),('b',2.),('c',3.)]
             for i in range(20) for r in (.4,.7,1.)]
    report = gauge_result(rows)
    assert report['paired_high_minus_low'] == pytest.approx(-1.2)
    assert report['paired_standard_error'] == pytest.approx(.6/3**.5)
    assert report['pass']


def test_ovr_0422_selects_only_and_does_not_change_rating_digest():
    from openpyxl import Workbook

    def workbook(delta):
        book=Workbook()
        tab=book.active
        tab.title='All 712 Players'
        tab.append(['Franchise','Player ID','Position','Opening-day OVR','OVR 0.422',
                    'Height (m)','Mass (kg)','Arm span (m)','Standing reach (m)',
                    *PHYSICAL.values(),'Ball Handling (rating)','Goalkeeping (rating)'])
        for team in ('Home','Away'):
            for i,position in enumerate(['KPR']*3+['ARC']*3+['field']*20):
                tab.append([team,str(i),position,100-i,50+i+delta,2.4,230.,2.5,3.,
                            *([73]*len(PHYSICAL)),66,82 if position=='KPR' else None])
        stream=BytesIO()
        book.save(stream);stream.seek(0)
        return stream

    a=load_nbl_workbook(workbook(0),('Home','Away'),technical='explicit')
    b=load_nbl_workbook(workbook(1),('Home','Away'),technical='explicit')
    for team in ('A','B'):
        assert a[team].digest==b[team].digest
        assert [p.source_id for p in a[team].athletes if p.role=='keeper']==['2','1']
        assert [p.source_id for p in a[team].athletes if p.role=='archer']==['5','4']
        assert [p.source_id for p in a[team].athletes if p.role=='field']==[str(i) for i in range(25,7,-1)]
        assert all(p.get('ball_handling')==.66 for p in a[team].athletes)
        assert all(p.get('keeper_skill')==.82 for p in a[team].athletes if p.role=='keeper')
