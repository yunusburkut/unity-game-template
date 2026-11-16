# PreToolUse for the live mcp__Blender__* tools: they talk to the MCP add-on inside a running Blender on
# localhost:9876 (BLENDER_MCP_HOST and BLENDER_MCP_PORT override both, as they do for the extension). When Blender is
# closed, start it and wait for the add-on's server, so a live call works in any session without a manual step (agents
# call a live tool only when the user asks to see Blender: blender-director).
# The docs tools need no Blender: the hooks.json matcher keeps them from starting this script at all, and the check
# below passes them anyway. The *_for_cli tools need no running Blender either, but they time out unless the Claude
# extension's blender_cli.py keeps a local patch (stdin=subprocess.DEVNULL), which an extension update overwrites; this
# hook checks for it, so the loss blocks at once with the fix instead of a timeout.
# Exit 0 lets the call run; exit 2 blocks it and stderr tells Claude what the user has to fix.
# Time budget: hooks.json gives this hook 120 s. The slowest path (a Blender window just opened, or a launch) stays
# under about 85 s, and a parallel call waits at most 90 s for the first one and then only probes, so neither is
# killed by the timeout (a killed hook lets the call through to a raw connection error).
# Pure ASCII on purpose: Windows PowerShell 5.1 reads a BOM-less script as ANSI.

$ErrorActionPreference = 'Stop'
# The messages carry paths (BLENDER_PATH, the profile folder); Claude Code reads UTF-8, not the console's code page.
[Console]::OutputEncoding = [Text.Encoding]::UTF8
try {
    $buffer = New-Object IO.MemoryStream
    [Console]::OpenStandardInput().CopyTo($buffer)
    # A PowerShell pipe prepends a BOM; Claude Code sends raw UTF-8.
    $tool = ([Text.Encoding]::UTF8.GetString($buffer.ToArray()).TrimStart([char]0xFEFF) | ConvertFrom-Json).tool_name
} catch { exit 0 }
if (-not $tool -or $tool -like '*docs*') { exit 0 }

