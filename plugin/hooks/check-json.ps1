# PostToolUse check (gamekit plugin): after Edit or Write on a .json, .asmdef or .asmref file, parse it. A broken
# Packages/manifest.json or asmdef sends Unity into a Package Manager error or a failed compile on next focus, and
# gk-bridge then answers UNKNOWN without naming the cause. The write already happened, so this cannot undo it: it
# blocks once with the parse error, so Claude fixes the file in the same turn. Unity reads these as plain JSON (no
# comments). hooks/hooks.json runs it only for matching extensions (`if`).
# Ceiling: the PowerShell 5.1 parser is more lenient than Unity's on a few syntax errors, so this catches broken
# structure (a lost brace, quote or comma), not every strictness issue; the compile gate catches the rest. It is also
# stricter on two things Unity never sees: // comments (JSONC) and keys that differ only in case. So editor configs
# that allow JSONC (.vscode\, tsconfig*.json, jsconfig*.json) are skipped below; add a path there if another shows up.
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$stdin = [Console]::OpenStandardInput()
$buffer = New-Object IO.MemoryStream
$stdin.CopyTo($buffer)
try {
    # A PowerShell pipe prepends a BOM; Claude Code sends raw UTF-8.
    $payload = [Text.Encoding]::UTF8.GetString($buffer.ToArray()).TrimStart([char]0xFEFF) | ConvertFrom-Json
} catch { exit 0 }

$path = [string]$payload.tool_input.file_path
if ($path -notmatch '\.(json|asmdef|asmref)$' -or -not (Test-Path -LiteralPath $path -PathType Leaf)) { exit 0 }
# Generated or third-party folders: not Claude's to fix. Library/Temp/Logs only at the project root, so a file under
# %TEMP% (AppData\Local\Temp) is still checked.
$root = if ($env:CLAUDE_PROJECT_DIR) { $env:CLAUDE_PROJECT_DIR } else { [string]$payload.cwd }
$rel = ($path -replace '/', '\')
$base = ($root -replace '/', '\').TrimEnd('\') + '\'
if ($root -and $rel.StartsWith($base, 'OrdinalIgnoreCase')) { $rel = $rel.Substring($base.Length) }
if ($rel -match '^(Library|Temp|Logs)\\' -or $rel -match '(^|\\)(node_modules|\.vscode)\\' -or
    $rel -match '(^|\\)[tj]sconfig[^\\]*\.json$') { exit 0 }

$text = [IO.File]::ReadAllText($path, [Text.Encoding]::UTF8)
$problem = $null
if ([string]::IsNullOrWhiteSpace($text)) {
    $problem = 'the file is empty'
} else {
    try { $null = $text | ConvertFrom-Json -ErrorAction Stop } catch { $problem = $_.Exception.Message }
}
if (-not $problem) { exit 0 }
# A structural error (lost brace or bracket) ends the message with "(<offset>): <the whole input>"; keep the offset only.
$parts = $problem -split '\): ', 2
if ($parts.Count -eq 2) { $problem = $parts[0] + ')' }
if ($problem.Length -gt 300) { $problem = $problem.Substring(0, 300) + '...' }

@{
    decision = 'block'
    reason   = "check-json: $path is not valid JSON ($problem). The edit is written but the file is broken: fix it now. Unity will not resolve packages or compile that assembly until it parses."
} | ConvertTo-Json -Compress
exit 0
