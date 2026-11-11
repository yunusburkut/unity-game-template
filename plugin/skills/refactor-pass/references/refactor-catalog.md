# Refactor catalog for the game

Fowler's definition still holds: a refactoring is a small transformation that leaves observable
behaviour alone, applied one at a time with a check after each. In a Unity project "observable"
is wider than the C# — it includes what the scene serialized, what the Animator expects to be
called, what PhysX sees on the next fixed step, and what happens on the *second* Play session
with domain reload off. Every entry below names the transformation, then the trap that is specific
to this kind of project.

## Contents

1. The risk ladder
2. Green transformations
3. Amber transformations
4. Red — ask first
5. Things that look like refactors and are not
6. Diff checklist
7. Ledger format

## 1. The risk ladder

| Tag | Touches | Safety step | Autonomous? |
|---|---|---|---|
| green | Names, method boundaries, duplication, caching, member order, comments | Compile + read the diff | Yes |
| amber | Serialized fields, lifecycle methods, events, public members with external readers | Listed per entry below | Yes, and say so in the report |
| red | Solver arithmetic, `[DefaultExecutionOrder]`, `SimulationStep.Max`, enum ordinals, tuning defaults, test-pinned behaviour | Permission | No — list it |

## 2. Green transformations

**Rename** (locals, private fields, methods, parameters). Keep the repo's shapes: `_camelCase`
private fields, `PascalCase` members, `readonly struct` for one-frame data. A private
`[SerializeField]` is *not* green — see amber.

**Extract Method.** Only for an expression that appears twice, or a block whose name would carry
more than the block's comment does. Extracting from a solver: keep the helper `static`, take
`ref` state and `in` tuning exactly as the caller does, and never let it return a copy of the
state struct. Extracting from a MonoBehaviour: a private method, no new field.

**Inline Method.** Direct code beats a one-line forwarder, so inlining a method with one caller
and no explanatory name is a net gain. Keep the comment if the method carried one.

**Extract Variable / Introduce Explaining Variable.** Free in C#: a local float costs nothing.
Especially good for `Mathf.InverseLerp` / `Lerp` chains whose meaning is "0..1 how hard".

**Replace Magic Number with Named Constant** — only when the literal is either repeated or
unexplained. `SimulationStep.Max` (`Game/SimulationStep.cs`) is the precedent: one shared clamp.
A shared constant is a legitimate dedupe *as long as the value does not move*. A number that is a
feel decision belongs in the ScriptableObject, not in a `const`.

**Consolidate Duplicate Code.** The most valuable green move. When two release / reset / game-over
paths each clear half of the state, make every path converge on one method so no caller can
forget half of the reset — that is the shape.

**Decompose Conditional / Guard Clauses.** Early `return` on the "nothing to do" branch. Check that
the guard does not skip a reset that the fall-through used to perform.

**Cache a lookup.** `GetComponent*`, `transform`, `Camera.main`, `Animator.StringToHash`,
`Shader.PropertyToID`, query buffers — resolved in `Awake`, stored in a field. A hierarchy walk per
frame (`GetComponentInParent<T>()` on a ground or tap hit) becomes `collider.attachedRigidbody`
plus `TryGetComponent` when the target type carries `[RequireComponent(typeof(Rigidbody))]`;
same answer, no walk. See `caching-and-hot-paths.md`.

**Reorder members** to the repo's order: serialized fields, constants, private fields, public
properties, events, Unity messages in lifecycle order, public methods, private methods, gizmos.

**Comments.** Add the *why* where it is missing; delete a comment that restates the line below;
fix a comment that lies. Never delete a comment that records a measurement or a reverted attempt —
those are the cheapest tests the project has.

## 3. Amber transformations

**Rename a `[SerializeField]`.** Add `[FormerlySerializedAs("oldName")]` on the same field and
keep it until every scene and prefab has been re-saved. Name the assets that hold the field in the
report.

**Rename a public property or method.** Grep `Assets/<Game>` for every reader first, including
the Editor assembly (builders and setup code read config fields by name) and the EditMode tests.
If the member is an Animator parameter name, an `InputAction` name or a bone name, the string in
the asset wins and the C# does not change.

