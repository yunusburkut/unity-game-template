# Feedback stack: feel rules, layers, patterns and per-action targets

This file decides *which layer and how loud*; `numbers.md` decides *how much*. Never restate its values here. The IDs
(`FR14`, `FS6`, `FP28`, `FX07`) are local to this skill and stable: cite them in reviews, append new ones, never
renumber.

## Contents

- §1 Priority order
- §2 FR: feel rules (15)
- §3 FS: the eight layers
- §4 FP: feel patterns (32)
- §5 Per-action target (fill in per game)
- §6 FX: feel anti-patterns (10)
- §7 Checklist before adding an effect

---

## 1. Priority order

**Mechanic clarity > readable state change > meaningful feedback > decorative juice.** A lower tier never pays for a
missing higher one: a door nobody can link to its switch is a clarity problem, and no particle fixes it.

The evidence, as secondary summaries:

- Swink (2009) supplies the vocabulary (input, response, context, polish), not data.
- Kao (2020, N = 3018, an action RPG) compared four juice levels: *none* and *extreme* both scored worse than
  *medium* and *high* on play time, experience, motivation and performance. The curve is an inverted U: the goal is a
  band, not a maximum.
- Hicks et al. (DiGRA 2018): judge juice as a coherent system of categories, not a pile of effects.
- Hicks et al. (CHI PLAY 2019): visual embellishment reliably raised visual *appeal*; effects on *competence*
  depended on context.
- Singhal & Schneider (CHI 2021): vibrotactile embellishment in a phone Breakout clone improved player experience. This
  is the direct evidence for haptics on mobile.

These come from other genres. Take the direction (a band, contrast, coherence), not the magnitudes; magnitudes come
from `numbers.md` and Play Mode.

---

## 2. FR: feel rules (15)

| ID | Rule | What it means in practice |
|---|---|---|
| FR01 | **Mechanics before juice**: no effect until action, change and consequence read without it. | Play every new beat once with every `MMF_Player` off; it must still read. |
| FR02 | **Feedback confirms causality**: the player can say what they did, what changed and why. | A switch that opens a door somewhere needs a visible link, not only a door that moves. |
| FR03 | **Stay inside the useful intensity band**: dead and overloaded both lose. | Empty feedback slots sit at "none"; five equal layers on a landing lean to "extreme". |
| FR04 | **One event, one hierarchy**: primary loudest, secondary supports, ambience stays quiet. | Name one primary channel per action (§5). |
| FR05 | **Redundancy reinforces, never contradicts**: every channel reports one timing and one magnitude. | Pick one light/heavy threshold pair and use it in sound, particles, animation and haptics. |
| FR06 | **Magnitude matches gameplay importance**: a small event never outshouts a big one. | Win > failure > checkpoint > routine verbs. |
| FR07 | **Visual appeal is not competence**: prettier is not more skilful. | Spend effort on reading hazards and targets, not on bloom. |
| FR08 | **Response latency is part of feel**: quick acknowledgement beats one more layer. | Budget 100 ms from press to visible change. |
| FR09 | **Recovery deserves feedback too**: near-fail, catch, rescue and stabilise read, not only success. | Spawn protection, a last-moment save, an undo: each gets a cue. |
| FR10 | **Social consequences need attribution** (multiplayer): show who caused it when that is fair and useful. | The player colour is the attribution channel. |
| FR11 | **Do not juice hidden information**: no effect leaks what the mechanic conceals. | A secret, a hidden tile or a private role gets no idle glow, sound or particle. |
| FR12 | **Haptics are a scarce channel**: no buzz per tap; distinct signatures for events that matter. | On PC carry the lesson to audio: one distinct sound per event class. |
| FR13 | **Synchronise multisensory peaks**: the strongest sound, visual, motion and haptic accents share one frame. | The jump peaks at launch, not at the press; the landing at the landed edge. |
| FR14 | **Contrast, not constant intensity**: quiet stretches make the big impacts land. | Routine verbs stay small so the win can be the largest thing in the level. |
| FR15 | **Measure before adding**: if it already reads, name the problem another effect solves. | On a routine verb, remove one effect before adding another. |

