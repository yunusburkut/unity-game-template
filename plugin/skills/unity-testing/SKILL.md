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
- Name it `<Scenario>_<Expected>` (`JumpBufferedBeforeLanding_JumpsOnLandFrame`), never `Test1` or `Basic`. Every
  test asserts the outcome its name states: a test with no `Assert` passes and proves nothing.
- A Core formula or step covers: a typical input and its expected output; zero or empty input (no crash, the minimum
  output); the maximum (no overflow, NaN or infinity); negative modifiers where allowed; each edge case the DESIGN.md
  rule names. A numeric bound gets the minimum, the cap and one value past each. The test names the formula or
  Config field it pins, so a tuning change points at it.
- Computed floats: `Assert.AreEqual(expected, actual, 1e-4f)` or `Is.EqualTo(expected).Within(1e-4f)`, never exact.
- A test written for a bug fix runs against the unfixed code first and must fail; only then apply the fix and see it
  pass. A regression test only ever seen passing is not known to test anything, and the fixture is usually why (an
  iteration-order bug tested on a board where no cell takes part in two moves per step). Running it still needs the
  user's OK, so this applies only when such a test is being written anyway.

## A test that passes and fails

| Cause | Sign | Fix |
|---|---|---|
| Order dependency | Passes alone, fails after another test | A shared static or a leftover object: reset statics in `[SetUp]` (no domain reload runs between tests), `DestroyImmediate` every object and ScriptableObject the test creates |
| Float equality | `Assert.AreEqual(0.5f, x)` on a computed value | Compare with a delta, as above |
| Randomness | `UnityEngine.Random` or an unseeded `new System.Random()` | Pass a fixed seed into the Core step |
| Timing | A PlayMode test waits a real-time duration | Step a counted number of frames, or yield on a condition with a frame cap; never `WaitForSeconds` as a correctness gate |
| Scene load race | Asserts right after `LoadScene` | `yield return null` (or wait for the scene's `isLoaded`) first |

A test that failed once is run alone and again before it is called flaky; under three runs it is "şüpheli", never a
fact. Skipping one: `[Ignore("flaky: <cause>")]` plus a Known issues line, never a silent delete.

## Running

Only with the user's OK, with the Editor open: `gk-bridge run-tests` (or `gk-bridge run-tests playmode`) in a
background Bash call. It runs a refresh gate first and prints the head of `Logs/agent/tests.log`; exit 0 = pass,
1 = fail, 2 = unknown (never a pass). `0 passed` is UNKNOWN too, whatever the exit code: a suite that is empty,
filtered out or not compiled into the run proved nothing. An open scene with unsaved changes ends it `SKIPPED ... unsaved scene(s)`
(the test runner's save dialog would block the Editor): ask the user to save. An AgentBridge older than GameKit 0.1.1
opens that dialog instead, so ask first there too. The Unity CLI also runs tests (`unity-editor-cli`). Batch mode locks the project:
never run it while the Editor is open.
