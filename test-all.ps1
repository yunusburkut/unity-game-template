<#
.SYNOPSIS
    One entry point for every check of the template. Fast static checks over the whole repo, then the plugin's hook
    tests and validator; -Full adds test-template.ps1 (about 5 min, launches Unity).

.DESCRIPTION
    Static: every tracked JSON parses; every .ps1 parses and is ASCII or has a BOM (PowerShell 5.1 reads a BOM-less
    script as ANSI); every bash script passes bash -n; each skill and agent in plugin/ and packs/*/.claude/ has
    name/description frontmatter (name = folder or file name, description <= 250 chars, the listing budget); output
    styles have name/description; every references/, scripts/ and ${CLAUDE_PLUGIN_ROOT}/ path a skill or agent names
    exists; the docs/, Assets/, .claude/ and ~/.claude/skills/ paths in packs' .claude files exist; every backticked
    gk-bridge verb is in its usage block; packs/ci-github ci.yml has no tabs, GAMEKIT_TOKEN on both GameCI steps,
    no workflow-level Unity credentials and a pinned butler; feature.js scores findings with the rubric's weights; the
    names new-game's skill relies on exist; the CCGS-derived content keeps its source keys and licence pointer and the
    clarity CL IDs are unique and every cited one defined; every tracked export_scene.fbx call follows unity-export
    (FBX_SCALE_ALL, bake_space_transform=False; city_assets.py is pre-contract); every GameKit file and folder has a
    committed .meta.
    This machine (state no repo commit fixes): a missing user-level piece (README "Global Claude katmani") is listed;
    every tracked .py and every ~/.claude/skills/blender-*, unity-export .py compiles in Blender, a cube exports headless
    with unity-export's FBX call verbatim, and blender-image-to-3d's test_pack_mask.py passes; the Blender MCP
    extension keeps its stdin=DEVNULL patch (README.md, Blender step 5); a unity CLI newer than unity-editor-cli's stamp
    or unity-cli's CHANGELOG is a warning. Each is skipped when its tool is not installed.
    sync-template: plugin/skills/sync-template/scripts/test-sync.sh (a few seconds, no Unity, no network).
    Pack merge: new-game.ps1 -NoSetup -NoGit with every pack into %TEMP% (copy only, no Unity), then the merged
    manifest holds every pack's dependencies and registries and no __GAME__/__COMPANY__ is left.
    Then plugin\test-hooks.ps1 and `claude plugin validate plugin` (its missing-version warning is intended).
    About 20-40 s with Blender installed. -Full adds test-template.ps1 (5-10 min, Unity): run it in the background.
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
# plugin skills and agents, plus the ones packs copy into a game's .claude\
$skills = @($tracked | Where-Object { $_ -like 'plugin/skills/*/SKILL.md' -or $_ -like 'packs/*/.claude/skills/*/SKILL.md' })
# 250: the skill listing has a character budget and drops long descriptions (the spec limit is 1024)
$fmBad = foreach ($f in $skills) {
    $h = Front $f; $dir = Split-Path (Split-Path $f) -Leaf
    if ($h.name -ne $dir -or -not $h.description -or $h.description.Length -gt 250) { "$f ($($h.description.Length))" }
}
Check "$($skills.Count) skills: name = folder, description 1-250 chars" (-not $fmBad) ($fmBad -join ', ')
$agents = @($tracked | Where-Object { $_ -like 'plugin/agents/*.md' -or $_ -like 'packs/*/.claude/agents/*.md' })
$agBad = foreach ($f in $agents) {
    $h = Front $f
    if ($h.name -ne [IO.Path]::GetFileNameWithoutExtension($f) -or -not $h.description -or $h.description.Length -gt 250) { "$f ($($h.description.Length))" }
}
Check "$($agents.Count) agents: name = file, description 1-250 chars" (-not $agBad) ($agBad -join ', ')
$styles = @($tracked -like 'plugin/output-styles/*.md')
$stBad = foreach ($f in $styles) { $h = Front $f; if (-not $h.name -or -not $h.description) { $f } }
Check "$($styles.Count) output styles have name and description" (-not $stBad) ($stBad -join ', ')
# relative references/ and scripts/ paths resolve against the skill's folder; ${CLAUDE_PLUGIN_ROOT}/ paths (skills
# and agents load the reviewer rubrics this way) resolve against plugin/
$refCount = 0
$refBad = foreach ($f in @($skills) + @($agents)) {
    $dir = Split-Path $f
    $text = [IO.File]::ReadAllText((Resolve-Path -LiteralPath $f))
    if ($f -like '*/SKILL.md') {
        foreach ($m in [regex]::Matches($text, '(?<![\w/.-])((?:references|scripts)/[\w./-]+\.\w+)')) {
            $refCount++
            $rel = $m.Groups[1].Value
            if (Test-Path -LiteralPath (Join-Path $dir $rel)) { continue }
            # "the `game-feel` skill's references/x.md": the last plugin skill named in the 200 characters before it
            $before = $text.Substring([math]::Max(0, $m.Index - 200), [math]::Min(200, $m.Index))
            $owner = @([regex]::Matches($before, '`(?:gamekit:)?([a-z0-9-]+)`') | ForEach-Object { $_.Groups[1].Value } |
                Where-Object { Test-Path -LiteralPath "plugin/skills/$_" -PathType Container }) | Select-Object -Last 1
            if (-not $owner -or -not (Test-Path -LiteralPath "plugin/skills/$owner/$rel")) { "$f -> $rel" }
        }
    }
    foreach ($m in [regex]::Matches($text, '\$\{CLAUDE_PLUGIN_ROOT\}/([\w./-]*[\w-])')) {
        $refCount++
        if (-not (Test-Path -LiteralPath (Join-Path 'plugin' $m.Groups[1].Value))) { "$f -> `${CLAUDE_PLUGIN_ROOT}/$($m.Groups[1].Value)" }
    }
}
Check "$refCount references/, scripts/ and `${CLAUDE_PLUGIN_ROOT}/ paths named in skills and agents exist" (-not $refBad) ($refBad -join '; ')

