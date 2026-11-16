<#
.SYNOPSIS
    Checks that the template still makes a working game: runs new-game.ps1 into a temp folder with this checkout's
    GameKit, then asserts the result. Run it after changing project\, packs\, packages\ or new-game.ps1.

.DESCRIPTION
    Checks: ProjectSetup finished with 0 compile errors and no shader errors, Main.unity exists, the first commit
    carries the unity-game-template@<sha> sync marker, GameKit comes from this checkout, no __GAME__/__COMPANY__ is
    left in the committed game, Feel is committed (copied from the first sibling of this checkout that has
    Assets\Feel\MMFeedbacks, as new-game.ps1 looks under -Path; "skip Feel" when none), and each selected pack's own
    check passes
    ($packChecks below; toon-art's shader check, ci-github's GAMEKIT_TOKEN, each pack's packages.json dependencies,
    CLAUDE.md lines and Networking section, each pack assembly and packages.json gameReferences in Game.asmdef's
    references, mobile-2d's 2D renderer and Main, mobile-store's notification defaults, steam's DISABLESTEAMWORKS on
    Android, iOS and WebGL). -Tests or mobile-store adds one launch of GameKit's AgentBridge.CompilePlayerScriptsBatch
    -platform android (its exit 0/1/2 contract and the #if UNITY_ANDROID code; exit 2, no Android module, is a skip).
    -Tests also runs unity-package-management's headless.md PackageInstaller once without -quit (one launch: exit 0
    and the package in packages-lock.json, then manifest and lock restored) and the game's EditMode and PlayMode tests
    (two more Unity launches).
    -Tests, coop-multiplayer or toon-art adds one launch that compiles and runs skill code (AssetAudit.cs,
    urp-postprocessing's Editor classes run in a throwaway scene, unity-package-management's headless.md installer
    classes and unity-architecture's core-system skeleton compiled, a FishNet relay probe with coop-multiplayer,
    toon-art's examples/PropBuilder.cs.txt compiled with toon-art). Not checked: mobile-store's NotificationsSettings
    asset values (no com.unity.mobile.notifications source here to confirm its YAML keys).
    Takes 5-10 min: an agent runs it in the background. Each Unity launch (ProjectSetup included) is killed after
    -TimeoutMinutes and its log tail printed. A failed ProjectSetup is a failed check, and the log checks still run.
    Each run has its own temp folder (unity-game-template-test-<PID>), so parallel runs (one per changed pack) share
    no game and no Unity project lock. The temp game is deleted on a pass unless -Keep, and kept on a failure for
    diagnosis.
    Pack manifest merging for every pack is checked without Unity by test-all.ps1. Exit code 0 = pass, 1 = fail.

.EXAMPLE
    .\test-template.ps1

.EXAMPLE
    .\test-template.ps1 -Packs mobile-2d,steam -Tests
#>
param(
    # Packs to include; test the ones you changed. Packs are not combined by default: not every pair makes sense.
    [string[]]$Packs = @(),
    [switch]$Tests,
    [switch]$Keep,
    # per Unity launch: new-game.ps1's ProjectSetup run and each test run
    [int]$TimeoutMinutes = 30,
    # Unity.exe. Default: the Hub install that matches project\ProjectSettings\ProjectVersion.txt
    [string]$Unity
)

$ErrorActionPreference = 'Stop'
# per run: two background runs (one per changed pack) would otherwise delete each other's game and fight over its lock
$root = Join-Path $env:TEMP "unity-game-template-test-$PID"
$name = 'TplTest'
$game = Join-Path $root $name
# a reused PID can meet a kept folder; paths under Library pass 260 characters, hence \\?\ and rmdir. A folder that
# survives it is locked (a Unity still has it open): stop, or every check below would read that old game
if (Test-Path -LiteralPath $game) { cmd /c rmdir /s /q "\\?\$game" }
if (Test-Path -LiteralPath $game) { throw "$game could not be deleted: close the Unity that has it open." }

$failures = New-Object System.Collections.Generic.List[string]
function Check([bool]$ok, [string]$what) {
    if ($ok) { Write-Host "  ok    $what" } else { Write-Host "  FAIL  $what" -ForegroundColor Red; $failures.Add($what) }
}

# new-game.ps1's own lookup (Hub's custom install folder, then its default), resolved once here so the setup run and
# the test runs use one editor, the one a real game gets
if (-not $Unity) { $Unity = & (Join-Path $PSScriptRoot 'new-game.ps1') -ResolveUnity }
# Feel: new-game.ps1 looks under -Path, the temp root here, so hand it the first sibling project that has one, as a game
# made under C:\GitHub finds it; without it Feel is never compiled together with GameKit and the packs
$feel = Get-ChildItem -LiteralPath (Split-Path $PSScriptRoot) -Directory -ErrorAction SilentlyContinue |
    Where-Object { Test-Path -LiteralPath (Join-Path $_.FullName 'Assets\Feel\MMFeedbacks') } | Select-Object -First 1 -ExpandProperty FullName
$feelArgs = @{}
if ($feel) { $feelArgs.FeelFrom = $feel } else { Write-Host '  skip  Feel: no sibling project has Assets\Feel\MMFeedbacks' }

$started = Get-Date
$setupFailed = $false
try {
    & (Join-Path $PSScriptRoot 'new-game.ps1') -Name $name -Path $root -Packs $Packs -LocalGameKit -Unity $Unity -SetupTimeoutMinutes $TimeoutMinutes @feelArgs
    if ($LASTEXITCODE -ne 0) { throw "new-game.ps1 failed ($LASTEXITCODE)." }
} catch {
    # a failed ProjectSetup (a compile error exits 1) still leaves the game and its log: record it and run the checks
    if (-not (Test-Path -LiteralPath (Join-Path $game 'Packages\manifest.json'))) { throw }
    $setupFailed = $true
    Check $false "new-game.ps1: $($_.Exception.Message)"
}

Write-Host "`nChecks ($(if ($Packs) { $Packs -join ', ' } else { 'no packs' }))"
$log = Join-Path $game 'Logs\setup.log'
$text = if (Test-Path -LiteralPath $log) { [IO.File]::ReadAllText($log) } else { '' }
Check ($text -ne '') 'Logs\setup.log written'
Check (-not ($text -match 'error CS\d+')) "0 compile errors $(([regex]::Matches($text, 'error CS\d+[^\r\n]*') | Select-Object -First 3 | ForEach-Object Value) -join ' | ')"
Check ($text -match '\[ProjectSetup\] Done:') 'ProjectSetup done'
Check (Test-Path -LiteralPath (Join-Path $game "Assets\$name\Scenes\Main.unity")) 'Main.unity created'
Check ((git -C $game log -1 --format=%s) -match 'unity-game-template@[0-9a-f]{7}') 'start commit has the sync marker'
if ($Packs) { Check (((git -C $game log -1 --format=%B) -join "`n") -match "(?m)^Packs: $([regex]::Escape($Packs -join ', '))\s*$") 'start commit lists the packs (sync.sh reads it)' }
Check ((Get-Content -LiteralPath (Join-Path $game 'Packages\manifest.json') -Raw) -match '"com\.yunusburkut\.gamekit":\s*"file:') 'GameKit from this checkout'
# the plugin's hooks and gk-bridge treat bridge.log as "this bridge knows refresh"; it must exist before any refresh
$bridge = Join-Path $game 'Logs\agent\bridge.log'
Check ((Test-Path -LiteralPath $bridge) -and (Get-Content -LiteralPath $bridge -TotalCount 1) -match '^READY') 'AgentBridge wrote bridge.log READY'
Check (-not ($text -match 'Shader error in')) "0 shader errors $(([regex]::Matches($text, "Shader error in[^\r\n]*") | Select-Object -First 3 | ForEach-Object Value) -join ' | ')"
$left = @(git -C $game grep -lE '__GAME__|__COMPANY__')
Check (-not $left) "no __GAME__ / __COMPANY__ left $($left -join ', ')"
if ($feel) { Check ([bool](git -C $game ls-files 'Assets/Feel/*.cs' | Select-Object -First 1)) "Feel committed (from $feel)" }
# what a pack's own setup step logs when it worked (a warning path would otherwise pass as green)
$packChecks = @{
    'mobile-2d' = @{ Log = '\[Setup2D\] Done:'; What = 'Setup2D done (2D Renderer, 2D mode, orthographic Main camera)' }
    'mobile-store' = @{ Log = '\[mobile-store\] Done:'; What = 'NotificationDefaults done (iOS launch authorization off, Android inexact)' }
}
foreach ($pack in $Packs) {
    if ($packChecks.ContainsKey($pack)) { Check ($text -match $packChecks[$pack].Log) "$pack`: $($packChecks[$pack].What)" }
}
if ($Packs -contains 'mobile-2d') {
    # Setup2D logs Done even when Main had no camera: read what it wrote
    $settings = Join-Path $game "Assets\$name\Settings"
    $rendererMeta = Join-Path $settings 'URP_2D_Renderer.asset.meta'
    $guid = if (Test-Path -LiteralPath $rendererMeta) { [regex]::Match([IO.File]::ReadAllText($rendererMeta), '(?m)^guid: (\w+)').Groups[1].Value }
    foreach ($tier in 'Mobile', 'PC') {
        $urp = Join-Path $settings "URP_$tier.asset"
        Check ($guid -and (Test-Path -LiteralPath $urp) -and [regex]::IsMatch([IO.File]::ReadAllText($urp), "m_RendererDataList:\s*\r?\n\s*- \{fileID: \d+, guid: $guid")) "mobile-2d: URP_$tier renders through URP_2D_Renderer"
    }
    $main = Join-Path $game "Assets\$name\Scenes\Main.unity"
    $mainText = if (Test-Path -LiteralPath $main) { [IO.File]::ReadAllText($main) } else { '' }
    Check (($mainText -match 'orthographic: 1') -and ($mainText -match 'm_Name: Global Light 2D')) 'mobile-2d: Main has an orthographic camera and the Global Light 2D'
}
if ($Packs -contains 'steam') {
    # SteamSetup logs nothing; the defines it sets keep Steam code off phones and the web
    $player = [IO.File]::ReadAllText((Join-Path $game 'ProjectSettings\ProjectSettings.asset'))
    $defines = [regex]::Match($player, '(?m)^  scriptingDefineSymbols:\s*\r?\n((?:    [^\r\n]*\r?\n)*)').Groups[1].Value
    $noSteam = @('Android', 'iPhone', 'WebGL' | Where-Object { $defines -notmatch "(?m)^    ${_}: [^\r\n]*\bDISABLESTEAMWORKS\b" })
    Check (-not $noSteam -and $defines -notmatch '(?m)^    Standalone: [^\r\n]*\bDISABLESTEAMWORKS\b') "steam: DISABLESTEAMWORKS on Android, iOS and WebGL, not on Standalone $($noSteam -join ', ')"
}
if ($Packs -contains 'toon-art') {
    # ToonShaderCheck, a [ProjectSetupStep], logs OK or each shader error; a broken shader is no compile error
    Check ($text -match '\[toon-art\] Toon shader OK') "toon-art: Toon shader compiles $(([regex]::Matches($text, '\[toon-art\][^\r\n]*') | Select-Object -First 3 | ForEach-Object Value) -join ' | ')"
}
if ($Packs -contains 'ci-github') {
    # the template repo is private: GameCI cannot fetch GameKit's git URL without the token
    $ci = [IO.File]::ReadAllText((Join-Path $game '.github\workflows\ci.yml'))
    Check (([regex]::Matches($ci, 'gitPrivateToken: \$\{\{ secrets\.GAMEKIT_TOKEN \}\}')).Count -ge 2) 'ci-github: both GameCI steps pass gitPrivateToken: ${{ secrets.GAMEKIT_TOKEN }}'
}
# what new-game.ps1 merges from each pack: packages.json into the manifest, the README's CLAUDE.md block, each pack
# assembly in Game.asmdef (test-all.ps1 checks the same merge for all packs at once without Unity; this is the real game)
$gameManifest = Get-Content -LiteralPath (Join-Path $game 'Packages\manifest.json') -Raw | ConvertFrom-Json
$gameClaude = [IO.File]::ReadAllText((Join-Path $game 'CLAUDE.md'))
foreach ($pack in $Packs) {
    $spec = Join-Path $PSScriptRoot "packs\$pack\packages.json"
    if (Test-Path -LiteralPath $spec) {
        $deps = @((Get-Content -LiteralPath $spec -Raw | ConvertFrom-Json).dependencies.PSObject.Properties)
        $miss = @($deps | Where-Object { $gameManifest.dependencies.($_.Name) -ne $_.Value } | ForEach-Object Name)
        Check (-not $miss) "$pack`: manifest.json has the $($deps.Count) packages.json dependencies $($miss -join ', ')"
    }
}
if ($Packs -contains 'coop-multiplayer') { Check ($gameClaude -match '(?m)^## Networking') 'coop-multiplayer: CLAUDE.md has the Networking section net-auditor reads' }
if (@($Packs | Where-Object { [IO.File]::ReadAllText((Join-Path $PSScriptRoot "packs\$_\README.md")) -match '(?m)^## CLAUDE\.md''ye eklenecek sat\u0131r' })) {
    Check ($gameClaude -match '(?m)^## Packs') 'CLAUDE.md has the packs'' lines (## Packs)'
}
$gameAsm = [IO.File]::ReadAllText((Join-Path $game "Assets\$name\Game\$name.Game.asmdef"))
foreach ($pack in $Packs) {
    $packGame = Join-Path $PSScriptRoot "packs\$pack\Assets\__GAME__\Game"
    if (-not (Test-Path -LiteralPath $packGame)) { continue }
    foreach ($asm in @(Get-ChildItem -LiteralPath $packGame -Recurse -Filter *.asmdef | ForEach-Object { $_.BaseName -replace '__GAME__', $name })) {
        Check ($gameAsm -match ('"' + [regex]::Escape($asm) + '"')) "$pack`: $name.Game.asmdef references $asm"
    }
}
foreach ($pack in $Packs) {
    $spec = Join-Path $PSScriptRoot "packs\$pack\packages.json"
    if (-not (Test-Path -LiteralPath $spec)) { continue }
    foreach ($asm in @((Get-Content -LiteralPath $spec -Raw | ConvertFrom-Json).gameReferences | Where-Object { $_ })) {
        Check ($gameAsm -match ('"' + [regex]::Escape($asm) + '"')) "$pack`: $name.Game.asmdef references $asm (packages.json gameReferences)"
    }
}
if (-not ($text -match '\[ProjectSetup\] Done:') -and $text) {
    Write-Host "`nLast 20 lines of Logs\setup.log:"; ($text -split '\r?\n' | Select-Object -Last 20) | ForEach-Object { Write-Host "    $_" }
}

# GameKit's batch compile entry, the one check of its exit contract (0 OK, 1 fail, 2 platform module missing) and of
# the #if UNITY_ANDROID code no Editor compile reaches (mobile-store's StoreReview Play Review branch among it). It
# exits on its own: no -quit
if (($Tests -or $Packs -contains 'mobile-store') -and -not $setupFailed) {
    $cpLog = Join-Path $game 'Logs\compile-player-android.log'
    $cpReport = Join-Path $game 'Logs\agent\compile-player.log'
    $run = Start-Process -FilePath $Unity -PassThru -NoNewWindow -ArgumentList @(
        '-batchmode', '-projectPath', "`"$game`"", '-executeMethod', 'GameKit.Editor.AgentBridge.CompilePlayerScriptsBatch',
        '-platform', 'android', '-logFile', "`"$cpLog`"")
    $null = $run.Handle   # PowerShell 5.1: without the cached handle ExitCode reads empty after the exit
    $cpFirst = { if (Test-Path -LiteralPath $cpReport) { Get-Content -LiteralPath $cpReport -TotalCount 1 } }
    if (-not $run.WaitForExit($TimeoutMinutes * 60000)) {
        cmd /c "taskkill /T /F /PID $($run.Id) >nul 2>&1"
        Check $false "Android player scripts compile (CompilePlayerScriptsBatch killed after $TimeoutMinutes min)"
    } elseif ($run.ExitCode -eq 2) {
        Write-Host "  skip  Android player scripts: $(& $cpFirst) (install the Android module to check them)"
    } else {
        Check ($run.ExitCode -eq 0) "Android player scripts compile (AgentBridge.CompilePlayerScriptsBatch -platform android exit $($run.ExitCode)) $(& $cpFirst)"
        if ($run.ExitCode -ne 0) {
            $tail = if (Test-Path -LiteralPath $cpReport) { $cpReport } else { $cpLog }
            if (Test-Path -LiteralPath $tail) { Get-Content -LiteralPath $tail -Tail 30 | ForEach-Object { Write-Host "    $_" } }
        }
    }
}

# unity-package-management's headless install route, run as headless.md writes it: its first csharp block (the
# installer itself, read from the page so the check cannot drift from it) with one leaf package no template, pack or
# transitive dependency brings, launched without -quit so the async AddAndRemove finishes and EditorApplication.Exit
# sets the code, then the page's Verify proof (the id in packages-lock.json). Manifest, lock and installer are put back
# afterwards, so the test runs below see the usual project.
if ($Tests -and -not $setupFailed) {
    $piId = 'com.unity.device-simulator.devices'
    $piDir = Join-Path $game 'Assets\Editor\ProjectBootstrap'
    $piLog = Join-Path $game 'Logs\package-installer.log'
    $piManifest = Join-Path $game 'Packages\manifest.json'
    $piLock = Join-Path $game 'Packages\packages-lock.json'
    $piSaved = @{}
    foreach ($f in $piManifest, $piLock) { if (Test-Path -LiteralPath $f) { $piSaved[$f] = [IO.File]::ReadAllText($f) } }
    $piCode = [regex]::Match([IO.File]::ReadAllText((Join-Path $PSScriptRoot 'plugin\skills\unity-package-management\references\headless.md')), '(?s)```csharp\r?\n(.*?)```').Groups[1].Value
    $piInLock = { (Test-Path -LiteralPath $piLock) -and (Select-String -LiteralPath $piLock -SimpleMatch "`"$piId`":" -Quiet) }
    if ($piCode -notmatch 'class PackageInstaller' -or -not $piCode.Contains('"<id>",')) {
        Check $false 'headless.md: first csharp block is PackageInstaller with its "<id>", placeholder line'
    } elseif (& $piInLock) {
        Check $false "headless install probe: $piId is already in packages-lock.json, pick another leaf package so the check proves something"
    } else {
        New-Item -ItemType Directory -Force $piDir | Out-Null
        [IO.File]::WriteAllText((Join-Path $piDir 'PackageInstaller.cs'), $piCode.Replace('"<id>",', "`"$piId`","), (New-Object Text.UTF8Encoding $false))
        $run = Start-Process -FilePath $Unity -PassThru -NoNewWindow -ArgumentList @(
            '-batchmode', '-projectPath', "`"$game`"", '-executeMethod', 'ProjectBootstrap.PackageInstaller.Install', '-logFile', "`"$piLog`"")
        $null = $run.Handle   # PowerShell 5.1: without the cached handle ExitCode reads empty after the exit
        $piOk = $false
        if (-not $run.WaitForExit($TimeoutMinutes * 60000)) {
            cmd /c "taskkill /T /F /PID $($run.Id) >nul 2>&1"
            Check $false "headless PackageInstaller (unity-package-management headless.md) killed after $TimeoutMinutes min"
        } else {
            Check ($run.ExitCode -eq 0) "headless PackageInstaller (unity-package-management headless.md) exit $($run.ExitCode)"
            Check (& $piInLock) "headless install resolved $piId into packages-lock.json"
            $piOk = $run.ExitCode -eq 0 -and (& $piInLock)
        }
        if (-not $piOk) {
            if (Test-Path -LiteralPath $piLog) { Select-String -LiteralPath $piLog -Pattern '\[PackageInstaller\]|error' | Select-Object -First 20 | ForEach-Object { Write-Host "    $($_.Line)" } }
        }
        cmd /c rmdir /s /q "\\?\$piDir"
        Remove-Item -LiteralPath "$piDir.meta" -ErrorAction SilentlyContinue
        $piEditor = Split-Path $piDir
        if (-not (Get-ChildItem -LiteralPath $piEditor -Force -ErrorAction SilentlyContinue)) { Remove-Item -LiteralPath $piEditor, "$piEditor.meta" -Force -ErrorAction SilentlyContinue }
        foreach ($f in $piSaved.Keys) { [IO.File]::WriteAllText($f, $piSaved[$f], (New-Object Text.UTF8Encoding $false)) }
    }
}

if ($Tests -and $setupFailed) { Write-Host '  skip  tests: ProjectSetup failed' }
elseif ($Tests) {
    # GameKit's own tests run only in this throwaway game: a real game does not list the package as testable, so its
    # suite never reruns ProjectSetup. Text insert keeps the manifest's LF formatting (no ConvertTo-Json rewrite).
    $manifestPath = Join-Path $game 'Packages\manifest.json'
    $manifestText = [IO.File]::ReadAllText($manifestPath)
    if ($manifestText -notmatch '"testables"') {
        $manifestText = ([regex]'\{').Replace($manifestText, "{`n  `"testables`": [`"com.yunusburkut.gamekit`"],", 1)
        [IO.File]::WriteAllText($manifestPath, $manifestText, (New-Object Text.UTF8Encoding $false))
    }
    foreach ($platform in 'EditMode', 'PlayMode') {
        $results = Join-Path $game "Logs\tests-$platform.xml"
        $testLog = Join-Path $game "Logs\tests-$platform.log"
        $run = Start-Process -FilePath $Unity -PassThru -NoNewWindow -ArgumentList @(
            '-batchmode', '-projectPath', "`"$game`"", '-runTests', '-testPlatform', $platform,
            '-testResults', "`"$results`"", '-logFile', "`"$testLog`"")
        $null = $run.Handle   # PowerShell 5.1: without the cached handle ExitCode reads empty after the exit
        if (-not $run.WaitForExit($TimeoutMinutes * 60000)) {
            # a licence or package prompt, or a lock from a crashed Editor, would otherwise wait forever
            cmd /c "taskkill /T /F /PID $($run.Id) >nul 2>&1"
            Check $false "$platform tests finished within $TimeoutMinutes min (killed)"
            if (Test-Path -LiteralPath $testLog) { Get-Content -LiteralPath $testLog -Tail 30 | ForEach-Object { Write-Host "    $_" } }
            continue
        }
        $summary = if (Test-Path -LiteralPath $results) { ([xml](Get-Content -LiteralPath $results -Raw)).'test-run' }
        Check ($run.ExitCode -eq 0 -and $summary -and [int]$summary.total -gt 0) "$platform tests: $($summary.passed)/$($summary.total) passed"
    }
}

# Code the skills hand to agents, which nothing else builds, compiled and run in one more Unity launch: unity-performance's
# AssetAudit.cs (run once: its report must hold both tables), urp-postprocessing's complete `public static class` Editor
# blocks (compiled, then CreateGlobalVolume, EnableCameraPostFx and PostFxPreflight run in a throwaway scene) and, with
# coop-multiplayer, a probe of the two FishNet APIs networking.md relies on (ServerRpc codegen, FishyUnityTransport's
# byte-array SetRelayServerData) and, with toon-art, examples/PropBuilder.cs.txt copied in as the art-pipeline skill
# says (Editor/Art, in __GAME__.Editor next to ToonShader). Ceiling: other skills' C# blocks are left out (some use
# game types, and Feel is missing when no sibling project has it); add a skill to $snippetSkills once its blocks
# compile on their own. PropBuilder is compiled, not run: running RebuildAll and measuring the "keeps Blender X,
# negates Z" axis claim needs an asymmetric FBX fixture under Game/Art/Models (the way up). The probe files are
# removed afterwards.
$probeCoop = $Packs -contains 'coop-multiplayer'
$probeToon = $Packs -contains 'toon-art'
if (($Tests -or $probeCoop -or $probeToon) -and -not $setupFailed) {
    $utf8 = New-Object Text.UTF8Encoding $false
    $probeDir = Join-Path $game 'Assets\__SkillProbe'
    $probeEditor = Join-Path $probeDir 'Editor'
    New-Item -ItemType Directory -Force $probeEditor | Out-Null
    Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'plugin\skills\unity-performance\scripts\AssetAudit.cs') -Destination $probeEditor
    $snippetSkills = 'urp-postprocessing'
    # plus single pages whose `public static class` blocks compile alone: unity-package-management's headless installer
    $snippetPages = 'unity-package-management\references\headless.md'
    $snippets = New-Object System.Collections.Generic.List[string]
    foreach ($md in @($snippetSkills | ForEach-Object { Get-ChildItem -Path (Join-Path $PSScriptRoot "plugin\skills\$_") -Recurse -Filter *.md }) +
            @($snippetPages | ForEach-Object { Get-Item -LiteralPath (Join-Path $PSScriptRoot "plugin\skills\$_") })) {
        foreach ($m in [regex]::Matches([IO.File]::ReadAllText($md.FullName), '(?s)```csharp\r?\n(.*?)```')) {
            $cls = [regex]::Match($m.Groups[1].Value, 'public static class (\w+)')
            if ($cls.Success) { [IO.File]::WriteAllText((Join-Path $probeEditor "$($cls.Groups[1].Value).cs"), $m.Groups[1].Value, $utf8); $snippets.Add($cls.Groups[1].Value) }
        }
    }
    # Logs\, not Temp\: Unity empties Temp\ when it quits. urp-postprocessing runs as the skill orders it (Create, Enable,
    # then the pre-flight) in a saved throwaway scene, and the profile is read back from disk: its past bugs were logic
    # (overrides left as missing sub-assets, a pre-flight that passed a broken tier), which compiling alone never shows
    [IO.File]::WriteAllText((Join-Path $probeEditor 'SkillProbe.cs'), @'
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

public static class SkillProbe
{
    public static void Run()
    {
        System.IO.File.WriteAllText("Logs/asset-audit.txt", AssetAudit.Run());
        var report = new System.Text.StringBuilder();
        try
        {
            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var cam = new GameObject("Main Camera") { tag = "MainCamera" };
            cam.AddComponent<Camera>();
            if (!cam.TryGetComponent<UniversalAdditionalCameraData>(out _)) cam.AddComponent<UniversalAdditionalCameraData>();
            EditorSceneManager.SaveScene(scene, "Assets/__SkillProbe/PostFxProbe.unity");
            report.AppendLine("create: " + CreateGlobalVolume.Run());
            EditorSceneManager.SaveScene(scene);
            report.AppendLine("enable: " + EnableCameraPostFx.Run());
            EditorSceneManager.SaveScene(scene);
            var path = AssetDatabase.GetAssetPath(Object.FindObjectsByType<Volume>()[0].sharedProfile);
            report.AppendLine("subassets: " + string.Join(",", AssetDatabase.LoadAllAssetsAtPath(path).Select(o => o.GetType().Name)));
            report.AppendLine("preflight: " + PostFxPreflight.Run().Replace("\r", "").Replace("\n", " "));
            AssetDatabase.DeleteAsset(path);
        }
        catch (System.Exception e) { report.AppendLine("exception: " + e.Message); }
        System.IO.File.WriteAllText("Logs/postfx-probe.txt", report.ToString());
    }
}
'@, $utf8)
    if ($probeCoop) {
        $probeNet = Join-Path $probeDir 'Net'
        New-Item -ItemType Directory -Force $probeNet | Out-Null
        [IO.File]::WriteAllText((Join-Path $probeNet 'GkProbe.Net.asmdef'), "{`n    `"name`": `"GkProbe.Net`",`n    `"references`": [`"FishNet.Runtime`", `"FishyUnityTransport`", `"Unity.Networking.Transport`"],`n    `"autoReferenced`": false`n}`n", $utf8)
        [IO.File]::WriteAllText((Join-Path $probeNet 'NetProbe.cs'), @'
using FishNet.Object;
using FishNet.Transporting.UTP;

namespace GkProbe.Net
{
    public class NetProbe : NetworkBehaviour
    {
        [ServerRpc] void Ping(int value) { }

        public static void Relay(UnityTransport transport) =>
            transport.SetRelayServerData("127.0.0.1", 7777, new byte[16], new byte[64], new byte[255], new byte[255], true);
    }
}
'@, $utf8)
    }
    # unity-architecture's core-system skeleton, the shape every new Core system copies: each block split one type per
    # file, as the page tells a game to, into the game's own Core\Countdown and Game\Countdown (its asmdefs, SimulationStep)
    $skeleton = New-Object System.Collections.Generic.List[string]
    $skeletonDirs = @()
    $skelText = [IO.File]::ReadAllText((Join-Path $PSScriptRoot 'plugin\skills\unity-architecture\references\core-system-skeleton.md'))
    foreach ($m in [regex]::Matches($skelText, '(?s)```csharp\r?\n(.*?)```')) {
        $code = $m.Groups[1].Value.Replace('__GAME__', $name) -replace '\r\n', "`n"
        $ns = [regex]::Match($code, '(?s)\A(.*?)namespace ([\w.]+)\n\{\n(.*)\n\}\s*\z')
        if (-not $ns.Success) { continue }   # the EditMode test fragment has no namespace
        $dir = Join-Path $game "Assets\$name\$($ns.Groups[2].Value.Split('.')[-1])\Countdown"
        New-Item -ItemType Directory -Force $dir | Out-Null
        $skeletonDirs += $dir
        # a type ends at its closing brace at namespace indent; the comments and attributes above a type stay with it
        foreach ($chunk in [regex]::Split($ns.Groups[3].Value, '(?m)(?<=^    \}\n)\n*')) {
            $type = [regex]::Match($chunk, '(?m)^    public [\w ]*?(?:class|struct) (\w+)')
            if (-not $type.Success) { continue }
            [IO.File]::WriteAllText((Join-Path $dir "$($type.Groups[1].Value).cs"), "$($ns.Groups[1].Value)namespace $($ns.Groups[2].Value)`n{`n$($chunk.TrimEnd())`n}`n", $utf8)
            $skeleton.Add($type.Groups[1].Value)
        }
    }
    $propBuilder = Join-Path $game "Assets\$name\Editor\Art\PropBuilder.cs"
    if ($probeToon) {
        New-Item -ItemType Directory -Force (Split-Path $propBuilder) | Out-Null
        [IO.File]::WriteAllText($propBuilder, [IO.File]::ReadAllText((Join-Path $PSScriptRoot 'packs\toon-art\examples\PropBuilder.cs.txt')).Replace('__GAME__', $name), $utf8)
    }
    $probeLog = Join-Path $game 'Logs\skill-probe.log'
    $auditOut = Join-Path $game 'Logs\asset-audit.txt'
    $run = Start-Process -FilePath $Unity -PassThru -NoNewWindow -ArgumentList @(
        '-batchmode', '-quit', '-projectPath', "`"$game`"", '-executeMethod', 'SkillProbe.Run', '-logFile', "`"$probeLog`"")
    $null = $run.Handle   # PowerShell 5.1: without the cached handle ExitCode reads empty after the exit
    $what = "skill code compiles and runs: AssetAudit.cs, $($snippets -join ', '), core-system skeleton $($skeleton.Count) types$(if ($probeCoop) { ', FishNet NetProbe' })$(if ($probeToon) { ', toon-art PropBuilder.cs.txt' })"
    if (-not $run.WaitForExit($TimeoutMinutes * 60000)) {
        cmd /c "taskkill /T /F /PID $($run.Id) >nul 2>&1"
        Check $false "$what (killed after $TimeoutMinutes min)"
    } else {
        $plog = if (Test-Path -LiteralPath $probeLog) { [IO.File]::ReadAllText($probeLog) } else { '' }
        Check ($run.ExitCode -eq 0 -and $snippets.Count -and $skeleton.Count -ge 7 -and $plog -notmatch 'error CS\d+') "$what $(([regex]::Matches($plog, 'error CS\d+[^\r\n]*') | Select-Object -First 3 | ForEach-Object Value) -join ' | ')"
        $audit = if (Test-Path -LiteralPath $auditOut) { [IO.File]::ReadAllText($auditOut) } else { '' }
        Check ($audit -match '(?m)^## Textures' -and $audit -match '(?m)^## Audio') 'unity-performance: AssetAudit.Run reports ## Textures and ## Audio'
        $pfxOut = Join-Path $game 'Logs\postfx-probe.txt'
        $pfx = if (Test-Path -LiteralPath $pfxOut) { [IO.File]::ReadAllText($pfxOut) } else { '' }
        $subs = [regex]::Match($pfx, '(?m)^subassets: ([^\r\n]*)').Groups[1].Value -split ','
        Check ($subs -contains 'Bloom' -and $subs -contains 'Tonemapping' -and $pfx -match '(?m)^preflight: .*looks correct' -and $pfx -notmatch '(?m)^exception:') "urp-postprocessing: CreateGlobalVolume stores Bloom and Tonemapping in the profile on disk, PostFxPreflight passes after EnableCameraPostFx $(($pfx -split '\r?\n' | Where-Object { $_ -match '^(subassets|preflight|exception):' }) -join ' | ')"
    }
    if ($run.ExitCode -ne 0 -and (Test-Path -LiteralPath $probeLog)) { Get-Content -LiteralPath $probeLog -Tail 20 | ForEach-Object { Write-Host "    $_" } }
    cmd /c rmdir /s /q "\\?\$probeDir"
    Remove-Item -LiteralPath "$probeDir.meta", $propBuilder, "$propBuilder.meta" -ErrorAction SilentlyContinue
    foreach ($d in $skeletonDirs) { Remove-Item -LiteralPath $d -Recurse -Force -ErrorAction SilentlyContinue; Remove-Item -LiteralPath "$d.meta" -ErrorAction SilentlyContinue }
}

$minutes = [math]::Round(((Get-Date) - $started).TotalMinutes, 1)
if ($failures.Count) { Write-Host "`nKept for diagnosis (Logs\setup.log, Logs\tests-*.log): $game" }
elseif ($Keep) { Write-Host "`nKept: $game" }
else { cmd /c rmdir /s /q "\\?\$game" }
if ($failures.Count) { Write-Host "`nFAIL: $($failures.Count) check(s), $minutes min" -ForegroundColor Red; exit 1 }
Write-Host "`nPASS in $minutes min" -ForegroundColor Green
exit 0
