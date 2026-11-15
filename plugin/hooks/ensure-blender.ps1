# PreToolUse for mcp__Blender__*: the live tools talk to the MCP add-on inside a running Blender on
# localhost:9876. When Blender is closed, start it and wait for the add-on's server, so a live call works in
# any session without a manual step. The *_for_cli and docs tools need no running Blender and pass straight on.
# Exit 0 lets the call run; exit 2 blocks it and stderr tells Claude what the user has to fix.
# Pure ASCII on purpose: Windows PowerShell 5.1 reads a BOM-less script as ANSI.

$ErrorActionPreference = 'Stop'
try { $tool = ([Console]::In.ReadToEnd() | ConvertFrom-Json).tool_name } catch { exit 0 }
if (-not $tool -or $tool -like '*_for_cli' -or $tool -like '*docs*') { exit 0 }

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

$fix = 'In Blender: Edit > Preferences > System > Allow Online Access on, then Add-ons > MCP > Start.'

if (Get-Process blender -ErrorAction SilentlyContinue) {
    # Blender may still be starting; the add-on starts its server a few seconds after launch.
    if (Wait-Port 20) { exit 0 }
    [Console]::Error.WriteLine("Blender is running but its MCP server is not listening on localhost:$port. $fix")
    exit 2
}

$exe = $env:BLENDER_PATH
if (-not $exe -or -not (Test-Path $exe)) {
    $exe = Get-ChildItem 'C:\Program Files\Blender Foundation\Blender *\blender.exe' -ErrorAction SilentlyContinue |
        Sort-Object FullName -Descending | Select-Object -First 1 -ExpandProperty FullName
}
if (-not $exe) {
    [Console]::Error.WriteLine('Blender is not running and blender.exe was not found. Set BLENDER_PATH to it.')
    exit 2
}

Start-Process $exe
if (Wait-Port 75) { exit 0 }
[Console]::Error.WriteLine("Started $exe but its MCP server did not open localhost:$port within 75 s. $fix")
exit 2
