# Social-sabotage design grammar — Mixtrol catalog

Our paraphrase of `source/01_social_sabotage_design_grammar_expanded.pdf` (PDF pages 1–13). Every entry is checked against the game as it stood on 2026-09-22.
Cite by ID (P31, FC13, AG1, DC05); IDs are stable. Add new entries at the end and never renumber.
Status: ✅ built · 🟡 partial · 🧩 cheap with existing systems, no new key · 🆕 needs a new system · ⛔ conflicts with a recorded decision · — not applicable to a horizontal 2.5D lane.

## Decomposition

This is the default way to take a mechanic apart. Fill all ten fields before judging the idea.

1. **Goal**: one shared objective that fits in one sentence.
2. **Base affordance**: what the object visibly looks able to do.
3. **Constraint**: what blocks the obvious solo solution.
4. **Dependency**: why another player materially matters.
5. **Sabotage vector**: an ordinary, legal action that can disrupt someone, on purpose or by accident.
6. **Information model**: who knows what, when, and how surely.
7. **Consequence**: the immediate state change the action causes.
8. **Recovery**: how failure stays playable instead of becoming a dead stop.
9. **Escalation**: how the same rules get harder without new buttons.
10. **Clip moment**: a 5–10 s causal story that an outsider can follow.

Generation equation: `object + affordance + constraint + dependency + sabotage + information rule + recovery + escalation`.

The same fields, filled in for Mixtrol:
- Dependency and sabotage go through the swap table or a shared body (cauldron, plate, seesaw).
- Escalation never adds a key.
- Recovery is filed as tier 1 or tier 2 (see RC).

## P — Interaction patterns (70)

The PDF subtitle says 60 patterns, but the list has 70; use the list. The tags are the corpus's own. The Mixtrol column gives the status mark and where the pattern lives today.

