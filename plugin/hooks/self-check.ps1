# Stop hook (gamekit plugin): the self-check before Claude ends a turn. In a project with the AgentBridge (Logs/agent/compile.log),
# it waits for a pending refresh to finish, refuses the stop once if the last compile has errors and no script changed
# since, and sends Claude back once to run the gate if a script is newer than the last compile (errors in a log that
# old may already be fixed: Unity closed, or a refresh SKIPPED in Play Mode, leaves compile.log as it was).
# Everywhere else it does nothing.
# Ceiling: it judges the whole project, not only this turn's edits, so broken code from an earlier turn or a script
# the user saved in their IDE also blocks once. stop_hook_active lets the second stop through, so it can never loop.
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding = [System.Text.Encoding]::UTF8
$hook = $null
try { $hook = [Console]::In.ReadToEnd() | ConvertFrom-Json } catch { exit 0 }
if ($hook.stop_hook_active) { exit 0 }
# A running /gamekit:feature workflow has its own builder gating its units; blocking here would make this session a
# second writer on code the builder owns. Any other workflow (name: meta.name, with or without the plugin prefix)
# leaves the check on. A background `gk-bridge build` or `run-tests` compiles the edits itself, and until it reports
# no other bridge request may be sent (project CLAUDE.md), so sending Claude back to refresh would break that rule.
# Payload contract (checked against Claude Code 2.1.285): Stop input background_tasks[] holds in-flight tasks with
# type ('shell', 'workflow', ...), name (workflow only) and command (shell only); it is absent on older versions.
$busy = $hook.background_tasks | Where-Object {
    ($_.type -eq 'workflow' -and [string]$_.name -match '(^|:)feature$') -or
    ($_.type -eq 'shell' -and [string]$_.command -match 'gk-bridge(\.sh)?["'']?\s+(build|run-tests)\b') }
if (@($busy).Count) { exit 0 }

$dir = if ($env:CLAUDE_PROJECT_DIR) { $env:CLAUDE_PROJECT_DIR } else { $hook.cwd }
$agent = Join-Path $dir 'Logs\agent'
$compileLog = Join-Path $agent 'compile.log'
if (-not (Test-Path -LiteralPath $compileLog)) { exit 0 }

# The PostToolUse hook queues a refresh after every .cs/.asmdef edit and every `git rm`/`git mv` (a deleted script
# leaves no newer file for the stale test below; a plain `rm` is not caught); wait until the bridge has compiled it.
# Ceiling: an `if` pattern longer than the command name also fires on any command with $(), backticks or $VAR (hooks
# doc), so a few unrelated commands queue an extra refresh too; it costs one import, never a wrong verdict.
$request = Join-Path $agent 'request.txt'
$bridgeLog = Join-Path $agent 'bridge.log'
# Only a running Editor (it holds Temp/UnityLockfile open) ever consumes the request; with Unity closed, do not wait.
$lock = Join-Path $dir 'Temp\UnityLockfile'
$editorOpen = $false
if (Test-Path -LiteralPath $lock) {
    try { [IO.File]::Open($lock, 'Open', 'Read', 'None').Dispose() } catch { $editorOpen = $true }
}
$deadline = if ($editorOpen) { (Get-Date).AddSeconds(45) } else { Get-Date }
# The bridge reads request.txt from EditorApplication.update and answers REFRESHING at once; a request still pending
# after 10 s with no REFRESHING was not taken (a modal dialog, such as the API Updater or a save prompt, or a long
# import holds the Editor), so stop waiting and send Claude to the gate below instead of hanging 45 s every Stop.
$untaken = $false
while ((Get-Date) -lt $deadline) {
    $pending = (Test-Path -LiteralPath $request) -and (Get-Item -LiteralPath $request).Length -gt 0
    # A REFRESHING line older than a minute was left by a closed or crashed Editor; do not wait on it.
    $refreshing = (Test-Path -LiteralPath $bridgeLog) -and
        ((Get-Item -LiteralPath $bridgeLog).LastWriteTime -gt (Get-Date).AddSeconds(-60)) -and
        ((Get-Content -LiteralPath $bridgeLog -Tail 1) -match '^REFRESHING')
    if (-not $pending -and -not $refreshing) { break }
    if ($pending -and -not $refreshing -and (Get-Item -LiteralPath $request).LastWriteTime -lt (Get-Date).AddSeconds(-10)) {
        $untaken = $true; break
    }
    Start-Sleep -Milliseconds 500
}

