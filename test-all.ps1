<#
.SYNOPSIS
    One entry point for every check of the template. Fast static checks over the whole repo, then the plugin's hook
    tests and validator; -Full adds test-template.ps1 (about 5 min, launches Unity).

.DESCRIPTION
    Static: every tracked JSON parses; every .ps1 parses and is ASCII or has a BOM (PowerShell 5.1 reads a BOM-less
    script as ANSI); every bash script passes bash -n; each skill and agent in plugin/ and packs/*/.claude/ has
    name/description frontmatter (name = folder or file name; the 250-char description budget and the
    ${CLAUDE_PLUGIN_ROOT}/ paths of plugin/ files are test-hooks.ps1's, this script checks the packs' ones); output
    styles have name/description; every references/ and scripts/ path a skill names exists; the docs/, Assets/, .claude/
    and ~/.claude/skills/ paths in packs' .claude files exist; every backticked gk-bridge verb in skills, agents and
    project/CLAUDE.md, DESIGN.md, REHBER.md is in its usage block, and every skill those project docs name exists;
    packs/ci-github ci.yml has no tabs, GAMEKIT_TOKEN on both GameCI steps, no workflow-level Unity credentials and a
    pinned butler, and its commented steam: job ships the uploaded Windows build from BuildMenu's Builds/Windows; the
    command words project/CLAUDE.md and REHBER.md teach are routed by route.ps1; feature.js scores findings with the
    rubric's weights; the names, README paragraphs and new-game.ps1 lines new-game's skill relies on exist, and both
    clear GITHUB_TOKEN/GH_TOKEN for gh repo create; launch-review's build menus, build.log tokens and butler channel
    match BuildMenu.cs and ci.yml; platform-targets' Player Settings and build values are in ProjectSetup.cs and
    BuildMenu.cs, and AgentBridge compiles gk-bridge's platforms; reference-docs' README table lists every file and its
    cited plugin/ paths exist; project/.claude/settings.json keeps each git/gh/butler/steamcmd/unity ask and deny
    rule in both Bash() and PowerShell() form; the Pipeline version the template pins (when a local game caches it) has
    the flags unity-package-management names; vendored skills keep their house edits (HOUSE markers paired, unity-cli's block); the
    template pins an existing GameKit tag (a version not yet released is a warning); the CCGS-derived content keeps its
    source keys and licence pointer, the clarity CL IDs are unique and every CL ID and section cited anywhere in
    plugin/ or the project docs is defined; every tracked export_scene.fbx call follows unity-export (FBX_SCALE_ALL,
    bake_space_transform=False; city_assets.py is pre-contract); every GameKit file and folder has a committed .meta.
    This machine (state no repo commit fixes): every user-level piece (README "Global Claude katmani") is present;
    Blender is the one BLENDER_PATH names, else PATH's, else the newest install (as the hook and the *_for_cli tools
    pick it), with a warning when its version has no MCP add-on; every tracked .py and every ~/.claude/skills/blender-*,
    unity-export .py compiles in it, a cube exports headless with unity-export's FBX call verbatim, toon-art's
    toon_prop.py exports a prop and a manifest whose collider signs hold for an off-centre copy too,
    blender-image-to-3d's test_pack_mask.py passes, and its validate, export_delivery and roundtrip --manifest exit 0
    on the local _asset-samples\PR_Anvil or, without it, a fixture with a packed mask built headless; every --background
    line in those user-level skills carries --factory-startup; the Blender MCP
    extension's copies keep their stdin=DEVNULL patch (README.md, Blender step 5) and the active copy's run_blender_cli
    answers with stdin held open; grill-me's card fields and unity-games.md's gk-bridge exit codes match the plugin; a
    unity CLI newer than unity-editor-cli's stamp or unity-cli's CHANGELOG is a warning. Each is skipped when its tool
    is not installed.
    sync-template: plugin/skills/sync-template/scripts/test-sync.sh (a few seconds, no Unity, no network).
    Pack merge: no pack file shares a path with project/ or another pack; new-game.ps1 -NoSetup with every pack and its
    git step into %TEMP% (copy only, no Unity; a probe file with a space in its name makes the template dirty), then the
    merged manifest holds every pack's dependencies and registries, CLAUDE.md every pack's README block and section,
    Game.asmdef every pack assembly and packages.json gameReferences, no __GAME__/__COMPANY__ is left, and the start
    commit carries the -dirty marker, the Packs line and the dirty note, with core.hooksPath and an executable
    pre-commit hook. Twins: reference-docs pointers, visual-clarity and visual-explainer headings and size caps, the
    marketplace and plugin.json descriptions, grill-me's round rules in new-game, the two lean-code copies, the
    headings the agents cite, launch-review's quoted log lines, APIs and secrets, ui-ugui's and unity-cli's house
    edits. Warning: no GITHUB_TOKEN/GH_TOKEN for background plugin updates.
    Then plugin\test-hooks.ps1 and `claude plugin validate plugin` (its missing-version warning is intended).
    About 60-130 s with Blender installed, longer on a busy machine (288 s seen): an agent runs it with
    run_in_background. -Full adds test-template.ps1 (5-10 min, Unity): run it in the background.
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
    # Latin-1 maps each byte to one char, so one regex scans the file (a pipeline over every byte took seconds)
    if (-not $bom -and [Text.Encoding]::GetEncoding(28591).GetString($b) -cmatch '[^\x00-\x7F]') { $f }
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
    # values trimmed of YAML quotes, as test-hooks.ps1 measures them
    if ($m.Success) { foreach ($l in $m.Groups[1].Value -split '\r?\n') { if ($l -match '^(\w+):\s*(.*)$') { $h[$Matches[1]] = $Matches[2].Trim().Trim('"', "'") } } }
    return $h
}
# plugin skills and agents, plus the ones packs copy into a game's .claude\. The description budget and the
# ${CLAUDE_PLUGIN_ROOT}/ paths of plugin/ files are test-hooks.ps1's (it runs alone after a plugin change); this
# script checks them for the packs' files and checks name = folder or file for all.
$skills = @($tracked | Where-Object { $_ -like 'plugin/skills/*/SKILL.md' -or $_ -like 'packs/*/.claude/skills/*/SKILL.md' })
# 250: the skill listing has a character budget and drops long descriptions (the spec limit is 1024)
$fmBad = foreach ($f in $skills) {
    $h = Front $f; $dir = Split-Path (Split-Path $f) -Leaf
    if ($h.name -ne $dir -or -not $h.description -or ($f -like 'packs/*' -and $h.description.Length -gt 250)) { "$f ($($h.description.Length))" }
}
Check "$($skills.Count) skills: name = folder, description set (packs: at most 250 chars; plugin: test-hooks)" (-not $fmBad) ($fmBad -join ', ')
# The total of the gamekit skill descriptions against the session's shared skill-listing budget has one number, in
# plugin/test-hooks.ps1 (a failing check, with the evidence behind the number); this script runs it below.
$agents = @($tracked | Where-Object { $_ -like 'plugin/agents/*.md' -or $_ -like 'packs/*/.claude/agents/*.md' })
$agBad = foreach ($f in $agents) {
    $h = Front $f
    if ($h.name -ne [IO.Path]::GetFileNameWithoutExtension($f) -or -not $h.description -or ($f -like 'packs/*' -and $h.description.Length -gt 250)) { "$f ($($h.description.Length))" }
}
Check "$($agents.Count) agents: name = file, description set (packs: at most 250 chars; plugin: test-hooks)" (-not $agBad) ($agBad -join ', ')
$styles = @($tracked -like 'plugin/output-styles/*.md')
$stBad = foreach ($f in $styles) { $h = Front $f; if (-not $h.name -or -not $h.description) { $f } }
Check "$($styles.Count) output styles have name and description" (-not $stBad) ($stBad -join ', ')
# relative references/ and scripts/ paths resolve against the skill's folder; ${CLAUDE_PLUGIN_ROOT}/ paths in a pack's
# files resolve against plugin/ (plugin/ files: test-hooks.ps1)
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
    if ($f -like 'plugin/*') { continue }
    foreach ($m in [regex]::Matches($text, '\$\{CLAUDE_PLUGIN_ROOT\}/([\w./-]*[\w-])')) {
        $refCount++
        if (-not (Test-Path -LiteralPath (Join-Path 'plugin' $m.Groups[1].Value))) { "$f -> `${CLAUDE_PLUGIN_ROOT}/$($m.Groups[1].Value)" }
    }
}
Check "$refCount references/, scripts/ (skills) and packs' `${CLAUDE_PLUGIN_ROOT}/ paths exist" (-not $refBad) ($refBad -join '; ')

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

