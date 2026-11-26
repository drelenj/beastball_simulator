"""Load frozen B0 physical sources in a private namespace, never alter B0 files.
Provenance: core_src at 2abe497. Config-specific geometry/CATCH_V2 edits are
asserted source anchors and readback-tested. No environment switches are read.
"""
import importlib.util
import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def build_core(config):
    name = '_beastball_native_' + config.digest[:12]
    # A fresh namespace per match prevents legacy/global patches contaminating it.
    suffix = 0
    while name in sys.modules:
        suffix += 1
        name = '_beastball_native_' + config.digest[:12] + '_' + str(suffix)
    package = types.ModuleType(name)
    package.__path__ = [str(ROOT/'core_src')]
    sys.modules[name] = package
    patches = {
        'geometry': [('norm(y-50,z)+r<=6+1e-7',f'norm(y-50,z)+r<={config.goal_radius}+1e-7'),
                     ('norm(x,y-50)<=radius','norm(x,y-50)<radius'),
                     ('norm(x-100,y-50)<=radius','norm(x-100,y-50)<radius')],
        'engine': [('0<=q.loaded<=5','0<=q.loaded<=25')],
        'match': [("(1.1 if p.role=='keeper'else.9)",".9"), ("(1.1 if q.role=='keeper'else.9)",".9"), ("return p.a.reach*1.1","return p.a.reach*.9"),("if d_.id in down:continue", "if d_.id in down or not self.native_wrap_authorized(d_,car):continue"),("if b.last_releaser==p.id:continue","if b.last_releaser==p.id and self.e.dribble_replay!=p.id:continue"),("6-b.radius<=norm(yy-50,zz)<=6+self.assume['frame_thickness']+b.radius",f"{config.goal_radius}-b.radius<=norm(yy-50,zz)<={config.goal_radius}+self.assume['frame_thickness']+b.radius"),
                  ("skill=p.a.keeper_skill if p.role=='keeper'else p.a.catching",'skill=p.a.catching'),
                  ("capacity=A['catch_arrest_force_N']*A['catch_hand_travel_m']*(.4+.9*skill)*max(0.,1-miss*miss)", 'capacity=self.native_catch_capacity(skill,miss)'),
                  ('secure=1/(1+(energy/capacity)**2)if capacity>1e-9 else 0.', 'secure=1/(1+(energy/capacity)**8)if capacity>1e-9 else 0.')]
    }
    if config.version == 'native-rb/3':
        if 'mouth_boundary' in config.rb333:
            patches['match'].append(("if p.posture!='airborne'and not(0<=p.x<=100 and 0<=p.y<=100):","if p.posture!='airborne' and (not 0<=p.y<=100 or not 0<=p.x<=100 and not legal_goal(p.y,p.hand_height,b.radius)):"))
        if 'sideline_held_ball' in config.rb333:
            patches['match'].extend((
                ('    if outward:cuts.append((frac,axis,limit))',
                 '    if outward and not (axis==1 and self.native_held_sideline_in_play(b)):cuts.append((frac,axis,limit))'),
                ('  if cuts:\n   frac,axis,limit=min(cuts)',
                 '  if b.carrier and b.z<=b.radius and (b.y<=0 or b.y>=100):cuts.append((1.,1,0 if b.y<=0 else 100))\n'
                 '  if cuts:\n   frac,axis,limit=min(cuts)'),
                ('  elif b.x<-b.radius or b.x>100+b.radius or b.y<-b.radius or b.y>100+b.radius:',
                 '  elif b.x<-b.radius or b.x>100+b.radius or ((b.y<-b.radius or b.y>100+b.radius) and not self.native_held_sideline_in_play(b)):'),
            ))
        if 'endline_held_ball' in config.rb333:
            # Ignore held-ball end crossings only outside the mouth. A
            # genuine goal still participates in the swept event ordering.
            outward = ('    if outward and not (axis==1 and self.native_held_sideline_in_play(b)):cuts.append((frac,axis,limit))'
                       if 'sideline_held_ball' in config.rb333 else '    if outward:cuts.append((frac,axis,limit))')
            fallback = ('  elif b.x<-b.radius or b.x>100+b.radius or ((b.y<-b.radius or b.y>100+b.radius) and not self.native_held_sideline_in_play(b)):'
                        if 'sideline_held_ball' in config.rb333 else '  elif b.x<-b.radius or b.x>100+b.radius or b.y<-b.radius or b.y>100+b.radius:')
            patches['match'].extend((
                (outward, outward.replace('outward','outward and not (axis==0 and self.native_held_endline_in_play(b) and not legal_goal(old[1]+(b.y-old[1])*frac,old[2]+(b.z-old[2])*frac,b.radius))',1)),
                (fallback, fallback.replace('b.x<-b.radius or b.x>100+b.radius','((b.x<-b.radius or b.x>100+b.radius) and not self.native_held_endline_in_play(b))',1)),
            ))
        if 'universal_set_speed' in config.rb333:
            patches['match'].append(("sp>A['keeper_set_mps']", "sp>p.a.braking*.40 "))
        if 'universal_unset' not in config.rb333:
            patches['match'].append(('   kr=None\n',
                '   observer=getattr(self,"native_reaction_observe",None)\n'
                '   if observer is not None:observer(p)\n   kr=None\n'))
        if 'universal_unset' in config.rb333:
            patches['match'].extend((
                ('   kr=None\n', '   unset=self.native_hands_delay(p)\n'
                 '   lo=max(lo,(self.seen_from+unset-s.now)/ms)\n'
                 '   if lo>=hi:continue\n   kr=None\n'),
                ('     state=self.seen_from\n', '     state=self.seen_from+unset\n'),
            ))
        if 'movement_clock' in config.rb333:
            patches['match'].append(('if p.id in targets and s.now>=p.next_decision:', 'if p.id in targets:'))
        if 'braking' in config.rb333:
            patches['match'].append(('p.target=targets[p.id];p.next_decision=', 'p.target=self.native_boundary_target(p,targets[p.id]);p.next_decision='))
        if 'keeper_deadline' in config.rb333:
            patches['match'].append(("   if landings_only:continue", "   timing=getattr(p,'native_keeper_flight',None)\n   if timing and b.carrier is None and timing[2]>s.now:out.append(timing[2])\n   if landings_only:continue"))
        if getattr(config, 'fatigue_rotation', False):
            from .rulebook.fatigue_rotation import KERNEL_PATCHES
            patches['match'].extend(KERNEL_PATCHES)
        patches['match'].append((
            "top=p.a.maximum_speed*(.70+.30*p.fatigue)*((policy.pace*.90)if s.ball.carrier==p.id else.88)",
            "top=p.a.maximum_speed*(.70+.30*p.fatigue)",
        ))
        if config.rb3_carrier_moves_enabled:
            patches['match'].extend([
                ("else:hd['pin_now']=0.",
                 "else:hd['pin_now']=0.\n    lam*=self.rb318_strip_multiplier(car,end_ms)"),
                ("J=(1+(eps if armed else 0.))*vn/(1/ma+1/mb)",
                 "truck=self.rb318_truck(car,a,b,ua,ub,t,now_ms) if armed else False\n"
                 "   J=(1+(eps if armed and not truck else 0.))*vn/(1/ma+1/mb)"),
                ("self.c3_add(a,('shock',b.id),sa,lawful[b.id],now_ms);self.c3_add(b,('shock',a.id),sb,lawful[a.id],now_ms)",
                 "self.c3_add(a,('shock',b.id),0. if truck and a is car else sa,lawful[b.id],now_ms);"
                 "self.c3_add(b,('shock',a.id),0. if truck and b is car else sb,lawful[a.id],now_ms)"),
            ])
    if getattr(config, 'individuation', 'off') == 'individuation/1':
        patches['match'].append((
            "   if state is not True and tau>1e-9:",
            "   if state is not True:\n"
            "    ready=max(self.seen_from,self.native_catch_ready_at(p))\n"
            "    if ready>s.now+hi*ms:continue\n"
            "    fset=max(lo,(ready-s.now)/ms);self.hands_set[p.id]=True;state=True\n"
            "   if state is not True and tau>1e-9:",
        ))
    if getattr(config, 'individuation', 'off') == 'individuation/2':
        patches['match'].append((
            "    slip=norm(max(0.,sep),tan)",
            "    slip=norm(max(0.,sep),tan)\n"
            "    region=self.native_grip_region(d_,car)\n"
            "    if region is not None and region!=hd['region']:\n"
            "     hd['region']=region;hd['g']*=self.native_grip_switch_retention",
        ))
        patches['match'].append((
            "   if state is not True and tau>1e-9:",
            "   if state is not True:tau*=self.native_late_catch_gain(p)\n"
            "   if state is not True and tau>1e-9:",
        ))
    from .rulebook.ball_ground import enabled as _rb320_enabled, PATCHES as _RB320, GEOMETRY_PATCHES as _RB320G
    from .rulebook import ball_material as _rb321
    if _rb321.enabled(config):            # RB-3.21: Beastball ball material everywhere (engine step and every forecast)
        patches['match'].extend(_rb321.match_patches(ROOT))
        patches.setdefault('geometry', []).extend(_rb321.geometry_patches(ROOT, _rb321.params(config)))
    elif _rb320_enabled(config):          # RB-3.20a: exact ball-ground contact (defect fix), native-rb/3 only
        patches['match'].extend(_RB320)
        patches.setdefault('geometry', []).extend(_RB320G)
    for part in ('geometry','types','policies','engine','match'):
        path = ROOT/'core_src'/f'{part}.py'
        source = path.read_text()
        for old,new in patches.get(part,()):
            if old not in source:
                raise RuntimeError(f'Native source anchor absent: {part}: {old}')
            source = source.replace(old,new)
        mod = types.ModuleType(name+'.'+part)
        mod.__package__, mod.__file__ = name, str(path)
        sys.modules[mod.__name__] = mod
        exec(compile(source,str(path),'exec'),mod.__dict__)
        setattr(package,part,mod)
    from .rules import install
    install(package,config)
    if config.profile=="native-rb":
        from .rulebook.engine import install as install_rb
        install_rb(package,config)
    return package
