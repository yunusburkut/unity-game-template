# UserPromptSubmit hook (gamekit plugin): the task router for Unity games. Its stdout becomes context for this prompt.
# A hook cannot rewrite a prompt, so the "best-practice" rewrite is the model's first line (the spec line) and, for M
# and L, the gamekit:pipeline skill's spec card. Kept ASCII so PowerShell 5.1 output encoding cannot garble it.
# Prints only at a Unity project root (ProjectSettings\ProjectVersion.txt under CLAUDE_PROJECT_DIR, else stdin cwd);
# the global router (~/.claude/hooks/enhance-prompt.ps1) exits on the same marker, so exactly one router prints.
# Silent for slash commands, plain replies (evet, tamam, ok, a number...) and background-task or subagent reports,
# which fire this event too; a short new task ("muzik ekle") still gets it. Ceiling: the size is the model's
# judgement; "bu S|M|L" corrects it.
[Console]::InputEncoding = [System.Text.Encoding]::UTF8
$hook = $null
try { $hook = [Console]::In.ReadToEnd() | ConvertFrom-Json } catch { exit 0 }
$root = if ($env:CLAUDE_PROJECT_DIR) { $env:CLAUDE_PROJECT_DIR } else { [string]$hook.cwd }
if (-not $root -or -not (Test-Path -LiteralPath (Join-Path $root 'ProjectSettings\ProjectVersion.txt'))) { exit 0 }
$p = ([string]$hook.prompt).Trim()
if (-not $p -or $p.StartsWith('/') -or $p -match '<task-notification>|\[SYSTEM NOTIFICATION|<agent-message') { exit 0 }
if ($p -match '^(evet|hay.r|tamam|ok|okay|olur|peki|yes|no|hepsi tamam|[0-9]+)\W*$') { exit 0 }
Write-Output @'
Unity game task router (gamekit plugin; the user asked for it). For a NEW task, open with ONE line, then work:
"Boyut S|M|L | Netlesmis istem: <goal> | <facts left implicit: files, Core/Game, PC/phone> | bitti sayilir: <checkable done>"
Write the line in Turkish with Turkish letters. It adds facts and a checkable done only; it never widens scope or
invents requirements. Where the game's CLAUDE.md differs from this router, CLAUDE.md wins. No line and no routing
for replies, button answers, confirmations, follow-ups inside the current task, or questions answerable without tools;
a read-only ask (fps on a phone, a level critique, a text review, a store page) goes to the matching read-only gamekit
agent (perf-auditor, design-critic, clarity-reviewer, launch-auditor), no line.
S - one sentence, place known, 1-3 files, no design choice: do it, gate with `gk-bridge refresh` in Bash (exit 0 =
    pass, 2 = unknown, never a pass), commit. No review agent unless the user says review or puanla.
M - several files, crosses Core/Game, one design choice, or a bug whose cause is not in one file: load the
    gamekit:pipeline skill and run it (spec card -> plan -> build with a gate per step -> verify -> scored review
    until 9/10 -> handoff). Bug: gamekit:bug-hunter first.
L - a new system, 5+ units, more than one session, or fuzzy requirements: load gamekit:pipeline, write the spec card
    and ask its open questions; with the answers, commit the card and stop (the skill's phase 1 says how).
Unsure: take the smaller size and move up. "bu S", "bu M", "bu L" from the user wins.
While a /gamekit:feature workflow you started is running, edit no file and commit nothing: answer read-only, and say
a new request waits for the run's report, then you do it.
"devam": after an UNKNOWN gate, rerun that gate first (a bridge that does not know refresh: read
Logs/agent/compile.log instead, clean and newer than the edited scripts). Otherwise read PLAN.md Now and the last 10
commits, then continue the card where it stopped (gamekit:pipeline, "Longer than one session"); a card whose Open
questions line still lists questions: ask them first (phase 1 L), never build past them. No card, and the last
commit is "design: review open" (a review et below 9): one more fix-and-review round on the range its body names.
"kabul": once the card in PLAN.md Now has been reviewed, run gamekit:pipeline phase 7, open findings left under Known
issues; a card not reviewed yet: say so and offer "devam". No card, and the last commit is "design: review open":
nothing left to do, its findings stay under Known issues.
"karti Next'e tasi" (any spelling): park the card in PLAN.md Now (gamekit:pipeline phase 1).
"review et" / "puanla": run only gamekit:pipeline phase 6 (score, fix, re-score until 9, 3 rounds max) on the range
the user names, else the card's commits (body line "Card: <Base>"), else the last task's commits.
'@
# A Unity project with no bridge at all (not made from the template) has nothing gk-bridge can ask. Logs/ is not
# committed, so a fresh clone of a game with its own AgentBridge copy has no compile.log yet: that copy counts, in any
# Editor folder under Assets (Assets/<Game>/Scripts/Editor too). Feel, most of Assets, is skipped; the search runs
# last, only when the cheap checks found nothing.
$manifest = Join-Path $root 'Packages\manifest.json'
if (-not (Test-Path -LiteralPath (Join-Path $root 'Logs\agent\compile.log')) -and
    -not ((Test-Path -LiteralPath $manifest) -and (Select-String -LiteralPath $manifest -Pattern 'com\.yunusburkut\.gamekit' -Quiet)) -and
    -not (Get-ChildItem -LiteralPath (Join-Path $root 'Assets') -Directory -ErrorAction SilentlyContinue |
          Where-Object Name -ne 'Feel' | Get-ChildItem -Recurse -Filter AgentBridge.cs -ErrorAction SilentlyContinue |
          Where-Object { $_.Directory.Name -eq 'Editor' } | Select-Object -First 1)) {
    Write-Output @'
This project has no AgentBridge (no GameKit, no Logs/agent/compile.log): gk-bridge can only answer UNKNOWN here. The
gate is the check the project's CLAUDE.md names; without one, ask the user to focus Unity and report the Console, and
commit with "Verified: compile unverified (no AgentBridge)" until they do. Say this once, not every turn.
'@
}
