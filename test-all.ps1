<#
.SYNOPSIS
    One entry point for every check of the template. Fast static checks over the whole repo, then the plugin's hook
    tests and validator; -Full adds test-template.ps1 (about 5 min, launches Unity).

.DESCRIPTION
    Static: every tracked JSON parses; every .ps1 parses and is ASCII or has a BOM (PowerShell 5.1 reads a BOM-less
    script as ANSI); every bash script passes bash -n; each skill and agent has name/description frontmatter (name =
    folder or file name, description <= 1024 chars); every references/ or scripts/ path a skill names exists; every
    GameKit file and folder has a committed .meta; project/ still carries the __GAME__ placeholder.
    Then plugin\test-hooks.ps1 and `claude plugin validate plugin` (its missing-version warning is intended).
    Exit 0 = all pass, 1 = a failure. Pure ASCII on purpose.

.EXAMPLE
    .\test-all.ps1

.EXAMPLE
    .\test-all.ps1 -Full -Packs mobile-2d
#>
param(
    [switch]$Full,
    [string[]]$Packs = @()
)

$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$started = Get-Date
$failures = New-Object System.Collections.Generic.List[string]
function Check([string]$what, [bool]$ok, [string]$detail = '') {
    if ($ok) { Write-Host "  ok    $what" }
    else { Write-Host "  FAIL  $what  $detail" -ForegroundColor Red; $failures.Add($what) }
}
function Section([string]$title) { Write-Host "`n== $title" }
$tracked = @(git ls-files)

Section 'JSON'
$bad = foreach ($f in $tracked -like '*.json') {
    try { $null = [IO.File]::ReadAllText((Resolve-Path -LiteralPath $f)) | ConvertFrom-Json } catch { $f }
}
Check "$(@($tracked -like '*.json').Count) JSON files parse" (-not $bad) ($bad -join ', ')

Section 'PowerShell'
$ps = @($tracked -like '*.ps1')
$parseBad = foreach ($f in $ps) {
    $errs = $null
    $null = [Management.Automation.Language.Parser]::ParseFile((Resolve-Path -LiteralPath $f), [ref]$null, [ref]$errs)
    if ($errs) { "$f ($($errs[0].Message))" }
}
Check "$($ps.Count) scripts parse" (-not $parseBad) ($parseBad -join '; ')
$encBad = foreach ($f in $ps) {
    $b = [IO.File]::ReadAllBytes((Resolve-Path -LiteralPath $f))
    $bom = $b.Length -ge 3 -and $b[0] -eq 0xEF -and $b[1] -eq 0xBB -and $b[2] -eq 0xBF
    if (-not $bom -and ($b | Where-Object { $_ -gt 127 } | Select-Object -First 1)) { $f }
}
Check 'scripts are ASCII or carry a BOM' (-not $encBad) ($encBad -join ', ')

