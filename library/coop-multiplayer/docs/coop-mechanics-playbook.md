# Co-op mechanics playbook

What `reference-teardowns.md` found, turned into decisions for Mixtrol. Read the teardowns first; this
document assumes them.

> **Status 2026-09-22.** The GDD has since made the **control swap** the primary coupling; the carried
> object below is the secondary loss engine it plays out in (the cauldron). Networking is built (FishNet).
> Failure is two-tiered. Where this document disagrees with the GDD, the GDD wins — see the precedence
> rule in `docs/design-corpus/README.md`. The reasoning below is kept because it is still why the
> cauldron exists.
>
> What is **not built**, whatever the body below says: the time-based stress grace window (240 ms floor,
> per difficulty) — stress is a pure function of carrier separation (`CarriedObjectSolver.StressAt`);
> `Cracked` fires when separation passes `stressSpan` and spilling starts the same step. The cauldron
> cannot break ("Kırılır" is future per the GDD; `CarriedObjectState` has `Cracked`, `Caught` and
> `Spilling`, no `Broke` edge). There is no soft tether and no per-character carry force: `MovementState`
> holds a `CarryLoad` speed multiplier and a facing lock.

Mixtrol is becoming a **2–4 player horizontal 2.5D co-op platformer**. That combination is rare, and the
reason it is rare is the first thing this document has to deal with.

## The problem the horizontal axis creates

Every breakout in this genre runs on the same engine: **gravity as a loss machine**. A fall is instant,
it is visible at thumbnail size, it is measurable ("we lost twenty minutes"), and it is attributable —
everyone watching knows whose hand slipped. Chained Together, PEAK, Getting Over It, Jump King,
A Difficult Game About Climbing, Only Up: all vertical, all running on that same engine.

A horizontal platformer does not get that for free. Moving right is not a countdown you can lose; a pit
is a binary death, not a fall from a height the camera can show. If you build horizontally and change
nothing else, you get a competent platformer that produces no clips — and in this genre, a game that
produces no clips does not sell, because the clip *is* the marketing channel.

Two games that did break out without leaning on a long fall replaced gravity with the same substitute —
Pico Park on a horizontal axis, Carry The Glass as the level-based carried-object proof (its levels,
Skyscraper and Lighthouse, are vertical-ish):

> **Carry The Glass** gives two players one fragile pane to hold between them.
> **Pico Park** makes each player physically necessary to the others.

Both replaced "height you can fall from" with **shared fragile state that the players carry**.

### The doctrine

**On a horizontal axis, the players must be carrying something they can break.** Not a metaphor —
a literal object or a literal shared value that (a) is visible in frame at all times, (b) degrades or
dies from ordinary mistakes, and (c) points at whoever caused it.

If Mixtrol ships a horizontal co-op platformer without that, it has removed its own loss engine and
kept only the genre's difficulty. That is the worst half of the trade.

## Coupling taxonomy

Four ways to bind players together. Pick one as primary. Do not stack three.

### 1. Hard tether (Chained Together)

A simulated chain or rope with a length limit. One player's momentum is transmitted into everyone else's
body.

- **Clip it produces:** the yank. Player A falls, players B, C, D are dragged off the ledge behind them.
- **Scales to 4?** Yes, and gets funnier — a 4-chain is a whip.
- **Netcode cost:** high. A constraint solver coupling four bodies has to be authoritative somewhere, and
  it is the single most latency-sensitive thing you can build.
- **Mixtrol cost:** `MovementSolver` currently solves one character in isolation and returns a
  displacement. A hard tether means the four characters can no longer be stepped independently — you
  need a constraint pass after the per-character step. This is a real architectural change, not an
  addition.
- **Horizontal problem:** on a flat run the tether mostly does nothing. It only bites near a height
  change. Horizontal + hard tether means every interesting beat has to be a vertical beat anyway, which
  is the vertical game with extra steps.

### 2. Carried fragile object (Carry The Glass) — **recommended**

