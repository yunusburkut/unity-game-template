---
name: level-beat-review
description: Laying out or critiquing a __GAME__ level, a level pack or a level order before it is built, or reviewing a built one ("bölümü yorumla", "level eleştir", "zorluk sırası", "zorluk eğrisi", "nefes", "çok mu uzun", "sıkıcı mı") — difficulty rhythm (the sawtooth, valleys after peaks, where new mechanics and checkpoints sit, trolls), segment and level length, checkpoint placement, failure tiers and how much a failure costs, the teaching arc, beat construction, difficulty modes, replay levers, camera and readability, and world pacing. Use when designing a level, segment or level pack, when asked "is this level too long", "where do checkpoints go", "how much should a failure cost", "is this section boring", "how do we make it harder", "why would anyone replay this", when playtesters quit or stopped reacting, when adding a hazard or obstacle, or before building any level geometry so the beats are chosen rather than discovered.
---

# Reviewing a __GAME__ level before it exists

`DESIGN.md` holds the game's genre, its mechanics and any decisions that override the starting values here. The rules
with their evidence and the full critique procedure are in `references/difficulty-rhythm.md` (DR01–DR28).

**Sourced** numbers are cited. **Starting values** are marked *(start)*: tune them in Play Mode and write the result
into `DESIGN.md`.

## Map the units to the genre first

Every rule below talks about beats, segments, acts and worlds. Fix what those are for this game, once, in `DESIGN.md`:

| Unit | Platformer / action | Level-based puzzle (mobile packs) | Run-based (roguelike, endless) |
|---|---|---|---|
| Beat | One authored obstacle or encounter | One decision or move that matters | One encounter |
| Segment (one tooth) | Checkpoint to checkpoint | One level | One room |
| Act | 3–5 segments *(start)* | A pack of ~5–10 levels *(start)* | A floor or biome |
| World | A chapter or biome | A world or theme | A run |

## Rule zero

**Design the moment, then build the level around it.** Before anything is placed, write one sentence for the moment
this segment produces: what the player will remember or want to show. If it cannot be written, this is filler. Filler
is allowed as rest between beats; it must be deliberate and short.

## The numbers

| | Target | Note |
|---|---|---|
| Segment, clean run | 45–90 s *(start)* | Under 45 s a loss does not sting; over 90 s players stop retrying |
| Level-based puzzle level | 30 s–3 min *(start)* | Mobile sessions are short; one level must fit in a bus stop |
| Beats per segment | 3–5 *(start)* | Under 3 is filler; over 5 nothing lands |
| A memorable moment | one per 60–90 s *(start)* | The level's real score |
| Recoverable failure | next decision within **3–8 s** | Undo, a catch, a short fall: fixed in place |
| Consequence beat | 2–3 s of quiet *(start)* | After a rescue or a cleared beat: the reaction is the content |
| Filler | ≤ ~15 s *(start)* | Longer is dead air |
| Reaction floor for any window | **240 ms** (sourced) | Human perceive-decide-act loop |
| Telegraph for a hazard | > 240 ms | Shorter is not reactable |

**The governing rule: a player must be able to lose the same segment four times without quitting.** If they quit on
the third loss, the segment is too long or the failure was unfair, and unfair almost always means *unreadable*, not
hard.

## Failure tiers

- **Tier 1, recovered in place.** Geometry or rules do most of the work: a lower ledge instead of a pit, an undo, a
  catch window, a cheap restart of only the last move. Every beat names its tier-1 outcome.
- **Tier 2, terminal.** Back to the checkpoint or the level start. Reserve it for the beat's real failure, not every
  slip.
- **One loss engine per beat.** A timer, a chase, a fall, limited moves: at most one is load-bearing in a beat. Two at
  once is the commonest unfair beat.

## Teaching arc

One new idea per segment, in this order:

1. **Safe teach**: the mechanic alone, nothing that can fail you.
2. **Develop**: a harder form of it.
3. **Twist**: a known mechanic used in a way the teach did not show (the peak).
4. **Combination**: two learned mechanics, both rules intact.
5. **Recovery**: mistakes route into tier-1 rescues instead of restarts.
6. **Mastery finale**: everything learned, under pressure.

**Never introduce a mechanic for the first time under a timer, a chase or inside a combination.**

## Beat construction

1. **Setup (2–4 s)**: the problem and the player in the same frame. A hazard first discovered by failing is an ambush.
2. **Commitment**: where backing out stops being free.
3. **Resolution (1–3 s)**: loud: the fall, the catch, the near miss, the solve.
4. **Consequence**: the tier-1 recovery or the tier-2 return, then the exhale.

Write every beat as a row of this table before building it:

| Moment sentence | New idea? | Tier-1 outcome (s) | Tier-2 outcome | Loss engine | Visible from before? | Dominant strategy risk |
|---|---|---|---|---|---|---|

## Escalation without new rules

Harder means turning an existing knob, never a new button or a new screen: compress time, add distance, make a static
element expire, require two actions in sequence or at once, do the same action while carrying a constraint, remove a
safety. Each new knob in the game's configs is an escalation operator; list them in `DESIGN.md`.

## Difficulty is a dial, not a level rewrite

Modes change only knobs (checkpoint density, timer length, hazard speed, hints), never geometry or beat order, and never
adapt at runtime without the user's decision. A failure never costs more than one segment in any mode. An easy mode is
what lets the weakest player in a household finish, and on mobile that is most of the market.

## Replay levers

Raise these with the user; do not decide them here.

