---
name: unity-performance
description: Keeping __GAME__'s per-frame code allocation-free and its frame time flat on phones and PCs — Update/FixedUpdate/LateUpdate, solver code, physics queries, HUD text, spawning, pooling, draw calls and overdraw. Use when writing or changing anything reached every frame, or when diagnosing GC spikes, stutter, heat or battery drain.
---

# Hot-path discipline

A hot path is anything reached per frame: `Update`, `FixedUpdate`, `LateUpdate`, the solvers, spawn logic, and
everything they call. The target is **flat frame time on a mid-range phone**; a PC then has headroom for free. A 0.3 ms
GC spike is worse than a 0.05 ms inefficiency. Outside hot paths, do not micro-optimise without evidence.

## Avoid in hot paths

- LINQ, capturing lambdas, boxing (`$""` / `string.Format` over value types), per-frame `new` on reference types
  (preallocate in `Awake`, `Clear()`), `Find*` / `GetComponent` / `Camera.main` / repeated `transform` (cache in
  `Awake`), `tag ==` (`CompareTag`).
- String building: cache the last displayed values, rebuild into a preallocated `StringBuilder` only when they change,
  and return early otherwise.

## Prefer

- `NonAlloc` physics overloads with a preallocated hit array; `Physics.CheckSphere` when a boolean is enough.
- One `Update` on a manager driving N items over N MonoBehaviours each with their own `Update`.
- Pooling only where objects genuinely recur during play (projectiles, pickups, VFX).
- Many identical meshes: `Graphics.RenderMeshInstanced` with an instancing-enabled material, one call per material.

## Mobile GPU budget

Phones are fill-rate and bandwidth bound, and run hot:

- The Mobile quality level has its own URP asset (`Assets/__GAME__/Settings/URP_Mobile.asset`): no HDR, MSAA 2x, one
  shadow cascade. Tune quality there, not per object.
- Overdraw is the usual killer: large transparent quads, stacked UI panels, full-screen particles. Prefer opaque, cut
  particle counts on the Mobile tier.
- Post-processing: bloom and colour grading are affordable; depth of field, motion blur and SSAO are not, on Mobile.
- Textures: set a max size per platform in the importer (phones rarely need above 1024), use ASTC on Android and iOS.
- Keep the frame at 60 fps with headroom: a phone at 100% load throttles within minutes.

## Struct passing

Simulation types are passed `in` to avoid a copy, which only pays off if every computed member on them is `readonly`;
otherwise the compiler inserts a defensive copy per access.

## Frame stepping

Run Update-driven simulation with `SimulationStep.Delta` (`Game/SimulationStep.cs`, clamped to 1/20 s) so a hitch
cannot tunnel anything through geometry. Do not move simulation to `FixedUpdate` without a reason: stepping at 50 Hz
against a 60 or 120 Hz display is what produces judder.

## Measuring

Only the Profiler confirms a spike, and only on the device: an Editor capture says little about a phone. Connect a
Development Build with Autoconnect Profiler, look at GC Alloc per frame (target: 0 B in gameplay) and the CPU main
thread. Hand that as steps to the user; do not guess numbers.

Every Development Build also runs `FrameLog` (Game): one CSV line per second (fps, p99, worst frame and where the
camera was, GC bytes per frame, draw and SetPass calls, CPU/GPU ms) in `Application.persistentDataPath`, and the same
numbers on screen with F3 or a three-finger tap. Ask the user for that CSV after a play session on the phone; it is the
cheapest real-device number there is.
