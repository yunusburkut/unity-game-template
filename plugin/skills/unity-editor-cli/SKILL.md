---
name: unity-editor-cli
description: Driving this Unity Editor from the command line — editing a scene, prefab, ScriptableObject or component through the Editor (`unity command`, `script run`), recompiling without window focus, play-capture screenshots, tests and builds through gk-bridge, and Windows argument traps. Use alongside unity-cli, which covers the CLI itself.
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
open one. The gamekit plugin's PreToolUse hook (`hooks/guard-unity-yaml.ps1`) refuses such an Edit/Write, and a Bash/PowerShell
one-liner that writes one inside the project (redirect, `sed -i`, `Set-Content`, ...), while the Editor holds
`Temp/UnityLockfile`. Drive the Editor instead.

## C# LSP

The `csharp-lsp` plugin loads the solution and reports diagnostics after each `.cs` edit, with no Unity focus needed.
Unity lists every source file in its csproj, so a **new** `.cs` file belongs to no project until Unity regenerates them
(focus or `unity command script recompile`); ignore its diagnostics until then. `Logs/agent/compile.log` stays the final word.

Call the CLI as bare `unity` (it is on PATH, `%LOCALAPPDATA%\Unity\bin\unity.exe`, not the Editor binary): the
permission allowlist matches `unity command ...`, not a full path or `& $var`.

## Prefer `script run` over `script eval`

```powershell
unity command script run --file <absolute .cs path> --timeout <seconds>
```

It compiles a real C# file into an ephemeral assembly and runs its single public static method (`--entry Type.Method`
picks another, `--args` passes a JSON array, `--dry_run` only compiles), so `using` directives, helper methods and a
normal class all work. `script eval` wraps the code in a *method body* (every type fully qualified) and has a 5 s
main-thread budget; `script run` has 60 s by default. `CreateAsset` + `SaveAssets` + `SaveOpenScenes` in one
`script eval` will blow through it. Anything opening a modal dialog blocks the main thread; `SaveOpenScenes()` on an untitled scene is the
usual culprit.

Keep the script **outside** `Assets/` (the scratchpad directory) so writing it triggers no asset import.

## Windows argument traps

CLI args are `--name value`, not `name=value`. A JSON value must be backslash-escaped (`'[\"D\"]'`) **and contain no
spaces**, or Windows argument splitting mangles it. `script run` sidesteps the whole problem.

Command names are grouped (`script run`, `capture game_view`, `editor status`, `editor.playmode start`). Most old
flat names (`run_script`, `capture_game_view`) fail with "renamed" (a few, like `eval` and `recompile`, still
resolve), and `unity command --obsolete-command-names` maps them.
The space form needs CLI 1.0.0-beta.14 or newer (`unity upgrade -y`); older ones accept only the dotted form
(`script.run`).

## Game View capture

`capture game_view --save_path` is confined to the project root and silently resolves a bare `Temp/x.png` to
**`Assets/Temp/x.png`**, importing it as an asset. Save outside `Assets/`, or delete it afterwards. `source=screen`
needs Play Mode; `source=camera` misses Screen Space - Overlay UI.

## An unfocused Editor

Auto Refresh runs only when the window regains focus, so a saved `.cs` file is not compiled until then (a
`Logs/agent/compile.log` older than the edit means exactly this). The Editor's update loop still ticks, so the agent
bridge and the CLI keep working: `gk-bridge refresh` imports and compiles what changed on disk, or run
`unity command script recompile`. The gamekit plugin's PostToolUse hook queues `refresh` after every Edit/Write of a
`*.cs`, `*.asmdef` or `*.asmref`, and after a `git rm` or `git mv`, in a project that has `Logs/agent/bridge.log`
(GameKit's AgentBridge writes it when the Editor starts; copies older than GameKit only after their first refresh), unless a request is already waiting there, so `compile.log` follows the edits by itself; during a multi-file change, judge it only after the last edit. Play Mode looks frozen without `runInBackground`, `editor set_auto_tick` does
not make the game advance, and keyboard and pointer input are gated on Game View focus. **Play Mode
cannot be played from here: hand gameplay checks back to the user** as a Play Mode checklist. What can be seen is the
untouched scene: `play-capture` (below) compiles, enters Play Mode with `runInBackground` on so an unfocused Editor
keeps ticking, saves three screenshots and the errors, and leaves Play Mode.

## Renaming scenes

Rename through the Editor or the CLI while Unity is open. Renaming a scene file with Unity closed leaves the remembered
scene path dangling, and the Editor silently opens an untitled empty scene on next launch.

## Agent bridge

With the Editor open, every request goes through `gk-bridge [-t seconds] <request>` (on the Bash tool's PATH), never a
hand-written `request.txt` wait loop. It writes `Logs/agent/request.txt`, waits for the AgentBridge's answer and prints
the log head. Exit 0 = pass, 1 = fail (the log says why), 2 = unknown (Editor closed, Play Mode, timeout, `compile.log`
older than the newest `.cs`); 2 is never a pass. Long requests (`run-tests`, `build`) go in a
background Bash call (until one reports, edit no script and send no other request); `play-capture` ends within 110 s,
so it runs in the foreground.

- Free, no need to ask: `refresh`, `compile ios|android`, `play-capture`.
- Ask first: `run-tests` (`unity-testing`), `build` (`platform-targets`).

| Request | Result in |
|---|---|
| `refresh` (also checks `compile.log` is newer than every `.cs`/`.asmdef`) | `Logs/agent/bridge.log` (`REFRESHED ... no script changes`, or `... compiled` after the compile), and `Logs/agent/compile.log` if code changed |
| `compile ios` / `compile android` (player scripts for that target, no platform switch) | `Logs/agent/compile-player.log` |
| `run-tests` / `run-tests playmode` (a refresh gate runs first) | `Logs/agent/tests.log` |
| `play-capture` / `play-capture 8` (seconds, 1–30, default 3) | `Logs/agent/capture.log`, screenshots in `Logs/agent/capture/` |
| `build windows\|android\|aab\|ios\|webgl [dev]` | `Logs/agent/build.log` |

A request the bridge does not know is answered in `Logs/agent/bridge.log` (older copies: `tests.log`). Games made
before GameKit carry their own AgentBridge copy, which may know fewer requests; that game's CLAUDE.md lists them.

With the Editor closed, batch mode works and **locks the project**:

```powershell
& "C:\Program Files\Unity\Hub\Editor\6000.6.0f1\Editor\Unity.exe" -batchmode -quit -projectPath . -executeMethod GameKit.Editor.BuildMenu.WebGL -logFile Logs/build-batch.log
```
