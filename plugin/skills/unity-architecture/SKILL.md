---
name: unity-architecture
description: Where new game code goes ("bu kod nereye", "yeni sistem", "kayıt ekle"): Core simulation vs Game glue, state, ScriptableObject tunables, saving, scene flow. Use when adding a gameplay system, a save or a screen, or making two systems talk.
---

# Where code goes

## The split, concretely

`<Game>.Core` holds the rules; `<Game>.Game` holds everything Unity insists on owning. The test for which side a
piece belongs on is not "is it gameplay" but **"could it run with no scene?"** The point is reproducibility and
testability: the same state, inputs and `dt` give the same result on the same build, so a bug seen on a phone replays
in an EditMode test. Movement math, board rules, state machines, timers, scoring and forgiveness windows can. A
raycast, a `CharacterController.Move`, an `InputAction` read and a `Transform` write cannot.

This is not cross-device determinism. `dt` varies per frame and float results can differ between builds (ARM IL2CPP
vs x64 Mono), so replays, lockstep and rollback netcode need a fixed tick and inputs recorded per tick on top of this
shape; the shape makes that possible but does not provide it.

World queries stay in Game and reach the solver as values. Per frame the MonoBehaviour: reads input and runs the
queries the rules need (grounded, hit normal, overlap, the cell under the pointer), packs them into `<System>Input`,
calls `Step`, then applies the result the solver left in `State` (a desired displacement or velocity, a cell to clear)
through `CharacterController.Move`, a `Rigidbody` or a `Transform` write. What the world did with it (the resolved
contact, a blocked move) comes back as next frame's query results; the solver never calls physics. The step runs in
`Update` with `SimulationStep.Delta`, not in `FixedUpdate` (which stops at time scale 0 and drops presses); changing
that choice is a red-tier refactor (`refactor-pass`).

A `Rigidbody` (or `Rigidbody2D`) is the one apply target that splits across clocks. The solver still steps in `Update`
and leaves a desired velocity, or an impulse accumulated over the frame, in `State`; the glue writes it to the body in
`FixedUpdate` (set `linearVelocity`, or one `AddForce(impulse, ForceMode.Impulse)` of the accumulated sum, then zero
it), with `interpolation` set to `Interpolate` so the body does not stutter between physics steps. `MovePosition` and
`ForceMode.Force` called from `Update` depend on frame rate (MovePosition keeps only the last write; forces pile up
between steps), so they never go there. A game whose rules are the physics itself (the `genre-defaults`
physics-puzzle sheet: shots applied in `FixedUpdate`, PhysX solves the rest) is the documented exception and not a
red-tier break; its Core holds what physics does not decide (aiming, scoring, the win check).

The shape every Core system follows:

- `<System>Input` — a `readonly struct` of one frame's intent, produced by Game from touch, mouse or keys.
- `<System>State` — a mutable `struct` holding everything carried between steps. Game owns one instance and hands it
  over by `ref`.
- `<System>Tuning` — flattened tunables, taken by the step as `in`. Computed members are `readonly` so `in` costs no
  defensive copy.
- `<System>Config` — the ScriptableObject in Core the designer edits, with `ToTuning()` returning the struct. It is
  the one `UnityEngine.Object` Core may hold (as `project/CLAUDE.md` states): data only, no callbacks, no scene
  references. It stays in Core because the EditMode tests reference Core alone and build tuning from it.
- `<System>Solver.Step(ref state, in input, in tuning, float dt)` — static, deterministic, allocation-free, no `Time`.
- A MonoBehaviour in Game feeds the step `SimulationStep.Delta`, applies the result and drives the view.

`Ease` / `Easing` are the smallest example of a Core type, but a stateless one. The full shape, one minimal system
with every part above and its glue, is `references/core-system-skeleton.md`. A new system mirrors it unless it has a
concrete reason not to.

Checking the boundary: no compiler catches a scene API in Core (the Core asmdef references the engine for the math
types). The source of truth is `Tests/EditMode/CoreBoundaryTests.cs`, which runs with the EditMode tests: it bans the
physics and input assemblies, any component type, and the scene APIs in its `Banned` regex; a new ban goes there.
Before handing over a change that touches Core, run the same regex as a cheap check with the Grep tool on
`Assets/<Game>/Core`: read `Banned` from the test (no copy is kept here, so a new ban is never missed), join its
string pieces, and rewrite each lookbehind `(?<![\w.])` as `(^|[^\w.])`, since the Grep tool's engine has no
lookbehind; `state.Time` and `System.Random` then pass as they do in the test.
`Core_HoldsNoSceneOrAssetReference` catches a `Transform` (or any other non-ScriptableObject `UnityEngine.Object`)
field; a method parameter or return of such a type is caught by neither test, so look for those too. Any hit outside
a comment is a boundary break to fix, not to justify.

## Ownership

- State lives with whoever advances it. The MonoBehaviour owns its `State`; the solver is stateless. Do not introduce
  a manager that also holds a copy.
- Dependencies come in through `[SerializeField] private` and are guaranteed by the scene. Do not re-null-check them
  per method. If one can genuinely be absent, fail loudly once in `Awake` (`Debug.LogError` + `enabled = false`).
- There is no composition root and no DI container. If one becomes necessary it is a single `GameBootstrap`
  MonoBehaviour wiring things once in `Awake`, not a service locator.
- Avoid global mutable state. If a `static` is genuinely right, it needs the `SubsystemRegistration` reset (Play Mode
  reload is disabled).

## Saving

