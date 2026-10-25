# Design corpus

The method Mixtrol's levels, mechanics, timing windows, feel, difficulty and replayability are designed
by, adopted by the user on 2026-09-22. It is a four-part reference on social-sabotage co-op design; this
folder holds the originals and our cited-by-ID catalogs of them. The game measured against it is
`docs/design-audit.md`.

## What is here

| File | Holds | IDs |
|---|---|---|
| `grammar.md` | Interaction patterns, failure chains, recovery types, comedy structures, escalation operators, anti-grief rules, design checks | P, FC, RC, CS, EO, AG, DC |
| `generator.md` | Mutation operators, the 60-object palette, seed pools, room archetypes, drills | OP, OB, CQ, RQ, RA, MD |
| `../../.claude/skills/mechanic-forge/` | The procedure: the mechanic card (17 corpus fields + 8 Mixtrol), Pass A–J, 13-axis rubric, protocol anti-patterns, recipes, worked chains | AP, WC, RX |
| `../../.claude/skills/game-feel/references/feedback-stack.md` | Feel rules, the eight-layer stack, feel patterns, per-action targets, feel anti-patterns | FR, FS, FP, FE, FX |
| `source/` | The four PDFs | — |

**Cite by ID.** Skills and docs name `P08`, `AG1`, `FP28` — they never restate a catalog row. That is
what keeps the copies from drifting. IDs are stable; a new entry gets the next number, a removed one
keeps its number and is marked retired.

`00_MASTER_social_sabotage_claude_corpus_v3_gamefeel.pdf` was the concatenation of 01–04 (word count
48 459 either way) and is not kept.

## Page index (Read a PDF with `pages`)

| PDF | Section | Pages |
|---|---|---|
| `01_social_sabotage_design_grammar_expanded.pdf` | Core model · P01–P70 | 1–8 |
| | FC01–FC30 · RC | 8–11 |
| | CS · EO · AG · DC | 11–13 |
| `02_mechanic_puzzle_idea_generator_expanded.pdf` | OP01–OP45 · the grammar | 1–3 |
| | The 240 seeds (formula-filled, not transcribed) | 3–59 |
| | RA01–RA36 · MD | 59–61 |
| `03_claude_game_design_reference_protocol_expanded.pdf` | System instruction · 17-field schema · Pass A–J | 1–2 |
| | 13-axis rubric · RX01–RX26 | 2–4 |
| | WC01–WC12 · AP01–AP15 · handoff · hard constraints | 4–6 |
| `04_game_feel_juiciness_research_supplement.pdf` | Evidence · FR01–FR15 | 1–4 |
| | FS · FP01–FP32 | 4–9 |
| | Haptics (out of scope) · FE01–FE20 · FX · checklist · bibliography | 9–13 |

## Which source wins

Rank by the kind of claim, not by the document:

| Claim | Wins | Because |
|---|---|---|
| A decision — what the game *is* | `docs/gdd.md` and user decisions in memory | The user's call; the corpus is a method, not a design |
| A fact — what the game *does* | Code and assets | Every doc here has been caught stale at least once |
| A method — how to generate, critique, mutate, dress | This corpus | Adopted 2026-09-22 for exactly this |
| Genre evidence — what sells, what the breakouts did | `reference-teardowns.md`, `market-2026.md` | Observed, not theorised |

The corpus changes a decision only through the user. Where it disagrees with one, the row goes in the
table below and the disagreement is raised, never resolved silently.

## Known conflicts

