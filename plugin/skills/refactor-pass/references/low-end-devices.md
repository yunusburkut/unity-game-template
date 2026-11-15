# Low-end headroom: weak PCs and mid-range phones

The game ships on PC and on phones. On both, the audience's weakest common device decides the
reviews: a laptop with an integrated GPU on PC, a two- or three-year-old mid-range Android on
mobile. Nothing in the C# decides whether that works; the render pipeline assets, the renderers,
the volume profiles and the quality tiers do. This file is the audit the pass runs over those
assets and the code-side rules that keep the headroom the assets buy.

Two constraints frame all of it. Asset changes are made **through the running Editor**
(`unity-editor-cli` / `unity command script run`), never by editing `.asset` YAML while Unity is open. And a
target has to exist before any number is judged: propose one, mark it *target to be set*, and let
the user confirm.

## Contents

1. Proposed targets
2. Settings audit, per tier
3. Quality tiers: the shape the template builds
4. Code-side rules
5. Phones: heat, battery and frame pacing
6. Physics and frame pacing on PC
7. Verifying on the device that matters
8. Sources

## 1. Proposed targets

*Targets to be set:*

- **PC Low:** a 2019-class laptop with an integrated GPU (Intel UHD 620 / AMD Vega 8 class, 4 CPU
  threads, shared memory) holding a steady 60 fps at 1080p, with 30 fps as the never-below floor.
- **Mobile:** a mid-range Android from about three years ago (Snapdragon 6-series / Mali-G57 class,
  4–6 GB RAM) and an iPhone from about five years ago holding a steady 60 fps for 20 minutes
  without thermal throttling. A low-end Android (2–3 GB RAM, Mali-G52 class) holding 30 fps is the
  floor if the user wants that market.

If the user names a different device, every row below is re-judged against it.

At 60 fps the whole frame is 16.7 ms and CPU and GPU each get the full budget in parallel. On an
integrated GPU and on a phone the GPU side is almost always the one that is over — phones are
fill-rate and bandwidth bound — which is why the audit is mostly about the render assets, not C#.

## 2. Settings audit, per tier

Read from `Assets/<Game>/Settings/URP_Mobile.asset`, `URP_PC.asset`, their `_Renderer` assets,
the scene volume profiles and `ProjectSettings/QualitySettings.asset`. Re-read the assets before
quoting; these values move.

