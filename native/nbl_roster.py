"""Opening night workbook adapter for native-rb/3. Labels select eligibility only."""
from dataclasses import replace

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
# RB-3.22 talent source (diagnosis only; defaults reproduce the RB-3.21 rosters exactly)
TECHNICAL_SOURCES = ('ovr', 'neutral')
PHYSICAL_SOURCES = ('roster', 'neutral')
NEUTRAL_TECHNICAL = .784          # the league mean Opening-day OVR / 100 (owner/lead figure)
STAGED_HEADERS = {
    'tackling': 'Tackling', 'blocking': 'Blocking', 'ball_security': 'Ball security',
    'passing': 'Passing', 'finishing': 'Finishing', 'long_shot': 'Long shot',
    'catching': 'Catching', 'evasion': 'Evasion', 'keeping': 'Keeping', 'archery': 'Archery',
    'vision': 'Vision', 'anticipation': 'Anticipation', 'reaction': 'Reaction',
    'judgment': 'Judgment', 'composure': 'Composure', 'discipline': 'Discipline',
    'aggression': 'Aggression', 'work_rate': 'Work rate',
}


def _stage_ratings(row, columns, number, fallback):
    values, defaults = [], []
    for key, label in STAGED_HEADERS.items():
        index = columns.get(label, columns.get(f'{label} (rating)'))
        raw = row[index] if index is not None else None
        if raw is None or (isinstance(raw, str) and not raw.strip()):
            values.append((key, fallback))
            defaults.append(key)
            continue
        try:
            rating = float(raw)
        except (ValueError, TypeError):
            raise RosterError(f'row {number} column {label}: expected a rating in 0..100') from None
        if not 0 <= rating <= 100:
            raise RosterError(f'row {number} column {label}: rating {rating} outside 0..100')
        values.append((key, rating / 100.))
    return tuple(values), tuple(defaults)


def load_nbl_workbook(source, franchises, technical='ovr', physical='roster'):
    """Choose each franchise's top OVR 2 KPR, 2 ARC, 18 field; ties keep sheet order.

    Technical skills use OVR/100, contact resistance uses Balance/100: PLACEHOLDER.
    No player labels enter the validated attribute record. Optional draft technical
    and mental workbook columns use the same 0..100 scale, with an OVR fallback;
    they are stored separately from the active attributes and gameplay digest.
    RB-3.22: technical='neutral' sets every technical skill to NEUTRAL_TECHNICAL; physical='neutral' sets each of the nine
    physical ratings to its league mean (all players on the sheet); bodies (height, mass, arm span, standing reach) are
    unchanged. Starters are chosen by OVR in every mode, so the same players play.
    """
    if technical not in TECHNICAL_SOURCES or physical not in PHYSICAL_SOURCES:
        raise RosterError(f'talent source: technical {technical!r} / physical {physical!r}')
    from openpyxl import load_workbook
    book=load_workbook(source,read_only=True,data_only=True)
    sheet=book['All 712 Players'];lines=sheet.values
    columns={name:i for i,name in enumerate(next(lines))}
    candidates={team:[] for team in franchises}
    league={key:[] for key in PHYSICAL}
    for number,line in enumerate(lines,start=2):
        franchise=line[columns['Franchise']]
        if franchise in candidates:candidates[franchise].append((number,line))
        if line[columns['Player ID']] is not None:
            for key,header in PHYSICAL.items():league[key].append(float(line[columns[header]])/100.)
    league_mean={key:sum(v)/len(v) for key,v in league.items()}
    out={}
    for side,franchise in zip(('A','B'),franchises):
        if not candidates.get(franchise):raise RosterError(f'franchise {franchise}: no roster rows')
        selected=[]
        staged=[]
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
                entry.update({key:(league_mean[key] if physical=='neutral' else rating(header)) for key,header in PHYSICAL.items()})
                entry.update({key:(NEUTRAL_TECHNICAL if technical=='neutral' else rating('Opening-day OVR')) for key in TECHNICAL_OVR})
                entry['contact_resistance']=entry['balance'] # PLACEHOLDER
                selected.append(entry)
                staged.append(_stage_ratings(row, columns, number, rating('Opening-day OVR')))
        roster=load_rows(selected,side)
        athletes=tuple(replace(athlete, staged_ratings=values, staged_rating_defaults=defaults)
                       for athlete, (values, defaults) in zip(roster.athletes, staged, strict=True))
        out[side]=replace(roster, athletes=athletes)
    return out


def load_canon_nbl(franchises,ref='81f92e3',technical='ovr',physical='roster'):
    """Read the owner workbook from a local Git object without copying it into this branch."""
    import io
    import subprocess
    path='audit/arcade/morphology/NBL_2026-27_Opening_Night_Rosters_CANON_OVR_morphology_physical.xlsx'
    blob=subprocess.check_output(['git','show',ref+':'+path])
    return load_nbl_workbook(io.BytesIO(blob),franchises,technical,physical)
