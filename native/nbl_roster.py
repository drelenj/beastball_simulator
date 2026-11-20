"""Opening night workbook adapter for native-rb/3. Labels select eligibility only."""
from .roster import load_rows, RosterError

PHYSICAL = {
    'speed':'Speed (rating)', 'strength':'Strength (rating)',
    'jump':'Jumping (rating)', 'acceleration':'Acceleration (rating)',
    'agility':'Agility (rating)', 'balance':'Balance (rating)',
    'throw_power':'Throw Power (rating)', 'stamina':'Stamina (rating)',
    'durability':'Durability (rating)',
}
TECHNICAL_OVR = ('tackling','blocking','ball_handling','catching','awareness',
                 'throw_accuracy','keeper_skill','archery_accuracy')


def load_nbl_workbook(source, franchises):
    """Choose each franchise's top OVR 2 KPR, 2 ARC, 18 field; ties keep sheet order.

    Technical skills use OVR/100, contact resistance uses Balance/100: PLACEHOLDER.
    No player labels enter the validated attribute record.
    """
    from openpyxl import load_workbook
    book=load_workbook(source,read_only=True,data_only=True)
    sheet=book['All 712 Players'];lines=sheet.values
    columns={name:i for i,name in enumerate(next(lines))}
    candidates={team:[] for team in franchises}
    for number,line in enumerate(lines,start=2):
        franchise=line[columns['Franchise']]
        if franchise in candidates:candidates[franchise].append((number,line))
    out={}
    for side,franchise in zip(('A','B'),franchises):
        if not candidates.get(franchise):raise RosterError(f'franchise {franchise}: no roster rows')
        selected=[]
        for code,count,role in (('KPR',2,'keeper'),('ARC',2,'archer'),('field',18,'field')):
            pool=[(number,row) for number,row in candidates[franchise]
                  if (row[columns['Position']]==code if code!='field' else row[columns['Position']] not in ('KPR','ARC'))]
            pool.sort(key=lambda item:-item[1][columns['Opening-day OVR']])
            if len(pool)<count:raise RosterError(f'franchise {franchise}: fewer than {count} {code} players')
            for number,row in pool[:count]:
                rating=lambda field:float(row[columns[field]])/100.
                entry=dict(id=str(row[columns['Player ID']]),role=role,
                           height_m=float(row[columns['Height (m)']]),mass_kg=float(row[columns['Mass (kg)']]),
                           reach_m=float(row[columns['Arm span (m)']]) / 2.,
                           standing_reach_m=float(row[columns['Standing reach (m)']]))
                entry.update({key:rating(header) for key,header in PHYSICAL.items()})
                entry.update({key:rating('Opening-day OVR') for key in TECHNICAL_OVR})
                entry['contact_resistance']=entry['balance'] # PLACEHOLDER
                selected.append(entry)
        out[side]=load_rows(selected,side)
    return out


def load_canon_nbl(franchises,ref='81f92e3'):
    """Read the owner workbook from a local Git object without copying it into this branch."""
    import io
    import subprocess
    path='audit/arcade/morphology/NBL_2026-27_Opening_Night_Rosters_CANON_OVR_morphology_physical.xlsx'
    blob=subprocess.check_output(['git','show',ref+':'+path])
    return load_nbl_workbook(io.BytesIO(blob),franchises)
