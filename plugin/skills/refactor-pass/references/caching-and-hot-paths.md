# Caching and hot paths

`unity-performance` holds the rules. This file is the pass's procedure for applying them to code
that already exists: what "cache it" concretely means per kind of lookup, what the survey script's
hits usually turn out to be, what is still true in Unity 6.6, and how to prove a change mattered
when it is not an allocation.

## Contents

1. What "caching" means, by kind
2. Reading a survey hit
3. Struct discipline
4. Unity 6.6 facts that change advice
5. Proving it, when proof is needed
6. What not to touch

## 1. What "caching" means, by kind

| Lookup | Cost if repeated | Cache as | Where |
|---|---|---|---|
| `GetComponent<T>()`, `GetComponentInParent`, `GetComponentsInChildren` | Native call; the parent/children forms walk the hierarchy; the plural form allocates an array | Field | `Awake` |
| `transform` | Native call per access | `Transform _transform` | `Awake` |
| `Camera.main` | Tag search (cached internally since 2020, still a call) | `[SerializeField] Camera` | Inspector |
| Animator parameter names | String hash per call | `static readonly int XHash = Animator.StringToHash("X")` | Static — a readonly `int` is immutable, so no reset needed |
| Shader property names | String hash per call | `static readonly int XId = Shader.PropertyToID("_X")` | Static |
| Config → tuning | Struct copy | Field, rebuilt every frame only under `#if UNITY_EDITOR` (so Inspector tweaks are felt live) | `Awake` + editor `Update` |
| Physics query results | Array allocation | Preallocated `Collider[]` / `RaycastHit[]` with the `NonAlloc` overload | Field initialiser |
| HUD strings | `string` allocation + Canvas rebuild | Last-displayed values + one `StringBuilder`; return early when unchanged | View |
| `WaitForSeconds` | Allocation per `yield` | Timers in `Update`, or one cached `WaitForSeconds` if a coroutine is truly needed | — |
| Delegates for events | Allocation per `+=` | Subscribe once in `OnEnable`, never per frame | — |
| Input actions | Lookup by string per frame | `InputAction` field or a generated wrapper resolved once | `Awake` / `OnEnable` |
| Materials | `renderer.material` instantiates a copy and leaks it | `sharedMaterial` swap or a `MaterialPropertyBlock` for one-off overrides | — |
| Bone / child lookups by name | Hierarchy walk + string compare | Fields resolved once | `Awake` |
| `LayerMask` tests | Cheap already | Inline bit test `(mask.value & (1 << layer)) != 0` | — |

The rule of thumb: anything whose answer cannot change between frames is resolved in `Awake`;
anything that can change is resolved per frame but never allocates. `Awake` runs once per Play
session even with domain reload off, so caches built there are always fresh — it is `static` state
that is not.

## 2. Reading a survey hit

`scripts/survey.sh` greps by line and cannot see the enclosing method. Interpret hits like this:

| Hit | Usually | Act |
|---|---|---|
| `GetComponent…` | In `Awake` — fine. In a Unity message or a per-frame helper — cache. In `OnTriggerEnter` — acceptable (event-driven), unless the trigger is crossed by many bodies every frame. | Read the method |
| `GetComponentInParent<T>` on a per-frame query result | Hierarchy walk per hit per frame | If `T` has `[RequireComponent(typeof(Rigidbody))]`, use `collider.attachedRigidbody` + `TryGetComponent`. Otherwise cache collider→component in a dictionary filled on first sight. |
| `foreach` | Over an array or `List<T>`: allocation-free (struct enumerators). Over an `IEnumerable<T>` / interface: boxes. | Change only the interface-typed case |
| `$"…"` / `string.Format` / `+ "` | In `Debug.LogError` inside `Awake`: fine, runs once. In `Update`: allocation every frame. | Last-value gate + `StringBuilder` |
| `new List<…>` / `new T[…]` | In a field initialiser or `Awake`: fine. In a method: per-call allocation. | Hoist to a field, `Clear()` per use |
| `Debug.Log(` in runtime code | Allocates and stalls, and on a phone writes to logcat every frame | Remove or gate under `#if UNITY_EDITOR || DEVELOPMENT_BUILD` |
| `Find(`, `FindObjectOfType`, `FindObjectsByType` | Scene scan | Inspector reference |
| `.tag ==` | Allocates the tag string | `CompareTag` |
| `.material` | Instantiates a material | `sharedMaterial` or `MaterialPropertyBlock` |
| Lambda / `=>` with captured locals in a per-frame method | Display-class allocation | Method group or a cached delegate |
| `static` field, not `readonly`/`const`; or a `static readonly` collection, array or object (`readonly` fixes the reference, not its contents) | Survives Play sessions: a registry list keeps destroyed entries into the next Play | `[RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.SubsystemRegistration)]` reset |
| `Mouse.current` / `Touchscreen.current` / `UnityEngine.Input` | Works on one target only | Not a perf item: a platform bug. `<Pointer>` actions (`platform-targets`) |
| `#if UNITY_ANDROID` / `UNITY_IOS` | Platform branch | Fine for a real platform API in one small Game file; a gameplay rule behind it is a bug |