# a pack's agents, rules and skills land in the game's .claude\: a backticked docs/, Assets/ or .claude/ path must be
# in the pack or project/ (lines about Mixtrol, the game the coop pack came from, are history); ~/.claude/skills/<x>
# must be a user-level skill on this machine
$madeLater = 'Assets/__GAME__/Game/Net', 'Assets/DefaultPrefabObjects.asset'   # the game's net code; FishNet writes it
$packMd = @($tracked | Where-Object { $_ -like 'packs/*/.claude/*.md' -or $_ -eq 'packs/coop-multiplayer/docs/design-corpus/README.md' })
$pathCount = 0
$pathBad = foreach ($f in $packMd) {
    $pack = ($f -split '/')[1]
    foreach ($l in [IO.File]::ReadAllLines((Resolve-Path -LiteralPath $f))) {
        if ($l -match 'Mixtrol') { continue }
        foreach ($m in [regex]::Matches($l, '`((?:docs|Assets|\.claude)/[^`\s*<>]+)`')) {
            $pathCount++
            $p = $m.Groups[1].Value.TrimEnd('/')
            if ($madeLater -notcontains $p -and -not (Test-Path -LiteralPath "packs/$pack/$p") -and -not (Test-Path -LiteralPath "project/$p")) { "$f -> $p" }
        }
        foreach ($m in [regex]::Matches($l, '~/\.claude/skills/([\w-]+)')) {
            $pathCount++
            if (-not (Test-Path -LiteralPath (Join-Path $env:USERPROFILE ".claude\skills\$($m.Groups[1].Value)"))) { "$f -> ~/.claude/skills/$($m.Groups[1].Value)" }
        }
    }
}
Check "$pathCount repo and ~/.claude/skills paths in $($packMd.Count) pack .claude files exist" (-not $pathBad) ($pathBad -join '; ')

# skills teach gk-bridge's verbs; a renamed verb would mislead agents silently
$usage = @([regex]::Matches([IO.File]::ReadAllText((Resolve-Path -LiteralPath 'plugin/bin/gk-bridge')), '(?m)^#   gk-bridge ([a-z-]+)') | ForEach-Object { $_.Groups[1].Value })
$verbBad = foreach ($f in @($tracked | Where-Object { $_ -like 'plugin/skills/*.md' -or $_ -like 'plugin/agents/*.md' })) {
    foreach ($m in [regex]::Matches([IO.File]::ReadAllText((Resolve-Path -LiteralPath $f)), '`gk-bridge +([a-z-]+)')) {
        if ($usage -notcontains $m.Groups[1].Value) { "$f -> $($m.Groups[1].Value)" }
    }
}
Check "backticked gk-bridge verbs in skills and agents are in its usage block ($($usage -join ', '))" ($usage.Count -gt 0 -and -not $verbBad) (@($verbBad | Sort-Object -Unique) -join '; ')

