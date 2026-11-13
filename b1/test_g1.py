import unittest
import math

from .g1 import (CONDITIONS, FAILURE_CAUSES, TERMINALS, _failure_cause,
                 run_episode)


class GovernedScenarioTests(unittest.TestCase):
    def test_replay_and_telemetry_are_observer_neutral(self):
        a=run_episode(1,'C0_uniform',True)
        b=run_episode(1,'C0_uniform',False)
        self.assertEqual(a['execution_hash'],b['execution_hash'])
        self.assertEqual(a['state_hash'],b['state_hash'])
        self.assertIsNotNone(a['trace'])
        self.assertIsNone(b['trace'])

    def test_real_kernel_exhibits_required_outcomes(self):
        fixtures=((1,'C0_uniform','pass_completed'),
                  (10,'C3_close_defender','pass_intercepted'),
                  (35,'C3_close_defender','carrier_grounded'))
        for seed,condition,expected in fixtures:
            with self.subTest(seed=seed,condition=condition):
                result=run_episode(seed,condition,False)
                self.assertEqual(result['endpoint'],expected)
                self.assertIn(result['endpoint'],TERMINALS)
                if result['failure_cause']:
                    self.assertIn(result['failure_cause'],FAILURE_CAUSES)

    def test_only_carrier_and_defender_have_cognition(self):
        result=run_episode(1,'C0_uniform',True)
        actors={d['athlete'] for d in result['trace']['decisions']}
        self.assertEqual(actors,{'A0','B0'})
        self.assertEqual(result['final_state']['players']['A1'][2:4],[0.0,0.0])
        forbidden=set(result['trace']['scenario']['forbidden'])
        self.assertEqual(forbidden,{'formation_anchor','role_assignment',
                                    'scripted_receiver_route',
                                    'scripted_defender_failure'})

    def test_conditions_are_declared(self):
        self.assertEqual(len(CONDITIONS),6)
        self.assertIn('C4_lane_defender',CONDITIONS)
        self.assertIn('C5_lane_defender_sharp',CONDITIONS)

    def test_defender_tracks_released_ball_from_belief(self):
        result=run_episode(2,'C4_lane_defender',True)
        release_ms=next(e['t_ms'] for e in result['trace']['engine_events']
                        if e.get('event')=='release')
        ball_pursuit=[d for d in result['trace']['decisions']
                      if d['athlete']=='B0' and d['intent']['target']=='BALL'
                      and d['view']['delivered_ms']>=release_ms]
        self.assertTrue(ball_pursuit)

    def test_mr1_twenty_seeds_final_direction_matches_semantic_aim(self):
        for seed in range(1,21):
            with self.subTest(seed=seed):
                result=run_episode(seed,'C0_uniform',True)
                evidence=result['trace']['flight_evidence']
                self.assertLess(evidence['release_direction_error_deg'],8.)
                self.assertTrue(evidence['moving_release_recomputed'])
                self.assertLessEqual(evidence['correction_angle_deg'],60.)

    def test_failure_attribution_can_report_unknown(self):
        cause,basis=_failure_cause('pass_incomplete_ball_loose',{})
        self.assertEqual(cause,'unknown')
        self.assertIn('does not establish',basis)


if __name__=='__main__':
    unittest.main()
