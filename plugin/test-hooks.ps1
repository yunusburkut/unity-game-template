# Regression check for the gamekit plugin's hooks and reference indexes. Run after changing plugin/hooks/ or a
# skill's references: powershell -NoProfile -ExecutionPolicy Bypass -File plugin\test-hooks.ps1
# It pipes fixed payloads through every hook script (check-json, guard-unity-yaml with a held fake UnityLockfile,
# ensure-blender, route, self-check), runs gk-bridge against a fake AgentBridge, and checks that hooks.json and the
# scripts agree, so nothing here opens Blender or Unity. It also lints what the skills and agents point at (plugin
# paths, description budget, handoffs, facts restated from FrameLog, gk-bridge and Feel), runs refactor-pass's
# test-survey.sh, the global router's one-router test and a headless-Edge parse of workflows/feature.js; each of
# those skips with a note when its tool or source is absent. Not covered: ensure-blender's launch path (it starts a
# window) and the inline PostToolUse refresh one-liners in hooks.json. Exit 0 = all pass, 1 = a failure.
# Pure ASCII on purpose: Windows PowerShell 5.1 reads a BOM-less script as ANSI.
$ErrorActionPreference = 'Stop'
$hooks = Join-Path $PSScriptRoot 'hooks'
$tmp = Join-Path $env:TEMP ('gk-test-hooks-' + [guid]::NewGuid().ToString('N').Substring(0, 8))
New-Item -ItemType Directory -Path $tmp | Out-Null
$utf8 = New-Object Text.UTF8Encoding $false
$failed = 0

