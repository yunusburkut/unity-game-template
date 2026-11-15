# PreToolUse for mcp__Blender__*: the live tools talk to the MCP add-on inside a running Blender on
# localhost:9876. When Blender is closed, start it and wait for the add-on's server, so a live call works in
# any session without a manual step (agents call a live tool only when the user asks to see Blender: blender-director).
# The docs tools need no Blender and pass straight on. The *_for_cli tools need no running Blender either, but they
# time out unless the Claude extension's blender_cli.py keeps a local patch (stdin=subprocess.DEVNULL), which an
# extension update overwrites; this hook checks for it, so the loss blocks at once with the fix instead of a timeout.
# Exit 0 lets the call run; exit 2 blocks it and stderr tells Claude what the user has to fix.
# Pure ASCII on purpose: Windows PowerShell 5.1 reads a BOM-less script as ANSI.

$ErrorActionPreference = 'Stop'
try { $tool = ([Console]::In.ReadToEnd() | ConvertFrom-Json).tool_name } catch { exit 0 }
if (-not $tool -or $tool -like '*docs*') { exit 0 }

if ($tool -like '*_for_cli') {
    # The newest copy is the one an update just wrote; an older one belongs to an unused Claude profile.
    $cli = Get-ChildItem "$env:LOCALAPPDATA\Claude-Data\*\Claude Extensions\ant.dir.gh.blender.blender-mcp\blmcp\tools_helpers\blender_cli.py" -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if ($cli -and -not (Select-String -LiteralPath $cli.FullName -Pattern 'stdin=subprocess\.DEVNULL' -Quiet)) {
        [Console]::Error.WriteLine("The Blender MCP extension lost its local patch (an extension update overwrites it), so every *_for_cli call would time out: Blender inherits the MCP stdio pipe. Tell the user the fix: in $($cli.FullName) add the argument stdin=subprocess.DEVNULL, to the subprocess.run(...) call, then restart Claude so the extension reloads.")
        exit 2
    }
    exit 0
}

$port = if ($env:BLENDER_MCP_PORT) { [int]$env:BLENDER_MCP_PORT } else { 9876 }

function Test-Port {
    $c = New-Object Net.Sockets.TcpClient
    try { return $c.ConnectAsync('localhost', $port).Wait(2000) -and $c.Connected } catch { return $false } finally { $c.Close() }
}

function Wait-Port($seconds) {
    # Deadline, not a count: a refused connect to localhost costs ~2 s (IPv6, then IPv4).
    $sw = [Diagnostics.Stopwatch]::StartNew()
    while ($sw.Elapsed.TotalSeconds -lt $seconds) { if (Test-Port) { return $true }; Start-Sleep 1 }
    return $false
}

if (Test-Port) { exit 0 }

$fix = 'In Blender: Edit > Preferences > System > Allow Online Access on, then Add-ons > MCP > Start (and Auto Start on).'

# Live calls sent in one message run their hooks in parallel: one at a time, so only the first starts Blender and the
# others find its server. Abandoned (a killed hook) still means acquired.
$mutex = New-Object Threading.Mutex($false, 'Local\gk-ensure-blender')
try { $owned = $mutex.WaitOne(80000) } catch [Threading.AbandonedMutexException] { $owned = $true }
if (-not $owned) {
    [Console]::Error.WriteLine("Another Blender start is still waiting for localhost:$port after 80 s. $fix")
    exit 2
}
try {
    if (Test-Port) { exit 0 }

    # A --background run (bake, export, *_for_cli) has no window and no MCP server, so only a windowed Blender counts.
    $windowed = @(Get-Process blender -ErrorAction SilentlyContinue | Where-Object MainWindowHandle -ne 0)
    if ($windowed) {
        # Only a Blender that is still starting gets a grace period (the add-on starts its server a few seconds after
        # launch); one open for longer has its server off, and waiting would only delay the same answer.
        $age = @($windowed | ForEach-Object { try { ((Get-Date) - $_.StartTime).TotalSeconds } catch { 1e9 } } | Sort-Object)[0]
        if ($age -lt 90 -and (Wait-Port ([Math]::Max(5, 90 - $age)))) { exit 0 }
        [Console]::Error.WriteLine("Blender is running but its MCP server is not listening on localhost:$port. $fix")
        exit 2
    }

    $exe = $env:BLENDER_PATH
    if (-not $exe -or -not (Test-Path -LiteralPath $exe)) {
        # By version, not by name: 'Blender 5.10' sorts before 'Blender 5.9' as a string.
        $exe = Get-ChildItem 'C:\Program Files\Blender Foundation\Blender *\blender.exe' -ErrorAction SilentlyContinue |
            Sort-Object { $v = $_.VersionInfo; [version]('{0}.{1}.{2}' -f $v.FileMajorPart, $v.FileMinorPart, $v.FileBuildPart) } -Descending |
            Select-Object -First 1 -ExpandProperty FullName
    }
    if (-not $exe) {
        [Console]::Error.WriteLine('Blender is not running and blender.exe was not found. Set BLENDER_PATH to it.')
        exit 2
    }

    # The add-on is installed per Blender major.minor. Checked only where this machine keeps Blender settings in
    # %APPDATA% (not a portable install), so a new version without the add-on blocks now instead of after 75 s.
    $v = (Get-Item -LiteralPath $exe).VersionInfo
    $ver = '{0}.{1}' -f $v.FileMajorPart, $v.FileMinorPart
    $config = Join-Path $env:APPDATA 'Blender Foundation\Blender'
    if ((Test-Path -LiteralPath $config) -and -not (Test-Path (Join-Path $config "$ver\extensions\*\mcp\__init__.py"))) {
        [Console]::Error.WriteLine("The Blender MCP add-on is not installed for Blender $ver ($exe): install it in that version (the add-on and Allow Online Access are per version), or set BLENDER_PATH to the Blender that has it.")
        exit 2
    }

    # --online-mode: the add-on starts its server only with online access, whatever the saved preference says.
    Start-Process $exe '--online-mode'
    if (Wait-Port 75) { exit 0 }
    [Console]::Error.WriteLine("Started $exe but its MCP server did not open localhost:$port within 75 s. $fix")
    exit 2
} finally {
    $mutex.ReleaseMutex()
}
