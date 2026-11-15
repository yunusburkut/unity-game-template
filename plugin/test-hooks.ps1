# Regression check for the gamekit plugin's hooks and reference indexes. Run after changing plugin/hooks/ or a
# skill's references: powershell -NoProfile -ExecutionPolicy Bypass -File plugin\test-hooks.ps1
# It pipes fixed payloads through each hook and asserts the output, so nothing here opens Blender or Unity (the live
# Blender path of ensure-blender.ps1 is not covered: it starts a window). Exit 0 = all pass, 1 = a failure.
# Pure ASCII on purpose: Windows PowerShell 5.1 reads a BOM-less script as ANSI.
$ErrorActionPreference = 'Stop'
$hooks = Join-Path $PSScriptRoot 'hooks'
$tmp = Join-Path $env:TEMP ('gk-test-hooks-' + [guid]::NewGuid().ToString('N').Substring(0, 8))
New-Item -ItemType Directory -Path $tmp | Out-Null
$utf8 = New-Object Text.UTF8Encoding $false
$failed = 0

function Invoke-Hook($script, $payload, $cwd = $tmp) {
    $psi = New-Object Diagnostics.ProcessStartInfo
    $psi.FileName = 'powershell.exe'
    $psi.Arguments = "-NoProfile -NonInteractive -ExecutionPolicy Bypass -File `"$(Join-Path $hooks $script)`""
    $psi.UseShellExecute = $false; $psi.RedirectStandardInput = $true
    $psi.RedirectStandardOutput = $true; $psi.RedirectStandardError = $true
    $psi.StandardOutputEncoding = [Text.Encoding]::UTF8
    $psi.WorkingDirectory = $cwd
    $psi.EnvironmentVariables['CLAUDE_PROJECT_DIR'] = $cwd
    $p = [Diagnostics.Process]::Start($psi)
    $bytes = $utf8.GetBytes($payload)
    $p.StandardInput.BaseStream.Write($bytes, 0, $bytes.Length); $p.StandardInput.Close()
    $out = $p.StandardOutput.ReadToEndAsync(); $err = $p.StandardError.ReadToEndAsync()
    if (-not $p.WaitForExit(60000)) { $p.Kill(); return @{ code = -1; out = ''; err = 'timeout' } }
    return @{ code = $p.ExitCode; out = $out.Result.Trim(); err = $err.Result.Trim() }
}
function Check($name, $ok, $detail = '') {
    if ($ok) { Write-Output "PASS $name" } else { Write-Output "FAIL $name $detail"; $script:failed++ }
}
function Payload($obj) { return ($obj | ConvertTo-Json -Compress -Depth 5) }

try {
    # --- check-json.ps1 -----------------------------------------------------------------------------------------
    $files = @{
        'valid.json'      = '{"a": [1, 2], "b": {"c": true}}'
        'comma.json'      = '{"a": 1,, "b": 2}'
        'empty.json'      = '   '
        'notjson.txt'     = '{ broken'
        'Library\x.json'  = '{ broken'
        "t$([char]0x011F)rk$([char]0x00E7)e\bozuk.json" = '{"a": [1, 2'
    }
    $big = '{"dependencies": {' + ((1..3000 | % { "`"com.example.p$_`": `"1.0.$_`"" }) -join ', ')   # final } lost
    $files['big.json'] = $big
    foreach ($k in $files.Keys) {
        $f = Join-Path $tmp $k; New-Item -ItemType Directory -Force -Path (Split-Path $f) | Out-Null
        [IO.File]::WriteAllText($f, $files[$k], $utf8)
    }
    $cj = { param($rel) Invoke-Hook 'check-json.ps1' (Payload @{ tool_name = 'Write'; tool_input = @{ file_path = (Join-Path $tmp $rel) }; cwd = $tmp }) }

    $r = & $cj 'valid.json';     Check 'check-json: valid file is silent' ($r.code -eq 0 -and -not $r.out) $r.out
    $r = & $cj 'comma.json';     Check 'check-json: double comma blocks' ($r.out -match '"decision":\s*"block"') $r.out
    $r = & $cj 'empty.json';     Check 'check-json: empty file blocks' ($r.out -match 'the file is empty') $r.out
    $r = & $cj 'notjson.txt';    Check 'check-json: other extension is silent' (-not $r.out) $r.out
    $r = & $cj 'Library\x.json'; Check 'check-json: Library\ is skipped' (-not $r.out) $r.out
    $r = & $cj 'missing.json';   Check 'check-json: missing file is silent' (-not $r.out) $r.out
    $r = & $cj "t$([char]0x011F)rk$([char]0x00E7)e\bozuk.json"
    Check 'check-json: Turkish path blocks' ($r.out -match '"decision":\s*"block"') $r.out
    $r = & $cj 'big.json'
    Check 'check-json: lost brace blocks' ($r.out -match '"decision":\s*"block"') $r.out.Substring(0, [Math]::Min(200, $r.out.Length))
    Check "check-json: lost brace reason stays short ($($r.out.Length) chars, file $($big.Length))" ($r.out.Length -lt 1000)
    $r = Invoke-Hook 'check-json.ps1' 'not json'; Check 'check-json: bad payload fails open' ($r.code -eq 0 -and -not $r.out)

    # --- ensure-blender.ps1 (only the paths that never start Blender) ---------------------------------------------
    foreach ($t in 'mcp__Blender__execute_blender_code_for_cli', 'mcp__Blender__search_api_docs') {
        $sw = [Diagnostics.Stopwatch]::StartNew()
        $r = Invoke-Hook 'ensure-blender.ps1' (Payload @{ tool_name = $t; tool_input = @{} })
        Check "ensure-blender: $t passes" ($r.code -eq 0 -and $sw.Elapsed.TotalSeconds -lt 10) "exit $($r.code) $($r.err)"
    }
    $r = Invoke-Hook 'ensure-blender.ps1' 'not json'; Check 'ensure-blender: bad payload fails open' ($r.code -eq 0)

    # --- route.ps1 ------------------------------------------------------------------------------------------------
    $game = Join-Path $tmp 'game'; New-Item -ItemType Directory -Force -Path (Join-Path $game 'ProjectSettings') | Out-Null
    [IO.File]::WriteAllText((Join-Path $game 'ProjectSettings\ProjectVersion.txt'), 'm_EditorVersion: 6000.6.0f1', $utf8)
    $route = { param($prompt, $cwd) Invoke-Hook 'route.ps1' (Payload @{ prompt = $prompt; cwd = $cwd }) $cwd }
    $r = & $route 'muzik ekle' $game;  Check 'route: new task in a Unity project prints the router' ($r.out -match 'task router')
    Check 'route: router names the prototype route' ($r.out -match 'gamekit:prototype')
    $r = & $route 'evet' $game;        Check 'route: plain reply is silent' (-not $r.out) $r.out
    $r = & $route '/gamekit:feature' $game; Check 'route: slash command is silent' (-not $r.out) $r.out
    $r = & $route 'muzik ekle' $tmp;   Check 'route: non-Unity folder is silent' (-not $r.out) $r.out

    # --- genre-defaults indexes -----------------------------------------------------------------------------------
    $gd = Join-Path $PSScriptRoot 'skills\genre-defaults'
    $listed = Select-String -LiteralPath (Join-Path $gd 'SKILL.md') -Pattern '^- `([a-z0-9-]+)`:' |
        ForEach-Object { $_.Matches[0].Groups[1].Value }
    $missing = $listed | Where-Object { -not (Test-Path -LiteralPath (Join-Path $gd "references\$_.md")) }
    Check "genre-defaults: all $($listed.Count) indexed sheets exist" ($listed.Count -gt 0 -and -not $missing) ($missing -join ', ')
    $refs = Join-Path $gd 'references'
    $used = Get-ChildItem -LiteralPath $refs -Filter *.md | Where-Object Name -ne 'sources.md' |
        Select-String -Pattern '\[([a-z0-9]+(?:-[a-z0-9]+)*-\d+)\]' -AllMatches |
        ForEach-Object { $_.Matches } | ForEach-Object { $_.Groups[1].Value } | Sort-Object -Unique
    $defined = Select-String -LiteralPath (Join-Path $refs 'sources.md') -Pattern '^- \*\*\[([^\]]+)\]\*\*' |
        ForEach-Object { $_.Matches[0].Groups[1].Value }
    $unresolved = $used | Where-Object { $_ -notin $defined }
    Check "genre-defaults: all $($used.Count) source keys resolve" ($used.Count -gt 0 -and -not $unresolved) ($unresolved -join ', ')
    Check 'genre-defaults: LICENSE.md carries the MIT text' (Select-String -LiteralPath (Join-Path $gd 'LICENSE.md') -Pattern 'Permission is hereby granted' -Quiet)
} finally {
    Remove-Item -LiteralPath $tmp -Recurse -Force -ErrorAction SilentlyContinue
}
if ($failed) { Write-Output "$failed check(s) failed"; exit 1 }
Write-Output 'All checks passed'
exit 0
