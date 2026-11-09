---
name: coop-chaos-design
description: Deciding whether a proposed __GAME__ co-op mechanic ships — will it produce chaos, comedy and clips, can it be griefed, which failure tier it lands in — and where it belongs in the Core/Game split. Use when a specific mechanic or coupling is on the table and the question is "should we build this", "is this fun", "will this be funny", "how do I connect two players", "should they be chained / tethered / carry something together", "can a player ruin this for the other", how a mechanic scales from 2 to 4 players, or before writing any coupling code. Convergent gate — generating or mutating ideas is mechanic-forge.
---

> Written for Mixtrol (2–4 player 2.5D co-op platformer, FishNet over Unity Relay). Where this file states a
> Mixtrol fact (its keys, devices, levels, decisions), treat it as a worked example and use __GAME__'s own from
> DESIGN.md and CLAUDE.md instead.

# Does this mechanic ship?

Mixtrol is a **2–4 player 2.5D co-op platformer (a horizontal lane plus vertical towers) whose
primary coupling is the control swap**: Space plays the move you hold of your partner's (GDD "Ana
Mekanik — Hareket Takası"). The cauldron and the plates are the scenes the swap plays out in. Evidence is in
`docs/reference-teardowns.md`; the method is `docs/design-corpus/` (cite its items by ID); the game as
it stands against that method is `docs/design-audit.md`.

This skill is the gate. Ideas come from `mechanic-forge`; a card that reaches here either ships, ships
with a named weakness, or goes back.

## The thing that is easy to get wrong

Every breakout in the genre runs on **gravity as a loss engine**: a fall is instant, visible and
blameable. A horizontal lane does not get that for free (the vertical towers of Bölüm 2–3 do: there a
fall costs the climb). Mixtrol replaces it in two layers: the swap is the always-on floor that makes
every mistake somebody's key press, and on top of it a beat runs at most **one** loss engine (decided
2026-09-22) — on the lane the chase, in a tower the fall; the cauldron's spill was the other until
the user took the liquid out on 2026-09-28: a side mechanic must not reach into the run.
A proposal that makes failure **nobody's fault** has thrown away the loss engine — say so first.

## The gate

Run a card through these before any code is written.

| # | Test | Corpus | Fail means |
|---|---|---|---|
| 1 | **Muted clip** — sound off, within a second a stranger can tell what happened and whose fault it was | DC06, DC14 | Do not build |
| 2 | **Single machine** — at the moment of failure exactly one system demands attention | — | Do not build |
| 3 | **Attribution** — the failure points at a *player*, and the blame label names the cause, not the victim | DC04, AG8 | Do not build |
| 4 | **Solo solver** — the best player cannot finish it alone (crate, jump + air dash, solo push) | DC02 | Do not build: it is not co-op |
| 5 | **Grief** — no player can stall mandatory progress without a counter | DC10, AG1 | Do not build until a counter exists |
| 6 | **Recovery** — a tier-1 failure hands the group its next decision within 3–8 s | DC05, AG7 | Fix before building |
| 7 | **Network** — nothing needs two machines to agree inside 1 s | DC11, AP14 | Fix before building |
| 8 | **Legal troll** — a normal key at a bad moment can hurt a partner, recoverably | DC03, P32 | Builds, but carries less weight than claimed |
| 9 | **Zero explanation** — understandable from one screenshot | DC01 | Builds, but carries less weight than claimed |
| 10 | **Dominant strategy** — no safe routine deletes the need to talk by the third attempt | DC08 | Builds; give it an escalation (EO) |

State which rows a card fails, in the answer, even when it ships.

## Coupling: one primary, never stacked

