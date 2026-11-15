---
name: urp-postprocessing
description: Sets up, configures, and debugs URP post-processing effects using the Volume framework. Use when the user asks about bloom, tonemapping, color adjustments, depth of field, vignette, motion blur, or other Volume overrides in a URP project.
required_packages:
  com.unity.render-pipelines.universal: ">=14.0.0"
---

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
3. **Camera has post-processing enabled** — `renderPostProcessing` must be `true` (defaults to `false`). Camera Stacking: only a `CameraRenderType.Base` camera (or the last `Overlay` in the stack) should enable post-processing. Also verify the Renderer's PostProcessData asset is not null — if it is, the post-process pass won't exist.
4. **The Volume's GameObject layer is in the Camera's Volume Layer Mask** — `volumeLayerMask` defaults to layer 0 "Default" only. The Volume's `GameObject.layer` must be included, otherwise the camera ignores it.
5. **Volume exists with `enabled = true`, a valid Profile, and at least one override** — The `Volume` component must be enabled, have a non-null `profile` (or `sharedProfile`), and at least one active `VolumeComponent` with `overrideState = true` on its properties.

### Pre-Flight Check Snippet

Run this with `script run` to verify the setup programmatically:

```csharp
using System.Linq;
using System.Text;
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
                if (data is UniversalRendererData ur && ur.postProcessData == null)
                    report.AppendLine($"Warning: renderer '{ur.name}' on tier '{tier}' has no PostProcessData: no post-process pass.");
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

## 2. Post-Processing Effects

All effects are `VolumeComponent` subclasses added as overrides on a `VolumeProfile` via `profile.Add<T>()`. Check existence with `profile.Has<T>()` or `profile.TryGet<T>(out var t)`. Remove with `profile.Remove<T>()`.

Every property is a `VolumeParameter`. You **must** set `overrideState = true` before setting `value`, otherwise the Volume system ignores it.

When configuring a specific effect, load the full API reference:
- [references/effect-reference.md](references/effect-reference.md) — All VolumeComponent properties by effect (Bloom, Tonemapping, ColorAdjustments, DepthOfField, Vignette, MotionBlur, FilmGrain, ChromaticAberration, SplitToning, LensDistortion, WhiteBalance, PaniniProjection, LiftGammaGain, ShadowsMidtonesHighlights, ColorCurves, ChannelMixer)

For code templates:
- [references/code-templates.md](references/code-templates.md) — Global Volume setup, camera post-processing, and profile modification templates

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
- **Post-processing variants are stripped in this template.** ProjectSetup turns on Strip Unused Post Processing Variants (Project Settings > Graphics > URP) for every target on a new project's first run. URP then keeps only the effects some `VolumeProfile` asset in the project uses (scenes are not scanned), so an override added only from code at runtime (`profile.Add<T>()` on an instance) needs a profile asset that contains it, or the effect works in the Editor and is missing in the player.

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
9. Works in the Editor but not in a build? The effect's variant was stripped: no `VolumeProfile` asset in the project contains that override (Key Facts, "Post-processing variants are stripped").

## 5. Common Recipes

Format: Effect property=value. Bloom values are threshold/intensity/scatter.

**Cinematic (Film):** Tonemapping mode=ACES, ColorAdjustments contrast=15 saturation=-10, Bloom threshold=0.9 intensity=0.5 scatter=0.7, Vignette intensity=0.3 smoothness=0.4, FilmGrain type=Medium1 intensity=0.2

**Stylized/Vibrant:** Tonemapping mode=Neutral, ColorAdjustments saturation=20 contrast=10, Bloom threshold=0.8 intensity=1.5 scatter=0.6, SplitToning highlights=warm shadows=cool

**Horror/Dark:** ColorAdjustments postExposure=-0.5 saturation=-30 contrast=20, Vignette intensity=0.5 smoothness=0.3 color=dark-red, FilmGrain type=Large01 intensity=0.4, ChromaticAberration intensity=0.15

**Clean/Mobile:** Tonemapping mode=Neutral, ColorAdjustments postExposure=0.2, Bloom threshold=1.0 intensity=0.3 (subtle). Avoid FilmGrain, MotionBlur, DepthOfField on mobile.

**Clean/Mobile on this template's SDR Mobile tier:** the Tonemapping override is ignored without HDR, and a Bloom threshold of 1.0 never triggers there. Use ColorAdjustments postExposure=0.2, Bloom threshold=0.9 intensity=0.3 (subtle), and author the grade through ColorAdjustments rather than tonemapping. Avoid FilmGrain, MotionBlur, DepthOfField on mobile (`gamekit:unity-performance`).

**One profile, two tiers.** A single Global Volume serves both quality levels, so an HDR recipe (ACES or Neutral tonemapping, Bloom threshold at or above 1) looks different on the SDR Mobile tier: untonemapped, with less or no bloom. Keep Bloom `threshold` < 1 when Mobile must bloom, and check the look at both levels (Edit > Project Settings > Quality) before reporting it done. Tier tuning itself is `gamekit:platform-targets`.

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
