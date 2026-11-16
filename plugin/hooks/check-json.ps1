# PostToolUse check (gamekit plugin): after Edit or Write on a .json, .asmdef or .asmref file, or a Bash/PowerShell
# command that writes (redirect or write verb) and names one, parse each such file. A broken
# Packages/manifest.json or asmdef sends Unity into a Package Manager error or a failed compile on next focus, and
# gk-bridge then answers UNKNOWN without naming the cause. The write already happened, so this cannot undo it: it
# blocks once with the parse error, so Claude fixes the file in the same turn. Unity reads these as plain JSON (no
# comments) and as UTF-8, so a UTF-16 file (PowerShell 5.1 Out-File) blocks too. hooks/hooks.json runs it only for
# matching extensions (`if`, rooted so a sibling game's file counts too; a shell command by `*.json*` and the like);
# that file is generated from the extension list below by plugin\test-hooks.ps1 -Write.
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

$cwd = if ($payload.cwd) { [string]$payload.cwd } else { $env:CLAUDE_PROJECT_DIR }
$tool = [string]$payload.tool_name
if ($tool -eq 'Bash' -or $tool -eq 'PowerShell') {
    # A shell write (a heredoc, ConvertTo-Json | Out-File, sed -i): the same write-verb heuristic as guard-unity-yaml
    # (test-hooks.ps1 keeps the two lists equal); every file the command names is checked, relative ones against cwd.
    $command = [string]$payload.tool_input.command
    $verb = '(^|[\s;|&(])(sed\s+(-\w+\s+)*-i|perl\s+-\w*i|tee|truncate|cp|mv|Set-Content|Add-Content|Clear-Content|Out-File|Copy-Item|Move-Item|New-Item|Rename-Item|sc|ac|ni|cpi|copy|move|ren)\b|WriteAll(Text|Lines|Bytes)'
    if ($command -notmatch '>' -and $command -notmatch $verb) { exit 0 }
    $paths = @([regex]::Matches($command, "`"(?<p>[^`"]*\.(json|asmdef|asmref))`"|'(?<p>[^']*\.(json|asmdef|asmref))'|(?<p>[^\s`"'|;&<>(]+\.(json|asmdef|asmref))(?![\w.])") |
        ForEach-Object { ($_.Groups['p'].Value.Trim() -replace '^/([a-zA-Z])/', '$1:/') -replace '/', '\' } |
        Where-Object { $_ -notmatch '[$~]' } | ForEach-Object { if ([IO.Path]::IsPathRooted($_) -or -not $cwd) { $_ } else { Join-Path $cwd $_ } } |
        Sort-Object -Unique)
} else {
    $paths = @([string]$payload.tool_input.file_path)
}

# Generated or third-party folders: not Claude's to fix. Library/Temp/Logs only at the project root, so a file under
# %TEMP% (AppData\Local\Temp) is still checked.
$root = if ($env:CLAUDE_PROJECT_DIR) { $env:CLAUDE_PROJECT_DIR } else { [string]$payload.cwd }
$base = ($root -replace '/', '\').TrimEnd('\') + '\'
$problems = foreach ($path in $paths) {
    if ($path -notmatch '\.(json|asmdef|asmref)$' -or -not (Test-Path -LiteralPath $path -PathType Leaf)) { continue }
    $rel = ($path -replace '/', '\')
    if ($root -and $rel.StartsWith($base, 'OrdinalIgnoreCase')) { $rel = $rel.Substring($base.Length) }
    if ($rel -match '^(Library|Temp|Logs)\\' -or $rel -match '(^|\\)(node_modules|\.vscode)\\' -or
        $rel -match '(^|\\)[tj]sconfig[^\\]*\.json$') { continue }

    $bytes = [IO.File]::ReadAllBytes($path)
    $problem = $null
    if ($bytes.Length -ge 2 -and (($bytes[0] -eq 0xFF -and $bytes[1] -eq 0xFE) -or ($bytes[0] -eq 0xFE -and $bytes[1] -eq 0xFF))) {
        # PowerShell 5.1's Out-File and > write UTF-16; Unity reads these files as UTF-8.
        $problem = 'it is UTF-16, which Windows PowerShell 5.1 Out-File and > write; rewrite it as UTF-8 without a BOM, e.g. [IO.File]::WriteAllText(path, text, (New-Object Text.UTF8Encoding $false))'
    } else {
        $text = [Text.Encoding]::UTF8.GetString($bytes).TrimStart([char]0xFEFF)
        if ([string]::IsNullOrWhiteSpace($text)) {
            $problem = 'the file is empty'
        } else {
            try { $null = $text | ConvertFrom-Json -ErrorAction Stop } catch { $problem = $_.Exception.Message }
        }
    }
    if (-not $problem) { continue }
    # A structural error (lost brace or bracket) ends the message with "(<offset>): <the whole input>"; keep the offset only.
    $parts = $problem -split '\): ', 2
    if ($parts.Count -eq 2) { $problem = $parts[0] + ')' }
    if ($problem.Length -gt 300) { $problem = $problem.Substring(0, 300) + '...' }
    "$path is not valid JSON ($problem)"
}
if (-not $problems) { exit 0 }

@{
    decision = 'block'
    reason   = "check-json: $(@($problems) -join '; '). The write happened but the file is broken: fix it now. Unity will not resolve packages or compile that assembly until it parses."
} | ConvertTo-Json -Compress
exit 0
