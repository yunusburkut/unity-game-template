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
parameter. No `MonoBehaviour`, `GameObject`, `Physics`, `Time`, `Input` or scene APIs, only UnityEngine math types.
`__GAME__.Game` is the Unity glue (input, views, scene wiring, Feel). `__GAME__.Editor` is tooling. The EditMode tests
reference Core alone. This split is the whole architecture: do not add layers beneath it.

Shared tooling is the GameKit package (`Packages/manifest.json`, `com.yunusburkut.gamekit` from unity-game-template,
pinned to a `gamekit-vX.Y.Z` tag): `AgentBridge`, `BuildMenu`, `ProjectSetup` (`GameKit.Editor`), `FrameLog`,
`SafeAreaFitter` (`GameKit`). It is read-only here: a fix to it goes to the template, then the tag in the manifest moves.

`Ease` / `Easing` in Core and `EasingTests` are the worked example of a Core type and its test. `SimulationStep.Delta`
(Game) is the clamped `dt` every Update-driven simulation uses. `FrameLog` (GameKit) writes a frame-time CSV in every
Development Build (`unity-performance`). To fetch it (in Git Bash prefix adb with `MSYS_NO_PATHCONV=1`, or the
device path is rewritten to a Windows one): Android `adb pull /sdcard/Android/data/<bundle id>/files/` (or
`adb exec-out run-as <bundle id> cat /sdcard/Android/data/<bundle id>/files/<name>.csv` where that is blocked; the
exact path is in logcat as `FrameLog: ...`), Windows
`%USERPROFILE%\AppData\LocalLow\<Company>\<Product>\`, iOS Xcode > Devices > Download Container (Documents).

## Conventions

- Player-facing strings and Inspector `[Header]` / `[Tooltip]` text are TODO (Turkish / English); identifiers,
  namespaces, GameObject names and comments are English.
- Tunables live in a ScriptableObject, flattened into a plain struct for the Core step, so the simulation holds no
  managed reference.
- Dependencies wired in the Inspector are guaranteed; guard untrusted input only.
- Every input path works on both targets: pointer (mouse and touch through the Input System's `Pointer`) for anything
  you tap, keys only as a PC extra. Never read `UnityEngine.Input` (the old manager is off). `platform-targets` has
  the rules for input, UI scaling, the safe area and performance budgets.
- The package manifest is deliberately small. Ask before adding a package or a framework (DI container, event bus,
  pooling, save system, Addressables).
- Commits: `area: imperative summary` (area = core | game | ui | input | build | art | design | tools); the body says
  why and ends with `Verified: compile.log OK; Play Mode pending` (or what was checked), plus `Refs: #12` when one
  exists.

## Gotchas

- **Play Mode domain and scene reload are both off.** Every mutable `static` needs a
  `[RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.SubsystemRegistration)]` reset, or it survives into the
  next Play session and only breaks on the second run.
- `Assets/Feel` is a vendored paid package, gitignored, and dwarfs our code: scope searches to `Assets/__GAME__`.
  Feel's feedbacks compile into `MoreMountains.Tools`; reference that from `__GAME__.Game` the first time a feedback
  is used (`feel-authoring`).
- Phones run at `Application.targetFrameRate` (60, set in `AppStartup`), not vSync. Two quality levels exist: Mobile
  (0, phones and WebGL) and PC (1), each with its own URP asset under `Assets/__GAME__/Settings`. Tune those, do not
  add per-object platform branches.
- The Editor compiles only when its window regains focus or on a `refresh` request (Agent bridge below).
- Android builds target API 36. On Android 16 the back gesture may not arrive as `Keyboard.current.escapeKey`; test
  back navigation on a phone before relying on it.
- Never hand-edit `.unity`, `.prefab` or `.asset` YAML while the Editor is running (a PreToolUse hook enforces it);
  drive the Editor instead (`unity-editor-cli`). Commit before Editor-driven scene or prefab changes: `/rewind` cannot
  undo what the Editor wrote, and after a rewind write `refresh` yourself.
- One checkout writes code. A worktree or parallel session has no Library or Feel and its compile results come from
  this checkout's `Logs/agent`, so parallel agents only read.

## Agent bridge

