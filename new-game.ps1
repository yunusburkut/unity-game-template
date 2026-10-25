<#
.SYNOPSIS
    Starts a new Unity game repository from this template.

.DESCRIPTION
    Copies project\ to <Path>\<Name>, adds the opt-in packs from library\ named in -Packs, replaces __GAME__ /
    __COMPANY__ in file names and contents, copies Feel from another local project (it is a paid Asset Store package
    and never committed), runs ProjectSetup once in batch mode (URP Mobile + PC tiers, Input System only, Main
    scene) and makes the first commit.

.EXAMPLE
    .\new-game.ps1 -Name SkyHopper

.EXAMPLE
    .\new-game.ps1 -Name SkyHopper -Packs coop-multiplayer,toon-art

.EXAMPLE
    .\new-game.ps1 -Name SkyHopper -Path D:\Games -NoSetup
#>
param(
    [Parameter(Mandatory)]
    [ValidatePattern('^[A-Z][A-Za-z0-9]*$')]
    [string]$Name,

    [string]$Path = 'C:\GitHub',

    [ValidatePattern('^[A-Za-z][A-Za-z0-9]*$')]
    [string]$Company = 'yunusburkut',

    # Folders under library\ to add on top of project\ (each pack's README.md and examples\ stay behind).
    [string[]]$Packs = @(),

    # A project folder that has Assets\Feel. Default: the first folder under -Path that has one.
    [string]$FeelFrom,

    # Unity.exe. Default: the Hub install that matches project\ProjectSettings\ProjectVersion.txt.
    [string]$Unity,

    # Skip the batch-mode ProjectSetup run (run "<Name> > Set Up Project" from the menu later).
    [switch]$NoSetup,

    [switch]$NoGit
)

$ErrorActionPreference = 'Stop'
$template = Join-Path $PSScriptRoot 'project'
$library = Join-Path $PSScriptRoot 'library'
$dest = Join-Path $Path $Name
if (Test-Path -LiteralPath $dest) { throw "$dest already exists." }

# reference-docs is reading material, not a pack
$available = Get-ChildItem -LiteralPath $library -Directory | Where-Object Name -ne 'reference-docs' | ForEach-Object Name
foreach ($pack in $Packs) {
    if ($available -notcontains $pack) { throw "Unknown pack '$pack'. Available: $($available -join ', ')." }
}

Write-Host "1/6 Copying the template to $dest"
Copy-Item -LiteralPath $template -Destination $dest -Recurse

