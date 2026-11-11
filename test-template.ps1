<#
.SYNOPSIS
    Checks that the template still makes a working game: runs new-game.ps1 into a temp folder with this checkout's
    GameKit, then asserts the result. Run it after changing project\, packs\, packages\ or new-game.ps1.

.DESCRIPTION
    Checks: ProjectSetup finished with 0 compile errors, Main.unity exists, the first commit carries the
    unity-game-template@<sha> sync marker, GameKit comes from this checkout, and Feel is committed when one was found.
    -Tests also runs the game's EditMode and PlayMode tests (two more Unity launches). The temp game is deleted unless
    -Keep. Exit code 0 = pass, 1 = fail.

.EXAMPLE
    .\test-template.ps1

.EXAMPLE
    .\test-template.ps1 -Packs mobile-2d,steam -Tests
#>
param(
    # Packs to include; test the ones you changed. Packs are not combined by default: not every pair makes sense.
    [string[]]$Packs = @(),
    [switch]$Tests,
    [switch]$Keep
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
Check ((Get-Content -LiteralPath (Join-Path $game 'Packages\manifest.json') -Raw) -match '"com\.yunusburkut\.gamekit":\s*"file:') 'GameKit from this checkout'
if (Test-Path -LiteralPath (Join-Path $game 'Assets\Feel')) {
    Check ([bool](git -C $game ls-files 'Assets/Feel/*.cs' | Select-Object -First 1)) 'Feel committed'
}

if ($Tests) {
    $version = (Select-String -LiteralPath (Join-Path $PSScriptRoot 'project\ProjectSettings\ProjectVersion.txt') -Pattern '^m_EditorVersion: (.+)$').Matches[0].Groups[1].Value
    $unity = "C:\Program Files\Unity\Hub\Editor\$version\Editor\Unity.exe"
    foreach ($platform in 'EditMode', 'PlayMode') {
        $results = Join-Path $game "Logs\tests-$platform.xml"
        $run = Start-Process -FilePath $unity -Wait -PassThru -NoNewWindow -ArgumentList @(
            '-batchmode', '-projectPath', "`"$game`"", '-runTests', '-testPlatform', $platform,
            '-testResults', "`"$results`"", '-logFile', "`"$(Join-Path $game "Logs\tests-$platform.log")`"")
        $summary = if (Test-Path -LiteralPath $results) { ([xml](Get-Content -LiteralPath $results -Raw)).'test-run' }
        Check ($run.ExitCode -eq 0 -and $summary -and [int]$summary.total -gt 0) "$platform tests: $($summary.passed)/$($summary.total) passed"
    }
}

$minutes = [math]::Round(((Get-Date) - $started).TotalMinutes, 1)
if ($Keep) { Write-Host "`nKept: $game" } else { cmd /c rmdir /s /q "\\?\$game" }
if ($failures.Count) { Write-Host "`nFAIL: $($failures.Count) check(s), $minutes min" -ForegroundColor Red; exit 1 }
Write-Host "`nPASS in $minutes min" -ForegroundColor Green
exit 0