# a game's CI fails only on GitHub otherwise: YAML forbids tabs, GameCI needs the token for the private GameKit
# repo, the Unity credentials stay on the GameCI steps, butler is pinned
$ciText = [IO.File]::ReadAllText((Resolve-Path -LiteralPath 'packs/ci-github/.github/workflows/ci.yml'))
$ciBad = @(
    if ($ciText -match "`t") { 'a tab' }
    if (([regex]::Matches($ciText, 'gitPrivateToken: \$\{\{ secrets\.GAMEKIT_TOKEN \}\}')).Count -lt 2) { 'gitPrivateToken on fewer than 2 GameCI steps' }
    if ($ciText -match '(?ms)^env:\s*\r?\n(?:[ \t]+[^\r\n]*\r?\n)*?[ \t]+UNITY_PASSWORD') { 'workflow-level UNITY_PASSWORD' }
    if (@($ciText -split '\r?\n' | Where-Object { $_ -match 'broth\.itch\.zone/butler' -and $_ -notmatch '^\s*#' -and $_ -match 'LATEST' })) { 'butler URL uses LATEST' }
)
Check 'ci-github ci.yml: no tabs, GAMEKIT_TOKEN on both GameCI steps, credentials per step, butler pinned' (-not $ciBad) ($ciBad -join ', ')

# feature.js cannot be parsed here (no Node): check that its score formula matches the rubric it enforces
$fj = [IO.File]::ReadAllText((Resolve-Path -LiteralPath 'plugin/workflows/feature.js'))
$rb = [IO.File]::ReadAllText((Resolve-Path -LiteralPath 'plugin/skills/pipeline/references/review-rubric.md'))
$hi = 'y\u00FCksek'   # regex escape: the script stays ASCII
$fjOk = $fj -match "10 - 3 \* s\.findings\.filter\(f => f\.severity === '$hi'\)\.length -\s*s\.findings\.filter\(f => f\.severity === 'orta'\)\.length\)"
$rbOk = $rb -match "(?m)^\| \*\*\[$hi\]\*\*[^\r\n]*\| -3 each \|" -and $rb -match '(?m)^\| \*\*\[orta\]\*\*[^\r\n]*\| -1 each \|'
Check 'feature.js points() and review-rubric.md agree (high -3, medium -1)' ($fjOk -and $rbOk) "feature.js formula: $fjOk, rubric rows: $rbOk"

# gamekit:new-game edits and offers things the template provides by name
$ng = [IO.File]::ReadAllText((Resolve-Path -LiteralPath 'plugin/skills/new-game/SKILL.md'))
$packNames = @([regex]::Matches(($ng -split '## 4\.')[0], '`([a-z0-9]+(?:-[a-z0-9]+)+|steam|linear)`') | ForEach-Object { $_.Groups[1].Value } | Sort-Object -Unique)
$noPack = @($packNames | Where-Object { -not (Test-Path -LiteralPath "packs/$_" -PathType Container) })
Check "new-game skill: $($packNames.Count) pack names exist under packs/" ($packNames.Count -gt 0 -and -not $noPack) ($noPack -join ', ')
Check "new-game skill: project/DESIGN.md has the '## Rules (as built)' anchor, project/REHBER.md exists" (
    ([IO.File]::ReadAllText((Resolve-Path -LiteralPath 'project/DESIGN.md')) -match '(?m)^## Rules \(as built\)') -and (Test-Path -LiteralPath 'project/REHBER.md'))

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
# CL IDs are append-only and cited from the skill, clarity-reviewer and the reference-docs playbook
$clDefs = @([regex]::Matches($crText, '(?m)^(?:\*\*|\| )(CL\d\d)') | ForEach-Object { $_.Groups[1].Value })
$clDup = @($clDefs | Group-Object | Where-Object Count -gt 1 | ForEach-Object Name)
$clFiles = @($tracked | Where-Object { ($_ -like 'plugin/skills/player-clarity/*.md') -or $_ -eq 'plugin/agents/clarity-reviewer.md' -or $_ -eq 'packs/reference-docs/clarity-playbook.md' })
$clCited = @($clFiles | ForEach-Object { [regex]::Matches([IO.File]::ReadAllText((Resolve-Path -LiteralPath $_)), 'CL\d\d') | ForEach-Object Value } | Sort-Object -Unique)
$clMissing = @($clCited | Where-Object { $clDefs -notcontains $_ })
Check "clarity-rules: $($clDefs.Count) CL IDs unique, the $($clCited.Count) cited ones defined" ($clDefs.Count -gt 0 -and -not $clDup -and -not $clMissing) ((@($clDup | ForEach-Object { "dup $_" }) + $clMissing) -join ', ')
$ccgsFiles = @(git grep -l 'CCGS' -- plugin)
$noLicence = @($ccgsFiles | Where-Object { $_ -notlike 'plugin/skills/genre-defaults/*' -and -not (Select-String -LiteralPath $_ -Pattern 'genre-defaults/LICENSE\.md' -Quiet) })
Check "$($ccgsFiles.Count) files citing CCGS sit under genre-defaults or point to its LICENSE.md" (-not $noLicence) ($noLicence -join ', ')

