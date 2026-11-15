---
name: unity-package-management
description: Use for "install a Unity package", "add com.unity.*", "paket ekle", "hangi paketler", "which packages for a [genre] game" - adding, removing, upgrading or verifying UPM packages (live Editor or headless/CI), or upgrading the Unity Editor.
allowed-tools:
  - Bash
  - PowerShell
  - Read
  - Write
  - Edit
---

# Unity Package Management (headless, via the C# Client API)

Add, remove, upgrade, and discover UPM (Unity Package Manager) packages programmatically with
`UnityEditor.PackageManager.Client`, driven through the live Editor or headless from the terminal or CI. Do **not**
hand-edit `Packages/manifest.json` to add or upgrade a **registry** package — the Client API resolves dependencies
and compatible versions correctly, whereas manual edits routinely break resolution. Two edits in this template are
plain manifest text on purpose: moving the GameKit `#gamekit-vX.Y.Z` tag (**`gamekit:sync-template`**) and the
`packages.json` dependencies a pack inserts (`new-game.ps1 -Packs`).

**Ask the user before adding any package** (the game's CLAUDE.md keeps the manifest deliberately small), and check
`packs/` in unity-game-template first: a pack's `packages.json` is the source for its dependencies (see
[references/select-packages.md](references/select-packages.md)). The checked extras (PrimeTween, Localization,
IAP, the in-game debug console, Microsoft.Unity.Analyzers), release-automation tools and the packages not taken live
there too, under [Checked extras](references/select-packages.md#checked-extras-with-pinned-install-lines).

This complements the **`unity-cli`** skill (editor install, project creation, build/test): the
CLI has **no** package-management command, so all package work goes through the Editor's C# API.

> **Local gamekit adaptations** (this skill is a copy of the official Unity plugin's skill; re-apply these after
> refreshing it from upstream): the manifest-edit exceptions and ask-first rule above, the "Editor open?" branch,
> PowerShell recipes instead of `python3`, neutral version placeholders, the **Upgrading the Editor** section, the
> pack-first rule, template handoffs and the **Checked extras** section in `references/select-packages.md`.

## Editor open? Pick the route first

In this template the user's Editor is normally open. Unity refuses a second instance on the same project, so the
batchmode route below fails or hangs while it is.

- **Editor open** (`<project>/Temp/UnityLockfile` exists): drive the live Editor. Write a one-method script
  **outside** `Assets/` (the scratchpad directory) that only fires the request, and run it with
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
- **Editor closed** (CI, a throwaway project): use the headless installer below.

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

## The `-quit` problem — why NOT `unity run` for installs

`Client.Add` / `Client.AddAndRemove` are **asynchronous**: they return a `Request` that only
completes on later `EditorApplication.update` ticks (the UPM child process marshals its result
back on the Editor's main-loop pump, so a blocking `while (!req.IsCompleted)` busy-wait
deadlocks it). The Editor must **stay alive** after `-executeMethod` returns, until the request
finishes.

`unity run` **cannot** be used for the installer: its default path injects `-quit` (see the reserved
flags in the **`unity-cli`** skill). With `-quit`, the Editor quits the instant the method
returns — before UPM resolves — so packages never install and the callback never runs.

**Solution:** launch the **Editor binary directly** in `-batchmode` **without** `-quit`. The
Editor stays alive, `EditorApplication.update` keeps ticking, the poll callback runs, and it
calls `EditorApplication.Exit(code)` itself when done — which both quits and sets the process
exit code.

## The installer script

Write this to `Assets/Editor/ProjectBootstrap/PackageInstaller.cs`. It must live under an
`Editor/` folder (or an Editor-only assembly) because it uses `UnityEditor`.

```csharp
using System.Linq;
using UnityEditor;
using UnityEditor.PackageManager;
using UnityEditor.PackageManager.Requests;
using UnityEngine;

namespace ProjectBootstrap
{
    // Installs (and optionally removes) a fixed set of packages via the PackageManager
    // Client API, headless-safe.
    public static class PackageInstaller
    {
        // EDIT this list to the selection the user approved (see references/select-packages.md).
        // Leave out what the manifest already has (the template ships Input System, URP, uGUI, Test Framework).
        static readonly string[] PackagesToAdd =
        {
            "<id>",
            // "<id>@<version>"  // pin a version with @ when a minimum is required
        };

        // Optionally drop packages in the same resolution pass (e.g. a template default you don't want).
        static readonly string[] PackagesToRemove = { };

        const double TimeoutSeconds = 600; // UPM resolution + downloads can be slow

        static AddAndRemoveRequest _request;
        static double _deadline;

        // Invoke with: -executeMethod ProjectBootstrap.PackageInstaller.Install  (NO -quit)
        public static void Install()
        {
            if (PackagesToAdd.Length == 0 && PackagesToRemove.Length == 0)
            {
                Debug.Log("[PackageInstaller] Nothing to do.");
                EditorApplication.Exit(0);
                return;
            }

            Debug.Log($"[PackageInstaller] Adding: {string.Join(", ", PackagesToAdd)}");
            _request = Client.AddAndRemove(packagesToAdd: PackagesToAdd, packagesToRemove: PackagesToRemove);
            _deadline = EditorApplication.timeSinceStartup + TimeoutSeconds;
            EditorApplication.update += Poll;
        }

        static void Poll()
        {
            if (_request == null) return;

            if (!_request.IsCompleted)
            {
                if (EditorApplication.timeSinceStartup > _deadline)
                {
                    EditorApplication.update -= Poll;
                    Debug.LogError("[PackageInstaller] Timed out waiting for UPM.");
                    EditorApplication.Exit(2);
                }
                return;
            }

            EditorApplication.update -= Poll;

            if (_request.Status == StatusCode.Success)
            {
                var names = _request.Result.Select(p => $"{p.name}@{p.version}");
                Debug.Log($"[PackageInstaller] Resolved: {string.Join(", ", names)}");
                EditorApplication.Exit(0);
            }
            else
            {
                Debug.LogError($"[PackageInstaller] Failed: {_request.Error?.message}");
                EditorApplication.Exit(1);
            }
        }
    }
}
```

`AddAndRemove` installs the whole set in a single UPM resolution pass — faster and less
error-prone than one `Client.Add` per package.

**Add / remove / upgrade with one script:**
- **Add**: list the id in `PackagesToAdd`.
- **Remove**: list the id in `PackagesToRemove`.
- **Upgrade / pin**: add the id with `@<version>` (`<id>@<version>`; take the version from the registry, see
  Discovering below, never from memory). Without a version, resolution picks the latest compatible release.

## Discovering / verifying packages

To confirm an id exists or list its versions before adding it, search the registry. The
in-Editor `Client.SearchAll()` / `Client.Search("<id>")` calls are also async, so they use the
**same poll-and-`Exit` pattern and the same headless run** as the installer. Write
`Assets/Editor/ProjectBootstrap/PackageSearch.cs`:

```csharp
using System.Linq;
using UnityEditor;
using UnityEditor.PackageManager;
using UnityEditor.PackageManager.Requests;
using UnityEngine;

namespace ProjectBootstrap
{
    public static class PackageSearch
    {
        const double TimeoutSeconds = 120;
        static SearchRequest _request;
        static double _deadline;

        // Invoke with: -executeMethod ProjectBootstrap.PackageSearch.SearchAll  (NO -quit)
        public static void SearchAll()
        {
            _request = Client.SearchAll();                 // or Client.Search("<id>")
            _deadline = EditorApplication.timeSinceStartup + TimeoutSeconds;
            EditorApplication.update += Poll;
        }

        static void Poll()
        {
            if (_request == null) return;
            if (!_request.IsCompleted)
            {
                if (EditorApplication.timeSinceStartup > _deadline)
                {
                    EditorApplication.update -= Poll;
                    Debug.LogError("[PackageSearch] Timed out.");
                    EditorApplication.Exit(2);
                }
                return;
            }
            EditorApplication.update -= Poll;

            if (_request.Status == StatusCode.Success)
            {
                foreach (var p in _request.Result.OrderBy(p => p.name))
                    Debug.Log($"[PackageSearch] {p.name}@{p.versions.latestCompatible}  {p.displayName}");
                Debug.Log($"[PackageSearch] {_request.Result.Length} packages found.");
                EditorApplication.Exit(0);
            }
            else
            {
                Debug.LogError($"[PackageSearch] Failed: {_request.Error?.message}");
                EditorApplication.Exit(1);
            }
        }
    }
}
```

`_request.Result` is a `PackageInfo[]`; each entry exposes `name`, `displayName`, `description`,
and `versions` (`.latest`, `.latestCompatible`, `.all`). For a terminal-only check without the
Editor (a **known** id, not free-text search), query the registry directly — see
[references/select-packages.md](references/select-packages.md#discovering-and-verifying-packages).

## Run it headless (direct Editor invocation, no `-quit`)

Only with the Editor **closed** (see "Editor open?" above). Resolve the Editor binary from the version, then run it
in batch mode. The script owns quitting via `EditorApplication.Exit`, so do **not** pass `-quit`. The template is
Windows-only and this machine has no Python, so the recipe is PowerShell:

```powershell
$project = '<project-path>'
$method  = 'ProjectBootstrap.PackageInstaller.Install'   # or ...PackageSearch.SearchAll
# The version the project pins (or name an installed one)
$version = ((Get-Content "$project\ProjectSettings\ProjectVersion.txt" |
    Select-String '^m_EditorVersion:').Line -split ':\s*')[1].Trim()

# Install directory of that editor (Hub layout), via the unity CLI: { "data": { "path": ... } }
$ed = (unity editors path $version --format json | Out-String | ConvertFrom-Json).data.path
$unityBin = Join-Path $ed 'Editor\Unity.exe'
if (-not (Test-Path $unityBin)) { throw "No Editor at $unityBin" }

& $unityBin -batchmode -projectPath $project -executeMethod $method -logFile - | Out-Host
"Exit code: $LASTEXITCODE"   # 0 = success, 1 = UPM error, 2 = timeout
```

On macOS the binary is `<dir>/Unity.app/Contents/MacOS/Unity` (or `<dir>/Contents/MacOS/Unity` when the path is the
`.app` itself); on Linux it is `<dir>/Editor/Unity`.

`-logFile -` streams the Editor log (including the `[PackageInstaller]` / `[PackageSearch]`
lines) to stdout so you can watch resolution progress and read any UPM error. If
`unity editors path` output shape differs on your build, get the directory from
`unity editors --installed --format json` instead.

## Verify

```bash
# Every requested id should appear as a dependency
cat "<project-path>/Packages/manifest.json"
```

Confirm the run exited `0` and each package from the list is present in `manifest.json`. If a
package fails to resolve, `_request.Error.message` is logged; read it and check the id/version
against the registry. The Editor's own log (including the `[PackageInstaller]` lines) is the
stdout you streamed with `-logFile -` above — read it there, not via `unity logs` (which shows
the CLI's own log, not the Editor's).

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
7. Record one DESIGN.md Decisions line: `YYYY-MM-DD: Unity <from> -> <to>. Why.`

Knowledge gap: when the pinned Unity is newer than what you know, the manual and the upgrade guide are the source.
Write down what you could not confirm; never fill a gap from memory.

## Import & save headlessly (generate `.meta` files)

After a script or tool writes new `.cs`/asset files, Unity must **import** them so it generates
the `.meta` file each asset needs — and every `.cs`/asset MUST be committed together with its
`.meta`. Merely opening the project once (`unity open "<project-path>"`) imports and generates
them; use this method when you need it **headless** (in a script or CI). With the Editor open, `unity run` cannot
start a second instance: run `gk-bridge refresh` instead, which imports the new files in the live Editor.

Unlike the package installer, this is **synchronous** — it finishes before returning — so it's
safe to run via `unity run` (its injected `-quit` is harmless; the method also calls
`EditorApplication.Exit` for a clean exit code). Write
`Assets/Editor/ProjectBootstrap/ProjectSaver.cs`:

```csharp
using UnityEditor;
using UnityEngine;

namespace ProjectBootstrap
{
    public static class ProjectSaver
    {
        // Invoke with: -executeMethod ProjectBootstrap.ProjectSaver.SaveAll
        public static void SaveAll()
        {
            AssetDatabase.Refresh(ImportAssetOptions.ForceUpdate);
            AssetDatabase.SaveAssets();
            Debug.Log("[ProjectSaver] Assets imported and saved.");
            EditorApplication.Exit(0);
        }
    }
}
```

```bash
unity run "<project-path>" --editor-version <version> \
  -- -executeMethod ProjectBootstrap.ProjectSaver.SaveAll
```

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
