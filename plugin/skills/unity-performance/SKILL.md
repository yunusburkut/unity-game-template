---
name: unity-performance
description: Use when writing or changing code reached every frame, or for GC spikes, stutter ("kasıyor"), heat, memory growth or battery drain on phones and PCs. Update loops, physics queries, HUD text, pooling, draw calls, shaders, import settings, soak runs.
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
- `foreach` over an interface (`IEnumerable<T>`, `IList<T>`): the enumerator boxes. Over an array or `List<T>` it is
  allocation-free.
- `new WaitForSeconds` per `yield`: a timer in `Update`, or one cached instance when a coroutine is truly needed.
- `renderer.material`: it instantiates a copy (and leaks it unless destroyed). Swap `sharedMaterial` to a shared
  variant material (a hit flash swaps to one flash material and back). A `MaterialPropertyBlock` takes that renderer
  out of the SRP Batcher (and the GPU Resident Drawer): fine for a few renderers at once, not for many. Per-renderer
  data on many renderers: `Renderer.SetShaderUserValue` (read as `unity_RendererUserValue`), which keeps the SRP
  Batcher *(verify against the URP 17.6 SRP Batcher manual page before relying on it)*. Material instances you own
  (created once, destroyed with the object) stay batched: the SRP Batcher batches by shader variant, not by material.
- `Debug.Log` in runtime code: it allocates, stalls and writes to logcat every frame on a phone. Remove it or gate it
  under `#if UNITY_EDITOR || DEVELOPMENT_BUILD`.

How to apply these to existing code (cache-by-kind table, reading survey hits):
`refactor-pass/references/caching-and-hot-paths.md`.

## Prefer

- Allocation-free physics queries with a preallocated hit array: in 3D the `NonAlloc` overloads; in 2D the overloads
  that take a `ContactFilter2D` plus an array or `List<T>` (`Physics2D`'s `NonAlloc` methods are deprecated).
  `Physics.CheckSphere` when a boolean is enough.
- One `Update` on a manager driving N items over N MonoBehaviours each with their own `Update`.
- Pooling only where objects genuinely recur during play (projectiles, pickups, VFX), with
  `UnityEngine.Pool.ObjectPool<T>` (or `ListPool<T>` for scratch lists), not a hand-rolled pool.
- Many identical meshes: `Graphics.RenderMeshInstanced` with an instancing-enabled material, one call per material.
  It culls only the whole batch against `RenderParams.worldBounds`, never per instance, so it suits instances that
  have no GameObject (crowds, debris) and whose off-screen ones you skip yourself. Hundreds of ordinary
  `MeshRenderer` GameObjects on the PC tier: try URP's GPU Resident Drawer first (URP asset setting; needs the
  Forward+ or Deferred+ path and BatchRendererGroup Variants set to Keep All in Graphics settings; skinned meshes
  are not covered). On the Mobile tier measure it against plain SRP-Batcher GameObjects before keeping it.

## Mobile GPU budget

Phones are fill-rate and bandwidth bound, and run hot:

- The Mobile quality level has its own URP asset (`Assets/<Game>/Settings/URP_Mobile.asset`): no HDR, MSAA 2x, one
  shadow cascade. Tune quality there, not per object.
- Overdraw is the usual killer: large transparent quads, stacked UI panels, full-screen particles. Prefer opaque, cut
  particle counts on the Mobile tier.
- Particles: every system has an explicit Max Particles (lower on the Mobile tier); one-shot hit effects come from a
  pool. Never read GPU particle or compute data back to the CPU per frame.
- Post-processing: bloom and colour grading are affordable; depth of field, motion blur and SSAO are not, on Mobile.
- Textures and audio: per-platform importer overrides; the rules and their exceptions live in Asset audit below.
- Keep the frame at 60 fps with headroom: a phone at 100% load throttles within minutes, so a phone works to the
  phone budget in Measuring below, not to the full frame.

