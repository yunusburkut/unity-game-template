# Level design playbook: horizontal 2.5D co-op

The working document. `reference-teardowns.md` is the evidence and `coop-mechanics-playbook.md` is the
mechanical decision; this is how a level gets drawn.

Two kinds of number appear below. **Sourced** values come from the reference games or from
`gamekit:game-feel`'s `references/` and are cited. **Starting values** are derived from Mixtrol's own
geometry — the `LevelPalette` grid is 1.25 m, `CameraFollow` frames the group at 24–40 m — and are
marked *(starting value)*. Tune those in Play Mode and write the result back into this file. Never quote
a starting value as if it were evidence.

> **Status 2026-09-22.** Written when the carried object was the planned primary coupling; the GDD has
> since made the control swap primary. Failure is now two-tiered (tier 1 recovered in place within
> 3–8 s, tier 2 = shared death + one segment). The method for beats, recovery and escalation is
> `docs/design-corpus/`; `level-beat-review` is the current checklist. Where this document and the GDD
> disagree, the GDD wins.
>
> **Difficulty order (2026-10-01).** How challenge is ordered against relief — the sawtooth, valleys, where
> checkpoints and new devices sit, troll rationing, talk windows — is `docs/difficulty-rhythm.md` (rules
> DR01–DR28). This document keeps the beat and segment mathematics; where they disagree on ordering, the
> rhythm doc wins and its §E lists what was proposed to the user.
>
> What is **not built**, whatever the body below says: the time-based stress grace window (240 ms floor,
> per difficulty) — stress is a pure function of carrier separation (`CarriedObjectSolver.StressAt`);
> `Cracked` fires when separation passes `stressSpan` and spilling starts the same step. The cauldron
> cannot break ("Kırılır" is future per the GDD; `CarriedObjectState` has `Cracked`, `Caught` and
> `Spilling`, no `Broke` edge). There is no soft tether and no per-character carry force: `MovementState`
> holds a `CarryLoad` speed multiplier and a facing lock.

## Rule zero

**Design the clip, then build the level around it.**

Every breakout in this genre is structurally optimised for what a viewer sees, not only for what a player
does. That is not marketing varnish applied afterwards — Chained Together's regions, PEAK's mountain,
Carry The Glass's single fragile pane are all shaped so that failure is visible, dramatic, and legible.

Practically: before placing a single prefab, write one sentence describing the clip this segment
produces. "Three of them get the pane through the fan, the fourth walks into it." If you cannot write
that sentence, you are building corridor, not content. Corridor is allowed — it is the rest between beats
— but it must be deliberate and it must be short.

## Manufacturing visible loss without gravity

The horizontal axis does not hand you a loss engine. You have to build one. Four are available; the level
chooses which is running at any moment, and **only one runs at a time**.

*Decided 2026-09-22:* the swap is the always-on floor, not a loss engine; on top of it a beat or segment
runs **at most one** loss engine — the cauldron or the chase, not both.

### 1. Object integrity

The carried object degrades or breaks. It was planned as the primary engine at ~70 % of level time
*(starting value)*; in the built game the cauldron **spills** (a run score, not a segment loss) and the
swap's wrong-moment press is the more frequent loss. Losing the cauldron outright is tier 2.

Design it as three visible states, not a hidden hit-point counter:

| State | Reads as | Player affordance |
|---|---|---|
| Intact | clean, quiet | free movement |
| Stressed | visible crack, audible creak, tilt | the grace window — a partner can still save it |
| Broken | shatter, reset | none |

The stressed state must last at least **240 ms** — the human perceive-decide-act loop
(`game-feel/references/sources.md`). Shorter than that is not a warning, it is a cutscene of the failure.
Difficulty modes tune this window, not the level geometry. *(2026-09-22: not built; a window two machines
must agree on is ≥ 1 s, and it is not a difficulty knob.)*

**Never let a break be ambiguous.** The frame that contains the break must also contain the cause.

