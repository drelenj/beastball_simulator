"""RB/3 integration witnesses; short windows only."""
from dataclasses import replace
import io
import subprocess
from concurrent.futures import ProcessPoolExecutor

import pytest
from native import cognition as C
from native.roster import INERT_RATINGS, load_rows, mapped_values, RosterError
from native.test_attr import rows
from .config import RulebookConfigV3
from .port import RulebookPort
from .run import run_match


def fixture(change=None):
    raw=rows()
    if change:raw[0].update(change)
    rosters={team:load_rows(raw,team) for team in ('A','B')}
    cfg=RulebookConfigV3(roster_digests=tuple(rosters[t].digest for t in ('A','B')))
    return cfg,rosters


def test_acceleration_is_independent_and_large_body_is_legal():
    cfg,rs=fixture({'speed':.6,'agility':.9,'acceleration':.8,'height_m':3.447,'mass_kg':753.3})
    p=RulebookPort(1,cfg,rosters=rs)
    q=p.m.s.players['A:p0']
    assert q.a.maximum_speed==pytest.approx(26.8224)
    assert q.a.acceleration==pytest.approx(10.)
    assert q.a.braking==pytest.approx(16.875*.9)
    assert q.a.turning==pytest.approx(16.25*.9)
    assert q.a.height==3.447 and q.a.mass==753.3
    assert dict(rs['A'].warning_counts)['body_outside_design_envelope']==0
    assert mapped_values(rs['A'].athletes[0])['acceleration']==10.


@pytest.mark.parametrize('role',["keeper","archer"])
def test_specialist_field_cover_only_after_both_designated_ineligible(role):
    cfg,rs=fixture();p=RulebookPort(1,cfg,rosters=rs);e,s=p.m.e,p.m.s
    starter,backup=e.rb_designated['A'][role]
    assert e.rb_force_injury(starter)
    assert s.players[backup].active and s.players[backup].role==role
    field=next(q for q in s.players.values() if q.team=='A' and not q.active and q.role=='field')
    assert not e.rb_substitute(starter,field.id,role)
    assert e.rb_force_injury(backup)
    assert any(q.team=='A' and q.active and q.role==role and q.id not in (starter,backup) for q in s.players.values())
    assert s.phase!=p.types.Phase.FINAL


def test_contact_intent_expires_on_carrier_change_and_decision_interval():
    cfg,rs=fixture();p=RulebookPort(1,cfg,rosters=rs);s,m=p.m.s,p.m
    d=s.players['A:p0'];carrier=s.players['B:p0'];s.phase=p.types.Phase.LIVE
    s.ball.carrier=carrier.id;s.ball.mode=p.types.BallMode.CONTROLLED
    intent=C.ActionIntent('contact','decision',d.id,'tackle',carrier.id,(carrier.x,carrier.y),None,None,s.now,contact='takedown',period=s.period)
    d.native_intent=intent
    assert m.native_wrap_authorized(d,carrier) and not m.c3_contain(d,carrier)
    s.ball.carrier='B:p1'
    assert not m.native_wrap_authorized(d,carrier) and m.c3_contain(d,carrier)
    s.ball.carrier=carrier.id;s.now+=cfg.decision_ms
    assert not m.native_wrap_authorized(d,carrier) and m.c3_contain(d,carrier)


def _window(value):
    name,rating=value;cfg,rs=fixture({name:rating})
    result,_=run_match(3,cfg,max_steps=30,rosters=rs)
    return result['trace_hash'],result['state_hash'],result['config_digest']


def test_rb3_short_replay_serial_and_parallel():
    first=_window(('touch',.7))
    assert _window(('touch',.7))==first
    with ProcessPoolExecutor(2) as pool:
        assert list(pool.map(_window,[('touch',.7),('touch',.7)]))==[first,first]


def test_repeated_restart_watchdog_fails_on_third_same_spot_with_state():
    cfg,rs=fixture();p=RulebookPort(1,cfg,rosters=rs);e=p.m.e
    e.possession.dp_team=None
    for n in range(2):
        e.award('A',40.2+n*.3,20.2+n*.2,'fixture',normalize=False)
        p._watch_restart_progress()
    e.award('A',40.7,20.5,'fixture',normalize=False)
    with pytest.raises(RuntimeError,match='stuck restart invariant.*episode'):
        p._watch_restart_progress()