function Invoke-Hook($script, $payload, $cwd = $tmp, $envs = @{}) {
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
    $out = $p.StandardOutput.ReadToEndAsync(); $err = $p.StandardError.ReadToEndAsync()
    if (-not $p.WaitForExit(60000)) { $p.Kill(); return @{ code = -1; out = ''; err = 'timeout' } }
    return @{ code = $p.ExitCode; out = $out.Result.Trim(); err = $err.Result.Trim() }
}
function Check($name, $ok, $detail = '') {
    if ($ok) { Write-Output "PASS $name" } else { Write-Output "FAIL $name $detail"; $script:failed++ }
}
function Payload($obj) { return ($obj | ConvertTo-Json -Compress -Depth 5) }

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
    $held = [IO.File]::Open((Join-Path $gp 'Temp\UnityLockfile'), 'OpenOrCreate', 'ReadWrite', 'None')
    try {
        $r = & $guard 'Edit' (Join-Path $gp 'Assets\a.prefab'); Check 'guard: Edit of a prefab under a live Editor is denied' (& $denied $r) $r.out
        $r = & $guard 'Write' (Join-Path $gp 'Assets\New.mixer'); Check 'guard: Write of a mixer is denied' (& $denied $r) $r.out
        $r = & $guard 'Edit' (Join-Path $gp 'Assets\a.prefab') $tmp
        Check 'guard: Edit in another session folder is judged by the owning project' (& $denied $r) $r.out
        $r = & $guard 'Bash' 'sed -i s/x/y/ Assets/a.prefab'; Check 'guard: sed -i on a prefab is denied' (& $denied $r) $r.out
        $r = & $guard 'Bash' 'echo x > Assets/a.prefab'; Check 'guard: redirect into a prefab is denied' (& $denied $r) $r.out
        $r = & $guard 'PowerShell' "Set-Content Assets\x.asset 'a'"; Check 'guard: Set-Content on an asset is denied' (& $denied $r) $r.out
        $r = & $guard 'Bash' "cp $($gp -replace '\\', '/')/Assets/a.prefab /c/scratch/b.prefab"
        Check 'guard: copy with an absolute in-project path is denied' (& $denied $r) $r.out
        $r = & $guard 'Bash' 'cat Assets/a.prefab'; Check 'guard: reading a prefab is silent' (& $silent $r) $r.out
        $r = & $guard 'Bash' 'grep com.unity.pipeline Packages/manifest.json > out.txt'
        Check 'guard: a package id is not a .unity file' (& $silent $r) $r.out
        $r = & $guard 'Bash' 'cp /c/elsewhere/a.prefab /c/scratch/b.prefab'; Check 'guard: YAML outside every project is silent' (& $silent $r) $r.out
        $r = & $guard 'Edit' (Join-Path $tmp 'gproj-Backup\Assets\x.prefab'); Check 'guard: a sibling folder with the same prefix is silent' (& $silent $r) $r.out
    } finally { $held.Dispose() }
    $r = & $guard 'Edit' (Join-Path $gp 'Assets\a.prefab'); Check 'guard: a lockfile left by a crash is silent' (& $silent $r) $r.out
    $r = Invoke-Hook 'guard-unity-yaml.ps1' 'not json'; Check 'guard: bad payload is a non-blocking error' ($r.code -eq 1 -and -not $r.out)

    # --- hooks.json agrees with the scripts ---------------------------------------------------------------------------
    $hj = [IO.File]::ReadAllText((Join-Path $hooks 'hooks.json')) | ConvertFrom-Json
    $wired = foreach ($ev in $hj.hooks.PSObject.Properties) { foreach ($g in $ev.Value) { foreach ($h in $g.hooks) {
        [pscustomobject]@{ If = [string]$h.if; Cmd = ((@($h.args) + $h.command) -join ' ') } } } }
    $scripts = $wired | ForEach-Object { [regex]::Matches($_.Cmd, '\$\{CLAUDE_PLUGIN_ROOT\}/(\S+)') } | ForEach-Object { $_.Groups[1].Value } | Sort-Object -Unique
    $absent = $scripts | Where-Object { -not (Test-Path -LiteralPath (Join-Path $PSScriptRoot $_)) }
    Check "hooks.json: all $(@($scripts).Count) referenced scripts exist" (@($scripts).Count -gt 0 -and -not $absent) ($absent -join ', ')
    $extOf = { param($script, $pattern)   # the extension alternation a script matches on, sorted
        $m = [regex]::Match([IO.File]::ReadAllText((Join-Path $hooks $script)), $pattern)
        ($m.Groups[1].Value -split '\|' | Sort-Object) -join '|' }
    foreach ($c in @(@{ Script = 'guard-unity-yaml.ps1'; Pattern = '\$yaml = ''\\\.\(([^)]+)\)'; Tools = 'Edit', 'Write', 'Bash', 'PowerShell' },
                     @{ Script = 'check-json.ps1'; Pattern = "notmatch '\\\.\(([^)]+)\)\$'"; Tools = 'Edit', 'Write' })) {
        $want = & $extOf $c.Script $c.Pattern
        foreach ($tool in $c.Tools) {
            $got = ($wired | Where-Object { $_.Cmd -like "*$($c.Script)*" } |
                ForEach-Object { if ($_.If -match "^$tool\(\*\.(\w+)\*?\)$") { $Matches[1] } } | Sort-Object) -join '|'
            Check "hooks.json: $($c.Script) $tool rules cover its extensions" ($want -and $got -ceq $want) "rules: $got / script: $want"
        }
    }

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
    $listener = New-Object Net.Sockets.TcpListener ([Net.IPAddress]::Loopback), 0
    $listener.Start()
    try {
        $sw = [Diagnostics.Stopwatch]::StartNew()
        $r = Invoke-Hook 'ensure-blender.ps1' (Payload @{ tool_name = 'mcp__Blender__get_objects_summary'; tool_input = @{} }) $tmp @{ BLENDER_MCP_PORT = [string]$listener.LocalEndpoint.Port }
        Check "ensure-blender: a listening server passes a live call at once ($([int]$sw.Elapsed.TotalSeconds) s)" ($r.code -eq 0 -and $sw.Elapsed.TotalSeconds -lt 8) "exit $($r.code) $($r.err)"
    } finally { $listener.Stop() }
    $r = Invoke-Hook 'ensure-blender.ps1' 'not json'; Check 'ensure-blender: bad payload fails open' ($r.code -eq 0)

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
    } finally { $held.Dispose() }
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
reset() { rm -f "$d"/request.txt "$d"/bridge.log "$d"/compile-player.log "$d"/build.log "$d"/tests.log
          printf 'OK  old\n' > "$d/compile.log"; at -300 "$d/compile.log"; at -600 "$root/Assets/A.cs"; }
