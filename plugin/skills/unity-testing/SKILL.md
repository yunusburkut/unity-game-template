---
name: unity-testing
description: Writing or running the game's EditMode or PlayMode tests. Use only when tests are explicitly asked for, at an approved milestone, or when a deterministic Core algorithm (rules, generator, solver) clearly warrants automated validation — running the suite always needs permission first.
---

# Tests

Automated tests are used **selectively**, not as a completion step. The default assumption is that the user verifies
gameplay manually in Play Mode.

## Permission

Ask before running the suite. Say what you want to test, why it is worth it now, and roughly how much you intend to
run, then wait. Reasonable moments to propose it: a gameplay system is finished, a substantial refactor has landed,
several dependent systems were integrated, or a change is high-risk and cheap to validate. Never during an ordinary
small change, and never twice for the same change.

## What is worth testing

`Assets/<Game>/Tests/EditMode` references `<Game>.Core` only, so only deterministic simulation is reachable, which
is also what is worth covering: rules, level generators and the solver that proves a level winnable, forgiveness
windows, scoring. Do not test getters, serialization, forwarding methods or MonoBehaviour glue.

`Assets/<Game>/Tests/PlayMode` references Core and Game. `MainSceneTests` loads `Main` and runs it for two seconds,
failing on any error log; keep it passing. A PlayMode test that plays the real scene to a win through the same input
events the player sends is worth one, once the core loop exists.

## House style

Follow `EasingTests`:

- A class comment saying why the contract matters.
- Build tuning from a fresh `ScriptableObject.CreateInstance<...Config>()` and `DestroyImmediate` it, so tests pin the
  rules at the code defaults, not the shipped asset values. Override only the fields the test pins, with a comment.
- Drive a solver by stepping it a counted number of times at a fixed `Dt`, asserting on the state.
- `[ValueSource]` to sweep an enum when every member shares one contract.
- Assertion messages in the player-facing language (CLAUDE.md).

## Running

Only with the user's OK, with the Editor open: `gk-bridge run-tests` (or `gk-bridge run-tests playmode`) in a
background Bash call. It runs a refresh gate first and prints the head of `Logs/agent/tests.log`; exit 0 = pass,
1 = fail, 2 = unknown (never a pass). An open scene with unsaved changes ends it `SKIPPED ... unsaved scene(s)`
(the test runner's save dialog would block the Editor): ask the user to save. An AgentBridge older than GameKit 0.1.1
opens that dialog instead, so ask first there too. The Unity CLI also runs tests (`unity-editor-cli`). Batch mode locks the project:
never run it while the Editor is open.
