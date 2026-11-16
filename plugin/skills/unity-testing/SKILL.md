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
windows, scoring. Do not test getters, serialization, forwarding methods or MonoBehaviour glue. `CoreBoundaryTests`
(EditMode) guards the Core/Game split (project CLAUDE.md lists what it bans); keep it passing too: a failure there
means moving the offending code out of Core, never editing, skipping or ignoring the test.

`Assets/<Game>/Tests/PlayMode` references Core and Game. `MainSceneTests` loads `Main` and runs it for two seconds,
failing on any error log; keep it passing. A PlayMode test that plays the real scene to a win through the same input
events the player sends is worth one, once the core loop exists. The template does not wire that up yet; with the
user's OK add `"testables": ["com.unity.inputsystem"]` to `Packages/manifest.json` and `Unity.InputSystem` plus
`Unity.InputSystem.TestFramework` to the PlayMode asmdef, derive the test class from `InputTestFixture`, add devices
with `InputSystem.AddDevice<Keyboard>()` (or `Mouse`, `Touchscreen`) and drive them with `Press` / `Release` / `Set`.
Calling controller methods directly skips the input path, so such a test does not claim input coverage.

## House style

Follow `EasingTests` for the class comment, naming, assertion messages, `[ValueSource]` and float deltas. The
template has no Config-driven solver yet, so the Config and stepping rules below have no sample there; use this shape,
which steps a solver built from `unity-architecture`'s `references/core-system-skeleton.md` (`<System>Solver`,
`<System>Input`, `Step(ref state, in input, in tuning, dt)`; the Door names are illustrative). Ceiling: no check
compiles this sample; after a change to that skeleton's `Step` signature or Config/Tuning shape, re-check it by hand
the way the skeleton page says (its way up, a `test-template.ps1 -Tests` step, would cover a Countdown version of
this test too):

```csharp
DoorConfig config;
[SetUp] public void SetUp() => config = ScriptableObject.CreateInstance<DoorConfig>();
// `using System;` makes a bare Object ambiguous
[TearDown] public void TearDown() => UnityEngine.Object.DestroyImmediate(config);

const float Dt = 1f / 60f;

[Test]
public void OpenHeldPastDuration_ReachesFullyOpen()
{
    DoorTuning tuning = config.ToTuning();
    var state = new DoorState();
    int steps = Mathf.CeilToInt(tuning.OpenDuration / Dt) + 1;
    var hold = new DoorInput(true);
    for (int i = 0; i < steps; i++) DoorSolver.Step(ref state, in hold, in tuning, Dt);
    Assert.AreEqual(1f, state.Open01, 1e-4f, "OpenDuration dolunca kapı tam açık olmalı");
}
```

- A class comment saying why the contract matters.
- Build tuning from a fresh `ScriptableObject.CreateInstance<...Config>()` and `DestroyImmediate` it, so tests pin the
  rules at the code defaults, not the shipped asset values. Override only the fields the test pins, with a comment.
- Drive a solver by stepping it a counted number of times at a fixed `Dt`, asserting on the state.
- `[ValueSource]` to sweep an enum when every member shares one contract.
- Assertion messages in Turkish on every assert, the language the developer reads in the Test Runner. They are not
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

A test that failed once is not called flaky yet. `gk-bridge` runs only whole suites, so ask the user to run that test
alone three times from Unity's Test Runner window; with the Editor closed and the user's OK, three
`unity test <project> --mode <EditMode|PlayMode> --filter "<Namespace.Class.Test>"` runs (`unity-cli`) are the same
check. It is flaky only if those runs both pass and fail. Until then write
"şüpheli", never a fact. Skipping one: `[Ignore("flaky: <cause>")]` plus a Known issues line, never a silent delete.

## Running

Only with the user's OK, with the Editor open: `gk-bridge run-tests` (or `gk-bridge run-tests playmode`) in a
background Bash call; until it reports, edit no script and send no other `gk-bridge` request (a recompile mid-run
mixes old and new code, and gk-bridge answers UNKNOWN meanwhile). It runs a refresh gate first (not in a game whose own old AgentBridge copy has written no `bridge.log`
and that has no GameKit; gk-bridge then says "no refresh gate" in its output, and a pass there does not prove the
current code compiled or was tested) and prints the head of
`Logs/agent/tests.log`; exit 0 = pass, 1 = fail, 2 = unknown (never a pass). Scope: `run-tests` runs the whole
EditMode suite and `run-tests playmode` the whole PlayMode suite (`MainSceneTests` included); there is no name
filter. After a Core-only change propose EditMode; after a Game or scene change propose both (two runs, both covered
by the one OK when you name both up front). gk-bridge itself reports a run with `0 passed` as UNKNOWN (exit 2), so an
empty or filtered suite never passes the gate: a suite that is empty, filtered out, or whose test asmdef was left out
of the run proved nothing. An open scene with unsaved changes ends it `SKIPPED ... unsaved scene(s)` (the test
runner's save dialog would block the Editor): ask the user to save. If `Packages/manifest.json` pins GameKit below
`#gamekit-v0.1.1`, or the game keeps its own AgentBridge copy under `Assets/`, that dialog opens instead and blocks
the run until it times out: ask the user to save every open scene before `run-tests`. The Unity CLI also runs tests:
`unity test` (`unity-cli` has its flags, `--filter` and `--rerun-failed` included; `unity-editor-cli` covers gk-bridge).
Batch mode locks the project: never run it while the Editor is open.