# skills, agents and every new game's CLAUDE.md, DESIGN.md and REHBER.md teach gk-bridge's verbs; a renamed verb
# would mislead agents silently
$projectDocs = 'project/CLAUDE.md', 'project/DESIGN.md', 'project/REHBER.md'
$usage = @([regex]::Matches([IO.File]::ReadAllText((Resolve-Path -LiteralPath 'plugin/bin/gk-bridge')), '(?m)^#   gk-bridge ([a-z-]+)') | ForEach-Object { $_.Groups[1].Value })
$verbBad = foreach ($f in @($tracked | Where-Object { $_ -like 'plugin/skills/*.md' -or $_ -like 'plugin/agents/*.md' }) + $projectDocs) {
    foreach ($m in [regex]::Matches([IO.File]::ReadAllText((Resolve-Path -LiteralPath $f)), '`gk-bridge +([a-z-]+)')) {
        if ($usage -notcontains $m.Groups[1].Value) { "$f -> $($m.Groups[1].Value)" }
    }
}
Check "backticked gk-bridge verbs in skills, agents and the project docs are in its usage block ($($usage -join ', '))" ($usage.Count -gt 0 -and -not $verbBad) (@($verbBad | Sort-Object -Unique) -join '; ')
# a skill the project docs name (`gamekit:<x>`, or a backticked hyphenated name) must be something a game can reach:
# a plugin skill, agent, workflow, hook or bin/ tool, a pack, a pack's skill, a gk-bridge verb, or a user-level or spare
# Blender skill on this machine
$reachable = @(Get-ChildItem -LiteralPath plugin/skills, packs -Directory | ForEach-Object Name) +
    @(Get-ChildItem -Path plugin/agents/*.md, plugin/workflows/*.js, plugin/hooks/*.ps1, plugin/bin/* | ForEach-Object BaseName) +
    @(Get-ChildItem -Path 'packs\*\.claude\skills' -Directory -ErrorAction SilentlyContinue | ForEach-Object Name) +
    @(Get-ChildItem -Path (Join-Path $env:USERPROFILE '.claude\skills'), (Join-Path $env:USERPROFILE '.claude\spares\blender-skills') -Directory -ErrorAction SilentlyContinue | ForEach-Object Name) + $usage
$nameBad = foreach ($f in $projectDocs) {
    foreach ($m in [regex]::Matches([IO.File]::ReadAllText((Resolve-Path -LiteralPath $f)), 'gamekit:([a-z][a-z0-9-]*)|`([a-z][a-z0-9]*(?:-[a-z0-9]+)+)`')) {
        $n = if ($m.Groups[1].Success) { $m.Groups[1].Value } else { $m.Groups[2].Value }
        if ($reachable -notcontains $n) { "$f -> $n" }
    }
}
Check 'project docs: every gamekit:<x> and backticked skill name exists (plugin, packs, hooks, gk-bridge, ~/.claude)' (-not $nameBad) (@($nameBad | Sort-Object -Unique) -join '; ')
# the command words a game's CLAUDE.md (Working agreement) and REHBER.md teach are the ones route.ps1 routes: a renamed
# command would leave both docs teaching the old word
$routeRx = @([regex]::Matches([IO.File]::ReadAllText((Resolve-Path -LiteralPath 'plugin/hooks/route.ps1')), 'if \(\$p -match (?:''([^'']*)''|"([^"]*)")\) \{ Write-Output') | ForEach-Object { $_.Groups[1].Value + $_.Groups[2].Value })
$cmdBad = @(
    foreach ($w in 'devam', 'kabul', [regex]::Unescape('kart\u0131 Next''e ta\u015F\u0131'), 'review et', 'puanla') {
        foreach ($f in 'project/CLAUDE.md', 'project/REHBER.md') { if (-not [IO.File]::ReadAllText((Resolve-Path -LiteralPath $f)).Contains("``$w``")) { "$f no longer teaches ``$w``" } }
        if (-not @($routeRx | Where-Object { $w -match $_ })) { "no route.ps1 command regex matches '$w'" }
    }
)
Check "command words: devam, kabul, kart. Next'e tas., review et, puanla are taught in project CLAUDE.md and REHBER.md and routed by route.ps1 ($($routeRx.Count) regexes)" ($routeRx.Count -gt 0 -and -not $cmdBad) ($cmdBad -join '; ')

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
# the commented-out steam: job (packs/steam README) downloads the Windows build artifact and ships BuildMenu's folder
$ciLines = $ciText -split '\r?\n'
$steamAt = [array]::IndexOf($ciLines, '  # steam:')
$steamBad = @(
    if ($steamAt -lt 0) { "no '  # steam:' block" } else {
        $steam = ($ciLines[$steamAt..($ciLines.Count - 1)] | ForEach-Object { $_ -replace '^  # ?', '' }) -join "`n"
        $art = [regex]::Match($steam, 'name: Build-(\w+)').Groups[1].Value
        if (-not $art -or $ciText -notmatch "(?m)^\s+- targetPlatform: $art\s*$" -or $ciText -notmatch '(?m)^\s+name: Build-\$\{\{ matrix\.targetPlatform \}\}') { "downloads Build-$art, which no uncommented build matrix entry uploads" }
        if (-not [IO.File]::ReadAllText((Resolve-Path -LiteralPath 'packages/com.yunusburkut.gamekit/Editor/BuildMenu.cs')).Contains('return "Builds/Windows/"')) { 'BuildMenu.cs no longer writes Builds/Windows/' }
        elseif ($steam -notmatch 'artifact/Builds/Windows/' -or $steam -notmatch 'rootPath: artifact/Builds\b' -or $steam -notmatch 'depot1Path: Windows\b') { 'paths are not artifact/Builds + Windows, the folder BuildMenu.cs writes' }
    }
)
Check 'ci-github ci.yml: the commented steam: job downloads an uploaded Windows build and ships BuildMenu''s Builds/Windows' (-not $steamBad) ($steamBad -join '; ')

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
# step 2 offers each pack with the first paragraph under its README title (an awk that skips # lines), step 4 sorts
# new-game.ps1's WARNING lines and drops its closing "Open it in Unity Hub" line, REHBER.md names the shaping command
$ngScript = [IO.File]::ReadAllText((Resolve-Path -LiteralPath 'new-game.ps1'))
$ngBad = @(
    foreach ($p in @(Get-ChildItem -LiteralPath packs -Directory | Where-Object Name -ne 'reference-docs' | ForEach-Object Name)) {
        $first = @([IO.File]::ReadAllLines((Resolve-Path -LiteralPath "packs/$p/README.md")) | Select-Object -Skip 1 | Where-Object { $_.Trim() -and $_ -notmatch '^#' } | Select-Object -First 1)
        if (-not $first -or $first[0] -match '^\s*(```|\||- |\* |>)') { "packs/$p/README.md first paragraph is not prose" }
    }
    foreach ($w in "Write-Warning 'No local Feel found", 'Write-Warning "UnityYAMLMerge not found', 'Write-Warning "Add scope', "Write-Host '    Open it in Unity Hub") {
        if (-not $ngScript.Contains($w)) { "new-game.ps1 lacks: $w" }
    }
    if ($ng -notmatch 'closing "open it') { 'new-game SKILL.md step 4 no longer names the closing "open it" line' }
    # gh prefers GH_TOKEN/GITHUB_TOKEN over its login, and the plugin-update token is read-only (README, token conflict)
    if ($ngScript -notmatch '\$env:GITHUB_TOKEN = \$null; \$env:GH_TOKEN = \$null\s*\r?\n\s*gh repo create') { 'new-game.ps1 no longer clears GITHUB_TOKEN/GH_TOKEN right before gh repo create' }
    foreach ($l in @($ng -split '\r?\n' | Where-Object { $_ -match '^\s*(env\b.*\s)?gh repo create' })) { if ($l -notmatch 'env -u GITHUB_TOKEN -u GH_TOKEN gh repo create') { "new-game SKILL.md runs gh repo create with the token set: $($l.Trim())" } }
    if ([IO.File]::ReadAllText((Resolve-Path -LiteralPath 'project/REHBER.md')) -notmatch 'gamekit:new-game \u015Fekillendir') { 'project/REHBER.md lacks /gamekit:new-game sekillendir' }
    # step 6 holds a copy of grill-me's round rules: the twin lines must stay in both (the user-level file may be absent)
    $grill = Join-Path $env:USERPROFILE '.claude\skills\grill-me\SKILL.md'
    if (Test-Path -LiteralPath $grill) {
        $grillText = [IO.File]::ReadAllText($grill)
        foreach ($t in @(@('a frontier larger than one round is no reason to drop a question', 'frontier larger than one round is no reason to drop a question'), @('(Onerilen)', '\(\u00D6nerilen\)'),
                @('it takes at most 4', 'it takes at most 4, so such a round asks the top 4 and its fifth question opens the next round'))) {
            if (($ng -replace '\s+', ' ') -notmatch $t[1]) { "new-game SKILL.md lost grill-me's '$($t[0])'" }
            if (($grillText -replace '\s+', ' ') -notmatch $t[1]) { "~/.claude/skills/grill-me SKILL.md lost '$($t[0])'" }
        }
    }
)
Check 'new-game skill: pack READMEs open with prose, new-game.ps1 keeps the WARNING and closing lines step 4 handles, both clear the gh tokens for repo create, REHBER.md names the shaping command, grill-me''s round rules match' (-not $ngBad) ($ngBad -join '; ')

# launch-review restates GameKit's build menu and build.log, ci-github's butler channel; the reference-docs copy of
# shipping-2026.md points at the plugin's (packs/reference-docs/README.md)
$bm = [IO.File]::ReadAllText((Resolve-Path -LiteralPath 'packages/com.yunusburkut.gamekit/Editor/BuildMenu.cs'))
$menus = @([regex]::Matches($bm, '\[MenuItem\("GameKit/Build/([^"]+)"\)\]') | ForEach-Object { $_.Groups[1].Value })
$lrFiles = @($tracked -like 'plugin/skills/launch-review/*.md') + 'packs/reference-docs/shipping-2026.md'
$lrText = ($lrFiles | ForEach-Object { [IO.File]::ReadAllText((Resolve-Path -LiteralPath $_)) }) -join "`n"
$lrBad = @(
    foreach ($f in $lrFiles) {
        foreach ($m in [regex]::Matches([IO.File]::ReadAllText((Resolve-Path -LiteralPath $f)), '(?:\*\*|`)([^*`\r\n]+?) > Build > ([^*`\r\n]+?)(?:\*\*|`)')) {
            if ($m.Groups[1].Value -ne 'GameKit' -or $menus -notcontains $m.Groups[2].Value.Trim()) { "$f -> $($m.Groups[1].Value) > Build > $($m.Groups[2].Value)" }
        }
    }
    # build.log tokens: as the skill quotes them, as BuildMenu.cs writes them
    foreach ($t in @(@('`development no`', 'Append("development ")'), @('`WARNING debug-signed`', '"WARNING debug-signed:'), @('`versionCode`', 'Append("versionCode ")'),
            @('`16 KB` warning line', 'IndexOf("16 KB"'), @('`size` line', 'Append("size ")'))) {
        if (-not $lrText.Contains($t[0])) { "launch-review no longer quotes $($t[0])" } elseif (-not $bm.Contains($t[1])) { "BuildMenu.cs no longer writes $($t[0])" }
    }
    # the APIs and controls it names in other packs and GameKit: as quoted, as the source declares them
    foreach ($t in @(@('StoreReview.Prepare(host)', 'packs/mobile-store/Assets/__GAME__/Game/Store/StoreReview.cs', 'public static void Prepare(MonoBehaviour host)'),
            @('StoreReview.Request(host)', 'packs/mobile-store/Assets/__GAME__/Game/Store/StoreReview.cs', 'public static void Request(MonoBehaviour host)'),
            @('FrameLog on F3 or a three-finger tap', 'packages/com.yunusburkut.gamekit/Runtime/FrameLog.cs', 'F3 or a three-finger tap'),
            @('`SteamBootstrap.AppId`', 'packs/steam/Assets/__GAME__/Game/Steam/SteamBootstrap.cs', 'const uint AppId = '))) {
        if (-not ($lrText -replace '\s+', ' ').Contains($t[0])) { "launch-review no longer quotes $($t[0])" }
        elseif (-not [IO.File]::ReadAllText((Resolve-Path -LiteralPath $t[1])).Contains($t[2])) { "$($t[1]) no longer has $($t[2]) (launch-review quotes $($t[0]))" }
    }
    # every `NAME` secret it says a pack's workflow needs is one ci.yml reads
    foreach ($m in [regex]::Matches($lrText, '`([A-Z][A-Z0-9_]+)` secret')) {
        if ($ciText -notmatch ('secrets\.' + $m.Groups[1].Value + '\b')) { "launch-review names the $($m.Groups[1].Value) secret, ci.yml never reads it" }
    }
    $channels = [regex]::Match([IO.File]::ReadAllText((Resolve-Path -LiteralPath 'plugin/skills/launch-review/references/release-build.md')), 'One butler\s+channel per platform \(([^)]*)\)').Groups[1].Value
    foreach ($m in [regex]::Matches($ciText, 'butler push \S+ "?\$\w+:([a-z0-9-]+)')) {
        if ($channels -notmatch ('`' + $m.Groups[1].Value + '`')) { "ci.yml pushes channel $($m.Groups[1].Value), release-build.md lists ($channels)" }
    }
)
Check "launch-review: $(@($menus).Count) GameKit > Build menus, build.log lines, StoreReview/FrameLog/SteamBootstrap names, secrets and the butler channel match their sources" (@($menus).Count -and -not $lrBad) ($lrBad -join '; ')
# platform-targets restates what ProjectSetup and BuildMenu write (each as the skill words it, as the code has it), and
# AgentBridge's compile platforms are the ones gk-bridge accepts
$ptText = (@(Get-ChildItem -LiteralPath plugin/skills/platform-targets -Recurse -Filter *.md | ForEach-Object { [IO.File]::ReadAllText($_.FullName) }) -join "`n") -replace '\s+', ' '
$gkEditor = 'packages/com.yunusburkut.gamekit/Editor'
$psbm = [IO.File]::ReadAllText((Resolve-Path -LiteralPath "$gkEditor/ProjectSetup.cs")) + $bm
$ptBad = @(
    foreach ($t in @(@('targets API 36', 'AndroidSdkVersions.AndroidApiLevel36'), @('540x960 portrait', 'portrait ? 540 : 1280'), @('1280x720 landscape', 'portrait ? 960 : 720'),
            @('`PlayerSettings.fullScreenMode = FullScreenMode.Windowed`', 'fullScreenMode = FullScreenMode.Windowed'), @('Brotli with `decompressionFallback` off', 'WebGLCompressionFormat.Brotli'),
            @('Brotli with `decompressionFallback` off', 'decompressionFallback = false'), @('Responsive template', '"PROJECT:Responsive"'), @('high managed stripping', 'ManagedStrippingLevel.High'),
            @('URP post-processing variant stripping', 'stripUnusedPostProcessingVariants = true'), @('disk-size LTO', '"DiskSizeLTO"'), @('uncompressed with the fastest', 'development ? "BuildTimes"'))) {
        if (-not $ptText.Contains($t[0])) { "platform-targets no longer says '$($t[0])'" } elseif (-not $psbm.Contains($t[1])) { "ProjectSetup.cs/BuildMenu.cs lost $($t[1]) (platform-targets: '$($t[0])')" }
    }
    $abText = [IO.File]::ReadAllText((Resolve-Path -LiteralPath "$gkEditor/AgentBridge.cs"))
    $abPlat = @([regex]::Match($abText, '"compile ([a-z|]+),').Groups[1].Value -split '\|' | Where-Object { $_ } | Sort-Object)
    $gkPlat = @([regex]::Matches([IO.File]::ReadAllText((Resolve-Path -LiteralPath 'plugin/bin/gk-bridge')), "'compile ([a-z]+)'") | ForEach-Object { $_.Groups[1].Value } | Sort-Object)
    if (-not $abPlat -or ($abPlat -join ',') -ne ($gkPlat -join ',')) { "AgentBridge compile platforms ($($abPlat -join ', ')) differ from gk-bridge's ($($gkPlat -join ', '))" }
)
Check 'platform-targets: the Player Settings and build values it states are in ProjectSetup.cs/BuildMenu.cs; AgentBridge and gk-bridge compile the same platforms' (-not $ptBad) ($ptBad -join '; ')
# reference-docs keeps pointers, never second copies (packs/reference-docs/README.md); unity-package-management's
# select-packages.md names every pack whose packages.json it tells the agent to copy from
$ptrBad = @(
    foreach ($p in @(@('packs/reference-docs/shipping-2026.md', 'plugin/skills/launch-review/references/shipping-2026.md'), @('packs/reference-docs/packages.md', 'plugin/skills/unity-package-management/references/select-packages.md'))) {
        $lines = [IO.File]::ReadAllLines((Resolve-Path -LiteralPath $p[0]))
        if ($lines.Count -gt 5 -or -not (($lines -join ' ') -match [regex]::Escape($p[1]))) { "$($p[0]) is not a pointer of at most 5 lines to $($p[1])" }
    }
    $selTop = ([IO.File]::ReadAllLines((Resolve-Path -LiteralPath 'plugin/skills/unity-package-management/references/select-packages.md')) | Select-Object -First 15) -join "`n"
    foreach ($p in @(Get-ChildItem -Path 'packs\*\packages.json' | ForEach-Object { $_.Directory.Name })) {
        if (-not $selTop.Contains("``$p``")) { "select-packages.md lines 1-15 do not name the $p pack" }
    }
)
Check 'reference-docs shipping-2026.md and packages.md are pointers; select-packages.md names every pack with a packages.json' (-not $ptrBad) ($ptrBad -join '; ')
# its README says only the files in its table are here, and its docs cite plugin/ references by path
$rdReadme = [IO.File]::ReadAllText((Resolve-Path -LiteralPath packs/reference-docs/README.md))
$rdBad = @(
    foreach ($e in Get-ChildItem -LiteralPath packs/reference-docs) { $n = if ($e.PSIsContainer) { "$($e.Name)/" } else { $e.Name }; if ($e.Name -ne 'README.md' -and -not $rdReadme.Contains("| ``$n`` |")) { "packs/reference-docs/$n has no row in its README table" } }
    foreach ($f in @($tracked -like 'packs/reference-docs/*')) { foreach ($m in [regex]::Matches([IO.File]::ReadAllText((Resolve-Path -LiteralPath $f)), '`(plugin/[\w./-]+)`')) { if (-not (Test-Path -LiteralPath $m.Groups[1].Value)) { "$f cites $($m.Groups[1].Value), which does not exist" } } }
)
Check "reference-docs: README table lists every file and folder, every cited plugin/ path exists" (-not $rdBad) ($rdBad -join '; ')

# vendored skills: the house edits an upstream merge must reapply. ui-ugui marks them BEGIN/END HOUSE; unity-cli keeps
# a gamekit block, read-only allowed-tools and the exit-code table markers
$houseBad = @(
    foreach ($f in @($tracked -like 'plugin/skills/*.md')) {
        $marks = @([regex]::Matches([IO.File]::ReadAllText((Resolve-Path -LiteralPath $f)), '<!-- (BEGIN|END) HOUSE') | ForEach-Object { $_.Groups[1].Value })
        for ($i = 0; $i -lt $marks.Count; $i++) { if ($marks[$i] -ne @('BEGIN', 'END')[$i % 2]) { "${f}: HOUSE markers out of order"; break } }
        if ($marks.Count % 2) { "${f}: $($marks.Count) HOUSE markers (unpaired)" }
    }
    $uc = [IO.File]::ReadAllText((Resolve-Path -LiteralPath 'plugin/skills/unity-cli/SKILL.md'))
    foreach ($s in '> **In a gamekit game these project rules override', 'never run `unity mcp configure`', 'never the bootstrap recipe below',
        'into the game''s `.claude/skills/`, so do not run it', '**A gamekit game starts with `gamekit:new-game` instead.**',
        '<!-- exit-codes:begin', '<!-- exit-codes:end -->', '> House edits a merge from upstream must reapply',
        '**Tests and builds:**', '**Updating the CLI is the user''s call:**', '**No agent setup on your own:**',
        'Editor and module installs are the user''s call', '[catalog-plugins.md](references/catalog-plugins.md)') {
        if (-not $uc.Contains($s)) { "unity-cli SKILL.md lost: $s" }
    }
    # a merge that drops a whole HOUSE block, markers included, still pairs up: one line from each block that carries a
    # rule the upstream text contradicts
    $ug = [IO.File]::ReadAllText((Resolve-Path -LiteralPath 'plugin/skills/ui-ugui/SKILL.md'))
    foreach ($s in '**House rules win.**', '`InputSystemUIInputModule`, not `StandaloneInputModule`', '`SafeAreaFitter` (GameKit)',
        'importExamples: false, interactive: false)', 'Split canvases by change rate', '## Screens', 'Inspector refs are not',
        'ContentSizeFitter on a child of a Layout Group', 'Feature folders inside the game folder', 'nothing to close') {
        if (-not $ug.Contains($s)) { "ui-ugui SKILL.md lost house edit: $s" }
    }
    # one line from each house block of the ScrollRect reference
    $sv = [IO.File]::ReadAllText((Resolve-Path -LiteralPath 'plugin/skills/ui-ugui/references/scrollview-setup.md'))
    foreach ($s in 'a pooled long list: RectTransform only', '`RectMask2D` (no stencil', 'Mathf.Max(0, count',
        'a pooled list never sets `content.sizeDelta`') {
        if (-not $sv.Contains($s)) { "ui-ugui scrollview-setup.md lost house edit: $s" }
    }
    $ucFront = [regex]::Match($uc, '(?s)\A---\r?\n(.*?)\r?\n---').Groups[1].Value
    if ($ucFront -notmatch 'allowed-tools:' -or $ucFront -match '(?m)^\s*-\s*(Bash|PowerShell)\s*$|(?m)^allowed-tools:.*\b(Bash|PowerShell)\b(?!\()') { 'unity-cli allowed-tools is not narrowed to read-only unity forms' }
    foreach ($r in 'build-run-test', 'playmode-verification-loop', 'workflows', 'catalog-plugins') {
        $top = ([IO.File]::ReadAllLines((Resolve-Path -LiteralPath "plugin/skills/unity-cli/references/$r.md")) | Select-Object -First 15) -join "`n"
        if ($top -notmatch '(?i)> \*\*(In a )?gamekit') { "unity-cli references/$r.md lost its gamekit note at the top" }
    }
)
Check 'vendored skills: HOUSE markers pair up, ui-ugui and unity-cli keep their house edits' (-not $houseBad) ($houseBad -join '; ')

# twin texts: the output style's VISUAL EXPLAINER row lists the skill's section-2 headings in order; the marketplace
# entry repeats plugin.json's description
$vcRow = @([IO.File]::ReadAllLines((Resolve-Path -LiteralPath 'plugin/output-styles/visual-clarity.md')) | Where-Object { $_ -like '| VISUAL EXPLAINER |*' })
$vcHeads = @(if ($vcRow) { [regex]::Matches($vcRow[0], '`(### [^`]+)`') | ForEach-Object { $_.Groups[1].Value } })
$veSect = [regex]::Match([IO.File]::ReadAllText((Resolve-Path -LiteralPath 'plugin/skills/visual-explainer/SKILL.md')), '(?ms)^## 2\..*?(?=^## )').Value
$veHeads = @([regex]::Matches($veSect, '(?m)^\| `(### [^`]+)`') | ForEach-Object { $_.Groups[1].Value })
Check "visual-clarity's VISUAL EXPLAINER row lists visual-explainer's $($veHeads.Count) section headings in order" ($veHeads.Count -gt 0 -and ($vcHeads -join '|') -ceq ($veHeads -join '|')) "style: $($vcHeads -join ', ') / skill: $($veHeads -join ', ')"
# and its trigger stays narrow ("3+ parts": an "acikla" about one member must not load it), and each Size cell stays
# within the style's caps for diagrams, steps per group and table rows
$vcText = [IO.File]::ReadAllText((Resolve-Path -LiteralPath 'plugin/output-styles/visual-clarity.md'))
$caps = @{ nodes = [regex]::Match($vcText, 'at most (\d+) nodes').Groups[1].Value; 'steps per group' = [regex]::Match($vcText, 'at most (\d+) visible items per group').Groups[1].Value; rows = [regex]::Match($vcText, 'and (\d+) rows').Groups[1].Value }
$veBad = @(
    if ((Front 'plugin/skills/visual-explainer/SKILL.md').description -notmatch '3\+ parts') { 'description lost its "3+ parts" qualifier' }
    foreach ($k in @($caps.Keys)) { if (-not $caps[$k]) { "visual-clarity.md no longer states a $k cap" } }
    foreach ($row in [regex]::Matches($veSect, '(?m)^\| `(### [^`]+)`.*\| ([^|\r\n]+) \|\s*$')) {
        foreach ($k in @($caps.Keys)) {
            $n = [regex]::Match($row.Groups[2].Value, "(\d+) $k\b")
            if ($n.Success -and $caps[$k] -and [int]$n.Groups[1].Value -gt [int]$caps[$k]) { "$($row.Groups[1].Value) size '$($row.Groups[2].Value.Trim())' is over the style's $($caps[$k]) $k" }
        }
    }
)
Check "visual-explainer: description keeps '3+ parts', Size cells within the style's caps ($($caps.nodes) nodes, $($caps.'steps per group') steps per group, $($caps.rows) rows)" (-not $veBad) ($veBad -join '; ')
# the headings agents send their judging to by name: a quoted "Heading" or a section sign in an agent must be a heading
# (or, for a quoted phrase, a line start) in a file the agent cites: a ${CLAUDE_PLUGIN_ROOT}/ path, or the md files of a
# plugin skill it names. Quoted lower-case words and phrases with a colon are report strings, not headings.
$sect = [char]0xA7   # the section sign, kept out of this ASCII file
$skillNames = @(Get-ChildItem -LiteralPath plugin/skills -Directory | ForEach-Object Name)
$agHeadCount = 0
$agHeadBad = @(
    foreach ($f in @($tracked -like 'plugin/agents/*.md')) {
        $at = [IO.File]::ReadAllText((Resolve-Path -LiteralPath $f))
        $cited = @([regex]::Matches($at, '\$\{CLAUDE_PLUGIN_ROOT\}/(skills/[\w./-]+\.md)') | ForEach-Object { "plugin/$($_.Groups[1].Value)" }) +
            @($skillNames | Where-Object { $at -match "(?<![\w-])$([regex]::Escape($_))(?![\w-])" } | ForEach-Object { $n = $_; $tracked -like "plugin/skills/$n/*.md" })
        $citedText = (@($cited | Sort-Object -Unique | Where-Object { Test-Path -LiteralPath $_ } | ForEach-Object { [IO.File]::ReadAllText((Resolve-Path -LiteralPath $_)) })) -join "`n"
        # a heading is quoted right after "<skill>'s", alone or as a list ("A", "B" and "C"), or alone in parentheses
        # (section ("Two numbers have a budget")), and is words only; other quoted text is a UI, report or placeholder
        # string ("Tap", "temiz", "TODO (Turkish / English)")
        foreach ($list in [regex]::Matches($at, '''s ("[^"\r\n]+"(?:(?:, | and )"[^"\r\n]+")*)|\(("[^"\r\n]+")\)')) {
            foreach ($m in [regex]::Matches($list.Groups[1].Value + $list.Groups[2].Value, '"([A-Z][A-Za-z ,-]*[a-z])"')) {
                $agHeadCount++
                $h = [regex]::Escape($m.Groups[1].Value)
                if ($citedText -notmatch "(?m)^(#{2,4} (\d+\. |[A-Z]\.\d* )?$h\s*$|$h)") { "$f quotes ""$($m.Groups[1].Value)"", no heading or line of that name in the files it cites" }
            }
        }
        foreach ($m in [regex]::Matches($at, "$sect([A-Z0-9](?:\.\d+)?)\b")) {
            $agHeadCount++
            if ($citedText -notmatch "(?m)^#{2,3} $([regex]::Escape($m.Groups[1].Value))\.?\s") { "$f cites $sect$($m.Groups[1].Value), no such heading in the files it cites" }
        }
    }
)
Check "agents: the $agHeadCount quoted headings and section signs they cite exist in the files they name" ($agHeadCount -gt 0 -and -not $agHeadBad) (@($agHeadBad | Sort-Object -Unique) -join '; ')
$mkDesc = @((Get-Content -LiteralPath '.claude-plugin/marketplace.json' -Raw | ConvertFrom-Json).plugins | Where-Object name -eq 'gamekit').description
$plDesc = (Get-Content -LiteralPath 'plugin/.claude-plugin/plugin.json' -Raw | ConvertFrom-Json).description
Check 'marketplace.json gamekit description = plugin.json description' ($plDesc -and $mkDesc -ceq $plDesc)

Section 'GameKit release'
# CLAUDE.md, Releasing GameKit: the template pins the tag of package.json's version, and the tag exists here and on
# origin. A pending release (version bumped, not tagged or not pointed at) is a warning: new games get the old pin.
$gkVersion = (Get-Content -LiteralPath 'packages/com.yunusburkut.gamekit/package.json' -Raw | ConvertFrom-Json).version
$gkPin = [regex]::Match([IO.File]::ReadAllText((Resolve-Path -LiteralPath 'project/Packages/manifest.json')), '#(gamekit-v[\d.]+)"').Groups[1].Value
$localTags = @(git tag -l 'gamekit-v*')
Check "project manifest pins an existing GameKit tag ($gkPin)" ($gkPin -and $localTags -contains $gkPin) "tags: $($localTags -join ', ')"
if ($gkPin -ne "gamekit-v$gkVersion") {
    Write-Host "  warn  GameKit $gkVersion is not released: project/Packages/manifest.json pins $gkPin, so new games miss it. Finish CLAUDE.md 'Releasing GameKit' (tag gamekit-v$gkVersion, push it, re-point the manifest)" -ForegroundColor Yellow
}
$remoteTags = @(cmd /c "git ls-remote --tags origin gamekit-v* 2>nul" | ForEach-Object { ($_ -split 'refs/tags/')[-1] } | Where-Object { $_ -notlike '*^{}' })
if ($LASTEXITCODE -ne 0) { Write-Host '  skip  origin not reachable: pinned tag not checked on the remote' }
elseif ($gkPin -and $remoteTags -notcontains $gkPin) { Write-Host "  warn  $gkPin exists locally but not on origin: games cannot resolve it until the tag is pushed" -ForegroundColor Yellow }
# test-template.ps1 always uses a file: GameKit, so two template settings games rely on are checked here as text:
# agents read package sources under Library/PackageCache (no deny may cover it), and WebGL saves survive a reload
$gameSettings = Get-Content -LiteralPath 'project/.claude/settings.json' -Raw | ConvertFrom-Json
$denyCache = @($gameSettings.permissions.deny | Where-Object { $_ -match '^Read\((?:\./|\*\*/)?Library/(?:\*|PackageCache)' })
$webgl = [IO.File]::ReadAllText((Resolve-Path -LiteralPath 'project/Assets/WebGLTemplates/Responsive/index.html'))
Check 'project: no settings.json deny covers Library/PackageCache; the WebGL template keeps autoSyncPersistentDataPath: true' (-not $denyCache -and $webgl -match 'autoSyncPersistentDataPath:\s*true') ($denyCache -join ', ')
# the ask and deny rules for git, gh, butler, steamcmd and unity are kept by hand in both shells' forms: a rule in one
# form only lets the agent run that command unprompted through the other tool
$mirror = foreach ($list in 'ask', 'deny') {
    $rules = @($gameSettings.permissions.$list)
    foreach ($r in $rules) {
        if ($r -match '^(Bash|PowerShell)\(((?:git|gh|butler|steamcmd|unity)\b.*)\)$') {
            $twin = "$(if ($Matches[1] -eq 'Bash') { 'PowerShell' } else { 'Bash' })($($Matches[2]))"
            if ($rules -notcontains $twin) { "$list $r (no $twin)" }
        }
    }
}
Check 'project: every Bash/PowerShell(git|gh|butler|steamcmd|unity ...) ask/deny rule has its other-shell twin' (-not $mirror) ($mirror -join ', ')
# unity-package-management's SKILL.md names the Pipeline package's command flags as checked against the pinned
# version's source: read that source when a local game has the pinned version cached
$pipePin = [regex]::Match([IO.File]::ReadAllText((Resolve-Path -LiteralPath 'project/Packages/manifest.json')), '"com\.unity\.pipeline":\s*"([^"]+)"').Groups[1].Value
$pipeSrc = Get-ChildItem -Path (Join-Path (Split-Path $PSScriptRoot) '*\Library\PackageCache\com.unity.pipeline@*\package.json') -ErrorAction SilentlyContinue |
    Where-Object { (Get-Content -LiteralPath $_.FullName -Raw | ConvertFrom-Json).version -eq $pipePin } | Select-Object -First 1
