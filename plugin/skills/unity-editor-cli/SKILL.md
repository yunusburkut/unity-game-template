---
name: unity-editor-cli
description: Driving the open Editor from the command line - `unity command`, `script run`, editing a scene, prefab, ScriptableObject or component through it, compiling unfocused, play-capture, gk-bridge tests and builds, Windows arg traps. CLI itself: unity-cli.
---

# Driving this Editor

**`unity-cli` is the reference for the CLI itself**: installation, global flags, `unity status` / `list` / `command`,
Safe Mode recovery, `unity test`, `com.unity.pipeline` (already a dependency). This file holds only what it does not
cover; load `unity-cli` only when a CLI command, flag or output shape is unclear.

`unity-cli`, `ui-ugui`, `urp-postprocessing` and `unity-package-management` are copies of the official Unity plugin's
skills (`unity@claude-plugins-official`); the plugin itself stays off because its other skills cost every session
context. The copies do not update by themselves, and they carry house edits (template rules, gamekit hand-offs) mixed
into Unity's text, so a refresh is a merge, never a copy over: take the newer upstream (`unity skill show --list` /
`--path <file>` prints the CLI's own `unity-cli` skill and writes nothing; the other three come from the plugin's newer
version, installed and kept disabled), diff it against the folder here, take the upstream changes and keep every house
edit, and keep every file the copy added (never a mirror that deletes extra reference files). The house edits are
marked near the top of each copy; re-apply any that the merge touched: `unity-cli`'s top blockquote (the gamekit
overrides: `gk-bridge` for tests and builds, no `unity mcp configure`, no `unity skill install` / `setup` without a yes,
new games via `gamekit:new-game`), `unity-package-management`'s "Local gamekit adaptations" block and `ui-ugui`'s
"House rules win" list. `unity-cli` is copied from `unity@claude-plugins-official` 0.1.9-beta (docs for CLI
`1.0.0-beta.16`), as its blockquote says. Note the CLI version the merge was aligned to in that skill's `CHANGELOG.md`
(`unity-cli`) or `LICENSE.md` (the others).

The CLI-specific claims in this file (command names, `script run` and its 60 s default, the 5 s `script eval` budget,
`capture game_view` paths) were checked on **CLI 1.0.0-beta.14** with `com.unity.pipeline` as the template pins it.
When `unity --version` reports a newer CLI, recheck them; on an older one, see the fallbacks below.

Never hand-edit Unity YAML (`.unity`, `.prefab`, `.asset`, `.mat`, `.controller`, `.overrideController`, `.anim`,
`.mask`, `.mixer`, `.playable`, `.signal`, `.lighting`, `.preset`, `.terrainlayer`, `.renderTexture`, `.spriteatlasv2`,
`.physicMaterial`, `.physicsMaterial`, `.physicsMaterial2D`; the full list is `$yaml` in `hooks/guard-unity-yaml.ps1`)
while an Editor is live: fileIDs and GUIDs
are easy to get wrong, the running Editor will not see the change, and the write can land in a scene that is not the
open one. The gamekit plugin's PreToolUse hook (`hooks/guard-unity-yaml.ps1`) refuses such an Edit/Write, and a Bash/PowerShell
one-liner that writes one (redirect, `sed -i`, `Set-Content`, ...), while the Editor that owns that file's project
holds `Temp/UnityLockfile`. Drive the Editor instead.

## C# LSP

The `csharp-lsp` plugin loads the solution and reports diagnostics after each `.cs` edit, with no Unity focus needed.
Unity lists every source file in its csproj, so a **new** `.cs` file belongs to no project until Unity regenerates them
(on the next import: the `refresh` the PostToolUse hook queues, or `gk-bridge refresh`); ignore its diagnostics until then. `Logs/agent/compile.log` stays the final word.

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

CLI args are `--name value`, not `name=value`. A JSON value (`--args`) depends on the shell, and must **contain no
spaces** in either:

- PowerShell 5.1 drops embedded quotes on the way to a native exe, so escape them: `'[\"D\"]'`.
- Git Bash (the Bash tool) quotes the argument itself; a backslash would reach `unity.exe` literally and break the
  JSON, so write it plain: `'["D"]'`.

`script run` with the values set inside the `.cs` file sidesteps the whole problem in both shells.

