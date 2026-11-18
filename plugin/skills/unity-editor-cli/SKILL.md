---
name: unity-editor-cli
description: Driving the open Editor from the command line - `unity command`, `script run`, editing a scene, prefab, ScriptableObject, component or Animator through it, compiling unfocused, play-capture, gk-bridge tests/builds, Windows arg traps. CLI: unity-cli.
---

# Driving this Editor

**`unity-cli` is the reference for the CLI itself**: installation, global flags, `unity status` / `list` / `command`,
Safe Mode recovery, `unity test`, `com.unity.pipeline` (already a dependency). This file holds only what it does not
cover; load `unity-cli` only when a CLI command, flag or output shape is unclear. `unity-cli` is a house-edited copy of
Unity's skill: its top gamekit blockquote and this file win over its generic recipes (how the copies are refreshed, for
template maintainers only: `references/refreshing-copies.md`).

The CLI-specific claims in this file (command names, `script run` and its 60 s default, the 30 s `script eval`
default, `capture game_view` parameters, the exit codes below) were checked on **CLI 1.0.1** with
`com.unity.pipeline` as the template pins it (`0.10.0-exp.1`).
When `unity --version` reports a newer CLI, recheck them; on an older one, see the fallbacks below. `unity-cli`
may document a newer CLI than is installed: confirm an unfamiliar flag with `unity <cmd> --help`
before relying on it, and read a flag it rejects as an older CLI, not a project problem.

Since CLI 1.0.0 `unity command` exits `6` (`COMMAND_FAILED`) when the command's result reports `success: false` or a
failed status, so a `script run` whose method throws fails the call; an older CLI exits `0` there, so read the
result's `success` too. `unity command <name> --help` (1.0.0+) prints that command's parameters from the Editor; on
an older CLI read them from `unity command --detail full --json`.

Never hand-edit Unity YAML (`.unity`, `.prefab`, `.asset`, `.mat`, `.controller`, `.overrideController`, `.anim`,
`.mask`, `.mixer`, `.playable`, `.signal`, `.lighting`, `.preset`, `.terrainlayer`, `.renderTexture`, `.spriteatlasv2`,
`.physicMaterial`, `.physicsMaterial`, `.physicsMaterial2D`; the full list is `$yaml` in `hooks/guard-unity-yaml.ps1`)
while an Editor is live: fileIDs and GUIDs
are easy to get wrong, the running Editor will not see the change, and the write can land in a scene that is not the
open one. The gamekit plugin's PreToolUse hook (`hooks/guard-unity-yaml.ps1`) refuses such an Edit/Write, and a Bash/PowerShell
one-liner that writes one (redirect, `sed -i`, `Set-Content`, ...), while the Editor that owns that file's project
holds `Temp/UnityLockfile`. Drive the Editor instead. An Animator controller and its clips are built the same way, by
an Editor builder: `references/animation.md` (controller from a list, driving it from Core state, root motion, 2D).

## C# LSP

The `csharp-lsp` plugin loads the solution and reports diagnostics after each `.cs` edit, with no Unity focus needed.
Unity lists every source file in its csproj, so a **new** `.cs` file belongs to no project until Unity regenerates them
(on the next import: the `refresh` the PostToolUse hook queues, or `gk-bridge refresh`); ignore its diagnostics until then. `Logs/agent/compile.log` stays the final word.

Call the CLI as bare `unity` (it is on PATH, `%LOCALAPPDATA%\Unity\bin\unity.exe`, not the Editor binary), never a
full path or `& $var`: permission rules match the bare form. The user-level settings allow only the read-only ones
(`unity status`, `unity command editor status`, `console get`, `script recompile_status` and the like); `script run`
and every other edit always asks, which is expected, not a misconfiguration.

## Prefer `script run` over `script eval`

```powershell
unity command script run --file <absolute .cs path> --timeout <seconds>
```

It compiles a real C# file into an ephemeral assembly and runs its single public static method (`--entry Type.Method`
picks another, `--args` passes a JSON array, `--dry-run true` only compiles), so `using` directives, helper methods
and a normal class all work. `script eval` evaluates a snippet in Roslyn's script mode with a 30 s default
`--timeout`; `script run` has 60 s by default. Anything opening a modal dialog blocks the main thread until the
timeout; `SaveOpenScenes()` on an untitled scene is the usual culprit.