A per-frame cost with **no allocation** (a hierarchy walk, a redundant `SetPositionAndRotation`, a
second loop over four items) is fixed only when the fix is also simpler to read. Otherwise
`unity-performance` applies: do not micro-optimise without evidence.

## 3. Struct discipline

- Tuning structs are passed `in`. Every computed member on them must be `readonly` (member
  methods and properties), or the compiler copies the whole struct on each access. A pass that
  adds a helper to a tuning struct adds `readonly`.
- State structs are passed `ref` and mutated in place. Never return a state struct from a helper;
  never copy it into a local "for readability" — that is the bug where the copy is updated and the
  original is not.
- One-frame data is a `readonly struct` with a constructor (an input snapshot, a hit result).
- `ReadOnlySpan<T>` over a preallocated array is the way to pass a variable-length set to a solver
  without allocating. Keep that shape for any new solver that takes a set.
- Do not reach for `stackalloc`, `Span<byte>` tricks or `unsafe`; the asmdefs disallow unsafe and
  nothing in a typical frame is large enough to need them.

## 4. Unity 6.6 facts that change advice

Verified against the 6000.6 *What's new* page and the URP manual; recheck if the project moves off
6000.6.

- **Dynamic batching is removed.** Never recommend it. Draw-call work goes to the SRP Batcher and,
  on PC and capable phones, the GPU Resident Drawer.
- **Domain reload off is Unity's default** for new projects, which this project already runs. The
  6.6 Project Auditor ships an *Auto Statics* Roslyn analyzer that flags static fields needing a
  reset — a package, so ask before adding it; the manual grep in the survey script is the free
  version.
- **Burst is a built-in module.** Rarely justified for gameplay solvers: each `Step` is microseconds
  and Burst wants `Unity.Mathematics` types, not `Mathf`. Mention only if a solver ever iterates
  thousands of items (a big grid, a particle-like simulation). Burst on WebGL needs its own check.
- **The Profiler opens on the Highlights module** by default. It answers "CPU-bound or GPU-bound
  against the target frame time" before any deeper module is opened.
- **`Dictionary<TKey,TValue>` is serializable** with `[SerializeField]`. Useful for an authored
  lookup that used to be two parallel arrays; not a reason to add one.
- **Incremental GC** (`gcIncremental`) spreads collection cost across frames; it does not make
  allocations free, and a spike still shows as a longer frame — on a phone, also as heat.
- **3D physics `NonAlloc` overloads are still current.** `Physics2D`'s were deprecated in favour of
  array/list overloads; 3D has no `Span` overloads as of 6.6.
- **uGUI `LayoutElement` gained `maxWidth` / `maxHeight`**, and `ContentSizeFitter` a clamped mode.
  Relevant when a HUD grows layout groups; nested layout groups are still a rebuild cost.

## 5. Proving it, when proof is needed

Removing a per-frame allocation needs no measurement: the `GC.Alloc` column in the Profiler's CPU
module going to zero for that marker *is* the proof, and it is visible in one capture. Anything else:

1. Open the Profiler; the Highlights module states target frame time and whether CPU or GPU is
   over it. If the game is GPU-bound, no C# refactor will move the number — go to
   `low-end-devices.md`.
2. In the CPU module, Timeline view, find the marker (the controller's `Update`, `Canvas.BuildBatch`
   for HUD text) and read its self time and its `GC.Alloc` column across ~300 frames.
   `Profiler.BeginSample("Name")`/`EndSample` around a suspect block gives it a marker; they compile
   out of release builds.
3. Capture before and after in the **same scene at the same spot**, on the **same device**, in a
   Development Build. `FrameLog`'s CSV (if the game has it) gives p99 and worst frame without the
   Profiler attached. Compare medians, not single frames.
4. Report the two numbers in the ledger. A change that did not move the number is reverted unless
   it also made the code simpler.

Do not benchmark in the Editor's Stats overlay, and do not compare an Editor number to a build, or
a PC number to a phone.

## 6. What not to touch

- `Config.ToTuning()` per frame under `#if UNITY_EDITOR`: a struct copy, deliberate, so a slider
  is felt live. Builds do it once.
- O(n²) loops over a handful of items (players, carriers, selected pieces) when making them O(n)
  would make them wrong or unreadable.
- Per-frame pruning of a small list that a comment says `OnTriggerExit` alone cannot be trusted
  with.
- Editor code (`Assets/<Game>/Editor`): LINQ and string building are fine there; it never ships.
