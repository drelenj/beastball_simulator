import ast
import dataclasses
import json
from pathlib import Path
import tempfile
import unittest

from .emergence_intents import (
    ArcherView, AthleteBody, BallCourseBelief, KeeperView,
    ReleasePreparationView, RestartAthleteView, RestartDecisionRecord,
    admit_restart_claims, decide_archer_movement, decide_keeper,
    decide_release_preparation, decide_restart_claim,
    decide_restart_position, plan_keeper_motor,
)
from .preservation import load_inventory, verify_baseline

ROOT=Path(__file__).resolve().parents[1]
INVENTORY=ROOT/'b1/baseline/B0_2abe497_GIT_BLOBS.json'


def body(athlete='B10',team='B',x=2.,y=50.):
    return AthleteBody(athlete,team,x,y,0.,0.,0.,0.,2.2,1.0,
                       9.,11.,12.,.65)


class KeeperOwnershipTests(unittest.TestCase):
    def test_same_delivered_belief_is_the_complete_decision_input(self):
        view=KeeperView('o',1200,body(),0.)
        belief=BallCourseBelief('course-7',1000,1100,20.,52.,2.,-25.,0.,1.)
        first=decide_keeper(view,belief)
        # No authoritative match/ball argument exists to poison.
        self.assertEqual(first,decide_keeper(view,belief))
        params=list(__import__('inspect').signature(decide_keeper).parameters)
        self.assertEqual(params[:2],['view','belief'])
        self.assertNotIn('match',params)
        self.assertNotIn('ball',params)

    def test_belief_changes_threat_while_stale_has_no_truth_fallback(self):
        view=KeeperView('o',1200,body(),0.,position_belief=(3.,48.))
        threat=BallCourseBelief('toward',1000,1100,20.,50.,2.,-25.,0.,1.)
        away=dataclasses.replace(threat,revision='away',vx=25.)
        stale=dataclasses.replace(threat,revision='stale',captured_ms=0)
        self.assertEqual(decide_keeper(view,threat).kind,'save')
        self.assertEqual(decide_keeper(view,away).kind,'position')
        self.assertEqual(decide_keeper(view,stale).kind,'hold')

    def test_motor_rejection_does_not_rewrite_save_as_no_attempt(self):
        view=KeeperView('o',1200,body(x=1.,y=95.),0.)
        belief=BallCourseBelief('corner',1000,1100,15.,50.,2.,-35.,0.,0.)
        intent=decide_keeper(view,belief)
        self.assertEqual(intent.kind,'save')
        command=plan_keeper_motor(intent,dataclasses.replace(
            view.body,acceleration=.1,jump_height=.01,reach=.1),now_ms=1200,
            attempt_margin_m=0.)
        self.assertEqual(command.status,'rejected_infeasible')
        self.assertEqual(intent.kind,'save')


class RestartOwnershipTests(unittest.TestCase):
    def record(self,now=1000):
        return RestartDecisionRecord('r1','scrim','A',(40.,50.),(40.,50.),.9,
                                     1000,1000,4500,'A3')

    def view(self,athlete,now,team='A',x=40.,y=50.):
        return RestartAthleteView('o/'+athlete,now,athlete,team,x,y,True)

    def test_recorded_snapper_is_exclusive_until_35_second_fallback(self):
        record=self.record()
        preferred=decide_restart_claim(self.view('A3',2000),record)
        other=decide_restart_claim(self.view('A4',2000),record)
        self.assertEqual(preferred.kind,'claim_taker')
        self.assertEqual(other.reason,'preferred_taker_window')
        at_boundary=decide_restart_claim(self.view('A4',4500),record)
        self.assertEqual(at_boundary.kind,'claim_taker')

    def test_claim_admission_and_position_are_intent_driven(self):
        record=self.record()
        claims=[decide_restart_claim(self.view('A4',4500,x=40.6),record),
                decide_restart_claim(self.view('A2',4500,x=40.2),record)]
        self.assertEqual(admit_restart_claims(claims).athlete,'A2')
        taker=decide_restart_position(self.view('A2',4500,x=41.),record,'A2')
        defender=decide_restart_position(
            self.view('B0',4500,team='B',x=40.,y=50.),record,'A2')
        self.assertEqual(taker.target,record.taker_spot)
        self.assertGreater(abs(defender.target[0]-record.mark[0]),record.clearance_m)

    def test_claim_requires_physical_arrival_and_approach_is_an_intent(self):
        record=self.record()
        far=decide_restart_claim(self.view('A3',2000,x=50.),record)
        self.assertEqual(far.kind,'approach_restart')
        move=decide_restart_position(self.view('A3',2000,x=50.),record,None)
        self.assertEqual((move.target,move.reason),
                         (record.taker_spot,'approach_taker_claim'))

    def test_rule_record_can_publish_mandatory_spot_without_engine_planning(self):
        record=dataclasses.replace(self.record(),mandatory_spots=(('B0',(45.,50.)),))
        intent=decide_restart_position(
            self.view('B0',4500,team='B'),record,'A3')
        self.assertEqual((intent.target,intent.reason),
                         ((45.,50.),'rules_record_spot'))