### 2. Chasing hazard — the lava substitute

Chained Together's hardcore mode adds rising lava, converting a spatial problem into a time problem. The
horizontal equivalent is a wall, a flood, a collapsing floor, or a pursuer moving right at a fixed speed.

Use it sparingly — in the last third of a level, or as a difficulty mode — because it removes deliberation,
and deliberation is where co-op arguments happen. A chase is loud but it is not funny; it is tense.
**Cap it at 2 segments per level** *(starting value)*.

### 3. Rewind — the checkpoint as a visible distance

**Not adopted (2026-09-22):** the tier-2 return stays the 0.7 s collapse + teleport (`Respawn.asset`); no
rewind, no fade. The rest of this section is kept as the rejected option.

On failure, do not fade to black and respawn. **Pull the players backwards through the level they just
crossed**, visibly, so the loss is measured in metres they can see. This is the horizontal translation of
falling, and it is the single most important trick in this document. A fade-to-black respawn throws away
the entire loss engine; a visible reverse trip preserves it.

Budget: the rewind animation should take **1.5–3 s** *(starting value)*. Long enough to hurt and to be
clipped, short enough that it does not become the game. *(Not built: today `Respawn.asset` is a 0.7 s
collapse then a teleport, no fade, and `RespawnConfig`'s tooltip caps the whole beat at 1.5 s. The rewind
applies to tier-2 failures only; tier-1 mistakes recover in place.)*

### 4. Shared counter — the pressure layer only

Lives, a fuse, a shared stamina. Never the primary engine, for the reason given in
`coop-mechanics-playbook.md`: a bar going down does not point at anybody. Layer it under 1 or 2 the way
PEAK layers stamina under climbing.

## Segment and checkpoint mathematics

A **segment** is the distance between two checkpoints. It is the unit of loss, and therefore the unit this
whole document is about.

### The band

| | Target | Why |
|---|---|---|
| Segment traversal, clean run | 45–90 s *(starting value)* | Under 45 s the loss does not sting; over 90 s players stop retrying |
| Segment length in grid units | 40–80 cells at 1.25 m = 50–100 m *(starting value)* | Derived from `LevelPalette.gridSize` and the traversal band |
| Loss on failure | one full segment | Enough to hurt, bounded enough to be survivable |
| Segments per level | 8–14 *(starting value)* | 10–20 minutes clean, 45–90 minutes realistically |
| Beats per segment | 3–5 *(starting value)* | Below 3 the segment is corridor; above 5 nothing lands |

**The rule that governs all of these: a group must be able to lose the same segment four times without
quitting.** If playtesters quit on the third loss, the segment is too long or its failure is unfair — and
"unfair" in co-op almost always means *unattributable*, not *hard*.

### Difficulty as a dial, not a constant

Carry The Glass and Chained Together both shipped a difficulty dial, and it is why one build served
streamers and casual friend groups simultaneously. Carry The Glass ships Normal / Hard (fewer checkpoints) / Impossible (none).
Chained Together ships Beginner (return to your highest point) / standard / Hardcore (rising lava).

*Decided 2026-09-22:* **two** modes, Kolay and Normal — no İmkânsız — and the GDD cap holds in both: a
failure never costs more than one segment. Not built yet (DA-47). The modes change **only these knobs**,
and never the level geometry — one set of levels, two cuts:

| Knob | Kolay | Normal |
|---|---|---|
| Checkpoints | every segment + mid-segment | every segment |
| Chase speed | `Chase_Standart` (4 m/s) | as authored |
| Door type | `Kilitli` | as authored |
| SwapGate density | fewer | as authored |
| Cross-machine timing window | ≥ 1 s | ≥ 1 s |

*(The stress grace window is not built. Any window two machines must agree on is **≥ 1 s** in every mode —
≈3× the ~300 ms round trip of the 150 ms-each-way test preset, 2026-09-22.)* Player-facing mode names are
Turkish per the repo convention; identifiers stay English.

