"""ATTR-1 roster ingestion and immutable attribute mapping.

Labels are accepted only so generated files can carry metadata beside the
canonical columns.  Their values are deliberately discarded.
"""
from __future__ import annotations

from dataclasses import dataclass
import csv
import hashlib
import json
from pathlib import Path

MAPPING_VERSION = 'attr-map/1'
RATINGS = (
    'speed','agility','strength','balance','stamina','tackling','blocking',
    'contact_resistance','ball_handling','catching','awareness','throw_power',
    'throw_accuracy','jump','keeper_skill','archery_accuracy',
)
INERT_RATINGS = ('touch','vision','clarity','reaction','anticipation','focus','instinct','judgment','motor_control',
                 'playmaking','finishing','marking','zone_reads','goalkeeping','in_air_ball_pursuit',
                 'live_ball_pursuit','carrier_duel','defender_duel')
OPTIONAL_RATINGS = ('durability','injury','acceleration',*INERT_RATINGS)
REQUIRED = ('id','role',*RATINGS,'height_m','mass_kg')
IGNORED_LABELS = ('name','position','archetype','overall')

# canonical name -> accepted input headers.  Callers may extend this map, but
# every input header must resolve here; unknown columns are rejected.
DEFAULT_ALIASES = {
    **{name:(name,) for name in REQUIRED + OPTIONAL_RATINGS + IGNORED_LABELS},
    'reach_m':('reach_m','reach'),
    'standing_reach_m':('standing_reach_m',),
    'id':('id','athlete_id','player_id'),
    'role':('role',),
    # Known player_gen_v1/export metadata, accepted but never consumed.
    '_ignored':('team','seed','notes','top_speed_mph'),
}


class RosterError(ValueError):
    pass


def clamp(value):
    return min(1.,max(0.,value))


def speed_mps(rating):
    return 44.704*rating


def acceleration(rating,agility=None):
    return 12.5*rating


def braking(agility):
    return 16.875*agility


def turning(agility):
    return 16.25*agility


def throw_x(rating):
    return clamp((rating-.4)/.6)


def max_throw_speed(rating):
    x=throw_x(rating)
    return 134.1*(.5+.5*x)


def throw_error_base_deg(rating):
    return max(.15,3*(1-throw_x(rating)))


def sensor_noise_scale(awareness):
    return 2-1.25*awareness


@dataclass(frozen=True)
class AthleteAttributes:
    source_id: str
    role: str
    values: tuple
    defaults: tuple = ()
    sources: tuple[tuple[str, str], ...] = ()

    def get(self,name):
        return dict(self.values)[name]

    def record(self):
        record = {'id':self.source_id,'role':self.role,**dict(self.values),'defaults':self.defaults}
        if self.sources:
            record['sources'] = self.sources
        return record


@dataclass(frozen=True)
class TeamRoster:
    team: str
    athletes: tuple[AthleteAttributes,...]
    digest: str
    warning_counts: tuple

    def record(self):
        return {'team':self.team,'athletes':[a.record() for a in self.athletes]}


def _header_map(alias_map):
    aliases={key:tuple(values) for key,values in DEFAULT_ALIASES.items()}
    for key,values in (alias_map or {}).items():
        if key not in aliases and key!='_ignored':
            raise RosterError(f"alias map: unknown canonical column '{key}'")
        aliases[key]=tuple(values) if not isinstance(values,str) else (values,)
    result={}
    for canonical,names in aliases.items():
        for name in names:
            key=str(name).strip().lower()
            if key in result and result[key]!=canonical:
                raise RosterError(f"alias map: header '{name}' is ambiguous")
            result[key]=canonical
    return result


def _number(raw,row,column):
    try:return float(raw)
    except (TypeError,ValueError):raise RosterError(f"row {row} column {column}: expected a number") from None


