<#
.SYNOPSIS
    Starts a new Unity game repository from this template.

.DESCRIPTION
    Copies project\ to <Path>\<Name>, adds the opt-in packs from packs\ named in -Packs, replaces __GAME__ /
    __COMPANY__ in file names and contents, copies Feel from another local project (a paid Asset Store package,
    committed because game repos are private), runs ProjectSetup once in batch mode (URP Mobile + PC tiers, Input System only, Main
    scene) and makes the first commit.

.EXAMPLE
    .\new-game.ps1 -Name SkyHopper

.EXAMPLE
    .\new-game.ps1 -Name SkyHopper -Packs coop-multiplayer,toon-art

.EXAMPLE
    .\new-game.ps1 -Name SkyHopper -Path D:\Games -NoSetup

.EXAMPLE
    .\new-game.ps1 -Name SkyHopper -GitHub
#>
param(
    [Parameter(Mandatory)]
    [ValidatePattern('^[A-Z][A-Za-z0-9]*$')]
    [string]$Name,

    [string]$Path = 'C:\GitHub',

    [ValidatePattern('^[A-Za-z][A-Za-z0-9]*$')]
    [string]$Company = 'yunusburkut',

    # Folders under packs\ to add on top of project\ (each pack's README.md and examples\ stay behind).
    [string[]]$Packs = @(),

    # A project folder that has Assets\Feel. Default: the first folder under -Path that has one.
    [string]$FeelFrom,

    # Unity.exe. Default: the Hub install that matches project\ProjectSettings\ProjectVersion.txt.
    [string]$Unity,

    # Skip the batch-mode ProjectSetup run (run "GameKit > Set Up Project" from the menu later).
    [switch]$NoSetup,

    [switch]$NoGit,

    # After the first commit, create a private GitHub repo named <Name> under the gh account and push main to it.
    [switch]$GitHub,

    # Point the game at this checkout's packages\com.yunusburkut.gamekit (file:) instead of the tagged git URL, to try
    # GameKit changes before tagging them.
    [switch]$LocalGameKit
)

$ErrorActionPreference = 'Stop'
$template = Join-Path $PSScriptRoot 'project'
$packRoot = Join-Path $PSScriptRoot 'packs'
$dest = Join-Path $Path $Name
# absolute: [IO.File] calls resolve a relative path against the process directory, which cd does not change
$dest = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($dest)
if (Test-Path -LiteralPath $dest) { throw "$dest already exists." }
# checked before the copy and the Unity run, not after minutes of work
if ($GitHub -and $NoGit) { throw '-GitHub pushes the first commit; it cannot be combined with -NoGit.' }
if ($GitHub -and -not (Get-Command gh -ErrorAction SilentlyContinue)) { throw '-GitHub needs the GitHub CLI (gh), logged in.' }

# reference-docs is reading material, not a pack
$available = Get-ChildItem -LiteralPath $packRoot -Directory | Where-Object Name -ne 'reference-docs' | ForEach-Object Name
foreach ($pack in $Packs) {
    if ($available -notcontains $pack) { throw "Unknown pack '$pack'. Available: $($available -join ', ')." }
}

if (-not $Unity) {
    $version = (Select-String -LiteralPath (Join-Path $template 'ProjectSettings\ProjectVersion.txt') -Pattern '^m_EditorVersion: (.+)$').Matches[0].Groups[1].Value
    $Unity = "C:\Program Files\Unity\Hub\Editor\$version\Editor\Unity.exe"
}

Write-Host "1/6 Copying the template to $dest"
# a template opened in Unity once has Library\ and friends; they must not seed a new game
$generated = 'Library', 'Temp', 'Logs', 'obj', 'UserSettings', 'Builds', '.vs', '.idea' | ForEach-Object { Join-Path $template $_ }
robocopy $template $dest /E /XD $generated /XF *.csproj *.sln /NFL /NDL /NJH /NJS /NP | Out-Null
if ($LASTEXITCODE -ge 8) { throw "robocopy failed copying the template ($LASTEXITCODE)." }

