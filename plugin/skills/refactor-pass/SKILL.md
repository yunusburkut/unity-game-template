---
name: refactor-pass
description: Periodic behaviour-preserving clean-up of code recently added to the game — SOLID (above all open-closed) in this repo's Core/Game idiom, Unity 6 best practices, caching and allocation-free hot paths, readability, maintainability, and frame-time headroom on low-end PCs and low/mid Android phones. Use whenever the user asks to refactor, tidy, clean up, polish, simplify, optimise or "go over what we added lately", asks to make code more readable / maintainable / extensible / SOLID / OCP, asks whether the game will run on a weak PC, a laptop GPU or a cheap phone, or invokes the pass with no argument at all. Also use when a feature is finished and the user wants it "settled" before moving on. Not for pure review with no edits (unity-code-review), not for adding features, not for gameplay tuning.
---

# Refactor pass

The pass exists so that every system added in a hurry ends up looking like the systems that were
built carefully. It changes shape, never behaviour: same inputs give the same outputs, in the same
frame order, from the same serialized data, with the same Inspector wiring. Anything else — a bug
fix, a tuning change, a new seam nobody needs yet — is a separate conversation with the user.

Read this file, then pull in the reference that matches what you find. Do not re-derive
`unity-architecture`, `unity-performance` or `unity-code-review`; they are the base rules, this
skill is the procedure that applies them repeatedly to fresh code.

| Reference | Read it when |
|---|---|
| `references/refactor-catalog.md` | Before the first edit. Allowed transformations, the Unity traps in each, the risk ladder, the verification protocol. |
| `references/solid-in-core-game.md` | Any structural change: a seam, an interface, a duplicated rule, "how would a second variant of this arrive". |
| `references/caching-and-hot-paths.md` | Anything reached per frame or per trigger; anything that looks up, formats or allocates. |
| `references/low-end-devices.md` | The user mentions weak PCs, laptops, integrated GPUs, cheap or old phones, heat, battery, frame drops, stutter, quality settings — or the pass reaches the render/quality assets. |

## Scope

Default scope is **what changed since the last pass**. The ledger `docs/refactor-pass-log.md`
holds `last-pass: <sha>` on its first lines; the survey script reads it. The ledger does not exist
until the first pass: create it at the end of that pass (format in the catalog, section 7). With no
ledger the script falls back to the last 15 commits.

```bash
bash ~/.claude/skills/refactor-pass/scripts/survey.sh            # since last pass
bash ~/.claude/skills/refactor-pass/scripts/survey.sh HEAD~8     # explicit ref
bash ~/.claude/skills/refactor-pass/scripts/survey.sh --all      # whole tree
bash ~/.claude/skills/refactor-pass/scripts/survey.sh --editor   # also smell-grep Editor (any mode)
```

It prints the commits and `.cs` files in scope (committed, uncommitted and untracked), the
execution-order pipeline, mutable statics, platform branches, and a list of per-frame smell hits
with line numbers. Treat the hits as questions, not verdicts — the script cannot tell `Awake` from
`Update`.

A user argument narrows or widens this: a folder (`Game/Level`), a topic (`perf`, `solid`,
`low-end`, `mobile`), or a range. Vendored trees (`Assets/Feel`, `Assets/Plugins`, any Asset Store
folder) are never in scope. `Assets/<Game>/Editor` is in scope for readability only — it never
ships, so it gets no performance work.

## The pass

### 1. Read everything in scope, plus its other half

For a `Game` MonoBehaviour that means its Core solver, state, tuning and config; for a Core type
it means every Game caller and the EditMode test that pins it. Then read the ledger's *Noted between
passes* and *Accepted trade-offs* sections, if the ledger exists, so you do not re-open a decision
the user already made.

While reading, write down for each type: who owns its state, who reads it, where it sits in the
`[DefaultExecutionOrder]` chain, and which of its members a scene or asset depends on
(serialized fields, animator parameter names, `InputAction` names, player-facing strings).

### 2. Triage with the rubric