| Type | Clip | 4 players | Netcode | In Mixtrol |
|---|---|---|---|---|
| **Control swap** | the wrong-moment press | ring scales untouched | low — input packets, host-owned table | **Primary, built** |
| Carried heavy object | the drag | good, with design | moderate — host solves, `NetworkTransform` | Secondary, built: the cauldron (weight only; a spilling or fragile load would be its own component, not the run's) |
| Mutual dependency | the betrayal | best | low | Secondary, built: plates, seesaw, pushable |
| Hard tether / chain | the yank | great | **high** | Out of scope (GDD) |
| Shared counter | the argument | weak | trivial | **Never primary** — fails attribution |

One multi-handle object per level; at 3–4 players it has one handle per player. "Soft tether" means a separation that is eased or costs something,
never a rigid constraint. The cauldron no longer charges for separation.

## Failure has two tiers (decided 2026-09-22)

- **Tier 1 — recovered in place.** A small mistake starts a rescue, not a restart: a comeback window
  (P66), a fallen player given a task (P62), a two-player reset (P67), the object relocated rather than
  deleted (P65), a slower route (P61). The next decision arrives within 3–8 s.
- **Tier 2 — terminal.** Death or the lost cauldron: shared death, one segment back, as the GDD has it.

A card names the tier of every failure in its chain. A mechanic whose only failure is tier 2 is a
hazard, not a co-op mechanic.

## Sabotage is legal; stalling is not

- Trolling through normal keys is the comedy (DESIGN.md). Keep it.
- **No indefinite stall without a counter** (AG1). Open holes live in `docs/design-audit.md`.
  **Accepted exception (DA-13):** a held swapped move may be kept forever — at 2 players an idle
  partner stalls just as well, and the dependency is the pillar.
- **At two players a majority is one against one.** Vote and group counters (P09, AG2) degenerate; the
  counters that work are **timed** (expires on its own) and **reversible** (the victim can undo it).
- **Make sabotage tactically legitimate** somewhere (P33) and give it a cost to the troll (P36), so the
  same act is sometimes the right move.
- **Reveal the cause** of hidden sabotage (AG8): if the partner's Space press killed you, the label names
  the partner.
- **No permanent loss** (AG4, AP15): nothing required can be deleted by one player.

## Forgiveness goes to the connection, not the individual

- **Do not raise coyote time or the jump buffer to absorb co-op chaos.** `coyoteTime` and
  `jumpBufferTime` in `Assets/__GAME__/Core/Data/PlayerMovement.asset` (both under 0.15 s) are right. Individual forgiveness makes players harder
  to blame. Above 0.15 s is a red flag — `game-feel` has the bands.
- **Put the forgiveness in the coupling:** the swap's visible ask-back before a partner presses. That window is co-op's coyote time. (The difficulty dial does not turn it —
  `level-beat-review` has the four knobs.)
- **Floor any grace window at 240 ms** — the perceive-decide-act loop — and at **≥ 1 s** where two
  machines must agree (decided 2026-09-22; ≈ 3 × the 150 ms preset's round trip).
- **Never forgive silently.** A save nobody saw teaches nothing; the near-miss is a clip too (FR09).

## Authority

Networking is built (FishNet host + client). A card must fit it, not the other way round.

- The world — table, cauldron, crate holder, plates, doors, floors, seesaw, checkpoints, deaths — is the
  **host's**. New world state goes through `NetworkMechanisms` (index into the hierarchy-ordered list)
  or a SyncVar, never a new `NetworkObject` without cause.
- Characters are their **owner's**. A partner's swapped move lands **one round trip late**
  (`NetworkInput`): never gate a beat on two machines agreeing inside 1 s.
- **Prefer a discrete state the host decides over shared physics** (RX13).
- Celebrate on the host-confirmed edge, not the local trigger (FX06).

## Where the code goes

`__GAME__.Core` is value types and static step functions taking `dt`; `__GAME__.Game` is Unity glue.
`MovementSolver.Step` solves **one character in isolation**.

- Coupling state is a **new Core value type + static solver**, mirroring `MovementState` /
  `MovementSolver`. Do not invent a second shape for the same problem.
- It takes carrier **positions** and returns displacement plus per-carrier force; it does not hold a
  reference to `MovementState`. If the design needs `MovementSolver` to know about *other characters*,
  it has drifted toward a hard tether — stop and say so.
- **Keep the edge-flag contract.** One-step flags reset at the top of every `Step` are the only channel
  from simulation to presentation.
- **Domain and scene reload are off.** Every mutable static needs a
  `[RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.SubsystemRegistration)]` reset.

## Anti-patterns

| Anti-pattern | Threshold |
|---|---|
| Two couplings load-bearing at once | More than one primary in a level |
| Blame on the victim | The label names who died for what the partner did (AG8) |
| Silent save | Any forgiveness the players do not see or hear |
| Hard grief switch | A stall with no timed or reversible counter (AP04) |
| Permanent resource loss | One player can delete a required item for the session (AP15) |
| Long reset for a small mistake | A tier-1 failure costs the segment (AP05) |
| Sabotage designed out | Nothing lets a player deliberately ruin a teammate's run |