Write-Host '2/6 Packs'
foreach ($pack in $Packs) {
    $source = Join-Path $packRoot $pack
    # merged before the rename below, so the pack's Assets\__GAME__ lands in the template's and both get renamed once
    robocopy $source $dest /E /XF (Join-Path $source 'README.md') (Join-Path $source 'packages.json') /XD (Join-Path $source 'examples') /NFL /NDL /NJH /NJS /NP | Out-Null
    if ($LASTEXITCODE -ge 8) { throw "robocopy failed copying pack $pack ($LASTEXITCODE)." }

    # a pack's packages.json lists UPM dependencies and scoped registries; insert the missing ones as text so the
    # manifest keeps its layout
    $packages = Join-Path $source 'packages.json'
    if (Test-Path -LiteralPath $packages) {
        $manifestPath = Join-Path $dest 'Packages\manifest.json'
        $manifest = [IO.File]::ReadAllText($manifestPath)
        $spec = Get-Content -LiteralPath $packages -Raw | ConvertFrom-Json
        $lines = foreach ($dep in $spec.dependencies.PSObject.Properties) {
            if ($manifest -notmatch ('"' + [regex]::Escape($dep.Name) + '"')) { "    `"$($dep.Name)`": `"$($dep.Value)`"," }
        }
        if ($lines) {
            $manifest = ([regex]'"dependencies"\s*:\s*\{\s*\n').Replace($manifest, { param($m) $m.Value + ($lines -join "`n") + "`n" }, 1)
        }
        foreach ($registry in $spec.scopedRegistries) {
            # a registry another pack already added is not merged scope by scope: that is a one-line manual edit
            if ($manifest -match [regex]::Escape($registry.url)) {
                foreach ($scope in $registry.scopes) {
                    if ($manifest -notmatch ('"' + [regex]::Escape($scope) + '"')) {
                        Write-Warning "Add scope '$scope' to the $($registry.url) registry in Packages\manifest.json by hand."
                    }
                }
                continue
            }
            $scopes = ($registry.scopes | ForEach-Object { "`"$_`"" }) -join ', '
            $entry = "    {`n      `"name`": `"$($registry.name)`",`n      `"url`": `"$($registry.url)`",`n      `"scopes`": [ $scopes ]`n    }"
            if ($manifest -match '"scopedRegistries"\s*:\s*\[') {
                $manifest = ([regex]'"scopedRegistries"\s*:\s*\[\s*\n').Replace($manifest, { param($m) $m.Value + $entry + ",`n" }, 1)
            } else {
                $manifest = ([regex]'^\s*\{\s*\n').Replace($manifest, { param($m) $m.Value + "  `"scopedRegistries`": [`n" + $entry + "`n  ],`n" }, 1)
            }
        }
        [IO.File]::WriteAllText($manifestPath, $manifest, (New-Object System.Text.UTF8Encoding $false))
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
$textExtensions = '.cs', '.asmdef', '.md', '.json', '.txt', '.html', '.ps1', '.gitignore', '.shader', '.hlsl', '.sh', '.yml', '.yaml'
Get-ChildItem -LiteralPath $dest -Recurse -File -Force |
    Where-Object { $textExtensions -contains $_.Extension } |
    ForEach-Object {
        $content = [IO.File]::ReadAllText($_.FullName)
        if ($content -match '__GAME__|__COMPANY__') {
            $content = $content.Replace('__GAME__', $Name).Replace('__COMPANY__', $Company)
            [IO.File]::WriteAllText($_.FullName, $content, $utf8)
        }
    }

if ($LocalGameKit) {
    $manifestPath = Join-Path $dest 'Packages\manifest.json'
    $local = 'file:' + (Join-Path $PSScriptRoot 'packages\com.yunusburkut.gamekit').Replace('\', '/')
    $manifest = [IO.File]::ReadAllText($manifestPath) -replace '("com\.yunusburkut\.gamekit":\s*)"[^"]*"', "`$1`"$local`""
    [IO.File]::WriteAllText($manifestPath, $manifest, $utf8)
    Write-Host "    GameKit from $local"
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
    if (Test-Path -LiteralPath $Unity) {
        $log = Join-Path $dest 'Logs\setup.log'
        New-Item -ItemType Directory -Force (Split-Path $log) | Out-Null
        $run = Start-Process -FilePath $Unity -Wait -PassThru -NoNewWindow -ArgumentList @(
            '-batchmode', '-quit', '-projectPath', "`"$dest`"",
            '-executeMethod', "GameKit.Editor.ProjectSetup.Run", '-gameCompany', $Company, '-logFile', "`"$log`"")
        if ($run.ExitCode -ne 0) { throw "ProjectSetup failed (exit $($run.ExitCode)). See $log" }
        Write-Host "    done, log: $log"
    } else {
        Write-Warning "Unity not found at $Unity. Open the project in Unity and run 'GameKit > Set Up Project'."
    }
} else {
    Write-Host "    skipped: run 'GameKit > Set Up Project' from the menu once Unity has opened the project."
}

Write-Host '5/6 Git'
if (-not $NoGit) {
    # git writes warnings to stderr; under 'Stop' a redirected caller would see them as a terminating error
    $ErrorActionPreference = 'Continue'
    git -C $dest init -b main | Out-Null
    # .gitattributes routes scenes and prefabs to this driver; without it git merges them as plain text
    $yamlMerge = Join-Path (Split-Path $Unity) 'Data\Tools\UnityYAMLMerge.exe'
    if (Test-Path -LiteralPath $yamlMerge) {
        git -C $dest config merge.unityyamlmerge.name 'Unity SmartMerge'
        # git hands the driver extensionless temp files (.merge_file_XXXXXX): --force parses them as YAML anyway, and
        # --fallback none returns a conflict instead of opening a "Couldn't locate merge tool" dialog that hangs git
        git -C $dest config merge.unityyamlmerge.driver "'$($yamlMerge.Replace('\', '/'))' merge -h -p --force --fallback none %O %B %A %A"
        git -C $dest config merge.unityyamlmerge.recursive binary
    } else {
        Write-Warning "UnityYAMLMerge not found at $yamlMerge; scenes and prefabs merge as plain text until the driver is set (see .gitattributes)."
    }
    git -C $dest add -A
    git -C $dest update-index --chmod=+x .githooks/pre-commit
    # the template commit is the sync point gamekit:sync-template starts from
    $templateSha = git -C $PSScriptRoot rev-parse --short HEAD
    git -C $dest commit -q -m "Start $Name from unity-game-template@$templateSha"
    if ($LASTEXITCODE -ne 0) { throw "git commit failed ($LASTEXITCODE)." }
    # enabled after the first commit: with -NoSetup a pack's scripts have no .meta yet, and the hook would refuse it
    git -C $dest config core.hooksPath .githooks
    Write-Host '    first commit made on main; the .meta pre-commit hook is on'
    if ($GitHub) {
        # a failure here leaves a complete local game, so warn with the retry instead of throwing
        gh repo create $Name --private --source $dest --remote origin --push
        if ($LASTEXITCODE -ne 0) {
            Write-Warning "GitHub repo not created; the game is ready locally. Retry: gh repo create $Name --private --source `"$dest`" --remote origin --push"
        } else {
            Write-Host "    pushed main to a private GitHub repo: $Name"
        }
    }
    $ErrorActionPreference = 'Stop'
}

Write-Host "6/6 Ready: $dest"
Write-Host '    Open it in Unity Hub (Add > Add project from disk), then start Claude Code in that folder.'
Write-Host '    Fill in the TODO lines in CLAUDE.md and DESIGN.md first.'

# robocopy leaves 1-7 in $LASTEXITCODE on success; do not let that become the script's exit code
exit 0
