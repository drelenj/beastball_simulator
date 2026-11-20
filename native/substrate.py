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
        patches['match'].append((
            "top=p.a.maximum_speed*(.70+.30*p.fatigue)*((policy.pace*.90)if s.ball.carrier==p.id else.88)",
            "top=p.a.maximum_speed*(.70+.30*p.fatigue)",
        ))
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