| ID | Pattern | Tags | Rule | Risk | Mixtrol |
|---|---|---|---|---|---|
| P01 | Split Control | control, dependency | Players own different actions or axes of a shared actor. | Ownership must be visible; latency-bound actions need forgiveness. | ✅ move swap: Space plays the partner's move (`ControlSwap`) |
| P02 | Rotating Ownership | control, surprise | An action's owner changes after a trigger, timer or success. | Fast remapping becomes noise without strong feedback. | 🟡 `SwapGate` re-deals on entry; nothing rotates on success or death (`NetworkSwap.Reroll` has no other caller) |
| P03 | Partial Authority | control, coordination | Each player can start only one stage of a multi-stage action. | Long serial chains leave players idle. | 🟡 swapped jump: owner runs, holder launches; no multi-stage device |
| P04 | Shared Actor | control, physics | Several players steer one body or device at the same time. | Clamp forces so disagreement stays funny, not uncontrollable. | ✅ cauldron (`CoCarriedObject`) and `Pushable`, where opposite pushes cancel |
| P05 | Input Echo | control, delay | One player's input replays on another body after a readable delay. | Telegraph the pairing and the lag. | 🆕 needs a delayed replay channel in `ControlSwap.Compose` |
| P06 | Control Debt | control, reciprocity | A strong action lends one of your own controls away briefly. | Debt must be short, with a guaranteed return. | 🧩 `DashTriggered` edge lends a move through `NetworkSwap` for N s |
| P07 | Leader / Executor | control, communication | One player decides the command; another physically executes it. | Both roles need timing; nobody should be a passive caller. | ✅ radio ask: owner calls, holder presses Space; tunnel wall icon |
| P08 | One-Way Delegation | control, trust | A tool or action can be handed away but not snatched back. | Needs a timed or cooperative reclaim path. | 🟡 a taken move is never handed back on request; the ask only blinks (`ControlSwap.Asked`), no reclaim path — by design (DA-13, accepted) |
| P09 | Vote-to-Act | control, negotiation | State flips only once enough players commit to it. | Keep windows short; no menu friction. | 🧩 plate `requiredCount` N + `requireDistinctPlayers` as a body vote |
| P10 | Asymmetric Sensitivity | control, skill | Players push the same variable with different strengths. | Show strength differences through role and visuals. | 🟡 a carrier weighs 2 in `Seesaw` torque, invisibly to players |
| P11 | Local Visibility | information, voice | Each player sees facts the others cannot. | Facts must be callable in seconds under pressure. | ✅ `ColorTunnel`: only the owner sees and passes inside |
| P12 | Hidden Role Mapping | information, inference | Only part of who owns which action is shown. | Behaviour must let players infer ownership quickly. | ⛔ GDD rule: the antenna always shows the owner; only tunnel interiors are private |
| P13 | Asymmetric Map | information, navigation | One role sees the global layout; runners see only what is nearby. | Give the navigator hazards or choices, not downtime. | 🧩 `ColorTunnelView`'s per-seat LocalViewer reveal can show one seat the route |
| P14 | Perspective Mismatch | information, spatial | Players see one space from different orientations or scales. | Shared stable landmarks let calls converge. | — side-view |
| P15 | Noisy Signal | information, uncertainty | Useful information arrives distorted, partial or intermittently blocked. | Noise must leave players room to adapt. | 🧩 `ControlSwapView` can drop the antenna blink in a zone; Discord cannot be touched |
| P16 | Timed Knowledge | information, memory | A clue is visible only for a short window. | Keep the memory load modest and tie it to action, not trivia. | 🆕 no clue prop; needs a device with a reveal timer |
| P17 | One-Word Channel | information, comedy | A role can send only one fixed symbol at a time. | Restrict expression without hurting accessibility. | ✅ radio ask-back lights the move's icon over the asker in the holder's colour (MIX-155); tunnel wall icon |
| P18 | Remote Consequence | information, cause-effect | A local action changes a distant player's surroundings. | Reveal the link soon after the first failure. | ✅ `PressurePlate` → `Door`; the link is drawn only as an editor gizmo |
| P19 | False-Positive Cue | information, trust | Some cues are unreliable, under a rule players can learn. | No arbitrary lies; unreliability needs a rule. | ✅ `DecoyCheckpoint`: looks real from afar, gives itself away up close |
| P20 | Memory Relay | information, teamwork | Each player holds one fragment; the team rebuilds the whole. | Keep turns fast; nobody becomes a note-taker. | 🆕 needs per-seat fragment props; strongest at 3–4 players |
| P21 | Shared Limited Resource | resource, negotiation | Everyone draws on one finite pool. | Offer regeneration or another source of recovery. | 🟡 cauldron fill is shared and finite but gates nothing (`FillSufficient` unused) |
| P22 | Transferable Risk | resource, tension | A penalty or hazard moves between players by touch or action. | Owner and timer must be unmistakable. | 🧩 `Carryable` handoff on E plus a fuse-timer component |
| P23 | Personal Bonus / Shared Goal | incentive, harmless conflict | The team wins together; each player also chases a side incentive. | Side goals must never outrank the shared one. | 🧩 per-seat pickups tallied on `RunResultsView` beside the `BlameBoard` |
| P24 | Resource Decay | resource, urgency | Stored advantage that goes unused drains or changes over time. | Decay should set the tempo, not force waiting. | 🧩 add an idle leak to the `CarriedObjectSolver` fill; the spill path exists |
| P25 | Charge Sharing | resource, dependency | One player's gain draws down another player's charge. | Draw the transfer visibly. | 🆕 no per-player charge meter; dash and air jump are private |
| P26 | Hoarding Hazard | resource, anti-selfishness | Carrying too much brings a local penalty. | The penalty should be exploitable as well as harmful. | 🟡 a carrier weighs 2, so `CrumblingFloor` cracks twice as fast |
| P27 | Sacrifice Window | resource, trust | One player gives up mobility or a tool for a bounded time. | Never strand anyone indefinitely. | 🟡 the plate holder is rooted; only `Door_Kilitli` latching guarantees release |
| P28 | Debt Marker | resource, reciprocity | Receiving help leaves a token that later shifts control or priority. | Debt should make stories, not bookkeeping. | 🆕 no help ledger; `BlameBoard` records faults only |
| P29 | Scarcity Vote | resource, negotiation | The group decides who receives a one-use benefit. | Decide in play, never in a modal menu. | 🧩 one crate (`Yem_Sandik`) for two plates: whoever gets it is freed |
| P30 | Cost Transfer | resource, betrayal | An action's price can be shifted onto a nearby player. | Give a clear warning and room for counterplay. | 🟡 `SwapGate`: the walker's re-deal changes which move the partner lacks |
| P31 | Trust Contract | trust, betrayal | One player keeps a helpful state while another commits to danger. | Short consequences, fast recovery. | ✅ plate holder under `Door_Basili`; the swap holder times your jump |
| P32 | Reversible Sabotage | trolling, recovery | A harmful act always has a dependable way back. | The way back must work under normal latency. | 🟡 stepping back on a plate reopens it in 0.5 s; a withheld move never returns |
| P33 | Sabotage with Benefit | tradeoff, trolling | One act hurts a teammate and gains ground elsewhere. | Both the harm and the gain must read. | 🧩 `LaunchPad.launchesCarriers` on: flings a carrier across and spills the cauldron |
| P34 | Bait-and-Switch | trust, timing | A helpful-looking state changes once someone commits. | Telegraph after the first failure so it becomes mastery. | ✅ `CrumblingFloor` gives way under the second crosser; B1 S3 bait crate |
| P35 | Reciprocal Betrayal | trust, deterrence | Each player can hit another with a small penalty that can be returned. | Cap frequency to stop spam. | ✅ the 2P swap is mutual: each can mistime the other's move |
| P36 | Mutually Assured Sabotage | trust, negotiation | Disrupting others also exposes or weakens the instigator. | The cost deters hard griefing but keeps the temptation. | ✅ shared death resets the troll too; opposite pushes stall both |
| P37 | Accidental Framing | trust, comedy | Indirect effects get credited to the wrong player. | The causal chain must be inspectable afterwards. | 🟡 crumble and swap deaths frame the victim; no cause tag (MIX-12) |
| P38 | Conditional Safety | trust, surprise | A seemingly stable object is held up by someone else. | Reveal the dependency through feedback. | ✅ `Door_Basili` is open only while its plate is held; the door has no feedback |
| P39 | Bluffable Intent | trust, social play | Players signal a plan without being bound to it. | Success must never require deceit. | 🟡 the radio ask is non-binding; the holder has no intent cue |
| P40 | Rescue Bargain | trust, reciprocity | Rescuing a teammate costs the rescuer position, resources or time. | Always keep an anti-hostage fallback. | 🟡 helping means leaving the plate or dropping the cauldron (E) |
| P41 | Body-as-Tool | physics, co-op | Player bodies act as platforms, weights, shields or links. | Stabilise physics and collision layers. | 🟡 bodies weigh on plates and the `Seesaw`; standing on a partner is unverified |
| P42 | Tethered Pair | physics, dependency | Two players are joined by a tether of limited length. | Make the tension readable and give a safe way to unstick. | ⛔ no hard tether (GDD Kapsam Dışı); the cauldron is the soft form |
| P43 | Counterweight Team | physics, balance | Players distribute their weight to move a device. | No precision that depends on frame rate. | ✅ `Seesaw`: torque from weight × distance, solved on the host |
| P44 | Unstable Cargo | physics, care | Shared cargo degrades under tilt or impact. | Failure should change the cargo, never force a restart. | ✅ the cauldron spills when carriers separate; fill drops and the run continues |
| P45 | Shared Center of Mass | physics, coordination | The group's combined position steers a platform or vehicle. | Generous thresholds and a smoothed response. | ✅ `Seesaw` tilts from the summed torque of all riders; no vehicle yet |
| P46 | Push / Pull Asymmetry | physics, roles | Some roles can only push, others only pull. | Role icons must be obvious. | 🆕 no pull verb: `Pushable` only pushes, E only carries |
| P47 | Collision Ownership | physics, blame | The last player to touch something becomes its owner. | A short lockout stops ownership churn. | 🧩 `SeparateFromPartners`'s capsule-distance test can detect a touch that swaps the taken moves, with a lockout |
| P48 | Local Gravity | physics, spatial | Gravity direction differs by player or region. | Camera and controls must stay readable. | 🆕 `MovementSolver` has one gravity axis |
| P49 | Momentum Inheritance | physics, timing | Momentum passes on through grabs, collisions or handoffs. | Cap extreme speeds; watch for desync. | 🟡 `LaunchPad` keeps horizontal speed; a dropped crate keeps its momentum |
| P50 | Physics Cascade | physics, emergence | One moved object changes the state of another system. | Cap the chain length and make each cause stand out. | 🟡 crate on plate → `Door`; `Pushable` on `CrumblingFloor` → collapse. Two links at most |
| P51 | Synchronized Commitment | timing, network | Several players must commit inside one window. | Server-tolerant windows; never frame-perfect sync. | ✅ B2 S1: island and far-bank plates held by different players |
| P52 | Staggered Timing | timing, rhythm | The solution needs actions in a set order, not all at once. | Show the timing phase visually. | 🟡 `CrumblingFloor` forces one-at-a-time crossings; no phase display |
| P53 | Delayed Consequence | timing, blame | An action resolves later or somewhere else. | Keep causal memory short. | ✅ `CrumblingFloor` gives 0.6 s after touch; `DecoyCheckpoint` costs at the next death |
| P54 | Expiring State | timing, urgency | A helpful state ends on a visible timer. | The timer must be visible in the space. | 🧩 `Door_Zamanli` (`autoCloseDelay` 3 s) exists but only in the Gym; no countdown cue |
| P55 | Cooldown Theft | timing, trolling | Touching a device or player resets or borrows their cooldown. | An immunity window prevents loops. | 🆕 the dash cooldown lives inside each solver; nothing can borrow it |
| P56 | Sequence Ownership | timing, roles | The next required action belongs to a shifting player. | Failure reshuffles the order, never hard-resets it. | 🧩 seat-filtered `PressurePlate` (like the `ColorTunnel` owner check) in sequence |
| P57 | Freeze / Continue | timing, authority | One player pauses one subsystem while the others move. | Never freeze another player for long without agency. | 🧩 a held plate pauses a `MovingPlatform` clock via `NetworkMechanisms` |
| P58 | State Inversion | timing, surprise | Safe/danger or on/off flips temporarily under a trigger. | Use one consistent visual language for the flip. | 🆕 no invertible surfaces; tunnel colours are fixed per seat |
| P59 | Cascading Timer | timing, escalation | Resolving one countdown starts or hands off another. | Never stack countdowns that cannot be read. | 🆕 no timer chaining; `Door_Zamanli` and `ChasingHazard` are independent |
| P60 | Commitment Trap | timing, comedy | Once started, an interaction runs until it resolves. | Keep it short and visibly committed. | ✅ `ChasingHazard` start line; `LaunchPad` throw |
| P61 | Fail-Forward Route | recovery, pacing | Missing the ideal play opens a slower or stranger route. | The fallback route must still be interesting. | 🧩 a lower route under `CrumblingFloor` instead of a pit (layout only) |
| P62 | Rescue Role Inversion | recovery, status | Failure hands the failed player a role that helps the others. | Do not over-reward failing on purpose. | 🧩 a fall lands in a lower lane whose plate the fallen player holds for the rest |
| P63 | Failure Mutates Level | recovery, emergence | A failed action breaks, moves or reshapes something locally. | The change must keep the room solvable. | 🟡 `CrumblingFloor` collapses but regrows after 3 s; nothing lasts |
| P64 | Punishment Becomes Power | recovery, comedy | A penalty state grants a compensating ability. | Failure must not become the best plan. | 🆕 no penalty state beyond death and the landing slowdown |
| P65 | Tool Displacement | recovery, dependency | A lost tool relocates instead of disappearing. | Avoid long walks to fetch it. | 🧩 `CoCarriedObject.RestoreTo` on a pit fall, not only on death |
| P66 | Comeback Window | recovery, tension | Failure opens a short rescue window before the full cost lands. | The window must be readable and latency-tolerant. | 🟡 the holder's swapped air jump can save a fall; nothing signals the window |
| P67 | Cooperative Reset | recovery, anti-grief | Undoing sabotage takes a quick joint action, not a restart. | The reset must not become repetitive chore work. | 🧩 a distinct-player plate resets the swap table or a crate |
| P68 | Secondary Objective Spawn | recovery, variety | A mistake spawns a small side task that can be recovered. | Keep the side task short. | 🆕 a spill only lowers fill; nothing drops that can be picked back up |
| P69 | Split-Then-Merge | recovery, pacing | A mistake splits players into separate lanes that later merge. | Separated players must stay engaged. | 🧩 two-lane layout rejoining at a plate and door; best at 3–4 players |
| P70 | State Compensation | recovery, fairness | A bad state slightly improves another relevant attribute. | Compensation should help recovery, never erase the consequence. | 🟡 the cauldron carrier is slower (×0.55) but heavier on the `Seesaw`; players are not told |

