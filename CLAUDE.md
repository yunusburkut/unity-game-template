# unity-game-template

The source every game repo starts from, not a game. README.md (Turkish) explains it for people; this file is how to
work on it. Games made from it live in sibling folders under `C:\GitHub`.

## Layout: three parts that reach games differently

| Part | Folder | Reaches games |
|---|---|---|
| Copy: skeleton, CLAUDE.md, settings, packs | `project/`, `packs/` | New games at `new-game.ps1`; old ones through `/gamekit:sync-template` |
| GameKit package: AgentBridge, BuildMenu, ProjectSetup, FrameLog, SafeAreaFitter | `packages/com.yunusburkut.gamekit/` | A game moves its `#gamekit-vX.Y.Z` tag in `Packages/manifest.json` |
| gamekit plugin: skills, agents, hooks | `plugin/` (marketplace: `.claude-plugin/`) | Automatically from `main` (`autoUpdate`, no `version` on purpose) |

`__GAME__` and `__COMPANY__` are placeholders that `new-game.ps1` fills in; keep them in every file under `project/`
and `packs/`. A pack may add `packages.json` (UPM deps) and `[ProjectSetupStep]` Editor methods; its README.md and
`examples/` are never copied.

## Git

Everything goes straight on `main`: no branches, no PRs. Commit subject `area: summary` (`project:`, `plugin:`,
`tools:`, `gamekit:`, `packs:`), a body that says why, and a `Verified:` line naming what was run.

## Checking a change

| Changed | Run |
|---|---|
| `project/`, `packs/`, `packages/`, `new-game.ps1` | `.\test-template.ps1` (about 5 min; `-Packs <changed pack>`, `-Tests` for the game's tests) |
| `plugin/` | `claude plugin validate plugin` (the missing-version warning is intended), then `claude plugin update gamekit@unity-game-template` |
| `plugin/hooks/` | Also pipe a sample hook JSON into the script (`tool_name`, `tool_input`, `cwd`) and read its output |

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
  Node or Python on this machine.
- Paths under a game's `Library\PackageCache` pass 260 characters: delete with `cmd /c rmdir /s /q "\\?\<path>"`.
- Commit messages: write them to a file and use `git commit -F <file>`.
