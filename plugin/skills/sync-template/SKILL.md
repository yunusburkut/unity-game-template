---
name: sync-template
description: Bringing unity-game-template updates into a game that was made from it — the copied skeleton (`project/`, the packs the game has) and the GameKit package tag. Use when the user says "template'i güncelle", "template güncellemesini al", "sync template", "template'te ne değişti", "GameKit'i güncelle", or after changing the template and wanting a game to catch up. The gamekit plugin (skills, agents, hooks) updates itself and needs no sync.
---

# Syncing a game with the template

A game is a copy of `project/` (plus its packs) taken at one template commit. Later template commits do not reach it
on their own: this skill finds them, applies the ones that fit, and moves the GameKit tag. The copy belongs to the
game, so nothing is overwritten wholesale: every hunk is a patch against what the game has now, and the user picks.

Run from the game's root, in Bash, on `main` with a clean working tree (`git status --short` empty; otherwise stop
and ask). Unity may stay open; it reimports after the patch.

## 1. Facts

```bash
T="${TEMPLATE:-/c/GitHub/unity-game-template}"   # ask the user for the path if it is missing; never clone over one
git -C "$T" fetch -q origin && git -C "$T" status -sb | head -1
GAME=$(for d in Assets/*/; do g=$(basename "$d"); [ -f "Assets/$g/Core/$g.Core.asmdef" ] && echo "$g"; done | head -1)
COMPANY=$(sed -n 's/^  companyName: //p' ProjectSettings/ProjectSettings.asset 2>/dev/null)
# before the first ProjectSetup run there is no ProjectSettings.asset; the game's README carries the filled-in company
[ -z "$COMPANY" ] && COMPANY=$(sed -n 's/.*-gameCompany \([A-Za-z0-9]*\).*/\1/p' README.md | head -1)
# the sync point: the template commit named by the start commit or the last sync commit
BASE=$(git log --grep='unity-game-template@' -1 --format=%s | sed -n 's/.*unity-game-template@\([0-9a-f]\{7,\}\).*/\1/p')
# games made before the marker existed: the template's last main commit before the game's first commit
[ -z "$BASE" ] && BASE=$(git -C "$T" rev-list -1 --before="$(git log --reverse --format=%cI | head -1)" origin/main)
HEAD_T=$(git -C "$T" rev-parse --short origin/main)
echo "game=$GAME company=$COMPANY base=$BASE template=$HEAD_T"
git -C "$T" log --oneline "$BASE..origin/main" -- project packs packages/com.yunusburkut.gamekit
```

`GAME` empty: not a template game; stop. `BASE` equal to `HEAD_T` or an empty log: already in sync; say so and stop.
Work from `origin/main`, never from the template's working tree (it may hold uncommitted experiments).

## 2. Show the user what changed

One line per template commit: its subject, and **take / skip / partly** with the reason. Judge each against the game:

- A rule, setting or doc line the game never changed: take.
- Something the game has since rewritten (its CLAUDE.md sections, DESIGN.md, PLAN.md content, example code it
  replaced): partly; only the template's new rule text, never its TODO placeholders over the game's real content.
- A pack change: take only for packs the game has (the pack's files exist in the game under their mapped paths).
- A game without `com.yunusburkut.gamekit` in `Packages/manifest.json` (made before GameKit): skip hunks that point at
  `GameKit.Editor`, `GameKit > ...` menus or the package; it keeps its own `AgentBridge` / `BuildMenu`, and moving to
  the package changes script GUIDs (scenes show "Missing Script"), which is a separate, manual migration.

Wait for the user's go before step 3.

## 3. Apply

Build one patch with the template prefix stripped and the placeholders filled in, then apply what fits:

```bash
P=$(mktemp)
{ git -C "$T" diff --binary --relative=project "$BASE" origin/main -- project \
    ':(exclude)project/**/*.unity' ':(exclude)project/**/*.prefab' ':(exclude)project/**/*.asset' \
    ':(exclude)project/ProjectSettings/**' ':(exclude)project/Packages/**'
  for p in <packs the game has>; do git -C "$T" diff --binary --relative="packs/$p" "$BASE" origin/main -- "packs/$p" \
    ":(exclude)packs/$p/README.md" ":(exclude)packs/$p/examples/**" ":(exclude)packs/$p/packages.json"; done
} | sed "s/__GAME__/$GAME/g; s/__COMPANY__/$COMPANY/g" > "$P"
git apply --stat "$P"
git apply --reject --whitespace=nowarn "$P"
```

Then, in order:

1. **Rejects** (`*.rej`): each is a hunk whose context the game changed. Merge it by hand where the user said take or
   partly, using the template's intent rather than its exact text; delete every `.rej` afterwards. Hunks the user
   skipped: revert those files (`git checkout -- <file>`), or edit out just the skipped part.
2. **Excluded files**, never patched as text: list the template commits that touched `ProjectSettings/`, Unity YAML or
   `Packages/manifest.json` and say what each needs instead (rerun **GameKit > Set Up Project**, a change in the
   Editor, a package added in the manifest by hand next to the game's own).
3. **GameKit** (games that have the package only):
   ```bash
   TAG=$(git -C "$T" tag -l 'gamekit-v*' --sort=-v:refname | head -1)
   sed -i "s|#gamekit-v[0-9][0-9.]*\"|#$TAG\"|" Packages/manifest.json   # only the GameKit line has this suffix
   ```
   A `file:` GameKit entry is a local experiment: leave it and say so. Read the template's
   `git log <old tag>..$TAG -- packages/com.yunusburkut.gamekit` for anything the game must change with it.
4. **Compile:** queue `refresh` through the agent bridge (`unity-editor-cli`), or ask the user to focus Unity, and
   wait for `Logs/agent/compile.log` newer than the patch with 0 errors. Fix errors that the sync caused.

## 4. Record

One commit on `main`, so the next sync starts here:

```
template: sync to unity-game-template@<HEAD_T>

Took: <subjects>. Skipped: <subjects and why>. GameKit <old> -> <new>.

Verified: compile.log OK at <time>; Play Mode pending
```

The marker `unity-game-template@<sha>` in the subject is what step 1 reads next time; keep it exact even when every
commit was skipped. Hand the user the Play Mode checks for what changed behaviour (`implementation-verification`).