Ship `Kolay` even though nobody on the team will play it. It is not for the team. It is what lets the
group where one person is bad at platformers still finish the game, and that group is most of the market.

## Beat construction

A **beat** is one authored moment with a clip in it. Four phases, and skipping any of them costs you the
clip:

1. **Setup (2–4 s)** — the players see the problem before they are in it. The camera must contain the
   hazard and the players in the same frame. A beat the players discover by dying is not a beat, it is an
   ambush, and ambushes read as unfair.
2. **Commitment** — the point where backing out is no longer free. This is what makes the moment tense
   rather than merely difficult.
3. **Resolution (1–3 s)** — success or failure, and it must be *loud*. The shatter, the catch, the
   near-miss.
4. **Consequence** — the tier-2 return (0.7 s collapse + teleport), or the exhale. Do not cut immediately
   into the next beat; the reaction is the content, and reactions need 2–3 s of quiet to happen in
   *(starting value)* — after an exhale or a tier-1 rescue, not added to the tier-2 return.

### Beat archetypes for a carried object

Six that work horizontally. Each one is a different way of making the shared object the problem.

| Archetype | The problem | Clip |
|---|---|---|
| **The doorway** | The object is wider than the gap; someone has to rotate it | Clipping a corner at the last centimetre |
| **The low beam** | Everyone must crouch in sync, and the object must stay level | One player stands up early |
| **The split path** | Carriers are forced onto different heights or lanes | The object tilts past its limit |
| **The handoff** | One carrier must let go and re-grab on the other side | Nobody grabs; the object falls |
| **The swinging hazard** | A timed obstacle crosses the carry path | Timing it for three people at once |
| **The narrow ledge** | The carry path is narrower than the group's natural spacing | A shove, deliberate or not |

**The handoff is the highest-value archetype** and should appear in every level. It is the only one that
creates a moment where a player must trust another player to act, which is where both the best
cooperation clips and the best betrayal clips come from.

### Clip density target

**One clip-worthy moment every 60–90 seconds of play** *(starting value)*. Denser and nothing lands;
sparser and a 20-minute stream has three usable clips, which is not enough to spread.

Measure it honestly: record a playtest, count the moments where someone reacted audibly, divide by
minutes. That number is the level's real score and it is more predictive than any difficulty metric.

## Camera and readability

`CameraFollow` frames the whole group: height 2.5, `leadBias` 0.7, distance 24–40 m with
`framingMargin` 3, `smoothTimeX` 0.14, `smoothTimeY` 0.26, 1.6 m of look-ahead. The 24→40 m dolly is a
safety net — the rules below still apply.

What co-op needs:

- **Containment over following.** The frame must hold every player *and* the carried object. A player
  off-screen cannot be blamed, and unattributable failure is the thing this whole document is trying to
  avoid.
- **A hard separation cap enforced by design, not by the camera.** Decide the maximum player spread the
  camera will show — **18 m** at the current z-offset is a reasonable start *(starting value)* — and then
  make sure no level geometry ever requires a wider spread. Do not solve level-design problems by zooming
  out; a zoomed-out 2.5D frame loses the depth cue that makes the lane readable.
- **Never let the object leave frame.** If a carrier is off-screen you have lost attribution; if the
  *object* is off-screen you have lost the loss engine itself.
- **The break frame is sacred.** Whatever else the camera is doing, the moment of failure must be
  contained and unobstructed. Effects that occlude the thing they announce are already on the
  anti-pattern list in the `game-feel` skill; at the break, that rule is absolute.
- **2.5D readability.** Keep hazards and the carry path on the same `LevelLayer` z. The palette's layer
  system (`LevelPalette.Layers`, each with its own `z` and tint) is the tool for this: background layers
  carry theme, the gameplay layer carries every object that can kill you. A hazard that lives visually
  between layers is a bug report waiting to happen.

## Biome progression

