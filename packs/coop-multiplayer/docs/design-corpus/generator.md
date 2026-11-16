# Idea generator — operators, objects, pools, rooms, drills

Catalog of `source/02_mechanic_puzzle_idea_generator_expanded.pdf` (pp. 1–61; seeds pp. 3–59), paraphrased and mapped onto Mixtrol.
Cite by ID (`OP09`, `OB45`, `RA08`); IDs are stable — never renumber, append instead.
Mixtrol status (the marks in the Mixtrol columns): ✅ built (device) · 🟡 partial (what is missing) · 🧩 cheap with existing systems, no new key · 🆕 needs a new system · ⛔ conflicts with a recorded decision · — not applicable to a horizontal 2.5D lane.
In __GAME__ these marks and the class names beside them describe Mixtrol, never this game: rate a card's production cost and devices reused against __GAME__'s own systems (DESIGN.md, the code); `docs/design-audit.md` holds this game's own status once its first design audit fills it.

## 1. How a seed is built

The grammar, in order. Skip a step and the seed is a prop, not a mechanic.

1. **Object** — a familiar thing with a strong affordance (OB).
2. **Dependency** — one P pattern. Answer "why is a second player required?" in one line.
3. **Operator** — one OP that changes ownership, information, timing, cost or space.
4. **Sabotage** — one legal troll, using keys the player already has.
5. **Failure chain** — 3–5 causal steps (FC), each visible on screen.
6. **Recovery** — fail-forward or rescue instead of a hard reset (RQ, RC). In Mixtrol this is **tier 1**: recovered
   in place, next decision within 3–8 s. Tier 2 (shared death, one segment back) stays for terminal failure.
7. **Escalation** — combine learned systems; never add a button (EO, DC13).
8. **Clip** — one 5–10 s scenario that tells a story on its own (DC06).

**The seed formula:** `OB × one P × one OP → one CQ + one RQ + a clip line`.

- The PDF's 240 seeds (pp. 3–59) are this formula filled mechanically: 60 objects × 4 seeds, each pairing a P with
  an OP, with CQ and RQ drawn from the two 10-entry pools (§4, each entry used exactly 24 times). **They are not transcribed**
  — they hold nothing the tables below do not. Generate fresh seeds with the formula; `mechanic-forge` does it.
- Every seed's clip is one of four stock shapes, 60 seeds each: (a) A commits, B alters the shared state at the
  last safe moment, C's rescue sets off the consequence and the group finds the recovery in the same beat; (b) B
  calls "safe", A commits, the operator flips it, D's fix makes progress by accident before B can be blamed; (c) two
  players run different plans through one rule, collide, and the failure becomes a short rescue with a readable
  cause; (d) a deliberate troll rebounds on the troll and the victim becomes the accidental hero (CS07, CS20).
- Seeds assume four players A–D. Rewrite every one as "en az iki / herkes" (GDD). Each seed's closing rule — reuse
  move/jump/grab before inventing an input — is Mixtrol's one-key-per-action rule, not a suggestion.

**Example 1 — Closing door.** OB45 Pressure Plate × P27 Sacrifice Window × OP15 Expire → CQ04 + RQ02.
The holder stands on a plate wired to `Door_Zamanli` (stays open 3 s after release; the asset exists, only Gym uses it). The
runner is through; the holder now has 3 s to cross, and the hurdle at the sill needs the Jump the runner holds.
Clip: 1P sprints for the door, 2P presses Space a beat late, 1P bounces off the sill as it shuts — 2P walks back to a
far-side plate and reopens it. Tier 1: nobody dies, the cost is ten seconds and the argument.

**Example 2 — Second across.** OB44 Trapdoor × P53 Delayed Consequence × OP09 Swap → CQ09 + RQ01.
A `CrumblingFloor` strip arms under the first crosser and drops under the second. The strip sits over a lower lane
that climbs back up ahead (layout only, 🧩), not a pit. The second crosser needs their Jump, which the first holds.
Clip: 1P runs over yelling "now!", the Space-jump lands on the wrong tile, 2P drops into the lower lane — and pops out
at the exit before 1P. The drop is not a death, so no blame label fires; a cause tag on 1P's Space is 🆕 (FP11).

