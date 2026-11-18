<!--
Maintainers: this file loads into every session, so it holds only what Claude cannot infer from the code and needs on
any task. Test for each line: "would Claude make a mistake without it?" Detail that matters for part of the repo goes
in a path-scoped rule (.claude/rules/) or a skill. HTML comments are stripped before Claude sees the file.
Started from unity-game-template; replace every TODO line once the game's shape is decided (DESIGN.md).
-->
# __GAME__

TODO: one line on the game (genre, camera, core loop).
Targets: PC (Windows, keyboard + mouse) and mobile (Android, iOS, touch); WebGL for itch.io playtests. Unity 6000.6,
URP, the new Input System only. UI is uGUI.
TODO: orientation on phones (portrait / landscape), and whether a gamepad is in scope.

Current state and handoff: @PLAN.md

## Assembly boundary

`__GAME__.Core` (`Assets/__GAME__/Core`) is the simulation: value types and static step functions that take `dt` as a
parameter. No `MonoBehaviour`, `GameObject`, `Physics`, `Time`, `Input` or scene APIs, only UnityEngine math types
and data-only ScriptableObject configs (`<System>Config` with `ToTuning()`, no scene references; the shape is in
`unity-architecture`). `__GAME__.Game` is the Unity glue (input, views, scene wiring, Feel). `__GAME__.Editor` is
tooling. The EditMode tests reference Core alone. This split is the whole architecture: do not add layers beneath it.
The one exception is a throwaway `Prototypes/<Name>` asmdef that references Core and the engine and package assemblies
the question needs (Input System, uGUI, Feel), never Game, and is deleted with its verdict (`gamekit:prototype`).

Shared tooling is the GameKit package (`Packages/manifest.json`, `com.yunusburkut.gamekit` from unity-game-template,
pinned to a `gamekit-vX.Y.Z` tag): `AgentBridge`, `BuildMenu`, `ProjectSetup` (`GameKit.Editor`), `FrameLog`,
`SafeAreaFitter` (`GameKit`). It is read-only here: a fix to it goes to the template, then the tag in the manifest moves.

`Ease` / `Easing` in Core and `EasingTests` are the worked example of a Core type and its test. `CoreBoundaryTests` (EditMode) fails
when Core declares a component, links a physics/input/Editor assembly, or its source uses `MonoBehaviour`,
`GameObject`, `SceneManager`, `Time`, `Input`, `Physics`, `UnityEngine.Random`, `Screen`, `Camera`, `Application`,
`PlayerPrefs`, `Resources` or `Instantiate` / `Destroy`, and when a `Prototypes/<Name>` assembly references Game, or
when Core or Game references a prototype. `SimulationStep.Delta`
(Game) is the clamped `dt` every Update-driven simulation uses. `FrameLog` (GameKit) writes a frame-time CSV in every
Development Build; where to fetch it per platform (adb, LocalLow, Xcode) is in `unity-performance`.

## Conventions

- Player-facing strings and Inspector `[Header]` / `[Tooltip]` text are TODO (Turkish / English); identifiers,
  namespaces, GameObject names and comments are English.
- Tunables live in a ScriptableObject, flattened into a plain struct for the Core step, so the simulation holds no
  managed reference.
