# PreToolUse guard for hand edits of Unity YAML: scenes, prefabs, assets and the other Editor-serialized types in $yaml
# below. Never hand-edit them while an Editor has their project open: the running Editor does not see the change and
# overwrites it on its next save; a new file is not overwritten, but hand-written YAML gets fileIDs and GUID references
# wrong where the Editor would write them right. The gamekit plugin's hooks/hooks.json runs this only for matching
# extensions (`if`), so other edits and shell commands never start PowerShell. hooks.json is generated from $yaml:
# add a type here, then run plugin\test-hooks.ps1 -Write (the plain run fails while the two differ).
# The Edit/Write rules are rooted (`Edit(//**/*.prefab)`): a bare `Edit(*.prefab)` matches only under the session's
# folder, so a sibling game's file would never reach this script.
#
# Edit/Write are checked by file_path. Bash/PowerShell commands are checked by a heuristic: a write verb (redirect,
# sed -i, tee, Set-Content, Copy-Item, ...) in a command that names a YAML file. It catches the usual one-liners, not a
# script file that writes YAML on its own, and it also stops a copy whose source is project YAML; a hard block in every
# case would need permission deny rules, which would also block edits with the Editor closed.
# Each path is judged by the Unity project that owns it (the nearest folder up with ProjectSettings\ProjectVersion.txt),
# not by the session's folder: an edit in a sibling game is checked against that game's Editor, and a file in no
# project (a %TEMP% scratch copy) passes.

# The deny reason carries full paths; Claude Code reads UTF-8, not the console's OEM code page.
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
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
$yaml = '\.(unity|prefab|asset|mat|controller|overrideController|anim|mask|mixer|playable|signal|lighting|preset|terrainlayer|renderTexture|spriteatlasv2|physicMaterial|physicsMaterial|physicsMaterial2D)(?![\w.])'
$tool = [string]$payload.tool_name
# Relative paths in a command resolve against the shell's folder; the session's project is the fallback.
$cwd = if ($payload.cwd) { [string]$payload.cwd } else { $env:CLAUDE_PROJECT_DIR }

# The Unity project folder that owns $p, or $null. Git Bash /c/... paths and forward slashes are accepted.
function Get-UnityProject([string]$p) {
    if (-not $p) { return $null }
    # The shell expands ~, $HOME, $env:NAME (PowerShell) and $NAME / ${NAME} (Bash) before it writes; a variable this
    # process cannot resolve leaves the path unjudged rather than resolved against the session folder.
    if ($p -match '^~(?=[\\/]|$)') { $p = $env:USERPROFILE + $p.Substring(1) }
    foreach ($m in [regex]::Matches($p, '\$(?:env:)?\{?(\w+)\}?')) {
        $n = $m.Groups[1].Value
        $v = switch ($n) { 'HOME' { $env:USERPROFILE } 'PWD' { $cwd } default { [Environment]::GetEnvironmentVariable($n) } }
        if (-not $v) { return $null }
        $p = $p.Replace($m.Value, $v)
    }
    $p = ($p.Trim() -replace '^/([a-zA-Z])/', '$1:/') -replace '/', '\'
    if (-not [IO.Path]::IsPathRooted($p)) {
        if (-not $cwd) { return $null }
        $p = Join-Path $cwd $p
    }
    try { $d = [IO.Path]::GetDirectoryName([IO.Path]::GetFullPath($p)) } catch { return $null }
    while ($d) {
        if (Test-Path -LiteralPath (Join-Path $d 'ProjectSettings\ProjectVersion.txt') -PathType Leaf) { return $d }
        $d = [IO.Path]::GetDirectoryName($d)
    }
    return $null
}

if ($tool -eq 'Bash' -or $tool -eq 'PowerShell') {
    $command = [string]$payload.tool_input.command
    # A redirect target may be quoted with spaces inside ("Assets/My Scene.unity").
    $redirect = ">{1,2}\s*(`"[^`"]*|'[^']*|[^\s`"'|;&]*)$yaml"
    # PowerShell aliases (sc, ac, ni, cpi, copy, move, ren) write as their cmdlets do.
    $verb = '(^|[\s;|&(])(sed\s+(-\w+\s+)*-i|perl\s+-\w*i|tee|truncate|cp|mv|Set-Content|Add-Content|Clear-Content|Out-File|Copy-Item|Move-Item|New-Item|Rename-Item|sc|ac|ni|cpi|copy|move|ren)\b|WriteAll(Text|Lines|Bytes)'
    $writes = $command -match $redirect -or ($command -match $verb -and $command -match $yaml)
    if (-not $writes) { exit 0 }
    # Quoted paths first, so a name with spaces stays whole.
    $paths = @([regex]::Matches($command, "`"(?<p>[^`"]*$yaml)`"|'(?<p>[^']*$yaml)'|(?<p>[^\s`"'|;&>(]+$yaml)") | ForEach-Object { $_.Groups['p'].Value })
    # No path token: judge by the shell's folder.
    if (-not $paths) { $paths = @(Join-Path ([string]$cwd) 'x.unity') }
    $what = 'a Unity YAML file'
    $new = $false
} else {
    $paths = @([string]$payload.tool_input.file_path)
    $what = $paths[0]
    $new = $paths[0] -and -not (Test-Path -LiteralPath $paths[0] -PathType Leaf)
}
$projects = @($paths | ForEach-Object { Get-UnityProject $_ } | Where-Object { $_ } | Sort-Object -Unique)
if (-not $projects) { exit 0 }

function Deny([string]$reason) {
    @{ hookSpecificOutput = @{
        hookEventName = 'PreToolUse'
        permissionDecision = 'deny'
        permissionDecisionReason = $reason
    } } | ConvertTo-Json -Compress -Depth 4
    exit 0
}

foreach ($project in $projects) {
    $lock = Join-Path $project 'Temp\UnityLockfile'
    $editorOpen = $false
    # A running Editor holds Temp/UnityLockfile open; a lockfile left by a crash can be opened exclusively.
    if (Test-Path -LiteralPath $lock) {
        try { [IO.File]::Open($lock, 'Open', 'Read', 'None').Dispose() }
        catch { $editorOpen = $true }
    }
    if (-not $editorOpen) {
        # Fallback for a lockfile that cannot be read. Unity 6 titles read "<Project> - <Scene> - <Platform> - Unity
        # ...", so the separator keeps an open 'RunnerDeluxe' from matching the closed project 'Runner'.
        $name = Split-Path $project -Leaf
        $editorOpen = [bool](Get-Process -Name Unity -ErrorAction SilentlyContinue |
            Where-Object { $_.MainWindowTitle -like "$name - *" })
    }
    if ($editorOpen) {
        if ($new) {
            Deny "The Unity Editor has $project open, so create $what through the Editor, not by hand: hand-written Unity YAML gets fileIDs and GUID references wrong, and the Editor writes them and the .meta right. Drive the Editor instead (unity-editor-cli: unity command script run)."
        }
        Deny "The Unity Editor has $project open, so $what must not be hand-edited: the Editor will not see the change and overwrites it on its next save. Drive the Editor instead (unity-editor-cli: unity command script run)."
    }
}

exit 0
