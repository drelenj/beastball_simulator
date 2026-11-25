"""Read-only player box score and possession observations for Native RB/3."""
from array import array
from bisect import bisect_right
from collections import Counter, defaultdict
import csv
from math import hypot

from .fatigue_rotation import possession_start
from .tackle_stats import TackleWitness

BANDS = ('under10', '10_to20', '20plus')
COUNTS = (
    'points', 'carry_attempts', 'stretch_attempts', 'passes_attempted', 'passes_completed',
    'handoffs', 'interceptions_thrown', 'assists', 'targets', 'catches', 'drops',
    'turnovers', 'fumbles', 'tackles_attempted', 'tackles_made', 'takedowns', 'strips',
    'interceptions', 'passes_defended', 'blocks_made', 'shots_faced', 'saves',
    'arrows_fired', 'hits', 'freezes', 'illegal_arrows', 'minor_fouls',
    'physical_blocks', 'own_goals_conceded',
)
GROUPS = ('goals_by_method', 'shot_attempts_by_band', 'turnovers_by_type',
          'goals_against_by_band', 'attempted_by_target', 'completed_by_target')


class PlayerLine:
    def __init__(self, player, team_name, display=None):
        self.player_name, self.legacy_position = display or (player.id, None)
        self.team_name = team_name
        self.id, self.team, self.role = player.id, player.team, player.role
        self.starter = player.active
        self.live_ms = 0
        self.regulation_ms = 0
        self.stints_ms = []
        self.stint = None
        self.distance_m = 0.
        self.peak = 0.
        self.energy = player.fatigue
        self.speeds = array('d')
        self.intervals = array('H')
        self.counts = Counter()
        self.breakdown = {key: Counter() for key in GROUPS}
        self.changes = []

    def record(self):
        cutoff = .8 * self.peak
        return dict(player=self.id, player_name=self.player_name, team=self.team, team_name=self.team_name,
                    legacy_position=self.legacy_position, role=self.role, starter=self.starter,
                    live_ms=self.live_ms, regulation_ms=self.regulation_ms, minutes=self.live_ms / 60_000,
                    stints_count=len(self.stints_ms) + (self.stint is not None),
                    stints_ms=self.stints_ms + ([] if self.stint is None else [self.stint]),
                    distance_m=self.distance_m, top_speed_mps=self.peak,
                    above_80pct_ms=sum(dt for v, dt in zip(self.speeds,self.intervals) if v > cutoff),
                    lowest_energy=self.energy, substitutions=self.changes,
                    **{k: self.counts[k] for k in COUNTS}, **self.breakdown)


