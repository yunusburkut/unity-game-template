---
name: sync-template
description: Template updates into a game made from it ("template'i güncelle", "template güncellemesini al", "sync template", "template'te ne değişti", "GameKit'i güncelle", "GameKit'e geçir"): skeleton, packs, GameKit tag. The plugin updates itself.
---

# Syncing a game with the template

A game is a copy of `project/` (plus its packs) taken at one template commit. Later template commits do not reach it
on their own: this skill finds them, applies the ones that fit, and moves the GameKit tag. The copy belongs to the
game, so nothing is overwritten wholesale: every hunk is a patch against what the game has now, and the user picks.
Use it also after changing the template when a game should catch up. The gamekit plugin (skills, agents, hooks)
updates itself and needs no sync.

Run from the game's root, in Bash, on `main` with a clean working tree. Unity may stay open; it reimports after the
patch. With the argument `GameKit'e geçir`, run step 1 (its facts and clean-tree check), then only the last section.

The pipeline is `${CLAUDE_SKILL_DIR}/scripts/sync.sh`. Every Bash call starts with a fresh shell, so `facts` writes
what it found to `.git/sync-template.env` and each later subcommand reads it from there; never retype the values.
`bash "${CLAUDE_SKILL_DIR}/scripts/test-sync.sh"` checks the script against a throwaway template and game.

## 1. Facts

```bash
bash "${CLAUDE_SKILL_DIR}/scripts/sync.sh" facts    # TEMPLATE=<path> if the template is not at /c/GitHub/unity-game-template
```

It stops on a branch other than `main`, a dirty tree (ask the user), a missing template checkout (ask for the path;
never clone over one) or a game without `Assets/<Game>/Core/<Game>.Core.asmdef` (not a template game). It prints
`game`, `company`, `base` (the template commit named by the start commit or the last sync commit; only the subjects
`Start <Name> from unity-game-template@<sha>` and `template: sync to unity-game-template@<sha>` count), `template`
(origin/main), the packs, the GameKit tag the game has and the one the template's manifest names, then the template
commits since `base`.

- `base` taken from the date fallback (a game made before the marker existed): confirm it with the user first.
- `company` empty: ask the user; a patch with `__COMPANY__` unfilled must not be applied.
- Packs: the `Packs:` line of the start or last sync commit when it has one; otherwise each pack with any of its files
  at `base` present in the game, printed as `pack <p>: <have>/<total> files present`. A partial count means the game
  deleted or renamed some pack files; tell the user. A wrong list: fix the `PACKS=` line in `.git/sync-template.env`.
- `base` equal to `template`, or an empty commit list: already in sync; say so and stop.

The script works from `origin/main`, never from the template's working tree (it may hold uncommitted experiments).

## 2. Show the user what changed

One line per template commit: its subject, and **take / skip / partly** with the reason. Judge each against the game:

- A rule, setting or doc line the game never changed: take.
- Something the game has since rewritten (its CLAUDE.md sections, DESIGN.md, PLAN.md content, example code it
  replaced): partly; only the template's new rule text, never its TODO placeholders over the game's real content.
- A pack change: take only for packs the game has (step 1's list).
- A game without `com.yunusburkut.gamekit` in `Packages/manifest.json` (made before GameKit): skip hunks that point at
  `GameKit.Editor`, `GameKit > ...` menus or the package; it keeps its own `AgentBridge` / `BuildMenu`, and moving to
  the package is a separate step (the last section), only on request.

Wait for the user's go before step 3.

## 3. Apply

```bash
bash "${CLAUDE_SKILL_DIR}/scripts/sync.sh" patch <sha of each take and partly commit>
```

It applies only those commits, oldest first, each as its own patch with the template prefix stripped and `__GAME__` /
`__COMPANY__` filled in (`git apply --reject`). Skipped commits never enter the patch. Scenes, prefabs, `*.asset`,
`ProjectSettings/`, `Packages/` and each pack's `README.md`, `examples/` and `packages.json` are never patched as text.
Then, in order:

1. **Rejects** (`<file>.<sha>.rej`, one per commit so a later reject does not overwrite an earlier one): each is a hunk
   whose context the game changed. Merge it by hand using the template's intent rather than its exact text; delete
   every `.rej` afterwards. A **partly** commit: edit out the part the user did not take; a file it added that the
   user does not want is removed with `rm` (it is untracked, so `git checkout --` cannot drop it).
2. **Excluded files:** `sync.sh excluded` lists the template commits since `base` that touched them, with paths. For
   each the user took, say what it needs instead: rerun **GameKit > Set Up Project**, a change in the Editor, or a
   package or scoped registry added by hand to the game's `Packages/manifest.json` next to its own (a pack's
   `packages.json` change lands here; without it, code synced from that pack does not compile).
3. **GameKit** (games that have the package only): `sync.sh tag` moves the game's `#gamekit-v...` tag to the one the
   template's `origin/main` manifest names (the released tag, not merely the newest local one), after checking that
   the tag is on the template's origin, and prints the GameKit commits between the two tags: read them for anything
   the game must change with it. A `file:` GameKit entry is a local experiment: the script leaves it and says so.
4. **Compile:** a moved tag needs a package resolve, which a scripted refresh does not run (probed on 6000.6): ask
   the user to focus Unity and wait until `Packages/packages-lock.json` is newer than `Packages/manifest.json`. Then
   `gk-bridge refresh` in Bash must PASS; fix errors that the sync caused. Exit 2 (Editor closed, Play Mode, a bridge
   that does not know refresh): record `Verified: compile unverified (<reason>)` instead.

## 4. Record

One commit on `main`, so the next sync starts here. `HEAD_T`, `PACKS`, `OLD_TAG` and `TAG` come from
`.git/sync-template.env`:

```
template: sync to unity-game-template@<HEAD_T>

Took: <subjects>. Skipped: <subjects and why>. GameKit <OLD_TAG> -> <TAG>.
Packs: <PACKS>

Verified: gk-bridge refresh PASS <time>; Play Mode pending
```

The marker `unity-game-template@<sha>` in the subject is what step 1 reads next time; keep it exact even when every
commit was skipped. The `Packs:` line (space or comma separated) spares the next sync the file-presence guess. Hand
the user the Play Mode checks for what changed behaviour (`gamekit:implementation-verification`).

## Moving a game made before GameKit to the package

Only when the user asks (`GameKit'e geçir`), after step 1, as its own commit after a commit of everything else:

1. Add the GameKit line from the template's manifest to the game's, at the tag step 1 printed (it prints the line:
   `. .git/sync-template.env; git -C "$T" show origin/main:project/Packages/manifest.json | grep gamekit`). The
   game's Editor asmdef gets `GameKit.Editor` in its references.
2. Delete the game's own copies of what GameKit ships (`AgentBridge`, `BuildMenu`, `ProjectSetup`, `FrameLog`,
   `SafeAreaFitter`): two bridges would both answer `request.txt`, two FrameLogs both write. Keep a copy whose
   `.cs.meta` guid a scene or prefab uses (`grep -rl <guid> Assets --include=*.unity --include=*.prefab`): moving it
   shows "Missing Script", so it stays and the user hears which.
3. Ask the user to focus Unity (the old bridge cannot refresh), then `gk-bridge refresh` must PASS.
4. Take the template's CLAUDE.md "Agent bridge" section into the game's, and commit `tools: move to the GameKit
   package` with the gate's `Verified:` line.
