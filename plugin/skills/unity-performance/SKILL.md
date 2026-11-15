---
name: unity-performance
description: Keeping the game's per-frame code allocation-free and its frame time flat on phones and PCs — Update loops, physics queries, HUD text, pooling, draw calls, shaders, import settings, soak runs. Use when writing or changing anything reached every frame, or when diagnosing GC spikes, stutter, heat, memory growth or battery drain.
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

- The Mobile quality level has its own URP asset (`Assets/<Game>/Settings/URP_Mobile.asset`): no HDR, MSAA 2x, one
  shadow cascade. Tune quality there, not per object.
- Overdraw is the usual killer: large transparent quads, stacked UI panels, full-screen particles. Prefer opaque, cut
  particle counts on the Mobile tier.
- Particles: every system has an explicit Max Particles (lower on the Mobile tier); one-shot hit effects come from a
  pool. Never read GPU particle or compute data back to the CPU per frame.
- Post-processing: bloom and colour grading are affordable; depth of field, motion blur and SSAO are not, on Mobile.
- Textures: set a max size per platform in the importer (phones rarely need above 1024), use ASTC on Android and iOS.
- Keep the frame at 60 fps with headroom: a phone at 100% load throttles within minutes.

Custom shaders and passes:

- Every keyword doubles the variants. Use `shader_feature_local` for material toggles (unused variants are stripped);
  `multi_compile` only for keywords switched at runtime (always compiled); global keywords only for truly global
  features (fog, shadows).
- A hand-written URP shader keeps every material property in `CBUFFER_START(UnityPerMaterial)`, or it falls out of the
  SRP Batcher. The Frame Debugger shows its draws as "SRP Batch" when it is in.
- `half` for colour and most lighting math, `float` for positions and UVs.
- A custom `ScriptableRenderPass` implements `RecordRenderGraph(RenderGraph, ContextContainer)`. The old
  `Execute(ScriptableRenderContext, ref RenderingData)` belongs to URP Compatibility Mode, which this Unity no longer
  runs *(verify against the URP manual before writing one)*.
- Fragment cost on weak GPUs: `refactor-pass/references/low-end-devices.md` §4.

## Asset audit

Audit through the Editor (`unity command script run` reading `TextureImporter` / `AudioImporter`), never from file
headers.

- Textures: a max size per platform override, 1024 or less on phones; ASTC on Android and iOS; Read/Write off;
  mipmaps off for UI; non-power-of-two only for UI sprites in an atlas.
- Audio: Vorbis for long clips, ADPCM for short frequent SFX; Streaming load type for music; Force To Mono for SFX.
- A value that cannot be read is "not assessed", never an estimate. Do not report orphan assets from a code grep:
  references live in scenes and prefabs. Report misses as ordinary [yüksek]/[orta]/[düşük] findings.

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

Every Development Build (not the Editor) also runs `FrameLog` (GameKit): one CSV line per second in
`Application.persistentDataPath/frame-log-*.csv` with `t_s, scene, fps, p99_ms, max_ms, slow_frames` (frames over
17 ms), `worst_x/y/z` (camera at the worst frame), `gc_bytes_per_frame, draw_calls, setpass_calls, cpu_ms, gpu_ms,
sys_mb, gc_reserved_mb`. F3 or a three-finger tap shows the frame numbers on screen. Ask the user for that CSV after a
play session on the phone; it is the cheapest real-device number there is.

Two numbers have a budget: frame ms against DESIGN.md Platforms Frame target (vSync = the display's refresh rate;
still TODO, or vSync with an unknown refresh rate: not assessed, never headroom against an assumed 16.7 ms) and `gc_bytes_per_frame` against 0 B. The other columns are read, not judged.

## Soak run

Leaks and thermal throttling show only in long sessions. Before a playtest build, a store upload or after a
memory-heavy change, ask the user for one Development Build session on the weakest target phone: fresh launch, other
apps closed, at least 30 min (60 min if the game's sessions are long), playing the loop and reloading levels or scenes
again and again. Then read the FrameLog CSV and judge against the session's own first 2 minutes, never an absolute MB
number:

- **Leak:** `sys_mb` or `gc_reserved_mb` higher after each reload and never coming back, across 3 or more reloads. One
  step up on the first load is normal; steady growth is the leak (`unity-debugging` names the mechanisms).
- **Thermal:** `fps` or `p99_ms` worse after 10-20 min with no new content or scene change. `cpu_ms` and `gpu_ms`
  say which side grew (throttling slows both); `gpu_ms` of 0 means not available on this device, not flat. Cut that
  side's cost on the Mobile tier.
- **Accumulation:** `slow_frames` or `max_ms` rising with play time: lists, pools or subscriptions that keep growing.
- **Allocation:** `gc_bytes_per_frame` above 0 in steady gameplay is a hot-path allocation at any length.

Report the first-2-min and last-2-min numbers side by side. Pass: memory flat after warm-up, fps within 10% of the
start, no crash. A run under 30 min, or no CSV, is not measured, never "stable". Fatigue notes (still fun at minute
25?) go to DESIGN.md Playtests.