## FC — Failure chains (30)

A good chain has 4–6 readable steps: local action → state change → knock-on → social reaction → recovery or a new opening. The "Mixtrol seed" column names a current device that already produces the opening; — means nothing does yet.

| ID | Chain | Steps | Mixtrol seed |
|---|---|---|---|
| FC01 | Premature Action | acts before alignment → mechanism moves → teammate loses footing → rescue adds a hazard → survive, worse placed | holder presses Space before the partner lines up |
| FC02 | Wrong Information | wrong call given → runner commits → hazard fires → correction opens a side path → shortcut found | `ColorTunnel` owner calls a move too early; the blind holder obeys |
| FC03 | Resource Greed | one spends the shared pool → emergency option gone → small slip grows → roles reshuffle → spender must rescue | — |
| FC04 | Intentional Betrayal | support released on purpose → teammate falls → fall trips a remote switch → betrayer trapped → fallen frees them | plate holder steps off; `Door_Basili` shuts on the partner |
| FC05 | Physics Cascade | object drops → hits a moving system → another object redirected → player displaced → accidental solve | `Pushable` shoved onto `CrumblingFloor` or a plate (B1 S4) |
| FC06 | Timing Drift | synced action begins → one input late → phase slips → hazard targets the wrong player → improvise | a partner-played jump lands one network trip late (`NetworkInput`) |
| FC07 | Ownership Confusion | control changes quietly → old owner presses → new owner fires by surprise → blame spreads → feedback shows owner → recover | `SwapGate` re-deal: the old key now only asks |
| FC08 | Over-Rescue | two go for one rescue → both leave their posts → support collapses → rescued becomes the anchor → roles flip | — |
| FC09 | Panic Communication | hazard appears → conflicting calls → runner follows the wrong one → team splits → separated player learns something | B1 S7: `ChasingHazard` warning while a swapped move is still owed |
| FC10 | False Confidence | routine works twice → hidden condition changes → habit repeats → failure exposes it → next try informed | B1 S3 bait crate opens door 1; door 2 refuses it |
| FC11 | Friendly Fire Utility | accidental hit on a teammate → knocked onto a useful switch → shortcut opens → team tries to repeat it | — |
| FC12 | Shortcut Backfire | risky shortcut → time saved locally → resource stop skipped → later room harder → creative recovery | — |
| FC13 | Delayed Blame | harmless-looking press → seconds pass → distant hazard fires → wrong player blamed → feedback shows the real cause | first crosser cracks `CrumblingFloor`; the second falls and the label names them |
| FC14 | Chain of Promises | A promises to hold → B commits → C trusts A too → A moves → B and C fail differently → one rescues | — |
| FC15 | Tool Misdelivery | tool thrown → misses → lands with a third player → used for something unplanned → plan changes | crate (`Yem_Sandik`) dropped mid-run keeps momentum and lands off target |
| FC16 | Role Theft | shared device grabbed → ownership moves → old owner loses control → device fires wrongly → new owner repairs | `SwapGate` walker takes a new move; the partner's missing move flips |
| FC17 | Overcharge | team charges a device → one keeps going → it overshoots safe → environment changes → new exploit | — |
| FC18 | Greedy Rescue | rescuer rushes → resource left alone → hazard takes or moves it → rescue works → next objective changes | — |
| FC19 | Mutual Sabotage | two troll each other at once → penalties interact → a third player profits → trolls cooperate to catch up | — |
| FC20 | Signal Collision | two callers at once → runner misparses → commits to a blend → failure shows whose call was whose | — |
| FC21 | Split Failure | one side succeeds, one fails → state turns asymmetric → winners choose progress or rescue → regroup changed | — |
| FC22 | Momentum Mistake | object released early → wrong trajectory → teammate catches it → momentum transfers → new area reached | — |
| FC23 | Recovery Overshoot | recovery used too hard → state passes neutral → opposite problem appears → players learn to modulate | both rush to the `Seesaw`'s high end and it slams the other way |
| FC24 | Vote Fracture | vote barely passes → dissenter unready → global state flips → dissenter stranded → majority recovers them | — |
| FC25 | Countdown Transfer | own timer resolved → it jumps to the nearest teammate → panic → passed again → lands somewhere useful | — |
| FC26 | False Rescue | teammate assumed trapped → emergency route opened → they were on another path → collision → paths merge | a blind partner presses Space to "help" the `ColorTunnel` owner |
| FC27 | Environmental Theft | moving hazard takes a carried object → it travels through systems → someone intercepts → ownership and plan change | — |
| FC28 | Information Expiry | clue shown → team debates → clue gone → partial memories pieced together → disagreement settled by action | — |
| FC29 | Body Block | player stops in a doorway → team blocked → pressure builds → a push sets off a chain → blocker launched | character capsules block each other in corridors; there is no shove |
| FC30 | Recovery Hero | player causes the failure → sits nearest the recovery tool → must rescue → blamed becomes hero within seconds | the holder who mistimed the jump also owns the air jump that can save the fall |