# answer <log> <first line> [compile.log first line]: take request.txt and answer the way AgentBridge does
answer() { ( for _ in $(seq 100); do [ -e "$d/request.txt" ] && break; sleep 0.1; done
             sleep 0.3; [ -z "${3:-}" ] || printf '%s\n' "$3" > "$d/compile.log"
             rm -f "$d/request.txt"; printf '%s\n' "$2" > "$d/$1" ) & }
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
# run-tests: no bridge.log and no GameKit in the manifest, so this AgentBridge copy is asked without a refresh gate
reset; answer tests.log 'Passed  12 passed, 0 failed, 0 skipped';               run 'run-tests that passed passes' 0 run-tests
reset; answer tests.log 'Passed  0 passed, 0 failed, 0 skipped';                run 'run-tests with no test run is unknown' 2 run-tests
reset; answer tests.log 'Failed  0 passed, 2 failed, 0 skipped';                run 'run-tests with failures fails' 1 run-tests
reset; printf 'PENDING  windows\n' > "$d/build.log";                           run 'a running build is unknown' 2 refresh
reset; printf 'refresh\n' > "$d/request.txt"; answer bridge.log 'REFRESHED  now  compiled' 'OK  now'; run 'joins the queued hook request' 0 refresh
reset; T=3 run 'a request nobody takes is unknown' 2 refresh
[ ! -e "$d/request.txt" ] && echo 'PASS gk-bridge: an untaken request is withdrawn' || echo 'FAIL gk-bridge: an untaken request is withdrawn'
run 'bad usage is unknown' 2 frobnicate
'@.Replace("`r`n", "`n"), $utf8)
        $lines = & $bash $driver ((Join-Path $PSScriptRoot 'bin\gk-bridge') -replace '\\', '/') ($gb -replace '\\', '/') 2>&1
        foreach ($l in $lines) {
            if ("$l" -match '^(PASS|FAIL) (.*)$') { Check $Matches[2] ($Matches[1] -eq 'PASS') } else { Check "gk-bridge: driver output" $false "$l" }
        }
    } else { Write-Output "SKIP gk-bridge: no Git Bash at $bash" }

    # --- route.ps1 ------------------------------------------------------------------------------------------------
    $game = Join-Path $tmp 'game'; New-Item -ItemType Directory -Force -Path (Join-Path $game 'ProjectSettings') | Out-Null
    [IO.File]::WriteAllText((Join-Path $game 'ProjectSettings\ProjectVersion.txt'), 'm_EditorVersion: 6000.6.0f1', $utf8)
    $route = { param($prompt, $cwd, $sid = '') Invoke-Hook 'route.ps1' (Payload @{ prompt = $prompt; cwd = $cwd; session_id = $sid }) $cwd }
    $r = & $route 'muzik ekle' $game;  Check 'route: new task in a Unity project prints the router' ($r.out -match 'task router')
    Check 'route: router names the prototype route' ($r.out -match 'gamekit:prototype')
    Check 'route: a prompt without "devam" skips the devam rule' ($r.out -notmatch '"devam": after') $r.out
    $r = & $route 'devam' $game;       Check 'route: "devam" prints the devam rule' ($r.out -match '"devam": after') $r.out
    $sid = 'gktest-' + [guid]::NewGuid().ToString('N').Substring(0, 8)   # $game has no compile.log, GameKit or bridge copy
    try {
        $r = & $route 'muzik ekle' $game $sid; Check 'route: the no-AgentBridge note prints on the first prompt' ($r.out -match 'no AgentBridge') $r.out
        $r = & $route 'ses ekle' $game $sid;   Check 'route: the no-AgentBridge note prints once per session' ($r.out -match 'task router' -and $r.out -notmatch 'no AgentBridge') $r.out
    } finally { Remove-Item -LiteralPath (Join-Path ([IO.Path]::GetTempPath()) "gamekit-route-$sid.bridge") -Force -ErrorAction SilentlyContinue }
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
    Check 'genre-defaults: LICENSE.md carries the MIT text' (Select-String -LiteralPath (Join-Path $gd 'LICENSE.md') -Pattern 'Permission is hereby granted' -Quiet)

    $template = Split-Path $PSScriptRoot
    # --- skills and agents: plugin paths, descriptions, handoffs ----------------------------------------------------
    $docs = @(Get-ChildItem -LiteralPath (Join-Path $PSScriptRoot 'agents') -Filter *.md) +
        @(Get-ChildItem -LiteralPath (Join-Path $PSScriptRoot 'skills') -Filter SKILL.md -Recurse)
    $allMd = @(Get-ChildItem -LiteralPath (Join-Path $PSScriptRoot 'agents'), (Join-Path $PSScriptRoot 'skills') -Filter *.md -Recurse)
    $rootRefs = $allMd + @(Get-ChildItem -LiteralPath (Join-Path $PSScriptRoot 'workflows') -Filter *.js) |
        Select-String -Pattern '\$\{CLAUDE_PLUGIN_ROOT\}/([^\s`"''()<>]+)' -AllMatches |
        ForEach-Object { $_.Matches } | ForEach-Object { $_.Groups[1].Value.TrimEnd('.', ',', ';', ':') } | Sort-Object -Unique
    $absent = $rootRefs | Where-Object { -not (Test-Path -LiteralPath (Join-Path $PSScriptRoot $_)) }
    Check "plugin: all $(@($rootRefs).Count) `${CLAUDE_PLUGIN_ROOT} paths exist" (@($rootRefs).Count -gt 0 -and -not $absent) ($absent -join ', ')
    # The skill listing has a budget and drops long descriptions; 250 characters keeps every one listed.
    $long = foreach ($d in $docs) {
        $fm = [regex]::Match([IO.File]::ReadAllText($d.FullName), '(?s)\A---\r?\n(.*?)\r?\n---')
        $m = [regex]::Match($fm.Groups[1].Value, '(?m)^description:[ \t]*(.*)$')
        if (-not $m.Success) { "$($d.Directory.Name)/$($d.Name) (none)" }
        elseif ($m.Groups[1].Value.Trim().Trim('"', "'").Length -gt 250) { "$($d.Directory.Name)/$($d.Name) ($($m.Groups[1].Value.Trim().Length))" }
    }
    Check "plugin: all $($docs.Count) skill and agent descriptions are set and at most 250 characters" (-not $long) ($long -join ', ')
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

    $gf = Join-Path $PSScriptRoot 'skills\game-feel'; $sect = [char]0xA7   # the section sign, kept out of this ASCII file
    $ptr = Select-String -LiteralPath (Join-Path $gf 'SKILL.md') -Pattern "``references/([a-z-]+)\.md`` $sect(\d+)|$sect(\d+) of ([a-z-]+)" -AllMatches |
        ForEach-Object { $_.Matches } | ForEach-Object { if ($_.Groups[1].Success) { "$($_.Groups[1].Value)|$($_.Groups[2].Value)" } else { "$($_.Groups[4].Value)|$($_.Groups[3].Value)" } } | Sort-Object -Unique
    $badPtr = $ptr | Where-Object { $f, $n = $_ -split '\|'; $ref = Join-Path $gf "references\$f.md"
        -not (Test-Path -LiteralPath $ref) -or -not (Select-String -LiteralPath $ref -Pattern "^## $n\. " -Quiet) }
    $fs = [IO.File]::ReadAllText((Join-Path $gf 'references\feedback-stack.md'))
    $badCount = foreach ($id in 'FR', 'FP', 'FX') { $h = [regex]::Match($fs, "(?m)^## \d+\. ${id}: .*\((\d+)\)")
        $rows = [regex]::Matches($fs, "(?m)^\| $id\d\d\b").Count
        if (-not $h.Success -or [int]$h.Groups[1].Value -ne $rows) { "$id header $($h.Groups[1].Value) rows $rows" } }
    Check "game-feel: $(@($ptr).Count) section pointers resolve and the FR/FP/FX counts match their rows" ($ptr -and -not $badPtr -and -not $badCount) ((@($badPtr) + @($badCount)) -join ', ')

    $feel = Get-ChildItem -Path 'C:\GitHub\*\Assets\Feel' -Directory -ErrorAction SilentlyContinue | Where-Object { Test-Path -LiteralPath (Join-Path $_.FullName 'MMFeedbacks') } | Select-Object -First 1
    if ($feel) {
        $fa = Join-Path $PSScriptRoot 'skills\feel-authoring'
        $text = (@(Get-Item -LiteralPath (Join-Path $fa 'SKILL.md')) + @(Get-ChildItem -LiteralPath (Join-Path $fa 'references') -Filter *.md) | ForEach-Object { [IO.File]::ReadAllText($_.FullName) }) -join "`n"
        # Every event the skill triggers must be a declared type whose file has a static Trigger; every other
        # backticked MM name must be a word in Feel's code (type, member, enum value) or a Feel folder (a module).
        # A line that calls a name old or removed names it on purpose. ALL-CAPS names are scripting defines.
        $events = [regex]::Matches($text, '\b(MM\w+Event)\.Trigger\b') | ForEach-Object { $_.Groups[1].Value } | Sort-Object -Unique
        $names = [regex]::Matches($text, '(?m)^(.*)`(MMF?_?[A-Z]\w*[a-z]\w*)`') | Where-Object { $_.Groups[1].Value -notmatch '(?i)\bold\b|legacy|removed|deprecated' } |
            ForEach-Object { $_.Groups[2].Value } | Sort-Object -Unique
        $declared = @{}; $words = @{}
        foreach ($cs in Get-ChildItem -LiteralPath $feel.FullName -Filter *.cs -Recurse) { $src = [IO.File]::ReadAllText($cs.FullName)
            foreach ($m in [regex]::Matches($src, '\b(?:class|struct|enum|interface)\s+(MM\w+)')) { $declared[$m.Groups[1].Value] = $src }
            foreach ($m in [regex]::Matches($src, '\bMM\w+')) { $words[$m.Value] = 1 } }
        Get-ChildItem -LiteralPath $feel.FullName -Directory -Recurse | ForEach-Object { $words[$_.Name] = 1 }
        $unknownTypes = @($events | Where-Object { -not $declared.ContainsKey($_) -or $declared[$_] -notmatch '\bstatic\b[^;{(=]*\bTrigger\s*\(' } | ForEach-Object { "$_.Trigger" }) +
            @($names | Where-Object { -not $words.ContainsKey($_) })
        Check "feel-authoring: all $(@($events).Count) event triggers and $(@($names).Count) MM names exist in $($feel.Parent.Parent.Name)'s Feel" (@($events).Count -and -not $unknownTypes) ($unknownTypes -join ', ')
    } else { Write-Output 'SKIP feel-authoring: no game under C:\GitHub has Assets\Feel\MMFeedbacks' }

    # --- scripts the skills ship ---------------------------------------------------------------------------------
    $bash = Join-Path $env:ProgramFiles 'Git\bin\bash.exe'
    if (Test-Path -LiteralPath $bash) {
        $o = & $bash (Join-Path $PSScriptRoot 'skills\refactor-pass\scripts\test-survey.sh') 2>&1
        Check 'refactor-pass: test-survey.sh passes' ($LASTEXITCODE -eq 0) (($o | Select-Object -Last 5) -join ' | ')
    } else { Write-Output "SKIP refactor-pass: no Git Bash at $bash" }
    # feature.js must parse as a Workflow script (an async function body; meta is an export). No Node here, so headless
    # Edge compiles it: the page prints OK or the SyntaxError.
    $edge = @("${env:ProgramFiles(x86)}\Microsoft\Edge\Application\msedge.exe", "$env:ProgramFiles\Microsoft\Edge\Application\msedge.exe") |
        Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
    if ($edge) {
        $js = [IO.File]::ReadAllText((Join-Path $PSScriptRoot 'workflows\feature.js')) -replace '(?m)^export const meta', 'const meta'
        $page = Join-Path $tmp 'parse-feature.html'
        [IO.File]::WriteAllText($page, '<!doctype html><meta charset="utf-8"><textarea id="s">' + [Net.WebUtility]::HtmlEncode($js) + '</textarea><pre id="r"></pre><script>' +
            "try { new (Object.getPrototypeOf(async function () {}).constructor)('args', 'agent', 'parallel', 'phase', 'log', document.getElementById('s').value); r.textContent = 'PARSE-OK' }" +
            " catch (e) { r.textContent = 'PARSE-ERROR ' + e.name + ': ' + e.message }</script>", $utf8)
        $psi = New-Object Diagnostics.ProcessStartInfo $edge
        $psi.Arguments = "--headless --disable-gpu --no-first-run --user-data-dir=`"$(Join-Path $tmp 'edge')`" --dump-dom `"$(([Uri]$page).AbsoluteUri)`""
        $psi.UseShellExecute = $false; $psi.RedirectStandardOutput = $true; $psi.RedirectStandardError = $true
        $PSScriptRoot = [Diagnostics.Process]::Start($psi); $out = $PSScriptRoot.StandardOutput.ReadToEndAsync(); $null = $PSScriptRoot.StandardError.ReadToEndAsync()
        if (-not $PSScriptRoot.WaitForExit(60000)) { $PSScriptRoot.Kill() }
        $res = [regex]::Match($out.Result, 'PARSE-(OK|ERROR[^<]*)').Value
        Check 'feature.js: parses as a Workflow script' ($res -eq 'PARSE-OK') $(if ($res) { $res } else { 'no answer from headless Edge' })
    } else { Write-Output 'SKIP feature.js parse: no Microsoft Edge' }
} finally {
    Remove-Item -LiteralPath $tmp -Recurse -Force -ErrorAction SilentlyContinue
}
if ($failed) { Write-Output "$failed check(s) failed"; exit 1 }
Write-Output 'All checks passed'
exit 0
