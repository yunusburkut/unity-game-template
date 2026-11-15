## Code Templates

Each template is a C# file to run through `script run` (SKILL.md section 0, `gamekit:unity-editor-cli`): save it in
the scratchpad directory, outside `Assets/`, and run
`unity command script run --file <absolute .cs path> --timeout 60`. Hard stops `throw`, so the run fails loudly;
anything the caller needs to read is `return`ed. Because `script run` compiles a real file, these keep their `using`
directives. Only if you pass one to `script eval` instead do you strip the usings and fully qualify every type
(SKILL.md, "If you use `script eval` instead").

**Before and after (house rules, `project/CLAUDE.md` and `gamekit:pipeline` phase 4):**

- **Commit first.** `/rewind` cannot undo what the Editor wrote, and Edit > Undo does not reliably cover CLI edits
  (see "Undo and reverting" below), so git is the way back.
- **Save only what you changed, then commit it with the change.** An asset (the Volume Profile): call
  `AssetDatabase.SaveAssetIfDirty(asset)` in the same `script run`. The active scene: run `unity command scene save`
  afterwards. Never `editor save_all`: it also saves the user's other scenes.
- **A scene that was already dirty before your edit holds the user's unsaved work: ask first.** The scene templates
  below check `scene.isDirty` before touching anything and stop if it is set, so the save afterwards writes only
  your change.

### Creating a Global Volume with Effects

The profile goes into the game's own Settings folder, `Assets/<Game>/Settings`, next to the URP assets (there is no
`Assets/Settings` in games made from this template). The bloom threshold is below 1 so it also triggers on the
Mobile tier, which is SDR on purpose; the tonemapping override applies on the HDR tier only (SKILL.md pre-flight
check 2).

```csharp
using System.IO;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

public static class CreateGlobalVolume
{
    public static string Run()
    {
        var urpAsset = UniversalRenderPipeline.asset;
        if (urpAsset == null) throw new System.Exception("No UniversalRenderPipelineAsset active.");

        var scene = EditorSceneManager.GetActiveScene();
        if (scene.isDirty) throw new System.Exception($"Scene '{scene.name}' already has unsaved changes: ask the user first.");

        // The game's Settings folder is where its URP assets live (Assets/<Game>/Settings)
        var settingsFolder = Path.GetDirectoryName(AssetDatabase.GetAssetPath(urpAsset)).Replace('\\', '/');
        var assetPath = AssetDatabase.GenerateUniqueAssetPath(settingsFolder + "/PostProcessProfile.asset");
        var profile = ScriptableObject.CreateInstance<VolumeProfile>();
        AssetDatabase.CreateAsset(profile, assetPath);

        // MUST set overrideState = true on each property
        var bloom = profile.Add<Bloom>();
        bloom.threshold.overrideState = true;
        bloom.threshold.value = 0.9f;   // < 1: also blooms on the SDR Mobile tier
        bloom.intensity.overrideState = true;
        bloom.intensity.value = 1f;
        bloom.scatter.overrideState = true;
        bloom.scatter.value = 0.7f;

        var tonemapping = profile.Add<Tonemapping>();   // HDR tiers only; ignored on the SDR Mobile tier
        tonemapping.mode.overrideState = true;
        tonemapping.mode.value = TonemappingMode.ACES;

        var volumeObj = new GameObject("Global Volume");
        var volume = volumeObj.AddComponent<Volume>();
        volume.isGlobal = true;
        volume.sharedProfile = profile;   // the asset itself; `profile` would clone it into an instance

        // profile.Add<T>() only adds the component to the in-memory list (VolumeProfile.cs); it is not a
        // sub-asset yet, so after a reload the override is a missing reference. Store each one in the asset,
        // as the Volume Profile inspector does.
        foreach (var component in profile.components)
            if (!AssetDatabase.Contains(component)) AssetDatabase.AddObjectToAsset(component, profile);
        EditorUtility.SetDirty(profile);
        AssetDatabase.SaveAssetIfDirty(profile);
        EditorSceneManager.MarkSceneDirty(scene);

        return $"Created Global Volume with Bloom and ACES Tonemapping; profile saved at {assetPath}. "
             + $"Scene '{scene.name}' is modified: run `unity command scene save`, then commit both.";
    }
}
```

### Enabling Post-Processing on Camera