| Looking for | Question | If yes |
|---|---|---|
| Bug | Would a player notice this? Does a test contradict it? | Report it separately. Do not fix it inside the pass — a fix is a behaviour change and the user decides. |
| Duplication | Is the same rule written in two places, or the same reset done by two paths? | One home, callers converge. Prefer the copy that already has the comment explaining why. |
| Hidden per-frame cost | A lookup, walk, format or allocation inside anything reached per frame? | `caching-and-hot-paths.md`. Fix by construction (cache in `Awake`, preallocate, last-value gate). |
| Closed to extension | Would the next variant of this mechanic require editing a switch, a manager or a solver? | `solid-in-core-game.md`. Open a seam only if the second variant is real. Otherwise leave a one-line note in the ledger. |
| Unreadable | Would a new teammate need the author to explain the *why*? | Rename, extract, or comment the intent. Never comment the line below. |
| Boundary drift | Unity scene API in `<Game>.Core`, or a gameplay rule inside a MonoBehaviour? | Move it, keeping the `static Step(ref state, in tuning, dt)` shape. |
| Lifecycle | `OnEnable` without `OnDisable`, a mutable `static` without its `SubsystemRegistration` reset, `Awake` reading another object's `Awake` result? | Fix — these are shape defects with no behaviour on a correct first run, and a break on the second Play. |
| Platform gap | Gameplay reading `Mouse.current` / `Touchscreen.current`, a rule branching on `#if UNITY_ANDROID`, hover-only UI, a save only in `OnApplicationQuit`? | Report it as a bug (it is one on the other target); `platform-targets` has the fix. |
| Low-end headroom | Render or quality settings that a laptop iGPU or a mid-range phone will not carry? | `low-end-devices.md`. Produce a checklist; asset edits go through `unity-editor-cli`, never by hand while the Editor runs. |

### 3. Plan before editing

Write the plan as a numbered list, each item tagged with its risk from the catalog's ladder:

- **green** — rename, extract, inline, dedupe, cache, reorder members, comments. Do it.
- **amber** — touches a serialized field, a lifecycle method, an event subscription, a public
  member another type reads. Do it with its safety step (`[FormerlySerializedAs]`, a paired
  `OnDisable`, a grep of the callers) and say so in the report.
- **red** — solver arithmetic, execution order values, the `SimulationStep.Max` clamp, enum
  ordinals, tuning defaults, anything the EditMode suite pins. Do not do it. List it with the
  reason and let the user pick.

Keep a pass to about six changes. A pass that rewrites twenty things cannot be verified by reading
its diff, and reading the diff is the primary verification here.

### 4. Apply one item at a time

Edit, then check `Logs/agent/compile.log` for a fresh `OK` (Unity only compiles when its window
has focus — see `unity-editor-cli` to force it). A change that does not compile is undone, not
patched forward. Keep unrelated items out of the same edit so each one can be reverted alone.

Do not commit unless the user asks. When they do, one commit per refactor kind: a title line, then
the *why*, ending with the sentence "No behaviour change; verified by …".

### 5. Verify proportionally

1. Read the whole diff against the catalog's checklist: flags still cleared at the top of every
   step, no early `return` skipping a reset, every renamed serialized field carrying its old name,
   no `in` parameter whose struct gained a non-`readonly` member.
2. `compile.log` says `OK`, and `console.log` shows no new warning.
3. If Core was touched, ask once — one sentence — whether to run the EditMode suite this pass. A
   solver refactor is the case `unity-testing` allows; do not run it unasked.
4. Hand the user the Play Mode list from `implementation-verification`: concrete actions and what
   must look identical to before, on PC and, if input, UI or rendering moved, on a phone.

### 6. Report and record

Report in the language the user is writing in. Structure:

1. **Changed** — one line per item: file, what, why, risk tag.
2. **Not changed (red)** — what you would change with permission and what it risks.
3. **Bugs seen** — separate from refactors, with a repro or a test that would show it.
4. **Low-end checklist** — only if the pass touched or was asked about rendering; Inspector
   steps the user performs, with the current value and the proposed one, per quality tier.
5. **Play Mode check** — five lines at most.

Then update `docs/refactor-pass-log.md` (create it on the first pass): move `last-pass` to `HEAD`,
add a dated section with the same five headings, and append anything the user explicitly accepted
as a trade-off to *Accepted trade-offs* so the next pass stays quiet about it.

## Guardrails

- **The solver stays whole.** A long `Step` is often one continuous argument; splitting it into
  strategies or phases adds calls, hides order dependencies and costs determinism. Extract a static
  helper only when the same expression appears twice.
- **No new abstractions without a second concrete case in hand.** Interfaces with one
  implementation, base MonoBehaviours with virtual `Update`, managers, service locators, event
  buses and DI containers are all "ask first" (see CLAUDE.md on packages and frameworks).
- **Numbers are not yours.** A tuning value lives in its ScriptableObject and its default is a
  feel decision. Moving a literal into a constant is fine; changing what it equals is not.
- **Player-facing text stays in the language CLAUDE.md names**, as do `[Header]` and `[Tooltip]`;
  identifiers, names and comments stay English. A refactor that "fixes" a player-facing string is a
  regression.
- **Assets are edited through the Editor**, never as YAML while Unity is running.
- **Measure before optimising anything that is not an allocation.** Removing a per-frame
  allocation needs no profiler; anything else needs the Profiler's Highlights module to say it
  mattered, on the device that matters.
- **Editor code is documentation, not a hot path.** Readability changes only.
