---
name: implementation-verification
description: Checking a game change cheaply after implementing it, ticking the spec card's acceptance items with evidence, and handing the user a short Play Mode checklist for PC and, when relevant, the phone. Use at the end of every implementation instead of test suites, builds or broad validation.
---

# Verifying a change

Verification is proportional and cheap: a minute, not a test run. Every claim names its evidence; a check that could
not run is reported as unverified, never as passed.

## The pass

1. Read the diff. Look for what static reading catches: a flag set but never cleared, a field renamed without
   `[FormerlySerializedAs]`, an early `return` that skips cleanup.
2. Compile gate: `gk-bridge refresh` in Bash (not found: `bash "${CLAUDE_PLUGIN_ROOT}/bin/gk-bridge" refresh`). Exit
   0 = clean and newer than every script; 1 = errors (fix them; a verify-only step reports them); 2 = unknown (no
   Editor, Play Mode, busy): say "compile unverified" in the handoff. `Logs/agent/console.log` holds the last 200
   Console errors and warnings.
3. Platform code changed: the Editor compiles only the active build target's `#if` branches, never a `!UNITY_EDITOR`
   one, and Device Simulator does not simulate `#define`s. Check the others: `UNITY_ANDROID` → `gk-bridge compile
   android`, `UNITY_IOS` → `gk-bridge compile ios`, `!UNITY_EDITOR` → both. `UNITY_WEBGL`, a PC-only branch while
   another target is active, and PC-player-only code (a `!UNITY_EDITOR` branch phones skip, such as Steam's under
   `DISABLESTEAMWORKS`) have no compile request: report them as unverified.
4. References and ownership: who else reads the state you changed, and does anything else mutate it.
5. Lifecycle when the change touched one: `Awake` ordering, `OnEnable`/`OnDisable` symmetry, a mutable `static`
   without its `SubsystemRegistration` reset (Enter Play Mode Options keep statics between sessions).
6. Both targets when input or UI changed: touch and mouse, inside the safe area, portrait and landscape
   (`platform-targets`).
7. Allocations only if the code is reached per frame (`unity-performance`).
8. Visual or startup change with the Editor open: `gk-bridge play-capture` in Bash (foreground: it ends within
   110 s), then open the three screenshots it lists.
   It enters Play Mode, records every error, and leaves by itself (about 5 s plus compile). It shows the first seconds
   only, so it never replaces the user's checklist.

## Spec card

When `PLAN.md` Now holds a spec card (`gamekit:pipeline`), run each acceptance item's evidence check and tick the item
only with evidence that shows its outcome, on the same line: `- [x] <item> - play-capture: shot 2 shows the HUD
inside the safe area` or `- [x] <item> - Game/Ball.cs:41 resets it`. A compile pass shows only that the code
compiles, never a behaviour. An item that needs Play Mode stays unticked and moves to the handoff list. An item whose
check failed or could not run stays unticked with the state on its line (`- [ ] <item> - failed: <why>` or `- not
run: <why>`), so a later session and the reviewers can tell them apart. Never reword an item to make it pass.

## The handoff

End with a short list of what to verify in Play Mode: concrete actions and what should happen, not a generic "test
it". Add a line for the phone when input, UI or performance changed (Device Simulator in the Game view is the cheap
first pass; a real device for feel and frame rate). Call out separately anything that needs an Inspector or scene
change (a new serialized field left empty, a layer mask, a reference to assign), because nothing in the code reveals
it.

Do not escalate a small change into a test run or a build. If automated verification genuinely looks worth it, say why
in a sentence and ask (`gk-bridge run-tests`, `unity-testing`).