---

## 3. FS: the eight layers

Walk them in order for every notable action. A layer may be absent, but on purpose.

| ID | Layer | Question it answers | Typical channels |
|---|---|---|---|
| FS1 | Intent cue | What can I do here, and what is about to happen? | Highlight, idle animation, prompt, telegraph |
| FS2 | Input acknowledgement | Did the game hear me? | Press squash, button scale, click sound, light haptic |
| FS3 | State transition | What changed? | Motion, material swap, icon change |
| FS4 | Physical consequence | How did it move, how heavy was it? | Simulation motion, springs, knockback, ragdoll |
| FS5 | Sensory reinforcement | How big was it? | Particles, sound, post-FX, shake, hit stop, haptics |
| FS6 | Social attribution | Who did it, to whom, on purpose? | Player colour, cause label, results screen |
| FS7 | Recovery window | Can it still be saved? | Coyote time, buffers, grace periods, undo |
| FS8 | Resolution | How did it end, what is kept? | Checkpoint, results, score, unlock |

---

## 4. FP: feel patterns (32)

| ID | Pattern | Use |
|---|---|---|
| FP01 | Anticipation compression | Short squash, hold or rising pitch just before a release. Hazards, not player verbs. |
| FP02 | Impact accent | One very short peak at contact: punch, flash, freeze or transient. |
| FP03 | Follow-through | Secondary motion that settles after the event (springs on limbs, a wobble). |
| FP04 | Energy trail | Trail, density or brightness scales with speed or force. |
| FP05 | State snap | A crisp cue when a continuous input crosses a discrete threshold (a latch, a snap into place). |
| FP06 | Tension readout | Bend, strain sound, colour or meter exposes building tension. |
| FP07 | Near-fail warning | A rising, non-blocking cue as the system nears failure. |
| FP08 | Recovery pop | A smaller, distinct reward when a failing state is rescued. |
| FP09 | Team save accent | A save gets local cues for everyone involved plus a shared-world cue (multiplayer). |
| FP10 | Sabotage signature | A compact, mischievous cue marking deliberate interference (multiplayer). |
| FP11 | Cause tag | A brief marker, colour or icon naming who or what triggered an event. |
| FP12 | Chain reaction escalation | Each linked reaction grows or shifts pitch, reading as a sequence (combos, cascades, match chains). |
| FP13 | Soft failure collapse | Failure shows as visible loss of control, not instant removal. |
| FP14 | Delayed consequence telegraph | A latent effect leaves a trace from cause to later result. |
| FP15 | Shared object weight | Every channel conveys the same mass (and on every machine online). |
| FP16 | Sticky grab | Grab and release get different, unmistakable signatures. |
| FP17 | Friction contrast | Surfaces differ in acceleration, sound, particles and stopping distance. |
| FP18 | Elastic contrast | Springy overshoots, rigid stops dead, soft deforms and recovers. |
| FP19 | Danger rhythm | Hazards keep a learnable audiovisual cadence. |
| FP20 | Success breath | A brief quiet settle after intensity, before the reward. |
| FP21 | Readable randomness | Random results get an anticipation phase and a reveal (loot, a deal, a spin). |
| FP22 | Escalating retry | Repeated failures vary the cosmetic reaction; mechanics stay deterministic. |
| FP23 | Ambient confirmation | A low persistent cue confirms a held state without demanding attention. |
| FP24 | Directional impact | Sound, particles or camera point along the real force. |
| FP25 | Depth cue | Scale, shadow, parallax, squash and sound make depth legible. |
| FP26 | Momentum read | Lean, trail, dust and camera lag show acceleration before contact. |
| FP27 | Ownership colour echo | The controller's colour briefly runs through what they control. |
| FP28 | Control transfer pulse | Outgoing and incoming owner receive matched, opposite cues. |
| FP29 | Hidden role protection | Private cues stay private; public cues show only what the rules permit. |
| FP30 | Object exhaustion | Near a limit or a cooldown, feedback changes rather than going silent (a press during cooldown fizzles visibly). |
| FP31 | Resolution freeze | After a spectacular failure, hold the framing briefly so the moment registers. |
| FP32 | Comedic aftermath | Harmless residual motion and late sounds finish the joke. |

