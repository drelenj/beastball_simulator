"""Verify the archived RB-3.36 replay and table gates without rerunning matches."""
import json
from pathlib import Path

from audit.native.rb334.tables import IDENTITY, load
from .tables import render


def check():
    root = Path('audit/native/rb336/evidence')
    history = {}
    for lane in range(2):
        history.update(json.loads((root/f'history{lane}.json').read_text()))
    expected = json.loads(Path('audit/native/rb333/evidence/identity.json').read_text())
    for name in ('R1','PLANNED','compatibility','core'):
        assert all(history[name][key]==expected[name][key] for key in IDENTITY), name
    for replay,folder,name in (('RB332-1','rb333','RB332'),('A6-1','rb334','A6-1')):
        target = load(Path(f'audit/native/{folder}/evidence'),name)
        assert all(load(root,replay)[key]==target[key] for key in IDENTITY), replay
    assert (root/'legacy.txt').read_bytes()==Path('native/evidence/rb3-reach/legacy-hashes.txt').read_bytes()
    assert render(root,Path('audit/native/rb335/evidence'))==(root.parent/'TABLES.md').read_text()
    print('Verified replay identities, T3 repeat, and byte-identical tables.')


if __name__ == '__main__':
    check()
