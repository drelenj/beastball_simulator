import unittest
from dataclasses import replace
from beastball_unified_locomotion_v30 import *
class TestV30(unittest.TestCase):
 def setUp(self):self.p=profile('average','field')
 def test_invalid_dt(self):
  with self.assertRaises(ValueError):Settings(dt=0)
 def test_invalid_speed(self):
  with self.assertRaises(ValueError):World(self.p).setup(50)
 def test_initial_foot_separation(self):
  s=World(self.p).setup(10);self.assertNotEqual(s.left,s.right)
 def test_no_flight_contact(self):
  w=World(self.p);s=replace(w.setup(10),phase='flight',z=.2,vz=.5)
  n=w.step(s);self.assertEqual(n.normal_N,0);self.assertEqual(n.shear,(0.,0.))
 def test_flight_velocity_constant(self):
  w=World(self.p);s=replace(w.setup(10),phase='flight',z=.2,vz=.5)
  n=w.step(s);self.assertAlmostEqual(n.vx,s.vx)
 def test_gravity(self):
  w=World(self.p);s=replace(w.setup(10),phase='flight',z=.2,vz=.5)
  self.assertLess(w.step(s).vz,s.vz)
 def test_traction_bound(self):
  w=World(self.p);s=w.setup(10)
  for _ in range(100):
   s=w.step(s);self.assertLessEqual(length(s.shear),w.mu*s.normal_N+1e-7)
 def test_no_foot_teleport(self):
  w=World(self.p);s=w.setup(20)
  for _ in range(100):
   n=w.step(s)
   self.assertLessEqual(length((n.left[0]-s.left[0],n.left[1]-s.left[1])),w.c.swing_speed_m_s*w.c.dt+1e-8)
   self.assertLessEqual(length((n.right[0]-s.right[0],n.right[1]-s.right[1])),w.c.swing_speed_m_s*w.c.dt+1e-8)
   s=n
 def test_support_anchor(self):
  w=World(self.p);s=w.setup(20);anchor=s.left
  for _ in range(30):s=w.step(s)
  self.assertEqual(s.left,anchor)
 def test_landing(self):
  r=assess(self.p,10,Settings(duration_s=.8));self.assertGreaterEqual(r['landings'],1)
 def test_no_flight_mode(self):
  r=assess(self.p,10,Settings(flight_enabled=False));self.assertEqual(r['takeoffs'],0);self.assertFalse(r['grounded'])
 def test_turn(self):
  r=assess(self.p,10,Settings(turn_degrees=90,duration_s=.6));self.assertGreater(r['y_m'],0)
 def test_straight(self):
  r=assess(self.p,10,Settings(turn_degrees=0,duration_s=.6));self.assertAlmostEqual(r['y_m'],0)
 def test_deterministic(self):
  c=Settings(duration_s=.5);self.assertEqual(assess(self.p,10,c),assess(self.p,10,c))
 def test_no_friction_violation(self):
  self.assertEqual(assess(self.p,20)['friction_violation_N'],0)
 def test_strength(self):
  weaker=replace(self.p,athlete=replace(self.p.athlete,strength=.2))
  strong=replace(self.p,athlete=replace(self.p.athlete,strength=1.))
  c=Settings(flight_enabled=False,duration_s=.3,traction=4.)
  self.assertGreater(assess(strong,0,c)['vx_m_s'],assess(weaker,0,c)['vx_m_s'])
 def test_timestep(self):
  a=assess(self.p,10,Settings(dt=.005,duration_s=.5,flight_enabled=False))
  b=assess(self.p,10,Settings(dt=.0025,duration_s=.5,flight_enabled=False))
  self.assertLess(abs(a['x_m']-b['x_m']),.3)
if __name__=='__main__':unittest.main()
