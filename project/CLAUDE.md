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

## Assembly boundary

`__GAME__.Core` (`Assets/__GAME__/Core`) is the simulation: value types and static step functions that take `dt` as a
parameter. No `MonoBehaviour`, `GameObject`, `Physics`, `Time`, `Input` or scene APIs, only UnityEngine math types.
`__GAME__.Game` is the Unity glue (input, views, scene wiring, Feel). `__GAME__.Editor` is tooling. The EditMode tests
reference Core alone. This split is the whole architecture: do not add layers beneath it.

`Ease` / `Easing` in Core and `EasingTests` are the worked example of a Core type and its test. `SimulationStep.Delta`
(Game) is the clamped `dt` every Update-driven simulation uses. `FrameLog` (Game) writes a frame-time CSV in every
Development Build (`unity-performance`).

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
- The Editor compiles only when its window regains focus.
- Never hand-edit `.unity`, `.prefab` or `.asset` YAML while the Editor is running (a PreToolUse hook enforces it);
  drive the Editor instead (`unity-editor-cli`).

## Agent bridge

`Assets/__GAME__/Editor/AgentBridge.cs` mirrors the Editor into `Logs/agent/`: `compile.log` (`OK` plus a timestamp
means clean; a stale timestamp means Unity has not been focused since the edit), `console.log` (last 200 errors and
warnings), `tests.log`, `build.log`, `capture.log`. Requests go into `Logs/agent/request.txt`: `run-tests`,
`run-tests playmode`, `play-capture [seconds]` (enters Play Mode, saves three screenshots and the errors, leaves),
`build windows|android|ios|webgl`. Read these, never the multi-MB `Logs/Editor.log`.

## Working agreement

Fast iteration. For a normal change: inspect the affected code, implement it, sanity-check the diff and
`Logs/agent/compile.log`, then say what to verify in Play Mode, on PC and, when input, UI or performance changed, on a
phone. Gameplay verification is mine. Do not run the test suite, batch-mode Unity or a build as a routine completion
step, and do not write tests for every small change; ask first (`unity-testing`).

When compacting, keep the files changed and the pending Play Mode checklist.

## Art

3D art is made in Blender through the Blender MCP and the global blender-skills (start with `blender-director`).
Scripts that generate art live in `Tools/Blender/`; their outputs are rebuilt, never hand-edited.