class StatsLedger:
    """Sample authoritative live state and observe narrow scoring/rules seams."""

    def __init__(self, port):
        self.port = port
        self.state = s = port.m.s
        self.engine = e = port.m.e
        self.team_names = {team: port.roster_display.get(team, (team, ()))[0] for team in 'AB'}
        display = {f'{team}:{pid}': (name, position)
                   for team, (_, players) in port.roster_display.items() for pid, name, position in players}
        self.players = {p.id: PlayerLine(p, self.team_names[p.team], display.get(p.id)) for p in s.players.values()}
        self.tackles = TackleWitness(port.m)
        self.player_refs = tuple((p,self.players[p.id]) for p in s.players.values())
        self.active = tuple((p,l) for p,l in self.player_refs if p.active)
        self.regulation_limit = port.config.period_seconds * port.config.periods * 1000
        self.team_only = {t: PlayerLine(type('Team',(),dict(id=t,team=t,role='team',active=False,fatigue=1.)), self.team_names[t]) for t in 'AB'}
        self.live = s.live_ms
        self.keeper = {}
        self.carries = []
        self.awards = []
        self.scorers = {}
        self.team_credit = {t: Counter() for t in 'AB'}
        self.install(e)

    def install(self, e):
        carry, award, score, release = e.rb_carry_attempt, e.award, e.add_score, e.release

        def observe_release(pid, velocity, kind='pass', *args, **kwargs):
            at = self.state.now
            result = release(pid,velocity,kind,*args,**kwargs)
            if result and kind == 'shot':
                team = self.team(pid)
                self.keeper[at,pid] = next((p.id for p,line in self.active
                                            if p.active and p.team != team and p.role == 'keeper'),None)
            return result

        def observe_carry(holder, *args, **kwargs):
            result = carry(holder,*args,**kwargs)
            if result:
                self.carries.append((self.state.now,holder.id,holder.team))
            return result

        def observe_award(team,x,y,reason,foul=False,fresh=False,normalize=True):
            s = self.state
            awarded = team or s.alternate
            previous = e.possession.pp or s.owner
            witness = None
            if previous and previous != awarded and (fresh or s.owner != awarded):
                witness = (s.now, previous, reason, s.ball.carrier, len(e.log))
            result = award(team,x,y,reason,foul=foul,fresh=fresh,normalize=normalize)
            if witness and result:
                self.awards.append(witness)
            return result

        def observe_score(team, points, kind, **data):
            s = self.state
            carrier, releaser = s.ball.carrier, s.ball.last_releaser
            keeper = next((p.id for p,l in self.active if p.role == 'keeper' and p.team != team), None)
            start = len(e.log)
            result = score(team,points,kind,**data)
            for row in e.log[start:]:
                if row['event'] in ('goal','foul_award'):
                    self.scorers[row['id']] = (carrier,releaser,keeper)
                    break
            return result

        e.rb_carry_attempt, e.award, e.add_score, e.release = observe_carry, observe_award, observe_score, observe_release

    def sample(self):
        s = self.state
        dt = s.live_ms-self.live
        reg = min(s.live_ms,self.regulation_limit)-min(self.live,self.regulation_limit)
        self.live = s.live_ms
        if not dt:
            return
        # A boundary sample implements a right-endpoint estimate and excludes
        # dead-ball placement and platform changes from distance.
        for p,line in self.active:
            v = hypot(p.vx,p.vy)
            line.live_ms += dt
            line.regulation_ms += reg
            line.stint = (line.stint or 0) + dt
            line.distance_m += v * dt * .001
            if v > line.peak:
                line.peak = v
            if p.fatigue < line.energy:
                line.energy = p.fatigue
            line.speeds.append(v)
            line.intervals.append(dt)
        if s.phase.value != 'live':
            for p,line in self.active:
                if not p.active and line.stint is not None:
                    line.stints_ms.append(line.stint)
                    line.stint = None
            self.active = tuple((p,l) for p,l in self.player_refs if p.active)

    def before(self):
        if self.state.phase.value != 'live':
            for p,line in self.active:
                if not p.active and line.stint is not None:
                    line.stints_ms.append(line.stint)
                    line.stint = None
            self.active = tuple((p,l) for p,l in self.player_refs if p.active)

    def add(self, player, key, n=1):
        if player in self.players:
            self.players[player].counts[key] += n

    def group(self, player, key, value):
        if player in self.players:
            self.players[player].breakdown[key][value] += 1

    def team(self, pid):
        if pid in self.players:
            return self.players[pid].team

    def credit(self, team, pid):
        return self.players[pid] if self.team(pid)==team else self.team_only[team]

    def events(self):
        e = self.engine
        flight = last_pass = last_release = saving_keeper = None
        holder = None
        lost = None
        arrows = {}
        touches = set()
        scored = []
        blame_at = {}
        award_contexts = sorted(self.awards,key=lambda row:row[4])
        award_index = 0
        closed = None
        for row in e.log:
            event,d = row['event'],row['data']
            pid = d.get('player')
            if event=='restart_closed':
                closed = (row['t_ms'],d['status'])
            elif event in ('release','restart_release'):
                if saving_keeper:
                    self.add(saving_keeper,'saves')
                    saving_keeper = None
                pid = d.get('player',d.get('taker'))
                kind = d.get('kind','pass' if event=='restart_release' else None)
                flight = (kind,pid,d.get('target'))
                last_release = pid
                holder = None
                lost = (pid,'fumble') if kind=='loose' and d.get('forced') else None
                if lost:
                    self.add(pid,'fumbles')
                blame_at[row['t_ms']] = lost
                touches.clear()
                if kind=='pass':
                    self.add(pid,'passes_attempted')
                    self.add(flight[2],'targets')
                    self.group(pid,'attempted_by_target',flight[2] or 'untargeted')
                elif kind=='shot':
                    keeper = self.keeper.get((row['t_ms'],pid))
                    self.add(keeper,'shots_faced')
                if event=='restart_release':
                    last_pass = None
            elif event=='control':
                if last_pass and self.team(last_pass[1]) != self.team(pid):
                    last_pass = None
                holder = pid
                if flight:
                    kind,origin,target = flight
                    if kind in ('pass','shot') and origin!=pid:
                        self.add(pid,'catches')
                        if kind=='pass' and self.team(origin)==self.team(pid):
                            self.add(origin,'passes_completed')
                            self.group(origin,'completed_by_target',pid)
                            last_pass=(origin,pid)
                        if self.team(origin)!=self.team(pid):
                            if kind=='pass':
                                self.add(pid,'interceptions')
                                self.add(origin,'interceptions_thrown')
                                lost=(origin,'interception')
                            elif self.players[pid].role=='keeper':
                                saving_keeper = pid
                    flight = None
                if lost and self.team(lost[0])==self.team(pid):
                    lost = None
                blame_at[row['t_ms']]=lost
            elif event=='touch' and flight and pid in self.players:
                kind,origin,target = flight
                key=(pid,kind)
                if key not in touches:
                    touches.add(key)
                    if kind=='pass' and self.team(origin)!=self.team(pid):
                        self.add(pid,'passes_defended')
                    if kind=='pass' and pid==target:
                        self.add(pid,'drops')
                    if kind=='shot' and self.team(origin)!=self.team(pid) and self.players[pid].role=='keeper':
                        saving_keeper=pid
            elif event in ('restart_awarded','period_end','boundary'):
                while award_index < len(award_contexts) and award_contexts[award_index][4] <= row['id']-1:
                    context=award_contexts[award_index]
                    t,team,reason,carrier,_=context
                    if t<=row['t_ms'] and event=='restart_awarded' and d['reason']==reason:
                        actor=carrier or (lost[0] if lost else None) or holder or last_release
                        turnover_reason = 'toss_timeout' if reason=='turnover' and closed==(t,'toss_timeout') else reason
                        self.turnover(team,actor,turnover_reason)
                        award_index+=1
                        break
                    if t<row['t_ms']:
                        self.turnover(team,carrier,reason)
                        award_index+=1
                    else:
                        break
                if saving_keeper:
                    self.add(saving_keeper,'saves')
                    saving_keeper = None
                if event=='boundary':
                    lost=(d.get('carrier') or holder or last_release,'out_of_bounds')
                else:
                    holder = last_release = None
                    lost = None
                    blame_at[row['t_ms']] = None
                flight = last_pass = None
            elif event in ('goal','foul_award'):
                team,points,method=d['team'],d['points'],d['method']
                if method=='release':
                    method=f'throw_{points}'
                carrier,releaser,keeper=self.scorers.get(row['id'],(None,None,None))
                actor = (carrier or releaser or last_release) if event=='goal' and method!='own' else None
                credit=self.credit(team,actor)
                credit.counts['points']+=points
                credit.breakdown['goals_by_method'][method]+=1
                if method=='own':
                    self.add(carrier or releaser or last_release,'own_goals_conceded')
                if event=='goal':
                    saving_keeper = None
                    self.group(keeper,'goals_against_by_band',method)
                    if last_pass and actor==last_pass[1] and method!='own':
                        self.add(last_pass[0],'assists')
                scored.append((row['t_ms'],team,points,method))
                self.team_credit[team][method]+=points
            elif event=='tackle_count':
                lost=(d.get('target'),'tackle')
            elif event=='c3_grounding' and d.get('counted'):
                self.add(d.get('credited'),'takedowns')
            elif event=='strip':
                self.add(d.get('actor'),'strips')
                lost=(d.get('target'),'strip')
                blame_at[row['t_ms']]=lost
                flight=None
            elif event=='handoff_complete':
                self.add(d['giver'],'handoffs')
            elif event=='handoff_fumble':
                self.add(d['giver'],'fumbles')
                lost=(d['giver'],'fumble')
                blame_at[row['t_ms']]=lost
            elif event=='stretch_start':
                self.add(d.get('carrier'),'stretch_attempts')
            elif event=='block_engaged':
                self.add(d.get('blocker'),'blocks_made')
            elif event=='engagement' and d.get('kind')=='block':
                self.add(d.get('actor'),'physical_blocks')
            elif event=='foul' and not d.get('major'):
                self.add(d.get('actor'),'minor_fouls')
                if d.get('reason')=='archery_target':
                    self.add(d.get('actor'),'illegal_arrows')
            elif event=='arrow_release':
                arrows[d['arrow']]=pid
                self.add(pid,'arrows_fired')
            elif event=='arrow_geometry_impact' and d.get('target') not in ('ball',None):
                self.add(arrows.get(d['arrow']),'hits')
            elif event=='freeze':
                self.add(arrows.get(d.get('arrow')),'freezes')
            elif event in ('fatigue_substitution','rotation_substitution') or event=='rb_substitution' and not getattr(self.port,'rotation',None):
                if event=='rb_substitution':
                    d=d['ruling']
                if d.get('outgoing') is not None:
                    for key in ('incoming','outgoing'):
                        if d[key] in self.players:
                            self.players[d[key]].changes.append(dict(direction=key,t_ms=row['t_ms'],
                                live_ms=row['live_ms'],other=d['outgoing' if key=='incoming' else 'incoming'],
                                reason=d.get('reason','required_cover'),tier=d.get('tier')))
        if saving_keeper:
            self.add(saving_keeper,'saves')
        for _,team,reason,carrier,_ in award_contexts[award_index:]:
            self.turnover(team,carrier,reason)
        return scored,blame_at

    def turnover(self, team, actor, reason):
        kind = {'out_of_bounds':'out_of_bounds','second_tackle':'tackle','boundary':'out_of_bounds','possession_expiry':'play_clock',
                'goal':'score_restart'}.get(reason,reason)
        if reason.startswith('ZR-') or reason in ('zone_residence','zone_unmarked'):
            kind='zone_violation'
        credit=self.credit(team,None if reason=='goal' else actor)
        credit.counts['turnovers']+=1
        credit.breakdown['turnovers_by_type'][kind]+=1

    def possessions(self, scores, blame):
        e = self.engine
        changes=[row for row in e.possession_history+e.possession.ledger if possession_start(row)]
        award_reason={(row['t_ms'],row['data']['team']):row['data']['reason'] for row in e.log
                      if row['event']=='restart_awarded'}
        loss_times=sorted(blame)
        def loss(at, team):
            index=bisect_right(loss_times,at)-1
            witness=blame[loss_times[index]] if index>=0 else None
            if witness and (witness[0] is None or self.team(witness[0]) == team):
                return witness
            return None,'opponent_control'

        times=[(r['t_ms'],1,r) for r in changes]
        times.extend((t,0,(team,pts,method)) for t,team,pts,method in scores)
        times.extend((r['t_ms'],4,None) for r in e.log if r['event']=='period_end')
        times.extend((row['t_ms'],2,(row['team'],'attempt' if row['shot_attempt'] else 'pass')) for row in e.rb_attempts)
        times.extend((row['t_ms'],2,(self.team(row['data']['player']),'control')) for row in e.log if row['event']=='control')
        # Same-tick controls precede releases as in the RB-3.27 measure.
        times.sort(key=lambda r: (r[0],r[1], -(r[1]==2 and r[2][1]=='control')))
        times.extend((t,3,(team,'attempt')) for t,_,team in self.carries)
        times.sort(key=lambda r:(r[0],r[1]))
        rows=[]
        current=None
        off_points=Counter()
        for at,category,datum in times:
            if category==0:
                team,points,method=datum
                if current and current['team']==team:
                    current['points']+=points
                    if method not in ('half_goal','full_goal_award'):
                        current['end_reason']='score'
                else:
                    off_points[team]+=points
                    if current:
                        current['opponent_points']+=points
                        if method=='own':
                            current['end_reason']='own_goal'
                continue
            if category==4:
                if current and current['end_reason']=='match_end':
                    current['end_reason']='period_end'
                continue
            if category==1:
                if datum['event']=='passive_possession' and datum.get('previous'):
                    team=datum['previous']
                    actor,reason=loss(at,team)
                    self.turnover(team,actor,reason)
                if current and current['end_reason']=='match_end':
                    cause=award_reason.get((at,datum['team']))
                    if datum['event']=='passive_possession':
                        cause=loss(at,datum.get('previous'))[1]
                    current['end_reason']=cause or 'restart_awarded'
                current=dict(team=datum['team'],start_ms=at,points=0,opponent_points=0,
                             end_reason='match_end',terminal=None)
                rows.append(current)
            elif current and current['team']==datum[0]:
                current['terminal']=datum[1]
        return rows,off_points

    def build(self, result):
        e = self.engine
        for line in (*self.players.values(), *self.team_only.values()):
            line.counts.clear()
            line.changes.clear()
            for counter in line.breakdown.values():
                counter.clear()
        for counter in self.team_credit.values():
            counter.clear()
        for actor, made in self.tackles.totals(e.log):
            self.add(actor, 'tackles_attempted')
            if made:
                self.add(actor, 'tackles_made')
        for _,pid,_ in self.carries:
            self.add(pid,'carry_attempts')
        for row in e.rb_attempts:
            if row['shot_attempt']:
                self.group(row['player'],'shot_attempts_by_band',row['band'])
        scored,blame=self.events()
        possessions,off_points=self.possessions(scored,blame)
        from .rb31_soak import measure
        reference = measure(self.port, [(t,team) for t,_,team in self.carries])['possessions']
        lines=[l.record() for l in self.players.values()]
        unattributed=[l.record() for l in self.team_only.values()]
        totals=[]
        for team in 'AB':
            counts=Counter()
            groups=defaultdict(Counter)
            for line in (*lines,*unattributed):
                if line['team']==team:
                    counts.update({key:line[key] for key in COUNTS})
                    for key in GROUPS:
                        groups[key].update(line[key])
            npos=sum(r['team']==team for r in possessions)
            goals=sum(v for k,v in groups['goals_by_method'].items() if k!='half_goal')
            stats=result['team_stats'][team]
            assert (counts['points'],goals,counts['turnovers']) == (
                result['score'][team],stats.get('goals',0),stats.get('turnovers',0)), (team,counts,goals,stats)
            assert groups['goals_by_method']['half_goal']==stats.get('half_goal_awards',0)
            assert npos==reference[team]['count']
            terminal=sum(r['team']==team and r['terminal']=='attempt' for r in possessions)
            assert terminal==reference[team]['ending_in_attempt']
            assert counts['carry_attempts']==e.rb_bands[team]['carry_attempts']
            assert counts['points']==sum(r['points'] for r in possessions if r['team']==team)+off_points[team]
            members=[row for row in lines if row['team']==team]
            totals.append(dict(team=team,team_name=self.team_names[team],player='TEAM TOTAL',
                               player_name='TEAM TOTAL',legacy_position=None,possessions=npos, goals=goals,
                               possessions_ending_in_attempt=terminal,
                               live_ms=sum(r['live_ms'] for r in members),
                               minutes=sum(r['minutes'] for r in members),
                               stints_count=sum(r['stints_count'] for r in members),
                               distance_m=sum(r['distance_m'] for r in members),
                               above_80pct_ms=sum(r['above_80pct_ms'] for r in members),
                               top_speed_mps=max(r['top_speed_mps'] for r in members),
                               lowest_energy=min(r['lowest_energy'] for r in members),
                               points_outside_own_possession=off_points[team],
                               scoring_points_by_method=self.team_credit[team],**counts,**groups))
        return dict(schema='native-box/2', players=lines, unattributed=unattributed, teams=totals,
                    possessions=possessions, scores=scored)


def write_csv(box, stream):
    import json

    rows=[*box['players'],*box['unattributed'],*box['teams']]
    fields=list(dict.fromkeys(key for row in rows for key in row))
    writer=csv.DictWriter(stream,fields,lineterminator='\n')
    writer.writeheader()
    for row in rows:
        writer.writerow({k:json.dumps(v,ensure_ascii=False,sort_keys=True) if isinstance(v,(list,dict)) else v
                         for k,v in row.items()})
