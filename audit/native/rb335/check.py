"""Verify the replay evidence and the reproducible result tables."""
import json
from pathlib import Path

from audit.native.rb334.tables import IDENTITY, load
from .tables import render


def check():
    root = Path('audit/native/rb335/evidence')
    parent = Path('audit/native/rb334/evidence')
    history = {}
    for lane in range(2):
        history.update(json.loads((root/f'history{lane}.json').read_text()))
    expected = json.loads(Path('audit/native/rb333/evidence/identity.json').read_text())
    for name in ('R1','PLANNED','compatibility','core'):
        assert all(history[name][key]==expected[name][key] for key in IDENTITY), name
    rb332 = load(Path('audit/native/rb333/evidence'),'RB332')
    assert all(load(root,'RB332-1')[key]==rb332[key] for key in IDENTITY)
    assert (root/'legacy.txt').read_bytes()==Path('native/evidence/rb3-reach/legacy-hashes.txt').read_bytes()
    assert render(root,parent)==(root.parent/'TABLES.md').read_text()
    print('Verified all saved replay fingerprints and byte-identical tables.')


if __name__ == '__main__':
    check()