| Setting | Template default (Mobile / PC) | Low-end proposal | Why |
|---|---|---|---|
| Quality levels | Mobile (0), PC (1) | Add a PC Low tier when the PC target is an iGPU; split Mobile into Low/High only when one phone tier cannot hold both targets | One level per platform means no headroom lever on that platform. |
| Rendering path | Forward / Forward (`ProjectSetup` never sets it, so both renderers keep the `UniversalRendererData` default; check the renderer asset, a game may have changed it) | **Keep Forward** on Low and Mobile; Forward+ on PC only after measuring | Forward+ runs a light-culling pass; with one directional light and few point lights plain Forward is often cheaper. |
| GPU Resident Drawer | Off / per project | PC only, after measuring; verify BRG variants are *Keep All* | Needs compute and Forward+; not a mobile lever, and it skips Animator-driven renderers anyway. |
| SRP Batcher | On | On | Reduces per-draw CPU setup on every tier. |
| Static batching | Per project | Off if GRD is on; on otherwise for static scenery | A statically batched renderer is a slice of a combined mesh GRD cannot instance. |
| HDR | Off / On | Off on Low and Mobile | At URP's default 32-bit HDR precision (B10G11R11) the colour buffer is the same size as LDR RGBA8; the saving is the HDR post work (wider-range bloom, tonemapping) and the 64-bit RGBA16F buffer used when *HDR Precision* is 64-bit, the camera output needs alpha, or the device cannot blend B10G11R11. Bloom degrades but works in LDR. |
| MSAA | 2x / 4x | 2x or off on Mobile; off on PC Low | On tile-based mobile GPUs 2x is cheap; on an iGPU it is bandwidth. |
| Render Scale | 1.0 | 0.8–0.85 on Low; on phones consider 0.75–0.9 with FSR/Bilinear | Largest single GPU lever. A phone's high-dpi screen hides it well. |
| Depth Texture | Off unless needed | On only if a shader or SSAO reads `_CameraDepthTexture` | An extra pass on some paths. |
| Opaque Texture | Off | **Off** on every tier unless a shader samples `_CameraOpaqueTexture` | A full-screen colour copy every frame. |
| Main light shadows | 1024, 1 cascade, 25 m / 2048, 2 cascades, 50 m | 1024, 1–2 cascades, shortest distance the camera needs | Cascades multiply shadow draw passes. |
| Soft shadows | Off / On | Off on Low and Mobile | Extra PCF taps per shadowed pixel. |
| Additional lights | Per project | Per-vertex or disabled on Low/Mobile; **shadows off** | Additional light shadows are the classic iGPU and phone killer. |
| Reflection probe blending / box projection | Per project | Off on Low/Mobile | Two probe samples per pixel instead of one. |
| SSAO renderer feature | None | **Never on Mobile**; downsampled on PC High only | Depth-normals prepass plus full-screen AO plus blur. |
| Post: Bloom | Per project | Fewer iterations / lower quality on Low and Mobile | A mip chain of blits. |
| Post: Tonemapping | Per project | Neutral over ACES on Low and Mobile | ACES is the costlier curve. |
| Post: DoF, Motion Blur, Lens effects | Per project | Off on Mobile | Full-screen passes the screen size does not justify. |
| Color grading | Per project | LDR mode, LUT 16 on Low and Mobile | The URP manual's explicit recommendation. |
| LOD cross-fade | Per project | Bayer dithering, or off on Mobile | Cheaper than blue noise. |
| Textures | Per importer | Per-platform override; rules and the hero-texture exception: `unity-performance` Asset audit | Memory and bandwidth; the importer's per-platform override beats a runtime branch. |
| Graphics APIs | Unity default | Windows: D3D11 first for old iGPU drivers, DX12 deliberately. Android: Vulkan first with an OpenGLES3 fallback, unless a target device misbehaves on Vulkan | Old drivers are where crashes on launch come from. |
| Shader variants / prewarm | Nothing preloaded | Turn on *Log Shader Compilation* in a dev build once to find first-use hitches, then a `ShaderVariantCollection` prewarm at boot | First-time shader compiles are the stutter a laptop or phone will report. |

## 3. Quality tiers: the shape the template builds

Unity's guidance is one URP asset (and renderer) per quality level, switched with
`QualitySettings.SetQualityLevel` only at boot or from a settings menu — switching mid-play causes
a significant one-off stall. `ProjectSetup` already creates Mobile (0, phones and WebGL) and PC
(1). To add a tier:

1. Duplicate the nearest URP asset and its renderer (`URP_PC` → `URP_PCLow`), apply the Low column
   above, and add the quality level in Project Settings with that asset assigned. Per-platform
   defaults stay: Standalone → PC, everything else → Mobile.
2. A small Game-side `QualityBootstrap` (one, in the first scene, `Awake`): reads a saved choice
   from `PlayerPrefs`; with none, picks the low tier on PC when `SystemInfo.graphicsMemorySize` is
   small or the adapter is integrated, and on phones when `SystemInfo.systemMemorySize` is low.
   Player-facing labels in the game's language. No other component reads quality.
3. Nothing else in the code mentions quality. Feel players, particles and lights stay authored;
   the tier decides how they are drawn.

This is Inspector work plus one small script; the pass writes the checklist and, if asked, the
script. It does not hand-edit the assets.

## 4. Code-side rules

These are the code habits that keep whatever the tier bought:

- **Split the HUD Canvas.** A uGUI `Text` change dirties its whole Canvas, and the Canvas rebuilds
  every element it contains. Put text that changes during play on its own Canvas so static text is
  never re-batched.
- **Overdraw on phones.** Stacked full-screen UI panels, large transparent quads and full-screen
  particles are the usual mobile GPU cost; disable (not just hide with alpha 0) panels that are
  closed, and turn off `Raycast Target` on non-interactive graphics.
- **`sharedMaterial`, never `.material`,** on anything instanced. A material instance breaks
  batching for that renderer and leaks until scene unload.
- **No realtime additional lights with shadows** authored in levels. If a level needs a glow, it is
  emissive + Bloom, not a shadow-casting point light.
- **Particles**: cap `maxParticles` on every system, avoid soft particles and per-particle lights,
  cut counts on the Mobile tier.
