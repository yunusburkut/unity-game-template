---
name: new-game
description: Start a new game from unity-game-template, or shape a new game's idea. Use on /gamekit:new-game <Ad> <fikir>, "yeni oyun oluştur", "yeni proje aç", "template'ten oyun başlat", or /gamekit:new-game şekillendir, "fikri şekillendir" in a new game.
argument-hint: <OyunAdı> <ilk fikir> | şekillendir
---

# New game

Two jobs, one skill, so the first design pass is the same from the desktop app and from a terminal:

- `$ARGUMENTS` is `şekillendir` (or `shape`), or the user asks to shape the idea, while the current folder is a game
  (`ProjectSettings/ProjectVersion.txt` exists): skip to **Shape the idea** below.
- `$ARGUMENTS` is `şekillendir` or `shape` but the current folder is not a game's root: say to run it from the game's
  root folder (`C:\GitHub\<Name>`) and stop; it is never a game name.
- Otherwise make the game, steps 1-8. `$ARGUMENTS`: the first word is the game's name, the rest is the user's first
  idea, kept word for word (a name of several words comes in quotes: `"Sky Hopper" ...`). Works from any folder; the
  game goes to `C:\GitHub\<Name>`.

Talk to the user in Turkish.

## 1. Name and idea

- The name must match `^[A-Z][A-Za-z0-9]*$` (new-game.ps1 refuses anything else): `skyhopper` becomes `Skyhopper`,
  a quoted `"sky hopper"` becomes `SkyHopper`, Turkish letters become their ASCII base (`ş`->`s`, `ı`/`İ`->`i`/`I`,
  `ğ`->`g`, `ç`->`c`, `ö`->`o`, `ü`->`u`: `Kuşçu` becomes `Kuscu`), and a leading digit is spelled out or moved
  (`2048Plus` becomes `Plus2048`); say what you made of it. No name, or unclear where the name ends: ask
  for the name and nothing else. No idea: carry on; DESIGN.md keeps its TODO.
- It is a working title: carry on with any name the user gives.

## 2. Facts (Bash)

```bash
T="${TEMPLATE:-/c/GitHub/unity-game-template}"   # missing: ask the user for the path; never clone over one
NAME=<Name>
DIRTY=$(git -C "$T" status --short -- project packs new-game.ps1); echo "dirty: ${DIRTY:-none}"   # only these are copied into the game
git -C "$T" fetch -q origin main; echo "fetch exit $?"            # nonzero: offline or GitHub down
[ -z "$DIRTY" ] && { git -C "$T" merge -q --ff-only origin/main; echo "merge exit $?"; }   # nonzero: main has diverged
git -C "$T" log --oneline -1
echo "unpushed $(git -C "$T" rev-list --count origin/main..HEAD)"   # the game records HEAD as its sync base
cygpath -w "$T"                                    # the Windows path step 4 runs the script from
[ -e "/c/GitHub/$NAME" ] && echo "TAKEN: C:/GitHub/$NAME"
V=$(sed -n 's/^m_EditorVersion: //p' "$T/project/ProjectSettings/ProjectVersion.txt"); echo "version $V"
# the Unity.exe new-game.ps1 picks: Hub's custom install folder (Preferences > Installs) first, then its default
H2=$(cat "$APPDATA/UnityHub/secondaryInstallPath.json" 2>/dev/null | tr -d '"\r\n')
for d in ${H2:+"$(cygpath -u "$H2")"} "/c/Program Files/Unity/Hub/Editor"; do
  [ -f "$d/$V/Editor/Unity.exe" ] && { echo "UNITY: $(cygpath -w "$d/$V/Editor/Unity.exe")"; break; }
done
# env -u: the read-only GITHUB_TOKEN/GH_TOKEN for plugin updates would shadow the gh login (README.md, token conflict)
env -u GITHUB_TOKEN -u GH_TOKEN gh auth status 2>&1 | head -2
env -u GITHUB_TOKEN -u GH_TOKEN gh repo view "$NAME" >/dev/null 2>&1 && echo "GH_TAKEN: $NAME"   # only when logged in: the account already has it
for p in "$T"/packs/*/README.md; do echo "== $p"; awk '/^#/ {next} NF {p=1; print; next} p {exit}' "$p"; done   # first paragraph under the title
```

Stop and say why when:

- `project/`, `packs/` or `new-game.ps1` has uncommitted changes (they would land in the game; name the files);
- the merge failed (show its error: a diverged `main` is the user's to sort out). A failed fetch alone does not
  stop: say the template could not be updated and carry on, since `unpushed` below still guards the sync base;
- `unpushed` is not 0: the template has commits origin lacks, so the game's recorded sync base would be missing there
  and `gamekit:sync-template` would fail on it later; ask the user to push the template's `main` first;
- the folder is taken (ask for another name);
- no `UNITY:` line: that Unity version is not installed (Unity Hub > Installs > that version, with the Android and
  iOS modules if the game ships on phones).

## 3. Ask once

One `AskUserQuestion` with two questions:

1. **Paketler** (multiSelect). The packs are the folders under `$T/packs` except `reference-docs` (read-only, never
   copied); the README paragraphs step 2 printed (the first one under each title) say what each is for, and they are the only source: match the idea against
   them (for example a 2D sprite game, a store release, online co-op, Blender toon art), so a new or renamed pack is
   offered under its real folder name. Recommended ones first, at most 3 packs, each option's description taken from
   its README paragraph, plus a last option `Paket yok` (it wins over any ticked pack); the user can type any other pack.
2. **GitHub**: `Private repo aç ve gönder` / `Şimdilik sadece yerel`. This answer is the approval the template's
   rule asks for: no repo, no push without it. If they pick the repo while `gh auth status` showed no login, stop
   here and ask them to run `gh auth login` themselves, then rerun step 2's `gh repo view` line and go on. If they
   pick it while step 2 printed `GH_TAKEN`, ask for another repo name (the local folder keeps `<Name>`) and use it in
   step 6.

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
env -u GITHUB_TOKEN -u GH_TOKEN gh repo create <Name> --private --source "/c/GitHub/<Name>" --remote origin --push
```

Always private: the game commits Feel, a paid package. A failure leaves a complete local game; give the user the same
command to retry (with `env -u`: a 403 means the read-only env token was used), or, when the error says the name already exists on the account, the command with another repo name.

## 7. Open it

1. Unity, PowerShell tool, with the `UNITY:` path from step 2 (the batch run has ended by now; this first open writes
   `Logs/agent/compile.log`, which the game's compile gate needs):
   `Start-Process "<UNITY path>" -ArgumentList '-projectPath','"C:\GitHub\<Name>"'`
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

Five lines: the folder and packs, the GitHub link or "yalnızca yerel" (`push et` in the game publishes it later),
Unity opening, that Unity Hub does not list the game yet (step 7 opened Unity.exe directly; add it once with Add > Add
project from disk > `C:\GitHub\<Name>`), and the link to the new session (or the terminal line from step 7); then any step 4 warning. One next
action: answer that session's first question.

## Shape the idea

The first session in a new game, once. It fills the TODOs in `CLAUDE.md`, `DESIGN.md` and `README.md` from the user's answers.

1. Read `REHBER.md`, `DESIGN.md` (First idea first) and `CLAUDE.md`. Once the genre is known, load
   `gamekit:genre-defaults` and offer its defaults as the recommended answers.
2. Ask in rounds, the grill-me way (a copy of the round rules in `~/.claude/skills/grill-me/SKILL.md`, kept here
   because the user layer is not versioned; change both together): each round is the frontier (every open decision whose prerequisites are settled),
   at most five questions, highest impact first, numbered, each with your recommended answer; use `AskUserQuestion`
   when every question of the round has 2-4 clear options (recommendation first, its label ending in "(Önerilen)");
   it takes at most 4, so such a round asks the top 4 and its fifth question opens the next round. A question that depends on one still open waits for a later round; recompute the frontier after every round, and a
   frontier larger than one round is no reason to drop a question. The tree to cover: genre, camera, core loop of
   2-4 steps, goal and fail state, PC and phone input, gamepad, orientation, session length, monetisation (premium,
   free with ads, free with IAP, per platform; settle it before the core loop is final, since it shapes the session,
   with `gamekit:launch-review` "Price and business model" as the recommendation), 3-5 pillars with their
   tests, 1-3 anti-pillars, the look (mood, palette, references, which Blender style skill or pack makes it), the language of
   player-facing strings (Turkish / English), the voice (`player-clarity` §E defaults as the recommendation), the kill
   condition. A fact from the repo is yours to look up, not a question. If the idea is thin, offer three starts: the
   core verb, a mashup of two known games, or the feeling worked backward.
3. Push back past 7 features and propose cuts. List the systems each feature implies (combat: damage, health, hit
   detection, AI, death and respawn; inventory: item data, slots, UI, save).
4. When the frontier is empty, summarise the decisions and wait for the user's yes. Then fill every TODO in
   `CLAUDE.md` (the string language in Conventions included), `DESIGN.md` (Pillars, Look, Voice and the kill condition
   included) and `README.md` (its one line on the game), except three sections that fill
   later: Rules (as built) once a card builds a rule, Levels once the first level exists, Playtests once a person plays
   a build. Open questions keeps whatever the user left undecided. Keep what the user removed in their own words and
   mark an inferred line *guessed*. Put only the riskiest systems in `PLAN.md` Next (it holds at most 5); log the decisions under `DESIGN.md` Decisions
   (the monetisation model included).
5. Stage only the files this pass wrote, `git add CLAUDE.md DESIGN.md README.md PLAN.md` (never `-A`: Unity's first
   open from step 7 may have changed `Packages/` or `ProjectSettings/`, which are not part of a text-only commit), then
   commit `design: <summary>` (message written to a scratchpad file, `git commit -F`), a body saying why,
   `Verified: text only` and the session's attribution line.

Never quote a market number from memory; write no game code before the user approves the design.