- Dependencies wired in the Inspector are guaranteed; guard untrusted input only.
- Every input path works on both targets: pointer (mouse and touch through the Input System's `Pointer`) for anything
  you tap, keys only as a PC extra. Never read `UnityEngine.Input` (the old manager is off). Input actions live in
  one asset, `Assets/__GAME__/Settings/__GAME__Controls.inputactions`, created by the first input feature and assigned
  as the project-wide actions (until then `InputSystem.actions` is unset).
  `platform-targets` has the rules for input, UI scaling, the safe area and the quality tiers; the performance budgets are in
  `unity-performance`.
- The package manifest is deliberately small. Ask before adding a package or a framework (DI container, event bus,
  pooling, save system, Addressables).
- Commits: `area: imperative summary` (area = core | game | ui | input | build | art | design | tools | template; a
  `template: sync to unity-game-template@<sha>` subject is the marker `gamekit:sync-template` reads, so keep it
  exact); the body says why and ends with `Verified: gk-bridge refresh PASS <time>; Play Mode pending` (or what was checked; an UNKNOWN gate
  is `Verified: compile unverified (<reason>)`), plus `Refs: #12` when one exists.

## Gotchas

- **Play Mode domain and scene reload are both off.** Every mutable `static` needs a
  `[RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.SubsystemRegistration)]` reset, or it survives into the
  next Play session and only breaks on the second run.
- `Assets/Feel` is a vendored paid package (committed, so the repo stays private) that dwarfs our code: never edit
  it, and scope searches to `Assets/__GAME__`. If `Assets/Feel` is missing (new-game found no local copy and warned),
  ask me to import Feel from the Asset Store before any Feel work.
  Feel's feedbacks compile into `MoreMountains.Tools`; reference that from `__GAME__.Game` the first time a feedback
  is used (`feel-authoring`); `__GAME__.Game` already references `GameKit` (`SafeAreaFitter`, `FrameLog`).
- Frame rate, the quality tiers (tune their URP assets, never per-object platform branches) and the Android back
  gesture: `platform-targets`. Android builds target API 36.
- The Editor compiles when its window regains focus, when the gamekit hook queues a refresh after a `.cs` / `.asmdef`
  edit or a `git rm` / `git mv`, and on `gk-bridge refresh`, which is still the gate that reports it (Agent bridge
  below).
- Never hand-edit `.unity`, `.prefab` or `.asset` YAML, or the other Editor-serialized types (`.mat`, `.anim`,
  `.controller` ...; the full list is `$yaml` in the gamekit hook `guard-unity-yaml.ps1`), while the Editor is
  running (a PreToolUse hook enforces it);
  drive the Editor instead (`unity-editor-cli`). Commit before Editor-driven scene or prefab changes: `/rewind` cannot
  undo what the Editor wrote, and after a rewind run `gk-bridge refresh`.
- One checkout writes code. A worktree has no Library and no Editor, so `gk-bridge` answers UNKNOWN there; parallel
  agents only read.

## Agent bridge

GameKit's `AgentBridge` mirrors the Editor into `Logs/agent/`: `compile.log` (`OK` or `0 error(s),
N warning(s)` plus a timestamp means clean; a stale timestamp means no compile has run since the edit), `console.log` (last 200 errors and
warnings), `tests.log`, `build.log`, `capture.log`, `compile-player.log`, and `bridge.log` (answers to `refresh` and
to unknown requests). Send a request with `gk-bridge <request>` in Bash (gamekit plugin): it waits for the Editor's
answer and prints `PASS`, `FAIL` or `UNKNOWN` with the log head. Exit 0 = pass, 1 = fail, 2 = unknown (no Editor,
Play Mode, busy, timeout), and unknown is never a pass. Requests (it writes them to `Logs/agent/request.txt`):

- `refresh`: import changed files and compile without focusing Unity. `bridge.log` says `REFRESHING`, then
  `REFRESHED ... compiled: see compile.log` or `REFRESHED ... no script changes`. In Play Mode it answers only
  `REFRESHED ... in Play Mode: compiles after Play ends` (Preferences > General > Script Changes While Playing set to
  Recompile After Finished Playing; `compile.log` updates once Play Mode exits) or `SKIPPED ...` (any other setting:
  nothing was imported, so run `gk-bridge refresh` again after Play Mode ends).
- `compile ios` / `compile android`: type-check the code behind `UNITY_IOS` / `UNITY_ANDROID` without switching
  platforms; the result is in `compile-player.log`.
- `run-tests`, `run-tests playmode`.
- `play-capture [seconds]`: enter Play Mode, save three screenshots and the errors, leave.
- `build windows|android|aab|ios|webgl [dev]`: `aab` is the Google Play bundle, `dev` a Development Build with the
  profiler attached.

Read these, never the multi-MB `Logs/Editor.log`.

Run `build` and `run-tests` (ask first) in a background Bash call; until it reports, edit no script and send no other
request (gk-bridge answers UNKNOWN meanwhile). A restarted Editor closes a build, test run, capture
or `compile` it left open as `FAILED ... Editor restarted`. A build imports changed files first and ends `SKIPPED` if
Play Mode starts before it. A build with an unsaved scene in the build list ends `FAILED ... unsaved scene(s)`: ask me
to save, never save a scene you did not change. A scene or asset you changed through `unity command` you save and
commit with that change.

Compile state, tests, capture and builds go through `gk-bridge`; scene, prefab, component and asset edits and
hierarchy queries go through `unity command` (`unity-editor-cli`). New Editor automation is a `[CliCommand]` static
method in `__GAME__.Editor` (its asmdef already references `Unity.Pipeline.Attributes`), not a new request verb. No Unity MCP server.

## Working agreement

The task router sizes each task S, M or L. S: inspect the affected code, implement it, `gk-bridge refresh`, write
the Play Mode checks (PC and, when input, UI or performance changed, the phone; `implementation-verification`) under
PLAN.md Pending, commit, then tell me those checks. A change to a rule or a tuned value also updates its DESIGN.md
Rules (as built) line, worked example included, in the same commit. M and L run the `gamekit:pipeline` skill: the
prompt becomes a spec card in PLAN.md Now, then plan, build with a gate per unit, verify, a scored review until every
reviewer gives 9/10, and the handoff. `/gamekit:feature` runs the pipeline unattended, only when I ask. `review et` or
`puanla` on code or commits runs only the pipeline's review loop (score, fix, re-score until 9); on a level, text or
store page the matching read-only agent critiques it instead; `devam` continues the card in PLAN.md
Now; `kabul` hands off a reviewed card that stayed below 9 (or whose handoff stopped), its open findings under Known
issues; `kartı Next'e taşı` parks the card. A design question ("does X feel good?") goes to `gamekit:prototype`
instead: one PLAN.md Now line with its question, no spec card. A choice I will see or feel with 2+ real options (on
M and L, not S) I pick on an HTML decision page first; the picks go into the card or DESIGN.md before the build
(`gamekit:pipeline`). Gameplay
verification is mine. Do not run the test suite, batch-mode Unity or a build as a routine completion
step, and do not write tests for every small change; ask first (`unity-testing`).

When a task ends, update PLAN.md (Now, Next, Pending Play Mode checks) in the same commit; done items leave the file.
A Play Mode check I report as passing leaves Pending; one I report as failing becomes a Known issue.
A rule or architecture decision made in chat goes into DESIGN.md Decisions in the same commit. When I report a
playtest, log it under DESIGN.md Playtests before fixing anything; bugs from it go to PLAN.md Known issues.
A Known issue carries a severity tag: `[yüksek]` crash, data loss, cannot progress or blocks a build/ship; `[orta]` a
feature broken with a workaround; `[düşük]` cosmetic or polish. A `review <Base>: ` line keeps the review rubric's
tag, format and place (`gamekit:pipeline`); it blocks a release or earns a hotfix only when it is also a `[yüksek]`
case above.

Work straight on `main`: no feature branches, no PRs. Commit after each step that compiles.
Push only when I ask. With no `origin` yet, the first push is `gh repo create __GAME__ --private --source . --remote origin
--push` (private: Feel is committed).

When compacting, keep the files changed and the pending Play Mode checklist.

## Art

3D art is made by Claude in headless Blender (scripts and the Blender MCP `*_for_cli` tools) with the global
blender-skills (start with `blender-director`; a game asset from a reference image starts with `blender-image-to-3d`,
and every Unity delivery follows `unity-export`); the user never models by hand. A Blender window opens only when the
user asks to see one: only the `*_for_cli` and docs tools keep Blender closed, and any other Blender MCP tool starts a
Blender window (gamekit `ensure-blender` hook), so call one only then.
Scripts that generate art live in `Tools/Blender/`; their outputs are rebuilt, never hand-edited.
Sprites, UI images and audio are not Blender work (Blender only pre-renders sprites for a deliberately 3D-rendered
look): ask me where each comes from (my own files, a licensed or CC0 pack such as Kenney, a generator I approve) and
never ship a placeholder (sfxr-style beeps, WAVs synthesised in code, flat shapes) as final art or sound.
Route per class: 2D sprites and icons come from those sources, or from orthographic Blender renders
(`blender-director`) when the look is 3D-rendered; UI is uGUI built from those sprites (9-sliced panels, vector-sourced
icons), never code-drawn shapes as final; Unity AI Generators is one such generator, used only after my yes; store
screenshots come from `gk-bridge play-capture` at the store sizes (`launch-review`). This route wins over the
`unity-cli` advice to reach for AI Generators first.
Every asset that is not ours or that an AI made (you included: Blender scripts, generated textures, sounds) gets a
`docs/asset-sources.md` row in the same commit; `launch-review` reads it before a store submit.