**Move a member between lifecycle methods.** A type that uses `Start` and not `Awake`, or resets a
field in `Awake` (scene reload is off), usually says why in a comment. Read the comment; if there
is none, the safe move is *not* to move it.

**Split a MonoBehaviour.** Legal when the two halves have different owners of state and different
frame slots (a controller that steps the simulation and a view that presents it). Both halves keep
their `[DefaultExecutionOrder]` relationships; the scene needs the new component added and wired,
so the report must say exactly what to add and where.

**Change an event subscription.** Pair every `+=` in `OnEnable` with `-=` in `OnDisable`, and
check whether anything subscribes in `Awake` on purpose (a subscriber that must survive a disable).

**Replace a bool flag with an enum on a ScriptableObject.** Only when the third state is real. The
new field gets a default equal to the old bool's meaning so existing assets behave identically.

## 4. Red — ask first

- Any arithmetic in a `Core` solver, including reordering additions (float is not associative; a
  reordering that changes the fourth decimal changes a test that pins a result, and can change what
  a replay or a second machine computes).
- `[DefaultExecutionOrder]` values. They are the frame pipeline; `scripts/survey.sh` prints the live
  chain. The reason is in a comment on the attribute or in the class summary.
- `SimulationStep.Max` and the choice of `Update` over `FixedUpdate`.
- Enum ordinals. Enums such as `Ease` are serialized as integers; inserting a member in the
  middle silently re-tunes every asset.
- Default values of serialized tunables. Existing assets keep their own value, so the change only
  hits new assets and tests — the worst kind of divergence.
- Deleting an "unused" public member. A hook can be unused by design (a clip that exists for a
  feature deliberately not built yet); read the class comment and `DESIGN.md` first.
- Anything a test asserts. Read `Assets/<Game>/Tests` before touching the type it names.

## 5. Things that look like refactors and are not

- **A bug fix.** Report it under its own heading. Changing behaviour the user did not ask to change,
  even towards "correct", breaks the promise this pass makes.
- **Replacing a loop with LINQ** ("Replace Loop with Pipeline"). Allocates an enumerator and often
  a closure; banned in anything reached per frame, and pointless elsewhere in this codebase.
- **Introducing an interface for one implementation.** `unity-architecture` already says no. The
  test is a second concrete type *in hand*.
- **Wrapping a Unity API** (`PhysicsQueries.OverlapSphere(...)`) to make it prettier. A wrapper is
  another place to look when the query misbehaves.
- **Moving tuning into code** or code into tuning. Where a number lives is a design decision.
- **Changing `Time.deltaTime` usage** — for instance passing `dt` to a `SmoothDamp` that used the
  implicit one, or the reverse. Identical in a steady frame, different in a hitch.
- **Adding a platform branch** "to be safe". A rule that differs per platform is a tuning value,
  not an `#if` (`platform-targets`).

## 6. Diff checklist

Read the complete diff once, top to bottom, asking:

- Is every one-step edge flag still cleared at the top of the step it belongs to?
- Does any new early `return` skip a reset, a write-back, a `Delta = …`, an unsubscribe?
- Did a struct passed by `in` gain a non-`readonly` method or property? (Defensive copy per call.)
- Did a `[SerializeField]` change name without `[FormerlySerializedAs]`?
- Did a `static` field appear without a `SubsystemRegistration` reset?
- Did a public member's readers all get updated, including Editor and Tests assemblies?
- Did any player-facing string change spelling, or any English identifier become non-English?
- Did a comment stop being true?
- Would the second Play session behave exactly like the first?
- Would a touch-only phone still reach every path a mouse reaches?

## 7. Ledger format

`docs/refactor-pass-log.md`, newest section first, machine-readable header. Create it on the first
pass:

```markdown
# Refactor pass log
last-pass: <full sha>

## 2026-01-15 — <one-line scope>
### Changed
- `Game/Board/BoardView.cs` — merged the two clear paths into `ClearSelection()` (green)
### Not changed (red)
- …
### Bugs seen
- …
### Low-end checklist
- …
### Noted between passes
- …
### Accepted trade-offs (do not re-flag)
- `BoardSolver.Step` length — one argument, kept whole.
```

The header line is what `scripts/survey.sh` reads. Keep *Accepted trade-offs* cumulative: copy the
previous section's list forward so it never has to be rediscovered.
