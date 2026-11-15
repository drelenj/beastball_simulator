"""Engine-only rulings and resource ledgers; no athlete decision callbacks."""
from dataclasses import dataclass,field

CREW=('referee','goal_judge_A','goal_judge_B','line_judge_1','line_judge_2','zone_judge','clock_official')

@dataclass
class Authorities:
    config: object
    period: int = 1
    timeouts: dict = field(default_factory=lambda:{'A':2,'B':2})
    challenges: dict = field(default_factory=lambda:{'A':1,'B':1})
    timeout_triggers: set = field(default_factory=set)
    scores: list = field(default_factory=list)
    calls: list = field(default_factory=list)
    exclusions: dict = field(default_factory=dict)
    evaluated: dict = field(default_factory=dict)
    injuries: set = field(default_factory=set)
    warnings: dict = field(default_factory=dict)
    quotas: dict = field(default_factory=lambda:{'A':{'arrows':0,'freezes':0},'B':{'arrows':0,'freezes':0}})
    possession: str|None = None

    def ruling(self,kind,**data):
        authority='goal_judge_'+data.get('defending','A') if kind in ('goal','no_goal') else ('line_judge_1' if data.get('y',0)<=50 else 'line_judge_2') if kind=='boundary' else 'zone_judge' if kind=='keeper_immunity' else 'clock_official' if kind in ('break','timeout') else 'referee'
        row=dict(id=len(self.calls)+1,kind=kind,authority=authority,period=self.period,**data);self.calls.append(row);return row

    def enter_period(self,period):
        self.period=period
        if period==3:self.timeouts={'A':2,'B':2};self.challenges={'A':1,'B':1}
        elif period==5:self.timeouts={'A':1,'B':1};self.challenges={'A':2,'B':2}
        elif period>5:self.timeouts={'A':0,'B':0}
        duration=self.config.breaks_ms[period-2] if 2<=period<=5 else self.config.sudden_break_ms if period>5 else 0
        return self.ruling('break',duration_ms=duration,exchange_ends=period>1)

    def score(self,team):self.scores.append(team)

    def timeout(self,team,dead,possessor,remaining_ms,score):
        if self.period>5 or self.timeouts[team]<=0 or not(dead or team==possessor):return None
        other='B' if team=='A' else 'A';triggers=[]
        if dead and len(self.scores)>=2 and self.scores[-2:]==[other,other]:
            start=len(self.scores)-2
            while start>0 and self.scores[start-1]==other:start-=1
            triggers.append(('two_scores',start))
        if dead and self.period>=4 and remaining_ms<=60000 and score[team]<=score[other]:triggers.append(('late',self.period))
        trigger=next((t for t in triggers if (team,t) not in self.timeout_triggers),None)
        if trigger is None:return None
        self.timeout_triggers.add((team,trigger));self.timeouts[team]-=1
        return self.ruling('timeout',team=team,duration_ms=self.config.timeout_ms,trigger=trigger)

    def turnover(self,team):
        if team!=self.possession:
            self.possession=team
            for q in self.quotas.values():q.update(arrows=0,freezes=0)
            return self.ruling('quota_reset',team=team)

    def arrow(self,team,legal):
        q=self.quotas[team]
        if q['arrows']>=self.config.arrows:return self.ruling('arrow_denied',team=team)
        q['arrows']+=1
        return self.ruling('arrow_release' if legal else 'arrow_forfeited',team=team,minor=not legal)

    def discipline(self,player,kind,game_ms):
        if kind not in ('minor','major'):raise ValueError(kind)
        key=kind+'_count';count=getattr(player,key)+1;setattr(player,key,count)
        dq=count>= (2 if kind=='major' else 5)
        duration=120000 if kind=='major' else 60000 if count>=4 else 0
        if duration:
            self.exclusions[player.id]=dict(until=game_ms+duration,dq=dq,team=player.team,role=player.role)
            player.active=False
        player.disqualified=dq
        return self.ruling('discipline',player=player.id,kind_of_foul=kind,count=count,dq=dq,duration_ms=duration)

    def injury(self,player,head=False):
        if not head:self.injuries.add(player.id)
        player.active=False
        if head:self.evaluated[player.id]=self.period
        return self.ruling('head_evaluation' if head else 'injury',player=player.id,replacement_exempt=True)

    def can_enter(self,player,game_ms):
        debt=self.exclusions.get(player.id)
        return not player.disqualified and player.id not in self.injuries and self.evaluated.get(player.id)!=self.period and (not debt or game_ms>=debt['until'])

    def review(self,team,call_id,dead):
        # Evidence is supplied only by the engine's stored call record, never by athletes.
        call=next((c for c in self.calls if c['id']==call_id),None)
        if not dead or self.challenges[team]<=0 or not call:return None
        eligible=call['kind'] in ('goal','no_goal','keeper_immunity') or call['kind']=='boundary' and (call.get('scoring_play') or call.get('major_foul'))
        if not eligible:return None
        wrong=call.get('recorded_disagreement_m',0.)>self.config.review_tolerance_m if call['kind']!='keeper_immunity' else call.get('keeper_wrong',False)
        if not wrong:
            self.challenges[team]-=1
            if self.timeouts[team]>0:self.timeouts[team]-=1
        return self.ruling('review',team=team,call_id=call_id,reversed=wrong)

    def points(self,carry=False,distance=0.,own=False,award=False):
        if own:return self.config.own_goal_points
        if award:return 1 if self.period<=3 else self.config.full_award_points
        if self.config.scoring=='flat':return 2
        if carry:return self.config.carry_points
        return next(points for edge,points in self.config.release_bands if edge is None or distance<edge)
