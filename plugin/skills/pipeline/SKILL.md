---
name: pipeline
description: In a Unity game, use when the router sizes a task M or L, on "planla", "düzgün bitir", or on "devam", "review et", "puanla" for its PLAN.md card or commits - spec card, context, plan, compile gate per unit, verify, scored review to 9/10, handoff.
---

# Pipeline

Non-negotiable, in every phase:

- **Gates have three answers.** `gk-bridge refresh` exit 0 = pass, 1 = fail, 2 = unknown. Unknown is never a pass:
  nothing is committed as verified and the handoff says "compile unverified". (Not on PATH: run
  `bash "${CLAUDE_PLUGIN_ROOT}/bin/gk-bridge" refresh`; it asks for permission.)
- **One writer at a time.** The main session or one `gamekit:builder` writes code, never both; every other subagent
  only reads code, and the workflow's card, plan, verify and handoff steps edit only PLAN.md and DESIGN.md, one at a
  time. While `/gamekit:feature` runs, the main session edits and commits nothing. No worktrees (they have no
  Library and no Editor).
- **Scope is the spec card.** Nothing outside it is built; a good idea outside it goes to PLAN.md Next.
- **Evidence or it did not happen.** Every ticked item names its evidence on the same line.
- **Never hand-edit Unity YAML** (scene, prefab, asset and the other Editor-serialized types; the full list is `$yaml`
  in `hooks/guard-unity-yaml.ps1`, which `unity-editor-cli` also points to) while the Editor holds the project; drive
  the Editor instead (4.1 sets when).

| Phase | Output | Gate |
|---|---|---|
| 1 Spec | Spec card in PLAN.md Now | M: assumptions written; L: open questions answered |
| 2 Context | 5-10 files that matter, helpers to reuse, scene/prefab users | You can name where each change goes |
| 3 Plan | Units in the card, each one commit | Each unit names its files and gate |
| 4 Build | One commit per unit | `gk-bridge refresh` exit 0 per unit |
| 5 Verify | Acceptance ticked with evidence | `implementation-verification` |
| 6 Review | Score per reviewer | Every reviewer 9/10 or more, at most 3 rounds |
| 7 Handoff | PLAN.md updated, Play Mode checklist | The user plays it |

## 1 Spec: the prompt, made precise

Rewrite the user's prompt into this card under PLAN.md `## Now` (replace the TODO line; a game without PLAN.md gets
one with `## Now`, `## Next`, `## Pending Play Mode checks` and `## Known issues`). The card adds facts the
prompt left implicit (files, targets, existing helpers) and a checkable done; it never adds requirements. A design
question ("would X feel good?", "is X fun?") is not a card: it is a spike, `gamekit:prototype`. "Does X work?" about
existing code is a bug or a check, not a spike.

Now already holds another card, or a `prototype <Name>: <question>` line (a `gamekit:prototype` spike waiting for its
verdict): ask whether to finish it (`devam`; a spike: play it, then PROCEED / PIVOT / KILL, `gamekit:prototype`) or
park it, and never write a card over it. Parking a card commits the card as it stands (ticks included), then puts Now
back to its TODO line and adds one line to Next, `<goal> - parked, card at <short sha>` (that commit; asking for that
goal later brings it back from `git show <sha>:PLAN.md`); commit, then write the new card. Parking a prototype line
commits nothing new and keeps its folder: Now goes back to its TODO line and Next gets the line as it stands (its
`, first scene was <path>` note included) plus ` - parked, folder kept`; `devam` on that Next line moves it back to
Now. Then write the new card.

