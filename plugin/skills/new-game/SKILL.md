---
name: new-game
description: Starting a new game from unity-game-template in one go - the Unity project and a local git repo with the start commit, the user's first idea written into DESIGN.md, a private GitHub repo only after the user's yes, Unity opened on it, and a session in the new folder that shapes the idea. Use when the user types /gamekit:new-game <Ad> <fikir>, or says "yeni oyun oluştur", "yeni proje aç", "template'ten oyun başlat".
argument-hint: <OyunAdı> <ilk fikir>
---

# New game

`$ARGUMENTS`: the first word is the game's name, the rest is the user's first idea, kept word for word (a name of
several words comes in quotes: `"Sky Hopper" ...`). Talk to the user in Turkish. Works from any folder; the game goes
to `C:\GitHub\<Name>`.

## 1. Name and idea

- The name must match `^[A-Z][A-Za-z0-9]*$` (new-game.ps1 refuses anything else): `skyhopper` becomes `Skyhopper`,
  a quoted `"sky hopper"` becomes `SkyHopper`; say what you made of it. No name, or unclear where the name ends: ask
  for the name and nothing else. No idea: carry on; DESIGN.md keeps its TODO.
- It is a working title: carry on with any name the user gives.

## 2. Facts (Bash)

```bash
T="${TEMPLATE:-/c/GitHub/unity-game-template}"   # missing: ask the user for the path; never clone over one
NAME=<Name>
git -C "$T" status --short -- project packs new-game.ps1   # only these are copied into the game
git -C "$T" pull -q --ff-only origin main; echo "pull exit $?"; git -C "$T" log --oneline -1
cygpath -w "$T"                                    # the Windows path step 4 runs the script from
[ -e "/c/GitHub/$NAME" ] && echo "TAKEN: C:/GitHub/$NAME"
sed -n 's/^m_EditorVersion: //p' "$T/project/ProjectSettings/ProjectVersion.txt"
ls "/c/Program Files/Unity/Hub/Editor/"
gh auth status 2>&1 | head -2
```

Stop and say why when:

- `project/`, `packs/` or `new-game.ps1` has uncommitted changes (they would land in the game; name the files);
- the pull failed (show its error: a diverged `main` is the user's to sort out);
- the folder is taken (ask for another name);
- the Unity version is not installed (Unity Hub > Installs > that version, with the Android and iOS modules if the
  game ships on phones).

## 3. Ask once

One `AskUserQuestion` with two questions:

1. **Paketler** (multiSelect). The packs are the folders under `$T/packs` except `reference-docs`; line 3 of each
   README says what it is for. Recommend from the idea, recommended ones first: 2D sprites → `mobile-2d`; Google Play
   / App Store release → `mobile-store`; Steam → `steam`; online co-op → `coop-multiplayer`; 3D toon art from Blender →
   `toon-art`; cloud builds → `ci-github`; Linear issues → `linear`. At most 3 packs plus a last option `Paket yok`
   (it wins over any ticked pack); the user can type any other pack.
2. **GitHub**: `Private repo aç ve gönder` / `Şimdilik sadece yerel`. This answer is the approval the template's
   rule asks for: no repo, no push without it. If they pick the repo while `gh auth status` showed no login, stop
   here and ask them to run `gh auth login` themselves, then go on.

## 4. Create

PowerShell tool, in the background (2-5 minutes: copy, Feel, a batch-mode Unity run for ProjectSetup); wait for its
notification, do not poll. `<T>` is the Windows path from step 2:

```powershell
& "<T>\new-game.ps1" -Name <Name> -Packs <pack1>,<pack2>
```

Leave `-Packs` out for no packs, and never pass `-GitHub`: step 6 publishes after the idea commit.

- A failure (nonzero exit): show the last 20 lines and stop; the game folder may be half made, so say so and ask
  before deleting it.
- Success: collect every `WARNING:` line (no local Feel, no UnityYAMLMerge, manifest scopes) for the step 8 report;
  a game without Feel compiles without its juice until Feel is copied in. Do not relay the script's closing "open it
  in Unity Hub / start Claude Code / fill the TODOs" lines: steps 5-7 do those.

## 5. Write the idea

In `C:\GitHub\<Name>\DESIGN.md`, with the Edit tool, insert right before `## Rules (as built)`:

```markdown
## First idea

<YYYY-MM-DD> - the user's prompt, word for word:

> <the idea; every line starts with "> ">

```

Fill no other TODO from it: the shaping session (step 7) asks the open questions first. Write the commit message with
the Write tool into the scratchpad, never the game folder, and pass its path with forward slashes:

```bash
git -C "/c/GitHub/<Name>" add DESIGN.md && git -C "/c/GitHub/<Name>" commit -q -F <scratchpad>/first-idea.txt
```

The message: `design: first idea from the user`, a body saying it is the starting brief, `Verified: text only`, and
the session's attribution line.

## 6. GitHub (only after "Private repo aç")

```bash
gh repo create <Name> --private --source "/c/GitHub/<Name>" --remote origin --push
```

Always private: the game commits Feel, a paid package. A failure leaves a complete local game; give the user the same
command to retry.

## 7. Open it

1. Unity, PowerShell tool, on the version from step 2 (the batch run has ended by now; this first open writes
   `Logs/agent/compile.log`, which the game's compile gate needs):
   `Start-Process "C:\Program Files\Unity\Hub\Editor\<version>\Editor\Unity.exe" -ArgumentList '-projectPath','"C:\GitHub\<Name>"'`
2. A session in the game folder. If `mcp__ccd_session__start_session` is listed (the desktop app; load it with
   ToolSearch when it is deferred), call it with:
   - `initiation: "user_asked"`, `context: "fresh"`, `title: "<Name>: fikri şekillendir"`;
   - `cwd: "C:\GitHub\<Name>"` and `use_worktree: false` (a worktree has no Library or Feel and cannot compile);
   - `background` (80+ characters): the game was just made from the template, the idea is in DESIGN.md First idea,
     and whether it is on GitHub;
   - `prompt`: read REHBER.md and DESIGN.md First idea; ask the user the open questions one at a time (genre, camera,
     core loop, orientation, gamepad, PC and phone input, session length, art direction); then fill every TODO in
     CLAUDE.md and DESIGN.md, log the decisions under DESIGN.md Decisions, and commit `design: ...`; write no game
     code before the user approves the design.

   Without that tool (a terminal session), tell the user to run `claude` in `C:\GitHub\<Name>` and send
   `/grill-me CLAUDE.md ve DESIGN.md'deki TODO'ları doldur`.

## 8. Report

Four lines: the folder and packs, the GitHub link or "yalnızca yerel" (`push et` in the game publishes it later),
Unity opening, and the link to the new session; then any step 4 warning. One next action: answer that session's first
question.