Keep the script **outside** `Assets/` (the scratchpad directory) so writing it triggers no asset import.

An edit that is not saved lives only in memory: commit first, change only what the task names, then save exactly that
in the same script (the save rules are `pipeline`'s Build step and the game's CLAUDE.md). A plain field assignment marks
nothing dirty, so `SaveAssetIfDirty` alone writes nothing; edit a prefab through its asset, not a scene instance.
Most scene objects are prefab instances, and a direct assignment to one's component is not recorded as an instance
override: the scene saves without it and the value reverts to the prefab's on reload, while the script reports
success. After changing a component on an instance, call `PrefabUtility.RecordPrefabInstancePropertyModifications`
on it (or edit through `SerializedObject` + `ApplyModifiedProperties`, which records it). Do not rely on
`Undo.RecordObject` here: through the command server it records no undo entry (`urp-postprocessing`'s
code-templates.md), and the rollback is the commit made first.

```csharp
using UnityEditor; using UnityEditor.SceneManagement; using UnityEngine;
public static class AgentEdit {
    public static void Run() {
        // Scene: the open scene (a scene that was already dirty holds the user's edits: ask first)
        var scene = EditorSceneManager.GetActiveScene();
        // an untitled scene would open a modal Save As dialog and block the main thread until the timeout
        if (string.IsNullOrEmpty(scene.path)) throw new System.InvalidOperationException("untitled scene: ask the user to save it");
        // ... change objects in it; after each component change on a prefab instance:
        // PrefabUtility.RecordPrefabInstancePropertyModifications(component);
        EditorSceneManager.MarkSceneDirty(scene); EditorSceneManager.SaveScene(scene);
        // Prefab asset: load, edit, save, unload
        const string path = "Assets/__GAME__/Prefabs/Thing.prefab";
        var root = PrefabUtility.LoadPrefabContents(path);
        // ... change root ...
        PrefabUtility.SaveAsPrefabAsset(root, path); PrefabUtility.UnloadPrefabContents(root);
        // ScriptableObject or other asset: dirty it, then save only it
        var so = AssetDatabase.LoadAssetAtPath<ScriptableObject>("Assets/__GAME__/Data/Thing.asset");
        // ... change so ...
        EditorUtility.SetDirty(so); AssetDatabase.SaveAssetIfDirty(so);
    }
}
```