GameKit's `AgentBridge` mirrors the Editor into `Logs/agent/`: `compile.log` (`OK` or `0 error(s),
N warning(s)` plus a timestamp means clean; a stale timestamp means no compile has run since the edit), `console.log` (last 200 errors and
warnings), `tests.log`, `build.log`, `capture.log`, `compile-player.log`, and `bridge.log` (answers to `refresh` and
to unknown requests). Requests go into `Logs/agent/request.txt`, one per write:

- `refresh`: import changed files and compile without focusing Unity. `bridge.log` says `REFRESHING`, then
  `REFRESHED ... compiled: see compile.log` or `REFRESHED ... no script changes`. In Play Mode it answers only
  `REFRESHED ... in Play Mode: compiles after Play ends` (Preferences > General > Script Changes While Playing set to
  Recompile After Finished Playing; `compile.log` updates once Play Mode exits) or `SKIPPED ...` (any other setting:
  nothing was imported, so write `refresh` again after Play Mode ends).
- `compile ios` / `compile android`: type-check the code behind `UNITY_IOS` / `UNITY_ANDROID` without switching
  platforms; the result is in `compile-player.log`.
- `run-tests`, `run-tests playmode`.
- `play-capture [seconds]`: enter Play Mode, save three screenshots and the errors, leave.
- `build windows|android|aab|ios|webgl [dev]`: `aab` is the Google Play bundle, `dev` a Development Build with the
  profiler attached.

Read these, never the multi-MB `Logs/Editor.log`.

Wait on a long request (`build`, `run-tests`, `play-capture`, `compile ios|android`) with Monitor, never sleep or
re-read. One request at a time: wait until `request.txt` is gone (a hook may have queued a `refresh` there), take the
time, then write, e.g. (one line):

```bash
until [ ! -e Logs/agent/request.txt ]; do sleep 1; done; f=Logs/agent/tests.log; t=$(date +%s); echo run-tests > Logs/agent/request.txt; until [ "$(stat -c %Y "$f" 2>/dev/null || echo 0)" -ge "$t" ] && ! head -1 "$f" | grep -qE '^(RUNNING|PENDING)'; do sleep 2; done; head -20 "$f"
```

Give builds a 20-minute deadline, other requests 10 minutes. A restarted Editor closes a build, test run, capture or
`compile` it left open as `FAILED ... Editor restarted`, and an open refresh as `REFRESHED ... Editor restarted`. A build request imports
changed files first; `build.log` says `PENDING` from the moment it is accepted, and `SKIPPED` if Play Mode is on or
starts before the build does. While a build is pending the next `request.txt` stays unread. A build with an unsaved
scene in the build list ends `FAILED ... unsaved scene(s)`: ask me to save, never save the scene yourself.

Compile state, tests, capture and builds go through `request.txt`; scene, prefab, component and asset edits and
hierarchy queries go through `unity command` (`unity-editor-cli`). New Editor automation is a `[CliCommand]` static
method in `__GAME__.Editor` (its asmdef already references `Unity.Pipeline.Attributes`), not a new request verb. No Unity MCP server.

## Working agreement

Fast iteration. For a normal change: inspect the affected code, implement it, sanity-check the diff and
`Logs/agent/compile.log`, then say what to verify in Play Mode, on PC and, when input, UI or performance changed, on a
phone. Gameplay verification is mine. Do not run the test suite, batch-mode Unity or a build as a routine completion
step, and do not write tests for every small change; ask first (`unity-testing`).

When a task ends, update PLAN.md (Now, Next, Pending Play Mode checks) in the same commit; done items leave the file.
A rule or architecture decision made in chat goes into DESIGN.md Decisions in the same commit. When I report a
playtest, log it under DESIGN.md Playtests before fixing anything; bugs from it go to PLAN.md Known issues.

Work on a branch per feature (`feat/<slug>`, `fix/<slug>`) and commit after each step that compiles. When the feature
is ready, run `unity-reviewer` on the branch diff, then `gh pr create --body-file` following
`.github/pull_request_template.md` with its verdict; leave the Play Mode boxes for me. Never merge.

When compacting, keep the files changed and the pending Play Mode checklist.

## Art

3D art is made in Blender through the Blender MCP and the global blender-skills (start with `blender-director`).
Scripts that generate art live in `Tools/Blender/`; their outputs are rebuilt, never hand-edited.