```
**<goal in one line>** (M|L)
Why: <what the player gets, one line>
Scope: <areas, Core/Game, scenes/prefabs touched>    Not: <what is explicitly left out>
Targets: PC | Phone | WebGL
Budget: <ms or bytes allocated per frame, on the slowest target | no per-frame cost - <why>>
Accept:
- [ ] <checkable outcome> - evidence: <play-capture (what it shows) | dosya:satır (a code-level claim) | test run (gk-bridge run-tests, after the user's yes) | Play Mode (user) | gk-bridge refresh (only an item about compiling)>
Assumptions: <M: your reading of anything ambiguous, each as "<reading> (break it when: <condition>)" when it has one, or "none">
Open questions: <L: only those whose answer changes the build, or "none">
Base: <`git rev-parse --short=7 HEAD`, run when the card is written: the card's key>
Plan:
1. [ ] <unit> - <files> - gate: gk-bridge refresh
Review: <after each round: r1 unity-reviewer 8, clarity-reviewer 9 (its findings: `review <Base>: ` lines in Known issues)>
```

- Each Accept line is observable: "the ball bounces off paddles at the same speed on PC and phone", not "bounce works";
  its evidence can show that outcome (a compile pass shows only that it compiles). Pick the evidence by what the item
  is; a mixed item takes the evidence of its riskiest part:

  | Item | Evidence |
  |---|---|
  | Core rule, formula, state step | `dosya:satır` (an EditMode test only with the user's OK). The line names its bounds: zero or minimum input, the cap, an empty collection, the invalid case (dead target, missing reference) when the rule can meet one |
  | Two systems talking (an event across Core/Game) | play-capture when it shows in the first seconds, else Play Mode (user) |
  | Save/load round trip (save, quit, relaunch, the state is back) | Play Mode (user): play-capture cannot quit and relaunch |
  | Look, juice, timing, feel | Play Mode (user), with a number or a reference: "hit stop 60-80 ms", "shake ends before the next input" |
  | UI, HUD | play-capture, one shot per screen touched, inside the safe area |
  | A tuning value only | the ScriptableObject value at `dosya:satır`, plus one Play Mode spot check |

- A subjective line ("feels snappy", "looks good", "intuitive", "works correctly") cannot be ticked. Rewrite it into
  2-3 binary candidates before building: input to visible response within 1 frame at 60 fps; the menu in at most 2
  taps from any screen; 4 of 5 testers pick the right option first time. M: pick one, note it under Assumptions; L: ask.
- Ready to leave phase 1: `Not:` is filled, what the card depends on is done, and a card that touches per-frame code
  fills its `Budget:` line (the number Verify and the reviewers check it against).
- A tuning or rule-change card adds these lines (DESIGN.md Rules changes in the same commit):
  ```
  Tune: | Parameter | Old | New | Why | In range? |   (DESIGN.md or the field's [Range]; outside: a one-line reason)
  Rule: Was: <the DESIGN.md Rules line, quoted> / Now: <the new line>
  Affected systems: <every reader of the value or rule>
  - [ ] No regression: <old behaviour that must keep working> - evidence: ...   (under Accept)
  ```
- Base is the card's key. Every commit for the card after Base carries the body line `Card: <Base>`, and its Known
  issues lines start `review <Base>: `. The card's commits are `git log --format=%h --grep='^Card: <Base>'
  <Base>..HEAD`: other work in that span (an S task between sessions, another card while this one was parked) is not
  this card's. A repaired Base reads `Base: <sha> (önce: <x>)` (Longer than one session): the key is the sha, and the
  range adds `--grep='^Card: <x>'` for the commits made before the repair.
- M: write the smallest reasonable reading under Assumptions and go on; the handoff names them and moves them to
  DESIGN.md Decisions, so the user can correct them. Own calls made while building go there too: every choice a player
  could notice that the card does not state (a speed, duration, colour, string, an edge case it never names), one
  line each with `dosya:satır`.
- L: show the card, ask the open questions (AskUserQuestion, recommendation first), and wait. With the answers (or
  none to ask), write them into the card (`Open questions: none`), put each design choice in DESIGN.md Decisions,
  commit both, and end the turn with one line: "`devam` = burada yaparım · `/gamekit:feature` = gözetimsiz yapar".

## 2 Context

Read the code yourself; you keep the context. For a wide search, or before touching a script used by scenes and
prefabs, run the `gamekit:scout` agent with one question; it returns files, reuse candidates and GUID users.
Then load the skills the card needs, and only those:

| The card touches | Load |
|---|---|
| New types, Core/Game split, ownership | `unity-architecture` |
| Juice, shake, sound, haptics | `game-feel`, then `feel-authoring` |
| Input, UI, a screen, a build | `platform-targets`, `ui-ugui` |
| Player-facing text, hints, HUD | `player-clarity` |
| A level or difficulty | `level-beat-review` |
| A genre's core system (jump, match, idle economy, deck) | `genre-defaults` |
| Per-frame code | `unity-performance` |
| A scene, prefab, ScriptableObject or other asset change | `unity-editor-cli` |
| A bug | `gamekit:bug-hunter` agent first, then `unity-debugging` |

## 3 Plan

Climb the lean ladder before each unit: does it need to exist, does Core or Game already have it, does Unity or an
installed package do it. Then order the units so each one compiles alone and is one commit (about 1-3 files). Write
them into the card's Plan. A real design choice with two viable options: M picks the reversible one and writes it under
Assumptions; L asks.

## 4 Build

Per unit, in order:

1. Edit. A scene or prefab change goes through `unity command` (`unity-editor-cli`) after step 2's exit 0 (so the
   unit's new types are compiled) and before step 4's commit, and is saved into that same commit; after an exit 2 it
   waits (step 2). A scene that is already dirty
   holds the user's unsaved edits: ask first. Save only what you changed (the active scene: `unity command scene
   save`; a prefab or asset: `AssetDatabase.SaveAssetIfDirty(asset)` in the same `script run`; never `editor
   save_all`). A file the unit did not touch that shows up in `git status`: leave it unstaged and tell the user.
2. `gk-bridge refresh` in Bash (it ends within the Bash tool's default 120 s).
   - Exit 0: `Logs/agent/compile.log` holds only the latest compile's messages (the assemblies Unity rebuilt, old
     warnings too, at most 100 lines), so it is no baseline. A `warning CS0618` is the unit's failure, fixed like exit
     1, only when its `<file>(<line>,<col>)` falls inside the unit's added or changed lines (the `+` hunks of `git diff
     -U0 HEAD -- <file>`); any other one was there before: report it, never fix it in the unit (`Assets/Feel` and
     `Assets/Plugins` are vendored and exempt).
   - Exit 1: fix it; the same error after two fixes: stop and run `gamekit:bug-hunter`.
   - Exit 2: the unit's scene/prefab step (step 1) waits. Commit the code with `Verified: compile unverified
     (<reason>)`, name the waiting step in the body, and leave the unit unticked, so `devam` gates it again; go on only
     if the next unit does not depend on it, and tell the user what to open or end (Unity, Play Mode).
   - Run `gk-bridge refresh` again before Verify and before phase 7. A pass first does the unit's waiting step 1
     scene/prefab change, then ticks the unit and commits both (PLAN.md and the saved scene/prefab) with `Card: <Base>`
     and `Verified: gk-bridge refresh PASS <time>`; a unit still unknown at phase 7 goes to Pending Play Mode checks as
     `compile unverified: <unit> - focus Unity, check the Console` (its waiting scene/prefab step named there too).
3. Platform code, after exit 0: `#if UNITY_ANDROID` also gets `gk-bridge compile android`, `#if UNITY_IOS` gets
   `compile ios`, `#if UNITY_WEBGL` gets `compile webgl` (GameKit 0.1.3+), and `#if !UNITY_EDITOR` code gets android
   and ios, one after the other (the Editor never compiles it; two gk-bridge calls at once read each other's answers).
   A FAIL is fixed like step 2. An UNKNOWN (no answer in time, the platform module not installed) is written
   `compile <p> unverified (<reason>)` and goes to Pending Play Mode checks; `devam` or a fix round that touches the
   branch runs it again. Three cases have no gate short of a build: `#if UNITY_WEBGL` on a GameKit older than 0.1.3
   (`compile webgl` answers "Unknown platform"), a PC-only branch while another target is active, and PC-player-only
   code (a `!UNITY_EDITOR` branch phones skip, such as Steam's). Each also goes to Pending Play Mode checks as a
   `webgl unverified` or `pc player unverified` line, in the shape implementation-verification step 3 gives (its single
   source: the branch, the build step, the action and expected result).
4. Tick the unit, then commit it with PLAN.md: `area: summary`, a body that says why, `Card: <Base>`, and a Verified
   line that names every check, since reviewers trust it: `Verified: gk-bridge refresh PASS <time>`, plus `; compile
   android PASS`, `; compile webgl PASS`, `; compile ios unverified (<reason>)`, `; unverified: WebGL` or `; unverified: PC player` as they
   apply.

## 5 Verify

Run the `implementation-verification` pass. It runs each Accept item's evidence check and ticks it with the evidence;
items that need hands on the game move to PLAN.md Pending Play Mode checks. An item whose check failed or could not
run stays unticked and goes to the reviewers as such.

## 6 Review: scored, fresh, until 9

1. Pick reviewers by what changed: `gamekit:unity-reviewer` always (it covers per-frame cost with
   `unity-performance`); `gamekit:clarity-reviewer` for player-facing text; `gamekit:design-critic` for a level or
   mechanic. Run them in parallel. A unit or a fix that adds or changes player-facing text adds
   `gamekit:clarity-reviewer` from the next round on, even when the first pick left it out.
   A project agent in the game's `.claude/agents` whose description matches the change joins every round too (when
   `.claude/agents/net-auditor.md` exists, `net-auditor` for a change that touches Game/Net, a NetworkBehaviour,
   spawning or a moving device): its brief adds "map each
   finding to the review rubric's severities and list them in its format", and its findings are scored like any
   reviewer's. A co-op mechanic card (the game has `.claude/skills/coop-chaos-design`) also runs that skill's gate
   table on the built mechanic in the main session before round 1, since `design-critic` leaves the ship verdict to
   it. A failed row whose "Fail means" is "Do not build" or "Fix before building" becomes a [karar] in Next (fix it,
   or ship with the weakness named) and the card gets no handoff until the user answers; any other failed row is
   named in the handoff.
2. Brief each one with this text, then the Accept items Verify left open (with their `failed:` / `not run:` reason)
   and every `disputed` line so far:
   ```
   Score this change with the review rubric (${CLAUDE_PLUGIN_ROOT}/skills/pipeline/references/review-rubric.md).
   Range: the card's commits (git log --format=%h --grep='^Card: <Base>' <Base>..HEAD<, plus --grep='^Card: <x>' for
   a repaired Base>); other commits there are other work.
   Spec card: PLAN.md Now.
   ```
   A review-only run on other commits changes the Range and Spec lines as the review-only paragraph below says.
3. The score is the rubric's arithmetic (its Score table is the single source of the weights: 10, -3 per [yüksek],
   -1 per [orta]) on each reviewer's listed findings; a different number the reviewer wrote is noted, not used.
4. Before fixing, write the round into PLAN.md (files survive `/clear`; the fix commit carries it), then fix:
   1. The scores go on the card's Review line.
   2. Each [yüksek] and [orta] finding becomes a Known issues line
      `review <Base>: [orta] dosya:satır - <what> (<reviewer>) - <what breaks it> - düzeltme: <fix>`.
   3. **Pruning, the one rule for every round, the review-only path and phase 7:** this round's finding lines replace
      this card's finding lines from the round before. A `disputed` line stays until a newer dispute of the same
      `dosya:satır` replaces it (one per place); an `önceden` line stays (an older problem only one round named is not
      dropped); other lines, another card's or the user's, stay.
   4. Its [karar] items (options included) go to Next and its `Önceden:` lines to Known issues as
      `review <Base>: önceden <line> (<reviewer>)`, each once; phase 7 never writes a second copy.
   5. Its Inspector/scene steps wait for phase 7, which writes the last round's: a fix may wire one in code, and every
      re-run reviewer names the steps the range still needs (a kept reviewer's steps carry over).
   6. Judge each finding against the code. Fix the real ones (gate + commit with `Card: <Base>`; one commit per round
      is enough) and drop their lines. A wrong one becomes `review <Base>: disputed dosya:satır - <evidence>`; never
      drop it silently.
   7. Re-check Accept: an item a fix repairs gets its evidence check run again and is ticked with it, and so does
      every ticked item whose evidence file a fix commit touched (`git show --stat` over the round's fix commits): its
      `dosya:satır` may have moved.
   8. When every [yüksek]/[orta] a round lists is already disputed, do not run another round: each becomes a [karar]
      in Next (accept the finding, or keep the code) and the card stays open as in 6.
5. Re-review with **new** agent calls (a fresh reviewer, never a resumed one). Stop when every score is 9 or more.
   Round 2 on is lean, not shallow: each re-run reviewer gets its own previous findings and the round's fix commits,
   reads those diffs and the code its findings point at first, and reads the rest of the range only where a fix
   reaches into it. A reviewer already at 9+ keeps its result, except `unity-reviewer` (every fix is code) and
   `clarity-reviewer` after a fix that changed player-facing text. Briefs keep the fixed text first and the round's
   part last, so parallel reviewers share a cached prefix.
6. After round 3 below 9: no handoff. Write the round as in 4, its Inspector/scene steps to Pending too, without
   fixing; commit `design: review open for <goal>`
   with `Card: <Base>` in the body, and report the scores, the open findings and why they are open. The user
   decides: `devam` runs another fix-and-review round, `kabul` runs phase 7 with the open findings left under Known
   issues.

`review et` or `puanla` from the user runs this phase alone: on the range they name, else the card's commits, else the
commits of the last task. With no card those commits carry no `Card:` line: the key in place of `<Base>` is the parent
of the range's first commit (`git rev-parse --short=7 <first>~1`), every round's brief names the range as
`<key>..HEAD` (the reviewed commits plus the fix commits, no grep), and 6.6 writes that range into the commit body.
When the range is not the card's commits, the brief's spec line reads "Spec: <the user's request, or the task's goal
from its commit messages>; PLAN.md Now is another task, do not score its Accept items" in place of "Spec card:
PLAN.md Now", and no Accept items or disputes of that card go with it.
No phase 7 follows: when a round passes, prune the `review <key>: ` lines by 6.4.3 (its `disputed` and `önceden`
lines stay), write each [orta] it still lists as one, and, if that changed PLAN.md, commit it as `design: review
passed` with the range and the scores in the body.

## 7 Handoff

1. **Scope audit.** Compare the card's own commits (`git show --stat` over the `--grep='^Card: <Base>'` list, never
   a plain diff of the range) against Scope and Not: each addition outside Scope or inside Not is named in the
   handoff as kept, or moved to Next; a cut lands after the review, so it needs a `gk-bridge refresh` and its own
   Pending check. In an unattended run (`/gamekit:feature`) nobody can choose a cut: keep the code and add a Next
   [karar] `kapsam dışı: <file> - <what> - seçenekler: tut (Scope'a yaz) ya da kes`.
2. **Unverified units.** A Plan unit still unticked after `compile unverified` gets one more `gk-bridge refresh`
   first, with its waiting scene/prefab step on a pass (4.2); still unknown, it goes to Pending as 4.2 says and the
   handoff names it.
3. **The handoff commit**, PLAN.md and DESIGN.md only, subject `design: hand off <goal>`, a body that lists the
   scores, `Card: <Base>` and a Verified line naming the gates (as 4.4). It holds:
   1. The card's Assumptions copied to DESIGN.md Decisions.
   2. PLAN.md Now back to its TODO line. Nothing moves up from Next: a Next item reaches Now only through phase 1,
      when the user asks for it.
   3. Pending Play Mode checks, each a concrete action with the expected result: for PC; for the phone when input,
      UI or performance changed; a WebGL line when the card's Targets include WebGL and save, audio, input or
      lifecycle changed. The reviewers' Inspector/scene steps and any builder note the user must act on go there too.
   4. Known issues, as `review <Base>: ` lines: an [orta] a passing review left, a reviewer's unscored "Önceden:"
      line, and an Accept item still unticked that is not a Play Mode check. The card's older lines are pruned by
      6.4.3 (`disputed` and `önceden` lines stay). What 6.4 already wrote stays as it is: never a second copy.
   5. PLAN.md Next: each [karar] item (with its options or the playtest to run) and a builder's needed extra. Next
      keeps at most 5 items: merge related ones and list what still does not fit in the commit body, older
      non-decision items first; a [karar] line always stays in Next, past 5 if it must.
4. **Tell the user** what now works, the assumptions and own calls taken (each to keep or change: a change is a fix
   now or a Next item), the scores, what stayed unverified (a compile first), the decisions waiting for them in Next,
   the Play Mode checklist, and that `push et` sends the commits to GitHub. This is the content; the output style and
   ADHD rules set the order and size, and the first Play Mode check is the closing next action.

## Longer than one session

`devam` reads PLAN.md Now and `git log -10`, then continues: a Base line with no sha gets one first (the parent of the
oldest commit whose body carries `Card: <that line>`, written `Base: <sha> (önce: <that line>)` so the range keeps
those commits; with no such commit, `git rev-parse --short=7 HEAD`; commit PLAN.md). A missing Base line: the parent
of the oldest commit that added the card's goal line (`git log --reverse --format=%h -S'<goal>' -- PLAN.md`), with
`(önce: <x>)` when the card's commits carry `Card: <x>`; this holds whether or not a Plan line is ticked, since a
`compile unverified` unit is committed but unticked. Nothing found and no Plan line ticked: `git rev-parse --short=7
HEAD` (the card was never committed, so no unit was either); nothing found with units ticked: ask the user for the
card's first commit, never HEAD (it would drop the built units from review and the scope audit; `/gamekit:feature`
stops on the same card for this reason). Then go on from the first of these that holds:

1. Open questions still lists questions from phase 1 L: ask them, write the answers, commit, then go on.
2. No Plan lines: phase 2.
3. A Plan line unticked: from the first one. A unit already committed as `compile unverified`: gate it (4.2), then do
   its waiting scene/prefab step, tick and commit as 4.2 says; any other unit: from 4.1.
4. An Accept item unticked with no `failed:` / `not run:` mark and evidence other than `Play Mode (user)`: Verify.
5. Review line empty: phase 6, round 1.
6. A score below 9: the card's `review <Base>: [yüksek]` and `[orta]` lines in Known issues are the findings to fix;
   its `disputed` lines are re-judged and go into the brief; its `önceden` lines are left as they are (unscored, older
   than the range). Fix, then re-review, as 6.4.
7. Every score 9 or more (a `design: review passed` commit may already hold it): phase 7, no new review round.

Keep the card current after every unit and round: it is the only memory that survives `/clear` and compaction.

## Unattended run

`/gamekit:feature` runs phases 2-7 as a Workflow over a card whose open questions are answered; `/gamekit:feature
<istek>` with no card in Now writes the card first (M rules) and stops only if it has open questions: ask them, write
the answers into the card as phase 1 L does, commit, and the user runs `/gamekit:feature` again. It starts only
when the user asks for it, since it cannot ask questions mid-run; it keeps the card's Base and ticked units, builds
only the rest, logs each ruling and stops at an unknown gate. It reports when done; until then the main session only
reads, and a new request waits for the report.
