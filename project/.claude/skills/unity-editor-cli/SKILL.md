---
name: unity-editor-cli
description: __GAME__-specific gotchas when driving this Unity Editor from the command line — scene/prefab/asset changes, forcing a recompile, capturing the Game View, running tests and builds through the agent bridge. Use alongside the unity-cli skill, which covers the CLI itself.
---

# Driving this Editor

**`unity-cli` is the reference for the CLI itself**: installation, global flags, `unity status` / `list` / `command`,
Safe Mode recovery, `unity test`, `com.unity.pipeline` (already a dependency). This file holds only what it does not
cover.

`unity-cli`, `ui-ugui`, `urp-postprocessing` and `unity-package-management` are copies of the official Unity plugin's
skills (`unity@claude-plugins-official`); the plugin itself stays off because its other skills cost every session
context. The copies do not update: to refresh one, install the plugin's newer version, copy the folder over and keep it
disabled.

Never hand-edit `.unity`, `.prefab`, `.asset`, `.mat`, `.controller`, `.overrideController`, `.anim` or `.mask` YAML while an Editor is live: fileIDs and GUIDs
are easy to get wrong, the running Editor will not see the change, and the write can land in a scene that is not the
open one. A PreToolUse hook (`.claude/hooks/guard-unity-yaml.ps1`) refuses such an Edit/Write while the Editor holds
`Temp/UnityLockfile`. Drive the Editor instead.

## C# LSP

The `csharp-lsp` plugin loads the solution and reports diagnostics after each `.cs` edit, with no Unity focus needed.
Unity lists every source file in its csproj, so a **new** `.cs` file belongs to no project until Unity regenerates them
(focus or `unity command recompile`); ignore its diagnostics until then. `Logs/agent/compile.log` stays the final word.

```powershell
$unity = "$env:LOCALAPPDATA\Unity\bin\unity.exe"   # Unity's CLI, not the Editor binary
```

## Prefer `run_script` over `eval`

```powershell
& $unity command run_script --file <absolute .cs path> --timeout_ms N
```

It compiles a real C# file into an ephemeral assembly and runs its single public static method (`--entry Type.Method`
picks another, `--args` passes a JSON array, `--dry_run` only compiles), so `using` directives, helper methods and a
normal class all work. `eval` wraps the code in a *method body* (every type fully qualified) and has a 5 s main-thread
budget; `run_script` has 30 s by default. `CreateAsset` + `SaveAssets` + `SaveOpenScenes` in one `eval` will blow
through it. Anything opening a modal dialog blocks the main thread; `SaveOpenScenes()` on an untitled scene is the
usual culprit.

Keep the script **outside** `Assets/` (the scratchpad directory) so writing it triggers no asset import.

## Windows argument traps

CLI args are `--name value`, not `name=value`. A JSON value must be backslash-escaped (`'[\"D\"]'`) **and contain no
spaces**, or Windows argument splitting mangles it. `run_script` sidesteps the whole problem.

## Game View capture

`capture_game_view --save_path` is confined to the project root and silently resolves a bare `Temp/x.png` to
**`Assets/Temp/x.png`**, importing it as an asset. Save outside `Assets/`, or delete it afterwards. `source=screen`
needs Play Mode; `source=camera` misses Screen Space - Overlay UI.

## The Editor does not tick while unfocused

Play Mode looks frozen, and compilation does not start until the window regains focus (a stale timestamp in
`Logs/agent/compile.log` means exactly this; run `unity command recompile` or ask the user to alt-tab).
`set_autotick` does not make the game advance. Keyboard and pointer input are gated on Game View focus. **Play Mode
cannot be played from here: hand gameplay checks back to the user** as a Play Mode checklist. What can be seen is the
untouched scene: `play-capture` (below) compiles, enters Play Mode with `runInBackground` on so an unfocused Editor
keeps ticking, saves three screenshots and the errors, and leaves Play Mode.

## Renaming scenes

Rename through the Editor or the CLI while Unity is open. Renaming a scene file with Unity closed leaves the remembered
scene path dangling, and the Editor silently opens an untitled empty scene on next launch.

## Agent bridge: tests and builds

Only with permission (`unity-testing`, `platform-targets`). With the Editor open, write one line into
`Logs/agent/request.txt`:

| Request | Result in |
|---|---|
| `run-tests` / `run-tests playmode` | `Logs/agent/tests.log` |
| `play-capture` / `play-capture 8` (seconds, 1–30, default 3) | `Logs/agent/capture.log`, screenshots in `Logs/agent/capture/` |
| `build windows` / `build android` / `build ios` / `build webgl` | `Logs/agent/build.log` |

With the Editor closed, batch mode works and **locks the project**:

```powershell
& "C:\Program Files\Unity\Hub\Editor\6000.6.0f1\Editor\Unity.exe" -batchmode -quit -projectPath . -executeMethod __GAME__.Editor.BuildMenu.WebGL -logFile Logs/build-batch.log
```
