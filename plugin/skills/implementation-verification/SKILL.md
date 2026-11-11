---
name: implementation-verification
description: Checking a game change cheaply after implementing it, and handing the user a short manual Play Mode checklist for PC and, when relevant, the phone. Use at the end of a normal implementation instead of running test suites, builds or broad validation.
---

# Verifying a change

Verification is proportional and cheap. Finish the implementation, then spend a minute, not a test run, confirming it.

## The pass

1. Read the diff. Look for what static reading catches: a flag set but never cleared, a field renamed without
   `[FormerlySerializedAs]`, an early `return` that skips cleanup.
2. Check `Logs/agent/compile.log`: `OK` (or `0 error(s)`) plus a timestamp newer than the edit means clean. An older
   timestamp means nothing has compiled the edit yet: write `refresh` into `Logs/agent/request.txt` where the bridge has
   it (it imports new files too), else run `unity command script recompile` or ask the user to alt-tab. `Logs/agent/console.log` holds the last
   200 Console errors and warnings.
3. Check references and ownership: who else reads the state you changed, and does anything else mutate it.
4. Check lifecycle when the change touched one: `Awake` ordering, `OnEnable`/`OnDisable` symmetry, a mutable `static`
   without its `SubsystemRegistration` reset.
5. Check both targets when input or UI changed: does it work with touch and with mouse, inside the safe area, at a
   portrait and a landscape aspect (`platform-targets`).
6. Check for allocations only if the code is reached per frame (`unity-performance`).
7. When the change is visual or touches startup, and the Editor is open: write `play-capture` into
   `Logs/agent/request.txt`, then read `Logs/agent/capture.log` and look at the three screenshots it lists. It enters
   Play Mode, records every error logged, and leaves Play Mode by itself (about 5 s plus compile time). It shows the
   first seconds of the scene only, so it never replaces the user's checklist.

## The handoff

End with a short list of what to verify in Play Mode: concrete actions and what should happen, not a generic "test
it". Add a line for the phone when input, UI or performance changed (Device Simulator in the Game view is the cheap
first pass; a real device for feel and frame rate). Call out separately anything that needs an Inspector or scene
change (a new serialized field left empty, a layer mask, a reference to assign), because nothing in the code reveals
it.

Do not escalate a small change into a test run or a build. If automated verification genuinely looks worth it, say why
in a sentence and ask (`unity-testing`).
