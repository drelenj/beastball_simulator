"""Opening night workbook adapter for native-rb/3. Labels select eligibility only."""
from dataclasses import replace
import hashlib
import json

from .prism_registry import NEW_RATINGS, MANEUVERS, LEGACY_SOURCES, AVERAGE
from .roster import INERT_RATINGS, load_rows, RosterError

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
TECHNICAL_SOURCES = ('ovr', 'neutral', 'explicit')
PHYSICAL_SOURCES = ('roster', 'neutral')
NEUTRAL_TECHNICAL = .784          # the league mean Opening-day OVR / 100 (owner/lead figure)


def load_nbl_workbook(source, franchises, technical='ovr', physical='roster'):
    """Choose each franchise's top OVR 2 KPR, 2 ARC, 18 field; ties keep sheet order.

    Technical skills use OVR/100, contact resistance uses Balance/100: PLACEHOLDER.
    No player labels enter the validated attribute record.
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
    registry_columns = {key: key.replace('_', ' ').title() + ' (rating)' for key in (*NEW_RATINGS, *MANEUVERS)}
    registry_present = any(header in columns for header in registry_columns.values())
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
        source_records = []
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
                if technical == 'explicit' or registry_present:
                    sources = {}
                    for key in (*TECHNICAL_OVR, 'contact_resistance', *INERT_RATINGS):
                        header = key.replace('_', ' ').title() + ' (rating)'
                        value = row[columns[header]] if header in columns else None
                        if technical == 'explicit' and value is not None and value != '':
                            if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0 <= value <= 100:
                                raise RosterError(f'workbook row {number}, {header}: expected 0..100')
                            entry[key] = value / 100.
                            sources[key] = 'explicit:' + header
                        elif key == 'contact_resistance':
                            if technical == 'explicit':
                                entry[key] = NEUTRAL_TECHNICAL
                            sources[key] = 'neutral fallback' if technical == 'explicit' else 'Balance fallback'
                        else:
                            sources[key] = '0.70 default' if key in INERT_RATINGS else ('neutral fallback' if technical == 'neutral' else 'Opening-day OVR fallback')
                    for key, header in registry_columns.items():
                        value = row[columns[header]] if header in columns else None
                        if value is not None and value != '':
                            if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0 <= value <= 100:
                                raise RosterError(f'workbook row {number}, {header}: expected 0..100')
                            entry[key] = value / 100.
                            sources[key] = 'explicit:' + header
                        else:
                            alias = next((name for name in LEGACY_SOURCES.get(key, ()) if name in entry), None)
                            sources[key] = 'alias:' + alias if alias else f'{AVERAGE:.2f} default'
                    source_records.append(tuple(sorted(sources.items())))
                selected.append(entry)
        roster = load_rows(selected, side)
        if source_records:
            athletes = tuple(replace(a, sources=sources) for a, sources in
                             zip(roster.athletes, source_records, strict=True))
            roster = replace(roster, athletes=athletes)
            fingerprint = hashlib.sha256(json.dumps(roster.record(), sort_keys=True,
                                                    separators=(',', ':')).encode()).hexdigest()
            roster = replace(roster, digest=fingerprint)
        athletes = []
        for athlete in roster.athletes:
            sources = dict(athlete.sources)
            values = dict(athlete.values)
            sources.setdefault('awareness', f'{technical} fallback')
            for key in NEW_RATINGS:
                if key not in sources:
                    alias = next((name for name in LEGACY_SOURCES.get(key, ())
                                  if name in values and name not in athlete.defaults), None)
                    sources[key] = 'alias:' + alias if alias else f'{AVERAGE:.2f} default'
            athletes.append(replace(athlete, prism_sources=tuple(sorted(sources.items()))))
        out[side] = replace(roster, athletes=tuple(athletes))
    return out


def load_canon_nbl(franchises,ref='81f92e3',technical='ovr',physical='roster'):
    """Read the owner workbook from a local Git object without copying it into this branch."""
    import io
    import subprocess
    path='audit/arcade/morphology/NBL_2026-27_Opening_Night_Rosters_CANON_OVR_morphology_physical.xlsx'
    blob=subprocess.check_output(['git','show',ref+':'+path])
    return load_nbl_workbook(io.BytesIO(blob),franchises,technical,physical)
