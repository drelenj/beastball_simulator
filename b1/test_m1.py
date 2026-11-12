import dataclasses
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from .core import AthleteView, BeliefState, Contact, decide
from .preservation import historical_hashes

ROOT=Path(__file__).resolve().parents[1]


class PureBoundaryTests(unittest.TestCase):
    def test_decision_values_are_immutable(self):
        v=AthleteView('o','A0','A',1500,40,50,True,(Contact('A1','A',55,50,1000),))
        b=BeliefState('b','o',v.contacts)
        first=decide(v,b)
        self.assertEqual(first,decide(v,b))
        with self.assertRaises(dataclasses.FrozenInstanceError): v.x=100

    def test_observation_changes_selection(self):
        contacts=(Contact('A1','A',55,50,1000),)
        v=AthleteView('o','A0','A',1500,40,50,True,contacts)
        self.assertEqual(decide(v,BeliefState('b','o',contacts))[0].kind,'pass')
        contacts += (Contact('B0','B',47,50,1000),)
        v=dataclasses.replace(v,contacts=contacts)
        self.assertEqual(decide(v,BeliefState('b','o',contacts))[0].kind,'retain')

    def test_stale_belief_is_not_treated_as_current(self):
        fresh=Contact('A1','A',55,50,1500)
        stale=Contact('B0','B',47,50,0)
        v=AthleteView('o','A0','A',1500,40,50,True,(fresh,stale))
        intent,trace=decide(v,BeliefState('b','o',(fresh,stale),max_contact_age_ms=500))
        self.assertEqual(intent.kind,'pass')
        self.assertEqual(trace['stale_contact_ids'],['B0'])

    def test_cognition_has_no_engine_import(self):
        import ast
        tree=ast.parse((ROOT/'b1/core.py').read_text())
        modules=[n.module for n in ast.walk(tree) if isinstance(n,ast.ImportFrom)]
        self.assertEqual(modules,['dataclasses','math'])


class WorkerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.before=cls.hashes()

    @staticmethod
    def hashes():
        return historical_hashes(ROOT)

    def worker(self,case='pass',off=False):
        with tempfile.TemporaryDirectory() as d:
            cmd=[sys.executable,'-m','b1.run','--case',case,'--out',d+'/result.json']
            if off: cmd.append('--telemetry-off')
            r=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True,timeout=45)
            self.assertEqual(r.returncode,0,r.stderr)
            return json.loads(Path(d+'/result.json').read_text())

    def test_replay_and_observer_neutrality(self):
        a,b,c=self.worker(),self.worker(),self.worker(off=True)
        self.assertEqual(a['execution_hash'],b['execution_hash'])
        self.assertEqual(a['execution_hash'],c['execution_hash'])
        self.assertEqual(a['state_hash'],c['state_hash'])
        self.assertTrue(a['rng_states'])
        self.assertIn('match.rng.ball',a['rng_states'])
        self.assertEqual(a['rng_states'],c['rng_states'])
        trace=a['trace']
        self.assertGreaterEqual(a['decision_count'],2)
        first=trace['decisions'][0]['intent']
        accepted=next(x['admission'] for x in trace['admissions'] if x['admission'].get('command'))
        self.assertEqual(first['target'],accepted['command']['intent']['target'])
        self.assertTrue(any(d['belief']['own_feedback'] for d in trace['decisions']))
        outcomes=trace['outcomes']
        self.assertTrue(any(o['status']=='released' for o in outcomes))
        self.assertTrue(any(o['status']=='physical_contact' for o in outcomes))
        self.assertGreater(outcomes[0]['resolved_ms'],1000)

    def test_interruption(self):
        r=self.worker('interrupted')
        self.assertIn('interrupted',[e['status'] for e in r['trace']['outcomes']])

    def test_retain(self):
        r=self.worker('retain')
        self.assertEqual(r['trace']['decisions'][0]['intent']['kind'],'retain')

    def test_projector_uses_physical_world_and_poisoned_true_state_isolated(self):
        code='''
from b1.runtime import PhysicalExecutionPort,ObservationProjector,digest
from b1.core import decide
p=PhysicalExecutionPort(1)
import sys
sys.path.insert(0,str(__import__('pathlib').Path('.').resolve()))
import prism_ratings_v0
r=prism_ratings_v0.assign(p.roster_overrides,p.roster_names)['A0']
a=p.m.s.players['A0']; sensor=ObservationProjector(1,a,r)
for t in range(1000,1401,100): sensor.capture(t,p.m.s)
v,b=sensor.deliver(1400,p.m.s)
assert a.active and p.m.s.players['A1'].active and p.m.s.players['B0'].active
assert abs(v.x-a.x)<1e-12 and abs(v.y-a.y)<1e-12 and v.holds_ball
assert any(c.entity=='A1' for c in v.contacts)
assert abs(sensor.prism.prof['cone_half_angle_deg']-(60+60*r['vision']))<1e-9
assert abs(sensor.prism.gaze_az)<1e-12
first=decide(v,b)
p.m.s.players['B0'].x=99.
assert first==decide(v,b)  # true state changes; delivered frame remains fixed
from dataclasses import replace
changed=replace(v,contacts=tuple(c for c in v.contacts if c.entity!='B0'))
changed_b=replace(b,observation_id=changed.observation_id,contacts=changed.contacts)
assert decide(changed,changed_b)==decide(changed,changed_b)
assert changed.contacts!=v.contacts
'''
        r=subprocess.run([sys.executable,'-c',code],cwd=ROOT,text=True,capture_output=True,timeout=45)
        self.assertEqual(r.returncode,0,r.stderr)

    def test_batch_permutation_and_legacy_traps(self):
        code = '''
from dataclasses import replace
from b1.runtime import PhysicalExecutionPort, CommandIngress
from b1.core import ActionIntent
p=PhysicalExecutionPort(1)
i=ActionIntent('a','d','A0','pass','A1',(55.,50.),1000)
j=replace(i,intent_id='b')
results=CommandIngress(p).submit_batch([j,i])
assert results[0][0]=='a' and results[0][1]['status']=='accepted'
assert results[1][1]['reason']=='resource_busy'
for f in [p.m.step,p.m.carrier_decision,p.m.pol['A'].targets]:
    try: f()
    except RuntimeError as e: assert 'legacy tactical' in str(e)
    else: raise AssertionError('trap absent')
print([(x,r['status']) for x,r in results])
'''
        reverse=code.replace('submit_batch([j,i])','submit_batch([i,j])')
        outputs=[]
        for source in (code,reverse):
            r=subprocess.run([sys.executable,'-c',source],cwd=ROOT,text=True,capture_output=True,timeout=45)
            self.assertEqual(r.returncode,0,r.stderr)
            outputs.append(r.stdout)
        self.assertEqual(*outputs)

    def test_command_replay_independent_of_cognition(self):
        code='''
from b1.runtime import PhysicalExecutionPort,CommandIngress,digest
from b1.core import ActionIntent
import b1.core
b1.core.decide=lambda *a: (_ for _ in ()).throw(AssertionError('cognition reached'))
p=PhysicalExecutionPort(1)
i=ActionIntent('fixed','fixed_decision','A0','pass','A1',(55.,50.),1000)
assert CommandIngress(p).submit(i)['status']=='accepted'
p.advance(1600)
assert any(e.get('status')=='released' for e in p.records)
print(digest(p.records))
'''
        results=[]
        for _ in range(2):
            r=subprocess.run([sys.executable,'-c',code],cwd=ROOT,text=True,capture_output=True,timeout=45)
            self.assertEqual(r.returncode,0,r.stderr)
            results.append(r.stdout)
        self.assertEqual(*results)

    @classmethod
    def tearDownClass(cls):
        if cls.before != cls.hashes(): raise AssertionError('historical source changed')


if __name__=='__main__': unittest.main()