# Guidance, not an error: Stop hookSpecificOutput.additionalContext is non-error feedback and the conversation continues
# so Claude can act on it (Claude Code 2.1.285 hook output schema).
function Send-Guidance([string]$text) {
    @{ hookSpecificOutput = @{ hookEventName = 'Stop'; additionalContext = "Self-check: $text" } } | ConvertTo-Json -Compress
}
$gate = 'Run `gk-bridge refresh` in Bash; if it stays UNKNOWN (exit 2), say in the handoff that the compile is unverified.'
$waitNote = if ($untaken) { ' The Editor has not taken the queued refresh for 10 s: it may be waiting on a dialog, so ask the user to check Unity.' } else { '' }

# A compile.log older than a script means that edit never compiled (Editor closed, busy, in Play Mode where a refresh
# is SKIPPED, or the refresh never ran). A refresh that found "no script changes" saw every edit, so it counts as fresh
# too. Feel is skipped: it is a vendored asset nobody edits.
# Ceiling: a script copied with its old time (Copy-Item, `cp -p`) looks compiled; `gk-bridge refresh` after a copy.
$since = (Get-Item -LiteralPath $compileLog).LastWriteTime
if (Test-Path -LiteralPath $bridgeLog) {
    $bridgeTime = (Get-Item -LiteralPath $bridgeLog).LastWriteTime
    if ((Get-Content -LiteralPath $bridgeLog -TotalCount 1) -match 'no script changes' -and $bridgeTime -gt $since) { $since = $bridgeTime }
}
# Runs at every Stop, so it walks paths as strings ([IO.Directory] enumerates lazily, no FileInfo per texture or mesh)
# and stops at the first stale script. It walks one folder at a time, so an unreadable folder (access denied, a path
# over 260 characters) skips only itself, never its siblings, and is never a wrong block.
function Find-StaleScript {
    foreach ($top in 'Assets', 'Packages') {
        $topPath = Join-Path $dir $top
        if (-not [IO.Directory]::Exists($topPath)) { continue }
        $todo = New-Object 'System.Collections.Generic.Stack[string]'
        $todo.Push($topPath)
        while ($todo.Count) {
            $d = $todo.Pop()
            try {
                foreach ($file in [IO.Directory]::EnumerateFiles($d)) {
                    if ([IO.Path]::GetExtension($file) -in '.cs', '.asmdef', '.asmref' -and
                        [IO.File]::GetLastWriteTime($file) -gt $since) { return $file.Substring($dir.Length).TrimStart('\', '/') }
                }
            } catch { }
            try {
                foreach ($sub in [IO.Directory]::EnumerateDirectories($d)) {
                    if ($d -ne $topPath -or [IO.Path]::GetFileName($sub) -ne 'Feel') { $todo.Push($sub) }
                }
            } catch { }
        }
    }
    return $null
}

$lines = @(Get-Content -LiteralPath $compileLog -Encoding UTF8)
if ($lines.Count -gt 0 -and $lines[0] -match '^([1-9]\d* error|FAILED)') {
    # Errors with a script edited since may already be fixed: guidance, not a block, so a fixed error never costs a
    # forced round on every later prompt while Unity is closed or in Play Mode.
    $stale = Find-StaleScript
    if ($stale) {
        Send-Guidance "Logs/agent/compile.log reports $($lines[0].Trim()), but $stale is newer, so those errors may be stale.$waitNote $gate"
        exit 0
    }
    $errors = ($lines | Select-Object -Skip 1 | Where-Object { $_ -match '\): error ' } | Select-Object -First 5) -join "`n"
    # A FAILED compile with no CS line in that format (AgentBridge writes "compile failed without a CS error"): show the
    # log's other lines, and with none, where the cause is, so the list is never empty.
    if (-not $errors) { $errors = ($lines | Select-Object -Skip 1 | Where-Object { $_.Trim() } | Select-Object -First 5) -join "`n" }
    if (-not $errors) { $errors = 'No CS error lines in compile.log: read Logs/agent/console.log (else the Editor.log) for the cause.' }
    @{
        decision = 'block'
        reason   = "Self-check: Logs/agent/compile.log reports $($lines[0].Trim()). Fix these before finishing:`n$errors"
    } | ConvertTo-Json -Compress
    exit 0
}

# A clean log is checked only with the Editor open: closed, nothing could compile the edit, and the next session's
# Editor start compiles it. No bridge.log: a bridge that has not answered a refresh yet (GameKit 0.1.1+ writes it when
# the Editor starts; older ones on their first refresh, the oldest copies never), so the PostToolUse hook queued
# nothing that would compile the edit.
if (-not $editorOpen -or -not (Test-Path -LiteralPath $bridgeLog)) { exit 0 }
$stale = Find-StaleScript
if ($stale) { Send-Guidance "$stale is newer than the last compile, so that edit is not verified.$waitNote $gate"; exit 0 }
# A `git rm` leaves no newer file, so an untaken request is the only sign that its compile never ran.
if ($untaken) { Send-Guidance "a refresh is queued but not compiled yet, so the last edit is not verified.$waitNote $gate" }
