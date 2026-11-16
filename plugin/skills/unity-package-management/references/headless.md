# Headless package installs (Editor closed)

The route for CI or a throwaway project, when no Editor has the project open. With the Editor open use the Pipeline
`package` commands in [SKILL.md](../SKILL.md#editor-open-pick-the-route-first): Unity refuses a second instance on
the same project, so this batchmode route fails or hangs while it is.

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

        // Ceiling: these statics and the update subscription die if a domain reload lands before Poll sees
        // IsCompleted, and then neither Exit below fires. The launcher's outer limit is the guard for that case;
        // the way up is SessionState plus an [InitializeOnLoad] re-subscribe that checks the manifest and lock file.
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
[select-packages.md](select-packages.md#discovering-and-verifying-packages).

## Run it headless (direct Editor invocation, no `-quit`)

Only with the Editor **closed** (see "Editor open?" in [SKILL.md](../SKILL.md#editor-open-pick-the-route-first)).
Resolve the Editor binary from the version, then run it in batch mode. The script owns quitting via
`EditorApplication.Exit`, so do **not** pass `-quit`. A batchmode Editor without `-quit` never quits by itself, so the
launcher keeps an outer wall-clock limit above the script's own timeout: a domain reload that wipes the poll, a
licence prompt or a compile-error loop would otherwise block the shell forever. The template is Windows-only and this
machine has no Python, so the recipe is PowerShell:

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

$log = Join-Path $env:TEMP 'package-installer.log'
$p = Start-Process $unityBin -PassThru -NoNewWindow -ArgumentList @(
    '-batchmode', '-projectPath', "`"$project`"", '-executeMethod', $method, '-logFile', "`"$log`"")
$null = $p.Handle                       # PowerShell 5.1: without it ExitCode stays empty after the wait
$limitMs = 900 * 1000                   # outer limit, above the script's 600 s TimeoutSeconds
if ($p.WaitForExit($limitMs)) { $code = $p.ExitCode }
else { $p.Kill(); $p.WaitForExit(); $code = 2; 'Killed: no exit within the outer limit.' }
Select-String -Path $log -Pattern '\[Package(Installer|Search)\]|error' | ForEach-Object { $_.Line }
"Exit code: $code"   # 0 = success, 1 = UPM error, 2 = timeout (script or outer limit)
```

After a kill, `Temp/UnityLockfile` stays behind but nothing holds it, so the next Editor start takes it over. Check
`Packages/manifest.json` and `Packages/packages-lock.json` (Verify below): the resolve may have finished before the
reload that stranded the poll.

On macOS the binary is `<dir>/Unity.app/Contents/MacOS/Unity` (or `<dir>/Contents/MacOS/Unity` when the path is the
`.app` itself); on Linux it is `<dir>/Editor/Unity`.

`-logFile <file>` keeps the whole Editor log (including the `[PackageInstaller]` / `[PackageSearch]` lines); the
recipe prints the tagged and error lines, and `Get-Content $log -Wait` follows resolution live from a second shell.
(`-logFile -` streams it to stdout instead, but a pipe ties the shell to the process and leaves no outer limit.) If
`unity editors path` output shape differs on your build, get the directory from
`unity editors --installed --format json` instead.

## Verify

```powershell
# Every requested id must be in the lock file: the manifest alone does not prove the resolve finished
$project = '<project-path>'
foreach ($id in @('<id>', '<id2>')) {
    if (Select-String -Path "$project\Packages\packages-lock.json" -SimpleMatch "`"$id`":" -Quiet) { "OK      $id" }
    else { "MISSING $id" }
}
```

Confirm the run exited `0` and every id prints `OK` from `packages-lock.json` (an id in `manifest.json` but missing
from the lock file never resolved, for example after the outer-limit kill). If a
package fails to resolve, `_request.Error.message` is logged; read it and check the id/version
against the registry. The Editor's own log (including the `[PackageInstaller]` lines) is the
`-logFile` file above — read it there, not via `unity logs` (which shows the CLI's own log, not the Editor's).

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