Section 'Bash'
$bash = (Get-Command bash -ErrorAction SilentlyContinue).Source
# Git for Windows ships bash but does not put it on PATH for PowerShell
if (-not $bash) { $bash = @("$env:ProgramFiles\Git\bin\bash.exe") | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1 }
$sh = @($tracked | Where-Object { $_ -like '*.sh' -or $_ -like 'plugin/bin/*' })
if ($bash) {
    $shBad = foreach ($f in $sh) { cmd /c "`"$bash`" -n `"$f`" >nul 2>&1"; if ($LASTEXITCODE) { $f } }
    Check "$($sh.Count) bash scripts pass bash -n" (-not $shBad) ($shBad -join ', ')
} else { Write-Host '  skip  no bash (Git for Windows)' }

Section 'Skills and agents'
function Front([string]$path) {
    $m = [regex]::Match([IO.File]::ReadAllText((Resolve-Path -LiteralPath $path)), '(?s)\A---\r?\n(.*?)\r?\n---')
    $h = @{}
    if ($m.Success) { foreach ($l in $m.Groups[1].Value -split '\r?\n') { if ($l -match '^(\w+):\s*(.*)$') { $h[$Matches[1]] = $Matches[2] } } }
    return $h
}
$skills = @($tracked -like 'plugin/skills/*/SKILL.md')
$fmBad = foreach ($f in $skills) {
    $h = Front $f; $dir = Split-Path (Split-Path $f) -Leaf
    if ($h.name -ne $dir -or -not $h.description -or $h.description.Length -gt 1024) { $f }
}
Check "$($skills.Count) skills: name = folder, description 1-1024 chars" (-not $fmBad) ($fmBad -join ', ')
$agents = @($tracked -like 'plugin/agents/*.md')
$agBad = foreach ($f in $agents) {
    $h = Front $f
    if ($h.name -ne [IO.Path]::GetFileNameWithoutExtension($f) -or -not $h.description -or $h.description.Length -gt 1024) { $f }
}
Check "$($agents.Count) agents: name = file, description 1-1024 chars" (-not $agBad) ($agBad -join ', ')
$refCount = 0
$refBad = foreach ($f in $skills) {
    $dir = Split-Path $f
    $text = [IO.File]::ReadAllText((Resolve-Path -LiteralPath $f))
    foreach ($m in [regex]::Matches($text, '(?<![\w/.-])((?:references|scripts)/[\w./-]+\.\w+)')) {
        $refCount++
        if (-not (Test-Path -LiteralPath (Join-Path $dir $m.Groups[1].Value))) { "$f -> $($m.Groups[1].Value)" }
    }
}
Check "$refCount references/ and scripts/ paths named in skills exist" (-not $refBad) ($refBad -join '; ')

Section 'CCGS-derived content'
# genre-defaults sheets and source keys are checked in test-hooks.ps1; here: clarity-rules src keys and the licence
$cr = 'plugin/skills/player-clarity/references/clarity-rules.md'
$crText = [IO.File]::ReadAllText((Resolve-Path -LiteralPath $cr))
$defined = @([regex]::Matches($crText, '(?m)^- \*\*([A-Z0-9-]+):\*\*') | ForEach-Object { $_.Groups[1].Value })
$usedKeys = @([regex]::Matches($crText, '\(src: ([^)]+)\)') | ForEach-Object { $_.Groups[1].Value -split ',\s*' } | Sort-Object -Unique)
# KEY is the legend's placeholder (line 6), not a source
$usedKeys = @($usedKeys | Where-Object { $_ -ne 'KEY' })
$undef = @($usedKeys | Where-Object { $defined -notcontains $_ })
Check "clarity-rules: $($usedKeys.Count) src keys defined under Sources" ($usedKeys.Count -gt 0 -and -not $undef) ($undef -join ', ')
$ccgsFiles = @(git grep -l 'CCGS' -- plugin)
$noLicence = @($ccgsFiles | Where-Object { $_ -notlike 'plugin/skills/genre-defaults/*' -and -not (Select-String -LiteralPath $_ -Pattern 'genre-defaults/LICENSE\.md' -Quiet) })
Check "$($ccgsFiles.Count) files citing CCGS sit under genre-defaults or point to its LICENSE.md" (-not $noLicence) ($noLicence -join ', ')

Section 'Blender (headless, this machine)'
$blender = (Get-Command blender -ErrorAction SilentlyContinue).Source
if (-not $blender) { $blender = Get-ChildItem "$env:ProgramFiles\Blender Foundation" -Recurse -Filter blender.exe -ErrorAction SilentlyContinue | Sort-Object FullName -Descending | Select-Object -First 1 -Expand FullName }
if ($blender) {
    # Compiles every Python file Blender runs (the repo's packs and the user-level Blender skills) and exports a cube
    # with the unity-export FBX arguments. The toon-art examples are excerpts (kit_common needs a game's kit_palette),
    # so they are compiled, never imported.
    $py = @($tracked -like '*.py' | ForEach-Object { (Resolve-Path -LiteralPath $_).Path })
    $skillDir = Join-Path $env:USERPROFILE '.claude\skills'
    $py += @(Get-ChildItem -Path (Join-Path $skillDir 'blender-*'), (Join-Path $skillDir 'unity-export') -Recurse -Filter *.py -ErrorAction SilentlyContinue | ForEach-Object FullName)
    $fbx = Join-Path $env:TEMP 'gk-test-all-cube.fbx'
    $probe = Join-Path $env:TEMP 'gk-test-all-blender.py'
    $pyList = ($py | ForEach-Object { "r'$_'" }) -join ', '
    [IO.File]::WriteAllText($probe, @"
import bpy, py_compile, sys, os, tempfile
sys.dont_write_bytecode = True
bad = []
for f in [$pyList]:
    try: py_compile.compile(f, cfile=os.path.join(tempfile.gettempdir(), 'gk-test-all.pyc'), doraise=True)
    except Exception as e: bad.append(f + ': ' + str(e).splitlines()[0])
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.mesh.primitive_cube_add()
bpy.ops.export_scene.fbx(filepath=r'$fbx', use_selection=False, apply_scale_options='FBX_SCALE_UNITS', axis_forward='-Z', axis_up='Y', bake_space_transform=True, object_types={'MESH'}, use_mesh_modifiers=True, add_leaf_bones=False, bake_anim=False)
if not os.path.getsize(r'$fbx'): bad.append('fbx export empty')
print('GKRESULT %d %s' % (len(bad), ' | '.join(bad)))
sys.exit(1 if bad else 0)
"@, (New-Object Text.UTF8Encoding $false))
    $res = cmd /c "`"$blender`" --background --factory-startup --python-exit-code 1 --python `"$probe`" 2>&1"
    $line = ($res | Where-Object { $_ -like 'GKRESULT*' } | Select-Object -Last 1)
    Check "$(Split-Path (Split-Path $blender) -Leaf): $($py.Count) .py compile, headless FBX export" ($LASTEXITCODE -eq 0 -and $line -like 'GKRESULT 0*') "$line $(($res | Select-Object -Last 2) -join ' ')"
    Remove-Item -LiteralPath $probe, $fbx -ErrorAction SilentlyContinue
} else { Write-Host '  skip  no Blender installed' }
$cli = Get-ChildItem "$env:LOCALAPPDATA\Claude-Data\*\Claude Extensions\ant.dir.gh.blender.blender-mcp\blmcp\tools_helpers\blender_cli.py" -ErrorAction SilentlyContinue | Select-Object -First 1
if ($cli) {
    # local patch, lost on extension updates; without it every *_for_cli MCP call times out (see memory note)
    Check 'Blender MCP extension keeps the stdin=DEVNULL patch' (Select-String -LiteralPath $cli.FullName -Pattern 'stdin=subprocess\.DEVNULL' -Quiet)
} else { Write-Host '  skip  Blender MCP extension not installed' }

Section 'GameKit package'
$pkg = 'packages/com.yunusburkut.gamekit'
$assets = @($tracked -like "$pkg/*" | Where-Object { $_ -notlike '*.meta' })
$dirs = $assets | ForEach-Object { $d = Split-Path $_ -Parent; while ($d -and $d -ne ($pkg -replace '/', '\')) { $d; $d = Split-Path $d -Parent } } | Sort-Object -Unique
$metaBad = foreach ($p in @($assets) + @($dirs)) { if ($tracked -notcontains (($p -replace '\\', '/') + '.meta')) { $p } }
Check "$($assets.Count) files and $(@($dirs).Count) folders have a committed .meta" (-not $metaBad) ($metaBad -join ', ')

Section 'Template placeholders'
Check 'project/ carries __GAME__' ([bool](git grep -l '__GAME__' -- project | Select-Object -First 1))
Check 'new-game.ps1 fills __GAME__ and __COMPANY__' ((Get-Content -Raw new-game.ps1) -match '__GAME__' -and (Get-Content -Raw new-game.ps1) -match '__COMPANY__')

Section 'Plugin hooks (plugin\test-hooks.ps1)'
$out = & powershell -NoProfile -ExecutionPolicy Bypass -File plugin\test-hooks.ps1
$code = $LASTEXITCODE
$out | Where-Object { $_ -like 'FAIL*' } | ForEach-Object { Write-Host "        $_" -ForegroundColor Red }
Check "test-hooks: $(@($out -like 'PASS*').Count) pass, $(@($out -like 'FAIL*').Count) fail" ($code -eq 0)

Section 'Plugin manifest (claude plugin validate)'
if (Get-Command claude -ErrorAction SilentlyContinue) {
    $v = cmd /c "claude plugin validate plugin 2>&1"
    Check 'claude plugin validate plugin' ($LASTEXITCODE -eq 0) (($v | Select-Object -Last 3) -join ' | ')
} else { Write-Host '  skip  claude not on PATH' }

if ($Full) {
    Section 'Template end to end (test-template.ps1)'
    & (Join-Path $PSScriptRoot 'test-template.ps1') -Packs $Packs
    Check 'test-template.ps1' ($LASTEXITCODE -eq 0)
}

$sec = [math]::Round(((Get-Date) - $started).TotalSeconds)
if ($failures.Count) { Write-Host "`nFAIL: $($failures.Count) check(s) in $sec s: $($failures -join '; ')" -ForegroundColor Red; exit 1 }
Write-Host "`nPASS in $sec s$(if (-not $Full) { ' (static; -Full adds the Unity end-to-end run)' })" -ForegroundColor Green
exit 0