## RC — Recovery types (12)

The failure doctrine (decided 2026-09-22) has two tiers:
- **Tier 1:** a small mistake is recovered in place, and the next decision comes within 3–8 s.
- **Tier 2:** a terminal failure is a shared death and one segment back.

Tier-2 rows are hooks that ride on the shared death. Every other row must resolve without anyone dying.

| ID | Type | Meaning | Tier | Mixtrol |
|---|---|---|---|---|
| RC01 | Fast local retry | Reset only the device or player; team progress stays. | 1 | 🟡 plate re-press 0.5 s, `CrumblingFloor` regrows in 3 s; every death resets everyone |
| RC02 | Alternate route | Failure unlocks a slower, odder or more social way forward. | 1 | 🧩 lower lane under `CrumblingFloor` or the `Seesaw` (layout only) |
| RC03 | Role inversion | The failed player gains a new information or control role. | 1 (2 after a death) | 🆕 tier 1: the faller lands by the lever that saves the other (P62); 🧩 tier 2: `NetworkSwap.Reroll` on death deals new roles |
| RC04 | Physical rescue | Falling, hanging or stuck states invite a teammate to step in. | 1 | 🟡 a swapped air jump saves falls; no hanging and no grabbing a teammate |
| RC05 | State mutation | A broken object changes what it affords instead of vanishing. | 1 | ✅ a cauldron spill lowers fill and the carry continues |
| RC06 | Resource compensation | Failure grants a small tool or charge needed to recover. | 1 | 🧩 refresh air jump and dash on a caught fall (`LaunchPad` refresh path) |
| RC07 | Tool relocation | The critical item moves to another player or place. | 1 | 🧩 `CoCarriedObject.RestoreTo` on a pit fall |
| RC08 | Temporary disadvantage | A penalty that expires predictably and can be played around. | 1 | 🟡 landing slowdown ≤ 0.35 s; a carrier left alone on the cauldron moves at ×0.25 until it is re-grabbed |
| RC09 | Team reset action | Two or more players quickly restore a sabotaged system. | 1 | 🧩 a distinct-player plate restores the swap table or a crate |
| RC10 | Comeback action | A brief high-agency rescue window right after the mistake. | 1 | 🟡 the swapped air-jump window exists; nothing signals it |
| RC11 | Split path | Failure splits players into parallel tasks that merge later. | 1 | 🧩 a two-lane layout that merges at a plate and door |
| RC12 | Accidental shortcut | A rare failure gives alternate progress without becoming the best strategy. | 1 | 🧩 a `LaunchPad` overshoot onto an authored ledge (layout) |

