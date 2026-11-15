<#
.SYNOPSIS
    Checks that the template still makes a working game: runs new-game.ps1 into a temp folder with this checkout's
    GameKit, then asserts the result. Run it after changing project\, packs\, packages\ or new-game.ps1.

.DESCRIPTION
    Checks: ProjectSetup finished with 0 compile errors and no shader errors, Main.unity exists, the first commit
    carries the unity-game-template@<sha> sync marker, GameKit comes from this checkout, no __GAME__/__COMPANY__ is
    left in the committed game, Feel is committed when one was found, and each selected pack's own check passes
    ($packChecks below; toon-art's shader check, ci-github's GAMEKIT_TOKEN, each pack's packages.json dependencies,
    CLAUDE.md lines and Networking section, mobile-store's asmdef reference). -Tests also runs the game's EditMode and PlayMode tests (two more Unity launches).
    Takes 5-10 min: an agent runs it in the background. Each Unity launch is killed after -TimeoutMinutes and its log
    tail printed. The temp game is deleted on a pass unless -Keep, and kept on a failure for diagnosis.
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
    # per Unity test launch; new-game.ps1 has its own limit for the ProjectSetup run
    [int]$TimeoutMinutes = 30
)

$ErrorActionPreference = 'Stop'
$root = Join-Path $env:TEMP 'unity-game-template-test'
$name = 'TplTest'
$game = Join-Path $root $name
# a previous -Keep run or a crash leaves the folder; paths under Library pass 260 characters, hence \\?\ and rmdir
if (Test-Path -LiteralPath $game) { cmd /c rmdir /s /q "\\?\$game" }

$failures = New-Object System.Collections.Generic.List[string]
function Check([bool]$ok, [string]$what) {
    if ($ok) { Write-Host "  ok    $what" } else { Write-Host "  FAIL  $what" -ForegroundColor Red; $failures.Add($what) }
}

$started = Get-Date
& (Join-Path $PSScriptRoot 'new-game.ps1') -Name $name -Path $root -Packs $Packs -LocalGameKit
if ($LASTEXITCODE -ne 0) { throw "new-game.ps1 failed ($LASTEXITCODE)." }

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
if (Test-Path -LiteralPath (Join-Path $game 'Assets\Feel')) {
    Check ([bool](git -C $game ls-files 'Assets/Feel/*.cs' | Select-Object -First 1)) 'Feel committed'
}
# what a pack's own setup step logs when it worked (a warning path would otherwise pass as green)
$packChecks = @{
    'mobile-2d' = @{ Log = '\[Setup2D\] Done:'; What = 'Setup2D done (2D Renderer, 2D mode, orthographic Main camera)' }
}
foreach ($pack in $Packs) {
    if ($packChecks.ContainsKey($pack)) { Check ($text -match $packChecks[$pack].Log) "$pack`: $($packChecks[$pack].What)" }
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
# what new-game.ps1 merges from each pack: packages.json into the manifest, the README's CLAUDE.md block, the
# mobile-store asmdef reference (test-all.ps1 checks the manifest merge for all packs at once; this is the real game)
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
if ($Packs -contains 'mobile-store') {
    Check ([IO.File]::ReadAllText((Join-Path $game "Assets\$name\Game\$name.Game.asmdef")) -match "`"$name\.Store`"") "mobile-store: $name.Game.asmdef references $name.Store"
}
if (-not ($text -match '\[ProjectSetup\] Done:') -and $text) {
    Write-Host "`nLast 20 lines of Logs\setup.log:"; ($text -split '\r?\n' | Select-Object -Last 20) | ForEach-Object { Write-Host "    $_" }
}

if ($Tests) {
    # GameKit's own tests run only in this throwaway game: a real game does not list the package as testable, so its
    # suite never reruns ProjectSetup. Text insert keeps the manifest's LF formatting (no ConvertTo-Json rewrite).
    $manifestPath = Join-Path $game 'Packages\manifest.json'
    $manifestText = [IO.File]::ReadAllText($manifestPath)
    if ($manifestText -notmatch '"testables"') {
        $manifestText = ([regex]'\{').Replace($manifestText, "{`n  `"testables`": [`"com.yunusburkut.gamekit`"],", 1)
        [IO.File]::WriteAllText($manifestPath, $manifestText, (New-Object Text.UTF8Encoding $false))
    }
    $version = (Select-String -LiteralPath (Join-Path $PSScriptRoot 'project\ProjectSettings\ProjectVersion.txt') -Pattern '^m_EditorVersion: (.+)$').Matches[0].Groups[1].Value
    $unity = "C:\Program Files\Unity\Hub\Editor\$version\Editor\Unity.exe"
    foreach ($platform in 'EditMode', 'PlayMode') {
        $results = Join-Path $game "Logs\tests-$platform.xml"
        $testLog = Join-Path $game "Logs\tests-$platform.log"
        $run = Start-Process -FilePath $unity -PassThru -NoNewWindow -ArgumentList @(
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

$minutes = [math]::Round(((Get-Date) - $started).TotalMinutes, 1)
if ($failures.Count) { Write-Host "`nKept for diagnosis (Logs\setup.log, Logs\tests-*.log): $game" }
elseif ($Keep) { Write-Host "`nKept: $game" }
else { cmd /c rmdir /s /q "\\?\$game" }
if ($failures.Count) { Write-Host "`nFAIL: $($failures.Count) check(s), $minutes min" -ForegroundColor Red; exit 1 }
Write-Host "`nPASS in $minutes min" -ForegroundColor Green
exit 0
