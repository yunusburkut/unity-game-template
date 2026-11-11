# SOLID in the Core/Game idiom

SOLID was written for object graphs. the game's simulation is value types and static functions,
and its Unity half is sealed MonoBehaviours wired in the Inspector — so each principle has to be
translated before it says anything useful here. The translation below is what the pass applies;
the textbook version is not.

Unity's own guidance (the Unity 6 edition of *Level up your code with design patterns and SOLID*)
closes with the same caution this file does: patterns "won't apply to every situation", and
applying SOLID as rules rather than as answers to a felt problem makes code worse, not better.

## Contents

1. Single responsibility — the five-part shape
2. Open-closed — the seams this shape already has
3. When a seam is justified, and which kind
4. Liskov — contracts on interfaces
5. Interface segregation — narrow readers
6. Dependency inversion — the asmdef is the abstraction
7. Anti-patterns to reject, with the reason
8. Worked shapes

## 1. Single responsibility — the five-part shape

Every mechanic built the `unity-architecture` way is split five ways, and "one reason to change"
maps onto the parts directly:

| Part | Example name | Changes when |
|---|---|---|
| Config (ScriptableObject) | `MovementConfig`, `BoardConfig` | A designer wants a new dial |
| Tuning (flat struct, `in`) | `MovementTuning` | The solver needs a derived value |
| State (struct, `ref`) | `MovementState` | Something new must survive between steps |
| Solver (static `Step`) | `MovementSolver` | The rule changes |
| Glue (sealed MonoBehaviour) | `PlayerController`, `BoardController` | Unity's side changes: physics, transforms, input |
| View (MonoBehaviour polling edges) | `PlayerFeel`, `BoardView` | Presentation changes |

The SRP question during a pass is therefore not "is this class doing two things" but "did two of
these rows end up in one file". Warning signs: a MonoBehaviour that both steps a solver *and*
decides how something looks (a growing block of pose or tween math in the controller — fine at 15
lines, its own view at 50); a Config exposing view-only fields (tolerated and noted, not churned,
because moving serialized data between assets is red).

Do not split a view that owns one transform into two views that share it. The rule is **one writer
per transform node** — the controller on the root, a feel component on a body child, Feel players
on a visual child — and that rule is worth more than any file length.

## 2. Open-closed — the seams this shape already has

OCP asks: can the next variant arrive without editing what works today? This codebase answers it
with data and polling more often than with polymorphism. Route new variation through these before
inventing another:

| Seam | How a variant arrives | Example |
|---|---|---|
| ScriptableObject config | A new asset, zero code | A heavy enemy vs. a light one is two configs |
| Enum + evaluation table | One enum member, one `case` | A new curve is one line in `Easing.Evaluate`; every consumer gets it |
| Small interface with ≥2 implementations | A new class, holder untouched | `IInteractable` implemented by a pickup and a lever; the interactor never changes |
| One-step edge flags polled by views | A new consumer, producer untouched | `Landed`, `Matched`, `Cleared` — the solver never learns who listens |
| Layer masks | An Inspector edit | A trigger that is deliberately dumb about what enters it |
| Published per-frame contract | A new reader | A moving platform's `Delta` that anything standing on it adds to its own move |
| Execution order chain | A new component slots between existing orders | The live chain is what `scripts/survey.sh` prints |
| Quality tier | A per-tier asset value, not code | Mobile vs. PC URP assets (`platform-targets`) |

"Enum + table" deserves a defence because a textbook would call the `switch` a violation. When
the set is closed, small and value-typed, a `switch` compiles to a jump table, allocates nothing
and is readable in one screen. An `IEase` with 23 classes would satisfy the letter of OCP and cost
a virtual call per evaluation inside the solver. Prefer the table whenever the variants are data,
not behaviour.

## 3. When a seam is justified, and which kind

Open a seam when **the second concrete variant exists or is scheduled**, not when one can be
imagined. Then choose the cheapest kind that fits:

1. **Data first.** Can the variant be a field on the existing config, or a new asset? (A door that
   needs "two of three switches" is a `requiredCount` on the door, not an `IDoorRule`.)
2. **Enum + table** when the variants are a closed set of formulas or clips.
3. **Interface** when the variants differ in *behaviour* and are Unity-side objects the holder must
   not know. Keep it to the members the holder actually calls, and document the contract in the
   interface's summary.
4. **Inheritance** — effectively never for MonoBehaviours. A base class with a virtual `Update`
   hides the frame order and invites the "which override ran" bug.