One rigid object held by two or more players. It has health or is instantly breakable. It is the
objective and the fail state at the same time.

- **Clip it produces:** the break. Instant, loud, legible with the sound off, and attributable.
- **Scales to 4?** Yes, with design work — either one big object with four handles, or two objects across
  two pairs (which creates a second social layer: the pairs racing or blaming each other). *Two objects:
  rejected 2026-09-22 (GDD: one multi-handle object per level, handle count = player count).*
- **Netcode cost:** moderate. One shared rigid body with N attachment points is far cheaper to make
  authoritative than N coupled characters.
- **Mixtrol cost:** the lowest of the four. Characters keep stepping independently through the existing
  `MovementSolver.Step`; the object is a separate simulated body that reads player positions as
  constraints and writes back a carry force. `MovementState` gains one field and the solver gains one
  term.
- **Horizontal fit:** excellent, and it is the only option in this list that is *better* horizontal than
  vertical. A pane of glass carried sideways through a doorway, under a low beam, past a swinging hazard
  is a stronger scene than the same pane carried up a ladder.

### 3. Mutual dependency (Pico Park)

No physical link. The level is built so that one player physically cannot pass without another — stand on
a head, hold a switch, form a bridge.

- **Clip it produces:** the betrayal. The player holding the switch lets go.
- **Scales to 4?** Extremely well — it is the only coupling here that gets *richer* with more players
  rather than just noisier.
- **Netcode cost:** low. Players stay independent; only the world state is shared.
- **Mixtrol cost:** low in code, high in level design. The coupling lives entirely in the level, which
  means every single room has to be authored to require it. There is no emergent fallback.
- **Horizontal fit:** proven — this is exactly Pico Park.

### 4. Shared resource or counter

One pool everyone spends from: a shared health bar, a shared lives counter, a fuse burning down, a shared
stamina.

- **Clip it produces:** the argument. Nobody is on screen failing; someone is off screen wasting.
- **Scales to 4?** Yes, but weakly — the loss is a number changing, not a thing happening.
- **Netcode cost:** trivial.
- **Mixtrol cost:** trivial.
- **Verdict:** **never a primary coupling.** It fails the attribution test — a bar going down does not
  point at anyone, and it is not legible with the sound off. Use it as a *secondary* pressure layer on
  top of 2 or 3, the way PEAK layers stamina on top of climbing.

## The recommendation for Mixtrol

**Primary: a carried fragile object (2). Secondary: mutual dependency in level design (3). A soft tether
at most — never a hard one.**

Reasons, in order of weight:

1. It is the only coupling that is *stronger* horizontally than vertically, which is the axis already
   chosen.
2. It is the cheapest against the existing architecture. `MovementSolver` keeps its one-character-at-a-
   time contract; nothing about the Core/Game assembly split has to move.
3. It has the best netcode-cost-to-comedy ratio of the physical couplings (networking has since been
   built; see the constraint note below).
4. It carries its own tutorial. Nobody needs to be told what a pane of glass is for.

**What "soft tether" means here:** a maximum separation distance enforced by a gentle pull rather than a
rigid constraint — if two players holding the object drift too far apart, they are eased back rather than
snapped. This gives you the tether's framing benefit (the camera can always contain everyone) without the
constraint solver or the latency sensitivity.

### Rejected, and why

- **Hard chain.** Best-in-class comedy, but it is Chained Together's identity, it fights the horizontal
  axis, and it is the most expensive thing in this document to network. Building a weaker chain game is
  worse than building a different game.
- **Shared resource as primary.** Fails the attribution test. See above.
- **Asymmetric roles** (one player drives, one player builds). Not in the teardowns for a reason: it
  halves the number of people who can pick up the controller and immediately understand the joke, and it
  makes the clip harder to read.

## The five tests every mechanic has to pass

Apply these to any new mechanic before it is built. They come straight out of the teardowns.

