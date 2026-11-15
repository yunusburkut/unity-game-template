# unity-game-template

The source every game repo starts from, not a game. README.md (Turkish) explains it for people; this file is how to
work on it. Games made from it live in sibling folders under `C:\GitHub`.

## Layout: three parts that reach games differently

| Part | Folder | Reaches games |
|---|---|---|
| Copy: skeleton, CLAUDE.md, settings, packs | `project/`, `packs/` | New games at `new-game.ps1`; old ones through `/gamekit:sync-template` |
| GameKit package: AgentBridge, BuildMenu, ProjectSetup, FrameLog, SafeAreaFitter | `packages/com.yunusburkut.gamekit/` | A game moves its `#gamekit-vX.Y.Z` tag in `Packages/manifest.json` |
| gamekit plugin: skills, agents, hooks | `plugin/` (marketplace: `.claude-plugin/`) | Automatically from `main` (`autoUpdate`, no `version` on purpose) |

When I ask for a new game, run `new-game.ps1` without `-GitHub` (a local repo only); publish it
(`gh repo create <Name> --private --source <dest> --remote origin --push`) only after my yes.

`__GAME__` and `__COMPANY__` are placeholders that `new-game.ps1` fills in; keep them in every file under `project/`
and `packs/`. A pack may add `packages.json` (UPM deps) and `[ProjectSetupStep]` Editor methods; its README.md and
`examples/` are never copied.

## Git

Everything goes straight on `main`: no branches, no PRs. Commit subject `area: summary` (`project:`, `plugin:`,
`tools:`, `gamekit:`, `packs:`), a body that says why, and a `Verified:` line naming what was run.

## Checking a change

| Changed | Run |
|---|---|
| Anything (one entry for all checks below) | `.\test-all.ps1` (static checks incl. CCGS licence citations; when Blender is installed a headless `blender --background` run that compiles every tracked and user-level Blender `.py` and exports an FBX, plus the MCP extension patch check; GameKit `.meta`; a pack merge dry run of every pack through `new-game.ps1 -NoSetup -NoGit`, without Unity; hooks; plugin validate; about 20-40 s with Blender installed); `-Full` adds `test-template.ps1` |
| `project/`, `packs/`, `packages/`, `new-game.ps1` | `.\test-template.ps1` (launches Unity, about 5-10 min: run it, and `test-all.ps1 -Full`, with `run_in_background`; each Unity launch is killed after 30 min, `-TimeoutMinutes`; `-Packs <changed pack>`, `-Tests` for the game's tests) |
| `plugin/` | `claude plugin validate plugin` (the missing-version warning is intended), then `claude plugin update gamekit@unity-game-template` |
| `plugin/hooks/`, a skill's `references/` index | Also `powershell -NoProfile -ExecutionPolicy Bypass -File plugin\test-hooks.ps1` (fixed payloads through the hooks, the genre index and source keys); a new hook path gets a case there |

Never open `project/` itself in Unity: it is a template with placeholders, not a project. `test-template.ps1` makes a
real game in `%TEMP%` and deletes it.

## Releasing GameKit

A git package is immutable in games, so its `.meta` files are committed here. `test-template.ps1` points the game at
this folder (`file:`), so Unity writes the `.meta` of a new GameKit file straight into `packages/`; commit it with the
file. To release:

1. Bump `version` in `packages/com.yunusburkut.gamekit/package.json`.
2. Commit, `git tag -a gamekit-vX.Y.Z -m "GameKit X.Y.Z"`, push `main` and the tag.
3. Point `project/Packages/manifest.json` at the new tag so new games get it.

Moving a MonoBehaviour into GameKit changes its script GUID (scenes show "Missing Script"); older games keep their own
copies until migrated one by one.

## Windows gotchas

- PowerShell 5.1: `ConvertTo-Json` escapes `& ' < >` as `\u00XX` and writes CRLF; fix both before writing JSON. No
  Node or system Python on this machine; run Python through Blender
  (`blender --background --factory-startup --python-exit-code 1 --python <file>`).
- Blender MCP `*_for_cli` calls time out unless the extension's `blmcp\tools_helpers\blender_cli.py` passes
  `stdin=subprocess.DEVNULL` to `subprocess.run`; an extension update drops this local patch. Recipe: README.md,
  Blender step 5; `test-all.ps1` checks it.
- The user-level layer (`~/.claude` rules, hooks, grill-me, orchestrate, Blender skills) is in no repo; README.md
  "Global Claude katmani" lists it for a new machine.
- Paths under a game's `Library\PackageCache` pass 260 characters: delete with `cmd /c rmdir /s /q "\\?\<path>"`.
- Commit messages: write them to a file and use `git commit -F <file>`.
