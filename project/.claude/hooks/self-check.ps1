# Stop hook: the self-check before Claude ends a turn. In a project with the AgentBridge (Logs/agent/compile.log),
# it waits for a pending refresh to finish and refuses the stop once if the last compile has errors, so Claude fixes
# them before handing over. Everywhere else it does nothing.
# Ceiling: it judges the whole project's last compile, not only this turn's edits, so broken code left from an earlier
# turn also blocks once. stop_hook_active lets the second stop through, so it can never loop.
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$hook = [Console]::In.ReadToEnd() | ConvertFrom-Json
if ($hook.stop_hook_active) { exit 0 }

$dir = if ($env:CLAUDE_PROJECT_DIR) { $env:CLAUDE_PROJECT_DIR } else { $hook.cwd }

# A project that ships its own hooks (games from unity-game-template) runs them itself; a global copy steps aside.
$own = Join-Path $dir '.claude\hooks'
if ((Test-Path (Join-Path $own 'self-check.ps1')) -and
    -not [IO.Path]::GetFullPath($PSCommandPath).StartsWith([IO.Path]::GetFullPath($own), 'OrdinalIgnoreCase')) { exit 0 }
$agent = Join-Path $dir 'Logs\agent'
$compileLog = Join-Path $agent 'compile.log'
if (-not (Test-Path $compileLog)) { exit 0 }

# The PostToolUse hook queues a refresh after every .cs edit; wait until the bridge has picked it up and compiled.
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
if ($lines.Count -eq 0 -or $lines[0] -notmatch '^([1-9]\d* error|FAILED)') { exit 0 }

$errors = ($lines | Select-Object -Skip 1 | Where-Object { $_ -match '\): error ' } | Select-Object -First 5) -join "`n"
@{
    decision = 'block'
    reason   = "Self-check: Logs/agent/compile.log reports $($lines[0].Trim()). Fix these before finishing:`n$errors"
} | ConvertTo-Json -Compress