| Corpus says | Mixtrol says | Status |
|---|---|---|
| No long resets; next decision within seconds (AG7, AP05, DC05) | One segment lost per failure (GDD "Ucuz ceza") | **Resolved 2026-09-22: two tiers.** Tier 1 recovers in place within 3–8 s; tier 2 is shared death + one segment, returned by the 0.7 s collapse + teleport (no fade, no rewind) |
| Shared Limited Resource is a primary pattern (P21, RA13) | A shared counter is never the primary loss engine (coop playbook) | Open — the playbook's reason (a draining bar blames nobody) stands until a design beats it |
| Scripted jokes die after one play (AP01) | One-shot traps: decoy checkpoint, twin shuttle, bait crate (`bolum-01-beats.md` rule 1) | Open — keep at most one per level, and prefer traps whose outcome depends on who acts |
| Voice matters but must not be required (DC09, RX22) | Voice via Discord is assumed ("Sesli iletişim zorunlu") | Partly met — radio + antenna blink is the nonverbal fallback |
| Camera shake is not default feedback (FX02) | GDD "Ses ve his" lists shake as juice; the Feel recipes put it on routine verbs | **Resolved 2026-09-22: magnitude, not absence.** Routine verbs keep it small; rare events get the largest |
| Tether patterns (P42, RA21) | Hard chain and physics tether are out of scope | Soft logical coupling only (the cauldron's separation stress is one) |
| Hidden ownership (P12) | Ownership is always public on the antenna | Deliberate — the antenna is the readability pillar; hide *other* facts (P11: the tunnel) |
| Rooms assume 4 players | Content is built for 2; mechanics are 2–4 | Write beats as "at least two" / "everyone" (GDD rule) |
| Deterministic recovery after disconnect (AG5) | A disconnect ends the run; no host migration | Accepted by the GDD. At 3–4 players a leave with ≥ 2 remaining re-deals the leaver's moves and continues (decided 2026-09-22, not built) |
| Haptic layer, mobile lens | PC keyboard only, no gamepad | Out of scope (keyboard only; no gamepad planned) |
| No permanent stall; one-way delegation needs a reclaim path (AG1, P08) | A held swapped move is a wall (GDD "Zorunlu bağımlılık") | **Resolved 2026-09-22 (DA-13): accepted exception** — at 2 players an idle partner stalls anyway |

## Mixtrol deltas — read these before applying any corpus item

- **Inputs.** The corpus's "move, jump, crouch, dash, grab" is Mixtrol's A/D, W, Ctrl, Shift and E, plus
  Space, which plays the move you hold of your partner's. One key per action, no alternates, **no new
  keys** — every "no new input" rule in the corpus is already a repo rule.
- **Players.** Mechanics are 2–4, content is 2. With two players a "majority" is one against one, so a
  group or vote counter-action (AG1, AG2, P09) degenerates. **Timed or reversible counters are the only
  class that works at 2**; design those first.
- **Communication.** Discord is assumed. The one-word channel (P17) already exists: the radio ask-back
  lights exactly one antenna. Any new call must fit in under three seconds (RX14).
- **Failure.** Two tiers, above. Tier-1 devices are RC01–RC12 and P61–P70; tier 2 is the existing
  shared death.
- **Authority.** World state is host-authoritative (`NetworkMechanisms`, SyncVars); characters are
  client-authoritative; a swapped move lands one round trip late. Any shared timing window must survive
  that — see `game-feel/references/numbers.md` §11. Prefer discrete state over shared physics (RX13).
- **Feel.** Keyboard only: the haptic rules (FR12, the mobile layer) translate to "audio is the scarce
  channel".
- **Coupling.** Control swap is the primary coupling (GDD). The cauldron and the plates are the scenes
  it plays out in. One multi-handle object per level.

## How the skills use this

| Task | Skill | Reads |
|---|---|---|
| Invent, mutate, critique a mechanic or room | `mechanic-forge` | `grammar.md`, `generator.md`, its own `references/recipes.md` |
| Decide whether a shape ships and where its code goes | `coop-chaos-design` | DC, AG, P rows by ID |
| Lay out or review a level | `level-beat-review` | RA, EO, RC, DC rows by ID |
| Pick how an action feels | `game-feel` | `references/feedback-stack.md` |

Grep by ID across both homes (`rg "^\| P08 " docs/design-corpus .claude/skills`); do not load whole
catalogs. `mechanic-forge` has a "where to start" table for when you have no ID yet.