- **Custom shaders**: few texture samples in the fragment stage and none inside a loop; `step` / `smoothstep` /
  `lerp` over a dynamic branch; a blur in two passes (horizontal, then vertical); a heavy effect has a cheaper
  fallback on the low tier. Keywords, the SRP Batcher CBUFFER and `half` precision are in `unity-performance`; watch
  the variant count in the build log.
- **No `Camera.main`, no `FindObjectsByType`, no per-frame `Text` rebuilds** — `unity-performance`.
- **Keep the simulation in `Update` with `SimulationStep.Delta`.** On a slow device `Time.deltaTime`
  grows; the clamp keeps things from tunnelling and the solver deterministic enough to reason
  about. Never remove it "because the device is fast".
- **Target frame rate is a setting, not a constant.** A battery-saver 30 fps option is read from
  the same bootstrap as quality and applied once.

## 5. Phones: heat, battery and frame pacing

- A phone at sustained 100 % GPU throttles within minutes and the frame rate halves. Headroom is
  the target: aim for the frame done in the phone budget in `unity-performance` Measuring (about 11 ms at 60 fps).
- `Application.targetFrameRate = 60` is set by `AppStartup`; vSync does nothing on mobile. A 120 Hz
  phone still runs 60 unless the game asks for more; do not ask for more unless the game needs it.
- Menus and paused screens can drop to 30 fps (`targetFrameRate`) — free battery.
- `OnDemandRendering.renderFrameInterval` lets a static screen (a puzzle board waiting for input)
  render less often while input stays responsive.
- Measure thermal behaviour with a soak run on the device (`unity-performance` Soak run, 30 min or more), not a
  30-second capture.

## 6. Physics and frame pacing on PC

Check `ProjectSettings/TimeManager.asset`: Fixed Timestep and Maximum Allowed Timestep. The
simulation does not run in `FixedUpdate`, but PhysX still steps triggers and kinematic bodies on
the fixed clock. With a large allowance (Unity's default 0.333 s), a 300 ms hitch (a shader compile
on a laptop) makes the next frame run many physics steps, which makes *that* frame long, which is
the spiral. Proposal: Maximum Allowed Timestep **0.1**. It also caps `Time.deltaTime`, so check
the feel after a hitch before changing it.

vSync on PC holds a finished frame for the next refresh with frames queued behind it; for a game
where input latency matters, vSync off with a frame cap (e.g. 2× the refresh rate) is the
alternative — a settings toggle if a player minds tearing.

## 7. Verifying on the device that matters

1. **Development Build**, not the Editor. Editor numbers include the Editor.
2. On the target laptop or phone, connect the Profiler (Autoconnect Profiler, or USB/ADB for
   Android). The **Highlights** module says CPU-bound or GPU-bound against the target first.
3. GPU-bound → toggle one row of the audit table at a time in the tier's asset and re-read the GPU
   time. The Frame Debugger shows the pass list; SSAO, the opaque copy and shadow cascades are
   visible as named passes and their disappearance is the proof. On Android, the vendor GPU tools
   (Android GPU Inspector, Arm Performance Studio, Snapdragon Profiler) show bandwidth.
4. CPU-bound → CPU module, Timeline: `Canvas.BuildBatch`, `Physics.Simulate` step count,
   `GC.Alloc` markers, then the `Update` markers of the scripts in scope.
5. Record both numbers in the ledger with the scene, the device, and the build hash.

## 8. Sources

- Unity Manual (6000.x), *Adjust settings to improve performance in URP* — the per-setting
  recommendations in the table above.
- Unity Manual (6000.x), *GPU Resident Drawer* — requirements and excluded objects.
- Unity Manual (6000.6), *New in Unity 6.6* — dynamic batching removed, DXC for DX12, Profiler
  Highlights default.
- Unity Manual (6000.x), *Change the active URP Asset at runtime* — one URP asset per quality
  level, switch only when performance does not matter.
- Unity, *Optimize your game performance for mobile, XR, and the web in Unity (Unity 6 edition)*
  and *…for consoles and PCs (Unity 6 edition)* e-books.
- Unity, *Best practices for profiling game performance*; Highlights module reference.

Device-class examples in section 1 are proposals, not measured facts; recheck them against current
hardware surveys (Steam Hardware Survey, Google Play Console device catalog) before quoting.