def test_restart_watchdog_resets_on_passive_possession_change():
    cfg,rs=fixture();p=RulebookPort(1,cfg,rosters=rs);e=p.m.e
    for team in ('A','A','B'):
        e.possession.pp=team;e.s.owner=team
        e.award(team,40.,20.,'fixture',normalize=False);p._watch_restart_progress()
    assert len(p._restart_watch)==1 and p._restart_watch[0]['team']=='B'


def test_second_same_team_restart_chain_foul_is_corrected_without_retake():
    cfg,rs=fixture();p=RulebookPort(1,cfg,rosters=rs);s,e=p.m.s,p.m.e
    s.phase=p.types.Phase.LIVE;s.owner='B';e.possession.pp='B';s.ball.carrier=None
    e.rb_restart_chain_active=True;e.rb_restart_chain_fouls=set()
    e.foul('A:p0','B:p0','holding');serial=e.restart_serial
    first=s.players['A:p0'].minor_count
    s.phase=p.types.Phase.LIVE;s.restart=None;s.ball.carrier=None
    e.foul('A:p1','B:p0','zone_unmarked')
    assert e.restart_serial==serial and s.players['A:p0'].minor_count==first==1
    assert s.players['A:p1'].minor_count==0
    assert e.rb.calls[-1]['kind']=='warning' and e.rb.calls[-1]['reason']=='repeated_restart_chain_foul'


def test_restart_foul_chain_resets_only_after_direct_control():
    cfg,rs=fixture();p=RulebookPort(1,cfg,rosters=rs);s,e=p.m.s,p.m.e
    e.rb_restart_chain_active=True;e.rb_restart_chain_fouls={'A'}
    s.ball.carrier='B:p0';e.possession.dp_team=None;e.native_sync()
    assert e.rb_restart_chain_fouls=={'A'}
    e.possession.dp_team='B';e.native_sync()
    assert not e.rb_restart_chain_active and e.rb_restart_chain_fouls==set()


def test_rb31_control_roster_uses_owner_specified_average_body():
    from .rb31_soak import uniform_rosters
    rosters=uniform_rosters()
    cfg=RulebookConfigV3(roster_digests=tuple(rosters[t].digest for t in ('A','B')))
    p=RulebookPort(1,cfg,rosters=rosters);q=p.m.s.players['A:0']
    assert q.a.height==2.39 and q.a.mass==226. and q.a.reach==3.05
    assert q.a.maximum_speed==pytest.approx(31.2928)
    assert all(value==.7 for key,value in rosters['A'].athletes[0].values if key not in ('height_m','mass_kg','reach_m'))


def test_rb31_collector_accepts_structured_carry_events():
    from .rb31_soak import measure
    cfg,rs=fixture();p=RulebookPort(1,cfg,rosters=rs);e=p.m.e
    e.rb_bands['A']['carry_attempts']=1
    arrows=[dict(t_ms=0,player='A:p20',team='A',legal=True,arrow=1,outcome='arrow_release')]
    result=measure(p,[dict(t_ms=0,team='A',player='A:p0',x=80.,y=50.)],[],arrows)
    assert result['carry_attempts']['A']['attempts']==1
    assert result['carry_attempts']['A']['outcomes']=={'other_or_match_end':1}
    assert result['arrows_by_archer']['A:p20']=={'released_no_impact':1}


@pytest.mark.parametrize('name',INERT_RATINGS)
def test_inert_rating_changes_digest_but_not_play_or_view(name):
    low,middle,high=(_window((name,value)) for value in (.4,.7,1.))
    assert low[:2]==middle[:2]==high[:2]
    assert len({low[2],middle[2],high[2]})==3
    cfg,rs=fixture({name:1.});p=RulebookPort(3,cfg,rosters=rs)
    p.capture(0);p.m.s.now=300
    v,_=p.view('A:p0',300)
    assert name not in vars(v) and name not in dict(v.own_skills)
    assert all(name not in vars(track) for track in v.tracks)
    assert name in dict(rs['A'].athletes[0].values)
    assert name not in rs['A'].athletes[0].defaults
    assert name in rs['A'].athletes[1].defaults


