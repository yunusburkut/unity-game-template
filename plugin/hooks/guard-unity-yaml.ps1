# PreToolUse guard for hand edits of Unity YAML (.unity, .prefab, .asset, .mat, .controller, .overrideController,
# .anim, .mask). Never hand-edit them while an Editor has this project open: the running Editor does not see the change
# and overwrites it on its next save. The gamekit plugin's hooks/hooks.json runs this only for matching extensions
# (`if`), so other edits and shell commands never start PowerShell.
#
# Edit/Write are checked by file_path. Bash/PowerShell commands are checked by a heuristic: a write verb (redirect,
# sed -i, tee, Set-Content, Copy-Item, ...) in a command that names a YAML file inside the project. It catches the usual
# one-liners, not a script file that writes YAML on its own, and it also stops a copy whose source is project YAML; a
# hard block in every case would need permission deny rules, which would also block edits with the Editor closed.

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

# Not followed by a word character or a dot, so package ids like com.unity.pipeline do not count as a .unity file.
$yaml = '\.(unity|prefab|asset|mat|controller|overrideController|anim|mask)(?![\w.])'
$tool = [string]$payload.tool_name
$root = if ($env:CLAUDE_PROJECT_DIR) { $env:CLAUDE_PROJECT_DIR } else { [string]$payload.cwd }

if ($tool -eq 'Bash' -or $tool -eq 'PowerShell') {
    $command = [string]$payload.tool_input.command
    $redirect = ">{1,2}\s*[`"']?[^\s`"'|;&]*$yaml"
    $verb = '(^|[\s;|&(])(sed\s+(-\w+\s+)*-i|perl\s+-\w*i|tee|truncate|cp|mv|Set-Content|Add-Content|Clear-Content|Out-File|Copy-Item|Move-Item|New-Item)\b|WriteAll(Text|Lines|Bytes)'
    $writes = $command -match $redirect -or ($command -match $verb -and $command -match $yaml)
    if (-not $writes) { exit 0 }

    # A command whose YAML paths are all absolute and outside the project (a scratch copy) is not this Editor's.
    $paths = [regex]::Matches($command, "[^\s`"'|;&>(]+$yaml") | ForEach-Object { ($_.Value -replace '^/([a-zA-Z])/', '$1:/') -replace '/', '\' }
    $inside = @($paths | Where-Object { -not [IO.Path]::IsPathRooted($_) -or $_.StartsWith($root, 'OrdinalIgnoreCase') })
    if ($paths -and $inside.Count -eq 0) { exit 0 }
    $path = 'a Unity YAML file'
} else {
    $path = [string]$payload.tool_input.file_path
}

function Deny([string]$reason) {
    @{ hookSpecificOutput = @{
        hookEventName = 'PreToolUse'
        permissionDecision = 'deny'
        permissionDecisionReason = $reason
    } } | ConvertTo-Json -Compress -Depth 4
    exit 0
}

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
