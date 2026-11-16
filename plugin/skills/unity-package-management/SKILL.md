---
name: unity-package-management
description: Use for "install a Unity package", "add com.unity.*", "paket ekle", "hangi paketler", "which packages for a [genre] game" - adding, removing, upgrading or verifying UPM packages (live Editor or headless/CI), or upgrading the Unity Editor.
allowed-tools:
  - Read
  - Bash(unity command package search:*)
  - Bash(unity command package list:*)
  - Bash(unity command package status:*)
  - Bash(unity editors path:*)
  - PowerShell(unity command package search:*)
  - PowerShell(unity command package list:*)
  - PowerShell(unity command package status:*)
  - PowerShell(unity editors path:*)
---

# Unity Package Management (live Editor first, headless C# Client API for CI)

Add, remove, upgrade, and discover UPM (Unity Package Manager) packages through Unity's own resolver: the Pipeline
`package` commands in the live Editor, or `UnityEditor.PackageManager.Client` headless from the terminal or CI. Do
**not** hand-edit `Packages/manifest.json` to add or upgrade a **registry** package by id — the resolver handles
dependencies and compatible versions correctly, whereas manual edits routinely break resolution. A registry id with a
pinned version (the [Checked extras](references/select-packages.md#checked-extras-with-pinned-install-lines) rows)
goes through the same route as `<id>@<version>`. Plain manifest text on purpose, and only these:

- moving the GameKit `#gamekit-vX.Y.Z` tag (**`gamekit:sync-template`**);
- a pack's `packages.json` lines, `scopedRegistries` included: `new-game.ps1 -Packs` merges them into a new game, and
  an existing game takes the exact same lines by hand;
- a package from a scoped registry (PrimeTween): the resolver takes only an id, so the `scopedRegistries` entry and
  its dependency line are manifest text. A git URL is not an exception: `package add` and `Client.Add` take it.

After any manifest edit, make Unity resolve it and read the outcome. Editor open: `unity command package resolve`, then
`unity command package status` until it reads `completed` or `failed` (a failure carries the UPM error), then
`gk-bridge refresh` must exit 0 (a clean compile alone does not prove UPM resolved the new entry). Editor closed: the
headless run resolves it. Either way, check that `Packages/packages-lock.json` lists the package.

**Ask the user before adding any package** (the game's CLAUDE.md keeps the manifest deliberately small), and check
`packs/` in unity-game-template first: a pack's `packages.json` is the source for its dependencies (see
[references/select-packages.md](references/select-packages.md)). The checked extras (PrimeTween, Localization,
IAP, the in-game debug console, Microsoft.Unity.Analyzers), release-automation tools and the packages not taken live
there too, under [Checked extras](references/select-packages.md#checked-extras-with-pinned-install-lines).

This complements the **`unity-cli`** skill (editor install, project creation, build/test). The `unity` CLI itself has
no package command; the Pipeline package (`com.unity.pipeline`, pinned in the template manifest) adds
`unity command package ...` to a running Editor, and that is the first route. With the Editor closed, the Editor's C#
Client API runs headless ([references/headless.md](references/headless.md)).

> **Local gamekit adaptations** (this skill is a copy of the official Unity plugin's skill; re-apply these after
> refreshing it from upstream): the manifest-edit exceptions and ask-first rule above, the "Editor open?" branch with
> the Pipeline `package` route, the headless material moved to `references/headless.md` (with the outer time limit),
> PowerShell recipes instead of `python3`, neutral version placeholders, the **Upgrading the Editor** section, the
> pack-first rule, template handoffs, the **Checked extras** section in `references/select-packages.md`, and
> `allowed-tools` narrowed to read-only forms (upstream grants all of Bash, PowerShell and Write, which would
> pre-approve the package adds the ask-first rule holds back).

## Editor open? Pick the route first

In this template the user's Editor is normally open. Unity refuses a second instance on the same project, so the
batchmode route fails or hangs while it is. The Editor is open when `unity status --project-path <project>` lists an
instance for the project, or when `<project>/Temp/UnityLockfile` exists **and** is held: Unity keeps it open without
sharing (gk-bridge's `editor_open` test). A lock file that opens fine is stale from a crashed Editor, so the Editor is
closed.

- **Editor open**: use the Pipeline `package` commands (com.unity.pipeline 0.10.0-exp.1 and newer). The
  `--caller plugin --skill unity-package-management` labels are optional in gamekit (see **`unity-cli`**), so the
  examples omit them. One package per call:

  ```powershell
  unity command package search --query <id>                         # id exists; versions; installed flag
  unity command package add --name <id> --dry-run true              # preview the plan, changes nothing
  unity command package add --name <id> --confirm true --wait true  # apply; blocks up to 300 s
  unity command package status                                      # completed | failed, with the error
  unity command package list                                        # the resolved set (indirect too)
  ```

  A bare `<id>` resolves the latest compatible release and is the default. Write `<id>@<version>` only for a
  [Checked extras](references/select-packages.md#checked-extras-with-pinned-install-lines) row, a required minimum, an
  upgrade or a pin. `--name` also takes a git URL or `file:../Path`; `package remove --name <id>` takes the same `--dry-run`,
  `--confirm` and `--wait`. Without `--confirm true` the call is refused; `busy` means another package operation is
  running, so poll `package status` first. Upgrade or pin = `add` with the new `<id>@<version>` (take the version from
  `package search`, never from memory). The add triggers a recompile and domain reload that can drop the synchronous
  reply: `package status` reads a Temp file that survives it, so it is the result to trust. Then `gk-bridge refresh`
  must exit 0. The parameter spellings are the command's own (`name`, `confirm`, `dry-run`, `wait`, `timeout` in
  0.10.0-exp.1, checked against that version's `PackageManagerCommand.cs`; 0.9.x spelled them `identifier` and
  `dry_run`); if one is refused, read them from `unity command --query package`.

  **Fallback**, for a Pipeline package with no `package` group (`unity command --query package` finds nothing): write
  a one-method script **outside** `Assets/` (the scratchpad directory) that only fires the request, and run it with
  `unity command script run` (see **`gamekit:unity-editor-cli`**):

  ```csharp
  using UnityEditor.PackageManager;

  public static class AddPackagesLive
  {
      // Fire and return: the live Editor keeps ticking and finishes the resolve. Never call
      // EditorApplication.Exit here, it would close the user's Editor.
      public static void Run() =>
          Client.AddAndRemove(packagesToAdd: new[] { "<id>" }, packagesToRemove: new string[0]);
  }
  ```

  ```powershell
  unity command script run --file <absolute path to AddPackagesLive.cs> --timeout 60
  ```

  Then verify: each id is in `Packages/manifest.json`, `Packages/packages-lock.json` is newer than the manifest, and
  `gk-bridge refresh` exits 0. An unfocused Editor may not finish the resolve (not probed on 6000.6): if the lock file
  does not update, ask the user to focus Unity, or to add the package themselves (**Window > Package Manager > + >
  Add package by name**).
- **Editor closed** (CI, a throwaway project): the headless installer, registry search, launcher (with its outer time
  limit), verification and the headless import/save are in [references/headless.md](references/headless.md). In
  short: an `Editor/` script calls `Client.AddAndRemove` and exits itself, and the Editor binary runs in `-batchmode`
  **without** `-quit`, because `unity run` injects `-quit` and quits before UPM resolves.

## When to use

- Add / remove / upgrade one or more packages in an existing or freshly-created project.
- Set up a project's packages non-interactively in CI.
- Verify a package id exists, or find its available versions, before depending on it.
- Decide which packages a game actually needs — see
  [references/select-packages.md](references/select-packages.md).

## Choosing what to install

Install what the project actually needs, not everything; prefer packages the chosen template
already provides (URP templates already include the render pipeline, Input System, etc.). The
genre / look / platform / monetization → package mapping, plus how to search the registry, is
in [references/select-packages.md](references/select-packages.md). Produce a **deduplicated
list of package ids** and read it back to the user before installing.


## Upgrading the Editor

1. Commit first: git is the undo.
2. Read `ProjectSettings/ProjectVersion.txt` for the from version; the user names the to version.
3. Read Unity's upgrade guide for every version jump in the span (6000.5 to 6000.6 is one jump) and list the renamed
   or removed APIs. Grep `Assets/` for each.
4. The user opens the project in the new Editor and lets the packages resolve (Unity offers updated versions of the
   `com.unity.*` packages). GameKit stays on its `#gamekit-vX.Y.Z` tag; `Assets/Feel` is vendored, so check its
   release notes for the new Unity version before blaming the upgrade.
5. Compile gate: `gk-bridge refresh` (exit 0 only), then `gk-bridge compile android` and `gk-bridge compile ios`.
6. Fix the obsolete API: CS0619 is an error and fails the gate; CS0618 is a warning in `Logs/agent/compile.log`. Fix
   each one or list it in the handoff.
7. Tooling check: `unity status --until-ready --project-path <project>`, then `unity command package list`. If it
   cannot connect, the Pipeline package did not load on the new Editor (Safe Mode, or a `com.unity.pipeline` the new
   Editor rejects): read `unity status` and the package's changelog before any later `unity command` step.
8. Behaviour check: ask the user, then `gk-bridge run-tests` and `gk-bridge run-tests playmode` in the background
   (**`gamekit:unity-testing`**). An engine jump can compile and still change physics, serialization or URP output;
   list each failure in the handoff, and hand the user a Play Mode check of the core loop.
9. Record one DESIGN.md Decisions line: `YYYY-MM-DD: Unity <from> -> <to>. Why.`

Knowledge gap: when the pinned Unity is newer than what you know, the manual and the upgrade guide are the source.
Write down what you could not confirm; never fill a gap from memory.

## Notes

- These editor scripts are a bootstrap convenience. Leave them in
  `Assets/Editor/ProjectBootstrap/` (they do nothing unless invoked) or delete them after
  setup — your call; mention it to the user.
- All scripts live under `Editor/` because they use `UnityEditor`; they never ship in a build.
- Monetization / backend packages (`com.unity.purchasing`, `com.unity.services.levelplay`, the
  UGS packages) install through this same mechanism. The upstream integration skills
  (implement-in-app-purchases, levelplay-unity-integration, build-live-game) are **not** loaded
  in gamekit games (the Unity plugin stays off), so do not invoke them. The business choice is
  **`gamekit:launch-review`**; store review and notifications come from the `mobile-store` pack;
  networking from the `coop-multiplayer` pack. For the integration itself, follow the guardrails
  in [references/select-packages.md](references/select-packages.md#by-monetization) and Unity's
  documentation for the installed version, and record what you could not confirm.
