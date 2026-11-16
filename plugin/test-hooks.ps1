# Regression check for the gamekit plugin's hooks and reference indexes. Run after changing plugin/hooks/ or a
# skill's references: powershell -NoProfile -ExecutionPolicy Bypass -File plugin\test-hooks.ps1
# It pipes fixed payloads through every hook script (check-json, guard-unity-yaml with a held fake UnityLockfile,
# guard-readonly-agent, ensure-blender, route, self-check), runs gk-bridge against a fake AgentBridge, and checks that hooks.json and the
# scripts agree, so nothing here opens Blender or Unity. It also lints what the skills and agents point at (plugin
# paths, description budget, handoffs, facts restated from FrameLog, gk-bridge and Feel), runs refactor-pass's
# test-survey.sh, the global router's one-router test and a headless-Edge parse of workflows/feature.js; each of
# those skips with a note when its tool or source is absent. hooks.json is generated here (New-HooksJson below, from
# the extension lists in guard-unity-yaml.ps1 and check-json.ps1): after changing either list or a hook entry, run
# this script with -Write, then once more without it. ensure-blender's launch path runs against a stub exe (a short
# console flash). Not covered: Claude Code's own `if` matching (the generated rules follow the permissions doc: a bare
# `Edit(*.prefab)` is anchored at the session folder, `Edit(//**/*.prefab)` at the filesystem root) and the full
# feature.js run (its dispute helpers run). Unprobed: whether a Bash `if` such as `Bash(*.prefab*)` or `Bash(*>*)` sees
# a redirect target (`echo x > a.prefab`); guard-unity-yaml and guard-readonly-agent rely on it. A one-off probe needs
# a signed-in claude: a settings file whose PreToolUse Bash hooks `if: Bash(*.prefab*)` and `if: Bash(*>*)` each append
# a word to a log, then `claude -p "<run: echo x > t.prefab>" --settings <file> --allowedTools Bash`. If neither word
# is logged, give those hooks a plain `Bash` matcher with no `if` (the scripts filter on their own). Not run yet: the
# 2026-11 attempt had an expired sign-in. The payload fields the hooks read (agent_type, background_tasks[]) were
# checked against the Claude Code version named in self-check.ps1; a newer claude prints a WARN below.
# Exit 0 = all pass, 1 = a failure.
# Pure ASCII on purpose: Windows PowerShell 5.1 reads a BOM-less script as ANSI.
param([switch]$Write)
$ErrorActionPreference = 'Stop'
$hooks = Join-Path $PSScriptRoot 'hooks'
$template = Split-Path $PSScriptRoot
$tmp = Join-Path $env:TEMP ('gk-test-hooks-' + [guid]::NewGuid().ToString('N').Substring(0, 8))
New-Item -ItemType Directory -Path $tmp | Out-Null
$utf8 = New-Object Text.UTF8Encoding $false
$failed = 0

