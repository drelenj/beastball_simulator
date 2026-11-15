// Canon (Rulebook 1.0) field and rules constants. Units: metres, seconds.
// Coordinates: x along the field (goals at x = -50 and +50), y across (-50..50), z up.
export const FIELD_HALF = 50;               // playing surface 100 m x 100 m
export const GOAL_R = 3;                    // goal: semicircle radius 3 m front view (6 m base, 3 m high)
export const BALL_R = 0.11;                 // ARCADE PLACEHOLDER ball radius
export const KEEPER_ZONE_R = 20;            // area closer than 20 m to goal centre
export const PLATFORM_BACK = 5;             // archer platform 5 m back from boundary
export const PLATFORM_H = 5;                // and 5 m high, centred on the goal plane
export const CENTRE_CIRCLE_R = 5;           // centre circle 10 m across
export const SCRIM_LINE = 40;               // 40 m scrimmage lines parallel to each goal
export const PERIOD_LEN = 600;              // 4 periods of 600 s game time
export const OT_LEN = 300;                  // first overtime 300 s, then sudden death
export const PLAY_CLOCK = 30;               // 30 s per possession
export const SNAP_LIMIT = 10;               // snap within 10 s
export const KZ_ATTACKER_LIMIT = 5;         // attackers in Keeper Zone at most 5 s at a time
export const ARROWS_PER_POSS = 15;          // per team possession
export const FREEZES_PER_POSS = 5;
export const ARROW_SPEED = 250;             // m/s, no cap
export const FREEZE_TIME = 5;
export const IMMUNE_TIME = 10;
export const RECOVERY_DIST = 3, RECOVERY_TIME = 2;
export const SPEED_UNIT = 44.704;           // speed rating 1.0 = 44.704 m/s
export const MAJOR_EXCL = 120, MINOR_EXCL = 60;
export const TOSS_IN_CLEAR = 3;
export const G = 9.81;
export const DT = 1 / 60;                   // fixed simulation step
export const BREAK_SHORT = 120, BREAK_HALF = 600; // shown as skippable screens
