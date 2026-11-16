# unity-game-template

The source every game repo starts from, not a game. README.md (Turkish) explains it for people; this file is how to
work on it. Games made from it live in sibling folders under `C:\GitHub`.

## Layout: three parts that reach games differently

| Part | Folder | Reaches games |
|---|---|---|
| Copy: skeleton, CLAUDE.md, settings, packs | `project/`, `packs/` | New games at `new-game.ps1`; old ones through `/gamekit:sync-template` |
| GameKit package: AgentBridge, BuildMenu, ProjectSetup, FrameLog, SafeAreaFitter | `packages/com.yunusburkut.gamekit/` | A game moves its `#gamekit-vX.Y.Z` tag in `Packages/manifest.json` |
| gamekit plugin: skills, agents, hooks | `plugin/` (marketplace: `.claude-plugin/`) | Automatically from `main` (`autoUpdate`, no `version` on purpose) |

When I ask for a new game, follow the `gamekit:new-game` skill: it runs `new-game.ps1` without `-GitHub` (a local
repo only), writes my idea into DESIGN.md, opens Unity and starts the shaping session; it publishes
(`gh repo create <Name> --private --source <dest> --remote origin --push`) only after my yes.

`__GAME__` and `__COMPANY__` are placeholders that `new-game.ps1` fills in; keep them in every file under `project/`
and `packs/`. A pack may add `packages.json` (UPM deps) and `[ProjectSetupStep]` Editor methods; its README.md and
`examples/` are never copied, except that `new-game.ps1` lifts two parts of the README into the game's CLAUDE.md: the
fenced block under `## CLAUDE.md'ye eklenecek satır` (into `## Packs`) and every ```` ```markdown ```` block that starts
with a `## ` heading (coop-multiplayer's `## Networking`, which net-auditor reads). Keep those headings and fences.
A pack README's first paragraph under its title says in a sentence what the pack is for; new-game offers packs from it.

## Git

Everything goes straight on `main`: no branches, no PRs. Commit subject `area: summary` (`project:`, `plugin:`,
`tools:`, `gamekit:`, `packs:`), a body that says why, and a `Verified:` line naming what was run.

## Checking a change

| Changed | Run |
|---|---|
| Anything (one entry for all checks below) | `.\test-all.ps1`: every check that needs no Unity (static checks, the headless Blender run, the sync-template pipeline, the user-level layer, the pack merge dry run, hooks, plugin validate); the list and the run time are in its help block (`Get-Help .\test-all.ps1`). It takes 1-2 min with Blender installed and longer on a busy machine (nearly 5 min seen): run it with `run_in_background`, never on the default 120 s tool timeout. `-Full` adds `test-template.ps1` |
| `project/`, `packs/`, `packages/`, `new-game.ps1` | `.\test-template.ps1` (launches Unity, about 5-10 min: run it, and `test-all.ps1 -Full`, with `run_in_background`; each Unity launch is killed after 30 min, `-TimeoutMinutes`; `-Packs <changed pack>`, `-Tests` for the game's tests) |
| `plugin/` | `claude plugin validate plugin` (the missing-version warning is intended), then `claude plugin update gamekit@unity-game-template` |
| `plugin/hooks/`, a skill's `references/` index | Also `powershell -NoProfile -ExecutionPolicy Bypass -File plugin\test-hooks.ps1` (fixed payloads through the hooks, the genre index and source keys); a new hook path gets a case there |
| A skill in `plugin/skills` added, renamed, removed, or its use changed | Also update `NOTES` in `~/.claude/mods/skill-notlari/hooks/register.tsx` (the "Skill notları" button above the prompt in template and game sessions; no repo, so no commit), then `claude plugin test ~/.claude/mods/skill-notlari`; the user runs `/reload-plugins` |

Never open `project/` itself in Unity: it is a template with placeholders, not a project. `test-template.ps1` makes a
real game in `%TEMP%` and deletes it.

## Releasing GameKit

A git package is immutable in games, so its `.meta` files are committed here. `test-template.ps1` points the game at
this folder (`file:`), so Unity writes the `.meta` of a new GameKit file straight into `packages/`; commit it with the
file. To release:

1. Bump `version` in `packages/com.yunusburkut.gamekit/package.json`.
2. Grep `plugin/skills` for what ProjectSetup, BuildMenu and AgentBridge do (e.g. platform-targets "Orientation and
   window") and update those claims, version-aware, in the same commit; no check compares them.
3. Commit, `git tag -a gamekit-vX.Y.Z -m "GameKit X.Y.Z"`, push `main` and the tag.
4. Point `project/Packages/manifest.json` at the new tag so new games get it.

Moving a MonoBehaviour into GameKit changes its script GUID (scenes show "Missing Script"); older games keep their own
copies until migrated one by one.

## Windows gotchas

- PowerShell 5.1: `ConvertTo-Json` escapes `& ' < >` as `\u00XX` and writes CRLF; fix both before writing JSON. No
  Node or system Python on this machine; run Python through Blender
  (`blender --background --factory-startup --python-exit-code 1 --python <file>`).
- Blender MCP `*_for_cli` calls time out unless the extension's `blmcp\tools_helpers\blender_cli.py` passes
  `stdin=subprocess.DEVNULL` to `subprocess.run`; an extension update drops this local patch. Recipe: README.md,
  Blender step 5; `test-all.ps1` checks it.
- The user-level layer (`~/.claude` settings.json with the hook registrations, plugins and output style, rules, hooks,
  grill-me, orchestrate, Blender skills) is in no repo; README.md
  "## Global Claude katmanı (`~/.claude`" lists it for a new machine; `test-all.ps1` checks the pieces are present.
- Paths under a game's `Library\PackageCache` pass 260 characters: delete with `cmd /c rmdir /s /q "\\?\<path>"`.
- Commit messages: write them to a file and use `git commit -F <file>`.
