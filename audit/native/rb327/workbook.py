"""Verify the pinned 0.4 workbook selection and explicit ratings readback."""
import argparse
from collections import Counter, defaultdict
from hashlib import sha256
import json
from pathlib import Path

from openpyxl import load_workbook
from native.nbl_roster import PHYSICAL, load_nbl_workbook
from match import PAIRS

SOURCE = 'b284e822fa2f23c820987c795a2d780f16334fc3'
GIT_PATH = 'audit/arcade/ratings/NBL_2026-27_Opening_Night_Rosters_ratings-0.4_overall-trials.xlsx'


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('workbook',type=Path)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    book=load_workbook(args.workbook,read_only=True,data_only=True)
    rows=book['All 712 Players'].values
    headers=next(rows)
    franchises=defaultdict(list)
    for rr in rows:
        row=dict(zip(headers,rr))
        franchises[row['Franchise']].append(row)
    book.close()
    assert sum(map(len,franchises.values()))==712 and len(franchises)==26
    covered={}
    for home,away in PAIRS:
        loaded=load_nbl_workbook(args.workbook,(home,away),technical='explicit')
        for team,franchise in zip(('A','B'),(home,away),strict=True):
            names = []
            for role, count in (('keeper',2),('archer',2),('field',18)):
                tag={'keeper':'KPR','archer':'ARC'}.get(role)
                candidates=[r for r in franchises[franchise] if (r['Position']==tag if tag
                             else r['Position'] not in ('KPR','ARC'))]
                ordered=sorted(candidates,key=lambda r:-r['OVR 0.422'])[:count]
                picked=[a for a in loaded[team].athletes if a.role==role]
                assert [a.source_id for a in picked]==[r['Player ID'] for r in ordered]
                for athlete,row in zip(picked,ordered,strict=True):
                    skills=dict(athlete.values)
                    assert not any('ovr' in key.lower() for key in skills)
                    for key,header in PHYSICAL.items():
                        if key in skills:
                            assert skills[key]==row[header]/100
                    for key in ('awareness','playmaking','finishing','ball_handling','throw_accuracy','catching'):
                        header=key.replace('_',' ').title()+' (rating)'
                        if row[header] is not None:
                            assert skills[key]==row[header]/100
                    if role=='archer':
                        assert skills['archery_accuracy']==row['Archery Accuracy (rating)']/100
                    if role=='keeper':
                        assert skills['goalkeeping']==row['Goalkeeping (rating)']/100
                    names.append({'id':athlete.source_id,'role':role,'selection_overall':row['OVR 0.422']})
            assert Counter(row['role'] for row in names)=={'keeper':2,'archer':2,'field':18}
            covered[franchise]=names
    data={'source_commit':SOURCE,'source_path':GIT_PATH,
          'sha256':sha256(args.workbook.read_bytes()).hexdigest(),
          'franchises_on_sheet':len(franchises),'players_on_sheet':sum(map(len,franchises.values())),
          'pairings':PAIRS,'selection':covered}
    args.out.write_text(json.dumps(data,sort_keys=True,indent=2)+'\n')


if __name__=='__main__':
    main()