function Invoke-Hook($script, $payload, $cwd = $tmp, $envs = @{}) { return Wait-Hook (Start-Hook $script $payload $cwd $envs) }
function Start-Hook($script, $payload, $cwd = $tmp, $envs = @{}) {
    $psi = New-Object Diagnostics.ProcessStartInfo
    $psi.FileName = 'powershell.exe'
    $psi.Arguments = "-NoProfile -NonInteractive -ExecutionPolicy Bypass -File `"$(Join-Path $hooks $script)`""
    $psi.UseShellExecute = $false; $psi.RedirectStandardInput = $true
    $psi.RedirectStandardOutput = $true; $psi.RedirectStandardError = $true
    $psi.StandardOutputEncoding = [Text.Encoding]::UTF8
    $psi.WorkingDirectory = $cwd
    $psi.EnvironmentVariables['CLAUDE_PROJECT_DIR'] = $cwd
    foreach ($k in $envs.Keys) { $psi.EnvironmentVariables[$k] = $envs[$k] }
    $p = [Diagnostics.Process]::Start($psi)
    $bytes = $utf8.GetBytes($payload)
    $p.StandardInput.BaseStream.Write($bytes, 0, $bytes.Length); $p.StandardInput.Close()
    return @{ p = $p; out = $p.StandardOutput.ReadToEndAsync(); err = $p.StandardError.ReadToEndAsync() }
}
function Wait-Hook($h, $ms = 60000) {
    if (-not $h.p.WaitForExit($ms)) { $h.p.Kill(); return @{ code = -1; out = ''; err = 'timeout' } }
    return @{ code = $h.p.ExitCode; out = $h.out.Result.Trim(); err = $h.err.Result.Trim() }
}
function Check($name, $ok, $detail = '') {
    if ($ok) { Write-Output "PASS $name" } else { Write-Output "FAIL $name $detail"; $script:failed++ }
}
function Payload($obj) { return ($obj | ConvertTo-Json -Compress -Depth 5) }

# hooks.json, built from the scripts' own extension lists so the `if` rules cannot drift from them. Each `if` holds one
# rule, so every extension gets its own entry: that lets Claude Code skip starting PowerShell on unrelated calls.
# The path-judging hooks root their file rules (`//**/`) so a sibling game's file reaches them; the refresh one-liner
# keeps the session-relative form, because it queues the refresh in the session's own project only.
$refresh = 'd="${CLAUDE_PROJECT_DIR:-.}/Logs/agent"; [ -f "$d/bridge.log" ] && [ ! -s "$d/request.txt" ] && printf ''refresh\n'' > "$d/request.txt"; exit 0'
$blenderMatcher = 'mcp__Blender__(?!.*_docs$).*'
function New-HooksJson {
    $ps = { param($script, $timeout, $if) $h = [ordered]@{ type = 'command' }; if ($if) { $h.if = $if }
        $h.command = 'powershell.exe'
        $h.args = @('-NoProfile', '-NonInteractive', '-ExecutionPolicy', 'Bypass', '-File', "`${CLAUDE_PLUGIN_ROOT}/hooks/$script")
        $h.timeout = $timeout; $h }
    $extOf = { param($script, $pattern) [regex]::Match([IO.File]::ReadAllText((Join-Path $hooks $script)), $pattern).Groups[1].Value -split '\|' }
    $yamlExt = & $extOf 'guard-unity-yaml.ps1' '\$yaml = ''\\\.\(([^)]+)\)'
    $jsonExt = & $extOf 'check-json.ps1' "notmatch '\\\.\(([^)]+)\)\$'"
    if ($yamlExt.Count -lt 5 -or $jsonExt.Count -lt 2) { throw 'New-HooksJson: an extension list was not found in its script' }
    $guard = foreach ($t in 'Edit', 'Write') { foreach ($e in $yamlExt) { & $ps 'guard-unity-yaml.ps1' 15 "$t(//**/*.$e)" } }
    $guard = @($guard) + @(foreach ($t in 'Bash', 'PowerShell') { foreach ($e in $yamlExt) { & $ps 'guard-unity-yaml.ps1' 15 "$t(*.$e*)" } })
    $oneLiner = { param($if) [ordered]@{ type = 'command'; if = $if; shell = 'bash'; command = $refresh; timeout = 5 } }
    $post = @(foreach ($t in 'Bash', 'PowerShell') { foreach ($c in 'git rm *', 'git mv *') { & $oneLiner "$t($c)" } }) +
        @(foreach ($t in 'Edit', 'Write') { foreach ($e in '*.cs', '*.asm*') { & $oneLiner "$t($e)" } }) +
        @(foreach ($e in $jsonExt) { foreach ($t in 'Edit', 'Write') { & $ps 'check-json.ps1' 10 "$t(//**/*.$e)" } }) +
        @(foreach ($e in $jsonExt) { foreach ($t in 'Bash', 'PowerShell') { & $ps 'check-json.ps1' 10 "$t(*.$e*)" } })
    $doc = [ordered]@{ hooks = [ordered]@{
        # The docs tools (search_api_docs, get_python_api_docs, ...) need no Blender: the matcher keeps them out.
        PreToolUse = @([ordered]@{ matcher = $blenderMatcher; hooks = @(& $ps 'ensure-blender.ps1' 120) },
                       [ordered]@{ matcher = 'Edit|Write|Bash|PowerShell'; hooks = $guard },
                       [ordered]@{ matcher = 'Bash'; hooks = @(foreach ($c in '*git *', '*>*', '*tee *') { & $ps 'guard-readonly-agent.ps1' 10 "Bash($c)" }) })
        PostToolUse = @([ordered]@{ matcher = 'Edit|Write|Bash|PowerShell'; hooks = $post })
        Stop = @([ordered]@{ hooks = @(& $ps 'self-check.ps1' 60) })
        UserPromptSubmit = @([ordered]@{ hooks = @(& $ps 'route.ps1' 10) }) } }
    # PowerShell 5.1 escapes & ' < > as \u00XX and writes CRLF: undo both (see the template's CLAUDE.md).
    $json = ($doc | ConvertTo-Json -Depth 10) -replace '\\u0026', '&' -replace '\\u0027', "'" -replace '\\u003c', '<' -replace '\\u003e', '>'
    return ($json -replace "`r`n", "`n") + "`n"
}
$hooksJson = Join-Path $hooks 'hooks.json'
if ($Write) { [IO.File]::WriteAllText($hooksJson, (New-HooksJson), $utf8); Write-Output "Wrote $hooksJson" }

try {
    # --- check-json.ps1 -----------------------------------------------------------------------------------------
    $files = @{
        'valid.json'      = '{"a": [1, 2], "b": {"c": true}}'
        'comma.json'      = '{"a": 1,, "b": 2}'
        'empty.json'      = '   '
        'notjson.txt'     = '{ broken'
        'Library\x.json'  = '{ broken'
        "t$([char]0x011F)rk$([char]0x00E7)e\bozuk.json" = '{"a": [1, 2'
    }
    $big = '{"dependencies": {' + ((1..3000 | % { "`"com.example.p$_`": `"1.0.$_`"" }) -join ', ')   # final } lost
    $files['big.json'] = $big
    foreach ($k in $files.Keys) {
        $f = Join-Path $tmp $k; New-Item -ItemType Directory -Force -Path (Split-Path $f) | Out-Null
        [IO.File]::WriteAllText($f, $files[$k], $utf8)
    }
    $cj = { param($rel) Invoke-Hook 'check-json.ps1' (Payload @{ tool_name = 'Write'; tool_input = @{ file_path = (Join-Path $tmp $rel) }; cwd = $tmp }) }

    $r = & $cj 'valid.json';     Check 'check-json: valid file is silent' ($r.code -eq 0 -and -not $r.out) $r.out
    $r = & $cj 'comma.json';     Check 'check-json: double comma blocks' ($r.out -match '"decision":\s*"block"') $r.out
    $r = & $cj 'empty.json';     Check 'check-json: empty file blocks' ($r.out -match 'the file is empty') $r.out
    $r = & $cj 'notjson.txt';    Check 'check-json: other extension is silent' (-not $r.out) $r.out
    $r = & $cj 'Library\x.json'; Check 'check-json: Library\ is skipped' (-not $r.out) $r.out
    $r = & $cj 'missing.json';   Check 'check-json: missing file is silent' (-not $r.out) $r.out
    $r = & $cj "t$([char]0x011F)rk$([char]0x00E7)e\bozuk.json"
    Check 'check-json: Turkish path blocks' ($r.out -match '"decision":\s*"block"') $r.out
    $r = & $cj 'big.json'
    Check 'check-json: lost brace blocks' ($r.out -match '"decision":\s*"block"') $r.out.Substring(0, [Math]::Min(200, $r.out.Length))
    Check "check-json: lost brace reason stays short ($($r.out.Length) chars, file $($big.Length))" ($r.out.Length -lt 1000)
    $r = Invoke-Hook 'check-json.ps1' 'not json'; Check 'check-json: bad payload fails open' ($r.code -eq 0 -and -not $r.out)
    # JSONC editor configs are skipped; a shell write is checked through the files its command names.
    foreach ($k in '.vscode\settings.json', 'tsconfig.json') {
        $f = Join-Path $tmp $k; New-Item -ItemType Directory -Force -Path (Split-Path $f) | Out-Null
        [IO.File]::WriteAllText($f, "{ // comment`n `"a`": 1 }", $utf8)
        $r = & $cj $k; Check "check-json: JSONC $k is skipped" (-not $r.out) $r.out }
    $cjShell = { param($tool, $cmd) Invoke-Hook 'check-json.ps1' (Payload @{ tool_name = $tool; tool_input = @{ command = $cmd }; cwd = $tmp }) }
    $r = & $cjShell 'Bash' "cat > comma.json <<EOF`n{`"a`": 1,, `"b`": 2}`nEOF"
    Check 'check-json: a Bash heredoc into broken JSON blocks' ($r.out -match '"decision":\s*"block"' -and $r.out -match 'comma\.json') $r.out
    $r = & $cjShell 'Bash' 'cat comma.json'; Check 'check-json: a Bash read of broken JSON is silent' (-not $r.out) $r.out
    $r = & $cjShell 'PowerShell' "Get-Content valid.json | Set-Content `"$tmp\valid.json`""; Check 'check-json: a PowerShell write of valid JSON is silent' (-not $r.out) $r.out
    [IO.File]::WriteAllText((Join-Path $tmp 'utf16.json'), '{"a": 1}', [Text.Encoding]::Unicode)
    $r = & $cjShell 'PowerShell' '$m | ConvertTo-Json | Out-File utf16.json'
    Check 'check-json: a UTF-16 file from Out-File blocks' ($r.out -match '"decision":\s*"block"' -and $r.out -match 'UTF-16') $r.out
    # check-json and guard-unity-yaml share one write-verb heuristic.
    $verbOf = { param($s) [regex]::Match([IO.File]::ReadAllText((Join-Path $hooks $s)), "(?m)^\s*\`$verb = '([^']+)'").Groups[1].Value }
    Check 'check-json: its write-verb list equals guard-unity-yaml''s' ((& $verbOf 'check-json.ps1') -and (& $verbOf 'check-json.ps1') -ceq (& $verbOf 'guard-unity-yaml.ps1'))

    # --- guard-unity-yaml.ps1 ---------------------------------------------------------------------------------------
    # A running Editor is simulated by holding <project>\Temp\UnityLockfile open without sharing, as Unity does.
    $gp = Join-Path $tmp 'gproj'
    New-Item -ItemType Directory -Force -Path (Join-Path $gp 'ProjectSettings'), (Join-Path $gp 'Temp') | Out-Null
    [IO.File]::WriteAllText((Join-Path $gp 'ProjectSettings\ProjectVersion.txt'), 'm_EditorVersion: 6000.6.0f1', $utf8)
    $guard = { param($tool, $input_, $cwd = $gp)
        $ti = if ($tool -in 'Bash', 'PowerShell') { @{ command = $input_ } } else { @{ file_path = $input_ } }
        Invoke-Hook 'guard-unity-yaml.ps1' (Payload @{ tool_name = $tool; tool_input = $ti; cwd = $cwd }) $cwd }
    $denied = { param($r) $r.code -eq 0 -and $r.out -match '"permissionDecision":\s*"deny"' }
    $silent = { param($r) $r.code -eq 0 -and -not $r.out }
    New-Item -ItemType Directory -Force -Path (Join-Path $gp 'Assets') | Out-Null
    [IO.File]::WriteAllText((Join-Path $gp 'Assets\a.prefab'), "%YAML 1.1`n", $utf8)
    # A project folder with Turkish letters: the deny reason must reach Claude Code as UTF-8, not the OEM code page.
    $tp = Join-Path $tmp "oyun-$([char]0x011F)$([char]0x00FC)$([char]0x015F)"
    New-Item -ItemType Directory -Force -Path (Join-Path $tp 'ProjectSettings'), (Join-Path $tp 'Temp') | Out-Null
    [IO.File]::WriteAllText((Join-Path $tp 'ProjectSettings\ProjectVersion.txt'), 'm_EditorVersion: 6000.6.0f1', $utf8)
    $held = [IO.File]::Open((Join-Path $gp 'Temp\UnityLockfile'), 'OpenOrCreate', 'ReadWrite', 'None')
    $heldTr = [IO.File]::Open((Join-Path $tp 'Temp\UnityLockfile'), 'OpenOrCreate', 'ReadWrite', 'None')
    try {
        $r = & $guard 'Edit' (Join-Path $gp 'Assets\a.prefab')
        Check 'guard: Edit of a prefab under a live Editor is denied as an overwrite' ((& $denied $r) -and $r.out -match 'overwrites it on its next save') $r.out
        $r = & $guard 'Write' (Join-Path $gp 'Assets\New.mixer')
        Check 'guard: Write of a new mixer is denied with the fileID/GUID reason' ((& $denied $r) -and $r.out -match 'GUID' -and $r.out -notmatch 'overwrites') $r.out
        $r = & $guard 'Edit' (Join-Path $tp 'Assets\a.prefab') $tp
        Check 'guard: a Turkish project path survives in the deny reason' ((& $denied $r) -and $r.out.Contains($tp.Replace('\', '\\'))) $r.out
        $r = & $guard 'Edit' (Join-Path $gp 'Assets\a.prefab') $tmp
        Check 'guard: Edit in another session folder is judged by the owning project' (& $denied $r) $r.out
        $r = & $guard 'Bash' 'sed -i s/x/y/ Assets/a.prefab'; Check 'guard: sed -i on a prefab is denied' (& $denied $r) $r.out
        $r = & $guard 'Bash' 'echo x > Assets/a.prefab'; Check 'guard: redirect into a prefab is denied' (& $denied $r) $r.out
        $r = & $guard 'PowerShell' "Set-Content Assets\x.asset 'a'"; Check 'guard: Set-Content on an asset is denied' (& $denied $r) $r.out
        $r = & $guard 'Bash' "cp $($gp -replace '\\', '/')/Assets/a.prefab /c/scratch/b.prefab"
        Check 'guard: copy with an absolute in-project path is denied' (& $denied $r) $r.out
        foreach ($c in 'echo x > "Assets/My Scene.unity"', "printf x >> 'Assets/My Level.prefab'", '"x" | Out-File Assets\a.prefab',
                       'sc Assets\a.asset x', 'Rename-Item Assets\a.prefab b.prefab', 'ni Assets\b.mat', "cp `"$gp\Assets\My Scene.unity`" /c/scratch/b.unity") {
            $r = & $guard 'PowerShell' $c; Check "guard: '$c' is denied" (& $denied $r) $r.out }
        foreach ($c in 'Set-Content $env:TEMP\probe.asset x', 'cp ~/a.prefab ~/b.prefab', 'cp $NO_SUCH_GK_VAR/a.prefab b.txt') {
            $r = & $guard 'PowerShell' $c; Check "guard: '$c' outside the project is silent" (& $silent $r) $r.out }
        $r = & $guard 'Bash' 'cat Assets/a.prefab'; Check 'guard: reading a prefab is silent' (& $silent $r) $r.out
        $r = & $guard 'Bash' 'grep com.unity.pipeline Packages/manifest.json > out.txt'
        Check 'guard: a package id is not a .unity file' (& $silent $r) $r.out
        $r = & $guard 'Bash' 'cp /c/elsewhere/a.prefab /c/scratch/b.prefab'; Check 'guard: YAML outside every project is silent' (& $silent $r) $r.out
        $r = & $guard 'Edit' (Join-Path $tmp 'gproj-Backup\Assets\x.prefab'); Check 'guard: a sibling folder with the same prefix is silent' (& $silent $r) $r.out
    } finally { $held.Dispose(); $heldTr.Dispose() }
    $r = & $guard 'Edit' (Join-Path $gp 'Assets\a.prefab'); Check 'guard: a lockfile left by a crash is silent' (& $silent $r) $r.out
    $r = Invoke-Hook 'guard-unity-yaml.ps1' 'not json'; Check 'guard: bad payload is a non-blocking error' ($r.code -eq 1 -and -not $r.out)

    # --- guard-readonly-agent.ps1 ---------------------------------------------------------------------------------
    $ro = { param($cmd, $agent = 'gamekit:scout') $p = @{ tool_name = 'Bash'; tool_input = @{ command = $cmd }; cwd = $tmp }
        if ($agent) { $p.agent_type = $agent }; Invoke-Hook 'guard-readonly-agent.ps1' (Payload $p) }
    foreach ($c in 'git log --oneline -15 -- Assets', 'git stash list', 'git branch -a', 'git diff 2>&1 | head', 'grep -rl x Assets > /dev/null',
                   "git show HEAD > $($env:TEMP -replace '\\', '/')/d.txt") {
        $r = & $ro $c; Check "readonly-agent: scout may run '$c'" (& $silent $r) $r.out }
    foreach ($c in 'git stash', 'git -C . checkout -- a.cs', 'git --no-pager reset --hard', 'git commit -m x', 'git branch -D old', 'echo x > notes.txt', 'git diff | tee out.txt') {
        $r = & $ro $c; Check "readonly-agent: scout is denied '$c'" ((& $denied $r) -and $r.out -match 'read-only') $r.out }
    $r = & $ro 'git stash' 'bug-hunter'; Check 'readonly-agent: an unprefixed agent_type is judged too' (& $denied $r) $r.out
    $r = & $ro 'git commit -m x' 'gamekit:builder'; Check 'readonly-agent: the builder may commit' (& $silent $r) $r.out
    $r = & $ro 'git stash' ''; Check 'readonly-agent: the main session is untouched' (& $silent $r) $r.out
    $r = Invoke-Hook 'guard-readonly-agent.ps1' 'not json'; Check 'readonly-agent: bad payload fails open' (& $silent $r)
    # Every read-only agent (no Edit/Write in its tools) is in the script's list, and no writing agent is.
    $roList = [regex]::Match([IO.File]::ReadAllText((Join-Path $hooks 'guard-readonly-agent.ps1')), "agent -notmatch '.*?\)\?\(([a-z|-]+)\)\$'").Groups[1].Value -split '\|'
    $roWant = Get-ChildItem -LiteralPath (Join-Path $PSScriptRoot 'agents') -Filter *.md | Where-Object {
        $t = [regex]::Match([IO.File]::ReadAllText($_.FullName), '(?m)^tools:(.*)$').Groups[1].Value; $t -match '\bBash\b' -and $t -notmatch '\b(Edit|Write)\b' } | ForEach-Object BaseName
    $roDiff = Compare-Object @($roWant) @($roList) | ForEach-Object { "$($_.InputObject) $($_.SideIndicator)" }
    Check "readonly-agent: guards exactly the $(@($roWant).Count) agents with Bash and no Edit/Write" (@($roWant).Count -ge 5 -and -not $roDiff) ($roDiff -join ', ')

    # --- hooks.json agrees with the scripts ---------------------------------------------------------------------------
    $committed = [IO.File]::ReadAllText($hooksJson)
    Check 'hooks.json: equals the generated file (else run test-hooks.ps1 -Write)' ($committed -ceq (New-HooksJson))
    $hj = $committed | ConvertFrom-Json
    $wired = foreach ($ev in $hj.hooks.PSObject.Properties) { foreach ($g in $ev.Value) { foreach ($h in $g.hooks) {
        [pscustomobject]@{ If = [string]$h.if; Cmd = ((@($h.args) + $h.command) -join ' ') } } } }
    $scripts = $wired | ForEach-Object { [regex]::Matches($_.Cmd, '\$\{CLAUDE_PLUGIN_ROOT\}/(\S+)') } | ForEach-Object { $_.Groups[1].Value } | Sort-Object -Unique
    $absent = $scripts | Where-Object { -not (Test-Path -LiteralPath (Join-Path $PSScriptRoot $_)) }
    Check "hooks.json: all $(@($scripts).Count) referenced scripts exist" (@($scripts).Count -gt 0 -and -not $absent) ($absent -join ', ')
    # A bare file rule is anchored at the session folder (permissions doc), so the guards must stay rooted.
    $bare = $wired | Where-Object { $_.Cmd -match 'guard-unity-yaml|check-json' -and $_.If -match '^(Edit|Write)\((?!//\*\*/)' } | ForEach-Object If
    Check 'hooks.json: the guards'' Edit/Write rules are rooted (//**/), so a sibling game''s file reaches them' (-not $bare) ($bare -join ', ')
    # The fixed payloads above cannot notice Claude Code renaming a field the hooks read (agent_type in
    # guard-readonly-agent, background_tasks[] in self-check). A claude newer than the version self-check names is a
    # WARN, not a failure: re-check those fields against the hooks doc, then update the version there.
    $ccChecked = [regex]::Match([IO.File]::ReadAllText((Join-Path $hooks 'self-check.ps1')), 'checked against Claude Code (\d+\.\d+\.\d+)').Groups[1].Value
    $ccNow = try { [regex]::Match([string](& claude --version 2>$null), '\d+\.\d+\.\d+').Value } catch { '' }
    if (-not $ccChecked) { Check 'hook payload contract: self-check.ps1 names the Claude Code version it was checked against' $false }
    elseif (-not $ccNow) { Write-Output 'SKIP hook payload contract: no claude on PATH' }
    elseif ([version]$ccNow -gt [version]$ccChecked) { Write-Output "WARN hook payload contract: claude $ccNow is newer than $ccChecked; re-check agent_type and background_tasks[] (type, name, command)" }
    else { Write-Output "PASS hook payload contract: claude $ccNow is the checked version $ccChecked" }
    # The refresh one-liner, run as Claude Code runs it (bash, CLAUDE_PROJECT_DIR set).
    $bashExe = Join-Path $env:ProgramFiles 'Git\bin\bash.exe'
    if (Test-Path -LiteralPath $bashExe) {
        $rp = Join-Path $tmp 'refreshproj'; $rq = Join-Path $rp 'Logs\agent\request.txt'
        # From a file: PowerShell 5.1 does not escape the one-liner's inner double quotes in a `bash -c` argument.
        $refreshSh = Join-Path $tmp 'refresh.sh'; [IO.File]::WriteAllText($refreshSh, $refresh + "`n", $utf8)
        $runRefresh = { $was = $env:CLAUDE_PROJECT_DIR; $env:CLAUDE_PROJECT_DIR = $rp -replace '\\', '/'
            try { & $bashExe $refreshSh } finally { $env:CLAUDE_PROJECT_DIR = $was } }
        New-Item -ItemType Directory -Force -Path (Split-Path $rq) | Out-Null
        & $runRefresh; Check 'refresh one-liner: no bridge.log queues nothing' ($LASTEXITCODE -eq 0 -and -not (Test-Path -LiteralPath $rq))
        [IO.File]::WriteAllText((Join-Path $rp 'Logs\agent\bridge.log'), "READY`n", $utf8)
        & $runRefresh; Check 'refresh one-liner: with bridge.log it queues refresh' ($LASTEXITCODE -eq 0 -and (Test-Path -LiteralPath $rq) -and [IO.File]::ReadAllText($rq) -eq "refresh`n")
        [IO.File]::WriteAllText($rq, "build windows`n", $utf8)
        & $runRefresh; Check 'refresh one-liner: a pending request is kept' ([IO.File]::ReadAllText($rq) -eq "build windows`n")
    } else { Write-Output "SKIP refresh one-liner: no Git Bash at $bashExe" }

    # --- ensure-blender.ps1 (every path that never starts Blender) ---------------------------------------------------
    $la = Join-Path $tmp 'localappdata'   # stands in for %LOCALAPPDATA%, so the real extension never decides a result
    foreach ($t in 'mcp__Blender__execute_blender_code_for_cli', 'mcp__Blender__search_api_docs') {
        $sw = [Diagnostics.Stopwatch]::StartNew()
        $r = Invoke-Hook 'ensure-blender.ps1' (Payload @{ tool_name = $t; tool_input = @{} }) $tmp @{ LOCALAPPDATA = $la }
        Check "ensure-blender: $t passes" ($r.code -eq 0 -and $sw.Elapsed.TotalSeconds -lt 10) "exit $($r.code) $($r.err)"
    }
    $cliPy = Join-Path $la 'Claude-Data\p\Claude Extensions\ant.dir.gh.blender.blender-mcp\blmcp\tools_helpers\blender_cli.py'
    New-Item -ItemType Directory -Force -Path (Split-Path $cliPy) | Out-Null
    $cliTool = Payload @{ tool_name = 'mcp__Blender__execute_blender_code_for_cli'; tool_input = @{} }
    [IO.File]::WriteAllText($cliPy, "proc = subprocess.run(cmd,`n    stdin=subprocess.DEVNULL,`n    text=True)", $utf8)
    $r = Invoke-Hook 'ensure-blender.ps1' $cliTool $tmp @{ LOCALAPPDATA = $la }
    Check 'ensure-blender: *_for_cli passes with the stdin patch' ($r.code -eq 0) "exit $($r.code) $($r.err)"
    [IO.File]::WriteAllText($cliPy, "proc = subprocess.run(cmd,`n    text=True)", $utf8)
    $r = Invoke-Hook 'ensure-blender.ps1' $cliTool $tmp @{ LOCALAPPDATA = $la }
    Check 'ensure-blender: *_for_cli without the stdin patch blocks with the fix' ($r.code -eq 2 -and $r.err -match 'stdin=subprocess\.DEVNULL') "exit $($r.code) $($r.err)"
    [IO.File]::WriteAllText($cliPy, "from subprocess import DEVNULL`nproc = subprocess.run(cmd, stdin=DEVNULL, text=True)", $utf8)
    $r = Invoke-Hook 'ensure-blender.ps1' $cliTool $tmp @{ LOCALAPPDATA = $la }
    Check 'ensure-blender: an upstream fix spelled stdin=DEVNULL passes' ($r.code -eq 0) "exit $($r.code) $($r.err)"
    # Two profiles: the copy owned by the running blender-mcp.exe decides, not the newer file.
    [IO.File]::WriteAllText($cliPy, "proc = subprocess.run(cmd,`n    stdin=subprocess.DEVNULL,`n    text=True)", $utf8)
    [IO.File]::SetLastWriteTime($cliPy, (Get-Date).AddDays(-1))
    $cliPy2 = $cliPy -replace '\\p\\Claude Extensions', '\q\Claude Extensions'
    New-Item -ItemType Directory -Force -Path (Split-Path $cliPy2) | Out-Null
    [IO.File]::WriteAllText($cliPy2, "proc = subprocess.run(cmd,`n    text=True)", $utf8)
    $extRoot = { param($py) $py.Substring(0, $py.IndexOf('\blmcp\')) + '\blender-mcp.exe' }
    $r = Invoke-Hook 'ensure-blender.ps1' $cliTool $tmp @{ LOCALAPPDATA = $la; GK_BLENDER_MCP_LIVE = (& $extRoot $cliPy) }
    Check 'ensure-blender: the live profile''s patched copy wins over a newer unpatched one' ($r.code -eq 0) "exit $($r.code) $($r.err)"
    $r = Invoke-Hook 'ensure-blender.ps1' $cliTool $tmp @{ LOCALAPPDATA = $la; GK_BLENDER_MCP_LIVE = (& $extRoot $cliPy2) }
    Check 'ensure-blender: the live profile''s unpatched copy blocks' ($r.code -eq 2 -and $r.err.Contains($cliPy2)) "exit $($r.code) $($r.err)"
    $r = Invoke-Hook 'ensure-blender.ps1' $cliTool $tmp @{ LOCALAPPDATA = $la; GK_BLENDER_MCP_LIVE = 'none' }
    Check 'ensure-blender: with no server running the newest copy decides' ($r.code -eq 2 -and $r.err.Contains($cliPy2)) "exit $($r.code) $($r.err)"
    # The extension is there but blender_cli.py moved: pass, with a note instead of a silent blind pass.
    $la2 = Join-Path $tmp 'localappdata2'
    New-Item -ItemType Directory -Force -Path (Join-Path $la2 'Claude-Data\p\Claude Extensions\ant.dir.gh.blender.blender-mcp\blmcp') | Out-Null
    $r = Invoke-Hook 'ensure-blender.ps1' $cliTool $tmp @{ LOCALAPPDATA = $la2 }
    Check 'ensure-blender: a moved blender_cli.py passes with a note' ($r.code -eq 0 -and $r.out -match 'systemMessage' -and $r.out -match 'cannot be checked') "exit $($r.code) $($r.out)"
    # The matcher keeps the docs tools from starting the hook at all.
    $bm = ([IO.File]::ReadAllText($hooksJson) | ConvertFrom-Json).hooks.PreToolUse[0].matcher
    $bmWrong = @('search_api_docs', 'get_python_api_docs', 'search_manual_docs' | Where-Object { "mcp__Blender__$_" -match "^(?:$bm)$" }) +
        @('execute_blender_code', 'execute_blender_code_for_cli', 'get_objects_summary' | Where-Object { "mcp__Blender__$_" -notmatch "^(?:$bm)$" })
    Check "ensure-blender: the matcher '$bm' skips the docs tools and keeps the live ones" (-not $bmWrong) ($bmWrong -join ', ')
    $listener = New-Object Net.Sockets.TcpListener ([Net.IPAddress]::Loopback), 0
    $listener.Start()
    try {
        $sw = [Diagnostics.Stopwatch]::StartNew()
        $r = Invoke-Hook 'ensure-blender.ps1' (Payload @{ tool_name = 'mcp__Blender__get_objects_summary'; tool_input = @{} }) $tmp @{ BLENDER_MCP_PORT = [string]$listener.LocalEndpoint.Port }
        Check "ensure-blender: a listening server passes a live call at once ($([int]$sw.Elapsed.TotalSeconds) s)" ($r.code -eq 0 -and $sw.Elapsed.TotalSeconds -lt 8) "exit $($r.code) $($r.err)"
    } finally { $listener.Stop() }
    $r = Invoke-Hook 'ensure-blender.ps1' 'not json'; Check 'ensure-blender: bad payload fails open' ($r.code -eq 0)
    $live = Payload @{ tool_name = 'mcp__Blender__get_objects_summary'; tool_input = @{} }
    $r = Invoke-Hook 'ensure-blender.ps1' $live $tmp @{ BLENDER_MCP_PORT = 'abc' }
    Check 'ensure-blender: a malformed BLENDER_MCP_PORT blocks with the fix' ($r.code -eq 2 -and $r.err -match 'not a port number') "exit $($r.code) $($r.err)"
    # Add-on missing for the exe's version: blocks before Start-Process. Any versioned exe stands in for blender.exe and
    # an empty settings folder for %APPDATA%; a free port has no server. Skipped while a windowed Blender runs (that
    # branch answers first).
    if (-not @(Get-Process blender -ErrorAction SilentlyContinue | Where-Object MainWindowHandle -ne 0).Count) {
        $free = New-Object Net.Sockets.TcpListener ([Net.IPAddress]::Loopback), 0; $free.Start(); $freePort = $free.LocalEndpoint.Port; $free.Stop()
        $ad = Join-Path $tmp 'appdata'; New-Item -ItemType Directory -Force -Path (Join-Path $ad 'Blender Foundation\Blender') | Out-Null
        $sw = [Diagnostics.Stopwatch]::StartNew()
        $r = Invoke-Hook 'ensure-blender.ps1' $live $tmp @{ BLENDER_MCP_PORT = [string]$freePort; APPDATA = $ad; BLENDER_PATH = (Get-Command powershell.exe).Source }
        Check "ensure-blender: a Blender version without the add-on blocks before launch ($([int]$sw.Elapsed.TotalSeconds) s)" ($r.code -eq 2 -and $r.err -match 'not installed for Blender') "exit $($r.code) $($r.err)"
        # Launch path: a stub .bat stands in for blender.exe (no version info, so the add-on is looked up under 0.0,
        # in an id folder not named exactly mcp) and logs each start; the test opens the "server" once it has started.
        # Two calls at once: the mutex lets only one launch, and the other finds the server.
        $ad2 = Join-Path $tmp 'appdata2'; $addon = Join-Path $ad2 'Blender Foundation\Blender\0.0\extensions\lab\blender_mcp\__init__.py'
        New-Item -ItemType Directory -Force -Path (Split-Path $addon) | Out-Null; [IO.File]::WriteAllText($addon, '', $utf8)
        $stub = Join-Path $tmp 'stub blender.bat'; $launchLog = Join-Path $tmp 'launch.log'
        [IO.File]::WriteAllText($stub, "@echo %*>>`"$launchLog`"`r`n", (New-Object Text.ASCIIEncoding))
        $envs = @{ BLENDER_MCP_PORT = [string]$freePort; APPDATA = $ad2; BLENDER_PATH = $stub }
        $sw = [Diagnostics.Stopwatch]::StartNew()
        $h1 = Start-Hook 'ensure-blender.ps1' $live $tmp $envs; $h2 = Start-Hook 'ensure-blender.ps1' $live $tmp $envs
        while (-not (Test-Path -LiteralPath $launchLog) -and $sw.Elapsed.TotalSeconds -lt 40) { Start-Sleep -Milliseconds 200 }
        $server = New-Object Net.Sockets.TcpListener ([Net.IPAddress]::Loopback), $freePort
        $server.Start()
        try { $r1 = Wait-Hook $h1 110000; $r2 = Wait-Hook $h2 110000 } finally { $server.Stop() }
        $starts = @(if (Test-Path -LiteralPath $launchLog) { Get-Content -LiteralPath $launchLog })
        Check "ensure-blender: two parallel calls launch Blender once with --online-mode and both pass ($([int]$sw.Elapsed.TotalSeconds) s)" ($r1.code -eq 0 -and $r2.code -eq 0 -and $starts.Count -eq 1 -and $starts[0] -match '--online-mode') "exit $($r1.code)/$($r2.code), starts $($starts -join '|') $($r1.err) $($r2.err)"
    } else { Write-Output 'SKIP ensure-blender: add-on and launch checks (a windowed Blender is running)' }

    # --- self-check.ps1 (Stop) ------------------------------------------------------------------------------------
    # The '[' in the folder name catches a -Path where -LiteralPath is needed (PowerShell reads it as a wildcard).
    $sc = Join-Path $tmp 'sc[game]'; $scLog = Join-Path $sc 'Logs\agent'
    foreach ($d in $scLog, (Join-Path $sc 'Assets\Feel'), (Join-Path $sc 'Assets\Scripts'), (Join-Path $sc 'Temp')) { [void][IO.Directory]::CreateDirectory($d) }
    $stop = { param($extra = @{}) $p = @{ hook_event_name = 'Stop'; cwd = $sc }; foreach ($k in $extra.Keys) { $p[$k] = $extra[$k] }
        Invoke-Hook 'self-check.ps1' (Payload $p) $sc }
    $r = & $stop; Check 'self-check: no compile.log (no AgentBridge) is silent' ($r.code -eq 0 -and -not $r.out) $r.out
    [IO.File]::WriteAllText((Join-Path $scLog 'compile.log'), "2 error(s), 0 warning(s)`nAssets/A.cs(3,5): error CS1002: ; expected`n", $utf8)
    $r = & $stop; Check 'self-check: compile errors block the stop' ($r.out -match '"decision":\s*"block"' -and $r.out -match 'CS1002') $r.out
    $r = & $stop @{ stop_hook_active = $true }; Check 'self-check: the second stop passes' (-not $r.out) $r.out
    $r = & $stop @{ background_tasks = @(@{ id = '1'; type = 'workflow'; status = 'running'; description = ''; name = 'gamekit:feature' }) }
    Check 'self-check: a running feature workflow passes' (-not $r.out) $r.out
    $r = & $stop @{ background_tasks = @(@{ id = '1'; type = 'workflow'; status = 'running'; description = ''; name = 'gamekit:other' }) }
    Check 'self-check: another workflow keeps the check on' ($r.out -match '"decision":\s*"block"') $r.out
    $r = & $stop @{ background_tasks = @(@{ id = '1'; type = 'shell'; status = 'running'; description = ''; command = 'gk-bridge build android' }) }
    Check 'self-check: a background gk-bridge build passes' (-not $r.out) $r.out
    $r = & $stop @{ background_tasks = @(@{ id = '1'; type = 'shell'; status = 'running'; description = ''; command = 'gk-bridge run-tests' }) }
    Check 'self-check: a background gk-bridge run-tests passes' (-not $r.out) $r.out
    # Errors with a script edited since (Editor closed, no lockfile held): guidance that they may be stale, no block.
    [IO.File]::SetLastWriteTime((Join-Path $scLog 'compile.log'), (Get-Date).AddMinutes(-10))
    $scStale = Join-Path $sc 'Assets\Scripts\Fixed.cs'; [IO.File]::WriteAllText($scStale, 'class Fixed { }', $utf8)
    $r = & $stop; Check 'self-check: errors older than a script edit are guidance, not a block' ($r.out -notmatch '"decision":\s*"block"' -and $r.out -match 'additionalContext' -and $r.out -match 'may be stale') $r.out
    Remove-Item -LiteralPath $scStale
    [IO.File]::WriteAllText((Join-Path $scLog 'compile.log'), "OK  2026-01-01 00:00:00`n", $utf8)
    [IO.File]::WriteAllText((Join-Path $scLog 'bridge.log'), "REFRESHED  2026-01-01 00:00:00  compiled`n", $utf8)
    [IO.File]::WriteAllText((Join-Path $sc 'Assets\A.cs'), 'class A { }', $utf8)
    foreach ($n in 'compile.log', 'bridge.log') { [IO.File]::SetLastWriteTime((Join-Path $scLog $n), (Get-Date).AddMinutes(-10)) }
    $r = & $stop; Check 'self-check: a clean compile with the Editor closed is silent' (-not $r.out) $r.out
    [IO.File]::SetLastWriteTime((Join-Path $sc 'Assets\A.cs'), (Get-Date).AddMinutes(-20))
    [IO.File]::WriteAllText((Join-Path $sc 'Assets\Feel\F.cs'), 'class F { }', $utf8)
    $held = [IO.File]::Open((Join-Path $sc 'Temp\UnityLockfile'), 'OpenOrCreate', 'ReadWrite', 'None')
    try {
        $r = & $stop; Check 'self-check: a newer script under Assets\Feel is ignored' (-not $r.out) $r.out
        [IO.File]::WriteAllText((Join-Path $sc 'Assets\Scripts\B.cs'), 'class B { }', $utf8)
        $r = & $stop; Check 'self-check: a script newer than the compile sends Claude back once' ($r.out -match 'additionalContext' -and $r.out -match 'B\.cs') $r.out
        [IO.File]::WriteAllText((Join-Path $scLog 'bridge.log'), "REFRESHED  2026-01-01 00:00:00  no script changes`n", $utf8)
        $r = & $stop; Check 'self-check: a later "no script changes" refresh counts as fresh' (-not $r.out) $r.out
        # A pending request.txt holds the stop until the Editor takes it; a helper stands in, clearing it after 1 s.
        $scReq = Join-Path $scLog 'request.txt'; [IO.File]::WriteAllText($scReq, "refresh`n", $utf8)
        $taker = Start-Process powershell.exe -WindowStyle Hidden -PassThru -ArgumentList '-NoProfile', '-Command',
            "Start-Sleep 1; Remove-Item -LiteralPath '$($scReq.Replace("'", "''"))'"
        $sw = [Diagnostics.Stopwatch]::StartNew(); $r = & $stop; $waited = $sw.Elapsed.TotalSeconds; $taker.WaitForExit(10000) | Out-Null
        Check "self-check: a pending refresh is waited for, then the stop passes ($([Math]::Round($waited, 1)) s)" (-not $r.out -and $waited -ge 1 -and $waited -lt 30 -and -not (Test-Path -LiteralPath $scReq)) $r.out
        # A request nobody took for 10 s (a modal dialog): stop waiting and say so, never the full 45 s.
        [IO.File]::WriteAllText($scReq, "refresh`n", $utf8); [IO.File]::SetLastWriteTime($scReq, (Get-Date).AddSeconds(-20))
        $sw = [Diagnostics.Stopwatch]::StartNew(); $r = & $stop; $waited = $sw.Elapsed.TotalSeconds; Remove-Item -LiteralPath $scReq
        Check "self-check: an untaken refresh is reported, not waited for ($([Math]::Round($waited, 1)) s)" ($r.out -match 'has not taken' -and $waited -lt 15) $r.out
        # A REFRESHING line left by a crashed Editor (older than a minute) is not waited on.
        [IO.File]::WriteAllText((Join-Path $scLog 'bridge.log'), "REFRESHING  2026-01-01 00:00:00`n", $utf8)
        [IO.File]::SetLastWriteTime((Join-Path $scLog 'bridge.log'), (Get-Date).AddMinutes(-2))
        $sw = [Diagnostics.Stopwatch]::StartNew(); $r = & $stop; $waited = $sw.Elapsed.TotalSeconds
        Check "self-check: a stale REFRESHING line is not waited on ($([Math]::Round($waited, 1)) s)" ($waited -lt 10) $r.out
    } finally { $held.Dispose() }
    # A failed compile with no CS error line still names where the cause is.
    [IO.File]::WriteAllText((Join-Path $scLog 'compile.log'), "FAILED  2026-01-01 00:00:00  compile failed without a CS error: see console.log`n", $utf8)
    $r = & $stop; Check 'self-check: a FAILED compile without CS lines blocks and points at console.log' ($r.out -match '"decision":\s*"block"' -and $r.out -match 'before finishing:\\n[^"]*console\.log') $r.out
    $r = Invoke-Hook 'self-check.ps1' 'not json'; Check 'self-check: bad payload fails open' ($r.code -eq 0 -and -not $r.out)

    # --- gk-bridge against a fake AgentBridge ---------------------------------------------------------------------
    $bash = Join-Path $env:ProgramFiles 'Git\bin\bash.exe'
    if (Test-Path -LiteralPath $bash) {
        $gb = Join-Path $tmp 'gbgame'
        New-Item -ItemType Directory -Force -Path (Join-Path $gb 'ProjectSettings'), (Join-Path $gb 'Logs\agent'), (Join-Path $gb 'Assets'), (Join-Path $gb 'Packages') | Out-Null
        [IO.File]::WriteAllText((Join-Path $gb 'ProjectSettings\ProjectVersion.txt'), 'm_EditorVersion: 6000.6.0f1', $utf8)
        [IO.File]::WriteAllText((Join-Path $gb 'Assets\A.cs'), 'class A { }', $utf8)
        $driver = Join-Path $tmp 'gk-bridge-cases.sh'
        [IO.File]::WriteAllText($driver, @'
set -u
bridge=$1 root=$2 d=$2/Logs/agent
export GK_BRIDGE_ROOT=$root GK_BRIDGE_EDITOR_OK=1
at() { touch -d "@$(( $(date +%s) + $1 ))" "$2"; }   # set a file's time, seconds from now
reset() { rm -f "$d"/request.txt "$d"/bridge.log "$d"/compile-player.log "$d"/build.log "$d"/tests.log "$d"/capture.log "$root/Packages/manifest.json"
          printf 'OK  old\n' > "$d/compile.log"; at -300 "$d/compile.log"; at -600 "$root/Assets/A.cs"; }
# reply <log> <first line> [compile.log first line]: take request.txt and answer the way AgentBridge does
reply() { for _ in $(seq 100); do [ -e "$d/request.txt" ] && break; sleep 0.1; done
          sleep 0.3; [ -z "${3:-}" ] || printf '%s\n' "$3" > "$d/compile.log"
          rm -f "$d/request.txt"; printf '%s\n' "$2" > "$d/$1"; }
answer() { reply "$@" & }
run() { local name=$1 want=$2 out code; shift 2; out=$("$bridge" -t "${T:-12}" "$@" 2>&1); code=$?; wait
        if [ "$code" = "$want" ]; then echo "PASS gk-bridge: $name"; else echo "FAIL gk-bridge: $name (exit $code, want $want): $(printf '%s' "$out" | head -1)"; fi; }
reset; answer bridge.log 'REFRESHED  now  compiled' 'OK  now';                  run 'refresh OK passes' 0 refresh
reset; answer bridge.log 'REFRESHED  now  compiled' '2 error(s), 0 warning(s)'; run 'refresh with errors fails' 1 refresh
reset; at 60 "$root/Assets/A.cs"; answer bridge.log 'REFRESHED  now  compiled' 'OK  now'; run 'a script newer than the compile is unknown' 2 refresh
reset; answer bridge.log 'REFRESHED  now  no script changes';                   run 'no script changes passes' 0 refresh
reset; answer bridge.log 'SKIPPED  now  in Play Mode: refresh again after Play ends'; run 'Play Mode is unknown' 2 refresh
reset; answer bridge.log "Unknown request: 'compile ios'  now";                 run 'a request the bridge does not know is unknown' 2 compile ios
reset; answer compile-player.log 'OK  android  now';                            run 'compile android OK passes' 0 compile android
reset; answer compile-player.log 'FAILED  android  now';                        run 'compile android FAILED fails' 1 compile android
reset; answer compile-player.log 'OK  ios  now';                                run 'the other platform answering is unknown' 2 compile android
reset; answer compile-player.log 'UNSUPPORTED  android  the platform module is not installed'; run 'a missing module is unknown' 2 compile android
reset; answer compile-player.log 'OK  webgl  now';                              run 'compile webgl OK passes' 0 compile webgl
reset; answer compile-player.log "Unknown platform 'webgl'  now  use ios or android"; run 'an older GameKit without webgl is unknown' 2 compile webgl
out=$("$bridge" compile linux 2>&1); [ $? = 2 ] && printf '%s' "$out" | grep -q 'gk-bridge compile android' && echo 'PASS gk-bridge: compile linux prints usage' || echo "FAIL gk-bridge: compile linux prints usage: $(printf '%s' "$out" | head -1)"
# "no script changes" covers edits saved before the request only: one saved after it is unknown, even with a newer compile.log
reset; at 60 "$d/compile.log"; at 5 "$root/Assets/A.cs"; answer bridge.log 'REFRESHED  now  no script changes'; run 'a script saved after a no-script-changes request is unknown' 2 refresh
# run-tests: no bridge.log and no GameKit in the manifest, so this AgentBridge copy is asked without a refresh gate
reset; answer tests.log 'Passed  12 passed, 0 failed, 0 skipped';               run 'run-tests that passed passes' 0 run-tests
reset; answer tests.log 'Passed  0 passed, 0 failed, 0 skipped';                run 'run-tests with no test run is unknown' 2 run-tests
reset; answer tests.log 'Failed  0 passed, 2 failed, 0 skipped';                run 'run-tests with failures fails' 1 run-tests
reset; answer tests.log "Unknown request: 'run-tests'  now";                    run 'an old copy answering Unknown request in tests.log is unknown' 2 run-tests
# run-tests with GameKit in the manifest: a refresh gate first, then the tests
reset; printf '{"dependencies": {"com.yunusburkut.gamekit": "x"}}\n' > "$root/Packages/manifest.json"
( reply bridge.log 'REFRESHED  now  compiled' 'OK  now'; reply tests.log 'Passed  5 passed, 0 failed, 0 skipped' ) &
run 'gated run-tests passes after its refresh' 0 run-tests
reset; printf '{"dependencies": {"com.yunusburkut.gamekit": "x"}}\n' > "$root/Packages/manifest.json"
answer bridge.log 'REFRESHED  now  compiled' '1 error(s), 0 warning(s)';       run 'gated run-tests stops on a failed refresh' 1 run-tests
reset; answer capture.log 'OK  3 shots  now';                                   run 'play-capture OK passes' 0 play-capture
reset; answer capture.log 'ERRORS  3 shots  now';                               run 'play-capture with errors fails' 1 play-capture
reset; answer capture.log 'COMPILE FAILED  now  see compile.log';               run 'play-capture that cannot compile fails' 1 play-capture
reset; answer capture.log 'BUSY  already in Play Mode  now';                    run 'play-capture while playing is unknown' 2 play-capture
reset; answer capture.log 'FAILED  now  Editor restarted before the capture finished'; run 'a capture cut by a restart is unknown' 2 play-capture
reset; answer build.log 'Succeeded  windows  now';                              run 'build Succeeded passes' 0 build windows
reset; answer build.log 'Failed  windows  now';                                 run 'build Failed fails' 1 build windows
reset; answer build.log 'SKIPPED  now  in Play Mode: Unity cannot build while playing'; run 'build in Play Mode is unknown' 2 build windows
reset; answer build.log 'FAILED  now  Editor restarted before the build finished'; run 'a build cut by a restart is unknown' 2 build windows
reset; printf 'RUNNING editmode  now\n' > "$d/tests.log";                       run 'a fresh RUNNING test run holds a refresh' 2 refresh
reset; printf 'RUNNING editmode  now\n' > "$d/tests.log"; at -700 "$d/tests.log"; answer bridge.log 'REFRESHED  now  compiled' 'OK  now'; run 'a stale RUNNING line does not' 0 refresh
reset; printf 'PENDING  windows\n' > "$d/build.log";                           run 'a running build is unknown' 2 refresh
reset; printf 'refresh\n' > "$d/request.txt"; answer bridge.log 'REFRESHED  now  compiled' 'OK  now'; run 'joins the queued hook request' 0 refresh
reset; T=3 run 'a request nobody takes is unknown' 2 refresh
[ ! -e "$d/request.txt" ] && echo 'PASS gk-bridge: an untaken request is withdrawn' || echo 'FAIL gk-bridge: an untaken request is withdrawn'
run 'bad usage is unknown' 2 frobnicate
'@.Replace("`r`n", "`n"), $utf8)
        # Under EAP Stop, a stderr line from a native call with 2>&1 is a terminating error: Continue for this call.
        $ErrorActionPreference = 'Continue'
        $lines = & $bash $driver ((Join-Path $PSScriptRoot 'bin\gk-bridge') -replace '\\', '/') ($gb -replace '\\', '/') 2>&1
        $ErrorActionPreference = 'Stop'
        foreach ($l in $lines) {
            if ("$l" -match '^(PASS|FAIL) (.*)$') { Check $Matches[2] ($Matches[1] -eq 'PASS') } else { Check "gk-bridge: driver output" $false "$l" }
        }
    } else { Write-Output "SKIP gk-bridge: no Git Bash at $bash" }
    # The fixtures above are hand-typed: every status text gk-bridge matches must still be written by GameKit's
    # AgentBridge (AgentBridge.cs lists them). Ceiling: this checks the current GameKit only; games on an older
    # gamekit-vX.Y.Z tag keep the wording of their tag, so a rewording must stay readable for both.
    # build.log's Succeeded/Failed/Cancelled are BuildResult names (UnityEditor), so only the summary.result line is checked.
    $gk = Join-Path $template 'packages\com.yunusburkut.gamekit\Editor'
    $bridgeSrc = [IO.File]::ReadAllText((Join-Path $gk 'AgentBridge.cs')) + [IO.File]::ReadAllText((Join-Path $gk 'BuildMenu.cs'))
    $said = 'REFRESHED  ', 'REFRESHING', 'no script changes', 'in Play Mode', 'SKIPPED  ', 'Unknown request', 'OK  ', 'FAILED  ',
        'module is not installed', 'Editor restarted', ' passed, ', 'PENDING  ', 'RUNNING ', 'ERRORS', 'COMPILE FAILED', 'BUSY  ', 'summary.result'
    $unsaid = $said | Where-Object { $bridgeSrc.IndexOf($_, [StringComparison]::Ordinal) -lt 0 }
    Check "gk-bridge: all $($said.Count) status texts it reads are written by GameKit's AgentBridge" (-not $unsaid) ($unsaid -join ' | ')

    # --- route.ps1 ------------------------------------------------------------------------------------------------
    $game = Join-Path $tmp 'game'; New-Item -ItemType Directory -Force -Path (Join-Path $game 'ProjectSettings') | Out-Null
    [IO.File]::WriteAllText((Join-Path $game 'ProjectSettings\ProjectVersion.txt'), 'm_EditorVersion: 6000.6.0f1', $utf8)
    $route = { param($prompt, $cwd, $sid = '') Invoke-Hook 'route.ps1' (Payload @{ prompt = $prompt; cwd = $cwd; session_id = $sid }) $cwd }
    $r = & $route 'muzik ekle' $game;  Check 'route: new task in a Unity project prints the router' ($r.out -match 'task router')
    Check 'route: router names the prototype route' ($r.out -match 'gamekit:prototype')
    Check 'route: a prompt without "devam" skips the devam rule' ($r.out -notmatch '"devam": after') $r.out
    $r = & $route 'devam' $game;       Check 'route: "devam" prints the devam rule' ($r.out -match '"devam": after') $r.out
    foreach ($k in 'simdi devam et', 'tamam devam', 'evet devam') {
        $r = & $route $k $game; Check "route: `"$k`" prints the devam rule" ($r.out -match '"devam": after') $r.out }
    $sid = 'gktest-' + [guid]::NewGuid().ToString('N').Substring(0, 8)   # $game has no compile.log, GameKit or bridge copy
    try {
        $r = & $route 'muzik ekle' $game $sid; Check 'route: the no-AgentBridge note prints on the first prompt' ($r.out -match 'no AgentBridge') $r.out
        $r = & $route 'ses ekle' $game $sid;   Check 'route: the no-AgentBridge note prints once per session' ($r.out -match 'task router' -and $r.out -notmatch 'no AgentBridge') $r.out
    } finally { Remove-Item -LiteralPath (Join-Path ([IO.Path]::GetTempPath()) "gamekit-route-$sid.bridge") -Force -ErrorAction SilentlyContinue }
    # The full router prints once per session, a short reminder after it, and the full text again after a compaction.
    $sid = 'gktest-' + [guid]::NewGuid().ToString('N').Substring(0, 8); $trf = Join-Path $tmp 'transcript.jsonl'
    [IO.File]::WriteAllText($trf, "{`"type`":`"user`"}`n", $utf8)
    $routeTr = { param($prompt) Invoke-Hook 'route.ps1' (Payload @{ prompt = $prompt; cwd = $game; session_id = $sid; transcript_path = $trf }) $game }
    try {
        $r = & $routeTr 'muzik ekle'; Check 'route: the first prompt of a session gets the full router' ($r.out -match 'the user asked for it') $r.out
        [IO.File]::AppendAllText($trf, "{`"type`":`"assistant`"}`n", $utf8)
        $r = & $routeTr 'ses ekle'; Check 'route: a later prompt gets the short reminder' ($r.out -match 'task router' -and $r.out -match 'still hold' -and $r.out -notmatch 'the user asked for it') $r.out
        [IO.File]::AppendAllText($trf, "{`"type`":`"system`",`"subtype`":`"compact_boundary`"}`n", $utf8)
        $r = & $routeTr 'isik ekle'; Check 'route: a compaction brings the full router back' ($r.out -match 'the user asked for it') $r.out
    } finally { foreach ($x in 'router', 'bridge') { Remove-Item -LiteralPath (Join-Path ([IO.Path]::GetTempPath()) "gamekit-route-$sid.$x") -Force -ErrorAction SilentlyContinue } }
    foreach ($k in @(@('kabul', '"kabul": once'), @('karti next''e tasi', 'Next''e tasi'), @('review et', '"review et" / "puanla"'), @('puanla', '"review et" / "puanla"'))) {
        $r = & $route $k[0] $game; Check "route: `"$($k[0])`" prints its rule" ($r.out.Contains($k[1])) $r.out }
    $r = & $route 'zipla ekle' $game; Check 'route: a prompt without a keyword prints no keyword rule' ($r.out -notmatch '"kabul"|Next''e tasi|"review et"') $r.out
    # The keyword patterns are anchored: game words that contain them print no rule.
    foreach ($k in 'devam eden hareket ekle', 'tamam devam eden hareket', 'NextLevel butonu ekle', 'oyuna puan tablosu ekle') {
        $r = & $route $k $game; Check "route: `"$k`" prints no keyword rule" ($r.out -match 'task router' -and $r.out -notmatch '"devam": after|"kabul": once|Next''e tasi|"review et"') $r.out }
    $r = & $route 'store sayfasini review et' $game
    Check 'route: a critique review goes to its agent without phase 6' ($r.out.Contains('gamekit:launch-auditor') -and $r.out.Contains('no phase 6')) $r.out
    Check 'route: a game without the co-op pack gets no co-op note' ($r.out -notmatch 'coop-chaos-design') $r.out
    $coop = Join-Path $tmp 'coopgame'; New-Item -ItemType Directory -Force -Path (Join-Path $coop 'ProjectSettings'), (Join-Path $coop '.claude\skills\coop-chaos-design') | Out-Null
    [IO.File]::WriteAllText((Join-Path $coop 'ProjectSettings\ProjectVersion.txt'), 'm_EditorVersion: 6000.6.0f1', $utf8)
    [IO.File]::WriteAllText((Join-Path $coop '.claude\skills\coop-chaos-design\SKILL.md'), "---`nname: coop-chaos-design`n---`n", $utf8)
    $r = & $route 'zipla ekle' $coop; Check 'route: a co-op game gets the coop-chaos-design note' ($r.out -match 'coop-chaos-design skill first') $r.out
    # The skip rules (slash, notifications, replies) are kept equal to the global router's on purpose (route.ps1 header).
    $ep = Join-Path $HOME '.claude\hooks\enhance-prompt.ps1'
    if (Test-Path -LiteralPath $ep) {
        $skipOf = { param($f) [regex]::Matches([IO.File]::ReadAllText($f), "-match '(<task-notification>[^']*|\^\(evet[^']*)'") | ForEach-Object { $_.Groups[1].Value } }
        $a = @(& $skipOf (Join-Path $hooks 'route.ps1')); $b = @(& $skipOf $ep)
        Check 'route: skip rules equal the global router''s' ($a.Count -eq 2 -and ($a -join "`n") -ceq ($b -join "`n")) "route: $($a -join ' / ') | global: $($b -join ' / ')"
    } else { Write-Output "SKIP route skip rules: no $ep" }
    $r = & $route 'evet' $game;        Check 'route: plain reply is silent' (-not $r.out) $r.out
    $r = & $route '/gamekit:feature' $game; Check 'route: slash command is silent' (-not $r.out) $r.out
    $r = & $route 'muzik ekle' $tmp;   Check 'route: non-Unity folder is silent' (-not $r.out) $r.out
    $named = Select-String -LiteralPath (Join-Path $hooks 'route.ps1') -Pattern 'gamekit:([a-z][a-z0-9-]*)' -AllMatches |
        ForEach-Object { $_.Matches } | ForEach-Object { $_.Groups[1].Value } | Sort-Object -Unique
    $dangling = $named | Where-Object { -not (Test-Path -LiteralPath (Join-Path $PSScriptRoot "skills\$_\SKILL.md")) -and
        -not (Test-Path -LiteralPath (Join-Path $PSScriptRoot "agents\$_.md")) -and
        -not (Test-Path -LiteralPath (Join-Path $PSScriptRoot "workflows\$_.js")) }
    Check "route: all $(@($named).Count) gamekit: names resolve to a skill, agent or workflow" (@($named).Count -gt 0 -and -not $dangling) ($dangling -join ', ')
    # The global router exits where route.ps1 prints; its own test checks that exactly one of the two prints.
    $ue = Join-Path $HOME '.claude\hooks\test-enhance-prompt.ps1'
    if (Test-Path -LiteralPath $ue) {
        $o = & powershell -NoProfile -ExecutionPolicy Bypass -File $ue -Route (Join-Path $hooks 'route.ps1')
        Check 'route + global router: exactly one prints' ($LASTEXITCODE -eq 0) (($o | Select-String '^FAIL') -join '; ')
    } else { Write-Output "SKIP route + global router: no $ue" }

    # --- genre-defaults indexes -----------------------------------------------------------------------------------
    $gd = Join-Path $PSScriptRoot 'skills\genre-defaults'
    $listed = Select-String -LiteralPath (Join-Path $gd 'SKILL.md') -Pattern '^- `([a-z0-9-]+)`:' |
        ForEach-Object { $_.Matches[0].Groups[1].Value }
    $missing = $listed | Where-Object { -not (Test-Path -LiteralPath (Join-Path $gd "references\$_.md")) }
    Check "genre-defaults: all $($listed.Count) indexed sheets exist" ($listed.Count -gt 0 -and -not $missing) ($missing -join ', ')
    $refs = Join-Path $gd 'references'
    # The other way too: SKILL.md matches genres only from its list, so an unlisted sheet is never used.
    $support = 'art-directions', 'mashups', 'online', 'sources'
    $sheets = Get-ChildItem -LiteralPath $refs -Filter *.md | ForEach-Object { $_.BaseName } | Where-Object { $_ -notin $support }
    $unlisted = $sheets | Where-Object { $_ -notin $listed }
    Check "genre-defaults: all $(@($sheets).Count) sheets are indexed" (-not $unlisted) ($unlisted -join ', ')
    # The mashup and Platforms steps read these sections from every sheet.
    $sections = 'Defaults', 'Feel', 'Variants', 'Choices that shape the pitch', 'Platforms', 'Later', 'In a mashup'
    $incomplete = $sheets | Where-Object {
        $heads = Select-String -LiteralPath (Join-Path $refs "$_.md") -Pattern '^## (.+?)\s*$' | ForEach-Object { $_.Matches[0].Groups[1].Value }
        @($sections | Where-Object { $_ -notin $heads }).Count -or
            -not (Select-String -LiteralPath (Join-Path $refs "$_.md") -Pattern '^\*\*Camera \(Unity\):\*\*' -Quiet) }
    Check "genre-defaults: every sheet has Camera and the $($sections.Count) sections" (-not $incomplete) ($incomplete -join ', ')
    $used = Get-ChildItem -LiteralPath $refs -Filter *.md | Where-Object Name -ne 'sources.md' |
        Select-String -Pattern '\[([a-z0-9]+(?:-[a-z0-9]+)*-\d+)\]' -AllMatches |
        ForEach-Object { $_.Matches } | ForEach-Object { $_.Groups[1].Value } | Sort-Object -Unique
    $defined = Select-String -LiteralPath (Join-Path $refs 'sources.md') -Pattern '^- \*\*\[([^\]]+)\]\*\*' |
        ForEach-Object { $_.Matches[0].Groups[1].Value }
    $unresolved = $used | Where-Object { $_ -notin $defined }
    Check "genre-defaults: all $($used.Count) source keys resolve" ($used.Count -gt 0 -and -not $unresolved) ($unresolved -join ', ')
    $uncited = $defined | Where-Object { $_ -notin $used }
    Check "genre-defaults: all $(@($defined).Count) sources are cited" (-not $uncited) ($uncited -join ', ')
    # art-directions.md's Sheets column names every sheet exactly once, so a new sheet cannot ship without a Look row.
    $artKeys = Select-String -LiteralPath (Join-Path $refs 'art-directions.md') -Pattern '^\| [^|]+ \| (.+?) \| ' | ForEach-Object {
        [regex]::Matches($_.Matches[0].Groups[1].Value, '`([a-z0-9-]+)`') | ForEach-Object { $_.Groups[1].Value } }
    $noLook = @($sheets | Where-Object { $_ -notin $artKeys }) + @($artKeys | Where-Object { $_ -notin $sheets })
    Check "genre-defaults: every sheet has one art-directions row" (@($artKeys).Count -and -not $noLook -and @($artKeys).Count -eq @($artKeys | Sort-Object -Unique).Count) ($noLook -join ', ')
    # art-directions.md routes each look to a Blender style skill: one installed or kept in the spares.
    $spares = Join-Path $HOME '.claude\spares\blender-skills'
    if (Test-Path -LiteralPath $spares) {
        $styles = Select-String -LiteralPath (Join-Path $refs 'art-directions.md') -Pattern '`([a-z0-9-]+-style)`' -AllMatches |
            ForEach-Object { $_.Matches } | ForEach-Object { $_.Groups[1].Value } | Sort-Object -Unique
        $noStyle = $styles | Where-Object { -not (Test-Path -LiteralPath (Join-Path $spares $_)) -and -not (Test-Path -LiteralPath (Join-Path $HOME ".claude\skills\$_")) }
        Check "genre-defaults: all $(@($styles).Count) style skills art-directions names exist" (@($styles).Count -and -not $noStyle) ($noStyle -join ', ')
    } else { Write-Output "SKIP genre-defaults style skills: no $spares" }
    Check 'genre-defaults: LICENSE.md carries the MIT text' (Select-String -LiteralPath (Join-Path $gd 'LICENSE.md') -Pattern 'Permission is hereby granted' -Quiet)

    # --- level-beat-review: the DR catalogue's IDs are stable (design-critic and the coop pack cite them) ----------
    $lbr = Join-Path $PSScriptRoot 'skills\level-beat-review'
    $dr = [IO.File]::ReadAllText((Join-Path $lbr 'references\difficulty-rhythm.md'))
    $ids = @([regex]::Matches($dr, '(?m)^\| DR(\d\d) \|') | ForEach-Object { [int]$_.Groups[1].Value })
    $drHead = [regex]::Match($dr, '(?m)^## B\. DR rules \((\d+)\)')
    $drGap = @(for ($i = 1; $i -le $ids.Count; $i++) { if ($ids[$i - 1] -ne $i) { 'DR{0:00} at row {1}' -f $ids[$i - 1], $i; break } })
    if (-not $drHead.Success -or [int]$drHead.Groups[1].Value -ne $ids.Count) { $drGap += "B header $($drHead.Groups[1].Value) rows $($ids.Count)" }
    # Source keys: every [Key, Key2] list before section D must be a row of D's Key table.
    $drParts = $dr -split '(?m)^## D\. '
    $drKeys = @([regex]::Matches($drParts[1], '(?m)^\| ([A-Z][A-Za-z]+\d{0,2}) \|') | ForEach-Object { $_.Groups[1].Value })
    $drCited = [regex]::Matches(($drParts[0] -replace '\r?\n\s*', ' '), '\[([^\]]+)\](?!\()') | ForEach-Object {
        $p = $_.Groups[1].Value -split '\s*[,;]\s*'; if (-not @($p | Where-Object { $_ -notmatch '^[A-Z][A-Za-z]+\d{0,2}$' }).Count) { $p } } | Sort-Object -Unique
    $drUnres = @($drCited | Where-Object { $_ -notin $drKeys }) + @(
        [regex]::Matches([IO.File]::ReadAllText((Join-Path $lbr 'SKILL.md')), 'DR(\d\d)') | ForEach-Object { [int]$_.Groups[1].Value } |
            Where-Object { $_ -notin $ids } | ForEach-Object { 'SKILL.md DR{0:00}' -f $_ })
    Check "level-beat-review: DR01-DR$($ids.Count) contiguous, $(@($drCited).Count) source keys resolve, SKILL DR refs exist" ($ids.Count -ge 28 -and @($drCited).Count -ge 3 -and -not $drGap -and -not $drUnres) ((@($drGap) + @($drUnres)) -join ', ')
    # Numbers repeated across files: each copy must read the owner's value (the owner comes first in each list).
    $txt = @{ skill = (Join-Path $lbr 'SKILL.md'); dr = (Join-Path $lbr 'references\difficulty-rhythm.md')
              critic = (Join-Path $PSScriptRoot 'agents\design-critic.md'); feel = (Join-Path $PSScriptRoot 'skills\game-feel\references\numbers.md') }
    foreach ($k in @($txt.Keys)) { $txt[$k] = [IO.File]::ReadAllText($txt[$k]) }
    $nd = '\u2013'   # the en dash the docs write in ranges
    $shared = [ordered]@{
        'reaction floor ms' = @(@('feel', 'Full perceive \u2192 act loop \| ~(\d+) ms'), @('feel', 'Broken \| > (\d+) ms'), @('feel', 'must exceed the (\d+) ms'),
                                @('skill', 'Reaction floor for any window \| \*\*(\d+) ms'), @('skill', 'Telegraph for a hazard \| > (\d+) ms'),
                                @('dr', 'Telegraph > (\d+) ms'), @('critic', '(\d+) ms reaction floor'))
        'recovery range s'  = @(@('skill', "next decision within \d+ s \*\(start\)\*: (\d+$nd\d+) s"), @('feel', "mistake \u2192 next decision \| (\d+$nd\d+) s"),
                                @('critic', "recovery within \d+ s \((\d+$nd\d+) s"))
        'recovery cap s'    = @(@('skill', 'next decision within (\d+) s'), @('skill', "\*\(start\)\*: \d+$nd(\d+) s for an in-world"), @('critic', 'recovery within (\d+) s'))
        'replay to peak s'  = @(@('skill', 'replay to the peak \u2264 (\d+) s'), @('dr', 'to the peak \u2264 (\d+) s'), @('dr', 'T2 \| Tier 2: back to the checkpoint, \u2264 (\d+) s'),
                                @('dr', 'with more than (\d+) s replay'))
        'segment cap s'     = @(@('skill', "checkpoint to checkpoint\) \| \d+$nd(\d+) s"), @('skill', 'over (\d+) s players stop'), @('skill', 'The (\d+) s segment cap'),
                                @('skill', 'Segment over (\d+) s'))
    }
    $numBad = foreach ($n in $shared.Keys) {
        $vals = foreach ($c in $shared[$n]) { $m = [regex]::Match($txt[$c[0]], $c[1]); if ($m.Success) { $m.Groups[1].Value } else { "missing in $($c[0]): $($c[1])" } }
        if (@($vals | Sort-Object -Unique).Count -ne 1) { "$n -> $($vals -join ' / ')" } }
    Check "level-beat-review: $($shared.Count) numbers shared with game-feel and design-critic agree in every copy" (-not $numBad) ($numBad -join '; ')

    # --- pipeline section pointers: "pipeline 6.4", "`gamekit:pipeline` 4 Build, item 3", "phase 7" ---------------
    $pl = [IO.File]::ReadAllText((Join-Path $PSScriptRoot 'skills\pipeline\SKILL.md'))
    $plItems = @{}
    foreach ($s in [regex]::Matches($pl, '(?ms)^## (\d+) [^\r\n]*(.*?)(?=^## |\z)')) {
        $plItems[[int]$s.Groups[1].Value] = [regex]::Matches($s.Groups[2].Value, '(?m)^\d+\. ').Count }
    $plDocs = @(Get-ChildItem -LiteralPath (Join-Path $PSScriptRoot 'agents'), (Join-Path $PSScriptRoot 'skills') -Filter *.md -Recurse | Where-Object FullName -notmatch '\\skills\\pipeline\\SKILL\.md$') +
        @(Get-ChildItem -LiteralPath (Join-Path $PSScriptRoot 'workflows') -Filter *.js) + @(Get-ChildItem -LiteralPath $hooks -Filter *.ps1)
    $plRefs = $plDocs | Select-String -Pattern '(?<![.\w])(?:gamekit:pipeline`?|pipeline)(?: phase)? (\d+)(?:\.(\d+)(?:-\d+\.(\d+))?| [A-Z]\w+, item (\d+))?(?!\d|\.\d)|\bphase (\d+)(?:\.(\d+))?\b' -AllMatches |
        ForEach-Object { $at = "$(Split-Path -Leaf $_.Path):$($_.LineNumber)"; foreach ($m in $_.Matches) {
            $n = if ($m.Groups[1].Success) { [int]$m.Groups[1].Value } else { [int]$m.Groups[5].Value }
            $item = (@(2, 3, 4, 6) | ForEach-Object { $m.Groups[$_] } | Where-Object Success | Select-Object -Last 1)
            [pscustomobject]@{ N = $n; Item = $(if ($item) { [int]$item.Value } else { 0 }); At = "$($m.Value) ($at)" } } }
    $plBad = $plRefs | Where-Object { -not $plItems.ContainsKey($_.N) -or $plItems[$_.N] -lt $_.Item } | ForEach-Object At
    Check "pipeline: all $(@($plRefs).Count) section and item pointers name an existing '## <n>' section and item" (@($plRefs).Count -ge 10 -and -not $plBad) ($plBad -join ', ')

    # --- skills and agents: plugin paths, descriptions, handoffs ----------------------------------------------------
    $docs = @(Get-ChildItem -LiteralPath (Join-Path $PSScriptRoot 'agents') -Filter *.md) +
        @(Get-ChildItem -LiteralPath (Join-Path $PSScriptRoot 'skills') -Filter SKILL.md -Recurse)
    $allMd = @(Get-ChildItem -LiteralPath (Join-Path $PSScriptRoot 'agents'), (Join-Path $PSScriptRoot 'skills') -Filter *.md -Recurse)
    $rootRefs = $allMd + @(Get-ChildItem -LiteralPath (Join-Path $PSScriptRoot 'workflows') -Filter *.js) |
        Select-String -Pattern '\$\{CLAUDE_PLUGIN_ROOT\}/([^\s`"''()<>]+)' -AllMatches |
        ForEach-Object { $_.Matches } | ForEach-Object { $_.Groups[1].Value.TrimEnd('.', ',', ';', ':') } | Sort-Object -Unique
    $absent = $rootRefs | Where-Object { -not (Test-Path -LiteralPath (Join-Path $PSScriptRoot $_)) }
    Check "plugin: all $(@($rootRefs).Count) `${CLAUDE_PLUGIN_ROOT} paths exist" (@($rootRefs).Count -gt 0 -and -not $absent) ($absent -join ', ')
    # The skill listing shares one budget, 1% of the context window (about 8,000 characters at 200k tokens), with every
    # user, account and plugin skill. When it overflows, Claude Code drops whole descriptions, least-invoked skills
    # first, so a gamekit skill can lose its triggers while each description is short. 250 characters per description
    # keeps the cost even; the total below is a ratchet: grow it only by trimming another gamekit description. Rarely
    # auto-needed reference skills can be listed name-only through skillOverrides in settings.
    # Evidence (2026-11 review, kept here as the one place for it): at about 6000 gamekit characters a session showed
    # 11 gamekit skills as names only. So the ratchet is not a safe size: it only stops growth at today's total (6,020,
    # plus a little slack). Ceiling: on this machine's skill set the listing still overflows; the way down is trimming
    # gamekit descriptions (trigger first, examples in the body) and turning unused account/plugin skills to name-only
    # or off with skillOverrides, then lowering this number to the new total.
    $descTotal = 0
    $long = foreach ($d in $docs) {
        $fm = [regex]::Match([IO.File]::ReadAllText($d.FullName), '(?s)\A---\r?\n(.*?)\r?\n---')
        $m = [regex]::Match($fm.Groups[1].Value, '(?m)^description:[ \t]*(.*)$')
        if ($d.Name -eq 'SKILL.md') { $descTotal += $m.Groups[1].Value.Trim().Trim('"', "'").Length }
        if (-not $m.Success) { "$($d.Directory.Name)/$($d.Name) (none)" }
        elseif ($m.Groups[1].Value.Trim().Trim('"', "'").Length -gt 250) { "$($d.Directory.Name)/$($d.Name) ($($m.Groups[1].Value.Trim().Length))" }
    }
    Check "plugin: all $($docs.Count) skill and agent descriptions are set and at most 250 characters" (-not $long) ($long -join ', ')
    $userDesc = 0
    foreach ($f in Get-ChildItem -LiteralPath (Join-Path $HOME '.claude\skills') -Filter SKILL.md -Recurse -ErrorAction SilentlyContinue) {
        $um = [regex]::Match([IO.File]::ReadAllText($f.FullName), '(?m)^description:[ \t]*(.*)$'); $userDesc += $um.Groups[1].Value.Trim().Length }
    Write-Output "NOTE skill listing: gamekit descriptions $descTotal + ~/.claude/skills $userDesc characters, against a budget of about 8,000 at a 200k context (plugins not counted)"
    Check "plugin: gamekit skill descriptions total $descTotal characters, at most the 6,025 ratchet" ($descTotal -le 6025)
    # A skill named as the one to load or invoke must exist: in the plugin, in ~/.claude/skills or in a pack.
    $known = @(Get-ChildItem -LiteralPath (Join-Path $PSScriptRoot 'skills') -Directory | ForEach-Object Name) +
        @(Get-ChildItem -LiteralPath (Join-Path $PSScriptRoot 'agents') -Filter *.md | ForEach-Object BaseName) +
        @(Get-ChildItem -Path (Join-Path $template 'packs\*\.claude\skills') -Directory -ErrorAction SilentlyContinue | ForEach-Object Name) +
        @(Get-ChildItem -LiteralPath (Join-Path $HOME '.claude\skills') -Directory -ErrorAction SilentlyContinue | ForEach-Object Name)
    $handoff = '(?i)\b(?:load|invoke|use|run|see|hand (?:it )?(?:off )?to|in) (?:the )?(?:\*\*|`)(?:gamekit:)?([a-z][a-z0-9]*(?:-[a-z0-9]+)+)(?:\*\*|`)(?! pack)'
    $named = $allMd | Select-String -Pattern $handoff -AllMatches -Context 0, 3 | ForEach-Object {
        $file = $_.Path; $near = (@($_.Line) + $_.Context.PostContext) -join ' '
        foreach ($m in $_.Matches) { if ($near -notmatch 'not loaded|not installed') { [pscustomobject]@{ Name = $m.Groups[1].Value; Where = "$(Split-Path -Leaf (Split-Path $file))/$(Split-Path -Leaf $file):$($_.LineNumber)" } } } }
    $dangling = $named | Where-Object { $_.Name -notin $known } | ForEach-Object { "$($_.Name) ($($_.Where))" }
    Check "plugin: all $(@($named).Count) skills named as a handoff exist" (-not $dangling) ($dangling -join ', ')
    # Sections an agent quotes from the files it names (`${CLAUDE_PLUGIN_ROOT}/skills/...md`) must still be there:
    # "## 1. Build the loop", the skill's "Prefer", unity-performance's "Asset audit", ("Two numbers have a budget"),
    # clarity-rules (section sign)E, difficulty-rhythm (section sign)C.5, item 11 (Pre-Unity-6 API).
    $sect = [char]0xA7; $anchorN = 0   # the section sign, kept out of this ASCII file
    $anchorMiss = foreach ($a in Get-ChildItem -LiteralPath (Join-Path $PSScriptRoot 'agents') -Filter *.md) {
        $at = [IO.File]::ReadAllText($a.FullName); $flat = $at -replace '\r?\n\s*', ' '
        $tf = [regex]::Matches($at, '\$\{CLAUDE_PLUGIN_ROOT\}/(skills/[^\s`"]+\.md)') | ForEach-Object { $_.Groups[1].Value } | Sort-Object -Unique
        $tt = ($tf | Where-Object { Test-Path -LiteralPath (Join-Path $PSScriptRoot $_) } | ForEach-Object { [IO.File]::ReadAllText((Join-Path $PSScriptRoot $_)) }) -join "`n"
        $want = @([regex]::Matches($flat, '"(## [^"]+)"') | ForEach-Object { @{ R = $_.Groups[1].Value; P = "(?m)^$([regex]::Escape($_.Groups[1].Value))\s*$" } }) +
            @([regex]::Matches($flat, $sect + '([A-Z0-9]+(?:\.\d+)?)') | ForEach-Object { @{ R = $sect + $_.Groups[1].Value; P = "(?m)^#{2,4} $([regex]::Escape($_.Groups[1].Value))[. ]" } }) +
            @([regex]::Matches($flat, 'item (\d+) \(([^)]+)\)') | ForEach-Object { @{ R = $_.Value; P = "(?m)^\s*$($_.Groups[1].Value)\. \*\*$([regex]::Escape($_.Groups[2].Value))" } }) +
            @([regex]::Matches($flat, '(?:skill''s |[a-z]+-[a-z-]+''s )"([A-Z][^"]+)"(?:(?:, | and )"([A-Z][^"]+)")*|\("([A-Z][^"]+)"\)') | ForEach-Object {
                foreach ($g in 1, 2, 3) { foreach ($c in $_.Groups[$g].Captures) { $e = [regex]::Escape($c.Value)
                    @{ R = "`"$($c.Value)`""; P = "(?m)^(?:#{1,4} (?:[\dA-Z]+\.\d* )?${e}\s*$|${e}:|\s*(?:[-*]|\d+\.) \*\*${e})" } } } })
        $anchorN += $want.Count
        foreach ($w in $want) { if (-not $tt -or -not [regex]::IsMatch($tt, $w.P)) { "$($a.BaseName): $($w.R)" } } }
    Check "plugin: all $anchorN sections, anchors and items the agents quote exist in the files they name" ($anchorN -ge 15 -and -not $anchorMiss) ($anchorMiss -join ', ')
    # This machine has no Python: a fenced example that calls python3 cannot run (Blender's bpy runs inside Blender).
    $py = foreach ($f in $allMd) { $in = $false; $n = 0
        foreach ($l in [IO.File]::ReadAllLines($f.FullName)) { $n++
            if ($l -match '^\s*```') { $in = -not $in } elseif ($in -and $l -match '(?<![-\w])python3?\s+\S') { "$($f.Directory.Name)/$($f.Name):$n" } } }
    Check 'plugin: no fenced example calls python' (-not $py) ($py -join ', ')
    # Backticked paths into the plugin, the user skills or a shipped docs/ folder must exist where the doc is read.
    # Ceiling: a top-level docs/<name>.md is mostly a file the game writes (gdd.md, go-to-market.md, a pass log), so only
    # docs/<folder>/... is checked, against project/docs and the packs' docs (both reach the game). reference-docs keeps
    # Mixtrol-only paths and is not scanned.
    $linkDocs = @(Get-ChildItem -LiteralPath $PSScriptRoot -Filter *.md -Recurse) +
        @(Get-ChildItem -LiteralPath (Join-Path $template 'packs') -Filter *.md -Recurse | Where-Object FullName -notmatch '\\packs\\reference-docs\\')
    $userSkills = Join-Path $HOME '.claude\skills'
    $broken = $linkDocs | Select-String -Pattern '`((?:plugin/|~/\.claude/skills/|docs/[^`/\s]+/)[^`\s*<>{}]+)`' -AllMatches | ForEach-Object {
        $at = "$(Split-Path -Leaf (Split-Path $_.Path))/$(Split-Path -Leaf $_.Path):$($_.LineNumber)"
        foreach ($m in $_.Matches) { $rel = ($m.Groups[1].Value -replace '[#:].*$', '').TrimEnd('/', '.', ',')
            $ok = if ($rel -like 'plugin/*') { Test-Path -LiteralPath (Join-Path $template $rel) }
                elseif ($rel -like '~/*') { -not (Test-Path -LiteralPath $userSkills) -or (Test-Path -LiteralPath (Join-Path $HOME $rel.Substring(2))) }
                else { (Test-Path -LiteralPath (Join-Path $template "project/$rel")) -or
                       @(Get-ChildItem -Path (Join-Path $template 'packs\*') -Directory | Where-Object { Test-Path -LiteralPath (Join-Path $_.FullName $rel) }).Count }
            if (-not $ok) { "$rel ($at)" } } }
    Check 'docs: every backticked plugin/, ~/.claude/skills/ and docs/ path exists' (-not $broken) (($broken | Select-Object -Unique) -join ', ')

    # --- facts a skill restates from code ------------------------------------------------------------------------
    $fl = [regex]::Match([IO.File]::ReadAllText((Join-Path $template 'packages\com.yunusburkut.gamekit\Runtime\FrameLog.cs')), 'const string Header = "([^"]+)"')
    $perf = [IO.File]::ReadAllText((Join-Path $PSScriptRoot 'skills\unity-performance\SKILL.md'))
    $cols = ($fl.Groups[1].Value -split ',') -replace '^worst_[xyz]$', 'worst_x/y/z' | Select-Object -Unique
    $unsaid = $cols | Where-Object { $perf.IndexOf($_, [StringComparison]::Ordinal) -lt 0 }
    Check "unity-performance: names all $(@($cols).Count) FrameLog CSV columns" ($fl.Success -and -not $unsaid) ($unsaid -join ', ')
    $gkb = [IO.File]::ReadAllText((Join-Path $PSScriptRoot 'bin\gk-bridge'))
    $cli = [IO.File]::ReadAllText((Join-Path $PSScriptRoot 'skills\unity-editor-cli\SKILL.md'))
    # The request list lives in gk-bridge's usage header and case, AgentBridge.cs and this skill's table.
    $verbs = [regex]::Matches($gkb, '(?m)^#\s+gk-bridge ([a-z-]+)') | ForEach-Object { $_.Groups[1].Value } | Sort-Object -Unique
    $case = [regex]::Match($gkb, '(?s)\ncase "\$req" in(.*?)\nesac').Groups[1].Value.Replace('\ ', ' ')
    $targets = [regex]::Match($gkb, 'build <target> \[dev\]\s+([a-z|]+)').Groups[1].Value
    $gap = @($verbs | Where-Object { $case -notmatch "\b$_\b" } | ForEach-Object { "case lacks $_" }) +
        @($verbs | Where-Object { $cli -notmatch ('\| `' + [regex]::Escape($_)) } | ForEach-Object { "table lacks $_" })
    if (-not $targets -or -not $cli.Contains("``build $($targets.Replace('|', '\|'))")) { $gap += "table lacks build $targets" }
    Check "unity-editor-cli: the request table lists all $(@($verbs).Count) gk-bridge requests" (@($verbs).Count -ge 5 -and -not $gap) ($gap -join ', ')
    $yamlExt = [regex]::Match([IO.File]::ReadAllText((Join-Path $hooks 'guard-unity-yaml.ps1')), '\$yaml = ''\\\.\(([^)]+)\)').Groups[1].Value -split '\|'
    $noExt = $yamlExt | Where-Object { -not $cli.Contains("``.$_``") }
    Check "unity-editor-cli: lists all $($yamlExt.Count) guarded YAML extensions" ($yamlExt.Count -ge 5 -and -not $noExt) ($noExt -join ', ')
    # The vendored unity-cli copy carries a gamekit override block; an upstream merge must keep its Play Mode rule.
    $ucli = [regex]::Match([IO.File]::ReadAllText((Join-Path $PSScriptRoot 'skills\unity-cli\SKILL.md')), '(?m)^> - \*\*Play Mode checks:\*\*.*(?:\r?\n>   .*)*').Value
    Check 'unity-cli: the gamekit block keeps the Play Mode checks override' ($ucli.Contains('`gk-bridge play-capture`') -and $ucli.Contains('`playmode-verification-loop.md`'))
    # gk-bridge's RUNNING hold equals AgentBridge.TestRunOpen's window (both sides say to change them together).
    $hold = [regex]::Match($gkb, '(?m)^hold=(\d+)'); $tro = [regex]::Match([IO.File]::ReadAllText((Join-Path $gk 'AgentBridge.cs')), '(?s)static bool TestRunOpen\(\).*?AddMinutes\(-(\d+)\)')
    Check "gk-bridge: the RUNNING hold ($($hold.Groups[1].Value) s) equals TestRunOpen's AddMinutes(-$($tro.Groups[1].Value))" ($hold.Success -and $tro.Success -and [int]$hold.Groups[1].Value -eq 60 * [int]$tro.Groups[1].Value)
    # Every Logs/agent/*.log the agents and skills read is written by GameKit or gk-bridge, and gk-bridge's refresh
    # verdict still checks for a script newer than the compile.
    $logSrc = $bridgeSrc + $gkb
    $logs = $allMd | Select-String -Pattern 'Logs/agent/([a-z-]+\.log)' -AllMatches | ForEach-Object { $_.Matches } | ForEach-Object { $_.Groups[1].Value } | Sort-Object -Unique
    $noLog = $logs | Where-Object { $logSrc.IndexOf($_, [StringComparison]::Ordinal) -lt 0 }
    $blk = [regex]::Match($gkb, '(?ms)^    bridge\.log\)(.*?)^        fi ;;').Value
    if (-not ($blk.Contains('find') -and $blk.Contains('-newer'))) { $noLog += 'the bridge.log verdict lost its find -newer check' }
    Check "gk-bridge: all $(@($logs).Count) Logs/agent logs the docs name are written by GameKit or gk-bridge" (@($logs).Count -ge 5 -and -not $noLog) ($noLog -join ', ')
    # The read-only reviewers restate that bridge.log verdict (they never run gk-bridge): same conditions, same file types.
    $fresh = 'REFRESHED', 'no script changes', "-name '*.asmref'"
    $freshGap = @(foreach ($ag in 'unity-reviewer', 'bug-hunter') { $at = [IO.File]::ReadAllText((Join-Path $PSScriptRoot "agents\$ag.md"))
        $fresh | Where-Object { -not $at.Contains($_) } | ForEach-Object { "$ag lacks $_" } }) +
        @($fresh | Where-Object { -not $blk.Contains($_) -and -not $gkb.Contains($_) } | ForEach-Object { "gk-bridge lacks $_" })
    Check 'agents: unity-reviewer and bug-hunter restate the gk-bridge freshness rule (REFRESHED, no script changes, .asmref)' (-not $freshGap) ($freshGap -join ', ')
    # implementation-verification restates AgentBridge's Console buffer, gk-bridge's default deadline and the capture length.
    $ab = [IO.File]::ReadAllText((Join-Path $gk 'AgentBridge.cs'))
    $iv = [IO.File]::ReadAllText((Join-Path $PSScriptRoot 'skills\implementation-verification\SKILL.md'))
    $cap = [regex]::Match($ab, 'const int ConsoleCapacity = (\d+)').Groups[1].Value
    $tmo = @([regex]::Matches($gkb, ': "\$\{timeout:=(\d+)\}"') | ForEach-Object { $_.Groups[1].Value })[-1]
    $about = [Math]::Round([double][regex]::Match($ab, 'const float DefaultCaptureSeconds = ([\d.]+)f').Groups[1].Value + [double][regex]::Match($ab, 'const double RefreshSettle = ([\d.]+)').Groups[1].Value)
    $ivGap = @(if (-not $cap -or -not $iv.Contains("last $cap Console")) { "last $cap Console" }) + @(if (-not $tmo -or $iv -notmatch "within\s+$tmo s") { "within $tmo s" }) +
        @(if ($iv -notmatch "about $about s plus compile") { "about $about s plus compile" })
    Check "implementation-verification: restates ConsoleCapacity $cap, the $tmo s gk-bridge deadline and the $about s capture" (-not $ivGap) ($ivGap -join ', ')

    $gf = Join-Path $PSScriptRoot 'skills\game-feel'
    $ptr = Select-String -LiteralPath (Join-Path $gf 'SKILL.md') -Pattern "``references/([a-z-]+)\.md`` $sect(\d+)|$sect(\d+) of ([a-z-]+)" -AllMatches |
        ForEach-Object { $_.Matches } | ForEach-Object { if ($_.Groups[1].Success) { "$($_.Groups[1].Value)|$($_.Groups[2].Value)" } else { "$($_.Groups[4].Value)|$($_.Groups[3].Value)" } } | Sort-Object -Unique
    $badPtr = $ptr | Where-Object { $f, $n = $_ -split '\|'; $ref = Join-Path $gf "references\$f.md"
        -not (Test-Path -LiteralPath $ref) -or -not (Select-String -LiteralPath $ref -Pattern "^## $n\. " -Quiet) }
    $fs = [IO.File]::ReadAllText((Join-Path $gf 'references\feedback-stack.md'))
    $badCount = foreach ($id in 'FR', 'FP', 'FX') { $h = [regex]::Match($fs, "(?m)^## \d+\. ${id}: .*\((\d+)\)")
        $rows = [regex]::Matches($fs, "(?m)^\| $id\d\d\b").Count
        if (-not $h.Success -or [int]$h.Groups[1].Value -ne $rows) { "$id header $($h.Groups[1].Value) rows $rows" } }
    Check "game-feel: $(@($ptr).Count) section pointers resolve and the FR/FP/FX counts match their rows" ($ptr -and -not $badPtr -and -not $badCount) ((@($badPtr) + @($badCount)) -join ', ')
    # Every number in SKILL.md's quick table must still appear in the numbers.md section(s) its column names, so a
    # band retuned in numbers.md cannot leave a stale copy in SKILL.md.
    $num = [IO.File]::ReadAllText((Join-Path $gf 'references\numbers.md'))
    $quick = [regex]::Matches([IO.File]::ReadAllText((Join-Path $gf 'SKILL.md')), '(?m)^\| ([^|]+) \| ([^|]+) \| ([\d., ]+) \|')
    $stale = foreach ($row in $quick) {
        $body = ($row.Groups[3].Value -split ',' | ForEach-Object { $s = $_.Trim()
            $m = [regex]::Match($num, "(?ms)^#{2,3} $([regex]::Escape($s))[. ].*?(?=^#{2,3} \d)"); if ($m.Success) { $m.Value } else { "<no section $s>" } }) -join "`n"
        foreach ($v in [regex]::Matches($row.Groups[2].Value, '\d+(?:\.\d+)?(?:\p{Pd}\d+(?:\.\d+)?)?')) {
            if (-not $body.Contains($v.Value)) { "$($row.Groups[1].Value.Trim()): $($v.Value) not in $($row.Groups[3].Value)" } } }
    Check "game-feel: $($quick.Count) quick-table rows match their numbers.md sections" ($quick.Count -ge 10 -and -not $stale) (@($stale) -join ', ')
    # feel-troubleshooting points into feel-authoring's references by section number and *Heading*.
    $fa = Join-Path $PSScriptRoot 'skills\feel-authoring\references'
    $ftText = [IO.File]::ReadAllText((Join-Path $PSScriptRoot 'skills\feel-troubleshooting\SKILL.md')) -replace '\r?\n\s*', ' '
    $ftPtr = [regex]::Matches($ftText, '`feel-authoring/references/([a-z-]+\.md)`,\s*(?:section (\d+)(?:\s*\*([^*]+)\*)?|\*([^*]+)\*)')
    $ftBad = foreach ($m in $ftPtr) { $ref = Join-Path $fa $m.Groups[1].Value
        $body = if (Test-Path -LiteralPath $ref) { [IO.File]::ReadAllText($ref) } else { '' }
        $head = if ($m.Groups[3].Success) { $m.Groups[3].Value } else { $m.Groups[4].Value }
        if (-not $body -or ($m.Groups[2].Success -and $body -notmatch "(?m)^## $($m.Groups[2].Value)\. ") -or
            ($head -and $body -notmatch "(?m)^#{2,3} .*$([regex]::Escape($head))")) { $m.Value } }
    Check "feel-troubleshooting: all $($ftPtr.Count) pointers into feel-authoring's references resolve" ($ftPtr.Count -ge 5 -and -not $ftBad) ($ftBad -join ' | ')

    $feel = Get-ChildItem -Path 'C:\GitHub\*\Assets\Feel' -Directory -ErrorAction SilentlyContinue | Where-Object { Test-Path -LiteralPath (Join-Path $_.FullName 'MMFeedbacks') } | Select-Object -First 1
    if ($feel) {
        $text = $(foreach ($fa in 'feel-authoring', 'feel-troubleshooting') { $fa = Join-Path $PSScriptRoot "skills\$fa"
            @(Get-Item -LiteralPath (Join-Path $fa 'SKILL.md')) + @(Get-ChildItem -LiteralPath (Join-Path $fa 'references') -Filter *.md -ErrorAction SilentlyContinue) |
                ForEach-Object { [IO.File]::ReadAllText($_.FullName) } }) -join "`n"
        # Every event the skill triggers must be a declared type whose file has a static Trigger; every other
        # backticked MM name must be a word in Feel's code (type, member, enum value) or a Feel folder (a module).
        # A line that calls a name old or removed names it on purpose. ALL-CAPS names are scripting defines.
        $events = [regex]::Matches($text, '\b(MM\w+Event)\.Trigger\b') | ForEach-Object { $_.Groups[1].Value } | Sort-Object -Unique
        # Every backticked name on the line, not only the last one (a catalog line lists several).
        # A second class: backticked PascalCase members of three or more humps (CanPlayWhileAlreadyPlaying).
        $current = $text -split "`n" | Where-Object { $_ -notmatch '(?i)\bold\b|legacy|removed|deprecated|\bbecame\b|pre-v\d|does not exist' }
        $names = $current | ForEach-Object { [regex]::Matches($_, '`(MMF?_?[A-Z]\w*[a-z]\w*)`') } | ForEach-Object { $_.Groups[1].Value } | Sort-Object -Unique
        $members = $current | ForEach-Object { [regex]::Matches($_, '`([A-Z][a-z]+(?:[A-Z][a-z0-9]+){2,})`') } | ForEach-Object { $_.Groups[1].Value } | Sort-Object -Unique
        $declared = @{}; $words = @{}
        foreach ($cs in Get-ChildItem -LiteralPath $feel.FullName -Filter *.cs -Recurse) { $src = [IO.File]::ReadAllText($cs.FullName)
            foreach ($m in [regex]::Matches($src, '\b(?:class|struct|enum|interface)\s+(MM\w+)')) { $declared[$m.Groups[1].Value] = $src }
            foreach ($m in [regex]::Matches($src, '\b[A-Z]\w+\b')) { $words[$m.Value] = 1 } }
        Get-ChildItem -LiteralPath $feel.FullName -Directory -Recurse | ForEach-Object { $words[$_.Name] = 1 }
        $unknownTypes = @($events | Where-Object { -not $declared.ContainsKey($_) -or $declared[$_] -notmatch '\bstatic\b[^;{(=]*\bTrigger\s*\(' } | ForEach-Object { "$_.Trigger" }) +
            @(@($names) + @($members) | Where-Object { -not $words.ContainsKey($_) })
        Check "feel skills: all $(@($events).Count) event triggers, $(@($names).Count) MM names and $(@($members).Count) members exist in $($feel.Parent.Parent.Name)'s Feel" (@($events).Count -and -not $unknownTypes) ($unknownTypes -join ', ')
    } else { Write-Output 'SKIP feel skills: no game under C:\GitHub has Assets\Feel\MMFeedbacks' }

    # --- scripts the skills ship ---------------------------------------------------------------------------------
    $bash = Join-Path $env:ProgramFiles 'Git\bin\bash.exe'
    if (Test-Path -LiteralPath $bash) {
        $ErrorActionPreference = 'Continue'   # a stderr line must not abort the suite (as for gk-bridge above)
        $o = & $bash (Join-Path $PSScriptRoot 'skills\refactor-pass\scripts\test-survey.sh') 2>&1
        $ErrorActionPreference = 'Stop'
        Check 'refactor-pass: test-survey.sh passes' ($LASTEXITCODE -eq 0) (($o | Select-Object -Last 5) -join ' | ')
    } else { Write-Output "SKIP refactor-pass: no Git Bash at $bash" }
    # unity-code-review item 11 is the source of the obsolete-API list; every old name it renames (the backticked name
    # before an arrow) has a line in test-survey.sh's Obsolete.cs fixture, so the survey regex is tested for it.
    $ucr = [IO.File]::ReadAllText((Join-Path $PSScriptRoot 'skills\unity-code-review\SKILL.md'), [Text.Encoding]::UTF8)
    $item11 = [regex]::Match($ucr, '(?ms)^11\. \*\*Pre-Unity-6 API.*?(?=^\d+\. \*\*|^## )').Value -replace '\r?\n\s*', ' '
    $fixture = [regex]::Match([IO.File]::ReadAllText((Join-Path $PSScriptRoot 'skills\refactor-pass\scripts\test-survey.sh')), '(?s)Obsolete\.cs" <<''CS''\r?\n(.*?)\r?\nCS').Groups[1].Value
    $renamed = [regex]::Matches($item11, '`([^`]+)`\s*' + [char]0x2192) | ForEach-Object { $_.Groups[1].Value.TrimStart('.') } | Sort-Object -Unique
    $noFixture = $renamed | Where-Object { -not $fixture.Contains($_) }
    Check "unity-code-review: all $(@($renamed).Count) renamed APIs in item 11 have a line in the survey's Obsolete.cs fixture" (@($renamed).Count -ge 15 -and $fixture -and -not $noFixture) ($noFixture -join ', ')
    # feature.js lets the plan pick the coop pack's net-auditor as a reviewer (its items' enum or pattern accepts it).
    $fjs = [IO.File]::ReadAllText((Join-Path $PSScriptRoot 'workflows\feature.js'))
    $revItems = [regex]::Match($fjs, '(?s)\n    reviewers: \{(.*?)\n    \w').Groups[1].Value
    $revEnum = [regex]::Match($revItems, 'enum: \[([^\]]*)\]'); $revPat = [regex]::Match($revItems, "pattern: '([^']+)'")
    $revOk = if ($revEnum.Success) { $revEnum.Groups[1].Value -match "'net-auditor'" } elseif ($revPat.Success) { 'net-auditor' -cmatch $revPat.Groups[1].Value } else { $false }
    Check 'feature.js: the reviewers schema accepts net-auditor' $revOk ($revItems.Trim() -replace '\s+', ' ')
    # feature.js must parse as a Workflow script (an async function body; meta is an export). No Node here, so headless
    # Edge compiles it: the page prints OK or the SyntaxError.
    $edge = @("${env:ProgramFiles(x86)}\Microsoft\Edge\Application\msedge.exe", "$env:ProgramFiles\Microsoft\Edge\Application\msedge.exe") |
        Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
    if ($edge) {
        $js = [IO.File]::ReadAllText((Join-Path $PSScriptRoot 'workflows\feature.js')) -replace '(?m)^export const meta', 'const meta'
        # The review loop's dispute helpers, lifted out of the body and run against the cases they exist for.
        $helpers = (@('given', 'disputedPrefix', 'disputeKey', 'dedupeDisputes', 'fileLine', 'sameWhere') | ForEach-Object {
            [regex]::Match($js, "(?m)^const $_ = .*$").Value }) + [regex]::Match($js, '(?ms)^const disputedBy = .*?^}').Value
        $asserts = @'
let disputes = ['review abc1234: disputed Assets/Game/Ball.cs:41 - the clamp is at Ball.cs:44', 'Assets/Game/Paddle.cs - uses Time.deltaTime']
const eq = (a, b, what) => { if (a !== b) throw new Error(what + ': got ' + JSON.stringify(a)) }
eq(fileLine('Assets\\Game\\Ball.cs:41 shake'), 'Assets/Game/Ball.cs:41', 'fileLine turns backslashes to slashes')
eq(sameWhere('assets\\game\\ball.cs:41', 'assets/game/ball.cs:41'), true, 'the same file:line matches across slashes')
eq(sameWhere('assets/game/ball.cs:41', 'assets/game/ball.cs:42'), false, 'another line does not match')
eq(sameWhere('assets/game/paddle.cs', 'assets/game/paddle.cs:9'), false, 'a bare file never matches a file:line')
eq(disputeKey(disputes[0]), 'assets/game/ball.cs:41', 'disputeKey strips the rerun prefix and the evidence')
eq(disputeKey('review abc1234 (\u00f6nce: x): disputed A.cs:3 - e'), 'a.cs:3', 'a repaired Base keeps its key')
eq(dedupeDisputes(['A.cs:1 - old', 'yok', 'a.cs:1 - new']).join('|'), 'a.cs:1 - new', 'one dispute per where, the latest kept, yok dropped')
eq(disputedBy({ where: 'Assets\\Game\\Ball.cs:41' }), 'Assets/Game/Ball.cs:41 - the clamp is at Ball.cs:44', 'disputedBy finds the dispute by file:line')
eq(disputedBy({ where: 'Assets/Game/Ball.cs:50' }), '', 'disputedBy leaves another line open')
'@
        $page = Join-Path $tmp 'parse-feature.html'
        [IO.File]::WriteAllText($page, '<!doctype html><meta charset="utf-8"><textarea id="s">' + [Net.WebUtility]::HtmlEncode($js) + '</textarea>' +
            '<textarea id="h">' + [Net.WebUtility]::HtmlEncode(($helpers -join "`n") + "`n" + $asserts) + '</textarea><pre id="r"></pre><pre id="q"></pre><script>' +
            "try { new (Object.getPrototypeOf(async function () {}).constructor)('args', 'agent', 'parallel', 'phase', 'log', document.getElementById('s').value); r.textContent = 'PARSE-OK' }" +
            " catch (e) { r.textContent = 'PARSE-ERROR ' + e.name + ': ' + e.message }" +
            " try { new Function(document.getElementById('h').value)(); q.textContent = 'HELPERS-OK' } catch (e) { q.textContent = 'HELPERS-FAIL ' + e.message }</script>", $utf8)
        $psi = New-Object Diagnostics.ProcessStartInfo $edge
        $psi.Arguments = "--headless --disable-gpu --no-first-run --user-data-dir=`"$(Join-Path $tmp 'edge')`" --dump-dom `"$(([Uri]$page).AbsoluteUri)`""
        $psi.UseShellExecute = $false; $psi.RedirectStandardOutput = $true; $psi.RedirectStandardError = $true
        $edgeProc = [Diagnostics.Process]::Start($psi); $out = $edgeProc.StandardOutput.ReadToEndAsync(); $null = $edgeProc.StandardError.ReadToEndAsync()
        if (-not $edgeProc.WaitForExit(60000)) { $edgeProc.Kill() }
        $res = [regex]::Match($out.Result, 'PARSE-(OK|ERROR[^<]*)').Value
        Check 'feature.js: parses as a Workflow script' ($res -eq 'PARSE-OK') $(if ($res) { $res } else { 'no answer from headless Edge' })
        $res = [Net.WebUtility]::HtmlDecode([regex]::Match($out.Result, 'HELPERS-(OK|FAIL[^<]*)').Value)
        Check 'feature.js: the dispute helpers match file:line across slashes and keep one dispute per where' ($res -eq 'HELPERS-OK') $(if ($res) { $res } else { 'no answer from headless Edge' })
    } else { Write-Output 'SKIP feature.js parse: no Microsoft Edge' }
} finally {
    Remove-Item -LiteralPath $tmp -Recurse -Force -ErrorAction SilentlyContinue
}
if ($failed) { Write-Output "$failed check(s) failed"; exit 1 }
Write-Output 'All checks passed'
exit 0
