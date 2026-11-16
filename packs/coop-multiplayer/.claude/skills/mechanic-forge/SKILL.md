---
name: mechanic-forge
description: A __GAME__ co-op mechanic, room, segment card through design corpus. Use for "mutate this", "mutasyon yap", "make it more social", "daha sosyal yap", "nasıl trollenir", "harder without new keys", "3-4 players". Batches: idea-forge.
---

<!-- The full trigger set, kept here because the listing budget caps the description at 250 characters: generating,
mutating and critiquing co-op mechanics, devices, rooms and segments with docs/design-corpus (the 25-field card,
Pass A-J, the 13-axis rubric, the recipe modes, tier-1 recovery design "make this failure recoverable in place");
"what else can the swap / cauldron / plate do", "how can this be trolled", "boring after ten minutes", "recoverable", "this feels flat", "make it work for 3-4 players", "find the clip
moments", "anti-grief pass", "what would kill this idea", before handing a mechanic to implementation. A batch of N
ideas in its own context is the idea-forge agent; the go/no-go gate is coop-chaos-design. -->

**Mode split.** This skill works one card (or a small set) in the main conversation. "Give me N ideas" as a batch
goes to the `idea-forge` agent, which runs this same procedure in its own context. Whether a card ships is
`coop-chaos-design`, never this skill and never the generic `design-critic`.

> Written for Mixtrol (2–4 player 2.5D co-op platformer, FishNet over Unity Relay). Where this file states a
> Mixtrol fact (its keys, devices, levels, decisions), treat it as a worked example and use __GAME__'s own from
> DESIGN.md and CLAUDE.md instead.

# Forging a __GAME__ mechanic

The corpus in `docs/design-corpus/` is the method; this skill is how to run it. Read the README there
once for the ID scheme, the precedence rule and the Mixtrol deltas (the reference game). Never load a whole catalog — grep
rows. IDs live in three places, so search all of them with the Grep tool (not a shell `rg`, which is not on
PATH here):

- One row by ID: pattern `^(\| |- \*\*|\d+\. \*\*)OP27\b` over `docs/design-corpus` and `.claude/skills`
  (MD rows are a numbered list, most others table rows).
- Candidates by keyword when you have no ID yet: pattern `^\| (P|RC|RA)\d+ .*recover`, case-insensitive, over
  `docs/design-corpus`.
- FR, FS, FP and FX rows are in the gamekit plugin: load the `gamekit:game-feel` skill and read its
  `references/feedback-stack.md` (section 2 FR, 3 FS, 4 FP, 6 FX). FE01–FE20 are retired: that section became
  "Per-action target (fill in per game)", so cite the action's row there instead.

Rows: P, FC, RC, CS, EO, AG, DC in `grammar.md`; OP, OB, CQ, RQ, RA, MD in `generator.md`; FR, FS, FP, FX in
`gamekit:game-feel`'s `references/feedback-stack.md`; AP here; RX, WC in `references/recipes.md`.

**Where to start when you have no ID:**

| Request | Start with |
|---|---|
| A recovery, "make this tier 1" | RC01–RC12, P61–P70, RX15, RX21 |
| More dependency, "too easy alone" | P01–P10, P31–P43, RX03 |
| Information / talking | P11–P20, RX14, RX22 |
| Sabotage and griefing | P31–P40, AG1–AG8, RX06, RX16 |
| Harder, no new keys | EO01–EO12, RX12 |
| A new device | OB01–OB60 with one OP, RX19 |
| A room or segment | RA01–RA36, RX01, RX09, RX20 |

**Never answer with a bare list of ideas.** Every request runs four passes: design (Pass A–J, with a
light Pass J cut) → critique (the rubric) → simplification (the full Pass J cut) → production (the card
and the kill test). A list of twenty names is the shallow-novelty failure the corpus was written
against. Produce at least two candidates through the passes so the rubric has something to compare.

**If a candidate contradicts a recorded decision** (a DESIGN.md rule, the two-tier split as written, one key
per action), do not resolve it: carry on, and end the answer with a "Decisions for the user" list.

## What is fixed before any idea

- **Keys:** the fixed set in `docs/design-corpus/README.md` (Mixtrol deltas, Inputs; Mixtrol's is A/D,
  W, S, Shift, E, R and Space), replaced by __GAME__'s once DESIGN.md records them. No new
  key, no alternate, no hold-to-X that changes an existing key's meaning without the user's say.
- **Players:** mechanics work for 2–4 without bespoke exceptions; content is built for 2. Write "at least
  two" or "everyone", never "exactly two".