## CS — Comedy structures (20)

| ID | Structure | Shape | Mixtrol instance or — |
|---|---|---|---|
| CS01 | Expectation Reversal | A predictable rule is set up; another known rule flips the result. | B1 S3: the crate opens door 1; door 2 demands different players |
| CS02 | Status Inversion | The confident leader suddenly depends on the least powerful player. | `ColorTunnel`: the owner, who can see, needs the blind partner's Space |
| CS03 | Rule Collision | Two simple rules meet in an unplanned but understandable way. | carriers weigh 2 each, plus the cauldron: `CrumblingFloor` is gone in 0.12 s |
| CS04 | Escalation | A small fix causes a bigger problem, then needs a bigger fix. | B1 S7: going back through `SwapGate` to fix a deal while the wall arrives |
| CS05 | Commitment Trap | Someone commits out loud; the deciding fact arrives too late. | `LaunchPad`: airborne, then remembering the partner owns the air jump |
| CS06 | Visible Blame | The game makes plain who caused the mishap. | the spill label names whoever pulled away (`CarryBlame`) over their head; the camera stays on the group (`FailureView`) |
| CS07 | Accidental Hero | A mistake unexpectedly produces progress. | — |
| CS08 | Delayed Reveal | The consequence lands after everyone has mentally moved on. | `DecoyCheckpoint`: the cost arrives at the next death |
| CS09 | Overcorrection | The reaction to a mistake is funnier than the mistake. | both run to the `Seesaw`'s high end and it slams over |
| CS10 | Competing Plans | Two valid strategies run at once and get in each other's way. | cauldron carriers head for different routes, and the separation spills it |
| CS11 | Misplaced Confidence | A player acts with certainty on incomplete information. | "Saved!" at the `DecoyCheckpoint`, which banked nothing |
| CS12 | Unwanted Success | A troll move accidentally solves the goal and spoils the troll's payoff. | — |
| CS13 | Delayed Retaliation | A small betrayal sets up a fair revenge later. | 2P mutual swap: one mistimes the partner's jump now; the partner mistimes theirs back later |
| CS14 | Role Embarrassment | A player's assigned power contradicts how they play. | a `SwapGate` deal hands the rusher the careful player's jump |
| CS15 | Physical Exaggeration | A small input produces a big but bounded physical reaction. | `Ped_Yuksek`: one step, an 8 m throw; the ragdoll pops on death |
| CS16 | Social Misread | A necessary legal move is read as malice until it pays off. | the plate holder leaves to fetch the crate; the door shuts; "troll!" |
| CS17 | Chain Rescue | Each rescue creates a new person who needs rescuing. | — |
| CS18 | Premature Celebration | Players celebrate before the system has settled. | `LevelGoal`: everyone is inside, the cauldron is still outside the box |
| CS19 | Symmetric Disaster | Two players make the same sensible mistake from opposite sides. | `Pushable` shoved from both sides cancels exactly |
| CS20 | Mechanical Irony | The tool meant to fix a problem causes the next one. | a swapped air jump meant to save a fall flings the partner into spikes |