- **Randomise within bounds**: the same geometry, a different deal or start.
- **Escalating retry**: repeated failures vary the cosmetic reaction, never the mechanics (`game-feel`).
- **Readable randomness**: any random pick shows anticipation and a reveal.
- **One-shot traps die**: a trick that works once is spent; keep at most one per level.
- **Dominant strategy**: if a safe routine appears by the third attempt, the beat needs an escalation.
- **Optional harder lines**: stars, collectibles or par times let strong players raise their own difficulty while the
  critical path stays at the ceiling.

## Camera and readability

- **Containment, not following**: everything the beat asks about is in frame, including on the narrowest phone aspect
  the game supports (`platform-targets`).
- **The failure frame is sacred**: contained and unobstructed by its own effects.
- **Thumbs and notches**: on a phone, the lower corners are under thumbs; nothing the player must read sits there.

## Difficulty rhythm (`references/difficulty-rhythm.md`, DR01–DR28)

**The shape: a rising sawtooth at every scale** (DR01). A segment is one tooth: `teach → develop → twist (the peak,
where tier 2 lives) → lap (tier 1 only) → checkpoint` (DR03). The next unit opens below the last peak and above the last
opening.

| Ask | Rule |
|---|---|
| What comes after a peak? | A valley that asks a *different* question (DR04); the checkpoint is the first safe ground after it, and nothing after the peak can cost the peak (DR08); replay to the peak ≤ 60 s *(start)* (DR09) |
| Where does a new mechanic go? | At a valley, alone; never under pressure or inside a combination; combine only what was met alone; retire a mechanic before it wears out (DR05–DR07) |
| How hard may it get? | Critical-path ceiling C4 (DR11); peak steps ≤ +1 and a smooth start (DR12); showpieces rare, no two peaks in a row asking the same question (DR13) |
| Acts and worlds | A valley segment between act peaks (DR14); a world opens with a hook below the last finale (DR15); set pieces fixed, taught moves only, low threat after (DR17); the finale (DR18); the game ratchets (DR19) |
| Trolls | Visible, cheap, identical on retry (DR22); a troll is a rationed twist (DR21); at most one per two segments, none in the first two or the finale (DR23) |
| Multiplayer | A talk window before every peak (DR24); pace for the most stressed player, every role wins a beat (DR25); blame stays a joke (DR26); partner sabotage windows (DR27); rate at the minimum and maximum player count (DR28) |

## Critiquing a level ("bölümü yorumla")

Use when the user shows a level, a level pack or a level order and asks for a critique. The scales, columns and Turkish
report template are `references/difficulty-rhythm.md` §C.

1. **Gather**: the level notes in `DESIGN.md`, moment sentences, clean times, and parameters read from the scene or
   level data through `unity-editor-cli` (read-only). Say which values are documented (D), estimated (E) or measured
   (M).
2. **Map**: one row per beat: role, question, challenge C1–C5, stakes T0–T3, pressure, novelty, window, visible,
   relief, checkpoint. Never invent a number; an unmeasured C comes from the proxy rule, tagged E.
3. **Curve**: each segment's peak as `▁▂▃▄▅`, `‖` after the tutorial, `|` at act edges.
4. **Check** every DR against the map.
5. **Report in Turkish**: the state (*geçici* or *ölçülmüş*), the curve, at most seven findings by severity
   (*Engelleyici, Büyük, Küçük, Ayar, Karar, Ölç*), each with its evidence tag and the measurement that would withdraw
   it. No single numeric score. The user decides every **Karar**.

## Anti-patterns

| Anti-pattern | Threshold |
|---|---|
| Ambush beat | A hazard first seen by failing to it |
| Segment loss for a slip | A tier-1 mistake sends the player back |
| Two loss engines at once | A timer and a second loss engine load-bearing in the same beat |
| Required item losable | Something the level needs can leave play for good |
| Filler over ~15 s | Travel or waiting with nothing authored in it |
| Segment over 90 s | Players stop retrying |
| Occluded failure | The failure frame hidden by its own effect |
| Flat load | Three or more consecutive segments at the same peak, or no valley after a peak (DR01, DR04) |
| Peak then peak | Two C4+ beats with no valley between, or two peaks asking the same question (DR04, DR13) |
| New mechanic at a peak | First contact at C ≥ 3, under pressure, or inside a combination (DR05) |
| Troll on a peak | A troll on a teach beat, a C ≥ 4 beat, after a checkpoint or on the finale (DR21) |
| Mobile wall | A level pack whose difficulty jumps more than one step between consecutive levels (DR12) |

### If the game is multiplayer

| Anti-pattern | Threshold |
|---|---|
| Solo-solvable beat | One player can do what the beat says needs two |
| Stall without a counter | One player can hold the group indefinitely |
| Idle partner | One player waits > ~10 s with nothing to do *(start)* |
| Works at 2, breaks at 4 | A beat whose rule needs exactly two players |
| Unattributable failure | A stranger cannot name the cause within 1 s |
| Frame-tight online window | A window two machines must agree on under 1 s |

## Verify in Play Mode

1. Record someone who has never played; count audible reactions per minute against one per 60–90 s.
2. Time mistake → next decision; tier-1 must land in 3–8 s.
3. Count tier-1 recoveries against tier-2 failures per segment: a segment with no recoveries has no tier 1.
4. Fail the same segment four times on purpose: do they still want to go again? Did a safe routine appear by the third
   try?
5. Watch it muted, and on a phone at the narrowest aspect: what was lost and why, every time?