Section 'Blender export calls'
# unity-export's contract: FBX_SCALE_ALL, no baked space transform. city_assets.py is marked PRE-CONTRACT in its
# header and kept for its modelling helpers
$fbxBad = foreach ($f in @($tracked -like '*.py' | Where-Object { $_ -ne 'packs/toon-art/examples/city_assets.py' })) {
    $t = [IO.File]::ReadAllText((Resolve-Path -LiteralPath $f))
    foreach ($m in [regex]::Matches($t, '(?s)export_scene\.fbx\((.*?)\)\s*(?:\r?\n|$)')) {
        if ($m.Groups[1].Value -notmatch "apply_scale_options\s*=\s*'FBX_SCALE_ALL'" -or $m.Groups[1].Value -notmatch 'bake_space_transform\s*=\s*False') { $f }
    }
}
Check "tracked export_scene.fbx calls use FBX_SCALE_ALL and bake_space_transform=False" (-not $fbxBad) (@($fbxBad | Sort-Object -Unique) -join ', ')

Section 'This machine: headless Blender and the user-level skills (a FAIL here is machine state, not the repo)'
# README "Global Claude katmani": the user-level layer the plugin and the Blender work lean on
foreach ($piece in 'skills\grill-me', 'skills\orchestrate', 'skills\unity-export', 'skills\blender-director', 'skills\blender-image-to-3d', 'rules\unity-games.md', 'hooks\enhance-prompt.ps1') {
    if (-not (Test-Path -LiteralPath (Join-Path $env:USERPROFILE ".claude\$piece"))) { Write-Host "  skip  ~/.claude/$($piece -replace '\\', '/') missing (README, Global Claude katmani)" -ForegroundColor Yellow }
}
$blender = (Get-Command blender -ErrorAction SilentlyContinue).Source
if (-not $blender) {
    # newest install by version ("Blender 5.10" above "Blender 5.2"), one folder deep, no recursive scan
    $blender = Get-ChildItem "$env:ProgramFiles\Blender Foundation\*\blender.exe" -ErrorAction SilentlyContinue |
        Sort-Object { $v = $null; if ([version]::TryParse(($_.Directory.Name -replace '[^\d.]', ''), [ref]$v)) { $v } else { [version]'0.0' } } -Descending |
        Select-Object -First 1 -ExpandProperty FullName
}
$skillDir = Join-Path $env:USERPROFILE '.claude\skills'
$contractFile = Join-Path $skillDir 'unity-export\SKILL.md'
# the export call is taken from unity-export's code block, the one contract, so the probe cannot drift from it
$contract = if (Test-Path -LiteralPath $contractFile) {
    [regex]::Match([IO.File]::ReadAllText($contractFile), '(?s)## Blender side[^\n]*\n.*?```python\r?\n(.*?)```').Groups[1].Value
}
if ($blender -and -not $contract) {
    Check 'unity-export SKILL.md has the export_scene.fbx code block under "## Blender side"' $false $contractFile
} elseif ($blender) {
    # Compiles every Python file Blender runs (the repo's packs and the user-level Blender skills) and exports a cube
    # with unity-export's FBX call verbatim. The toon-art examples are excerpts (kit_common needs a game's
    # kit_palette), so they are compiled, never imported.
    $py = @($tracked -like '*.py' | ForEach-Object { (Resolve-Path -LiteralPath $_).Path })
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
path = r'$fbx'
$contract
if not os.path.exists(path) or not os.path.getsize(path): bad.append('fbx export empty')
print('GKRESULT %d %s' % (len(bad), ' | '.join(bad)))
sys.exit(1 if bad else 0)
"@, (New-Object Text.UTF8Encoding $false))
    $res = cmd /c "`"$blender`" --background --factory-startup --python-exit-code 1 --python `"$probe`" 2>&1"
    $line = ($res | Where-Object { $_ -like 'GKRESULT*' } | Select-Object -Last 1)
    Check "$(Split-Path (Split-Path $blender) -Leaf): $($py.Count) .py compile, headless FBX export with the unity-export call" ($LASTEXITCODE -eq 0 -and $line -like 'GKRESULT 0*') "$line $(($res | Select-Object -Last 2) -join ' ')"
    Remove-Item -LiteralPath $probe, $fbx -ErrorAction SilentlyContinue
    # bake_maps.py --pack-mask: the URP mask channels (R metallic, G AO, A 1-roughness), about 3 s, no bake or GPU
    $packMask = Join-Path $skillDir 'blender-image-to-3d\evals\test_pack_mask.py'
    if (Test-Path -LiteralPath $packMask) {
        $maskOut = Join-Path $env:TEMP 'gk-test-pack-mask'
        $res = cmd /c "`"$blender`" --background --factory-startup --python-exit-code 1 --python `"$packMask`" -- --out `"$maskOut`" 2>&1"
        Check 'blender-image-to-3d: bake_maps pack_mask channels (test_pack_mask.py)' ($LASTEXITCODE -eq 0 -and ($res -match 'PACK MASK PASS')) (($res | Select-Object -Last 3) -join ' ')
        if (Test-Path -LiteralPath $maskOut) { Remove-Item -LiteralPath $maskOut -Recurse -Force -ErrorAction SilentlyContinue }
    }
} else { Write-Host '  skip  no Blender installed' }
# every profile: after a reinstall or account switch a stale patched copy can sit next to the active unpatched one
$cli = @(Get-ChildItem "$env:LOCALAPPDATA\Claude-Data\*\Claude Extensions\ant.dir.gh.blender.blender-mcp\blmcp\tools_helpers\blender_cli.py" -ErrorAction SilentlyContinue)
if ($cli) {
    # local patch, lost on extension updates; without it every *_for_cli MCP call times out. The fix (recipe:
    # README.md, Blender step 5): add stdin=subprocess.DEVNULL to the subprocess.run(...) call in each file listed
    $unpatched = @($cli | Where-Object { -not (Select-String -LiteralPath $_.FullName -Pattern 'stdin=subprocess\.DEVNULL' -Quiet) } | ForEach-Object FullName)
    Check "Blender MCP extension: $($cli.Count) copy(ies) keep the stdin=DEVNULL patch" (-not $unpatched) ("add stdin=subprocess.DEVNULL to subprocess.run in run_blender_cli (README.md, Blender step 5): " + ($unpatched -join ', '))
} else { Write-Host '  skip  Blender MCP extension not installed' }
# unity-editor-cli's CLI claims were checked on the version its SKILL.md stamps; a newer CLI may have moved them.
# A warning, not a failure: re-check the claims, then move the stamp
if (Get-Command unity -ErrorAction SilentlyContinue) {
    function CliKey([string]$v) {
        # 1.0.0-beta.14 sorts below 1.0.0: release stage 0 for a pre-release, 1 for a release
        if ($v -match '(\d+)\.(\d+)\.(\d+)(?:-[a-z]+\.(\d+))?') { '{0:D4}{1:D4}{2:D4}{3}{4:D4}' -f [int]$Matches[1], [int]$Matches[2], [int]$Matches[3], [int](-not $Matches[4]), [int]$Matches[4] }
    }
    $cliVer = (cmd /c "unity --version 2>nul" | Select-Object -First 1)
    $stamp = [regex]::Match([IO.File]::ReadAllText((Resolve-Path -LiteralPath 'plugin/skills/unity-editor-cli/SKILL.md')), 'checked on \*\*CLI ([\w.-]+)\*\*').Groups[1].Value
    $logged = [regex]::Match([IO.File]::ReadAllText((Resolve-Path -LiteralPath 'plugin/skills/unity-cli/CHANGELOG.md')), '(?m)^## CLI `([\w.-]+)`').Groups[1].Value
    foreach ($ref in @(@('unity-editor-cli stamp', $stamp), @('unity-cli CHANGELOG', $logged))) {
        if ($cliVer -and $ref[1] -and (CliKey $cliVer) -gt (CliKey $ref[1])) { Write-Host "  warn  unity CLI $cliVer is newer than the $($ref[0]) ($($ref[1])): re-check its claims" -ForegroundColor Yellow }
    }
}

