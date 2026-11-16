---
name: implementation-verification
description: Use at the end of every change in a Unity game made from the template, instead of test suites or builds - a cheap check of the change, the spec card acceptance items ticked with evidence, and a Play Mode checklist for PC and the phone.
---

# Verifying a change

Verification is proportional and cheap: a minute, not a test run. Every claim names its evidence; a check that could
not run is reported as unverified, never as passed.

## The pass

1. Read the diff. Look for what static reading catches: a flag set but never cleared, a field renamed without
   `[FormerlySerializedAs]`, an early `return` that skips cleanup. A new asset under `Assets/` that is not ours or
   that an AI made (Claude's Blender exports included) needs its `docs/asset-sources.md` row in the same commit; a
   missing row is a finding, because `launch-review` reads that file before a store upload.
2. Compile gate: `gk-bridge refresh` in Bash (not found: `bash "${CLAUDE_PLUGIN_ROOT}/bin/gk-bridge" refresh`). Exit
   0 = clean and newer than every script; 1 = errors (fix them; a verify-only step reports them); 2 = unknown (no
   Editor, Play Mode, busy): say "compile unverified" in the handoff. Exit 0 with a `warning CS0618` in
   `Logs/agent/compile.log` that points at a line your diff added (an obsolete Unity API brought in) is fixed like exit
   1; an older one is reported, not fixed (`gamekit:pipeline` 4 Build item 2 measures the same against a baseline it
   notes before the first edit). `Logs/agent/console.log` holds the last 200 Console errors and warnings.
3. Platform `#if` code changed, and only after step 2 exited 0: the Editor compiles only the active build target's
   branches, never a `!UNITY_EDITOR` one, and Device Simulator does not simulate `#define`s. Run the platform compile
   gates as `gamekit:pipeline` 4 Build, item 3 says (the single source of which branch gets which `gk-bridge compile`,
   `UNITY_WEBGL` included through `compile webgl` on GameKit 0.1.3+, one call at a time, and what an UNKNOWN becomes).
   A branch with no gate short of a build (`UNITY_WEBGL` on a GameKit older than 0.1.3, a PC-only branch while another
   target is active, PC-player-only code such as Steam's under `DISABLESTEAMWORKS`) is reported
   as unverified and also gets a Pending Play Mode line, so a later session still knows a build must check it. This
   step is the single source of that line's shape, during Build and Verify alike:
   `webgl unverified: <branch> - build webgl dev, serve over http, <action and expected result>` or `pc player
   unverified: <branch> - build windows dev, <action and expected result>` (build and serving steps: `platform-targets`).
4. References and ownership: who else reads the state you changed, and does anything else mutate it.
5. Lifecycle when the change touched one: `Awake` ordering, `OnEnable`/`OnDisable` symmetry, a mutable `static`
   without its `SubsystemRegistration` reset (Enter Play Mode Options keep statics between sessions).
6. Both targets when input or UI changed: read the input and UI code against `platform-targets` (Pointer events for
   touch and mouse, `SafeAreaFitter`, anchors for portrait and landscape). No tool here simulates touch or turns the
   screen, so the touch, orientation and safe-area run itself goes on the phone line of the handoff, never ticked
   from reading code.
7. Allocations only if the code is reached per frame (`unity-performance`).
8. Visual or startup change with the Editor open: `gk-bridge play-capture` in Bash (foreground: it ends within
   110 s), then open the screenshots it lists. Exit 0 = no errors logged; 1 = errors logged or compile failed (read
   `capture.log`: it is a fail, however good the stills look, except `FAILED ... Play Mode did not start`: the code
   never ran, so read `console.log` and treat it as exit 2 unless a game handler refused Play Mode, which is a
   fail); 2 = not run or stopped early (no Editor, busy, timeout,
   fewer shots): "play-capture not run", never a fail and never a pass. Play Mode starts in the scene open in the
   Editor: check from the stills that it is the scene the item is about, or the capture is no evidence for it.
   It enters Play Mode, records every error, and leaves by itself (about 5 s plus compile). It shows the first seconds
   only, so it never replaces the user's checklist. A still proves layout, clipping, presence and text; never timing,
   motion, feel or audio, which go to the user's checklist. To capture a hard-to-reach state, use a debug scene or an
   Editor-only entry point, never a change to game logic; when none exists and the step may not add one (a
   verify-only step told not to edit code), the item is Play Mode (user).

## Spec card

When `PLAN.md` Now holds a spec card (`gamekit:pipeline`), run each acceptance item's evidence check and tick the item
only with evidence that shows its outcome, on the same line: `- [x] <item> - play-capture: shot 2 shows the HUD
inside the safe area` or `- [x] <item> - Game/Ball.cs:41 resets it`. A compile pass shows only that the code
compiles, never a behaviour. The evidence kinds are the card template's in `gamekit:pipeline`. An item that needs
Play Mode stays unticked and moves to `PLAN.md` `## Pending Play Mode checks` and the handoff list. An item whose
check failed or could not run stays unticked with the state on its line (`- [ ] <item> - failed: <why>` or `- not
run: <why>`), so a later session and the reviewers can tell them apart. An item whose play-capture did not run also
gets a Pending Play Mode line (what to do and what to look at), since the user can check it by hand. Never reword an
item to make it pass.

- A behaviour item (what the player sees) is never ticked from reading code: code shows intent, not what the game
  does. `dosya:satır` ticks only a code-level claim; a behaviour needs play-capture, a test run (`gk-bridge
  run-tests`, only when the user said yes to it) or Play Mode (user).
- Evidence older than a later commit touching the same file is stale: run its check again before the handoff.
- A step or subagent report that names a file not on disk or a commit that does not exist has failed, however fluent
  it reads: check with `test -e <path>` (Bash; `Test-Path` in PowerShell) and `git cat-file -e <sha>^{commit}`.
- A pass with zero executed checks is "not verified", never done.

## The handoff

End with a short list of what to verify in Play Mode: concrete actions and what should happen, not a generic "test
it". Add a line for the phone when input, UI or performance changed (Device Simulator in the Game view is the cheap
first pass; a real device for feel and frame rate). Add a WebGL line when the card's Targets include WebGL and save,
audio, input or lifecycle changed (a dev build served over http, as `platform-targets` says), and the step 3 build
lines for an ungated branch. Call out separately anything that needs an Inspector or scene change (a new serialized
field left empty, a layer mask, a reference to assign), because nothing in the code reveals it. Every handoff line is
also written under `PLAN.md` `## Pending Play Mode checks`, so it survives `/clear` and compaction and the next session
knows what still waits on the user: in the change's own commit, or in a follow-up `design: pending checks` commit
when that one is already made; inside `/gamekit:feature` leave it uncommitted, its delivery step commits it, and
inside `gamekit:pipeline` leave it for phase 7's last commit.

After a bug fix the list is targeted, not a full-game pass: the exact bug scenario (it must not come back), related
edge cases in the same system, and every downstream reader of the fixed code path. Each line says what to do, what
passing looks like and what failing looks like. An open [yüksek] Known issue is named first: it blocks a playtest or
release build.

## Before a playtest build (not every change)

Gameplay checks are the user's: give them as Pending Play Mode checks.

1. Rapid input: mash or double-tap each action; try odd orders (pause during a transition, back button mid-animation).
2. Soak: the `unity-performance` Soak run (its length and pass rules live there only).
3. Stress: the largest entity count the design allows.
4. Regression: re-check each polish change by name, not "everything still works".
5. Audio: each action the design gives a sound plays it, and the levels are balanced.

The frame-time and GC sweep is `perf-auditor`; the weakest-device run goes to Pending when none is to hand. A metric
with no committed budget is reported as unverified, never as passing.

Do not escalate a small change into a test run or a build. If automated verification genuinely looks worth it, say why
in a sentence and ask (`gk-bridge run-tests`, `unity-testing`).