## EO — Escalation operators (12)

Apply these one at a time, and change only one operator per segment. Nothing on this list adds a key.

| ID | Operator | Existing Mixtrol knob (asset/field) or — |
|---|---|---|
| EO01 | Compress time windows before adding mechanics | `Chase_*` speed/warnTime (`Chase_Standart` 4 → `Chase_Bolum1` 5.5 m/s); `Crumble_Standart.crackTime`; `Door_Zamanli.autoCloseDelay`; `Platform_Hizli` (the last two are Gym-only) |
| EO02 | Increase distance between dependent players | plate↔door spacing (connect panel in `LevelEditorWindow`); `HeavyCauldron` stressSpan 2.4 / breakSpan 3.4 |
| EO03 | Add moving context around an unchanged interaction | `MovingPlatform` (`Platform_Mekik` / `Asansor` / `Hizli`); `ChasingHazard` |
| EO04 | Change which player owns the same action | `SwapGate`; `SwappedControls.channel` opening deal (Jump in every scene) |
| EO05 | Combine two learned systems | — layout only (Bölüm 2 pairs two devices per segment) |
| EO06 | Hide one visible fact, keep a communication path | `ColorTunnel` + `ColorTunnelSignalView` wall icon |
| EO07 | Make a resource shared instead of individual | `HeavyCauldron` fill (`fillThreshold` 0.5, gates nothing) |
| EO08 | Add a recoverable cost to a previously safe action | `Crumble_Standart` (restoreDelay 3); `HeavyCauldron.spillRate` 0.35 |
| EO09 | Require the same action while carrying | `HeavyCauldron` carry speed ×0.55; `CarryLoad` blocks jump/dash; `Crumble_Standart.carryWeight` |
| EO10 | Force sequential use where simultaneous was valid | `Crumble_Standart.crackTime` per unit of load; `PressurePlate.requireDistinctPlayers` |
| EO11 | Add a mild personal incentive against team convenience | — |
| EO12 | Static object becomes moving/expiring version | `Door_Basili` → `Door_Zamanli`; static block → `MovingPlatform`; floor → `CrumblingFloor` |

