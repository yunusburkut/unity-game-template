---
name: unity-architecture
description: Where new game code goes: Core simulation vs Game glue, state ownership, ScriptableObject tunables, saving, abstractions. Use when adding a gameplay system or a save, crossing the Core/Game boundary, wiring dependencies or making two systems talk.
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
types). Before handing over a change that touches Core, search `Assets/<Game>/Core` for
`\b(MonoBehaviour|GameObject|Transform|Time\.|Physics2?D?\.|Input\.|SceneManager)` with the Grep tool. Any hit
outside a comment is a boundary break to fix, not to justify.

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
replay its feedback every frame.

## Platforms

Core never knows the platform. Game turns platform input into the same `Input` struct (a tap and a click are one
`Pointer` press), so the rules are identical on PC and phone. A platform difference in the rules themselves (a
shorter level on mobile) is a tuning value, not an `#if`.

## Before adding an abstraction

Interfaces, factories, providers, wrappers and helper classes need a concrete reason today. Ask: is there a second
implementation right now, does it delete more code than it adds, does it allocate per frame, and will it still be
obvious in six months? If not, write the direct code. Prefer extending an existing type over a parallel one.
