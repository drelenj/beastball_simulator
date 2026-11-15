"""Create the two deterministic ATTR-1 validation rosters from player_gen_v1."""
from __future__ import annotations

import csv
from pathlib import Path

from player_gen_v1 import RATINGS,generate

POSITIONS=(
    ['utility','runner','receiver','forward','lineman','backer','corner','safety','passer']*2
    +['keeper','keeper','archer','archer']
)
FIELDS=('id','role','height_m','mass_kg','reach_m',*RATINGS,'name','position','archetype','overall')


def build(team):
    rows=[]
    for index,position in enumerate(POSITIONS):
        overall=.74+((index*7+(0 if team=='A' else 3))%15)/100
        name=f'ATTR-{team}-{index+1:02d}'
        athlete=generate(name,position,overall)
        row=dict(id=f'{team.lower()}{index+1:02d}',role=athlete['role'],height_m=athlete['height_m'],
                 mass_kg=athlete['mass_kg'],reach_m=athlete['reach_m'],name=name,position=position,
                 archetype=athlete['archetype'],overall=athlete['overall'],**athlete['ratings'])
        rows.append(row)
    return rows


def write(path,rows):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',newline='',encoding='utf-8') as stream:
        writer=csv.DictWriter(stream,fieldnames=FIELDS);writer.writeheader();writer.writerows(rows)


def main(directory='native/evidence/attr1/rosters'):
    directory=Path(directory)
    for team in ('A','B'):write(directory/f'team-{team}.csv',build(team))


if __name__=='__main__':main()
