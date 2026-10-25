---
name: unity-architecture
description: Deciding where new __GAME__ code belongs — Core simulation vs Game glue, ownership of state, ScriptableObject tunables, and when an abstraction is justified. Use when adding a gameplay system, moving code across the Core/Game boundary, wiring dependencies, or choosing how two systems talk.
---

# Where code goes

## The split, concretely

`__GAME__.Core` holds the rules; `__GAME__.Game` holds everything Unity insists on owning. The test for which side a
piece belongs on is not "is it gameplay" but **"could it run with no scene?"** The point is determinism and
testability: the same `dt` step gives the same answer every time, in an EditMode test as on a phone. Movement math,
board rules, state machines, timers, scoring and forgiveness windows can. A raycast, a `CharacterController.Move`, an
`InputAction` read and a `Transform` write cannot.

The shape every Core system follows:

- `<System>Input` — a `readonly struct` of one frame's intent, produced by Game from touch, mouse or keys.
- `<System>State` — a mutable `struct` holding everything carried between steps. Game owns one instance and hands it
  over by `ref`.
- `<System>Tuning` — flattened tunables, taken by the step as `in`. Computed members are `readonly` so `in` costs no
  defensive copy.
- `<System>Config` — the ScriptableObject in Core the designer edits, with `ToTuning()` returning the struct.
- `<System>Solver.Step(ref state, in input, in tuning, float dt)` — static, deterministic, allocation-free, no `Time`.
- A MonoBehaviour in Game feeds the step `SimulationStep.Delta`, applies the result and drives the view.

`Ease` / `Easing` are the smallest example of a Core type. A new system mirrors the shape above unless it has a
concrete reason not to.

## Ownership

- State lives with whoever advances it. The MonoBehaviour owns its `State`; the solver is stateless. Do not introduce
  a manager that also holds a copy.
- Dependencies come in through `[SerializeField] private` and are guaranteed by the scene. Do not re-null-check them
  per method. If one can genuinely be absent, fail loudly once in `Awake` (`Debug.LogError` + `enabled = false`).
- There is no composition root and no DI container. If one becomes necessary it is a single `GameBootstrap`
  MonoBehaviour wiring things once in `Awake`, not a service locator.
- Avoid global mutable state. If a `static` is genuinely right, it needs the `SubsystemRegistration` reset (Play Mode
  reload is disabled).

## Cross-system communication

Prefer a direct serialized reference, then a public property read by the interested party (the HUD reads
`controller.Score` rather than the controller pushing events at it). Reach for C# events only when the producer must
not know its consumers, and unsubscribe in `OnDisable`.

The solver exposes one-step edge flags on its state (`Landed`, `Matched`, `Cleared`, reset at the top of every step):
the view polls the edge instead of Core calling into the view. That is how Core stays free of presentation and Feel.

## Platforms

Core never knows the platform. Game turns platform input into the same `Input` struct (a tap and a click are one
`Pointer` press), so the rules are identical on PC and phone. A platform difference in the rules themselves (a
shorter level on mobile) is a tuning value, not an `#if`.

## Before adding an abstraction

Interfaces, factories, providers, wrappers and helper classes need a concrete reason today. Ask: is there a second
implementation right now, does it delete more code than it adds, does it allocate per frame, and will it still be
obvious in six months? If not, write the direct code. Prefer extending an existing type over a parallel one.