`Camera.main` needs the `MainCamera` tag; the template finds the camera by that tag, so name the camera you mean if
the scene has several.

```csharp
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering.Universal;

public static class EnableCameraPostFx
{
    public static string Run()
    {
        var cam = Camera.main;
        if (cam == null) throw new System.Exception("No camera tagged MainCamera found.");
        if (!cam.TryGetComponent<UniversalAdditionalCameraData>(out var data))
            throw new System.Exception("Missing UniversalAdditionalCameraData. Is URP active?");

        var scene = data.gameObject.scene;
        if (scene.isDirty) throw new System.Exception($"Scene '{scene.name}' already has unsaved changes: ask the user first.");

        data.renderPostProcessing = true;
        EditorUtility.SetDirty(data);

        // This edits a component, which lives in the scene rather than in an asset, so
        // AssetDatabase.SaveAssets() does not persist it. SetDirty only marks; nothing is written until
        // the scene is saved. If the session ends without a scene save, the edit is gone.
        EditorSceneManager.MarkSceneDirty(scene);
        return $"Post-processing enabled on '{cam.name}'. Scene '{scene.name}' is modified: "
             + "run `unity command scene save`, then commit it.";
    }
}
```

### Modifying an Existing Volume Profile

**Use `sharedProfile`, not `profile`.** `profile` auto-clones the asset into a runtime instance, so
`SetDirty` on it marks a clone that is not an asset at all and the edit can never reach disk. Merely
reading `volume.profile` is enough to trigger the clone, so the null check has to use `sharedProfile`
too. `sharedProfile` returns the asset itself, which is what an Editor-time edit needs.

```csharp
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

public static class EditVolumeProfile
{
    public static string Run()
    {
        var volumeObj = GameObject.Find("Global Volume");
        if (volumeObj == null || !volumeObj.TryGetComponent<Volume>(out var volume) || volume.sharedProfile == null)
            throw new System.Exception("No 'Global Volume' with a profile asset in the open scene(s).");

        var profile = volume.sharedProfile;
        if (!profile.TryGet<Bloom>(out var bloom))
            throw new System.Exception($"Profile '{profile.name}' has no Bloom override.");
        bloom.intensity.overrideState = true;
        bloom.intensity.value = 2f;

        EditorUtility.SetDirty(profile);
        // SetDirty only marks the asset. Without this the edit is in memory only: it reads back
        // correctly for the rest of the session and is lost when the session ends.
        AssetDatabase.SaveAssetIfDirty(profile);
        return $"Bloom intensity set to 2 on {AssetDatabase.GetAssetPath(profile)} (saved; commit it).";
    }
}
```

### Undo and reverting

`Undo.RecordObject` alone does **not** produce an undo entry when the code runs through the Editor's command server
(measured with `eval`: nothing appeared on the undo stack). `RecordObject` takes a *deferred* snapshot that Unity
flushes at the end of an Editor event, and a snippet executed by the Pipeline server is outside that loop. That is
why these templates carry no Undo calls and why the way back is git: commit before the edit, then
`git restore` / `git revert` the profile and scene files after it.

`Undo.RecordObject` (and `Undo.RegisterCreatedObjectUndo` for a new object) still belongs in code the user runs
interactively from a menu item or an editor window, where the event loop flushes it.

If the user does ask for an Edit > Undo entry from a CLI run, the explicit group + immediate-snapshot + flush sequence
does not rely on the event loop (it is not a substitute for the commit):

```csharp
Undo.IncrementCurrentGroup();
Undo.SetCurrentGroupName("Set up post-processing");     // the label the user will see
var group = Undo.GetCurrentGroup();

Undo.RegisterCompleteObjectUndo(target, "Set up post-processing");   // immediate, not deferred
// ... make the modification, and for a newly created object:
// Undo.RegisterCreatedObjectUndo(newObject, "Set up post-processing");
EditorUtility.SetDirty(target);
// ... then save as in "Before and after" above
Undo.FlushUndoRecordObjects();         // force the snapshot out now
Undo.CollapseUndoOperations(group);    // one entry, not several

return Undo.GetCurrentGroupName();     // report the label back to confirm it landed
```

The returned group name tells you the group exists; only the user can confirm the entry is on the stack
(`Edit > Undo <label>` should read your label). Do not promise Ctrl+Z on that basis alone.