def test_throw_power_changes_selected_speed_and_rb_scoring_is_banded():
    from native.cognition_v3 import _intent
    speeds=[]
    for power in (.6,1.):
        cfg,rs=fixture({'throw_power':power});p=RulebookPort(1,cfg,rosters=rs)
        p.capture(0);p.m.s.now=300
        v,b=p.view('A:p0',300);speeds.append(_intent(v,b,'pass')[0].speed)
    assert speeds[0]<speeds[1]
    assert cfg.scoring=='banded'


def test_archer_pass_in_flight_predicate_restored_only_for_rb3():
    cfg,rs=fixture();p=RulebookPort(1,cfg,rosters=rs)
    p.capture(0);p.m.s.now=300
    archer=p.m.e.rb_designated['A']['archer'][0]
    v,_=p.view(archer,300)
    signals=replace(v.signals,passive_team='B',ball_status='pass_in_flight')
    v=replace(v,signals=signals,hunt_cleared=True)
    target=C.Track('B:p0','B','field',50.,50.,0.,0.,0)
    assert C.archer_target_legal(target,v,300)
    assert not C.archer_target_legal(target,replace(v,cognition='native-v0/3'),300)


def test_rb3_keeps_rb21_own_flight_and_failed_carry_measurement():
    cfg,rs=fixture();p=RulebookPort(1,cfg,rosters=rs);s,e=p.m.s,p.m.e
    s.phase=p.types.Phase.LIVE;s.owner='A';e.possession.pp='A'
    a=s.players['A:p0'];b=s.players['B:p0'];a.x,a.y=25.,50.
    s.ball=p.types.Ball(mode=p.types.BallMode.CONTROLLED,carrier=a.id,x=25.,y=50.,z=a.hand_height,scoring=True)
    assert e.release(a.id,(-25.,0.,1.),'pass','A:p1')
    b.x,b.y=s.ball.x,s.ball.y;e.touch(b.id,True)
    assert s.ball.rb_release_team=='A'
    s.ball.x,s.ball.y,s.ball.z=-1.,50.,1.5
    assert e.goal('A') and s.score['B']==2 and e.rb_bands['B']['own_goals']==1
    s.phase=p.types.Phase.LIVE;s.owner='A';a.x,a.y=80.01,50.
    s.ball=p.types.Ball(mode=p.types.BallMode.CONTROLLED,carrier=a.id,x=a.x,y=a.y,z=a.hand_height,scoring=True)
    e.follow_carrier()
    assert e.rb_bands['A']['carry_attempts']==1 and e.rb_bands['A']['carry_goals']==0


def test_rb3_f2_deflection_and_f5_defender_hold():
    cfg,rs=fixture();p=RulebookPort(1,cfg,rosters=rs);s,e=p.m.s,p.m.e
    s.phase=p.types.Phase.LIVE;s.owner='A';e.possession.pp='A'
    a=s.players['A:p0'];b=s.players['B:p0'];a.x,a.y=75.,50.
    s.ball=p.types.Ball(mode=p.types.BallMode.CONTROLLED,carrier=a.id,x=75.,y=50.,z=a.hand_height,scoring=True)
    assert e.release(a.id,(25.,0.,1.),'shot');b.x,b.y=s.ball.x,s.ball.y;e.touch(b.id,True)
    s.ball.x,s.ball.y,s.ball.z=101.,50.,1.5
    assert e.goal('B') and s.score['A']==4 and e.rb_bands['A']['own_goals']==0
    s.phase=p.types.Phase.LIVE;s.owner='A';e.possession.pp='A';s.tackle_count=0
    e.foul('B:p1','A:p1','holding')
    assert s.score['A']==5 and s.tackle_count==0


