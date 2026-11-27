"""Perimeter witnesses, captured without changing live commands or adjudication."""
from native.edge_control import FIELD_M
from native.geometry import body_out

from audit.native.rb338.witness import Witness as ArcherWitness, line_distance


class Witness(ArcherWitness):
    def __init__(self, driver):
        super().__init__(driver)
        self.noncarrier_outs = []
        self.takedowns = []
        self.started_inside = set()
        emit = self.match.e.emit

        def observed_emit(event, rule, **data):
            if event=='tackle_count':
                actor,target = data['actor'],data['target']
                p = self.state.players[target]
                self.takedowns.append(dict(ms=self.state.now,actor=actor,target=target,
                                          x=p.x,y=p.y,line_m=min(abs(p.x),abs(p.y),abs(FIELD_M-p.x),abs(FIELD_M-p.y))))
            return emit(event,rule,**data)

        self.match.e.emit = observed_emit

    def physics(self, kind, now, targets):
        super().physics(kind,now,targets)
        if self.state.phase not in (self.port.types.Phase.LIVE,self.port.types.Phase.OPENING):
            self.started_inside.clear()
            return
        carrier = self.state.ball.carrier
        if kind=='physics':
            self.started_inside = {p.id for p in self.state.players.values()
                                   if p.active and p.role!='archer' and not body_out(p)}
            return
        for pid in sorted(self.started_inside):
            p = self.state.players[pid]
            if p.active and pid!=carrier and body_out(p):
                self.noncarrier_outs.append(dict(ms=now,player=pid,team=p.team,x=p.x,y=p.y,
                                                 distance_m=line_distance(p.x,p.y)))

    def perimeter(self):
        return dict(noncarrier_outs=self.noncarrier_outs,takedowns=self.takedowns)
