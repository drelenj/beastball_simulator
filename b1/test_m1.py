import dataclasses
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from .core import AthleteView, BeliefState, Contact, DecisionConfig, decide
from .preservation import historical_hashes, verify_baseline

ROOT=Path(__file__).resolve().parents[1]


class PureBoundaryTests(unittest.TestCase):
    def test_baseline_guard_detects_preexisting_modification_and_missing_file(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            source=root/'source.py'
            source.write_text('original')
            inventory=root/'inventory.json'
            inventory.write_text(json.dumps({'source.py':hashlib.sha256(b'original').hexdigest()}))
            self.assertEqual(verify_baseline(root,inventory),1)
            source.write_text('changed')
            with self.assertRaisesRegex(RuntimeError,'modified: source.py'):
                verify_baseline(root,inventory)
            source.unlink()
            with self.assertRaisesRegex(RuntimeError,'missing: source.py'):
                verify_baseline(root,inventory)

    def test_decision_values_are_immutable(self):
        v=AthleteView('o','A0','A',1500,40,50,True,(Contact('A1','A',55,50,1000),))
        b=BeliefState('b','o',v.contacts)
        first=decide(v,b)
        self.assertEqual(first,decide(v,b))
        with self.assertRaises(dataclasses.FrozenInstanceError): v.x=100

    def test_pending_action_and_failure_feedback_change_the_decision(self):
        contacts=(Contact('A1','A',55,50,1500),)
        view=AthleteView('o','A0','A',1500,40,50,True,contacts)
        ordinary=decide(view,BeliefState('b','o',contacts))[0]
        self.assertEqual(ordinary.kind,'pass')
        pending=dataclasses.replace(view,pending_command_id='cmd-1',pending_release_ms=1700)
        continuing=decide(pending,BeliefState('b2','o',contacts))[0]
        self.assertEqual((continuing.kind,continuing.related_command_id),
                         ('continue_current','cmd-1'))
        failed=BeliefState('b3','o',contacts,(('out','interrupted',1490),))
        self.assertEqual(decide(view,failed)[0].kind,'no_action')

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
        modules=[]
        for node in ast.walk(tree):
            if isinstance(node,ast.ImportFrom): modules.append(node.module)
            elif isinstance(node,ast.Import): modules.extend(a.name for a in node.names)
        self.assertEqual(sorted(modules),['dataclasses','math'])
        symbols={n.id for n in ast.walk(tree) if isinstance(n,ast.Name)}
        symbols.update(n.attr for n in ast.walk(tree) if isinstance(n,ast.Attribute))
        self.assertFalse(symbols & {'SimState','Match','Engine','PhysicalExecutionPort',
                                    'CommandIngress','pocket4_proto'})


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
        self.assertIn('continue_current',[d['intent']['kind'] for d in trace['decisions']])
        self.assertFalse(any(a['admission'].get('reason')=='resource_busy'
                             for a in trace['admissions']))
        outcomes=trace['outcomes']
        self.assertTrue(any(o['status']=='released' for o in outcomes))
        self.assertTrue(any(o['status']=='physical_contact' for o in outcomes))
        self.assertNotIn('physical_contact',[f[1] for f in trace['athlete_feedback']])
        self.assertGreater(outcomes[0]['resolved_ms'],1000)
        timing=trace['timing']
        self.assertEqual(timing['first_decision_ms'],timing['decision_times_ms'][0])
        self.assertEqual(timing['effective_decision_period_ms'],200)
        self.assertLess(timing['first_ready_ms'],timing['first_decision_ms'])

    def test_interruption(self):
        r=self.worker('interrupted')
        self.assertIn('interrupted',[e['status'] for e in r['trace']['outcomes']])
        affected=[d for d in r['trace']['decisions']
                  if d['decision']['considered_feedback'] and
                  any(f[1]=='interrupted'
                      for f in d['decision']['considered_feedback'])]
        self.assertEqual(len(affected),1)
        self.assertEqual(affected[0]['intent']['kind'],'no_action')

    def test_defender_pursuit_is_derived_from_belief(self):
        contacts=(Contact('A0','A',45,50,1000,2,-1),
                  Contact('BALL','neutral',45.2,50.1,1000,2,-1))
        view=AthleteView('o','B0','B',1200,50,51,False,contacts)
        intent,trace=decide(view,BeliefState('b','o',contacts),
                            DecisionConfig('defender'))
        self.assertEqual((intent.kind,intent.target),('move','A0'))
        self.assertNotEqual(intent.aim,(45,50))
        shifted=tuple(dataclasses.replace(c,x=c.x+3) for c in contacts)
        moved=decide(dataclasses.replace(view,contacts=shifted),
                     BeliefState('b2','o',shifted),
                     DecisionConfig('defender'))[0]
        self.assertAlmostEqual(moved.aim[0]-intent.aim[0],3)

    def test_retain(self):
        r=self.worker('retain')
        self.assertEqual(r['trace']['decisions'][0]['intent']['kind'],'retain')

    def test_projector_uses_physical_world_and_poisoned_true_state_isolated(self):
        code='''
from b1.runtime import PhysicalExecutionPort,ObservationProjector,digest
from b1.core import decide
from dataclasses import asdict
import json,sys
p=PhysicalExecutionPort(1)
sys.path.insert(0,str(__import__('pathlib').Path('.').resolve()))
import prism_ratings_v0
r=prism_ratings_v0.assign(p.roster_overrides,p.roster_names)['A0']
a=p.m.s.players['A0']; sensor=ObservationProjector(1,a,r)
mode=sys.argv[1]
d=p.m.s.players['B0']
if mode in ('hidden-a','hidden-b'):
    d.x,d.y=(2.,95.) if mode=='hidden-a' else (3.,94.)
if mode=='hidden-b':
    d.fatigue=.123; d.freeze_until=99999; d.next_action=99999
    d.target=(1.,1.); d.posture='hidden-sentinel'
elif mode=='visible':
    d.x,d.y=47.,50.8
for t in range(1000,2001,100): sensor.capture(t,p.m.s)
v,b=sensor.deliver(2000,p.m.s)
i,tr=decide(v,b)
print(json.dumps({'view':asdict(v),'intent':asdict(i),'decision':tr},sort_keys=True))
'''
        results={}
        for mode in ('hidden-a','hidden-b','visible'):
            r=subprocess.run([sys.executable,'-c',code,mode],cwd=ROOT,text=True,
                             capture_output=True,timeout=45)
            self.assertEqual(r.returncode,0,r.stderr)
            results[mode]=json.loads(r.stdout)
        self.assertEqual(results['hidden-a'],results['hidden-b'])
        self.assertNotEqual(results['hidden-a']['view'],results['visible']['view'])
        self.assertEqual(results['hidden-a']['intent']['kind'],'pass')
        self.assertEqual(results['visible']['intent']['kind'],'retain')

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