def load_rows(rows,team,alias_map=None):
    """Validate canonical roster rows; row numbers include a CSV header."""
    header=_header_map(alias_map)
    canonical=[]
    for row_number,raw in enumerate(rows,start=2):
        row={}
        for supplied,value in raw.items():
            name=str(supplied).strip().lower()
            if name not in header:
                raise RosterError(f"row {row_number} column {supplied}: unknown column")
            target=header[name]
            if target in ('_ignored',*IGNORED_LABELS):continue
            if target in row:
                raise RosterError(f"row {row_number} column {supplied}: duplicate alias for {target}")
            row[target]=value
        for column in REQUIRED:
            if column not in row or str(row[column]).strip()=='':
                raise RosterError(f"row {row_number} column {column}: missing required column")
        source_id=str(row['id']).strip()
        role=str(row['role']).strip().lower()
        if role not in ('field','keeper','archer'):
            raise RosterError(f"row {row_number} column role: unknown role '{row['role']}'")
        values={}
        for column in RATINGS+OPTIONAL_RATINGS:
            if column not in row:continue
            value=_number(row[column],row_number,column)
            if not 0<=value<=1:
                raise RosterError(f"row {row_number} column {column}: rating {value} outside 0..1")
            values[column]=value
        defaults=[]
        for column in INERT_RATINGS:
            if column not in values:values[column]=.70;defaults.append(column)
        if 'acceleration' not in values:values['acceleration']=.70;defaults.append('acceleration')
        height=_number(row['height_m'],row_number,'height_m')
        mass=_number(row['mass_kg'],row_number,'mass_kg')
        if not 1.4<=height<=3.6576:
            raise RosterError(f"row {row_number} column height_m: {height} outside engine limits 1.4..3.6576")
        if mass<=0:raise RosterError(f"row {row_number} column mass_kg: must be positive")
        reach=_number(row.get('reach_m',.46*height),row_number,'reach_m')
        if reach<=0:raise RosterError(f"row {row_number} column reach_m: must be positive")
        values.update(height_m=height,mass_kg=mass,reach_m=reach)
        if 'standing_reach_m' in row:
            standing = _number(row['standing_reach_m'], row_number, 'standing_reach_m')
            if standing <= 0:
                raise RosterError(f"row {row_number} column standing_reach_m: must be positive")
            values['standing_reach_m'] = standing
        canonical.append(AthleteAttributes(source_id,role,tuple(sorted(values.items())),tuple(sorted(defaults))))
    ids={}
    for index,a in enumerate(canonical,start=2):
        if a.source_id in ids:
            raise RosterError(f"row {index} column id: duplicate id '{a.source_id}' (first row {ids[a.source_id]})")
        ids[a.source_id]=index
    counts={role:sum(a.role==role for a in canonical) for role in ('field','keeper','archer')}
    if len(canonical)!=22:raise RosterError(f"roster column id: expected 22 athletes, got {len(canonical)}")
    if counts['field']<10:raise RosterError(f"roster column role: requires at least 10 field athletes, got {counts['field']}")
    for role in ('keeper','archer'):
        if counts[role]<2:raise RosterError(f"roster column role: requires active and reserve {role}, got {counts[role]}")
    warnings={'ratings_below_0.60':0,'ratings_above_1.00':0,'body_outside_design_envelope':0}
    for a in canonical:
        vals=dict(a.values)
        warnings['ratings_below_0.60']+=sum(vals[k]<.6 for k in RATINGS)
        warnings['ratings_above_1.00']+=sum(vals[k]>1 for k in RATINGS)
        # Legal body limits are the engine height range and positive mass above.
    record={'team':team,'athletes':[a.record() for a in canonical]}
    digest=hashlib.sha256(json.dumps(record,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return TeamRoster(team,tuple(canonical),digest,tuple(sorted(warnings.items())))


def load_csv(path,team,alias_map=None):
    with Path(path).open(newline='',encoding='utf-8') as stream:
        reader=csv.DictReader(stream)
        if reader.fieldnames is None:raise RosterError('row 1 column header: missing header')
        return load_rows(list(reader),team,alias_map)


def rb3_control_rosters():
    """RB/3 evidence control: matched ratings and separate body reach measures."""
    height = 2.39
    roles = ['field'] * 18 + ['keeper'] * 2 + ['archer'] * 2
    rows = [dict.fromkeys(RATINGS, .70) | dict(
        id=str(index), role=role, height_m=height, mass_kg=226.,
        reach_m=.529 * height, standing_reach_m=3.05, acceleration=.70)
        for index, role in enumerate(roles)]
    return {team: load_rows(rows, team) for team in ('A', 'B')}


def engine_order(roster):
    """Ten field starters, one Keeper, one Archer, then the fixed-role bench."""
    field=[a for a in roster.athletes if a.role=='field']
    keepers=[a for a in roster.athletes if a.role=='keeper']
    archers=[a for a in roster.athletes if a.role=='archer']
    starters=field[:10]+keepers[:1]+archers[:1]
    used={id(a) for a in starters}
    return tuple(starters+[a for a in roster.athletes if id(a) not in used])


def mapped_values(athlete):
    r=dict(athlete.values)
    return dict(
        height=r['height_m'],mass=r['mass_kg'],reach=r['reach_m'],
        maximum_speed=speed_mps(r['speed']),
        acceleration=acceleration(r['acceleration']),
        braking=braking(r['agility']),turning=turning(r['agility']),
        jump_height=1.3*r['jump'],strength=r['strength'],agility=r['agility'],
        endurance=r['stamina'],balance=r['balance'],contact_resistance=r['contact_resistance'],
        tackling=r['tackling'],blocking=r['blocking'],ball_handling=r['ball_handling'],
        passing=r['throw_accuracy'],catching=r['catching'],awareness=r['awareness'],
        archery_accuracy=r['archery_accuracy'],keeper_skill=r['keeper_skill'],
        decision_speed=.3,archery_release_speed=250.,kicking=0.,
    )