## 2. OP — Mutation operators (45)

Mutate an existing affordance before inventing a control. The operator changes relationships; the object stays itself.

| ID | Operator | Changes (≤12 words) | Mixtrol example or — |
|---|---|---|---|
| OP01 | Reverse | Flips direction, ownership, polarity, safety or meaning | 🧩 inverted plate: the door shuts while the plate is held (one new DoorSolver flag) |
| OP02 | Split | Spreads one function across players, places or phases | ✅ move swap — your Jump on the partner's Space (ControlSwap) |
| OP03 | Combine | Needs two unrelated states true at the same time | ✅ Door `requireAll` over two plates (B2 S1, S5) |
| OP04 | Remove | Takes a familiar ability away for a while | ✅ a handed-away move; carrying the cauldron blocks jump and dash |
| OP05 | Delay | Puts time between the action and its result | 🟡 CrumblingFloor 0.6 s crack; a 2–6 s delay is config, and network-safe |
| OP06 | Relocate | Moves the effect, tool, risk or control somewhere else | ✅ PressurePlate → distant Door (P18) |
| OP07 | Share | One state or resource hits several players | ✅ shared death (one RespawnState); cauldron fill |
| OP08 | Steal | A legal interaction takes someone's resource or control | 🧩 bump-to-take the held move (SeparateFromPartners overlap + lockout) |
| OP09 | Swap | Exchanges roles, places, controls, states or targets | ✅ ControlSwap table, host-owned |
| OP10 | Hide | One relevant fact becomes local or briefly invisible | ✅ ColorTunnel interior visible to its owner only |
| OP11 | Lie | A cue turns unreliable for a reason players can learn | ✅ DecoyCheckpoint: real from afar, gives itself away up close |
| OP12 | Amplify | Bigger magnitude, same rule | 🧩 Chase_Standart 4 → Chase_Bolum1 5.5 m/s; Ped_* launch heights |
| OP13 | Shrink | Less range, time, space or tolerance | 🧩 tighten HeavyCauldron stress/break span (2.4 / 3.4 m) |
| OP14 | Chain | Solving one system switches on the next | ✅ plate → door → next beat; crate carried onto a plate |
| OP15 | Expire | A state gets a lifetime you can see | ✅ CrumblingFloor (regrows after 3 s); Door_Zamanli (Gym only) |
| OP16 | Charge | Power builds through time, motion or teamwork | 🆕 no charge state anywhere |
| OP17 | Overheat | Repeated use brings a temporary penalty | 🧩 SwapGate lockout after repeated passes (doubles as AG3) |
| OP18 | Anchor | Pins one player or object while the rest move | ✅ plate holder rooted (P27); cauldron carriers cannot jump |
| OP19 | Mirror | Reflects motion, state or input onto another actor | 🧩 `ControlSwap.Compose` feeding the partner's Left into your Right |
| OP20 | Oppose | Another player or system reacts in the opposite direction | ✅ Pushable: opposite pushers cancel exactly; Seesaw |
| OP21 | Vote | The effect waits until enough players commit | ✅ `requireDistinctPlayers` plates; majority-of-N is 🧩 |
| OP22 | Sacrifice | Gives up an ability or resource for temporary progress | ✅ plate holder stays behind; carrying gives up jump and dash |
| OP23 | Infect | A state spreads by contact | 🆕 no status that can spread |
| OP24 | Pass | Hands ownership or risk to another player | ✅ Carryable dropped for a partner to pick up; SwapGate hands the walker's old move back |
| OP25 | Echo | An action repeats later or somewhere else | 🆕 input replay (the partner's move landing one trip late is not this) |
| OP26 | Record/Replay | A captured sequence becomes a system input | 🆕 ghost replay; `NetworkInput` already serialises every tick's keys, nothing stores them |
| OP27 | Randomize Within Bounds | Shifts a known parameter inside readable limits | ✅ SwapGate: a random different move nobody else holds |
| OP28 | Personalize | Each player gets their own version of the rule | ✅ ColorTunnel course built from the owner's handed-away move |
| OP29 | Conditionalize | The rule applies only while a visible state holds | 🧩 `LaunchPad.launchesCarriers`; plate layer mask |
| OP30 | Make Physical | An abstract state becomes an object you handle | 🧩 Carryable token that re-deals a move on pickup; owner-colour cord is 🆕 visual |
| OP31 | Duplicate | A second copy shares or fights the first's state | 🧩 two Doors on one plate, one inverted (OP01) |
| OP32 | Rotate | Cycles owner, orientation, order or target | 🟡 ControlSwap ring deal for 3–4; nothing advances it on a beat (🧩 `NetworkSwap.Reroll`) |
| OP33 | Broadcast | Shows one player's action or state to everyone | ✅ antenna icon over the owner in the colour of whoever plays the move (MIX-155); ask-back blink |
| OP34 | Mute | A talk or feedback channel drops out briefly | 🧩 suppress the antenna/radio cue (ControlSwapView); voice is untouchable |
| OP35 | Tether | Couples two bodies so motion or state carries over | ⛔ no hard tether; ✅ soft form is the cauldron's separation stress |
| OP36 | Siphon | Drains one player or system to feed another | 🆕 e.g. cauldron fill spent as fuel |
| OP37 | Lock | Commits a state for a short spell | ✅ Door latch: `Door_Kilitli` holds for good, `Door_Zamanli` for 3 s (Gym only) |
| OP38 | Phase | Toggles between two collision or visibility states | 🟡 ColorTunnel plug is solid per seat, never over time |
| OP39 | Attach/Detach | Changes who carries or controls whom | ✅ E grab/release: cauldron handles, Carryable |
| OP40 | Decoy | A believable false target, told apart by behaviour | ✅ twin shuttle, bait crate, stair bait (B1) |
| OP41 | Accelerate | The rate rises with repetition or time | 🟡 ChasingHazard eases to full speed in 1.2 s, then holds; nothing speeds up with repeated use |
| OP42 | Trade | Swaps unlike abilities or resources between players | ✅ SwapGate: the walker returns one move and takes another |
| OP43 | Threshold | Fires once a combined state crosses a line | ✅ plate `requiredCount`; Seesaw torque; cauldron stress from 2.4 m |
| OP44 | Priority | Conflicts resolve by a shifting player order | 🆕 nothing conflicts today — each Space drives exactly one body |
| OP45 | Invert Cost | Helping spends a surprising but visible resource | 🧩 the rescue route that spills fill (`launchesCarriers`) |

## 3. OB — Object palette (60)

In seed order. **Every verb must land on a key Mixtrol already has**: E covers grab, carry, press, pull, insert, drop;
A/D/W/S/Shift cover the movement verbs; Space plays a dealt move (the full list: `README.md`, Mixtrol deltas, Inputs). Verbs that need aiming or a held crank (aim,
throw, turn) have no key — the object is 🆕 or loses that verb. Mixtrol column: the device that already *is* the object.

| ID | Object | Base affordance | State to manipulate | Familiar actions | Mixtrol |
|---|---|---|---|---|---|
| OB01 | Rope | Joins two points, carries tension | Slack, anchor point | pull, swing, tether, cut, reel | ⛔ no hard tether; soft form is the cauldron |
| OB02 | Door | Gates space between zones | Open, side, owner | open, close, lock, rotate, crush | ✅ Door (Basili/Kilitli/Zamanli); no crush logic, no feedback slot |
| OB03 | Bridge | Temporary crossing | Angle, support, occupancy | raise, lower, rotate, collapse | 🧩 a Door slid as a span off a plate; collapse = CrumblingFloor |
| OB04 | Platform | Carries and moves players | Position, speed, solidity | translate, tilt, phase, drop | ✅ MovingPlatform (Mekik/Asansor/Hizli); timer only, takes no input |
| OB05 | Elevator | Lifts a group between heights | Floor, direction, load | call, ride, stop, overload | 🟡 MovingPlatform + Platform_Asansor; no call, no load limit |
| OB06 | Magnet | Pulls or pushes tagged things | Polarity, strength, target | toggle, rotate, charge, redirect | 🆕 force field on bodies |
| OB07 | Balloon | Lift that bursts easily | Lift, volume, attachment | inflate, pop, tether, release | 🆕 lift state in MovementSolver |
| OB08 | Crate | Movable mass that holds cargo | Weight, contents, damage | carry, stack, slide, break | ✅ Carryable (Yem_Sandik) + Pushable (Kutu_Agir); neither ever resets |
| OB09 | Torch | Portable light and heat | Fuel, brightness, holder | carry, ignite, extinguish, transfer | 🧩 Carryable with a light; a fuel timer is the only new code |
| OB10 | Switch | Flips a discrete state | State, owner, cooldown | press, hold, toggle, sequence | 🧩 new `IInteractable` on E; Door reads only PressurePlate inputs today |
| OB11 | Seesaw | Weight difference becomes tilt | Angle, load spread | stand, shift, launch, balance | ✅ Seesaw (mask 513: a crate counts, so one player can fake it) |
| OB12 | Conveyor | Moves things continuously | Direction, speed | start, reverse, speed, redirect | 🧩 a `RiderSurface` returning a constant delta |
| OB13 | Fan | Pushes one way | Direction, force | rotate, power, aim, overheat | 🆕 force volume; LaunchPad is a one-shot, not a stream |
| OB14 | Cannon | Fires objects or players | Aim, load, fuse | aim, load, fire, charge | 🟡 LaunchPad: one fixed throw per asset (`Ped_Yatay` adds 16 m/s sideways); no aim, no load |
| OB15 | Ladder | Vertical climb | Length, anchor, occupancy | extend, retract, carry, anchor | ⛔ climbing is deliberately out of scope (GDD: "Tırmanma ve merdiven … bilerek yazılmadı" — vertical movement breaks the 2.5D lane's readability) |
| OB16 | Zipline | Height becomes guided travel | Speed, rider, endpoint | grab, brake, release, reroute | 🆕 rider state; E grabs and releases |
| OB17 | Boat | Carries a group over danger | Heading, speed, load | steer, row, balance, anchor | 🟡 B2 S1 rafts are timer MovingPlatforms; no steering, no load tilt |
| OB18 | Minecart | Momentum along rails | Speed, track, riders | push, brake, switch track, ride | 🆕 rail vehicle; Pushable is the nearest push model |
| OB19 | Spring | Stores and releases force | Compression, orientation | compress, aim, release, overload | 🟡 LaunchPad compresses 0.11 m but stores nothing |
| OB20 | Mirror | Bends rays or sight | Angle, target | rotate, carry, align, flip | 🆕 needs a ray system (OB21) |
| OB21 | Laser | A precise line, harmful or useful | Path, power, colour | aim, block, split, pulse | 🆕 raycast Hazard a crate can block; a static strip is just Hazard |
| OB22 | Valve | Meters flow | Rate, destination | open, close, throttle, redirect | 🆕 no fluid system |
| OB23 | Battery | Portable stored energy | Charge, holder | charge, carry, insert, drain | 🧩 Carryable on a PressurePlate — how the bait crate already works |
| OB24 | Fuse | Delayed trigger | Time left, target | light, cut, transfer, extend | 🆕 countdown object; CrumbleSolver's crack delay is the nearest |
| OB25 | Umbrella | Blocks falling force and wind | Angle, integrity | open, close, tilt, share | 🆕 drag state; tilting needs a key |
| OB26 | Key | Grants access | Owner, matching lock | carry, copy, insert, steal | 🧩 Carryable + a plate masked to its layer → Door |
| OB27 | Map | Spatial knowledge | Visible area, owner | reveal, rotate, annotate, tear | 🧩 ColorTunnel's per-seat `LocalViewer` hiding |
| OB28 | Bell | A timed signal everyone hears | Ring state, range | ring, dampen, sequence, relay | 🧩 PressurePlate + a sound feedback (no plate SFX yet; the game has 2 clips) |
| OB29 | Paint | Persistent surface marking | Colour, coverage | spray, mix, erase, transfer | 🆕 tunnel colour is fixed per seat; repainting ownership is new |
| OB30 | Lever | Committed mechanical state | Position, lock | pull, hold, reverse, jam | 🧩 `IInteractable` on E feeding Door (same gap as OB10) |
| OB31 | Wheel | Turns to steer, wind or align | Angle, torque | turn, brake, couple, free-spin | 🆕 held-E crank; the action asset has no hold interactions |
| OB32 | Hook | Grabs far targets | Target, tension | throw, latch, pull, release | 🆕 throwing needs aim; only fixed hook points fit the keys |
| OB33 | Bucket | Carries divisible stuff | Contents, volume | fill, pour, swing, leak | ✅ CoCarriedObject cauldron (fill; spills with separation) |
| OB34 | Spool | Stores and pays out line | Length, winding | reel, unwind, lock, cut | ⛔ no hard tether |
| OB35 | Ice Block | Slides, melts | Speed, size, temperature | push, ride, melt, refreeze | 🆕 low-friction Pushable variant + melt timer |
| OB36 | Bomb | Timer, danger and portable goal in one | Timer, owner | carry, pass, arm, disarm | 🆕 countdown on a Carryable (hot potato) |
| OB37 | Parachute | Slows falls, adds air steering | Deployed, drag | deploy, cut, share, steer | 🆕 drag state; apex gravity is already a tunable |
| OB38 | Flashlight | Reveals information in a cone | Beam, battery | aim, toggle, focus, handoff | 🆕 facing-aimed reveal on top of `LocalViewer` |
| OB39 | Portal | Links far spaces | Pairing, exit | enter, redirect, pair, disable | 🆕 teleport pair; NetworkTransform snaps need handling |
| OB40 | Gravity Zone | Local movement rules | Direction, area | enter, move, rotate, disable | 🆕 per-zone MovementTuning override; sideways gravity is lane-hostile |
| OB41 | Pulley | Turns one motion into another via rope | Ratio, tension, load | pull, lock, reroute, overload | 🧩 SeesawSolver-style balance driving two linked platforms |
| OB42 | Chain | Links bodies in segments | Links, tension | attach, drag, wrap, break | ⛔ no hard tether |
| OB43 | Cage | Holds a body, still lets it act | Occupant, lock | lock, move, rotate, open | 🆕 containment volume released on E |
| OB44 | Trapdoor | Floor becomes route or hazard | Open, destination | open, hold, reset, redirect | 🟡 CrumblingFloor drops under load and regrows; nobody opens it on purpose |
| OB45 | Pressure Plate | Reads weight or occupancy | Load, threshold | stand, stack, overload, release | ✅ PressurePlate (`requiredCount`, `requireDistinctPlayers`) |
| OB46 | Pendulum | Stores periodic momentum | Phase, amplitude | push, ride, catch, redirect | 🧩 MovingPlatform on an arc (PlatformSolver is linear today) |
| OB47 | Crane | Moves a hung load on several axes | Hook position, cargo | raise, lower, rotate, release | 🆕 multi-axis device; axes dealt across seats would be P01 |
| OB48 | Water Pump | Moves fluid between spaces | Pressure, reservoir levels | pump, reverse, prime, drain | 🆕 no fluid system |
| OB49 | Pipe | Routes material through a network | Connectivity, pressure | connect, rotate, block, vent | 🆕 routing puzzle |
| OB50 | Hose | Flexible directed flow | Pressure, aim | aim, kink, connect, spray | 🆕 aiming needs a key |
| OB51 | Generator | Player work becomes shared power | Output, heat | crank, fuel, overload, reroute | 🧩 plate occupancy as "power" into a Door |
| OB52 | Barrel | Rolls, holds stuff, acts as mass | Contents, momentum | roll, stack, open, ride | 🟡 Pushable slides, never rolls; no contents |
| OB53 | Boulder | Heavy momentum and blocking | Velocity, position | push, brake, redirect, wedge | 🟡 Pushable stops when pushing stops; ChasingHazard is the rolling-doom form |
| OB54 | Shield | Blocks hazards, turns force | Angle, durability | carry, angle, plant, share | 🆕 Carryable that masks Hazard contact |
| OB55 | Radio | Thin signal between separated players | Channel, signal quality | tune, transmit, jam, handoff | 🟡 ask-back radio (ControlSwapView): one symbol, cannot be tuned or jammed |
| OB56 | Clock | Shared timing | Offset, speed | set, stop, accelerate, synchronize | 🆕 Door_Zamanli and ChasingHazard timers are fixed, not shared |
| OB57 | Turnstile | One-at-a-time, one-way passage | Orientation, occupant | push, reverse, lock, rotate | 🆕 one-way gate; the tunnel plug is per owner, not per turn |
| OB58 | Rotating Room | Turns the world around the players | Angle, gravity relation | rotate, lock, counter-rotate, phase | — axis |
| OB59 | Trampoline | Landing force becomes launch | Tension, launch vector | aim, tension, move, overload | 🟡 LaunchPad: fixed height, ignores landing speed |
| OB60 | Drone | Remote movement, camera or carry | Controller, battery, cargo | pilot, handoff, dock, sacrifice | 🆕 pilotable pawn; Space could drive it as a dealt move |

## 4. CQ / RQ — Consequence and recovery pools (10 + 10)

The seeds draw their consequence and recovery from these two fixed pools. No canonical order; numbered by first
appearance in the seeds.

| ID | Pool entry — consequence (≤15 words) | Maps to RC/P ID |
|---|---|---|
| CQ01 | A moving hazard reshuffles everyone's positions | P50 · P60 |
| CQ02 | Control changes hands; roles must be renegotiated fast | P02 · P62 |
| CQ03 | The objective ends up somewhere worse but still solvable | P63 · P44 |
| CQ04 | A safe crossing turns into a rescue | P66 · P40 |
| CQ05 | Shared tempo or resource is spent and a comeback window opens | P21 · P66 |
| CQ06 | The group splits and knowledge becomes uneven | P69 · P11 |
| CQ07 | A second system wakes up later | P53 · P59 |
| CQ08 | The object flips from tool to obstacle, then back | P58 · P54 |
| CQ09 | Risk lands on the nearest or last player to touch it | P22 · P47 |
| CQ10 | A shortcut opens with local danger attached | P33 · RC12 |

| ID | Pool entry — recovery (≤15 words) | Maps to RC/P ID |
|---|---|---|
| RQ01 | The faller drops into a short side route that rejoins ahead | RC02 · P61 |
| RQ02 | A brief window lets a teammate step in before the full cost | RC10 · P66 |
| RQ03 | The group splits into parallel paths that merge after a short task | RC11 · P69 |
| RQ04 | The culprit ends up nearest — or alone — able to fix it | RC03 · P62 (FC30) |
| RQ05 | Two players restore the state with one quick joint action | RC09 · P67 |
| RQ06 | The broken object stays, usable in a new way | RC05 · P63 |
| RQ07 | The hazard times out and leaves a new way across | RC08 · P64 |
| RQ08 | The key tool moves to another player instead of vanishing | RC07 · P65 |
| RQ09 | The worse-off player gets a temporary compensating ability | RC06 · P70 |
| RQ10 | Failure spawns a small side task, not a restart | RC01 · P68 |

Every RQ is a tier-1 shape. Built today: only RQ02 (the swapped air jump saves a faller). Near misses: stepping back
on a plate reopens the door in 0.5 s, but one player does it (not RQ05); a CrumblingFloor regrows after 3 s, but as
the old way, not a new one (not RQ07). The rest are 🧩 layout or 🆕 — none of them replaces tier 2.

## 5. RA — Room archetypes (36)

A room is one archetype built from OB × P × OP. "Lane-hostile" means it fights the single horizontal lane and the
shared group camera.

| ID | Archetype | Premise (≤15 words) | Mixtrol |
|---|---|---|---|
| RA01 | Blind Navigator | One player sees the whole layout; runners see only their surroundings | 🟡 ColorTunnel, inverted: the runner sees inside, the Space-holder is blind |
| RA02 | Shared Balance | Group positions steer one platform; any step helps or tips everyone | 🟡 Seesaw tilts with group weight; nothing travels where the group leans |
| RA03 | Control Roulette | Move ownership rotates on success or failure; everyone keeps calling who holds what | 🟡 SwapGate re-deals on a gate pass, not on success or failure; that trigger is 🧩 (`NetworkSwap.Reroll`) |
| RA04 | Hot Potato Power | A useful, dangerous state must keep moving before it expires | 🆕 countdown Carryable (OB36) |
| RA05 | One-Way Rescue | Saving someone leaves the rescuer worse off, so the favour must be returned | 🧩 plate that opens the partner's way and strands the holder until the partner frees them |
| RA06 | Mirror Rooms | Two teams in linked spaces; one room mirrors or inverts the other | — lane-hostile: two rooms cannot share one frame; also needs 4 players |
| RA07 | Sacrifice Elevator | One player stays behind to power the lift, then needs a way back | 🧩 plate-driven Platform_Asansor (platforms take no input yet — small) |
| RA08 | Color Ownership | Objects answer only to their colour's player; colours can change hands | 🟡 ColorTunnel answers to its owner only; colours are fixed per seat (swapping them is 🆕) |
| RA09 | Echo Chamber | Inputs replay after a delay; players plan around their own past moves | 🆕 input replay (OP25) |
| RA10 | Body Bridge | Bodies become the path — and can step out of it on purpose | 🆕 standing on a partner is unverified (ground mask is Ground only) |
| RA11 | Unstable Cargo | Knocks change the carried object's later behaviour instead of ending the run | 🟡 CoCarriedObject cauldron: a spill lowers fill, no restart; lower fill changes no handling and gates nothing |
| RA12 | Vote Gate | A world state flips only once a majority commits | 🧩 distinct-player plates + `requireAll` door; majority-of-N needs the registry count |
| RA13 | Shared Oxygen | Everyone drains one pool; shortcuts spend it to buy time | 🟡 fill is shared and finite but gates nothing (`FillSufficient` unused); ⛔ as primary (playbook: shared counter never primary) |
| RA14 | Role Debt | Being helped creates a short obligation or forced hand-over later | 🧩 re-deal the helper's move after a rescue (`NetworkSwap.Reroll`) |
| RA15 | Sabotage Shortcut | The fastest line needs a move that briefly hurts a teammate | 🧩 `LaunchPad.launchesCarriers` on: the fast route spills the cauldron |
| RA16 | Information Relay | Each player holds one fragment; progress needs short calls down the line | 🟡 ColorTunnel wall icon is one fragment; multi-fragment rooms for 3–4 missing |
| RA17 | Gravity Relay | Ownership of local gravity passes between players or zones | — axis: sideways gravity breaks the lane; up/down only is 🆕 (OB40) |
| RA18 | Moving Safe Zone | One safe region moves, and players can shift where it goes | 🟡 MovingPlatform / B2 rafts over hazard; nobody can steer them |
| RA19 | False Exit | Several exits look right; an information role tells them apart under pressure | 🟡 DecoyCheckpoint, twin shuttle; no role sees the difference, and each is solved once, then dead (AP01, AP11) |
| RA20 | Chain Rescue Finale | Each rescue moves the danger to someone else until the system settles | 🧩 the swapped air jump saves a faller (P66); a 3–4 ring chains it |
| RA21 | Tether Maze | Linked pairs in different lanes; one side's progress strains the other | ⛔ no hard tether; lane-hostile as well |
| RA22 | Counterweight Tower | Climbing needs the group to keep shifting weight between floors | 🟡 one Seesaw; stacked floors crowd the camera (lane-hostile when tall) |
| RA23 | Delayed Control Room | Remote operators change the runners' space with a 2–5 s lag | 🆕 deliberate lag; an off-screen operator room is lane-hostile |
| RA24 | Fragile Shortcut | A breakable fast route reshapes the geometry for good when abused | 🟡 CrumblingFloor regrows after 3 s; never permanent |
| RA25 | Signal Blackout | Talk or sight drops out during the key movement windows | 🧩 mute the antenna/radio cue (ControlSwapView); Discord cannot be touched |
| RA26 | Shared Cooldown Arena | Strong moves share one cooldown; every dash becomes a negotiation | 🆕 dash cooldown is per body in MovementSolver |
| RA27 | Moving Ownership | The nearest player automatically controls the object | 🧩 contact re-deal via the SeparateFromPartners overlap (P47) |
| RA28 | Pressure Relay | Holding one state builds pressure someone elsewhere must release | 🟡 B2 S1 island + far-bank plates on a `requireAll` door; `Door_Kilitli` latches, so holding builds no pressure |
| RA29 | Asymmetric Race | Parallel routes with different info; each can open or shut the other's shortcut | 🟡 B2 S5 stacked ColorTunnels; no cross-route shortcuts; a wide split is lane-hostile |
| RA30 | Tool Migration | Every successful use sends the tool to another player | 🧩 re-deal the move after each use (ControlSwap ring) |
| RA31 | Unstable Vehicle | Four players run one vehicle's steering, power, brake and balance | 🆕 vehicle; nearest is one body's moves dealt across seats (ControlSwap) |
| RA32 | Punishment Playground | Common failure states hand out odd movement or tools for recovery | 🆕 tier-2 death grants nothing; tier-1 states with perks are new (P64) |
| RA33 | Commitment Corridor | Nothing can be cancelled once started; agree before entering | ✅ LaunchPad flight; ChasingHazard start line |
| RA34 | Resource Auction | Players jostle or bargain for one short-lived power | 🧩 SwapGate as the prize (first through re-deals) — needs a cooldown (AG3) |
| RA35 | Cause-and-Effect Lab | Actions visibly change far systems; learning the links is the puzzle | 🟡 plate → remote Door; the link is an editor gizmo only |
| RA36 | Recovery Gauntlet | Mistakes deliberately route into several small recoverable challenges | 🧩 lower routes under CrumblingFloor + `CoCarriedObject.RestoreTo` (tier 1) |

## 6. MD — Mutation drills (8)

Run on one seed at a time. Each drill changes exactly one thing.

1. **MD1** — Eight variants, each moving one axis only: ownership, information, timing, resource, space, physics, recovery, incentive.
2. **MD2** — Delete rules one at a time until the social story dies; ship the last set that still worked.
3. **MD3** — Easy / Medium / Hard from the same seed with no new input: tune timing, distance and grace, never keys.
4. **MD4** — Three versions: accidental comedy, intentional troll, accidental hero.
5. **MD5** — Works at 2, 3 and 4 players with no special cases ("en az iki / herkes").
6. **MD6** — Rewrite a physics-heavy seed as discrete state changes the host owns (`NetworkMechanisms`).
7. **MD7** — In an information-heavy seed, every hidden fact must be callable in under 3 s (one word or one icon).
8. **MD8** — Give a grief-prone seed a timed, reversible or majority counter-action (AG1–AG3).