1. **The muted-clip test.** Watch it with the sound off. Within one second, can a stranger tell what just
   happened and roughly whose fault it was? If not, it will not travel.
2. **The single-machine test.** At the moment of failure, is exactly one system demanding the player's
   attention? Chained Together's developers explicitly resisted complexity that would obscure the
   fundamental comedy. Two competing systems at the moment of failure means neither reads.
3. **The attribution test.** Does the failure point at a player? A hazard that kills everyone equally is
   an obstacle. A hazard that kills everyone *because of one player* is content.
4. **The sabotage test.** Can a player choose to do this to their friends on purpose? Pico Park's real
   engine is that griefing is possible. Accidental chaos is funny once per level; deliberate betrayal is
   funny forever, because the players author it and it never repeats.
5. **The zero-explanation test.** Can a new player understand the rule from one screenshot? If the
   mechanic needs a tutorial, a streamer has to explain it, and explanation is dead air.

If a mechanic fails 1, 2 or 3, do not build it. If it fails 4 or 5, build it but expect it to carry less
weight than you think.

## Forgiveness is given to the connection, not to the individual

This is the single most important tuning shift going from solo to co-op, and it is easy to get backwards.

In solo Mixtrol, coyote time and the jump buffer exist to forgive *the player's input* — you pressed jump
two frames after leaving the ledge, and the game pretends you did not. Current values in
`Assets/Mixtrol/Core/Data/PlayerMovement.asset`: coyote 0.12 s, jump buffer 0.12 s (see the `game-feel`
skill for the bands these sit in).

In co-op, individual forgiveness has a perverse effect: it makes each player harder to blame, which
softens attribution, which weakens the clip. Meanwhile the actual source of unfairness has moved. It is
no longer "my input was two frames late" — it is "my partner moved while I was mid-jump, so the object I
was holding was somewhere else than where I committed to."

So:

- **Keep individual forgiveness where it is.** Do not raise coyote time or the buffer to compensate for
  co-op chaos. 0.12 / 0.12 are correct values and they are not the problem.
- **Add forgiveness to the coupling instead.** The carried object should have a grace window before it
  breaks — a stress state that is visible (it cracks, it creaks, it tilts) and lasts long enough for a
  partner to react. That window is the co-op equivalent of coyote time, and it is where the difficulty
  dial should live.
- **The grace window must be reactable, not just forgiving.** The human perceive-decide-act loop is about
  **240 ms**. A stress warning shorter than that is not a warning, it is a slideshow of the failure. Give
  the "about to break" state a floor of 240 ms, and tune upward from there per difficulty mode.
  *Decided 2026-09-22:* any window two machines must agree on is **≥ 1 s** (≈3× the ~300 ms test round
  trip), and the difficulty knobs are checkpoints, chase speed, door type and SwapGate density
  (`level-design-playbook.md`), not this window.
- **Never forgive silently.** A save that the players do not notice teaches them nothing and produces no
  reaction. Every catch has to be visible and audible — a near-miss is a clip too.

## Fitting this into the Mixtrol architecture

The existing split is the constraint that shapes the implementation. `Mixtrol.Core` holds value types and
static step functions taking `dt`; `Mixtrol.Game` is the Unity glue. `MovementSolver.Step` is:

```
public static Vector2 Step(ref MovementState state, in MovementInput input,
                           in MovementTuning tuning, bool grounded, float dt)
```

It solves one character, in isolation, and returns a displacement. Collision and the ground test belong
to the caller — which, as the file's own comment says, is what lets the same code run server-side once
multiplayer lands. That decision is now cashing in.

**Where the coupling state lives.** A new `Mixtrol.Core` type — a `CarriedObjectState` value type plus a
`CarriedObjectSolver.Step` static function, mirroring the movement pair exactly. It takes the carrier
positions as inputs and returns the object's displacement plus a per-carrier carry force. It must not hold
a reference to `MovementState`; it takes positions and returns forces, like every other Core function.

