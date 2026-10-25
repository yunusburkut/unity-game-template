---
name: unity-code-review
description: Reviewing existing __GAME__ C# for correctness, architectural fit, Unity lifecycle and ownership problems, hidden allocations, platform gaps between PC and mobile, and unnecessary complexity. Use when asked to review, audit or critique code rather than write it.
---

# Reviewing code

Report what materially matters. Do not nitpick style that already matches its surroundings.

## Look for, in rough priority order

1. **Correctness** — off-by-one in timer windows, state flags set but never cleared (one-step edge flags must reset at
   the top of every step), sign errors, order dependencies between systems.
2. **Boundary violations** — a `MonoBehaviour`, `Physics` call, `Time` or `Input` access or scene API that has drifted
   into `__GAME__.Core`; game rules that have drifted into a MonoBehaviour.
3. **Lifecycle** — work in `Awake` that depends on another object's `Awake`; `OnEnable` subscriptions with no matching
   `OnDisable`; a mutable `static` with no `SubsystemRegistration` reset (Play Mode reload is disabled, so this only
   breaks on the second Play).
4. **Platform gaps** — input that only works with a mouse or only with keys, UI placed outside the safe area or sized
   in pixels instead of through the `CanvasScaler`, `#if UNITY_EDITOR` logic the build depends on, a feature with no
   path on one of the targets (`platform-targets`).
5. **Ownership** — two objects mutating the same state, or state duplicated across a view and its simulation.
6. **Hidden allocations** in anything reached per frame (`unity-performance`).
7. **Unnecessary complexity** — an interface with one implementation, a wrapper that only forwards, a factory for a
   single `new`, defensive null checks on Inspector-guaranteed dependencies, `try`/`catch` around code that cannot
   throw, unreachable fallback branches.
8. **Duplicated logic** — especially a second copy of a tuning number that already lives in a ScriptableObject.
9. **Inspector consequences** — a renamed serialized field silently loses its scene value unless it carries
   `[FormerlySerializedAs]`. Flag it, and say which assets need re-checking.

## Convention checks

Player-facing and Inspector-facing strings in the language CLAUDE.md names, English for everything else. Comments carry
non-obvious intent, an invariant, or a performance reason, never a restatement of the line below. Flag comments that
do restate it.