@pytest.mark.parametrize('distance,points',[(9.999,2),(10.,3),(19.999,3),(20.,4)])
def test_rb3_banded_shot_goals(distance,points):
    cfg,rs=fixture();p=RulebookPort(1,cfg,rosters=rs);s,e=p.m.s,p.m.e
    s.phase=p.types.Phase.LIVE;s.owner='A';e.rb_hunt_running=True
    a=s.players['A:p0'];a.x,a.y=100-distance,50.
    s.ball=p.types.Ball(mode=p.types.BallMode.CONTROLLED,carrier=a.id,x=a.x,y=50.,z=a.hand_height,scoring=True)
    e.follow_carrier();a.x+=(100-distance)-s.ball.x
    assert e.release(a.id,(25.,0.,1.),'shot')
    s.ball.x,s.ball.y,s.ball.z=101.,50.,1.5
    assert e.goal('B') and s.score['A']==points


def test_nbl_adapter_selects_independent_franchises_and_garvian_giant():
    openpyxl=pytest.importorskip('openpyxl')
    from native.nbl_roster import load_nbl_workbook
    path='audit/arcade/morphology/NBL_2026-27_Opening_Night_Rosters_CANON_OVR_morphology_physical.xlsx'
    blob=subprocess.check_output(['git','show','81f92e3:'+path])
    rs=load_nbl_workbook(io.BytesIO(blob),('Garvian Guardians','Ala Apex'))
    for team in ('A','B'):
        assert len(rs[team].athletes)==22
        assert [sum(a.role==role for a in rs[team].athletes) for role in ('field','keeper','archer')]==[18,2,2]
    giant=next(a for a in rs['A'].athletes if a.get('mass_kg')>750)
    assert giant.source_id=='NBL25-D32' and giant.get('mass_kg')==753.3
    assert giant.get('contact_resistance')==giant.get('balance')
    cfg=RulebookConfigV3(roster_digests=(rs['A'].digest,rs['B'].digest))
    p=RulebookPort(1,cfg,rosters=rs)
    q=p.m.s.players['A:'+giant.source_id]
    assert q.a.mass==753.3 and q.a.maximum_speed==pytest.approx(44.704*giant.get('speed'))
    p.m.e.award('A',50,50,'fixture')
    starter=p.m.e.rb_designated['A']['archer'][0]
    assert p.m.e.rb_substitute(starter,q.id,role='archer')
    assert q.active
    for _ in range(30):p.step()
    p.assert_invariants()


def test_nbl_serpents_have_two_keepers():
    pytest.importorskip('openpyxl')
    from native.nbl_roster import load_canon_nbl
    rs=load_canon_nbl(('Güunlekia Serpents','Ala Apex'))
    assert sum(a.role=='keeper' for a in rs['A'].athletes)==2


def test_updated_workbook_all_teams_and_named_canon_bodies():
    openpyxl=pytest.importorskip('openpyxl')
    from native.nbl_roster import load_canon_nbl
    path='audit/arcade/morphology/NBL_2026-27_Opening_Night_Rosters_CANON_OVR_morphology_physical.xlsx'
    blob=subprocess.check_output(['git','show','81f92e3:'+path])
    sheet=openpyxl.load_workbook(io.BytesIO(blob),read_only=True,data_only=True)['All 712 Players']
    data=iter(sheet.values);headers={name:i for i,name in enumerate(next(data))};lines=list(data)
    teams=sorted({line[headers['Franchise']] for line in lines});assert len(teams)==26
    for team in teams:
        roster=load_canon_nbl((team,team))['A']
        assert [sum(a.role==r for a in roster.athletes) for r in ('keeper','archer','field')]==[2,2,18]
    archers=[row for row in lines if row[headers['Position']]=='ARC']
    highest=max(archers,key=lambda row:row[headers['Opening-day OVR']])
    assert (highest[headers['Player ID']],highest[headers['Opening-day OVR']])==('NBL24-11-12',99)
    rs=load_canon_nbl(('Ala Marauders','Kasuf Bloodravens'))
    kamasi=next(a for a in rs['A'].athletes if a.source_id=='NBL24-02-04')
    assert kamasi.get('mass_kg')==461.8 and kamasi.get('reach_m')==3.833
    cfg=RulebookConfigV3(roster_digests=(rs['A'].digest,rs['B'].digest))
    p=RulebookPort(1,cfg,rosters=rs);q=p.m.s.players['A:NBL24-02-04']
    assert q.a.mass==461.8 and q.a.reach==3.833
