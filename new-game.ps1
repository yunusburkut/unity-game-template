<#
.SYNOPSIS
    Starts a new Unity game repository from this template.

.DESCRIPTION
    Copies project\ to <Path>\<Name>, adds the opt-in packs from packs\ named in -Packs (each pack's packages.json
    merged into the manifest, its README's CLAUDE.md lines appended to the game's CLAUDE.md), replaces __GAME__ /
    __COMPANY__ in file names and contents, copies Feel from another local project (a paid Asset Store package,
    committed because game repos are private), runs ProjectSetup once in batch mode (URP Mobile + PC tiers, Input System only, Main
    scene; killed after -SetupTimeoutMinutes) and makes the first commit "Start <Name> from unity-game-template@<sha>"
    (body "Packs: a, b" when packs were added), the base gamekit:sync-template diffs from. It warns, and marks the sha -dirty, when project\, packs\ or this script
    have uncommitted changes, warns when the template HEAD is not on origin/main, and warns when this checkout's
    GameKit is newer than the tag the manifest pins (a release not finished). Each pack assembly under
    Assets\__GAME__\Game (mobile-store, steam), and each name in a pack's packages.json "gameReferences"
    (coop-multiplayer's FishNet + UGS stack), is added to __GAME__.Game.asmdef's references. Takes 2-5 minutes with
    ProjectSetup: an agent runs it in the background.

.EXAMPLE
    .\new-game.ps1 -Name SkyHopper

.EXAMPLE
    .\new-game.ps1 -Name SkyHopper -Packs coop-multiplayer,toon-art

.EXAMPLE
    .\new-game.ps1 -Name SkyHopper -Path D:\Games -NoSetup

.EXAMPLE
    .\new-game.ps1 -Name SkyHopper -GitHub

.EXAMPLE
    .\new-game.ps1 -ResolveUnity
#>
[CmdletBinding(DefaultParameterSetName = 'Make')]
param(
    [Parameter(Mandatory, ParameterSetName = 'Make')]
    [ValidatePattern('^[A-Z][A-Za-z0-9]*$')]
    [string]$Name,

    [string]$Path = 'C:\GitHub',

    [ValidatePattern('^[A-Za-z][A-Za-z0-9]*$')]
    [string]$Company = 'yunusburkut',

    # Folders under packs\ to add on top of project\ (each pack's README.md and examples\ stay behind).
    [string[]]$Packs = @(),

    # A project folder that has Assets\Feel. Default: the first folder under -Path that has one.
    [string]$FeelFrom,

    # Unity.exe. Default: the Hub install (its custom install folder, then the default one) that matches
    # project\ProjectSettings\ProjectVersion.txt.
    [string]$Unity,

    # Skip the batch-mode ProjectSetup run (run "GameKit > Set Up Project" from the menu later).
    [switch]$NoSetup,

    # The batch-mode ProjectSetup run is killed after this long (a first import takes a few minutes).
    [int]$SetupTimeoutMinutes = 30,

    [switch]$NoGit,

    # After the first commit, create a private GitHub repo named <Name> under the gh account and push main to it.
    [switch]$GitHub,

    # Point the game at this checkout's packages\com.yunusburkut.gamekit (file:) instead of the tagged git URL, to try
    # GameKit changes before tagging them.
    [switch]$LocalGameKit,

    # Print the Unity.exe the run would use (the -Unity default below) and stop; test-template.ps1 reads it.
    [Parameter(Mandatory, ParameterSetName = 'Resolve')]
    [switch]$ResolveUnity
)

$ErrorActionPreference = 'Stop'
$template = Join-Path $PSScriptRoot 'project'
$packRoot = Join-Path $PSScriptRoot 'packs'
if (-not $Unity) {
    # Hub's custom install location (Preferences > Installs) first, then its default. test-template.ps1 gets the
    # same editor for its test runs through -ResolveUnity.
    $version = (Select-String -LiteralPath (Join-Path $template 'ProjectSettings\ProjectVersion.txt') -Pattern '^m_EditorVersion: (.+)$').Matches[0].Groups[1].Value
    $hubDirs = @()
    $secondary = Join-Path $env:APPDATA 'UnityHub\secondaryInstallPath.json'
    if (Test-Path -LiteralPath $secondary) { $hubDirs += @([IO.File]::ReadAllText($secondary) | ConvertFrom-Json) | Where-Object { $_ } }
    $hubDirs += 'C:\Program Files\Unity\Hub\Editor'
    $candidates = @($hubDirs | ForEach-Object { Join-Path $_ "$version\Editor\Unity.exe" })
    # none installed: the default path, which the step 4 warning names
    $Unity = @($candidates | Where-Object { Test-Path -LiteralPath $_ }) + @($candidates[-1]) | Select-Object -First 1
}
# test-template.ps1 asks for the path only, so it tests with the editor a real game gets
if ($ResolveUnity) { return $Unity }

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

# the start commit records HEAD as the base gamekit:sync-template diffs from; it only describes the copy when the
# copied paths are committed, and it only stays valid when HEAD is on origin/main (pushed, never rewritten)
$templateDirty = $null
if (-not $NoGit) {
    $templateDirty = @(cmd /c "git -C `"$PSScriptRoot`" status --porcelain -- project packs new-game.ps1 2>nul")
    if ($templateDirty) {
        Write-Warning "The template has uncommitted changes under project/, packs/ or new-game.ps1; the start commit is marked -dirty and its base does not hold them:`n$($templateDirty -join "`n")"
    }
    cmd /c "git -C `"$PSScriptRoot`" merge-base --is-ancestor HEAD origin/main >nul 2>&1"
    if ($LASTEXITCODE -ne 0) {
        Write-Warning 'Template HEAD is not on origin/main (unpushed or no remote): push the template before syncing this game, or the sync base may not exist there.'
    }
}

# the shipped manifest pins a GameKit tag; a newer version in this checkout is not released yet (CLAUDE.md,
# Releasing GameKit), so this game gets the pinned one without it
if (-not $LocalGameKit) {
    $pin = [regex]::Match([IO.File]::ReadAllText((Join-Path $template 'Packages\manifest.json')), '#gamekit-v([\d.]+)"').Groups[1].Value
    $pkgVersion = (Get-Content -LiteralPath (Join-Path $PSScriptRoot 'packages\com.yunusburkut.gamekit\package.json') -Raw | ConvertFrom-Json).version
    if ($pin -and $pin -ne $pkgVersion) {
        Write-Warning "GameKit $pkgVersion in this checkout is not released: the game gets the pinned gamekit-v$pin. Finish the release (CLAUDE.md, Releasing GameKit) or pass -LocalGameKit."
    }
}

Write-Host "1/6 Copying the template to $dest"
# a template opened in Unity once has Library\ and friends; they must not seed a new game
$generated = 'Library', 'Temp', 'Logs', 'obj', 'UserSettings', 'Builds', '.vs', '.idea' | ForEach-Object { Join-Path $template $_ }
robocopy $template $dest /E /XD $generated /XF *.csproj *.sln /NFL /NDL /NJH /NJS /NP | Out-Null
if ($LASTEXITCODE -ge 8) { throw "robocopy failed copying the template ($LASTEXITCODE)." }

Write-Host '2/6 Packs'
$claudeBullets = New-Object System.Collections.Generic.List[string]
$claudeSections = New-Object System.Collections.Generic.List[string]
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

    # the README is never copied, so what the game's agents must know about the pack is lifted from it: the fenced
    # block under "## CLAUDE.md'ye eklenecek satir" (bullets for a "## Packs" section), or a fenced markdown block that
    # is a whole CLAUDE.md section (coop-multiplayer's "## Networking", which net-auditor reads). Single-quoted regexes
    # keep the backticks literal; \u0131 keeps this script ASCII.
    $readme = Join-Path $source 'README.md'
    if (Test-Path -LiteralPath $readme) {
        $readmeText = [IO.File]::ReadAllText($readme)
        $m = [regex]::Match($readmeText, '(?ms)^## CLAUDE\.md''ye eklenecek sat\u0131r[ \t]*\r?$.*?^```[^\r\n]*\r?\n(.*?)\r?\n```')
        if ($m.Success) { $claudeBullets.Add(($m.Groups[1].Value -replace '\r\n', "`n")) }
        foreach ($s in [regex]::Matches($readmeText, '(?ms)^```markdown\r?\n(## .*?)\r?\n```')) {
            $claudeSections.Add(($s.Groups[1].Value -replace '\r\n', "`n"))
        }
    }
    # a pack's own assembly under Game\ (mobile-store's __GAME__.Store, steam's __GAME__.Steam) is what game code
    # calls, so Game.asmdef references each one and the pack's CLAUDE.md line holds from the first commit (text
    # insert, layout kept). test-all.ps1 and test-template.ps1 check the result.
    $packGame = Join-Path $source 'Assets\__GAME__\Game'
    $packAsm = if (Test-Path -LiteralPath $packGame) { @(Get-ChildItem -LiteralPath $packGame -Recurse -Filter *.asmdef | ForEach-Object BaseName) } else { @() }
    # and the package assemblies a pack's packages.json lists under gameReferences (coop-multiplayer's FishNet + UGS stack)
    if (Test-Path -LiteralPath $packages) {
        $packAsm += @((Get-Content -LiteralPath $packages -Raw | ConvertFrom-Json).gameReferences | Where-Object { $_ })
    }
    foreach ($asmName in $packAsm) {
        $asmdef = Join-Path $dest 'Assets\__GAME__\Game\__GAME__.Game.asmdef'
        $asmText = [IO.File]::ReadAllText($asmdef)
        if ($asmText -notmatch ('"' + [regex]::Escape($asmName) + '"')) {
            $asmText = ([regex]'("references"\s*:\s*\[[^\]]*?)\s*\]').Replace($asmText, {
                param($r) $r.Groups[1].Value + $(if ($r.Groups[1].Value -match '\[\s*$') { '' } else { ', ' }) + "`"$asmName`"]" }, 1)
            [IO.File]::WriteAllText($asmdef, $asmText, (New-Object System.Text.UTF8Encoding $false))
        }
    }
    Write-Host "    added $pack"
}
if (-not $Packs) { Write-Host '    none' }
if ($claudeBullets.Count -or $claudeSections.Count) {
    # appended before the placeholder pass below, which fills in the blocks' __GAME__
    $claudePath = Join-Path $dest 'CLAUDE.md'
    $claude = [IO.File]::ReadAllText($claudePath).TrimEnd() + "`n"
    if ($claudeBullets.Count) { $claude += "`n## Packs`n`n" + ($claudeBullets -join "`n") + "`n" }
    foreach ($s in $claudeSections) { $claude += "`n$s`n" }
    [IO.File]::WriteAllText($claudePath, $claude, (New-Object System.Text.UTF8Encoding $false))
}

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
        $run = Start-Process -FilePath $Unity -PassThru -NoNewWindow -ArgumentList @(
            '-batchmode', '-quit', '-projectPath', "`"$dest`"",
            '-executeMethod', "GameKit.Editor.ProjectSetup.Run", '-gameCompany', $Company, '-logFile', "`"$log`"")
        $null = $run.Handle   # PowerShell 5.1: without the cached handle ExitCode reads empty after the exit
        if (-not $run.WaitForExit($SetupTimeoutMinutes * 60000)) {
            # a licence or package-resolve prompt, or a lock left by a crashed Editor, would otherwise wait forever
            cmd /c "taskkill /T /F /PID $($run.Id) >nul 2>&1"
            if (Test-Path -LiteralPath $log) { Get-Content -LiteralPath $log -Tail 30 | ForEach-Object { Write-Host "    $_" } }
            throw "ProjectSetup did not finish within $SetupTimeoutMinutes min; Unity was killed. See $log"
        }
        if ($run.ExitCode -ne 0) {
            # usually a compile error in project\ or a pack (batch mode exits 1 on it): show the errors and the tail
            # here, so the caller does not have to search a log of several MB
            if (Test-Path -LiteralPath $log) {
                $errors = @(Select-String -LiteralPath $log -Pattern 'error CS\d+|Shader error in' | Select-Object -First 10 | ForEach-Object Line)
                if ($errors) { Write-Host '    Errors:'; $errors | ForEach-Object { Write-Host "    $_" } }
                Write-Host '    Log tail:'; Get-Content -LiteralPath $log -Tail 30 | ForEach-Object { Write-Host "    $_" }
            }
            throw "ProjectSetup failed (exit $($run.ExitCode)). See $log"
        }
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
    $marker = "unity-game-template@$templateSha"
    $templateNote = ''
    if ($templateDirty) {
        # the copy holds edits no commit has, so the base cannot describe it; sync-template reads only the hex sha
        $marker += '-dirty'
        $templateNote = "`n`nThe template had uncommitted changes under project/, packs/ or new-game.ps1:`n$($templateDirty -join "`n")"
    }
    # sync.sh reads the pack list from this line; without it it guesses from which pack files still exist
    $packsNote = if ($Packs) { "`n`nPacks: $($Packs -join ', ')" } else { '' }
    # from a file (UTF-8, LF), not -m: PowerShell 5.1 passes the quotes porcelain puts around a path with spaces
    # unescaped, so an inline message splits into pathspecs and the commit fails after the copy and the setup run
    $msgFile = Join-Path $dest '.git\GK_START_MSG'
    [IO.File]::WriteAllText($msgFile, "Start $Name from $marker$packsNote$templateNote`n", $utf8)
    git -C $dest commit -q -F $msgFile
    $commitExit = $LASTEXITCODE
    Remove-Item -LiteralPath $msgFile -ErrorAction SilentlyContinue
    if ($commitExit -ne 0) { throw "git commit failed ($commitExit)." }
    # enabled after the first commit: with -NoSetup a pack's scripts have no .meta yet, and the hook would refuse it
    git -C $dest config core.hooksPath .githooks
    Write-Host '    first commit made on main; the .meta pre-commit hook is on'
    if ($GitHub) {
        # a failure here leaves a complete local game, so warn with the retry instead of throwing. gh prefers
        # GH_TOKEN/GITHUB_TOKEN over the `gh auth login` credentials, and the read-only token for plugin updates
        # (README.md, token conflict) would get a 403: both are cleared for this call (and its git push) only
        $tokens = @{ GITHUB_TOKEN = $env:GITHUB_TOKEN; GH_TOKEN = $env:GH_TOKEN }
        try {
            $env:GITHUB_TOKEN = $null; $env:GH_TOKEN = $null
            gh repo create $Name --private --source $dest --remote origin --push
        } finally {
            foreach ($k in $tokens.Keys) { [Environment]::SetEnvironmentVariable($k, $tokens[$k], 'Process') }
        }
        if ($LASTEXITCODE -ne 0) {
            Write-Warning "GitHub repo not created; the game is ready locally. Retry: `$env:GITHUB_TOKEN = `$null; `$env:GH_TOKEN = `$null; gh repo create $Name --private --source `"$dest`" --remote origin --push"
        } else {
            Write-Host "    pushed main to a private GitHub repo: $Name"
        }
    }
    $ErrorActionPreference = 'Stop'
}

Write-Host "6/6 Ready: $dest"
Write-Host '    Open it in Unity Hub (Add > Add project from disk), then start Claude Code in that folder.'
Write-Host '    First step there: /gamekit:new-game shape (it fills in the TODO lines in CLAUDE.md and DESIGN.md with you).'
Write-Host '    How to work with Claude: REHBER.md.'

# robocopy leaves 1-7 in $LASTEXITCODE on success; do not let that become the script's exit code
exit 0