## AG — Anti-grief rules (8)

| ID | Rule | Mixtrol today |
|---|---|---|
| AG1 | No single player can stall required progress for good without a group counter-action. | Fail: R resets the team with no cooldown; opposite pushes stall `Pushable` (a withheld Space is an accepted exception, DA-13) |
| AG2 | Prefer timed, reversible or majority-held sabotage to irreversible destruction. | Fail (partial): plates and `CrumblingFloor` revert; `Door_Kilitli` latches; `Pushable` and crates never reset |
| AG3 | After repeated trolling, add a short immunity or cooldown; keep the mechanic. | Fail: `SwapGate`, R and partner-move spam have no cooldown or immunity |
| AG4 | Critical shared resources regenerate, relocate or have a fallback source. | Fail: the cauldron has no kill height; a checkpoint can bank it in a pit; crates never reset |
| AG5 | Host-authoritative interactions need a deterministic recovery after a disconnect. | Pass, bluntly: a disconnect ends the session and reloads the scene; the run is lost (GDD Kopma) |
| AG6 | A player isolated by failure must still have a meaningful task. | Pass by default: shared death isolates nobody; every tier-1 split lane must earn this again |
| AG7 | Long punishment walks kill comedy; recovery should start within seconds. | Fail: control returns in 0.7 s, but every death replays a segment; tier 1 barely exists |
| AG8 | Hidden sabotage must eventually reveal its cause, so blame turns social. | Fail: swap, tunnel, chase and crumble deaths name the victim; naming the causer (MIX-12) is not built |

