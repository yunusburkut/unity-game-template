---
name: new-game
description: Start a new game from unity-game-template, or shape a new game's idea. Use on /gamekit:new-game <Ad> <fikir>, "yeni oyun oluştur", "yeni proje aç", "template'ten oyun başlat", or /gamekit:new-game şekillendir, "fikri şekillendir" in a new game.
argument-hint: <OyunAdı> <ilk fikir> | şekillendir
---

# New game

Two jobs, one skill, so the first design pass is the same from the desktop app and from a terminal:

- `$ARGUMENTS` is `şekillendir` (or `shape`), or the user asks to shape the idea, while the current folder is a game
  (`ProjectSettings/ProjectVersion.txt` exists): skip to **Shape the idea** below.
- Otherwise make the game, steps 1-8. `$ARGUMENTS`: the first word is the game's name, the rest is the user's first
  idea, kept word for word (a name of several words comes in quotes: `"Sky Hopper" ...`). Works from any folder; the
  game goes to `C:\GitHub\<Name>`.

Talk to the user in Turkish.

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
for p in "$T"/packs/*/README.md; do echo "== $p"; sed -n '3,4p' "$p"; done   # what each pack is for
```

Stop and say why when:

- `project/`, `packs/` or `new-game.ps1` has uncommitted changes (they would land in the game; name the files);
- the pull failed (show its error: a diverged `main` is the user's to sort out);
- the folder is taken (ask for another name);
- the Unity version is not installed (Unity Hub > Installs > that version, with the Android and iOS modules if the
  game ships on phones).

## 3. Ask once

One `AskUserQuestion` with two questions:

1. **Paketler** (multiSelect). The packs are the folders under `$T/packs` except `reference-docs` (read-only, never
   copied); the README lines step 2 printed say what each is for, and they are the only source: match the idea against
   them (for example a 2D sprite game, a store release, online co-op, Blender toon art), so a new or renamed pack is
   offered under its real folder name. Recommended ones first, at most 3 packs, each option's description taken from
   its README line, plus a last option `Paket yok` (it wins over any ticked pack); the user can type any other pack.
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
  before deleting it. On a yes, first make sure no batch-mode Unity still has it open, then delete it with
  `cmd /c rmdir /s /q "\\?\C:\GitHub\<Name>"` (its `Library\PackageCache` paths pass 260 characters, so
  `Remove-Item` and `rm -rf` fail there), check the folder is gone, fix the cause and rerun step 4.
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
   - `prompt`: `Load the gamekit:new-game skill and follow its "Shape the idea" section.`
     The procedure lives only there, so this session and a terminal one run the same design pass.

   Without that tool (a terminal session), or when the call errors or the session does not start (a brand-new folder
   may never have been opened in Claude Desktop), tell the user to run `claude` in `C:\GitHub\<Name>` and send
   `/gamekit:new-game şekillendir`; step 8 reports that line in place of the session link.

## 8. Report

Four lines: the folder and packs, the GitHub link or "yalnızca yerel" (`push et` in the game publishes it later),
Unity opening, and the link to the new session (or the terminal line from step 7); then any step 4 warning. One next
action: answer that session's first question.

## Shape the idea

The first session in a new game, once. It fills the TODOs in `CLAUDE.md` and `DESIGN.md` from the user's answers.

1. Read `REHBER.md`, `DESIGN.md` (First idea first) and `CLAUDE.md`. Once the genre is known, load
   `gamekit:genre-defaults` and offer its defaults as the recommended answers.
2. Ask in rounds, the grill-me way: each round is the frontier (every open decision whose prerequisites are settled),
   at most five questions, highest impact first, numbered, each with your recommended answer; use `AskUserQuestion`
   when every question of the round has 2-4 clear options (recommendation first, its label ending in "(Önerilen)").
   A question that depends on one still open waits for a later round. The tree to cover: genre, camera, core loop of
   2-4 steps, goal and fail state, PC and phone input, gamepad, orientation, session length, 3-5 pillars with their
   tests, 1-3 anti-pillars, the look (mood, palette, references, which Blender style skill or pack makes it), the kill
   condition. A fact from the repo is yours to look up, not a question. If the idea is thin, offer three starts: the
   core verb, a mashup of two known games, or the feeling worked backward.
3. Push back past 7 features and propose cuts. List the systems each feature implies (combat: damage, health, hit
   detection, AI, death and respawn; inventory: item data, slots, UI, save).
4. When the frontier is empty, summarise the decisions and wait for the user's yes. Then fill every TODO in
   `CLAUDE.md` and `DESIGN.md` (Pillars, Look and the kill condition included; Rules (as built) stays TODO until a
   card builds a rule), keeping what the user removed in their own words and marking an inferred line *guessed*. Put
   only the riskiest systems in `PLAN.md` Next (it holds at most 5); log the decisions under `DESIGN.md` Decisions.
5. Commit `design: <summary>` (message written to a scratchpad file, `git commit -F`), a body saying why,
   `Verified: text only` and the session's attribution line.

Never quote a market number from memory; write no game code before the user approves the design.