Custom shaders and passes:

- Every keyword doubles the variants. Use `shader_feature_local` for material toggles (unused variants are stripped);
  `multi_compile` only for keywords switched at runtime (always compiled); global keywords only for truly global
  features (fog, shadows).
- A hand-written URP shader keeps every material property in `CBUFFER_START(UnityPerMaterial)`, or it falls out of the
  SRP Batcher. The Frame Debugger shows its draws as "SRP Batch" when it is in.
- A one-off URP material (hit flash, dissolve, stylised water) starts in Shader Graph (URP Lit or Unlit target): it is
  SRP Batcher compatible by default and its keywords follow the same variant rules (keyword Definition: Shader
  Feature, Scope: Local). Hand-written HLSL is the toon-art pack's route (its `art-pipeline` skill).
- `half` for colour and most lighting math, `float` for positions and UVs.
- A custom `ScriptableRenderPass` implements `RecordRenderGraph(RenderGraph, ContextContainer)`. The old
  `Execute(ScriptableRenderContext, ref RenderingData)` belongs to URP Compatibility Mode, which this Unity no longer
  runs *(verify against the URP manual before writing one)*.
- Fragment cost on weak GPUs: `refactor-pass/references/low-end-devices.md` §4.

## Asset audit

Audit through the Editor, never from file headers or `.meta` files. The main session runs it (the read-only
perf-auditor never runs Unity): `unity command script run --file <absolute path of this skill's
scripts/AssetAudit.cs> --timeout 120`. It changes nothing and writes one row per texture and clip (type, source size,
Read/Write, mipmaps, default and per-platform max size and format; audio load type, format, Force To Mono, overrides)
to `Temp/asset-audit.txt`. It skips the vendored trees (`Assets/Feel`, `Assets/Plugins`, `Assets/TextMesh Pro`): their
import settings are the vendor's, and an unreferenced file there never ships. Judge each row against these rules:

- Textures: a max size per platform override, 1024 or less on phones (2048 for a hero texture the camera fills the
  screen with, such as a main character or a title backdrop); ASTC on Android and iOS; Read/Write off; mipmaps on for
  3D textures, off for UI; non-power-of-two only for UI sprites in an atlas.
- WebGL textures: the same max size rule as phones, and a compressed format (the Web build's Texture Compression
  setting picks DXT/BC for desktop browsers or ASTC/ETC2 for mobile ones); every texture is in the download, so an
  oversized or uncompressed one costs load time and the build's memory ceiling as well. Crunch shrinks the download
  further at some quality cost: judge it by eye.
- Audio: Vorbis for long clips, ADPCM for short frequent SFX; Streaming load type for music; Force To Mono for SFX.
  On WebGL the browser decodes the clips itself, so the load type and format columns matter little there; judge length,
  quality and Force To Mono, which set download size and memory *(verify against the Unity Web audio manual)*.
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

Where the user fetches it (in Git Bash prefix adb with `MSYS_NO_PATHCONV=1`, or the device path is rewritten to a
Windows one):
- Android: `adb pull /sdcard/Android/data/<bundle id>/files/`, or where that is blocked
  `adb exec-out run-as <bundle id> cat /sdcard/Android/data/<bundle id>/files/<name>.csv`; the exact path is in
  logcat as `FrameLog: ...`.