Section 'GameKit package'
$pkg = 'packages/com.yunusburkut.gamekit'
$assets = @($tracked -like "$pkg/*" | Where-Object { $_ -notlike '*.meta' })
$dirs = $assets | ForEach-Object { $d = Split-Path $_ -Parent; while ($d -and $d -ne ($pkg -replace '/', '\')) { $d; $d = Split-Path $d -Parent } } | Sort-Object -Unique
$metaBad = foreach ($p in @($assets) + @($dirs)) { if ($tracked -notcontains (($p -replace '\\', '/') + '.meta')) { $p } }
Check "$($assets.Count) files and $(@($dirs).Count) folders have a committed .meta" (-not $metaBad) ($metaBad -join ', ')

Section 'Template placeholders and pack merge (new-game.ps1 -NoSetup -NoGit, every pack, no Unity)'
Check 'project/ carries __GAME__' ([bool](git grep -l '__GAME__' -- project | Select-Object -First 1))
$mergeRoot = Join-Path $env:TEMP 'gk-test-all-packs'
if (Test-Path -LiteralPath $mergeRoot) { cmd /c rmdir /s /q "\\?\$mergeRoot" }
$allPacks = @(Get-ChildItem -LiteralPath packs -Directory | Where-Object Name -ne 'reference-docs' | ForEach-Object Name)
$mergeGame = Join-Path $mergeRoot 'PackMerge'
try {
    # all packs at once: not a game anyone makes, but every packages.json merge and every placeholder runs
    & (Join-Path $PSScriptRoot 'new-game.ps1') -Name PackMerge -Path $mergeRoot -Packs $allPacks -NoSetup -NoGit -FeelFrom $mergeRoot 3>$null 6>$null | Out-Null
    $manifestText = [IO.File]::ReadAllText((Join-Path $mergeGame 'Packages\manifest.json'))
    $manifest = $manifestText | ConvertFrom-Json
    $missing = foreach ($pack in $allPacks) {
        $spec = Join-Path "packs\$pack" 'packages.json'
        if (-not (Test-Path -LiteralPath $spec)) { continue }
        $spec = Get-Content -LiteralPath $spec -Raw | ConvertFrom-Json
        foreach ($dep in $spec.dependencies.PSObject.Properties) {
            if ($manifest.dependencies.($dep.Name) -ne $dep.Value) { "$pack dependency $($dep.Name)" }
        }
        foreach ($reg in $spec.scopedRegistries) {
            $got = @($manifest.scopedRegistries | Where-Object url -eq $reg.url)
            foreach ($scope in $reg.scopes) { if (-not $got -or $got[0].scopes -notcontains $scope) { "$pack registry $($reg.url) scope $scope" } }
        }
    }
    Check "merged manifest.json parses and holds every pack's dependencies and registries" (-not $missing) ($missing -join ', ')
    $left = @(Get-ChildItem -LiteralPath $mergeGame -Recurse -File -Force |
        Where-Object { $_.Name -match '__GAME__|__COMPANY__' -or ($_.Length -lt 2MB -and [IO.File]::ReadAllText($_.FullName) -match '__GAME__|__COMPANY__') } |
        ForEach-Object { $_.FullName.Substring($mergeGame.Length + 1) })
    Check 'no __GAME__ / __COMPANY__ left in names or contents (new-game.ps1 text extensions cover every placeholder file)' (-not $left) ($left -join ', ')
} catch {
    Check 'new-game.ps1 -NoSetup -NoGit with every pack' $false $_.Exception.Message
} finally {
    if (Test-Path -LiteralPath $mergeRoot) { cmd /c rmdir /s /q "\\?\$mergeRoot" }
}

Section 'Plugin hooks (plugin\test-hooks.ps1)'
$out = & powershell -NoProfile -ExecutionPolicy Bypass -File plugin\test-hooks.ps1
$code = $LASTEXITCODE
$out | Where-Object { $_ -like 'FAIL*' } | ForEach-Object { Write-Host "        $_" -ForegroundColor Red }
Check "test-hooks: $(@($out -like 'PASS*').Count) pass, $(@($out -like 'FAIL*').Count) fail" ($code -eq 0)

Section 'sync-template pipeline (test-sync.sh: throwaway template and game, no Unity, no network)'
if ($bash) {
    $out = cmd /c "`"$bash`" plugin/skills/sync-template/scripts/test-sync.sh 2>&1"
    Check 'sync.sh: all checks passed' ($LASTEXITCODE -eq 0 -and ($out -match 'sync\.sh: all checks passed')) (($out | Select-Object -Last 3) -join ' | ')
} else { Write-Host '  skip  no bash (Git for Windows)' }

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
