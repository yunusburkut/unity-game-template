---
name: urp-postprocessing
description: URP post-processing through Volumes: bloom, tonemapping, color grading, DoF, vignette, motion blur, per-tier look ("parlama", "renk ayarı", "post-process", "sönük"). Feel post-process shakers: feel-authoring; tier cost: unity-performance.
required_packages:
  com.unity.render-pipelines.universal: ">=17.6.0"
---

> **House edits (gamekit).** A copy of Unity's skill (version in `LICENSE.md`); a refresh is a merge that keeps these
> (`gamekit:unity-editor-cli`, its refreshing-copies reference). Local: this description and the URP floor (the
> version the template pins: stack order, `volumeProfile` and the snippets' `FindObjectsByType<T>()`); section 0's `script run`
> prerequisite and `script eval` limits; pre-flight check 2's two-tier override, check 3's 2D Renderer line and the
> snippet's per-tier and 2D checks; section 1's stack order; the stripping Key Fact; debugging items 7, 9 and 10;
> section 5's tier labels, the SDR Mobile recipe and "One profile, two tiers"; section 6's tier, save and revert lines;
> in `references/code-templates.md`, the `script run` intro, "Before and after", the Settings-folder and rerun guards,
> the scene-dirty checks, the Create template's per-tier note, "Per-tier Volume Profile on each URP asset" and "Undo
> and reverting"; in `references/effect-reference.md`, Bloom `filter` and lens dirt, Tonemapping's HDR output
> parameters and Screen Space Lens Flare (read from URP 17.6's `Runtime/Overrides`).

Help the user set up, configure, and debug post-processing effects using URP's Volume framework.

**Goal: The user should have a working visual result with zero console errors after setup.**

## 0. Prerequisite: an Editor you can run C# in

Volume profiles, `VolumeParameter.overrideState`, and the camera's post-processing flags are
Editor/runtime object state — the checks and edits below all run C# inside a live Editor.

**The `unity-cli` skill owns getting you there** — installing the CLI, confirming a connected
Editor, adding the project's `com.unity.pipeline` package, telling a genuinely absent Editor
apart from one stuck in Safe Mode, and discovering the Editor's command catalog. Follow it
first; don't re-derive any of it here. If the Editor cannot run C#, say so and stop.

**In this template, run every snippet below with `script run`** (`gamekit:unity-editor-cli`, "Prefer
`script run` over `script eval`"): save it as a `.cs` file in the scratchpad directory (outside
`Assets/`) holding one class with one public static method, then

```powershell
unity command script run --file <absolute .cs path> --timeout 60
```

The method's return value comes back to you; a `throw` fails the run loudly. `using` directives and
helper methods work there, so the snippets are written as normal C# files.

### If you use `script eval` instead

Only for a one-line read. `eval` compiles a **statement block, not a file**, and has a 5 s
main-thread budget (`CreateAsset` + `SaveAssets` in one eval can exceed it, leaving a profile
without its Volume). Two consequences, both of which cause a compile error rather than a warning:

- **No `using` directives.** The compiler reads `using UnityEngine;` as a resource-disposal
  statement and rejects it (`CS0210`).
- **Types must be fully qualified.** A bare `AssetDatabase` or `Volume` does not resolve
  (`CS0246` / `CS0103`), and a bare `Object` is ambiguous with `object` (`CS0104`).

## 0. Pre-Flight Checks

Before configuring any effect, **verify all checks**. Fix failures first, except where check 2 says
the "failure" is the template's design.

1. **URP is the active render pipeline** — If not, inform the user and stop.
2. **HDR per quality tier** — Tonemapping requires HDR. Bloom works best with HDR; in SDR it still works but `threshold` must be < 1.
   **Template override:** this template has two quality levels, each with its own URP asset under
   `Assets/<Game>/Settings`: Mobile (level 0, phones and WebGL) with HDR **off** on purpose, and PC (level 1) with HDR on
   (`gamekit:unity-performance`, `gamekit:platform-targets`). `UniversalRenderPipeline.asset` reports only the level the
   Editor is on (usually PC), so check every level. On the Mobile tier, do not turn HDR on to make an effect work: skip
   Tonemapping there and use Bloom with `threshold` < 1. Enabling HDR on Mobile is a frame-budget decision: ask first.
3. **Camera has post-processing enabled** — `renderPostProcessing` must be `true` (defaults to `false`). Camera Stacking: only a `CameraRenderType.Base` camera (or the last `Overlay` in the stack) should enable post-processing. Also verify the Renderer's PostProcessData asset is not null — if it is, the post-process pass won't exist. 2D games (the `mobile-2d` pack) use the 2D Renderer (`Renderer2DData`), which carries PostProcessData too; the snippet checks both.
4. **The Volume's GameObject layer is in the Camera's Volume Layer Mask** — `volumeLayerMask` defaults to layer 0 "Default" only. The Volume's `GameObject.layer` must be included, otherwise the camera ignores it.
5. **Volume exists with `enabled = true`, a valid Profile, and at least one override** — The `Volume` component must be enabled, have a non-null `profile` (or `sharedProfile`), and at least one active `VolumeComponent` with `overrideState = true` on its properties.

### Pre-Flight Check Snippet

Run this with `script run` to verify the setup programmatically:

```csharp
using System.Linq;
using System.Text;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

public static class PostFxPreflight
{
    public static string Run()
    {
        var report = new StringBuilder();

        // 1. Check URP is active — a hard stop, so throw: it fails the run loudly
        if (UniversalRenderPipeline.asset == null)
            throw new System.Exception("URP is not the active render pipeline.");

        // 2. HDR and PostProcessData on every quality tier, not only the one the Editor is on
        for (int i = 0; i < QualitySettings.count; i++)
        {
            var tier = QualitySettings.names[i];
            if (QualitySettings.GetRenderPipelineAssetAt(i) is not UniversalRenderPipelineAsset urp)
            { report.AppendLine($"Warning: quality level '{tier}' has no URP asset (falls back to the default)."); continue; }
            report.AppendLine($"Tier '{tier}': HDR {(urp.supportsHDR ? "on" : "off (SDR: no Tonemapping, Bloom threshold < 1)")}.");
            foreach (var data in urp.rendererDataList)
            {
                // 3D: public field. 2D (mobile-2d games): Renderer2DData keeps it internal, so read the serialized field
                bool missing = data is UniversalRendererData ur ? ur.postProcessData == null
                    : data is Renderer2DData && new SerializedObject(data).FindProperty("m_PostProcessData")?.objectReferenceValue == null;
                if (missing)
                    report.AppendLine($"Warning: renderer '{data.name}' on tier '{tier}' has no PostProcessData: no post-process pass.");
            }
        }

        // 3. Post-processing on every enabled camera, not only the one tagged MainCamera
        var cams = Object.FindObjectsByType<Camera>();
        if (cams.Length == 0)
            throw new System.Exception("No camera in the open scene(s).");
        var withPost = cams.Where(c => c.TryGetComponent<UniversalAdditionalCameraData>(out var d) && d.renderPostProcessing).ToArray();
        if (withPost.Length == 0)
            report.AppendLine("Warning: no camera has post-processing enabled. Enable via camData.renderPostProcessing = true.");

        // 4. + 5. Volumes: enabled, on a layer some post camera sees, with a profile that overrides something
        foreach (var vol in Object.FindObjectsByType<Volume>())
        {
            if (!vol.enabled) { report.AppendLine($"Warning: Volume '{vol.name}' is disabled."); continue; }
            int bit = 1 << vol.gameObject.layer;
            if (withPost.Length > 0 && !withPost.Any(c => (c.GetComponent<UniversalAdditionalCameraData>().volumeLayerMask & bit) != 0))
                report.AppendLine($"Warning: Volume '{vol.name}' on layer {vol.gameObject.layer} is in no post-processing camera's volumeLayerMask.");
            var profile = vol.sharedProfile;
            if (profile == null) { report.AppendLine($"Warning: Volume '{vol.name}' has no profile assigned."); continue; }
            if (!profile.components.Any(c => c.active && c.parameters.Any(p => p.overrideState)))
                report.AppendLine($"Warning: Volume '{vol.name}' profile has no active override with overrideState = true.");
        }

        // Return the findings: logs land in the Editor console, the returned value comes back to you
        return report.ToString().Contains("Warning") ? report.ToString() : report + "Post-processing setup looks correct.";
    }
}
```

## 1. Volume Setup

Effects are added as **VolumeComponent overrides** on a **VolumeProfile** (a `ScriptableObject`).

**Global Volume** (most common): GameObject with `Volume` component, `isGlobal = true`, `profile` assigned. Affects every camera whose `volumeLayerMask` includes the Volume's layer.

**Local Volume (optional, but takes precedence)**: GameObject with trigger `Collider` + `Volume` component, `isGlobal = false`. Properties:
- `priority` (float) — higher values override lower when volumes overlap.
- `blendDistance` (float) — outer distance in world units to start blending from (0 = no blend, instant transition at collider boundary).
- `weight` (float, 0–1) — scales the volume's overall influence.

**Stack order (URP 17).** The camera blends three layers, each overriding only the parameters it has
`overrideState = true` on: (1) the **Default Volume Profile** (Project Settings > Graphics > URP,
`URPDefaultVolumeProfileSettings`), then (2) the active URP asset's **Volume Profile** (Inspector > Volumes,
`UniversalRenderPipelineAsset.volumeProfile`), one per quality level, then (3) the scene's Volumes. A parameter a scene
Volume overrides hides the same parameter in (1) and (2), so a per-tier value lives in (2) and stays unchecked in the
scene profile. Both are `VolumeProfile` assets, so they also count for variant stripping (Key Facts).

## 2. Post-Processing Effects

All effects are `VolumeComponent` subclasses added as overrides on a `VolumeProfile` via `profile.Add<T>()`. Check existence with `profile.Has<T>()` or `profile.TryGet<T>(out var t)`. Remove with `profile.Remove<T>()`.

Every property is a `VolumeParameter`. You **must** set `overrideState = true` before setting `value`, otherwise the Volume system ignores it.

When configuring a specific effect, load the full API reference:
- [references/effect-reference.md](references/effect-reference.md) — All VolumeComponent properties by effect (Bloom, Tonemapping, ColorAdjustments, DepthOfField, Vignette, MotionBlur, FilmGrain, ChromaticAberration, SplitToning, ScreenSpaceLensFlare, LensDistortion, WhiteBalance, PaniniProjection, LiftGammaGain, ShadowsMidtonesHighlights, ColorCurves, ChannelMixer)

For code templates:
- [references/code-templates.md](references/code-templates.md) — Global Volume setup, camera post-processing, profile modification, and per-tier Volume Profiles on the URP assets

## 3. Anti-Hallucination Rules

### Required Usings

These apply to every `.cs` file, including the `script run` snippets. **A snippet passed to `eval`
cannot carry them** — qualify the types instead (see "If you use `script eval` instead" above).

```csharp
using UnityEngine.Rendering;           // Volume, VolumeProfile, VolumeComponent, VolumeParameter
using UnityEngine.Rendering.Universal;  // Bloom, Tonemapping, ColorAdjustments, UniversalRenderPipeline, etc.
```

### Wrong → Correct API Mapping

| WRONG | CORRECT |
|-------|---------|
| `PostProcessVolume` | `Volume` (from `UnityEngine.Rendering`) |
| `PostProcessLayer` | `UniversalAdditionalCameraData.renderPostProcessing` (bool) |
| `UnityEngine.Rendering.PostProcessing` | `UnityEngine.Rendering.Universal` |
| `profile.GetSetting<T>()` | `profile.TryGet<T>(out var t)` (returns bool) |
| `profile.AddSettings<T>()` | `profile.Add<T>()` (returns T; throws if already exists — check `profile.Has<T>()` first) |
| `volume.sharedProfile` (to modify at runtime) | `volume.profile` (auto-clones the asset into an instance) |
| `VolumeManager.instance.stack.GetComponent<T>()` (to edit an effect) | `volume.profile.TryGet<T>(out var t)` edits one profile. `stack.GetComponent<T>()` is the right call only to **read** the blended value the camera sees (all volumes, weights, blend distance); never write to it. |

### Key Facts
- **`overrideState = true`** is required on every `VolumeParameter` you set. The volume system skips parameters where `overrideState` is `false`. This is the #1 scripting mistake.
- **`sharedProfile`** = returns the asset directly (edits persist to disk). **`profile`** = auto-clones into an instance if needed (safe for runtime edits). Check with `volume.HasInstantiatedProfile()`.
- **`profile.Add<T>(bool overrides = false)`** — pass `true` to auto-enable `overrideState` on all parameters of the added component.
- **On a profile asset, `Add<T>()` is not enough to persist the override.** It only appends to the in-memory list; call `AssetDatabase.AddObjectToAsset(component, profile)` for each added component before saving, or the override is a missing reference after the next reload (see the Global Volume template).
- **`volume.profile = x` does not serialize.** Its setter fills a runtime-only field; an Editor-time assignment that must survive a scene save sets `volume.sharedProfile`.
- **Post-processing variants are stripped in this template.** ProjectSetup turns on Strip Unused Post Processing Variants (Project Settings > Graphics > URP) for every target on a new project's first run. URP then keeps an effect's variants only when some `VolumeProfile` asset under `Assets/` holds it **active with its saved values** (scenes are not scanned; URP 17.6 `ShaderBuildPreprocessor`). Active means the effect's own `IsActive()`: Bloom `intensity` > 0, Tonemapping `mode` not None, FilmGrain/MotionBlur/ChromaticAberration `intensity` > 0, LensDistortion, DepthOfField and PaniniProjection likewise; Bloom's high-quality and lens-dirt variants count separately (`highQualityFiltering`, `dirtTexture` plus `dirtIntensity` > 0). The Default Volume Profile counts too, but its components sit at their defaults (intensity 0, mode None), so it keeps nothing by itself. So an override added only from code at runtime (`profile.Add<T>()` on an instance), or one saved at intensity 0 and raised at runtime, needs a profile asset that holds it active, or the effect works in the Editor and is missing in the player.

## 4. Debugging Checklist

When post-processing isn't working, check in order:

1. `cam.TryGetComponent<UniversalAdditionalCameraData>(out var data)` succeeds and `data.renderPostProcessing` is `true`?
2. Volume exists in scene with a non-null `profile` (or `sharedProfile`) assigned?
3. Overrides added via `profile.Add<T>()` AND `overrideState = true` on each property you set?
4. Volume's `GameObject.layer` is included in camera's `data.volumeLayerMask`? (Default mask is layer 0 "Default" only.)
5. `volume.isGlobal = true` (for global), or camera is inside the Volume's trigger `Collider` (for local)?
6. In a camera stack, post-processing is enabled on the `CameraRenderType.Base` camera or the last `Overlay` (pre-flight check 3)? Other Overlay cameras composite onto the Base camera's output.
7. `supportsHDR` on the URP asset of the quality level you are looking at? Required for Tonemapping; in SDR, Bloom needs `threshold` < 1. In this template the Mobile tier is SDR on purpose (pre-flight check 2).
8. Viewing in **Game view**? Scene view has a separate post-processing toggle in its toolbar.
9. Works in the Editor but not in a build? The effect's variant was stripped: no `VolumeProfile` asset under `Assets/`, the Default Volume Profile included, holds that override active with its saved values (intensity 0 in every asset and raised at runtime counts as absent; Key Facts, "Post-processing variants are stripped").
10. An effect is on, or a value differs, with no scene Volume explaining it, or only on one tier? Look in the Default
    Volume Profile and the active URP asset's Volume Profile (Volume Setup, "Stack order"). A scene Volume that
    overrides the same parameter hides a per-tier value set there.

## 5. Common Recipes

Format: Effect property=value. Bloom values are threshold/intensity/scatter.

**Cinematic (Film):** Tonemapping mode=ACES, ColorAdjustments contrast=15 saturation=-10, Bloom threshold=0.9 intensity=0.5 scatter=0.7, Vignette intensity=0.3 smoothness=0.4, FilmGrain type=Medium1 intensity=0.2

**Stylized/Vibrant:** Tonemapping mode=Neutral, ColorAdjustments saturation=20 contrast=10, Bloom threshold=0.8 intensity=1.5 scatter=0.6, SplitToning highlights=warm shadows=cool

**Horror/Dark:** ColorAdjustments postExposure=-0.5 saturation=-30 contrast=20, Vignette intensity=0.5 smoothness=0.3 color=dark-red, FilmGrain type=Large01 intensity=0.4, ChromaticAberration intensity=0.15

**Clean/Mobile (an HDR mobile tier; this template's Mobile tier is SDR, use the next recipe):** Tonemapping mode=Neutral, ColorAdjustments postExposure=0.2, Bloom threshold=1.0 intensity=0.3 (subtle). Avoid FilmGrain, MotionBlur, DepthOfField on mobile.

**Clean/Mobile on this template's SDR Mobile tier:** the Tonemapping override is ignored without HDR, and a Bloom threshold of 1.0 never triggers there. Use ColorAdjustments postExposure=0.2, Bloom threshold=0.9 intensity=0.3 (subtle) with its cost knobs set for the frame budget (phones and WebGL): filter=Dual (faster than the default Gaussian at a small quality cost), downscale=Quarter, highQualityFiltering=false, maxIterations=4, and author the grade through ColorAdjustments rather than tonemapping. Avoid FilmGrain, MotionBlur, DepthOfField on mobile (`gamekit:unity-performance`).

**One profile, two tiers.** A single Global Volume serves both quality levels, so an HDR recipe (ACES or Neutral tonemapping, Bloom threshold at or above 1) looks different on the SDR Mobile tier: untonemapped, with less or no bloom. When the tiers need different values, do not lower the PC grade to fit Mobile: keep the shared grade (ColorAdjustments, Vignette, ...) on the scene Global Volume and put the tier-specific overrides on each URP asset's Volume Profile (Volume Setup, "Stack order"): `URP_PC.asset` carries Tonemapping and the HDR Bloom (threshold at or above 1), `URP_Mobile.asset` carries the SDR Bloom above (threshold < 1, cost knobs) and no Tonemapping (`references/code-templates.md`, "Per-tier Volume Profile on each URP asset"). Those parameters must be unchecked in the scene profile, or it hides them: the Create template turns on Bloom (`threshold`, `intensity`, `scatter`) and Tonemapping `mode` there, so when moving to two tiers remove both overrides from the scene profile (`TryGet` the component, `profile.Remove<T>()`, which only drops it from the list, then `AssetDatabase.RemoveObjectFromAsset(component)` and save), or uncheck every parameter a tier sets. With one shared profile only, keep Bloom `threshold` < 1 when Mobile must bloom. Either way, check the look at both levels (Edit > Project Settings > Quality) before reporting it done. Tier tuning itself is `gamekit:platform-targets`.

## 6. Final Confirmation

After setup, report to user:

```
Post-Processing Setup Complete
- Volume: [Global/Local] on "[GameObject Name]"
- Profile: [Asset Path]
- Effects: [List with key property=value pairs]
- Camera: [Name] — renderPostProcessing=true, volumeLayerMask includes layer [N]

- Tiers: Mobile HDR [on/off], PC HDR [on/off]; effects that do nothing on an SDR tier: [list or none]
- Saved: [profile asset path, scene] (committed with the change)

View results in Game view (not Scene view), at both quality levels.
Revert through git: the work was committed before the edit (project rule), and Edit > Undo
does not reliably cover edits made through the CLI.
```