- Windows: `%USERPROFILE%\AppData\LocalLow\<Company>\<Product>\`.
- iOS: Xcode > Devices and Simulators > the app > Download Container (the CSV is under Documents).

What the frame columns mean at 60 fps: `fps` is the second's average; `p99_ms` is the 99th-percentile frame of the
last 10 s (the 6th-worst of about 600 frames), the sustained tail that a hitch pattern raises; `max_ms` is the single
worst frame of that second, the one-off hitch. One `max_ms` spike with a flat `p99_ms` is an isolated hitch (a load,
a GC); a rising `p99_ms` is frequent stutter.

WebGL (itch.io builds): FrameLog writes into the browser's virtual file system, so that CSV cannot be fetched; do not
ask for it. Measure with the F3 overlay (the user reads the numbers out), the Unity Profiler on a Development Build
with Autoconnect Profiler, or the browser's performance tools. The browser runs the game's managed code on one thread
and collects garbage only between frames, so per-frame allocation grows the heap toward the build's memory ceiling
instead of spiking a single frame: the 0 B rule matters most there.

Two numbers have a budget: frame time against DESIGN.md Platforms Frame target (vSync = the display's refresh rate;
still TODO, or vSync with an unknown refresh rate: not assessed, never headroom against an assumed 16.7 ms) and
`gc_bytes_per_frame` against 0 B. Which column is judged:

- **PC:** `p99_ms` against the full target frame. `fps` and `max_ms` are read, not judged: a lone `max_ms` spike is a
  hitch to explain (load, GC), not a budget miss.
- **Phones:** `p99_ms` against about 65% of the target frame (about 11 ms at 60 fps), so thermal throttling has
  room. `p99_ms` at 15-16 ms is a miss, not a pass. To say which side is over, `gpu_ms` is judged against the same
  11 ms; CPU work is judged on the Profiler's CPU main thread, or on `cpu_ms` only where the game's GameKit
  FrameLog computes it as `cpuMainThreadFrameTime` minus `cpuMainThreadPresentWaitTime` (main-thread work without the
  wait). GameKit 0.1.2 and older log `FrameTiming.cpuFrameTime`, which includes the vSync and `targetFrameRate` wait:
  on a capped phone it reads the frame time (about 16.7 at 60 fps) however light the work, so there it is read, never
  an AŞIM.
- The game's GameKit version is the `#gamekit-vX.Y.Z` tag in its `Packages/manifest.json` (a `file:` path means this
  template's `packages/` version). The CSV header is the same in every version, so the CSV cannot tell; an unknown
  version means `cpu_ms` is read, not judged.
- From GameKit 0.1.3, `cpu_ms` and `gpu_ms` are the second's average, judged per row like `fps`. In 0.1.2 and older
  they are one frame's timing sampled once a second: judge a minute of rows (the typical value and how often it is
  over), never one row.
- `gpu_ms` (or `cpu_ms`) of 0 means the device does not report it (no GPU timer queries on that graphics API): "not
  assessed", never within budget.

The other columns are read, not judged.

## Soak run

Leaks and thermal throttling show only in long sessions. Before a playtest build, a store upload or after a
memory-heavy change, ask the user for one Development Build session on the weakest target phone: fresh launch, other
apps closed, at least 30 min (60 min if the game's sessions are long), playing the loop and reloading levels or scenes
again and again. Then read the FrameLog CSV and judge against the session's own first 2 minutes, never an absolute MB
number:

- **Leak:** `sys_mb` or `gc_reserved_mb` higher after each reload and never coming back, across 3 or more reloads. One
  step up on the first load is normal; steady growth is the leak (`unity-debugging` names the mechanisms).
- **Thermal:** `fps` or `p99_ms` worse after 10-20 min with no new content or scene change. `cpu_ms` and `gpu_ms`
  say which side grew (throttling slows both; read them as Measuring says, and 0 is "not assessed"). Cut that
  side's cost on the Mobile tier.
- **Accumulation:** `slow_frames` or `max_ms` rising with play time: lists, pools or subscriptions that keep growing.
- **Allocation:** `gc_bytes_per_frame` above 0 in steady gameplay is a hot-path allocation at any length.

Report the first-2-min and last-2-min numbers side by side. Pass: memory flat after warm-up, fps within 10% of the
start, no crash. A run under 30 min, or no CSV, is not measured, never "stable". Fatigue notes (still fun at minute
25?) go to DESIGN.md Playtests.