- **Coupling:** the primary coupling DESIGN.md records. Mixtrol's: control swap is primary (its GDD), one
  multi-handle carried object per level, at 3–4 players one handle per player.
- **Failure:** two tiers — tier 1 recovers in place, next decision within 3–8 s; tier 2 is shared death
  + one segment back. A new mechanic must say which tier each of its failures lands in.
- **Authority:** the split in CLAUDE.md's Networking section (default: world state is the host's, a character is
  its owner's). Mixtrol's world state lived in `NetworkMechanisms` or a SyncVar, and a swapped move landed one round
  trip late.
- **Scope:** no new package without asking; the rest is DESIGN.md's out-of-scope list. Mixtrol's: no procedural
  levels, no hard tether, no gamepad.

## Pass A–J

| Pass | Question | Reject in Mixtrol when |
|---|---|---|
| A Affordance | Which familiar object (OB) and what does it already promise? | It needs a new verb or key |
| B Dependency | Why can the best player not do it alone? | A crate, a jump + air dash or a solo push at ×0.3 solves it (DC02) |
| C Mutation | Change exactly **one** of ownership, information, timing, resource, position, cost (OP) | Two changed at once. The swap table is the native ownership axis — use it before inventing another |
| D Sabotage | One legal action with existing keys that can hurt locally | The harm is permanent, or needs a key the saboteur does not have |
| E Readability | Who caused it, and can the screen say so (FP11, FP27, the game's blame label if it has one; Mixtrol's was `Blame` / `BlameBoard` in `Core/Level/Blame.cs`)? | The blame label would name the victim for the partner's act (P37 without AG8) |
| F Recovery | Fail-forward, rescue, role inversion, mutation (RC, P61–P70) | The only recovery is death, or tier 1 takes longer than 8 s |
| G Escalation | Harder through timing, distance, combination, owner (EO) | It adds a key, a UI screen or a second loss engine — the primary coupling is the floor, and a beat carries at most one loss engine on top (Mixtrol's floor was the swap, its loss engine the chase) |
| H Clip | Accidental failure, deliberate troll, accidental hero — each 5–10 s | Any of the three needs narration to follow (RX23) |
| I Anti-grief | Every indefinite stall a hostile player can create (AG1–AG8) | A stall has no counter. With two players only a timed or reversible counter counts |
| J Production cut | Delete rules before adding systems; fewest replicated states | A rule can go and the funny outcome survives — then it goes |

## The mechanic card

Every idea that survives the rubric is written as this card. The first seventeen fields are the corpus
schema; the last eight are Mixtrol's.

1. **Name** · 2. **Fantasy** · 3. **Base affordance** · 4. **Core action** (keys, from the fixed set) ·
5. **Shared goal** (one sentence, DC01) · 6. **Constraint** · 7. **Dependency** · 8. **Sabotage vector** ·
9. **Information model** (who knows what, when) · 10. **Authoritative state** (the smallest state that
decides the outcome) · 11. **Failure chain** (3–6 causal steps, FC shape) · 12. **Recovery** ·
13. **Escalation** (EO, no new key) · 14. **Clip moment** (setup → action → consequence → recovery,
5–10 s) · 15. **Anti-grief rule** · 16. **Network note** · 17. **Prototype scope** (one-day test)
18. **IDs** — P / OP / RC / CS it instantiates
19. **Failure tier** per failure in field 11
20. **Host-state owner** — `NetworkMechanisms` index, SyncVar, or owner-local, and why
21. **Edge flags** — the one-step events presentation reads (the `MovementSolver` contract)
22. **Config asset** — the ScriptableObject its tunables live in (Turkish Header/Tooltip)
23. **2 / 3 / 4 players** — the same rule at each count
24. **Devices reused** — existing prefabs it leans on
25. **Kill test** — see below

## Critique: thirteen axes, never one score

Rate each axis **Strong / OK / Weak**, separately; name the **weakest**, then propose one change that
lifts it **without a new input**. Collapsing the rubric into a total hides exactly the axis that kills
the idea.

| Axis | Fails when *(starting thresholds — tune in Play Mode, write results back here)* |
|---|---|
| Clarity | A new player cannot predict the local effect of their own key |
| Dependency | The best player finishes it alone (DC02) |
| Agency | The outcome is dice the players cannot plan around (AP08) |
| Sabotage quality | Trolling needs a special action rather than a normal one at a bad moment |
| Recoverability | The next decision after a tier-1 failure comes later than 8 s (DC05) |
| Emergence | The same rules produce the same story twice |
| Voice relevance | Talking changes nothing, or a critical fact takes more than 3 s to say (DC09) |
| Clip readability | Muted, a stranger cannot name actor, victim and cause in 5–10 s (DC14) |
| Depth per input | The key it uses has only this one use |
| Anti-grief | One player can stall mandatory progress with no counter inside ~10 s (AG1) |
| Network robustness | Success needs two machines to agree inside 1 s (≈ 3 × the 150 ms preset's ~300 ms round trip) (AP14) |
| Content leverage | It cannot appear in five different spatial contexts (RX24) |
| Production cost | It cannot be prototyped in a day from existing prefabs |

## Modes

The 26 corpus recipes, rewritten for Mixtrol's keys, are `references/recipes.md` (RX01–RX26), with two
worked cards. Match the request to a mode and follow it: "ideas for a room" → RX01, "mutate" → RX02,
"too easy alone" → RX03, "too complicated" → RX04, "boring after ten minutes" → RX10, "harder without
keys" → RX12, "3–4 players" → RX11, "clips" → RX05/RX23, "trolls" → RX06/RX16, "make this failure
recoverable" → RX15 + RX21, "ready to build" → RX26.

## Kill test

State the cheapest experiment that could prove the idea weak, **before** building it: a zone in the game's gym or
test scene, built from existing prefabs (if there is none yet, a scratch scene; Mixtrol's was `Assets/Scenes/Gym.unity`,
zones 200 m apart, reached from its zone bar), and the observed
behaviour that kills it. Typical killers: a stranger pair solves it without speaking; one player idles
more than ~10 s; a troll stall has no answer; nobody laughs on the third attempt; the blame label names
the wrong player. If no cheap test exists, the idea is too big — Pass J it.

## Handoff

When the card survives, convert it without changing its intent (RX26): states and transitions → a Core
value-type `State` + static `Solver` taking `dt`; tunables → a Config ScriptableObject flattened to a
`Tuning` struct; authority → field 20; events → field 21, reset at the top of `Step`; presentation →
the action's row in `gamekit:game-feel`'s `references/feedback-stack.md`; reset guarantees → what
respawn restores (the game's own list; Mixtrol's: players, the cauldron, and the crates and push blocks a
`CarryHome` holds — never one on a plate); network edge cases → simultaneous input, one-trip lag, disconnect. Then
`gamekit:unity-architecture` for placement and `gamekit:unity-performance` for anything per frame. Tests only if the
user asks (`gamekit:unity-testing`).

**Then, in order:** `coop-chaos-design` decides whether it ships → `gamekit:level-beat-review` places it →
`gamekit:game-feel` picks how it reads → `gamekit:feel-authoring` wires it.

## Anti-patterns

The protocol's catalog, with the Mixtrol threshold that trips each.

| ID | Anti-pattern | Trips when |
|---|---|---|
| AP01 | Scripted joke | The funny outcome is the same every play regardless of who acts |
| AP02 | Hidden-rule gotcha | The rule is first learned by dying (DESIGN.md) |
| AP03 | One-player dominance | A crate, a solo push or a jump + air dash replaces the partner |
| AP04 | Hard grief switch | A stall with no counter (today: R spam, SwapGate spam; the withheld swapped move is an accepted exception, DA-13) |
| AP05 | Long reset punishment | A tier-1 mistake costs the segment |
| AP06 | Button inflation | The fix is a new key or ability |
| AP07 | Physics soup | Outcome depends on unstable simulation, not intent |
| AP08 | Randomness without inference | A failed group cannot form a better plan |
| AP09 | Information overload | A call takes more than 3 s to say |
| AP10 | Bespoke-room trap | The device works in one set piece only |
| AP11 | Fake choice | One option is always right once found |
| AP12 | Spectator opacity | Players understand it; a muted viewer does not |
| AP13 | Punitive asymmetry | One failed player idles while the other plays |
| AP14 | Network-hostile precision | Two machines must agree inside 1 s |
| AP15 | Permanent resource loss | A troll can delete the only required item (crate or cauldron in a pit) |

Hard constraints from the protocol, all binding here: humour emerges from action and system, never from
prose; hidden information must be inferable or callable; no long resets as punishment; nobody can
permanently lock mandatory progress; no buttons added to rescue a weak idea; prefer discrete state over
shared physics; prefer one surprising interaction between simple systems over one bespoke system; teach
through affordance and feedback before a tutorial line.
