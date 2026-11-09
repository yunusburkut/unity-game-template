# PreToolUse guard for Edit/Write on Unity YAML (.unity, .prefab, .asset, .mat, .controller, .mask, .anim,
# .overrideController).
# Never hand-edit them while an Editor has this project open: the running Editor does not see the change and
# overwrites it on its next save. settings.json runs this only for matching extensions (`if`), so other edits
# never start PowerShell.

$stdin = [Console]::OpenStandardInput()
$buffer = New-Object IO.MemoryStream
$stdin.CopyTo($buffer)
try {
    # A PowerShell pipe prepends a BOM; Claude Code sends raw UTF-8.
    $payload = [Text.Encoding]::UTF8.GetString($buffer.ToArray()).TrimStart([char]0xFEFF) | ConvertFrom-Json
} catch {
    [Console]::Error.WriteLine("guard-unity-yaml: unreadable hook input, edit not checked: $_")
    exit 1
}

$path = [string]$payload.tool_input.file_path

function Deny([string]$reason) {
    @{ hookSpecificOutput = @{
        hookEventName = 'PreToolUse'
        permissionDecision = 'deny'
        permissionDecisionReason = $reason
    } } | ConvertTo-Json -Compress -Depth 4
    exit 0
}

$root = if ($env:CLAUDE_PROJECT_DIR) { $env:CLAUDE_PROJECT_DIR } else { [string]$payload.cwd }
$lock = Join-Path $root 'Temp\UnityLockfile'
$editorOpen = $false

# A running Editor holds Temp/UnityLockfile open; a lockfile left by a crash can be opened exclusively.
if (Test-Path -LiteralPath $lock) {
    try { [IO.File]::Open($lock, 'Open', 'Read', 'None').Dispose() }
    catch { $editorOpen = $true }
}

if (-not $editorOpen) {
    $project = Split-Path $root -Leaf
    $editorOpen = [bool](Get-Process -Name Unity -ErrorAction SilentlyContinue |
        Where-Object { $_.MainWindowTitle -like "$project*" })
}

if ($editorOpen) {
    Deny "The Unity Editor has this project open, so $path must not be hand-edited: the Editor will not see the change and overwrites it on its next save. Drive the Editor instead (unity-editor-cli: unity command script run), or ask the user to close Unity first."
}

exit 0