$pmCmd = if ($pipeSrc) { Join-Path $pipeSrc.DirectoryName 'Editor\Commands\PackageManager\PackageManagerCommand.cs' }
if ($pmCmd -and (Test-Path -LiteralPath $pmCmd)) {
    $pmText = [IO.File]::ReadAllText($pmCmd)
    $pmBad = @(foreach ($a in 'name', 'confirm', 'dry-run', 'wait') { if (-not $pmText.Contains("CliArg(`"$a`"")) { "--$a" } }) + @(if ($pmText -notmatch 'public static \w+ Resolve\(') { 'Resolve command' })
    Check "unity-package-management: Pipeline $pipePin's PackageManagerCommand.cs has --name, --confirm, --dry-run, --wait and Resolve" (-not $pmBad) ("missing: $($pmBad -join ', ') in $pmCmd")
} else { Write-Host "  skip  Pipeline $pipePin source: no local game has it in Library\PackageCache" }

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
# every plugin skill and agent (ui-ugui, design-critic cite them too), the project docs a game starts with, and the
# reference-docs playbook; a section cited as "player-clarity <section sign>F" must be a heading there
$clFiles = @($tracked | Where-Object { ($_ -like 'plugin/skills/*.md') -or $_ -like 'plugin/agents/*.md' -or $_ -eq 'packs/reference-docs/clarity-playbook.md' }) + $projectDocs
$clTexts = @($clFiles | ForEach-Object { [IO.File]::ReadAllText((Resolve-Path -LiteralPath $_)) })
$clCited = @($clTexts | ForEach-Object { [regex]::Matches($_, '\bCL\d\d\b') | ForEach-Object Value } | Sort-Object -Unique)
$clMissing = @($clCited | Where-Object { $clDefs -notcontains $_ })
$clSects = @($clTexts | ForEach-Object { [regex]::Matches($_, "(?:player-clarity|clarity-rules(?:\.md)?)``? ?$sect([A-Z])(\d?)") } | ForEach-Object { $_.Groups[1].Value + $_.Groups[2].Value } | Sort-Object -Unique)
# inside player-clarity's own files and clarity-reviewer a bare section sign means clarity-rules (other skills' files
# cite their own references' sections, e.g. difficulty-rhythm.md's, and the playbook numbers its own)
$clOwn = @($tracked | Where-Object { $_ -like 'plugin/skills/player-clarity/*.md' -or $_ -eq 'plugin/agents/clarity-reviewer.md' })
$clSects += @($clOwn | ForEach-Object { [regex]::Matches([IO.File]::ReadAllText((Resolve-Path -LiteralPath $_)), "$sect([A-Z])(\d?)\b") } | ForEach-Object { $_.Groups[1].Value + $_.Groups[2].Value })
$clSects = @($clSects | Sort-Object -Unique)
$clMissing += @($clSects | Where-Object { $crText -notmatch "(?m)^#{2,3} $_\. " } | ForEach-Object { "$sect$_" })
Check "clarity-rules: $($clDefs.Count) CL IDs unique, the $($clCited.Count) cited IDs and $($clSects.Count) cited sections defined" ($clDefs.Count -gt 0 -and -not $clDup -and -not $clMissing) ((@($clDup | ForEach-Object { "dup $_" }) + $clMissing) -join ', ')
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
# README "Global Claude katmani": the user-level layer the plugin and the Blender work lean on. A missing piece fails
# (machine state: restore ~/.claude), since the pipeline's Blender routing, the export contract and the router need it
$pieces = 'skills\grill-me', 'skills\orchestrate', 'skills\unity-export', 'skills\blender-director', 'skills\blender-image-to-3d', 'rules\unity-games.md', 'hooks\enhance-prompt.ps1'
$noPiece = @($pieces | Where-Object { -not (Test-Path -LiteralPath (Join-Path $env:USERPROFILE ".claude\$_")) } | ForEach-Object { '~/.claude/' + ($_ -replace '\\', '/') })
Check "user-level layer: all $($pieces.Count) pieces in ~/.claude (README, Global Claude katmani)" (-not $noPiece) ("missing: " + ($noPiece -join ', '))
# what the user layer restates from the plugin: grill-me's game branch writes pipeline's card (its fields, then phase 1
# L's closing line), and unity-games.md quotes gk-bridge's exit codes
$grillF = Join-Path $env:USERPROFILE '.claude\skills\grill-me\SKILL.md'
$ugF = Join-Path $env:USERPROFILE '.claude\rules\unity-games.md'
if ((Test-Path -LiteralPath $grillF) -and (Test-Path -LiteralPath $ugF)) {
    $grillT = [IO.File]::ReadAllText($grillF) -replace '\s+', ' '
    $pipeT = [IO.File]::ReadAllText((Resolve-Path -LiteralPath 'plugin/skills/pipeline/SKILL.md')) -replace '\s+', ' '
    $gkb = [IO.File]::ReadAllText((Resolve-Path -LiteralPath 'plugin/bin/gk-bridge'))
    $userBad = @(
        foreach ($t in '`Not:`', '`Targets:`', '`Budget:`', '`evidence:`', '`Open questions: none`', '`Base:`', 'phase 1 L') {
            if (-not $grillT.Contains($t)) { "grill-me lost $t" }
        }
        foreach ($t in @(@('Not:', '(?m)Not: <'), @('Targets:', 'Targets: PC'), @('Budget:', 'Budget: <'), @('evidence:', '- evidence: <'), @('Base:', 'Base: <'), @('Open questions: none', '`Open questions: none`'), @('closing line', '- L: .*end the turn with one line: "`devam` = burada'))) {
            if ($pipeT -notmatch $t[1]) { "pipeline SKILL.md no longer has the card's $($t[0]) that grill-me writes" }
        }
        if ([IO.File]::ReadAllText($ugF) -notmatch 'exit 0 pass, 1 fail, 2 unknown') { 'unity-games.md lost "exit 0 pass, 1 fail, 2 unknown"' }
        elseif (-not $gkb.Contains('PASS) exit 0 ;; FAIL) exit 1 ;; *) exit 2 ;;')) { 'gk-bridge exit codes are no longer 0 pass, 1 fail, 2 unknown (unity-games.md quotes them)' }
    )
    Check "user-level twins: grill-me's card fields and closing line match pipeline, unity-games.md's gk-bridge exit codes match gk-bridge" (-not $userBad) ($userBad -join '; ')
}
# both lean-code copies load in a game: outside the comment, the which-copy-wins line, rungs 2-3 and the seam bullet's
# second line (the game copy names its skills there) they must match
$leanUser = Join-Path $env:USERPROFILE '.claude\rules\lean-code.md'
if (Test-Path -LiteralPath $leanUser) {
    $leanBody = foreach ($lf in $leanUser, (Resolve-Path -LiteralPath 'project/.claude/rules/lean-code.md').Path) {
        $t = [regex]::Replace([IO.File]::ReadAllText($lf), '(?s)<!--.*?-->', '')
        $t = (($t -split '\r?\n' | Where-Object { $_ -notmatch '^(Inside a unity-game-template game|2\. |3\. |  case[ .])' }) -join "`n")
        [regex]::Replace($t, '\n{3,}', "`n`n").Trim()
    }
    Check 'lean-code: ~/.claude/rules and project/.claude/rules copies match outside rungs 2-3 and the seam bullet''s second line' ($leanBody[0] -ceq $leanBody[1]) 'lean-code copies drifted (outside rungs 2-3 and the seam bullet''s second line)'
} else { Write-Host '  skip  no ~/.claude/rules/lean-code.md' }
# every headless Blender line the user-level skills teach starts without the user's add-ons and prefs, as README step 4
# and the probe below run it
$bSkills = @('blender-director', 'blender-image-to-3d', 'unity-export', 'references' | ForEach-Object { Join-Path $env:USERPROFILE ".claude\skills\$_" } | Where-Object { Test-Path -LiteralPath $_ })
if ($bSkills) {
    $noFactory = @(Get-ChildItem -LiteralPath $bSkills -Recurse -File -Include *.md, *.py | Where-Object { $_.FullName -notmatch '\\__pycache__\\' } |
        Select-String -SimpleMatch '--background' | Where-Object { $_.Line -notmatch '--factory-startup' } | ForEach-Object { "$($_.Path.Substring($env:USERPROFILE.Length + 1)):$($_.LineNumber)" })
    Check 'user-level Blender skills: every --background line carries --factory-startup' (-not $noFactory) ($noFactory -join ', ')
}
# background auto-update of a private marketplace (this one) authenticates with a token from the environment
if (-not ($env:GITHUB_TOKEN -or $env:GH_TOKEN -or [Environment]::GetEnvironmentVariable('GITHUB_TOKEN', 'User') -or [Environment]::GetEnvironmentVariable('GH_TOKEN', 'User'))) {
    Write-Host '  warn  neither GITHUB_TOKEN nor GH_TOKEN is set: gamekit does not auto-update in the background (claude plugin update still works)' -ForegroundColor Yellow
}
# The Blender the *_for_cli tools (BLENDER_PATH, then PATH) and ensure-blender.ps1 (BLENDER_PATH, then the newest
# install by FileVersion) run: BLENDER_PATH first, then PATH, then the hook's FileVersion order
$blender = $null; $blenderFrom = ''; $cliBlend = $null
if ($env:BLENDER_PATH) {
    if (Test-Path -LiteralPath $env:BLENDER_PATH) { $blender = $env:BLENDER_PATH; $blenderFrom = 'BLENDER_PATH' }
    else { Write-Host "  warn  BLENDER_PATH ($env:BLENDER_PATH) does not exist: *_for_cli calls and ensure-blender cannot start it (README, Blender step 1)" -ForegroundColor Yellow }
}
if (-not $blender) { $blender = (Get-Command blender -ErrorAction SilentlyContinue).Source; if ($blender) { $blenderFrom = 'PATH' } }
if (-not $blender) {
    # by version, not by name: 'Blender 5.10' sorts before 'Blender 5.9' as a string
    $blender = Get-ChildItem "$env:ProgramFiles\Blender Foundation\Blender *\blender.exe" -ErrorAction SilentlyContinue |
        Sort-Object { $v = $_.VersionInfo; [version]('{0}.{1}.{2}' -f $v.FileMajorPart, $v.FileMinorPart, $v.FileBuildPart) } -Descending |
        Select-Object -First 1 -ExpandProperty FullName
    if ($blender) { $blenderFrom = 'newest install' }
}
if ($blender) {
    Write-Host "  note  probing $blender (from $blenderFrom)"
    # the live tools need the MCP add-on in this Blender's major.minor, the same test ensure-blender makes; its Auto
    # Start preference lives in userpref.blend and is not read here (README, Blender step 2)
    $bv = (Get-Item -LiteralPath $blender).VersionInfo; $bver = '{0}.{1}' -f $bv.FileMajorPart, $bv.FileMinorPart
    $bconfig = Join-Path $env:APPDATA 'Blender Foundation\Blender'
    if ((Test-Path -LiteralPath $bconfig) -and -not (Test-Path (Join-Path $bconfig "$bver\extensions\*\mcp\__init__.py")) -and
        -not (Test-Path (Join-Path $bconfig "$bver\scripts\addons\*mcp*\__init__.py"))) {
        Write-Host "  warn  no Blender MCP add-on for Blender ${bver}: live mcp__Blender__ calls will block (install it in $bver, README Blender step 2)" -ForegroundColor Yellow
    }
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
    # with unity-export's FBX call verbatim. kit_common.py and city_assets.py are excerpts (kit_common needs a game's
    # kit_palette), so they are compiled, never imported; toon_prop.py is complete and runs below. The probe also saves
    # an empty .blend for the *_for_cli check further down.
    $py = @($tracked -like '*.py' | ForEach-Object { (Resolve-Path -LiteralPath $_).Path })
    $py += @(Get-ChildItem -Path (Join-Path $skillDir 'blender-*'), (Join-Path $skillDir 'unity-export') -Recurse -Filter *.py -ErrorAction SilentlyContinue | ForEach-Object FullName)
    $fbx = Join-Path $env:TEMP 'gk-test-all-cube.fbx'
    $cliBlend = Join-Path $env:TEMP 'gk-test-all-empty.blend'
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
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.save_as_mainfile(filepath=r'$cliBlend')
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
    # the delivery half of the PR_Anvil gate runner (blender-image-to-3d SKILL.md), about 15 s: validate, export_delivery
    # --format FBX and roundtrip --manifest, written to %TEMP% so the source stays as it is. The source is the local,
    # untracked _asset-samples\PR_Anvil baked file when present; otherwise a fixture built headless here: a 0.8 m UV'd
    # cube in LOW wired to a basecolor and a roughness PNG, plus a packed mask named in scene["packed_channels"] the way
    # bake_maps --pack-mask writes it, so texture shipping, the mask swap and the manifest comparison all run on any
    # machine. Ceiling: bake_maps' bake itself and the Unity half (unity-check.ps1) stay manual; they need minutes and
    # an Editor.
    $anvil = Join-Path $PSScriptRoot '_asset-samples\PR_Anvil\PR_Anvil_baked.blend'
    $i3d = Join-Path $skillDir 'blender-image-to-3d\scripts'
    if (Test-Path -LiteralPath (Join-Path $i3d 'roundtrip.py')) {
        $delOut = Join-Path $env:TEMP "gk-test-all-delivery-$PID"
        New-Item -ItemType Directory -Force $delOut | Out-Null
        $delBad = @(
            if (Test-Path -LiteralPath $anvil) { $delBlend = $anvil; $delName = 'PR_Anvil' }
            else {
                $delName = 'PR_Fixture'
                $delBlend = Join-Path $delOut 'src\PR_Fixture_baked.blend'
                $fixPy = Join-Path $delOut 'make_fixture.py'
                [IO.File]::WriteAllText($fixPy, @"
import bpy, os
from mathutils import Matrix
blend = r'$delBlend'
tex = os.path.join(os.path.dirname(blend), 'textures')
os.makedirs(tex, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
low = bpy.data.collections.new('LOW')
scene.collection.children.link(low)
bpy.ops.mesh.primitive_cube_add(size=0.8)
ob = bpy.context.active_object
ob.name = ob.data.name = 'PR_Fixture'
ob.data.transform(Matrix.Translation((0.0, 0.0, 0.4)))
for c in list(ob.users_collection): c.objects.unlink(ob)
low.objects.link(ob)
def png(name, colour, non_color):
    img = bpy.data.images.new(name, 32, 32)
    img.generated_color = colour
    if non_color: img.colorspace_settings.name = 'Non-Color'
    img.filepath_raw = os.path.join(tex, name + '.png'); img.file_format = 'PNG'; img.save()
    return img
mat = bpy.data.materials.new('M_PR_Fixture')
mat.use_nodes = True
nt = mat.node_tree
bsdf = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
for img, socket in ((png('PR_Fixture_basecolor', (0.6, 0.4, 0.2, 1.0), False), 'Base Color'),
                    (png('PR_Fixture_roughness', (0.5, 0.5, 0.5, 1.0), True), 'Roughness')):
    node = nt.nodes.new('ShaderNodeTexImage'); node.image = img
    nt.links.new(node.outputs['Color'], bsdf.inputs[socket])
ob.data.materials.append(mat)
png('PR_Fixture_mask', (0.0, 1.0, 0.0, 0.5), True)
scene['packed_channels'] = 'R metallic, G AO, A 1-roughness; files: PR_Fixture_mask.png'
bpy.ops.wm.save_as_mainfile(filepath=blend)
"@, (New-Object Text.UTF8Encoding $false))
                $res = cmd /c "`"$blender`" --background --factory-startup --python-exit-code 1 --python `"$fixPy`" 2>&1"
                if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $delBlend)) { "fixture build exit ${LASTEXITCODE}: $(($res | Select-Object -Last 3) -join ' ')" }
            }
            if (Test-Path -LiteralPath $delBlend) {
                foreach ($step in @(
                    @('validate', "--python `"$i3d\validate.py`" -- --blend `"$delBlend`" --collections LOW --out `"$delOut\validate.json`" --budget-tris 1500 --require-uv"),
                    @('export_delivery', "--python `"$i3d\export_delivery.py`" -- --blend `"$delBlend`" --out `"$delOut\export`" --name $delName --format FBX --collections LOW --no-animation --engine Unity"),
                    @('roundtrip', "--python `"$i3d\roundtrip.py`" -- --file `"$delOut\export\$delName.fbx`" --out `"$delOut\rt`" --expect-height 0.80 --manifest `"$delOut\export\asset-manifest.json`" --res 256"))) {
                    # --factory-startup on every step, as the skill's own command lines run them
                    $res = cmd /c "`"$blender`" --background --factory-startup --python-exit-code 1 $($step[1]) 2>&1"
                    if ($LASTEXITCODE -ne 0) { "$($step[0]) exit ${LASTEXITCODE}: $(($res | Where-Object { $_ -match 'FAIL|ERRORS|Error|Traceback' } | Select-Object -First 2) -join ' ')"; break }
                    if ($step[0] -eq 'roundtrip' -and -not ($res -match '^ERRORS \[\]')) { 'roundtrip printed no empty ERRORS list' }
                }
                if ($delName -eq 'PR_Fixture' -and -not $LASTEXITCODE) {
                    # the mask replaces the roughness map and ships beside the FBX with the basecolor
                    $shipped = @(Get-ChildItem -LiteralPath "$delOut\export" -Filter *.png | ForEach-Object Name | Sort-Object) -join ','
                    if ($shipped -ne 'PR_Fixture_basecolor.png,PR_Fixture_mask.png') { "shipped textures '$shipped', expected the basecolor and the mask" }
                }
            }
        )
        Check "blender-image-to-3d: $delName validate, export_delivery FBX and roundtrip against its manifest exit 0" (-not $delBad) ($delBad -join '; ')
        Remove-Item -LiteralPath $delOut -Recurse -Force -ErrorAction SilentlyContinue
    } else { Write-Host '  skip  blender-image-to-3d delivery chain: the skill''s scripts are not installed' }
    # toon-art's runnable chain, Blender half: toon_prop.py builds, checks and exports SM_Barrel, and its manifest's
    # collider is the mesh bounds in Unity prefab space: the size is Blender (x, z, y), the centre is (-x, z, -y) of the
    # Blender bounds centre, the pivot at the base. The barrel is centred, so the same process then moves its mesh by
    # Blender (+0.1, +0.2, 0) and has toon_prop's own write_manifest write SM_Barrel_offset.json, whose centre must be
    # Unity (-0.1, h/2, -0.2): a lost minus sign in to_unity() fails there. Ceiling: the Unity half
    # (PropBuilder.cs.txt, the Euler(90,180,0) child that turns Blender's front -Y to transform.forward) runs only
    # when a game copies it in; test-template -Packs toon-art checks the pack's own compile, not this example.
    $toonOut = Join-Path $env:TEMP 'gk-test-all-toon'
    if (Test-Path -LiteralPath $toonOut) { Remove-Item -LiteralPath $toonOut -Recurse -Force }
    New-Item -ItemType Directory -Force $toonOut | Out-Null
    $toonPy = Join-Path $toonOut 'run_toon_prop.py'
    [IO.File]::WriteAllText($toonPy, @"
import bpy, os
from mathutils import Matrix
src = r'$((Resolve-Path -LiteralPath 'packs/toon-art/examples/toon_prop.py').Path)'
g = {'__name__': '__main__', '__file__': src}
exec(compile(open(src, encoding='utf-8').read(), src, 'exec'), g)
ob = bpy.data.objects[g['NAME']]
ob.data.transform(Matrix.Translation((0.1, 0.2, 0.0)))
ob.data.update()
g['write_manifest'](ob, 0, os.path.join(r'$toonOut', 'SM_Barrel_offset.json'))
"@, (New-Object Text.UTF8Encoding $false))
    $res = cmd /c "`"$blender`" --background --factory-startup --python-exit-code 1 --python `"$toonPy`" -- `"$toonOut`" 2>&1"
    $toonCode = $LASTEXITCODE
    $models = Join-Path $toonOut 'Assets\__GAME__\Game\Art\Models'
    $dims = [regex]::Match(($res -join "`n"), '\[toon_prop\] SM_Barrel: (\d+) triangles, ([\d.]+) x ([\d.]+) x ([\d.]+) m')
    $toonBad = @(
        if ($toonCode -ne 0 -or -not $dims.Success) { "run failed: $(($res | Select-Object -Last 3) -join ' ')" }
        elseif (-not ((Test-Path -LiteralPath "$models\SM_Barrel.fbx") -and (Get-Item -LiteralPath "$models\SM_Barrel.fbx").Length)) { 'no SM_Barrel.fbx' }
        elseif (-not (Test-Path -LiteralPath "$models\SM_Barrel.json")) { 'no SM_Barrel.json' }
        else {
            $man = Get-Content -LiteralPath "$models\SM_Barrel.json" -Raw | ConvertFrom-Json
            $c = $man.colliderCenter; $s = $man.colliderSize
            $bx, $by, $bz = [double]$dims.Groups[2].Value, [double]$dims.Groups[3].Value, [double]$dims.Groups[4].Value
            if ($man.mesh -ne 'SM_Barrel' -or [int]$man.triangles -ne [int]$dims.Groups[1].Value) { "manifest mesh/triangles $($man.mesh)/$($man.triangles)" }
            if ([math]::Abs($s.x - $bx) -gt 0.006 -or [math]::Abs($s.y - $bz) -gt 0.006 -or [math]::Abs($s.z - $by) -gt 0.006) { "colliderSize ($($s.x), $($s.y), $($s.z)) is not Blender ($bx, $by, $bz) as (x, z, y)" }
            if ([math]::Abs($c.y - $s.y / 2) -gt 0.001) { "colliderCenter.y $($c.y) is not half the height $($s.y): the pivot is not the base" }
            if ([math]::Abs($c.x) -gt 0.001 -or [math]::Abs($c.z) -gt 0.001) { "colliderCenter ($($c.x), $($c.z)) off the axis for the centred barrel: the (-x, z, -y) mapping broke" }
            if (@($man.roles).Count -ne @($man.colors).Count -or @($man.roles).Count -ne @($man.smoothness).Count) { 'roles, colors and smoothness differ in length' }
            $off = if (Test-Path -LiteralPath "$toonOut\SM_Barrel_offset.json") { (Get-Content -LiteralPath "$toonOut\SM_Barrel_offset.json" -Raw | ConvertFrom-Json).colliderCenter }
            if (-not $off) { 'no SM_Barrel_offset.json' }
            elseif ([math]::Abs($off.x + 0.1) -gt 0.001 -or [math]::Abs($off.z + 0.2) -gt 0.001 -or [math]::Abs($off.y - $c.y) -gt 0.001) { "colliderCenter ($($off.x), $($off.y), $($off.z)) for the barrel moved by Blender (+0.1, +0.2, 0) is not (-0.1, $($c.y), -0.2): to_unity() lost the (-x, z, -y) signs" }
        }
    )
    Check 'toon-art: toon_prop.py exports SM_Barrel and a manifest whose collider is the bounds in Unity space' (-not $toonBad) ($toonBad -join '; ')
    if (Test-Path -LiteralPath $toonOut) { Remove-Item -LiteralPath $toonOut -Recurse -Force -ErrorAction SilentlyContinue }
} else { Write-Host '  skip  no Blender installed' }
# every profile: after a reinstall or account switch a stale patched copy can sit next to the active unpatched one
$cli = @(Get-ChildItem "$env:LOCALAPPDATA\Claude-Data\*\Claude Extensions\ant.dir.gh.blender.blender-mcp\blmcp\tools_helpers\blender_cli.py" -ErrorAction SilentlyContinue)
if ($cli) {
    # local patch, lost on extension updates; without it every *_for_cli MCP call times out. The fix (recipe:
    # README.md, Blender step 5): add stdin=subprocess.DEVNULL to the subprocess.run(...) call in each file listed
    $unpatched = @($cli | Where-Object { -not (Select-String -LiteralPath $_.FullName -Pattern 'stdin=subprocess\.DEVNULL' -Quiet) } | ForEach-Object FullName)
    Check "Blender MCP extension: $($cli.Count) copy(ies) keep the stdin=DEVNULL patch" (-not $unpatched) ("add stdin=subprocess.DEVNULL to subprocess.run in run_blender_cli (README.md, Blender step 5): " + ($unpatched -join ', '))
    # End to end, what the grep only infers: the active copy's own run_blender_cli, called from its .venv python with
    # stdin held open as a pipe (as the MCP server's is) and this shell's BLENDER_PATH, returns within 60 s. The active
    # copy is chosen as plugin/hooks/ensure-blender.ps1 chooses it: the one under a running blender-mcp.exe, else the
    # newest (the installer keeps archive times, so newest is only a guess)
    $extName = 'Claude Extensions\ant.dir.gh.blender.blender-mcp'
    $live = @(try { Get-CimInstance Win32_Process -Filter "Name='blender-mcp.exe'" -ErrorAction Stop | ForEach-Object ExecutablePath } catch { })
    $active = @($cli | Where-Object { $r = $_.FullName.Substring(0, $_.FullName.IndexOf($extName) + $extName.Length)
            @($live | Where-Object { $_ -and $_.StartsWith($r + '\', [StringComparison]::OrdinalIgnoreCase) }).Count }) +
        @($cli | Sort-Object LastWriteTime -Descending) | Select-Object -First 1
    $extRoot = Split-Path (Split-Path (Split-Path $active.FullName))
    $venvPy = Join-Path $extRoot '.venv\Scripts\python.exe'
    if ((Test-Path -LiteralPath $venvPy) -and $blender -and $cliBlend -and (Test-Path -LiteralPath $cliBlend)) {
        $driver = Join-Path $env:TEMP 'gk-test-all-forcli.py'
        [IO.File]::WriteAllText($driver, @"
import sys
sys.path.insert(0, r'$extRoot')
from blmcp.tools_helpers.blender_cli import run_blender_cli
try: print('GKCLI', run_blender_cli(r'$cliBlend', 'result = {"ok": 1}', timeout=60))
except Exception as e: print('GKCLI error', str(e).splitlines()[0])
"@, (New-Object Text.UTF8Encoding $false))
        $psi = New-Object Diagnostics.ProcessStartInfo $venvPy
        $psi.Arguments = "-I `"$driver`""
        $psi.UseShellExecute = $false; $psi.RedirectStandardInput = $true; $psi.RedirectStandardOutput = $true; $psi.RedirectStandardError = $true
        $p = [Diagnostics.Process]::Start($psi); $pOut = $p.StandardOutput.ReadToEndAsync(); $null = $p.StandardError.ReadToEndAsync()
        if (-not $p.WaitForExit(90000)) { cmd /c "taskkill /T /F /PID $($p.Id) >nul 2>&1"; $cliLine = 'killed after 90 s' }
        else { $cliLine = @($pOut.Result -split '\r?\n' | Where-Object { $_ -like 'GKCLI*' })[-1] }
        $p.StandardInput.Close()
        Check "Blender MCP extension: run_blender_cli answers with stdin open (BLENDER_PATH $(if ($env:BLENDER_PATH) { 'set' } else { 'unset: blender on PATH' }))" ($cliLine -like "GKCLI {'ok': 1}*") "$cliLine (README.md, Blender steps 1 and 5)"
        Remove-Item -LiteralPath $driver -ErrorAction SilentlyContinue
    } else { Write-Host '  skip  run_blender_cli end to end: no extension .venv python or no Blender' }
} else { Write-Host '  skip  Blender MCP extension not installed' }
if ($cliBlend) { Remove-Item -LiteralPath $cliBlend -ErrorAction SilentlyContinue }
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

Section 'Template placeholders and pack merge (new-game.ps1 -NoSetup with its git step, every pack, no Unity)'
Check 'project/ carries __GAME__' ([bool](git grep -l '__GAME__' -- project | Select-Object -First 1))
# new-game.ps1's robocopy lets a pack file silently replace a project/ file or an earlier pack's: none may share a path
$owners = @{}
foreach ($f in @($tracked | Where-Object { $_ -like 'project/*' -or $_ -like 'packs/*' })) {
    $parts = $f -split '/'
    if ($parts[0] -eq 'project') { $rel = ($parts | Select-Object -Skip 1) -join '/'; $who = 'project' }
    else {
        if ($parts[1] -eq 'reference-docs' -or $parts.Count -lt 3 -or $parts[2] -in 'README.md', 'packages.json', 'examples') { continue }
        $rel = ($parts | Select-Object -Skip 2) -join '/'; $who = $parts[1]
    }
    $owners[$rel] = @($owners[$rel]) + $who | Where-Object { $_ }
}
$shared = @($owners.Keys | Where-Object { @($owners[$_]).Count -gt 1 } | Sort-Object | ForEach-Object { "$_ ($(@($owners[$_]) -join ', '))" })
Check 'no pack file overwrites a project/ file or another pack''s' (-not $shared) ($shared -join '; ')
# per run (PID): a parallel run would delete this one's game
$mergeRoot = Join-Path $env:TEMP "gk-test-all-packs-$PID"
if (Test-Path -LiteralPath $mergeRoot) { cmd /c rmdir /s /q "\\?\$mergeRoot" }
$allPacks = @(Get-ChildItem -LiteralPath packs -Directory | Where-Object Name -ne 'reference-docs' | ForEach-Object Name)
$mergeGame = Join-Path $mergeRoot 'PackMerge'
$dirtyProbe = Join-Path $PSScriptRoot 'packs\gk test-all dirty probe.txt'
try {
    # all packs at once: not a game anyone makes, but every packages.json merge and every placeholder runs. With the git
    # step (seconds without Unity), and an untracked probe with a space in its name under packs/ so the template is
    # dirty: porcelain quotes that path, which once split an inline commit message into pathspecs
    [IO.File]::WriteAllText($dirtyProbe, 'test-all.ps1 probe, deleted after the pack merge run')
    & (Join-Path $PSScriptRoot 'new-game.ps1') -Name PackMerge -Path $mergeRoot -Packs $allPacks -NoSetup -FeelFrom $mergeRoot 3>$null 6>$null | Out-Null
    Remove-Item -LiteralPath $dirtyProbe -ErrorAction SilentlyContinue
    $subject = git -C $mergeGame log -1 --format=%s
    $body = (git -C $mergeGame log -1 --format=%B) -join "`n"
    $yamlMerge = Join-Path (Split-Path (& (Join-Path $PSScriptRoot 'new-game.ps1') -ResolveUnity)) 'Data\Tools\UnityYAMLMerge.exe'
    $gitBad = @(
        if ($subject -notmatch '^Start PackMerge from unity-game-template@[0-9a-f]{7}-dirty$') { "subject '$subject' lacks the -dirty marker" }
        if ($body -notmatch "(?m)^Packs: $([regex]::Escape($allPacks -join ', '))$") { 'no Packs: line naming every pack' }
        if (-not $body.Contains('"packs/gk test-all dirty probe.txt"')) { 'the uncommitted-changes note lacks the quoted probe path' }
        if ((git -C $mergeGame config core.hooksPath) -ne '.githooks') { 'core.hooksPath is not .githooks' }
        if ((git -C $mergeGame ls-files -s .githooks/pre-commit) -notmatch '^100755 ') { '.githooks/pre-commit is not 100755 in the index' }
        if ((Test-Path -LiteralPath $yamlMerge) -and -not (git -C $mergeGame config merge.unityyamlmerge.driver)) { 'merge.unityyamlmerge.driver not set' }
    )
    Check 'new-game git step: start commit with -dirty, Packs: and the quoted dirty path, hooksPath, executable pre-commit, YAML merge driver' (-not $gitBad) ($gitBad -join '; ')
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
    # .git\ holds the start commit's message, whose dirty note names template paths with __GAME__ in them
    $left = @(Get-ChildItem -LiteralPath $mergeGame -Recurse -File -Force | Where-Object { $_.FullName -notlike "$mergeGame\.git\*" } |
        Where-Object { $_.Name -match '__GAME__|__COMPANY__' -or ($_.Length -lt 2MB -and [IO.File]::ReadAllText($_.FullName) -match '__GAME__|__COMPANY__') } |
        ForEach-Object { $_.FullName.Substring($mergeGame.Length + 1) })
    Check 'no __GAME__ / __COMPANY__ left in names or contents (new-game.ps1 text extensions cover every placeholder file)' (-not $left) ($left -join ', ')
    # the rest of the merge: each README's CLAUDE.md block under "## Packs", each ```markdown section (## Networking),
    # each pack assembly under Game\ in Game.asmdef's references
    $mergedClaude = [IO.File]::ReadAllText((Join-Path $mergeGame 'CLAUDE.md'))
    $mergedAsm = [IO.File]::ReadAllText((Join-Path $mergeGame 'Assets\PackMerge\Game\PackMerge.Game.asmdef'))
    $mergeBad = foreach ($pack in $allPacks) {
        $readme = [IO.File]::ReadAllText((Resolve-Path -LiteralPath "packs/$pack/README.md"))
        $blocks = @([regex]::Matches($readme, '(?ms)^## CLAUDE\.md''ye eklenecek sat\u0131r[ \t]*\r?$.*?^```[^\r\n]*\r?\n(.*?)\r?\n```') | ForEach-Object { $_.Groups[1].Value }) +
            @([regex]::Matches($readme, '(?ms)^```markdown\r?\n(## .*?)\r?\n```') | ForEach-Object { $_.Groups[1].Value })
        foreach ($b in $blocks) {
            $want = ($b -replace '\r\n', "`n").Replace('__GAME__', 'PackMerge').Replace('__COMPANY__', 'yunusburkut')
            if (-not $mergedClaude.Contains($want)) { "$pack CLAUDE.md block '$(($want -split "`n")[0])'" }
        }
        if ($blocks.Count -and $readme -match '(?m)^## CLAUDE\.md''ye eklenecek sat\u0131r' -and $mergedClaude -notmatch '(?m)^## Packs$') { "$pack CLAUDE.md has no ## Packs" }
        $packGame = "packs/$pack/Assets/__GAME__/Game"
        if (Test-Path -LiteralPath $packGame) {
            foreach ($asm in @(Get-ChildItem -LiteralPath $packGame -Recurse -Filter *.asmdef | ForEach-Object { $_.BaseName -replace '__GAME__', 'PackMerge' })) {
                if ($mergedAsm -notmatch ('"' + [regex]::Escape($asm) + '"')) { "$pack Game.asmdef lacks $asm" }
            }
        }
        # and the assemblies a pack's packages.json lists under gameReferences (coop-multiplayer's FishNet + UGS stack)
        $specPath = "packs/$pack/packages.json"
        if (Test-Path -LiteralPath $specPath) {
            foreach ($asm in @((Get-Content -LiteralPath $specPath -Raw | ConvertFrom-Json).gameReferences | Where-Object { $_ })) {
                if ($mergedAsm -notmatch ('"' + [regex]::Escape($asm) + '"')) { "$pack Game.asmdef lacks gameReferences $asm" }
            }
        }
    }
    Check 'merged CLAUDE.md holds every pack block and section, Game.asmdef references every pack assembly' (-not $mergeBad) ($mergeBad -join '; ')
} catch {
    Check 'new-game.ps1 -NoSetup with every pack' $false $_.Exception.Message
} finally {
    Remove-Item -LiteralPath $dirtyProbe -ErrorAction SilentlyContinue
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