class ArcherAndReleaseOwnershipTests(unittest.TestCase):
    def test_archer_tracks_belief_not_true_ball(self):
        view=ArcherView('o',1200,body('A11','A',20.,-5.1),.7,49.3,-5.1,
                        2,18,False)
        belief=BallCourseBelief('b',1000,1100,65.,40.,1.,0.,0.,0.)
        intent=decide_archer_movement(view,belief)
        self.assertEqual(intent.target,(49.3,-5.1))
        shifted=decide_archer_movement(
            view,dataclasses.replace(belief,revision='b2',x=10.))
        self.assertEqual(shifted.target,(10.,-5.1))
        self.assertEqual(decide_archer_movement(view,None).kind,'hold')

    def test_withhold_is_an_explicit_athlete_choice(self):
        def choose(rho,kind='pass'):
            return decide_release_preparation(ReleasePreparationView(
                'o',1000,'A0',kind,rho,1.)).kind
        self.assertEqual(choose(.49),'prepare_release')
        self.assertEqual(choose(.50),'retain')
        self.assertEqual(choose(.99,'kick'),'prepare_release')

    def test_overlay_disables_only_the_legacy_withhold_gate(self):
        tree=ast.parse((ROOT/'b1/emergence_runtime.py').read_text())
        source=ast.unparse(tree)
        self.assertIn('m.c3_withhold = types.MethodType',source)
        self.assertNotIn('s.ball.x',source)


class BaselineInventoryTests(unittest.TestCase):
    def test_inventory_is_the_complete_accepted_commit_tree(self):
        algorithm,files,meta=load_inventory(INVENTORY)
        self.assertEqual(algorithm,'git-blob-sha1')
        self.assertEqual(meta['commit'],'2abe497ca82588cb2d8c871a7aab61daaae95c12')
        self.assertEqual(len(files),427)
        for never_committed in (
                'commit_tree_2abe497.txt','codex_runs/reg_s1.json',
                'baseline/b0_claude_env/MANIFEST.json'):
            self.assertNotIn(never_committed,files)

    def test_clean_tree_guard_ignores_additions_but_rejects_changes(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            data=b'accepted\n'
            import hashlib
            blob=hashlib.sha1(f'blob {len(data)}\0'.encode()+data).hexdigest()
            inv=root/'inventory.json'
            inv.write_text(json.dumps({
                'schema':'b1-baseline-inventory-v2','algorithm':'git-blob-sha1',
                'commit':'x','files':{'accepted.txt':blob}}))
            (root/'accepted.txt').write_bytes(data)
            (root/'untracked.txt').write_text('ignored')
            self.assertEqual(verify_baseline(root,inv),1)
            (root/'accepted.txt').write_text('changed')
            with self.assertRaisesRegex(RuntimeError,'modified: accepted.txt'):
                verify_baseline(root,inv)


if __name__=='__main__':
    unittest.main()