## DC — Design checks (14)

| ID | Check | The question | A fail means |
|---|---|---|---|
| DC01 | One-sentence | Can a newcomer state the objective in one sentence? | The room hides its goal or is really two rooms; split it or cut it. |
| DC02 | Solo-solver | Can the best player ignore everyone and still solve it? | The dependency is decoration; add `requireDistinctPlayers` or make a swapped move necessary. |
| DC03 | Legal-troll | Can normal controls cause a meaningful, recoverable disruption? | No sabotage means no comedy; an unrecoverable disruption is a grief switch. |
| DC04 | Blame | After a failure, can players tell what caused it? | Arguments with no answer; add a cause tag (AG8). |
| DC05 | Recovery | Does failure hand back a decision within 3–8 s? | Dead air; make it tier 1 or shorten the tier-2 walk. |
| DC06 | Clip | Can a stranger read setup → action → consequence without explanation? | No shareable moment; the beat is corridor. |
| DC07 | Input-depth | Does one input serve several situations, rather than one bespoke use? | Pressure toward a new key; rebuild it from existing verbs. |
| DC08 | Dominant-strategy | Will one safe routine emerge that makes talking unnecessary? | The second run plays the same; add variance (`Reroll`, `SwapGate`). |
| DC09 | Voice | Does communication change outcomes, or merely decorate them? | Players go quiet; split the information between them. |
| DC10 | Grief | Can one hostile player lock the room indefinitely? | Add a group counter-action or a cooldown (AG1, AG3). |
| DC11 | Network | Does it need precise shared physics that lag will spoil? | Convert it to discrete state or widen the window past one round trip. |
| DC12 | Content-cost | Can the mechanic recombine across many rooms and assets? | Bespoke-room trap; make it a config asset. |
| DC13 | Escalation | Can difficulty rise without teaching another button? | It needs a key, which is ⛔ one-key-per-action; redesign it. |
| DC14 | Spectator | Is the key state legible to someone not playing? | A muted clip is unreadable; add an in-world cue. |
