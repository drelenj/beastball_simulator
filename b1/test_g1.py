import unittest

from .g1 import CONDITIONS, FAILURE_CAUSES, TERMINALS, run_episode


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
        self.assertEqual(len(CONDITIONS),4)


if __name__=='__main__':
    unittest.main()