- The save data is a plain `[Serializable]` type in Core with an `int version`. Validate and migrate
  in Core too (data in, data out), so an EditMode test can cover an old version and a corrupt file when tests are
  asked for. (De)serialising stays in Game with the file I/O, the path and the error handling around them, so Core
  only ever sees an already-parsed object.
- Each shipped version keeps its own `[Serializable]` type in Core (`SaveDataV1`, `SaveDataV2`), never edited once
  shipped. Game first parses a small `{ int version; }` probe, then calls `FromJson` on that version's type and hands
  it to Core, which migrates V1 to V2 and so on up to the current one. `FromJson` into the current type instead would
  drop a renamed or removed field's value and leave missing fields at their defaults before any migration runs.
- File I/O and `JsonUtility` live in one Game class that owns the path (`Application.persistentDataPath` plus a fixed name), the
  atomic write and the `.bak` fallback (`unity-code-review` item 4). Nothing else touches the file.
- Save at checkpoints and on pause (`platform-targets` App lifecycle).

## Cross-system communication

Prefer a direct serialized reference, then a public property read by the interested party (the HUD reads
`controller.Score` rather than the controller pushing events at it). Reach for C# events only when the producer must
not know its consumers, and unsubscribe in `OnDisable`.

The solver exposes one-step edge flags on its state (`Landed`, `Matched`, `Cleared`, reset at the top of every step):
the view polls the edge instead of Core calling into the view. That is how Core stays free of presentation and Feel.
The controller calls `Step` every frame, also while paused or at time scale 0 (`dt` is then 0), and hands the `State`
to its view in the same `Update`, right after the step. A view never polls on its own schedule: its `Update` order
against the controller is undefined, so it would react a frame late, and a skipped step would leave a flag set and
replay its feedback every frame. A game that substeps (`SimulationStep`'s ceiling: slices of at most `Max` per
frame) would lose an edge set in an early slice to the reset of the next one, so the controller ORs each edge flag
across the frame's slices and hands the view that combined `State` once.

Animator controllers and driving them from Core state: `unity-editor-cli` references/animation.md (Animation and
Timeline below says where they sit in the split).

The view is `<System>View` in the system's own folder (`Assets/<Game>/Game/<System>/`). It owns that system's
presentation, including its serialized `MMF_Player` fields (`feel-authoring`), so a system's feedbacks are found next
to its controller and the controller never grows a field per event.

## Animation and Timeline

- An Animator is presentation: it lives on the view's prefab and only the view sets its parameters, from the `State`
  the controller hands it (continuous values as floats or bools, edge flags as triggers). Core never reads a pose, a
  clip time or an animation event, so the rules play the same with the Animator culled or missing.
- Keep a controller small and built by its Editor builder (animation.md): one base layer, a blend tree for continuous
  locomotion instead of a state per speed, a sub-state machine per mode (combat, carry) once one layer passes about a
  dozen states, and Any State only for the few edge triggers that must always fire, never a web of Any State edges.
- Timeline (`com.unity.timeline`, added per game through `unity-package-management`) is only for authored
  sequences: intros, cutscenes, a level-clear reveal. It never drives simulation, timers or rules. `GameFlow` starts the
  `PlayableDirector` and holds the gameplay action map off while it plays; the sequence reports back through a Signal
  or the director's `stopped` event, and gameplay state changes only in the flow call that follows.

## Game flow and scenes

- One `Main` scene (the one ProjectSetup creates) is the game. Menu, pause, results and settings are uGUI screens in
  it (`ui-ugui`), shown and hidden, not separate scenes. Add scenes only for content too big to keep loaded (levels,
  worlds), loaded additively with `SceneManager.LoadSceneAsync(name, LoadSceneMode.Additive)` and unloaded with
  `UnloadSceneAsync`, while `Main` keeps the camera, UI and flow.
- One flow owner in Game (`GameFlow`, a MonoBehaviour with a state enum: Menu, Playing, Paused, Results) switches
  screens and starts or ends a run. Screens and systems read `flow.State`; they do not show or hide each other. If
  the flow has rules (lives, unlock order), those go to Core like any other system.
- Pause is `Time.timeScale = 0` plus disabling the gameplay action map. The Back/pause action (`platform-targets`
  App lifecycle) lives in the UI map, which stays enabled, so Esc, the pad and Android back can still unpause. Systems keep stepping with `dt` 0 (the split
  above), menus and their tweens run on unscaled time, and the app-lifecycle pause (`platform-targets`) goes through
  the same flow call.
- Loading is always async. On phones show a progress UI (`AsyncOperation.progress` stops at 0.9 while
  `allowSceneActivation` is false) and never call the synchronous `LoadScene` in play: it freezes the frame and can
  trip the OS watchdog.
- Restarting a run resets `State` (`default` or a fresh `Restart` input) rather than reloading the scene: faster, and
  nothing stale survives. A `DontDestroyOnLoad` object outlives scene loads within a run
  (exiting Play Mode still destroys it); with domain reload off a `static` outlives the Play session too and needs the
  `SubsystemRegistration` reset (Ownership). Anything that must persist across a run lives in `Main`, which is never
  unloaded.

## Platforms

Core never knows the platform. Game turns platform input into the same `Input` struct (a tap and a click are one
`Pointer` press), so the rules are identical on PC and phone. A platform difference in the rules themselves (a
shorter level on mobile) is a tuning value, not an `#if`.

## Before adding an abstraction

Interfaces, factories, providers, wrappers and helper classes need a concrete reason today. Ask: is there a second
implementation right now, does it delete more code than it adds, does it allocate per frame, and will it still be
obvious in six months? If not, write the direct code. Prefer extending an existing type over a parallel one.