**What changes in movement.** Ideally: one field on `MovementState` for the carry force being applied to
this character, and one term in `MovementSolver.Step` that folds it in. Nothing else. If the design starts
requiring the solver to know about *other characters*, that is the signal you have drifted from coupling 2
toward coupling 1, and the cost curve changes underneath you.

**Order of operations per step.** Step each character independently (unchanged), then step the carried
object with all carrier positions, then apply carry forces into the next character step. One frame of lag
between the object and the characters is fine and is in fact what makes the object feel heavy.

**The edge-flag contract stays.** `MovementSolver.Step` resets `Landed`, `JumpTriggered`,
`AirJumpTriggered` and `DashTriggered` at the top of every step, and those flags are the only sanctioned
channel from simulation to presentation. The carried object gets the same treatment: a `Cracked`,
`Broke`, `Caught` set of one-step edge flags, reset at the top of its own step, and the Feel layer reads
those. Do not invent a second shape for this problem — `game-feel` and `feel-authoring` already cover what
happens on the presentation side.

**Play Mode caveat.** Domain and scene reload are both off (`m_EnterPlayModeOptions: 3`). Any mutable
static introduced for session or lobby state needs a
`[RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.SubsystemRegistration)]` reset, or it survives
into the next Play session and only breaks on the second run.

## Two repo constraints this decision collides with

Flagging both rather than quietly working around them. Neither is changed by this document.

**1. Networking is no longer a later goal.** *(Resolved: FishNet over Unity Relay was added 2026-09-17;
the cauldron is host-authoritative — the host runs `CarriedObjectSolver`, clients request grab and
release, the pose rides a server-authoritative `NetworkTransform`.)* The point stands for the next
coupling: the authority model decides the solver's shape, so settle it before building.

**2. The architecture is already right for this, and that is not an accident.** Value types, static step
functions, `dt` as a parameter, collision resolution pushed to the caller, no `Time` access, no scene
APIs. That is a deterministic simulation core — exactly the shape a rollback or server-authoritative
netcode needs. This is the project's largest existing asset going into a co-op pivot and it should not be
compromised to make the coupling easier. If a proposed mechanic requires `MovementSolver` to touch a
`GameObject`, the mechanic is wrong, not the architecture.

## Anti-patterns

| Anti-pattern | Threshold that defines it |
|---|---|
| Two coupling types active at once | Beyond the primary (the swap), more than one other coupling load-bearing in the same beat or segment (decided 2026-09-22) |
| Unattributable failure | A death or break that no viewer can trace to a player within 1 second |
| Silent save | Any forgiveness the players do not see or hear |
| Grace window under 240 ms | Below the human perceive-decide-act loop; it is not a warning |
| Sabotage designed out | No mechanic in the game lets a player deliberately ruin a teammate's run |
| A mechanic that needs a tutorial | Cannot be understood from one screenshot |
| Coupling state in `Mixtrol.Game` | Simulation logic in a MonoBehaviour; it will not survive networking |
| Raising coyote/buffer to fix co-op chaos | Individual forgiveness tuned above 0.15 s to compensate for a coupling problem |

## Sources

See `reference-teardowns.md` for the full source list. The claims specific to this document:

- Chained Together's developers on resisting complexity that obscures the comedy —
  [indiegame.com](https://indiegame.com/en/archives/28817)
- Carry The Glass's carried-object design, physics on every body part, three checkpoint modes —
  [Steam](https://store.steampowered.com/app/3263320/Carry_The_Glass/)
- Pico Park's deliberate-prank affordance —
  [AUTOMATON WEST](https://automaton-media.com/en/news/20211011-3784/)
- PEAK's stamina-and-afflictions layer over free-form climbing —
  [Game Developer](https://www.gamedeveloper.com/production/how-co-op-climbing-hit-peak-achieved-2-million-sales-for-less-than-200-000-)
- The 240 ms perceive-decide-act budget — `~/.claude/skills/game-feel/references/sources.md`
