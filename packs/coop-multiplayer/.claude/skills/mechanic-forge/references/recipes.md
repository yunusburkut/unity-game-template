# Recipes, worked chains and two __GAME__ cards

The protocol's recipe library (03, pages 2–4) rewritten for Mixtrol. Every recipe runs inside the
four passes in `SKILL.md` and ends in cards, not a list. The corpus defaults ("4 players; move, jump,
crouch, dash, grab") become Mixtrol's fixed set: 2–4 players with 2-player content; A/D, W, Space,
S (crouch), Shift, E.

## Contents

- RX — Recipes
- WC — Worked transformation chains (corpus examples)
- Worked Mixtrol card 1 — Telsizle geri alma (reclaim)
- Worked Mixtrol card 2 — Kazan çukurda kaybolmaz (tool displacement)

## RX — Recipes

| ID | Recipe | Produce | Mixtrol constraint |
|---|---|---|---|
| RX01 | Generate room ideas | N segment concepts, each using exactly two P patterns, one OP and one RC | Buildable from existing prefabs in one day; beats written "at least two" |
| RX02 | Mutate one mechanic | Variants changing one dimension each: ownership, information, timing, resource, space, physics, incentive, recovery | Same keys; the swap table is the cheapest ownership lever |
| RX03 | Make it more social | A rewrite the best player cannot finish alone, plus one information asymmetry and one recoverable sabotage | Kill every crate / jump + air dash / solo-push bypass first |
| RX04 | Reduce complexity | Delete rules one at a time until the funniest outcome breaks; keep the last set that worked | Also count replicated states — fewer SyncVars wins |
| RX05 | Find clip moments | Accidental failure, deliberate troll, accidental hero — cause → reaction → consequence → recovery, each 5–10 s | Must read muted, with the antenna and blame label as the only text |
| RX06 | Anti-grief pass | Every indefinite stall, each replaced by a timed, reversible or group-counterable state | At 2 players only timed/reversible counters work. The swap table's held move is exempt (DA-13) |
| RX07 | Network pass | Authoritative state, owner-predicted parts, reconciliation, physics risks | Host owns the world; a swapped move is one round trip late; cross-machine windows ≥ 1 s |
| RX08 | Low-cost prototype | Fewer rigidbodies, networked transforms, unique assets, scripted sequences | Prefer a `NetworkMechanisms` entry over a new `NetworkObject` |
| RX09 | Teaching sequence | Six segments: safe teach → dependency → sabotage → combination → recovery chaos → mastery finale | Never introduce a device for the first time under a chase |
| RX10 | Mechanic autopsy | Why it dies after ten minutes: dominant strategy, communication collapse, solved state, repetition, grief, no escalation | Fix only the failure modes that are actually present |
| RX11 | 2/3/4-player adaptation | The same core rule at 2, 3 and 4 players, no bespoke exceptions | The swap ring already scales; plates use `requiredCount` / `requireDistinctPlayers` |
| RX12 | No-new-input escalation | Ten harder variants with no key, ability or UI screen added | Use EO01–EO12; existing knobs: chase speed, door type, gate density |
| RX13 | Physics-to-state rewrite | Fragile shared physics replaced by discrete state/events | Keep the player-caused chaos; host decides the discrete state |
| RX14 | Information compression | Every critical fact callable in under 3 s | One word or one antenna blink |
| RX15 | Recovery-first rewrite | Start from the funniest failure state, design backward to the normal interaction | Name its tier first |
| RX16 | Sabotage legitimacy | Make the troll action tactically useful somewhere (P33) | Wrong-moment Space press should sometimes be the right move |
| RX17 | Spectator readability | Feedback that shows actor, action, victim, consequence, recovery without prior rules | Seat colour is the actor; see feedback-stack FP11/FP27 |
| RX18 | Dominant-strategy breaker | Find the safest repeatable routine; change one relationship so talking matters again | Typical routine today: park the cauldron, solve, carry on |
| RX19 | Object affordance brainstorm | One OB object, many interactions by mutating ownership, information, timing, cost | Before any fantasy power |
| RX20 | Room recombination | Two learned devices, both rules intact; novelty only from their interaction | Bölüm 2 is built this way |
| RX21 | Fail-forward only | Five failure outcomes with zero full-segment restarts | Tier-1 design drill |
| RX22 | Voice-chat dependency | Voice valuable but not required; define the nonverbal fallback | Radio ask-back is the fallback; no chat key |
| RX23 | Streamer clip filter | Reject ideas whose best moment needs more than 10 s of explanation | Store line test: "your jump is on their keyboard" |
| RX24 | Content leverage pass | Turn a set-piece gimmick into a device usable in five spatial contexts | A new config of an existing solver beats a new solver |
| RX25 | Prototype kill test | The cheapest falsifying experiment and the behaviour that proves it weak | A Gym zone from existing prefabs |
| RX26 | Implementation handoff | State machine, data model, events, authority, feedback, pooling, tests, kill criteria | Config→Tuning→State→Solver; see SKILL.md "Handoff" |

## WC — Worked transformation chains (corpus examples)

Read these for the *shape* of a transformation, not the content. The lesson column is what transfers.

| ID | Chain | Moves it makes | Lesson for Mixtrol |
|---|---|---|---|
| WC01 | Shared Crate | Split control per side, one player sees tilt, release swings it, cracked crate leaks parts | The cauldron could leak collectable fill instead of losing it (P68) |
| WC02 | Rope Bridge | Operator holds tension, cutting drops a lane but raises a counterweight | Fallen players land where they can restore the route (P62) |
| WC03 | Elevator Debt | Power-holder is rooted; the last rider steals floor control | A plate holder deserves a return path (P27 risk) |
| WC04 | Laser Relay | Aim vs timing split; missed pulse echoes later | Delayed echoes create accidental heroes (P05, CS07) |
| WC05 | Balloon Lift | Shared centre of mass; overheat; popped balloon becomes a parachute | Failure mutates the object into a new tool (P63, P64) |
| WC06 | Minecart Priority | Steer/brake/switch owned by different players, rotating per checkpoint | Rotate the swap deal at checkpoints (P02) |
| WC07 | Flashlight Map | Light-holder vs map-holder; handing the light is one-way; darkness leaves footprints | One-way handoff needs a reclaim path (P08) — except the swap table's held move, which may be kept forever (DA-13) |
| WC08 | Bomb Door | Carrier opens gates while the timer runs; explosion stuns and breaks a wall | Terminal-looking events can open shortcuts (P33) |
| WC09 | Raft Balance | Strong steerer vs fine-tuners; anchor spins the raft around rocks | Sabotage with benefit (P33) |
| WC10 | Portal Ownership | Contact transfers the portal; rotation applies two seconds late | Collision ownership with a lockout (P47) |
| WC11 | Magnet Polarity | Charging one weakens the other; overcharge makes a wall platform | Overshoot becomes a platform (P64) |
| WC12 | Spool Tether | One reels, one locks; lock expires; snap splits into two grapples | A broken coupling can split into two routes (P69) |

## Worked Mixtrol card 1 — Telsizle geri alma (reclaim)

*Example of the card format only. **Rejected 2026-09-22 (DA-13):** the user kept the GDD rule
"Space'i basmayan ortak geçilemeyen bir duvardır" — do not re-propose without new evidence from 3–4-player play.*

1. **Name** Telsizle geri alma · 2. **Fantasy** "Fine, I'll do it myself." · 3. **Affordance** the radio
ask-back already exists · 4. **Core action** hold your own key for a move you have given away ·
5. **Goal** get your move back when the holder will not play it · 6. **Constraint** it takes time and
the holder sees it coming · 7. **Dependency** during the countdown the holder can still play it — or
play it at the worst moment · 8. **Sabotage** the holder plays the move exactly as the countdown ends ·
9. **Information** the antenna blink grows into a visible fill; both players see it · 10. **State** a
per-seat reclaim timer on the host; the table itself changes only on completion · 11. **Failure chain**
holder ignores → owner holds W → blink fills → holder jumps them into spikes at 90 % → shared death,
blame to the holder · 12. **Recovery** the move returns for a short window, then the deal restores
(control debt, P06) · 13. **Escalation** shorter windows, gates that re-deal mid-countdown (EO01, EO04) ·
14. **Clip** "I'll do it myself" — fill — partner jumps you into the pit at the last frame ·
15. **Anti-grief** closes AG1's worst hole: a withheld move is no longer a wall · 16. **Network** host
counts held seconds from the input packets already sent; one table write at the end ·
17. **Prototype** one Gym zone: a pit that needs a jump, table dealt with Jump swapped
18. **IDs** P06, P08, P17, AG1, CS13 · 19. **Tier** 1 (reclaim), 2 (the death in the chain) · 20. **Owner**
host, beside the swap table in `NetworkSwap` · 21. **Edge flags** `ReclaimStarted`, `Reclaimed`,
`ReclaimExpired` · 22. **Config** the swap view's config asset (reclaim seconds, window seconds) ·
23. **2/3/4** the same rule per seat; in a ring the reclaimer takes it from whoever holds it ·
24. **Reuses** `ControlSwap.Asked`, `ControlSwapView` blink, `NetworkSwap` · 25. **Kill test** if pairs
reclaim instead of talking, the swap stops producing arguments — cut or lengthen it

## Worked Mixtrol card 2 — Kazan çukurda kaybolmaz (tool displacement)

*Example of the card format only: fill and spill were removed from the game.*

1. **Name** Kazan kenara döner · 2. **Fantasy** the cauldron is heavy but not gone · 3. **Affordance**
a carried pot that spills · 4. **Core action** carry with E; nothing new · 5. **Goal** a cauldron that
leaves the lane is not lost for the session · 6. **Constraint** coming back costs fill and time ·
7. **Dependency** it returns to the last ground the carriers stood on, which both must reach again ·
8. **Sabotage** letting go over a gap — still legal, now it costs rather than ruins · 9. **Information**
the return is visible (it rises or slides back, not teleports) · 10. **State** host: last grounded
position + fill · 11. **Failure chain** carrier drops early → cauldron falls → returns to the ledge with
a spill → blame to whoever let go → pair walks back · 12. **Recovery** RC07 tool relocation instead of a
death · 13. **Escalation** gaps under moving platforms (EO03) · 14. **Clip** "You dropped it." — it
comes back half empty · 15. **Anti-grief** AP15/AG4: no required item can be lost by one player ·
16. **Network** host decides the fall and the return; clients see the `NetworkTransform` ·
17. **Prototype** one Gym gap zone
18. **IDs** P65, RC07, AG4, CS06 · 19. **Tier** 1 · 20. **Owner** host, in `CoCarriedObject` ·
21. **Edge flags** `Lost`, `Returned` · 22. **Config** `CarriedObjectConfig` (return delay, fill cost,
kill height) · 23. **2/3/4** unchanged · 24. **Reuses** `CoCarriedObject.RestoreTo`, `CarryBlame` ·
25. **Kill test** if groups start throwing it into pits as a shortcut, raise the fill cost