Before adding any of them, run `unity-architecture`'s questions: second implementation now;
deletes more than it adds; allocates nothing per frame; obvious in six months.

## 4. Liskov — contracts on interfaces

With no inheritance, LSP reduces to: every implementation of an interface must be safe to
substitute wherever the holder uses it. The contracts that usually matter:

- A `Can…` query is pure; it must not mutate anything. It often runs every frame.
- An action (`PickUp`, `Activate`) may be called after the world changed since the query said yes
  (another player or a second touch took it in between). Every implementation must handle that.
- A release / end call must leave the holder's state fully cleared, whatever the implementation
  does with the arguments.
- A label or prompt property returns a constant string, so the HUD can compare by reference and
  skip rebuilding text.

When a pass touches an interface, write its contract as `<summary>` text on the members if it is
not there yet. Contract comments are the only enforcement a duck-typed seam has.

## 5. Interface segregation — narrow readers

Views read narrow properties (`player.Speed`, `board.Score`) rather than the whole state struct,
and the HUD reads a prompt string rather than the focused object. Keep it that way. A view that
takes `in State` is acceptable when it is the designated edge consumer and copying would cost more
than the coupling.

Segregation smell: a method that takes a controller and uses one float of it. Pass the float.
Counter-smell: a method that takes six floats from the same object every frame. Pass the object.

## 6. Dependency inversion — the asmdef is the abstraction

`<Game>.Core` cannot reference `<Game>.Game`; the compiler enforces it. Core's "abstractions"
are its parameter shapes — `ref` state, `in` tuning, `bool grounded`, `ReadOnlySpan<T>` sets,
plain input structs. Game depends on Core concretes and that is correct: there is one simulation
and it is not going to be swapped.

So DIP here means: **never let Core learn about Unity's world**. A ground test, a raycast, a
transform read, a pointer read all come in as values. A pass that finds `Physics`, `Time`,
`GameObject`, `Input` or `MonoBehaviour` in Core moves the call to the caller and passes the result
in, keeping the `Step` signature shape. The same holds for the platform: Core never sees whether
the input came from a mouse or a finger.

Do not introduce `ISolver`, `ISimulation` or a solver factory. Static functions on value types
are already the most substitutable thing in C#: a test calls them directly.

## 7. Anti-patterns to reject, with the reason

| Proposal | Why not here |
|---|---|
| `GameManager` / singleton | Mutable static without a reset breaks on the second Play; ownership becomes "everyone". `unity-architecture` reserves one bootstrap for when wiring genuinely needs it. |
| Event bus / message broker | Producers stop knowing their consumers, so frame order becomes invisible. The answer here is edge flags polled in known order. |
| Abstract `InteractableBase : MonoBehaviour` | Adds a virtual call, hides `Awake` order, and implementations rarely share code. |
| Strategy objects inside the solver | Allocates or forces a class per strategy, breaks determinism reading, and the step is *one* argument. |
| Generic repository / registry of components | `FindObjectsByType` in disguise. Dependencies come through the Inspector. |
| DI container | CLAUDE.md: ask before adding a framework. |
| `PlatformService` with `IsMobile` checks everywhere | Platform differences live in the input mapping, the UI layout and the quality tier (`platform-targets`), not in gameplay branches. |
| "Utility" static class for math already in `Mathf` | A second name for the same thing. |
| Splitting `Config.ToTuning` into partial mappers | It is a flat copy; the flatness is the point. |

## 8. Worked shapes

**Dedupe (green).** Two paths that end a turn each reset half the state → one `EndTurn()` both
call. Copy the shape, not the names.

**Cache (green).** A per-frame `GetComponentInParent<Tile>()` on a raycast hit → `attachedRigidbody`
plus `TryGetComponent`, or a collider → component dictionary filled on first sight.

**A hypothetical second rule (data, not interface).** If a door needs "any two of three switches",
`requireAll` becomes `requiredCount` with a default that reproduces `requireAll`'s meaning for every
existing scene. No `IDoorRule`; no `DoorRuleConfig`. Red until asked, because it changes a
serialized field's meaning.

**Presentation values in a Core config (note, don't churn).** An ease or a colour on a Core config
read only by a view. Moving it to a Game-side asset would lose the serialized value
(`[FormerlySerializedAs]` does not cross types). Record it in the ledger as an accepted trade-off;
revisit when a second view needs it.