Keep the one block the task needs (`script run` wants a single public static method). Never `SaveOpenScenes` or
`editor save_all`: they save the user's other edits too.

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
The space form needs CLI 1.0.0-beta.14 or newer (`unity self-update` after the user's yes; `upgrade` is its older alias); older ones accept only the dotted form
(`script.run`). Where `script run` is missing (an older CLI or Pipeline package), `unity command script eval_file <file>`
is the fallback when the project registers it (see `unity-cli`'s integration-advanced.md), with `script eval`'s
rules and timeout.

Pipeline command parameters are kebab-case (`--output-path`, `--max-resolution`, `--dry-run`); the snake_case
spellings older Pipeline packages and older docs use (`--save_path`, `--max_resolution`, `--dry_run`) are refused:
CLI 1.0.1 exits `2` with "has no parameter --dry_run. Did you mean --dry-run?".

## Game View capture

`capture game_view --output-path <path>` writes the PNG to an absolute path or one relative to the project root; keep
it outside `Assets/` (`Screenshots/x.png`) so no asset or `.meta` is made (the Pipeline's own parameter description;
not test-run here). Without `--output-path` the image comes back inline (`--max-resolution 512` keeps it small);
`--include-inline-image true` returns both. To look at the game, `play-capture` (below) is the default: it writes to
`Logs/agent/capture/`, which is not an asset folder. `--source screen`
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
  looks frozen without `runInBackground` (`editor set_auto_tick` keeps the Editor loop ticking but cannot undo that
  pause), and keyboard and pointer input are gated on Game View focus. This wins over `unity-cli`'s
  `playmode-verification-loop.md`: in a gamekit game do not enter Play Mode, set auto-tick or change `runInBackground`
  yourself; look with `play-capture` and hand the rest back.
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
so it runs in the foreground. A long capture or one right after a big compile (compile, then up to 30 s for Play Mode to
start, then the capture) can outrun that: give `gk-bridge play-capture 30` the `-t 240` option before the request,
with a Bash timeout of 250000 ms. A gk-bridge timeout leaves the capture running (`capture.log` `PENDING`, and any
request answers UNKNOWN "a play-capture is running"): wait, then read the head of `Logs/agent/capture.log`; do not send it again until it ends.

- Free, no need to ask: `refresh`, `compile ios|android|webgl`, `play-capture`.
- Ask first: `run-tests` (`unity-testing`), `build` (`platform-targets`).

`gk-bridge` with no argument prints its usage header, the source of truth for the requests and deadlines; if it and
this table ever disagree, trust it.

| Request | Result in |
|---|---|
| `refresh` (also checks `compile.log` is newer than every `.cs`/`.asmdef`) | `Logs/agent/bridge.log` (`REFRESHED ... no script changes`, or `... compiled` after the compile), and `Logs/agent/compile.log` if code changed |
| `fresh` (read-only: `refresh`'s verdict on the last refresh; nothing is sent to Unity) | Printed by `gk-bridge` from `Logs/agent/bridge.log` and `compile.log` |
| `compile ios` / `compile android` / `compile webgl` (player scripts for that target, no platform switch; `webgl` needs GameKit 0.1.3+, older ones answer unknown) | `Logs/agent/compile-player.log` |
| `run-tests` / `run-tests playmode` (a refresh gate runs first) | `Logs/agent/tests.log` |
| `play-capture` / `play-capture 8` (seconds, 1–30, default 3) | `Logs/agent/capture.log`, screenshots in `Logs/agent/capture/` |
| `build windows\|android\|aab\|ios\|webgl [dev]` | `Logs/agent/build.log` |

A request the bridge does not know is answered in `Logs/agent/bridge.log` (older copies: `tests.log`). Games made
before GameKit carry their own AgentBridge copy, which may know fewer requests; that game's CLAUDE.md lists them.

Outcomes worth knowing beyond pass and fail:

- A restarted Editor closes a build, test run, capture or `compile` it left open as `FAILED ... Editor restarted`:
  send the request again.
- `play-capture`: `STOPPED ... a domain reload (script recompile) ended the capture` is UNKNOWN, capture again;
  `FAILED ... Play Mode did not start within 30 s` is FAIL: read `console.log` for the handler or dialog that refused
  Play Mode.
- `build` imports changed files first and ends `SKIPPED` if Play Mode starts before it. `build` and `run-tests` both
  refuse while a scene has unsaved edits: `build` as `FAILED ... unsaved scene(s)` (a scene in the build list),
  `run-tests` as `SKIPPED ... unsaved scene(s): ...; save them first` in `tests.log` (any open scene; gk-bridge reads
  it as UNKNOWN). Either way ask the user to save it and do not resend in a loop; never save a scene you did not
  change (one you changed through `unity command` you save and commit with that change).

With the Editor closed, batch mode works and **locks the project**. A batch build is ask-first, the same as `build`
(gk-bridge answers UNKNOWN while the Editor is closed; that is no licence to build without a yes). `unity run` picks the Editor from
`ProjectSettings/ProjectVersion.txt` (no hard-coded install path to go stale after an upgrade) and adds `-batchmode`,
`-quit` and `-projectPath` itself (passing them after `--` fails with exit 6). `-buildTarget` opens the project on that
target, so the build skips a mid-build platform switch and its full reimport (batch mode never switches back, so the
next GUI open is on that target; switch back in Build Profiles if needed):

```powershell
unity run . --timeout 1800 --log-file Logs/build-batch.log --no-tail -- -buildTarget WebGL -executeMethod GameKit.Editor.BuildMenu.WebGL
```

Run it in a **background** Bash call (a foreground call stops at 600 s while the build keeps the project locked);
`--no-tail` keeps the full Editor log out of the tool output. Swap the pair for another target (`-buildTarget Android`
with `BuildMenu.Android`, `Win64` with `BuildMenu.Windows`). A failed build exits 1 (`BuildMenu` calls
`EditorApplication.Exit(1)`), a timeout exits 14; read the head of `Logs/agent/build.log` for the result, and
`Logs/build-batch.log` only to find why it failed.
