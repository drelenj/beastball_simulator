"""Full historical identity replays for the final source."""
import argparse
import json
from pathlib import Path
from audit.native.rb330.check import assert_identity
from audit.native.rb330.verify import identity
from audit.native.rb332.match import match


def main():
    p=argparse.ArgumentParser()
    p.add_argument('book',type=Path)
    p.add_argument('evidence',type=Path)
    p.add_argument('--modes',nargs='+',choices=('compatibility','core','R1','PLANNED'),default=('compatibility','core','R1','PLANNED'))
    args=p.parse_args()
    expected=json.loads(Path('audit/native/rb332/evidence/identity.json').read_text())
    checks={}
    for mode in args.modes:
        if mode in ('compatibility','core'):
            row=identity(mode)
        else:
            row,_=match(args.book,mode,0,1,scale=.52,diagnostics=False)
        assert_identity(row,expected[mode])
        checks[mode]={k:row[k] for k in ('score','trace_hash','state_hash','config_digest')}
        print(mode,checks[mode],flush=True)
        args.evidence.write_text(json.dumps(checks,indent=2)+'\n')

if __name__=='__main__':
    main()
