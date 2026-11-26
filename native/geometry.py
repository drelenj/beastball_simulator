"""Configured exact rule geometry; metres. Body contacts use the physical proxy below."""
import math

def goal_section(y,z,radius,goal_radius=3.):
    return z>=radius and math.hypot(y-50,z)+radius<=goal_radius

def whole_ball_crossed(x,radius,goal_x):
    return x+radius<=0 if goal_x==0 else x-radius>=100

def net_volume(depth,y,z,radius=0.,goal_radius=3.,goal_depth=3.):
    return (depth>=radius and goal_section(y,z,radius,goal_radius) and
            math.hypot(depth,z)+radius<=goal_depth)

def body_out(p, mouth_radius=None):
    # PLACEHOLDER: body cylinder/ground-contact envelope; detailed toes/hand
    # support witnesses replace this proxy in Native v1.
    if mouth_radius is not None and goal_section(p.y,p.hand_height,.1075,mouth_radius):
        return p.posture!='airborne' and (p.y-p.radius<=0 or p.y+p.radius>=100)
    return p.posture!='airborne' and (p.x-p.radius<=0 or p.x+p.radius>=100 or p.y-p.radius<=0 or p.y+p.radius>=100)
