# Stop hook (gamekit plugin): the self-check before Claude ends a turn. In a project with the AgentBridge (Logs/agent/compile.log),
# it waits for a pending refresh to finish, refuses the stop once if the last compile has errors, and sends Claude
# back once to run the gate if a script is newer than the last compile while the Editor is open. Everywhere else it
# does nothing.
# Ceiling: it judges the whole project, not only this turn's edits, so broken code from an earlier turn or a script
# the user saved in their IDE also blocks once. stop_hook_active lets the second stop through, so it can never loop.
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding = [System.Text.Encoding]::UTF8
$hook = $null
try { $hook = [Console]::In.ReadToEnd() | ConvertFrom-Json } catch { exit 0 }
if ($hook.stop_hook_active) { exit 0 }
# A running /gamekit:feature workflow has its own builder gating its units; blocking here would make this session a
# second writer on code the builder owns. Any other workflow (name: meta.name, with or without the plugin prefix)
# leaves the check on.
$feature = $hook.background_tasks | Where-Object { $_.type -eq 'workflow' -and [string]$_.name -match '(^|:)feature$' }
if (@($feature).Count) { exit 0 }

$dir = if ($env:CLAUDE_PROJECT_DIR) { $env:CLAUDE_PROJECT_DIR } else { $hook.cwd }
$agent = Join-Path $dir 'Logs\agent'
$compileLog = Join-Path $agent 'compile.log'
if (-not (Test-Path $compileLog)) { exit 0 }

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
while ((Get-Date) -lt $deadline) {
    $pending = (Test-Path $request) -and (Get-Item $request).Length -gt 0
    # A REFRESHING line older than a minute was left by a closed or crashed Editor; do not wait on it.
    $refreshing = (Test-Path $bridgeLog) -and ((Get-Item $bridgeLog).LastWriteTime -gt (Get-Date).AddSeconds(-60)) -and
        ((Get-Content $bridgeLog -Tail 1) -match '^REFRESHING')
    if (-not $pending -and -not $refreshing) { break }
    Start-Sleep -Milliseconds 500
}

$lines = @(Get-Content $compileLog -Encoding UTF8)
if ($lines.Count -gt 0 -and $lines[0] -match '^([1-9]\d* error|FAILED)') {
    $errors = ($lines | Select-Object -Skip 1 | Where-Object { $_ -match '\): error ' } | Select-Object -First 5) -join "`n"
    @{
        decision = 'block'
        reason   = "Self-check: Logs/agent/compile.log reports $($lines[0].Trim()). Fix these before finishing:`n$errors"
    } | ConvertTo-Json -Compress
    exit 0
}

# A clean compile.log older than a script means that edit never compiled (Editor busy, in Play Mode, or the refresh
# never ran). Checked only with the Editor open: closed, nothing could compile it. A refresh that found "no script
# changes" saw every edit, so it counts as fresh too. Feel is skipped: it is a vendored asset nobody edits.
# Ceiling: a script copied with its old time (Copy-Item, `cp -p`) looks compiled; `gk-bridge refresh` after a copy.
# No bridge.log: a bridge that has not answered a refresh yet (GameKit 0.1.1+ writes it when the Editor starts; older
# ones on their first refresh, the oldest copies never), so the PostToolUse hook queued nothing that would compile the
# edit.
if (-not $editorOpen -or -not (Test-Path $bridgeLog)) { exit 0 }
$since = (Get-Item $compileLog).LastWriteTime
if ((Test-Path $bridgeLog) -and (Get-Content $bridgeLog -TotalCount 1) -match 'no script changes' -and
    (Get-Item $bridgeLog).LastWriteTime -gt $since) { $since = (Get-Item $bridgeLog).LastWriteTime }
$stale = Get-ChildItem -Path (Join-Path $dir 'Assets'), (Join-Path $dir 'Packages') -Exclude Feel -ErrorAction SilentlyContinue |
    Get-ChildItem -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object { $_.Extension -in '.cs', '.asmdef', '.asmref' -and $_.LastWriteTime -gt $since } | Select-Object -First 1
if (-not $stale) { exit 0 }
$name = $stale.FullName.Substring($dir.Length).TrimStart('\', '/')
# Guidance, not an error: additionalContext continues the turn like block but shows as hook feedback (hooks doc, Stop).
@{
    hookSpecificOutput = @{
        hookEventName     = 'Stop'
        additionalContext = "Self-check: $name is newer than the last compile, so that edit is not verified. Run ``gk-bridge refresh`` in Bash; if it stays UNKNOWN (exit 2), say in the handoff that the compile is unverified."
    }
} | ConvertTo-Json -Compress
