---
name: unity-cli
description: Reference for the Unity CLI itself - unity status/command/list, flags, output formats, exit codes, Safe Mode, Editor installs, modules, licenses, auth, logs. Use when a unity command or flag is unclear; Editor edits: unity-editor-cli.
allowed-tools:
  - Bash(unity --version)
  - Bash(unity status:*)
  - Bash(unity commands:*)
  - Bash(unity command --query:*)
  - Bash(unity skill show:*)
  - Bash(unity self-update --check:*)
  - PowerShell(unity --version)
  - PowerShell(unity status:*)
  - PowerShell(unity commands:*)
  - PowerShell(unity command --query:*)
  - PowerShell(unity skill show:*)
  - PowerShell(unity self-update --check:*)
---

# Unity CLI

> **In a gamekit game these project rules override the generic advice below** (copied from
> `unity@claude-plugins-official` 0.1.10-beta, docs for CLI `1.0.1`; `unity --version` shows what is
> installed, see the CHANGELOG):
>
> - **The installed CLI may be older than these docs:** confirm an unfamiliar flag or output field with
>   `unity <command> --help` before relying on it, and read a rejected flag or a missing field as an older CLI,
>   not a project problem.
> - **Editor edits:** follow `gamekit:unity-editor-cli`. Prefer `unity command script run --file` over
>   `script eval` (the "Joe" example below) for anything beyond one expression.
> - **Tests and builds:** through `gk-bridge` (`run-tests`, `build <target>`), asked first, as the game's CLAUDE.md
>   says. Do not start `unity test`, `unity build` or `unity run` against the project the Editor has open. The
>   "run the full suite before you hand the work back" advice below and in `build-run-test.md` does not apply:
>   never run the suite as a routine completion step (CLAUDE.md, `gamekit:unity-testing`).
> - **Play Mode checks:** `gk-bridge play-capture` plus a user Play Mode checklist (`gamekit:unity-editor-cli`,
>   `gamekit:implementation-verification`), not `playmode-verification-loop.md`: do not drive Play Mode, persist
>   `editor set_auto_tick` or change `runInBackground` yourself. So [Workflow](#workflow) step 5 ends at the console
>   check: never enter Play mode to chase a fault; the compile gate is `gk-bridge refresh`.
> - **Art:** 3D models and textures follow the Art section of the game's CLAUDE.md (headless Blender:
>   `blender-director`, `unity-export`; `art-pipeline` in a toon-art game). Skip the `ai` catalog plugin
>   (`common-workflows.md`); it is limited to Unity staff.
> - **Updating the CLI is the user's call:** `unity self-update` only after their yes (the "always use the latest
>   version" lines below mean check with `--check` and tell them), since unity-editor-cli's claims are checked
>   against a stamped CLI version.
> - **Editor and module installs are the user's call:** `unity install`, `install-modules`,
>   `editors upgrade|prune|module` and `uninstall` (multi-GB downloads, Unity's Editor EULA) run only after their
>   yes. Never pass `--accept-eula` for them; the examples that pass it (`editors-install.md`,
>   `projects-templates.md`, `common-workflows.md`) assume the user has accepted.
> - **One checkout, `main` only:** a gamekit game has no worktrees or feature branches (the game's CLAUDE.md), so
>   skip the "several worktrees" advice (`worktrees.md`) and `unity vcs git worktree`; `--project-path` still pins
>   the Editor.
> - **Agent shells:** a `--follow` or `--watch` stream never ends on its own; use `unity logs --level info`
>   without `--follow`, or run the stream in the background.
> - **`--caller plugin --skill <name>`:** optional labels in gamekit; the unity-editor-cli examples omit them.
> - **No Unity MCP server:** never run `unity mcp configure`.
> - **No agent setup on your own:** `unity skill install` / `refresh` / `sync` and `unity setup` write agent
>   configuration; run them only after the user's yes. To read an embedded skill without writing anything, use
>   `unity skill show` (`--list`, `--path <file>`, `--skill <name>`).
> - **New game:** `gamekit:new-game` (`new-game.ps1`), never the bootstrap recipe below (in
>   `common-workflows.md`); it gives the wrong template and no GameKit, skeleton or packs.
> - **Versions and targets in examples** (`6000.0.47f1`, `StandaloneLinux64`, `lts`) are placeholders: use the
>   game's `ProjectSettings/ProjectVersion.txt` and its targets (Windows, Android, iOS, WebGL).
>
> House edits a merge from upstream must reapply: this block; the `name`/`description` and `allowed-tools`
> narrowed to read-only `unity` forms (upstream grants all of Bash, which would pre-approve every command this block
> forbids), in Bash and PowerShell forms; upstream's main page is `unity-cli.md`, kept here as `SKILL.md`, with
> `CHANGELOG.md` at the skill root; the gamekit lines in the body below (Play Mode, `skill install --local`, new
> game); the gamekit notes at the top of `build-run-test.md`, `playmode-verification-loop.md` and
> [common-workflows.md](references/common-workflows.md).

**Always use the latest version of the Unity CLI unless you are told to use a
specific version.** Newer releases regularly add commands and output fields
these docs describe, so an outdated CLI fails in ways that read like the docs
being wrong. Check with `unity self-update --check --format json`.

**When you can run shell commands, use `unity command` and the rest of this CLI, not the Unity MCP server.** The CLI reaches more than the server's tools. MCP is for clients that have no shell.

Fetch a doc page directly (for example `WebFetch`) rather than searching (`WebSearch`). Replace `<VERSION>` first: the Unity version, eg `6000.3`, for docs.unity3d.com, or the package version, eg `1.2`, for a package page. These sites serve `.html` only, with no `.md` variant. Error codes, causes and fixes: [common-workflows.md](references/common-workflows.md#error-codes-cause-and-fix).

**Before you go forward with a workflow or diagnosis, open and read its page**: the reference file for the command group ([Commands](#commands)) or the recipe in [common-workflows.md](references/common-workflows.md). Name the files you read in your reply. Your training knowledge about Unity and this CLI might be out of date, incorrect, or for the wrong Unity version.

## Workflow

1. Check the CLI is installed and current ([Install the CLI](#install-the-cli-if-not-already-installed)).
2. Find the command ([search, don't grep help](#find-a-command-search-dont-grep-help)) and read its reference page.
3. If you will drive an Editor, run `unity command console status` first and keep its cursor.
4. Run the command, or drive the Editor with `unity command`.
5. Check the project has zero console errors with `unity command console status`, and read any with `console get -- --since <saved cursor> --level error`. Stop there unless the user asked for proof or you suspect a specific fault. To chase a fault in a change to runtime behaviour, enter Play mode once and read state with `unity command script eval` instead of adding logging, and take no screenshots.
6. If the fix doesn't work, go back and reread the reference page for that command group before trying again.

## Find a command: search, don't grep help

**Never filter `unity --help` or a group's help with `grep`.** Help is long, and a grep over it drops the match or the context around it. Use the CLI's own search:

```bash
unity commands --grep license                 # built-in commands, plugins and the connected Editor's Pipeline commands
unity command --query screenshot              # the same search
```

`unity commands --grep <pattern>` and `unity command --query <term>` are one search. It covers the CLI's built-in commands, the plugin catalog (installed or not) and the Pipeline commands of the live connected Editor, best match first. Plain words each match in any order; regex characters make it a regular expression (Rust `regex` syntax, case-insensitive; no lookaround or backreferences, which are refused with a usage error). Each row says how to run it (`invoke`): `unity projects link cloud`, `unity command create_gameobject`, `unity <id>` for an installed plugin, or `unity plugin install <id>` for one not yet installed. In `--format json` each row also carries `kind` (`command`, `plugin`, `pipeline`), `path`, `description` and `matchedOn` (`name`, `description` or `option`), so act on `invoke` rather than parsing the table.

- **Search before you work around the CLI or tell the user it can't help.** A request that names a Unity service, store or product feature (finding Asset Store assets, generating a texture, a cloud build) may be served by a catalog plugin that isn't installed yet, and nothing else on the machine will say so. Search with the request's own words (`unity commands --grep "asset store"`). A row whose `invoke` is `unity plugin install <id>` is that plugin: tell the user, and ask before installing it ([Use a catalog plugin](references/common-workflows.md#use-a-catalog-plugin-for-a-task-the-built-in-commands-dont-cover)).
- Use `unity command --query <term>` to search a specific Editor (`--project-path <project>`) or a Player (`--runtime <pattern>`, e.g. `unity command --query screenshot --runtime MyGame`).
- `commands --grep` waits at most 3 seconds for the Editor; `command --query` waits for it. When the Editor was not searched, a last line says why (no Editor, no answer in time, several Editors) and what to run. Wait for the Editor first with `unity status --until-ready --project-path <project>`: before it connects, no Pipeline row is not proof nothing exists.

Fields and flags: [integration-advanced.md](references/integration-advanced.md#querying-the-command-list).

## Drive a running Unity Editor (if one is open)

**If a Unity Editor is open on this machine, this CLI can control it live** — create and modify GameObjects, edit scenes and assets, inspect the hierarchy, and run arbitrary C# — through the project's **Pipeline** package (`com.unity.pipeline`). This runs entirely on your local machine, in your own user account, against your own open Editor: it is not remote access and grants no privilege you don't already have at your own terminal. When an Editor is available, drive it instead of hand-editing scene or asset files.

```bash
unity status                    # confirm a connected Editor (look for state "ready")
unity command                   # list the commands the Editor exposes
unity command editor.playmode start   # run one — e.g. enter Play mode
unity command editor.playmode start --help   # its parameters, read from the Editor
# Run arbitrary C# — e.g. add a GameObject named "Joe" — when the Editor exposes script eval:
unity command script eval --caller plugin --skill unity-cli 'new UnityEngine.GameObject("Joe");'
```

**Pass `--caller plugin --skill <name>` on every `unity command` invocation.** `--skill` is the
skill whose instructions produced the call, so a task skill that sends you here passes its own name
rather than `unity-cli`. The flags are inert to the command itself; they only label the invocation.

> **Verifying a running game, not just editing a scene?** (In a gamekit game: `gk-bridge play-capture` and a
> user checklist instead, see the block at the top.) Entering Play mode is setup, not proof:
> an unfocused Editor or a locked desktop can freeze at frame 1 while `unity status` still reports it
> as playing, and a screenshot can render a frozen frame that looks alive, or a flat color. The
> ordered recipe for playing, confirming the game is actually advancing, capturing the view, reading
> the console, and tuning it live with `script eval` is in
> [playmode-verification-loop.md](references/playmode-verification-loop.md).

### More than one Editor open? Pass `--project-path`

Every Editor-driving command takes `--project-path <path>`. **Pass it whenever more than one Editor may be running** — without it the CLI targets the Editor whose project contains the current directory, so the target follows the shell's cwd:

```bash
unity command editor.playmode start --project-path /path/to/MyProject
```

To pin one Editor when several share a project (worktrees, duplicate projects, Multiplayer Play Mode players), `unity command`, `list`, `job` and `mcp` also take `--port <number>`, `--pid <number>` or `--instance <name>` (the MPPM instance name or `vpId`); a pin that matches no running Editor exits 12 with `EDITOR_NOT_RUNNING`. A `unity status` instance's `project` field is what `--project-path` takes. For `unity command`/`list`/`job`/`mcp`, matching no running project fails with `AMBIGUOUS_EDITOR` and lists the candidates. [Details](references/integration-advanced.md#targeting-one-of-several-running-editors).

**Several worktrees or agent sessions? One Editor per worktree.** Pin every Editor call to your own project with `--project-path <full path>` or `UNITY_PROJECT_PATH`, and never drive an Editor open on a sibling checkout, because it edits that checkout. Full recipe: [worktrees.md](references/worktrees.md).

Requires the project's `com.unity.pipeline` package (Unity 6.0+) — add it once with `unity pipeline install`. Full details — launching a batch-mode Editor to drive, `unity command` tool discovery, and authoring custom `[CliCommand]` tools — are in [integration-advanced.md](references/integration-advanced.md).

The package also ships a deeper `unity-pipeline` agent skill, invisible to clients inside `Library/PackageCache` — in a project with the package, `unity skill install <client> --local` mirrors it beside this skill. In a gamekit game that writes a second `unity-cli` into the game's `.claude/skills/`, so do not run it; read the package's skill straight from `Library/PackageCache/com.unity.pipeline@*/.claude/skills/unity-pipeline/SKILL.md` instead.

> **Can't connect / commands time out? Check for Safe Mode first.** C# compile errors boot the Editor into **Safe Mode**, where the Pipeline package doesn't load, so `unity command` and `unity recompile` can't connect (`unity recompile` exits `12`). Run `unity status`: it reports Safe Mode and lists the compile errors (`safeMode.compileErrors` under `--format json`). Fix them and the Editor leaves Safe Mode. Full loop: [integration-advanced.md → Recovering from Safe Mode](references/integration-advanced.md#recovering-from-safe-mode-connection-fails-because-of-compile-errors).

> **Running as a sandboxed coding agent and `unity status` reports no instances?** A restrictive sandbox can hide an Editor that is genuinely running from this CLI's view of it — don't treat that alone as proof the Editor is down. Full detail in [integration-advanced.md → Sandboxed agent tooling can hide a running Editor](references/integration-advanced.md#sandboxed-agent-tooling-can-hide-a-running-editor).

> **A call timed out, or the Editor's lifecycle failed? Tell the user, don't silently work around it.** First rule out [Safe Mode](references/integration-advanced.md#recovering-from-safe-mode-connection-fails-because-of-compile-errors), a sandbox, and an Editor that is still importing or loading. Read `errors[0].code` under `--format json`, and give a slow import a longer `--timeout`. If it is still one of these, report it:
>
> - a command that times out
> - an Editor that never reaches `ready` under `unity status --until-ready` (exit 6)
> - a connection that drops mid-command
> - an Editor that quits or restarts under you
> - a `unity open` that never produces an Editor
>
> Don't quietly retry in a loop, switch to another Editor, or fall back to hand-editing scene and asset files. Say what you ran, what failed and what you already tried. Then offer to file it with `unity bug --area pipeline-package` (`--area editor` when the Editor itself quit or never started), and ask first: `unity bug` sends logs to Unity, so never run it on your own initiative.

## Install the CLI (if not already installed)

First check if the CLI is available:

```bash
which unity && unity --version
```

If not found, install it:

**macOS / Linux**
```bash
curl -fsSL https://unity.com/install.sh | bash
```

**Windows (PowerShell)**
```powershell
irm https://unity.com/install.ps1 | iex
```

After installing, open a new shell so `unity` is on PATH, then verify with `unity --version`. If the install script fails or the binary is still not found, tell the user and stop; if the command itself fails with a permissions error or crash, the installation may be broken — suggest re-running the install script.

---

## Global flags

Every command accepts `--format json|ndjson|tsv`, `--non-interactive`, `--proxy` and more. Confirmation flags such as `--yes` are command-specific, not global: check the command's own help. Use `--format json` whenever you parse output. Full list: [global-flags-env.md](references/global-flags-env.md#global-flags).

## Environment variables

The CLI reads `UNITY_*` variables for credentials, proxies, paths and CI behavior. Full list: [global-flags-env.md](references/global-flags-env.md#environment-variables).

## Getting help

Append `-h` or `--help` to any command or subcommand, at any level: `unity --help`, `unity projects create --help`.

`unity command <name> --help` asks the connected Editor for that command and prints its usage, description and parameters (name, type, required, default); a group name alone (`unity command editor.playmode --help`) lists the group's commands. The Editor gets at most 3 seconds. With no Editor, or no such command, the generic `unity command` help prints with one line saying why the parameters are missing and what to run. Help exits 0 either way and runs nothing.

Not sure which command? [Search, don't grep help](#find-a-command-search-dont-grep-help). `unity --help` and the unknown-command error end with that pointer too. Each search ends by naming the source it skipped and the command that searches it (`data.hint` in JSON): follow it before concluding nothing exists.

## Exit codes

`0` is success; any other code is a failure with a stable meaning (for example `7` for a network failure, `12` when no running Editor answers, `11` for a missing project, release or module). Branch on the code, not on message text. The table is in [exit-codes.md](references/exit-codes.md).

## Guardrails

- **Do only what's asked. Don't change unrelated assets or files. Avoid long explanations.** Editors, licenses and projects are the user's own.
- **Never leave verification code in the user's script. Never build logging or detection they didn't ask for.**
- **Ask before** installing or uninstalling an Editor, activating or returning a license, signing in or out, publishing, or running a command that deletes or overwrites project files, because these are slow or hard to undo.
- **Make a restore point before changing a project**: confirm a clean commit (`git status`) or a Unity Version Control checkin, and tell the user how to return to it.
- **Never run `console clear`**: it also deletes the user's own entries. Read only your own entries, from a cursor you saved before your first Editor operation.
- **Finish with the console check in [Workflow](#workflow) step 5** and a short report: what you ran, what changed, what failed or was skipped, and the next step.

## Commands

The full per-command reference — syntax, flags, and examples — lives in grouped files under
[`references/`](references/). **Read the file for the command group you need**; all the global
flags, environment variables, and exit codes above apply throughout. Every command also supports
`-h` / `--help` (see [Getting help](#getting-help)). What changed in this skill between CLI
releases: [CHANGELOG.md](CHANGELOG.md).

| Commands | Reference file |
|---|---|
| `auth` (login / logout / status / list / switch / default / consumers / revoke), `license` (activate / return / server), `cloud` (org / project) | [auth-license-cloud.md](references/auth-license-cloud.md) |
| `pipeline cloud-build` (targets incl. groups, create, update, auditlog / builds incl. steps, timeline, failures, artifacts, log, download, start, cancel / credentials upload / connections / scm check-url / org free-tier / project / tooling), `pipeline automation` (apps / pipelines incl. trigger / jobs incl. watch, logs, terminate, resume, approve, reject / automations / bots / profiles / templates, plus `apps versions`, `pipelines versions`, `jobs stats`) | [cloud-automation.md](references/cloud-automation.md) |
| `editors` (list / running / add / default / path / install-path / info / upgrade / prune / verify / module), `install`, `uninstall`, `modules`, `install-modules`, `terms` (accept / status) | [editors-install.md](references/editors-install.md) |
| `projects` (list / create / clone / open / link / require / upgrade / export / import / pin / size / clean / exec; its help reads "Create, open, upgrade, and link local Unity projects (Unity Cloud, GitHub/GitLab)", so linking a folder to Unity Cloud is `projects link cloud`, not `cloud`), `open`, `close`, `releases`, `templates` (list / info / create / pack / delete), `assets` (`inspect` / `export`) | [projects-templates.md](references/projects-templates.md) |
| `config` (proxy / update-check / accelerator / get / set / list / unset / resolve), `context` (save / use / list / current / delete), `hub install` | [config-hub.md](references/config-hub.md) |
| `run`, `test`, `build` (+ `build run`), `recompile`, `watch` (`test`) | [build-run-test.md](references/build-run-test.md) |
| `logs`, `doctor`, `env`, `version`, `cache`, `ci init`, `analytics`, `changelog`, `docs` (+ `toc`), `language`, `completion`, `bug`, `self-update`, `self-uninstall`, `diagnose proxy`, `diagnose accelerator`, `diagnose update` | [diagnostics-maintenance.md](references/diagnostics-maintenance.md). To find, cite and version-match Unity docs: [docs-workflow.md](references/docs-workflow.md) |
| `mcp` (+ `configure`), `setup claude` / `codex` / `grok` / `antigravity` / `copilot` / `qwen` / `vscode` / `opencode`, `skill` (install / refresh / show), `plugin` (install / remove / upgrade / list / changelog), local `pipeline` (install / upgrade / list / list-versions), `command` / `commands` / `status` / `list`, `job` (status / wait / cancel), answering an open modal dialog (`command editor dialog` / `editor dialog answer`, or `editor.dialog list` / `answer` / `dismiss`), `shell` | [integration-advanced.md](references/integration-advanced.md) |
| `vcs` — `setup` / `status` / `sync` / `switch` / `doctor` / `providers` / `merge-setup` / `conflicts` / `explain` / `resolve` / `diff` / `blame` / `summarize` / `affected` / `hooks`, `vcs git` (`migrate-lfs` / `worktree`), `vcs uvcs` (`locks` / `changesets` / `review`) | [version-control.md](references/version-control.md) |
| `collaboration` (alias `collab`) — `annotations` / `attachments` / `thumbnail` / `reactions` / `read` / `subscribe` / `jira` | [collaboration.md](references/collaboration.md) |

## Common workflows

Step-by-step recipes live in [common-workflows.md](references/common-workflows.md). Read it before you attempt one of these:

- inspect and run cloud builds and Pipeline Automation jobs
- edit a scene, GameObject, or asset (`unity status` first)
- use a catalog plugin for a task the built-in commands don't cover
- bootstrap a new project from scratch, and set up source control (**A gamekit game starts with `gamekit:new-game` instead.**)
- find and install a missing Editor, open a project with the right Editor
- CI: activate a license, build, run tests and publish results
- debug the CLI

## Notifications

A `--format json` or `--format ndjson` envelope may carry a `notifications`
array: advisories about the user's environment rather than about the command
you ran. **When one is present, tell the user** — they have no other way to see
it, because the human-facing equivalent is a terminal banner that never reaches
you.

The key is absent when there is nothing to report, so read it as
`envelope.notifications ?? []`.

```jsonc
{
  "code": "CLI_UPDATE_AVAILABLE",
  "message": "A new version of the Unity CLI is available: 1.0.0-beta.8 → 1.0.0-beta.9",
  "data": { "current": "1.0.0-beta.8", "latest": "1.0.0-beta.9" },
  "remediation": { "command": "unity self-update", "requiresUserApproval": true }
}
```

Branch on `code`; `message` is localized and meant for display. `data` is
shaped per `code`.

`PLUGIN_UPDATE_AVAILABLE` means an installed plugin has a newer version.
`data` is `{ "plugin": "<id>", "current": "…", "latest": "…" }`, and the
remediation is `unity plugin upgrade <id>`. There is one entry per outdated
plugin.

`remediation` says how the notification gets resolved. It may be absent, which
means the notification is informational and there is nothing to run.

`FEX_EMU_EXPERIMENTAL` means the command ran, or will run, the x86_64 Editor
through FEX-Emu on Linux arm64. Tell the user it is experimental and
unsupported and that C# script compilation is known to crash there.

**`requiresUserApproval: true` means do not run `remediation.command`
yourself.** Surface the notification and the command, and let the user decide.

---

## Notes

Short-flag rules, prompt suppression for CI, and other cross-cutting details: [notes.md](references/notes.md). Read it when a flag or prompt behaves unexpectedly.