Chained Together runs hell → purgatory → heaven, each visually distinct, difficulty rising with altitude.
The visual contrast between start and end *is* the progress bar, which matters because a viewer joining a
stream halfway through can instantly see how far the group has come.

Horizontal loses the altitude readout, so the biome has to carry more of that load:

- **One new coupling rule per biome, and only one.** Biome 2 introduces the handoff. Biome 3 introduces
  the split path. Never two at once — that breaks the single-machine test.
- **Silhouette and palette must differ hard between biomes.** A thumbnail from biome 1 and a thumbnail
  from biome 4 should be unmistakable. This is a marketing requirement as much as a design one; it is how
  a viewer measures progress and how a clip announces which part of the game it came from.
- **The rule stays flat inside a biome; the load is a rising sawtooth.** Players master one coupling rule
  before the next arrives, but the load on them climbs to a peak at the end of each segment and drops at the
  checkpoint, and each segment opens below the last peak and above the last opening (`difficulty-rhythm.md`
  DR01, DR03, DR14). A biome is a Bölüm for this purpose.
- **The last biome is the one in the trailer.** Build it first if you can; it is the asset the marketing
  plan depends on (Mixtrol's `go-to-market.md`, not shipped; trailer and store-art planning is
  `gamekit:launch-review`).

## Feeding the level editor

The Level Editor (`Mixtrol/Level Editor`, `docs/level-editor.md`) is where this playbook becomes real: a
1.25 m grid, every mechanic in a palette, a schematic over the Scene view, box fill, links, jump reach. Three
things belong in it:

1. **Every beat archetype as a stamp.** *Done (MIX-250):* a selection of pieces saves as a stamp with its links,
   and the kit recipes (pulley, safety net, two-plate door, delivery door, bell lift, throw wall, metronome stair)
   come built. A handoff or a lab built once is one click after that.
2. **Checkpoint and segment markers as first-class entries.** *Done (MIX-248):* checkpoints are in the palette,
   and the segment strip shows each checkpoint-to-checkpoint stretch against 40–80 cells while authoring, with
   its clip sentence and a measured clean run in the notes.
3. **A measurable spread.** *Still open.* Anything that shows, at author time, the widest player separation the
   geometry forces. That is the one number that silently breaks co-op levels and it is invisible in a static
   scene view. The jump-reach arcs are the nearest thing today: they show what a gap allows solo and with the
   partner.

Any change to the editor window or palette is a scene/asset change — see the `unity-editor-cli` skill, and
do not hand-edit the `.asset` YAML while the Editor is running.

## Anti-patterns

| Anti-pattern | Threshold |
|---|---|
| Fade-to-black respawn | Any fade on the tier-2 return (it stays the 0.7 s collapse + teleport, 2026-09-22) |
| Ambush beat | A hazard first seen by dying to it |
| Two loss engines at once | The cauldron and a chase in the same beat or segment (the swap underneath is the floor, not an engine) |
| Corridor longer than a beat | More than ~15 s *(starting value)* of travel with nothing authored in it |
| Segment over 90 s | Players stop retrying |
| Rule change inside a biome | The rule changes before it has been mastered |
| Flat load | Three or more consecutive segments at the same peak, or no valley after a peak (DR01, DR04) |
| Solving spread with zoom | Camera pulled back to fit geometry that should have been narrower |
| Occluded break | The failure frame hidden by its own effect |
| A beat that works at 2 but not at 4 players | Untested at the maximum player count |
| Grace window below 240 ms | Below the reaction floor; a window two machines must agree on below 1 s |

## What to verify in Play Mode

1. Record a full playtest with a group that has never played. Count audible reactions per minute against
   the 60–90 s clip-density target.
2. Fail the same segment four times on purpose. Does the group still want to go again?
3. Watch a recording with the sound off. Can you tell what was lost and whose fault it was, every time?
4. Play every segment at 2 players and at 4. The beats that only work at one count are the ones to fix.
5. Check that no geometry forces a player spread wider than the camera's containment cap.