Command names are grouped (`script run`, `capture game_view`, `editor status`, `editor.playmode start`). Most old
flat names (`run_script`, `capture_game_view`) fail with "renamed" (a few, like `eval` and `recompile`, still
resolve), and `unity command --obsolete-command-names` maps them.
The space form needs CLI 1.0.0-beta.14 or newer (`unity self-update -y`; `upgrade` is its older alias); older ones accept only the dotted form
(`script.run`). Where `script run` is missing (an older CLI or Pipeline package), `unity command script eval_file <file>`
is the fallback when the project registers it (see `unity-cli`'s integration-advanced.md), with `script eval`'s
method-body rules and budget.

## Game View capture

`capture game_view --save_path` is confined to the project root and silently resolves a bare `Temp/x.png` to
**`Assets/Temp/x.png`**, importing it as an asset. Save outside `Assets/`, or delete it afterwards. `--source screen`
needs Play Mode and an unlocked desktop (a locked Windows session returns a solid cyan image); `--source camera` works
on a locked machine but misses Screen Space - Overlay UI, which no camera draws.

## An unfocused Editor

Auto Refresh runs only when the window regains focus, so a saved `.cs` file is not compiled until then (a
`Logs/agent/compile.log` older than the edit means exactly this). The Editor's update loop still ticks, so the agent
bridge and the CLI keep working.

- **Compiling after edits: `gk-bridge refresh` is the one gate.** It imports and compiles what changed on disk and
  checks that `compile.log` is newer than every `.cs`/`.asmdef`. The gamekit plugin's PostToolUse hook queues `refresh`
  after every Edit/Write of a `*.cs`, `*.asmdef` or `*.asmref`, and after a `git rm` or `git mv`, in a project that has
  `Logs/agent/bridge.log`, unless a request is already waiting there, so `compile.log` follows the edits by itself.
  During a multi-file change, **judge it only after the last edit**. (GameKit's AgentBridge writes `bridge.log` when the
  Editor starts; copies older than GameKit only after their first refresh.) `unity command script recompile` is
  asynchronous and checks no log freshness: use it only to re-register a `[CliCommand]`, then poll
  `unity command script recompile_status` until `completed`; it is not a compile gate.
- **Play Mode cannot be played from here: hand gameplay checks back to the user** as a Play Mode checklist. Play Mode
  looks frozen without `runInBackground`, `editor set_auto_tick` does not make the game advance, and keyboard and
  pointer input are gated on Game View focus.
- **What can be seen** is the untouched scene: `play-capture` (below) compiles, enters Play Mode with
  `runInBackground` on so an unfocused Editor keeps ticking, saves three screenshots and the errors, and leaves Play
  Mode.

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

`gk-bridge` with no argument prints its usage header, the source of truth for the requests and deadlines; if it and
this table ever disagree, trust it.

| Request | Result in |
|---|---|
| `refresh` (also checks `compile.log` is newer than every `.cs`/`.asmdef`) | `Logs/agent/bridge.log` (`REFRESHED ... no script changes`, or `... compiled` after the compile), and `Logs/agent/compile.log` if code changed |
| `compile ios` / `compile android` (player scripts for that target, no platform switch) | `Logs/agent/compile-player.log` |
| `run-tests` / `run-tests playmode` (a refresh gate runs first) | `Logs/agent/tests.log` |
| `play-capture` / `play-capture 8` (seconds, 1–30, default 3) | `Logs/agent/capture.log`, screenshots in `Logs/agent/capture/` |
| `build windows\|android\|aab\|ios\|webgl [dev]` | `Logs/agent/build.log` |

A request the bridge does not know is answered in `Logs/agent/bridge.log` (older copies: `tests.log`). Games made
before GameKit carry their own AgentBridge copy, which may know fewer requests; that game's CLAUDE.md lists them.

With the Editor closed, batch mode works and **locks the project**. `unity run` picks the Editor from
`ProjectSettings/ProjectVersion.txt` (no hard-coded install path to go stale after an upgrade) and adds `-batchmode`,
`-quit` and `-projectPath` itself (passing them after `--` fails with exit 6). `-buildTarget` opens the project on that
target, so the build skips a mid-build platform switch and its full reimport (batch mode never switches back, so the
next GUI open is on that target; switch back in Build Profiles if needed):

```powershell
unity run . --timeout 1800 --log-file Logs/build-batch.log -- -buildTarget WebGL -executeMethod GameKit.Editor.BuildMenu.WebGL
```

Swap the pair for another target (`-buildTarget Android` with `BuildMenu.Android`, `Win64` with
`BuildMenu.Windows`). A failed build exits 1 (`BuildMenu` calls `EditorApplication.Exit(1)`), a timeout exits 14, and the
result is also in `Logs/agent/build.log`.
