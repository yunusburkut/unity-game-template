---
name: unity-testing
description: Writing or running EditMode/PlayMode tests ("test yaz", "testleri çalıştır", "birim testi"): house style, red/green, flaky causes, gk-bridge run-tests. Only when asked, at an approved milestone, or a Core rule/solver warrants it; ask first.
---

# Tests

Automated tests are used **selectively**, not as a completion step. The default assumption is that the user verifies
gameplay manually in Play Mode.

## Permission

Ask before writing a test and before running the suite (project CLAUDE.md: "ask first"); one OK may cover both. Say
what you want to test, why it is worth it now, and which suite you intend to run (EditMode, PlayMode or both; see
Running), then wait. Reasonable moments to propose it: a gameplay system is finished, a substantial refactor has
landed, several dependent systems were integrated, a deterministic Core rule, generator or solver was added, or a
change is high-risk and cheap to validate. Never during an ordinary small change, and never twice for the same change,
except the red and green runs of one regression test (House style), which a single OK covers.

## What is worth testing

`Assets/<Game>/Tests/EditMode` references `<Game>.Core` only, so only deterministic simulation is reachable, which
is also what is worth covering: rules, level generators and the solver that proves a level winnable, forgiveness
windows, scoring. Do not test getters, serialization, forwarding methods or MonoBehaviour glue.

`Assets/<Game>/Tests/PlayMode` references Core and Game. `MainSceneTests` loads `Main` and runs it for two seconds,
failing on any error log; keep it passing. A PlayMode test that plays the real scene to a win through the same input
events the player sends is worth one, once the core loop exists.

## House style

Follow `EasingTests` for the class comment, naming, assertion messages, `[ValueSource]` and float deltas. The
template has no Config-driven solver yet, so the Config and stepping rules below have no sample there; use this shape
(names are illustrative):

```csharp
DoorConfig config;
[SetUp] public void SetUp() => config = ScriptableObject.CreateInstance<DoorConfig>();
[TearDown] public void TearDown() => UnityEngine.Object.DestroyImmediate(config); // `using System;` makes bare Object ambiguous

const float Dt = 1f / 60f;

[Test]
public void OpenHeldPastDuration_ReachesFullyOpen()
{
    DoorTuning tuning = config.ToTuning();
    var state = new DoorState();
    int steps = Mathf.CeilToInt(tuning.OpenDuration / Dt) + 1;
    for (int i = 0; i < steps; i++) state = DoorStep.Step(state, true, in tuning, Dt);
    Assert.AreEqual(1f, state.Open01, 1e-4f, "OpenDuration dolunca kapı tam açık olmalı");
}
```

- A class comment saying why the contract matters.
- Build tuning from a fresh `ScriptableObject.CreateInstance<...Config>()` and `DestroyImmediate` it, so tests pin the
  rules at the code defaults, not the shipped asset values. Override only the fields the test pins, with a comment.
- Drive a solver by stepping it a counted number of times at a fixed `Dt`, asserting on the state.
- `[ValueSource]` to sweep an enum when every member shares one contract.
- Assertion messages in Turkish, the language the developer reads in the Test Runner (as `EasingTests`). They are not
  player-facing, so the player-facing language TODO in CLAUDE.md does not decide them.
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

A test that failed once is run alone (the user does that from Unity's Test Runner window; `gk-bridge` runs only whole
suites) and again before it is called flaky; under three runs it is "şüpheli", never a
fact. Skipping one: `[Ignore("flaky: <cause>")]` plus a Known issues line, never a silent delete.

## Running

Only with the user's OK, with the Editor open: `gk-bridge run-tests` (or `gk-bridge run-tests playmode`) in a
background Bash call. It runs a refresh gate first and prints the head of `Logs/agent/tests.log`; exit 0 = pass,
1 = fail, 2 = unknown (never a pass). Scope: `run-tests` runs the whole EditMode suite and `run-tests playmode` the
whole PlayMode suite (`MainSceneTests` included); there is no name filter. After a Core-only change propose EditMode;
after a Game or scene change propose both (two runs, both covered by the one OK when you name both up front). gk-bridge itself reports a run with
`0 passed` as UNKNOWN (exit 2), so an empty or filtered suite never passes the gate: a suite that is empty, filtered
out, or whose test asmdef was left out of the run proved nothing. An open scene with unsaved changes ends it `SKIPPED ... unsaved scene(s)`
(the test runner's save dialog would block the Editor): ask the user to save. An AgentBridge older than GameKit 0.1.1
opens that dialog instead, so ask first there too. The Unity CLI also runs tests (`unity-editor-cli`). Batch mode locks the project:
never run it while the Editor is open.