---

## 5. Per-action target (fill in per game)

The most important table for a real game, and the one this template cannot fill. Copy it into `DESIGN.md`, one row per
action, and keep the *Today* column as the inventory of what actually plays.

**Tier** sets the magnitude: *routine* (many per minute) may use shake, freeze or screen effects at small magnitude;
*notable* (a few per minute) sits mid; *rare* (per level) gets the largest screen, camera, time and haptic accents.

| Action | Tier | Primary channel | Today | Missing layers (FS) | Target |
|---|---|---|---|---|---|
| e.g. Jump | routine | body squash + sound | — | FS2, FS5 | Squash and a dry sound on the launch frame (FR13) |
| e.g. Tap a tile | routine | tile pop + click + light haptic | — | FS2 | Press scale on the press frame, release EaseOutBack |
| e.g. Wrong move | notable | shake on the object + warning haptic | — | FS3, FS7 | Object-local shake, never the camera; undo stays one tap |
| e.g. Level complete | rare | whole-screen resolution | — | FS5, FS8 | Brief settle (FP20), then the loudest stack in the level |
| e.g. Failure | rare | collapse + sting | — | FS6, FS7 | Visible loss of control (FP13); the retry starts fast |

Order of work for an unpolished game: (1) acknowledge every press inside 100 ms; (2) one distinct sound per event
class; (3) the win and the failure; (4) routine juice, small.

---

## 6. FX: feel anti-patterns (10)

| ID | Anti-pattern | What it looks like |
|---|---|---|
| FX01 | Particle confetti on every action | Every verb emits particles; nothing stands out. |
| FX02 | Camera shake as default feedback | Shake on routine verbs at rare-event magnitude. |
| FX03 | Long hit stop in multiplayer movement | Any freeze that stops other players' control. |
| FX04 | Same sound or haptic for all events | One generic pop reused across event classes. |
| FX05 | Juice that changes collision perception | Squash, tilt or trails that suggest a hitbox or timing that is not real. |
| FX06 | Success effects before confirmation | Online: the win plays on the local guess and replays or contradicts the authority. |
| FX07 | Global feedback for private actions | A partner's action flashes your screen or buzzes your phone. |
| FX08 | Vibration on every UI interaction | Every button, scroll or toggle buzzes. |
| FX09 | Extreme feedback stacking | Every channel fires on one routine event. |
| FX10 | Polish masking weak mechanics | No level has been played with every `MMF_Player` off. |

---

## 7. Checklist before adding an effect

1. With every `MMF_Player` off, does the action and its result still read? (FR01)
2. Does acknowledgement land on the press frame, inside 100 ms? (FR08)
3. Is the strongest signal on the most important state change of this beat? (FR04, FR06)
4. Do all channels peak on one frame and share one magnitude threshold? (FR05, FR13)
5. Routine or rare? Routine keeps any channel small; the largest accents are for rare events. (FR14)
6. Are hazards, the landing spot or the next tap target still visible through it? (FX05)
7. Multiplayer: if a player caused it, does it carry their colour? Is it private, gated to the local player? Does it
   wait for the authority's confirmed edge? (FR10, FR11, FX06, FX07)
8. Is recovery signalled as clearly as failure? (FR09)
9. Muted, does it still read, and unmuted, is its sound distinct from every other event's? On a phone, is the haptic
   distinct and switchable? (FR12, FX04, FX08)
10. Which problem does it solve (response, causality, readability, anticipation, impact, emotion), and which existing
    effect can go instead? (FR15)