if ($tool -like '*_for_cli') {
    $ext = 'Claude Extensions\ant.dir.gh.blender.blender-mcp'
    $copies = @(Get-ChildItem "$env:LOCALAPPDATA\Claude-Data\*\$ext\blmcp\tools_helpers\blender_cli.py" -ErrorAction SilentlyContinue)
    if (-not $copies.Count) {
        # The extension is installed but blender_cli.py is gone: an update moved it, and this check would pass blind.
        $dirs = @(Get-ChildItem "$env:LOCALAPPDATA\Claude-Data\*\$ext" -Directory -ErrorAction SilentlyContinue)
        if ($dirs.Count) {
            @{ systemMessage = "ensure-blender: $($dirs[0].FullName) has no blmcp\tools_helpers\blender_cli.py any more, so the stdin=subprocess.DEVNULL patch the *_for_cli tools need cannot be checked. If *_for_cli calls time out, find the file that runs Blender with subprocess.run(...) and add that argument; then update the path in the gamekit plugin's hooks\ensure-blender.ps1." } | ConvertTo-Json -Compress
        }
        exit 0
    }
    # The copy that counts is the one the running server was started from (one Claude profile per copy); the
    # installer keeps archive times, so with no server running the newest file is only a guess at the active copy.
    # One copy needs no process query. GK_BLENDER_MCP_LIVE (paths split by ';') stands in for it in plugin\test-hooks.ps1.
    $cli = $copies[0]
    if ($copies.Count -gt 1) {
        $live = if ($env:GK_BLENDER_MCP_LIVE) { $env:GK_BLENDER_MCP_LIVE -split ';' } else {
            @(try { Get-CimInstance Win32_Process -Filter "Name='blender-mcp.exe'" -ErrorAction Stop | ForEach-Object ExecutablePath } catch { }) }
        $cli = @($copies | Where-Object { $root = $_.FullName.Substring(0, $_.FullName.IndexOf($ext) + $ext.Length)
                @($live | Where-Object { $_ -and $_.StartsWith($root + '\', [StringComparison]::OrdinalIgnoreCase) }).Count }) +
            @($copies | Sort-Object LastWriteTime -Descending) | Select-Object -First 1
    }
    # The patch, or an upstream fix spelled another way (stdin=DEVNULL after a from-import, or input=... to feed stdin).
    if (-not (Select-String -LiteralPath $cli.FullName -Pattern 'stdin\s*=\s*(subprocess\.)?DEVNULL|\binput\s*=' -Quiet)) {
        [Console]::Error.WriteLine("The Blender MCP extension lost its local patch (an extension update overwrites it), so every *_for_cli call would time out: Blender inherits the MCP stdio pipe. Tell the user the fix: in $($cli.FullName) add the argument stdin=subprocess.DEVNULL, to the subprocess.run(...) call, then restart Claude so the extension reloads.")
        exit 2
    }
    exit 0
}

$hostName = if ($env:BLENDER_MCP_HOST) { $env:BLENDER_MCP_HOST } else { 'localhost' }
$port = 9876
if ($env:BLENDER_MCP_PORT -and -not [int]::TryParse($env:BLENDER_MCP_PORT, [ref]$port)) {
    [Console]::Error.WriteLine("BLENDER_MCP_PORT is '$env:BLENDER_MCP_PORT', not a port number: set it to the add-on's port (default 9876) or remove it.")
    exit 2
}
$at = "${hostName}:$port"

function Test-Port {
    $c = New-Object Net.Sockets.TcpClient
    try { return $c.ConnectAsync($hostName, $port).Wait(2000) -and $c.Connected } catch { return $false } finally { $c.Close() }
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
# others find its server. Abandoned (a killed hook) still means acquired. A call that had to wait never launches a
# second Blender: the first one's start already failed, and a second launch would overrun the time budget. One mutex
# per port, since only calls for the same server wait on each other (the tests use a free port and never queue).
$mutex = New-Object Threading.Mutex($false, "Local\gk-ensure-blender-$port")
$queued = $false
try {
    $owned = $mutex.WaitOne(0)
    if (-not $owned) { $queued = $true; $owned = $mutex.WaitOne(90000) }
} catch [Threading.AbandonedMutexException] { $owned = $true }
if (-not $owned) {
    [Console]::Error.WriteLine("Another Blender start is still waiting for $at after 90 s. $fix")
    exit 2
}
try {
    if (Test-Port) { exit 0 }
    if ($queued) {
        [Console]::Error.WriteLine("A parallel live call already waited for Blender, and its MCP server is still not open on $at. $fix")
        exit 2
    }

    # A --background run (bake, export, *_for_cli) has no window and no MCP server, so only a windowed Blender counts.
    $windowed = @(Get-Process blender -ErrorAction SilentlyContinue | Where-Object MainWindowHandle -ne 0)
    if ($windowed) {
        # Only a Blender that is still starting gets a grace period (the add-on starts its server a few seconds after
        # launch); one open for longer has its server off, and waiting would only delay the same answer. The wait is
        # the launch budget below minus the window's age, so this path stays inside the time budget too.
        $age = @($windowed | ForEach-Object { try { ((Get-Date) - $_.StartTime).TotalSeconds } catch { 1e9 } } | Sort-Object)[0]
        if ($age -lt 75 -and (Wait-Port ([Math]::Max(5, 75 - $age)))) { exit 0 }
        [Console]::Error.WriteLine("Blender is running but its MCP server is not listening on $at. $fix")
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
    # Any extension repository and any id with mcp in it (this machine: extensions\lab\mcp), or a legacy add-on.
    if ((Test-Path -LiteralPath $config) -and -not (Test-Path (Join-Path $config "$ver\extensions\*\*mcp*\__init__.py")) -and
        -not (Test-Path (Join-Path $config "$ver\scripts\addons\*mcp*\__init__.py"))) {
        [Console]::Error.WriteLine("The Blender MCP add-on is not installed for Blender $ver ($exe): install it in that version (the add-on and Allow Online Access are per version), or set BLENDER_PATH to the Blender that has it.")
        exit 2
    }

    # --online-mode: the add-on starts its server only with online access, whatever the saved preference says.
    try { Start-Process $exe '--online-mode' } catch {
        [Console]::Error.WriteLine("Could not start $exe ($($_.Exception.Message)). Set BLENDER_PATH to a working blender.exe.")
        exit 2
    }
    if (Wait-Port 75) { exit 0 }
    [Console]::Error.WriteLine("Started $exe but its MCP server did not open $at within 75 s. $fix")
    exit 2
} finally {
    $mutex.ReleaseMutex()
}