Write-Host '2/6 Packs'
foreach ($pack in $Packs) {
    $source = Join-Path $library $pack
    # merged before the rename below, so the pack's Assets\__GAME__ lands in the template's and both get renamed once
    robocopy $source $dest /E /XF (Join-Path $source 'README.md') (Join-Path $source 'packages.json') /XD (Join-Path $source 'examples') /NFL /NDL /NJH /NJS /NP | Out-Null
    if ($LASTEXITCODE -ge 8) { throw "robocopy failed copying pack $pack ($LASTEXITCODE)." }

    # a pack's packages.json lists UPM dependencies; insert the missing ones as text so the manifest keeps its layout
    $packages = Join-Path $source 'packages.json'
    if (Test-Path -LiteralPath $packages) {
        $manifestPath = Join-Path $dest 'Packages\manifest.json'
        $manifest = [IO.File]::ReadAllText($manifestPath)
        $lines = foreach ($dep in (Get-Content -LiteralPath $packages -Raw | ConvertFrom-Json).dependencies.PSObject.Properties) {
            if ($manifest -notmatch ('"' + [regex]::Escape($dep.Name) + '"')) { "    `"$($dep.Name)`": `"$($dep.Value)`"," }
        }
        if ($lines) {
            $manifest = ([regex]'"dependencies"\s*:\s*\{\s*\n').Replace($manifest, { param($m) $m.Value + ($lines -join "`n") + "`n" }, 1)
            [IO.File]::WriteAllText($manifestPath, $manifest, (New-Object System.Text.UTF8Encoding $false))
        }
    }
    Write-Host "    added $pack"
}
if (-not $Packs) { Write-Host '    none' }

# deepest first, so a renamed folder never invalidates a path still to be renamed
Get-ChildItem -LiteralPath $dest -Recurse -Force |
    Where-Object { $_.Name -like '*__GAME__*' } |
    Sort-Object { $_.FullName.Length } -Descending |
    ForEach-Object { Rename-Item -LiteralPath $_.FullName -NewName ($_.Name -replace '__GAME__', $Name) }

$utf8 = New-Object System.Text.UTF8Encoding $false
$textExtensions = '.cs', '.asmdef', '.md', '.json', '.txt', '.html', '.ps1', '.gitignore', '.shader', '.hlsl', '.sh'
Get-ChildItem -LiteralPath $dest -Recurse -File -Force |
    Where-Object { $textExtensions -contains $_.Extension } |
    ForEach-Object {
        $content = [IO.File]::ReadAllText($_.FullName)
        if ($content -match '__GAME__|__COMPANY__') {
            $content = $content.Replace('__GAME__', $Name).Replace('__COMPANY__', $Company)
            [IO.File]::WriteAllText($_.FullName, $content, $utf8)
        }
    }

Write-Host '3/6 Feel'
if (-not $FeelFrom) {
    $FeelFrom = Get-ChildItem -LiteralPath $Path -Directory -ErrorAction SilentlyContinue |
        Where-Object { $_.FullName -ne $dest -and (Test-Path (Join-Path $_.FullName 'Assets\Feel\MMFeedbacks')) } |
        Select-Object -First 1 -ExpandProperty FullName
}
if ($FeelFrom -and (Test-Path (Join-Path $FeelFrom 'Assets\Feel'))) {
    robocopy (Join-Path $FeelFrom 'Assets\Feel') (Join-Path $dest 'Assets\Feel') /E /NFL /NDL /NJH /NJS /NP | Out-Null
    if ($LASTEXITCODE -ge 8) { throw "robocopy failed copying Feel ($LASTEXITCODE)." }
    $meta = Join-Path $FeelFrom 'Assets\Feel.meta'
    if (Test-Path $meta) { Copy-Item -LiteralPath $meta -Destination (Join-Path $dest 'Assets\Feel.meta') }
    Write-Host "    copied from $FeelFrom"
} else {
    Write-Warning 'No local Feel found: import Feel from the Asset Store into Assets\Feel later.'
}

Write-Host '4/6 ProjectSetup (first import takes a few minutes)'
if (-not $NoSetup) {
    if (-not $Unity) {
        $version = (Select-String -LiteralPath (Join-Path $dest 'ProjectSettings\ProjectVersion.txt') -Pattern '^m_EditorVersion: (.+)$').Matches[0].Groups[1].Value
        $Unity = "C:\Program Files\Unity\Hub\Editor\$version\Editor\Unity.exe"
    }
    if (Test-Path -LiteralPath $Unity) {
        $log = Join-Path $dest 'Logs\setup.log'
        New-Item -ItemType Directory -Force (Split-Path $log) | Out-Null
        $run = Start-Process -FilePath $Unity -Wait -PassThru -NoNewWindow -ArgumentList @(
            '-batchmode', '-quit', '-projectPath', "`"$dest`"",
            '-executeMethod', "$Name.Editor.ProjectSetup.Run", '-logFile', "`"$log`"")
        if ($run.ExitCode -ne 0) { throw "ProjectSetup failed (exit $($run.ExitCode)). See $log" }
        Write-Host "    done, log: $log"
    } else {
        Write-Warning "Unity not found at $Unity. Open the project in Unity and run '$Name > Set Up Project'."
    }
} else {
    Write-Host "    skipped: run '$Name > Set Up Project' from the menu once Unity has opened the project."
}

Write-Host '5/6 Git'
if (-not $NoGit) {
    # git writes warnings to stderr; under 'Stop' a redirected caller would see them as a terminating error
    $ErrorActionPreference = 'Continue'
    git -C $dest init -b main | Out-Null
    git -C $dest add -A
    git -C $dest commit -q -m "Start $Name from unity-game-template"
    if ($LASTEXITCODE -ne 0) { throw "git commit failed ($LASTEXITCODE)." }
    $ErrorActionPreference = 'Stop'
    Write-Host '    first commit made on main'
}

Write-Host "6/6 Ready: $dest"
Write-Host '    Open it in Unity Hub (Add > Add project from disk), then start Claude Code in that folder.'
Write-Host '    Fill in the TODO lines in CLAUDE.md and DESIGN.md first.'

# robocopy leaves 1-7 in $LASTEXITCODE on success; do not let that become the script's exit code
exit 0
