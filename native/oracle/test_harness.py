from pathlib import Path
import ast

import pytest

from native import cognition
from native.oracle.harness import Force, run
from native.oracle.matches import match_build
from native.oracle.scenes import scene
from native.oracle.snapshot import Snapshot, capture, restore

EXAMPLES = Path(__file__).with_name('scenes')


def test_live_modules_cannot_import_oracle():
    root = Path(__file__).resolve().parents[2]
    for namespace in ('native','core_src','b1'):
        for file in (root / namespace).rglob('*.py'):
            if 'oracle' in file.parts or file.name.startswith('test_'):
                continue
            tree = ast.parse(file.read_text(), filename=str(file))
            for node in ast.walk(tree):
                if isinstance(node, (ast.Import,ast.ImportFrom)):
                    components = (getattr(node,'module',None) or '').split('.')
                    if 'oracle' in components or any('oracle' in item.name.split('.') for item in node.names):
                        pytest.fail(f'{file}:{node.lineno}: live module imports ORACLE')
                if isinstance(node, ast.Call):
                    function = getattr(node.func,'id',getattr(node.func,'attr',None))
                    if function in ('__import__','import_module') and node.args:
                        value = getattr(node.args[0],'value',None)
                        if isinstance(value,str) and 'oracle' in value.split('.'):
                            pytest.fail(f'{file}:{node.lineno}: live module dynamically imports ORACLE')


@pytest.mark.parametrize('mode', ['off','core'])
def test_snapshot_rejoins_uninterrupted_match(mode, tmp_path):
    build = match_build(1, mode, 'control')
    original = build.create()
    original.play(150)
    path = tmp_path / 'moment.snapshot.gz'
    capture(build,original).save(path)
    resumed, prepared = restore(Snapshot.load(path), record=False)
    assert prepared is None
    assert resumed.port.communication.__dict__ == original.port.communication.__dict__
    assert resumed.port.m.e.rb_coin.getstate() == original.port.m.e.rb_coin.getstate()
    for key, rng in original.port.m.rng.items():
        assert resumed.port.m.rng[key].getstate() == rng.getstate()
    for key, rng in original.port.streams.items():
        assert resumed.port.streams[key].getstate() == rng.getstate()
    original.play(220)
    resumed.play(220)
    for key in ('trace_hash','state_hash','score'):
        assert resumed.result()[key] == original.result()[key]


def test_authored_beliefs_keep_truth_separate_and_force_once():
    build, original = scene(EXAMPLES/'carrier_cut.json')
    state = original.port.m.s
    assert state.players['B:0'].x == 73
    assert next(t.x for t in original.port.frames['A:0'][-1].tracks if t.entity == 'B:0') == 71
    snapshot = capture(build,original)
    full, _ = restore(snapshot)
    result = run(full,force=Force('A:0','carrier',0),stop='time',max_ms=300)
    assert result['forced_intent'] == 'retain'
    assert result['end_reason'] == 'time_limit'
    assert result['steps'] == 3
    assert sum(i.athlete == 'A:0' for i in full.port.intents) == 1
    with pytest.raises(ValueError,match='outside'):
        run(original,force=Force('A:0','carrier',100),max_ms=300)


def test_prepared_turn_reproduces_without_reading_a_second_view():
    build, original = scene(EXAMPLES/'carrier_cut.json')
    captured = []

    def observer(view, belief, remaining):
        if view.athlete == 'A:0':
            captured.append(capture(build,original,prepared=(view,belief,remaining)))
        return cognition.decide(view,belief)

    original.advance(observer)
    resumed, prepared = restore(captured[0], record=False)
    resumed.advance(prepared=prepared)
    original.play(25)
    resumed.play(25)
    assert resumed.result()['trace_hash'] == original.result()['trace_hash']
    assert resumed.result()['state_hash'] == original.result()['state_hash']


def test_late_receiver_has_delivered_ball_course():
    _, driver = scene(EXAMPLES/'late_receiver.json')
    frame = driver.port.frames['A:0'][-1]
    state = driver.port.m.s
    assert frame.ball_course.delivered_ms == state.now
    assert (state.players['A:0'].x - state.ball.x) / state.ball.vx == pytest.approx(.30)
    assert frame.ball_course.x != state.ball.x
