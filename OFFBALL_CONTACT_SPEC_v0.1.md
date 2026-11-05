# Off-ball contact: spec v0.1 (draft, 1 Nov 2026)
Tags: [C] canon (DreLen), [I] my interpretation (needs confirming), [P] provisional, [E] what the engine does today (Pocket 2.0, read from the code).

## Canon [C] (DreLen, 1 Nov)
1. Off the ball, a player may touch another player only **below the neck and above the hip**, including the shoulder and arms.
2. **Hip jockeying is legal.**
3. You may **push and stab with the hands**. **No pulling or gripping.**
4. Applies to offence and defence alike.
5. Defender vs ball-carrier: a defender may **wrap and grip the ball carrier from below the neck down** (so gripping is legal on the carrier only; the legal zone on the carrier is everything below the neck, not just the torso band).
6. Off-ball contact that breaks the rule is a **minor foul**; a proper foul system is still to be designed.
7. Off-ball push or stab **can knock a player down if the physics allow** (no rule-level cap; the balance model decides).
8. Landing contact in the legal band is governed by **Motor Control, with Focus**.
9. Judgment decides **contain versus drive** (defender holding the carrier up vs driving him down).

## Contact vocabulary [I] (what the rule needs the engine to tell apart)
| Contact | Body part | Off-ball | Note |
|---|---|---|---|
| push | hands/arms/shoulder to torso, shoulder, arm | legal | impulse, no retained grip |
| stab | hand strike to torso, shoulder, arm | legal | short impulse; defines how a hand can fend or slow |
| jockey | hip/body positional contact | legal | positioning, body-to-body, no grip |
| grip / pull | any retained hold, or force toward the puller | foul | the line between push and grip is retention plus pulling force |
| head, neck | | foul | already dangerous surface |
| below the hip: thigh, knee, leg | | foul | new: engine only lists knee/joint, not thigh or lower leg [E] |

## What the engine does today [E]
- `contact_legal` refuses surfaces head, neck, spine, groin, joint, knee, claw, horn, weapon (dangerous_surface, a major foul). There is no concept of the hip band or of "above the hip" as a legal zone; the default surface is "torso".
- Off-ball contact is the `block` engagement. Its only positional rule is the blindside rule (hit from directly behind). It does not distinguish push, stab, jockey and grip.
- Gripping exists only as the carrier hold (`c3_holds`: grip g, region, mode contain/drive). Off-ball players have no hold, so a grip off-ball is not currently possible or punishable.
- `c3_contain` (contain vs drive) is a fixed placeholder: contain iff tackle count is 0 and the carrier's zone time will expire within `containment_window_s` (2 s, same for every defender).

## Gaps to close
1. Surface vocabulary: add the legal bands (torso, shoulder, arm, hand-push, hip-jockey) and mark everything else illegal, including thigh/lower leg.
2. Contact types: push / stab / jockey as impulses with no retained hold; "grip or pull" as the foul condition (a retained hold or sustained pulling force off-ball).
3. Foul severity ladder for off-ball (minor vs major) [Q2].
4. PRISM link: legality is a Strategy constraint (a defender chooses among legal actions), and where the contact lands is Motor Control. Which rating governs target accuracy is not decided [Q4].
5. Judgment: contain vs drive replaces the fixed 2 s window (below).

## Judgment: contain vs drive [P], measure first
Plan: (a) log every contain/drive decision with the zone clock, tackle count, grip and strength ratio, and the outcome (turnover by expiry, grip broken or escape, first tackle taken); (b) from that find where contain actually pays; (c) Judgment sets how well the defender picks the right one, with the same menu for everyone (as in the pursuit work). Paired measurement on identical decisions, not game goals.

## Answered (1 Nov)
Q1 carrier: wrap and grip from below the neck down. Q2 off-ball foul: minor; foul system to be designed. Q3 knockdowns: yes if physics allows. Q4 targeting: Motor Control with Focus.

## Open questions (new)
- **Q5.** 'Below the neck down' on the carrier would make legs legal to wrap. The engine currently treats knee and joint as dangerous (major foul). Should knee/joint stay illegal on the carrier, or does the carrier rule override it?
- **Q6.** Foul system: what should it cover (minor/major ladder, what a minor costs, accumulation, who gets the restart)? I can draft a starting ladder from the engine's current fouls.

## Superseded questions
- **Q1.** "Defender vs ball-carrier is the same": the same legal zone (below neck, above hip), with gripping and wrapping still allowed to hold the carrier? Or no gripping at all on the carrier either (which would remove wraps and holds)? I assume the first.
- **Q2.** Off-ball foul severity: is any illegal contact a major, or is a push above the shoulders minor?
- **Q3.** Can an off-ball push or stab knock a player down, or only shift and slow him? (the engine's balance model already lets large impulses unbalance)
- **Q4.** Which rating governs landing the contact in the legal band (Motor Control, with Focus/Clarity)?
