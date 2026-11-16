# Animation in Unity: Animator controllers driven by Core state

Loaded from `unity-editor-cli` when a character or object needs Animator states ("make it run, jump and land", the
Blender rig's clips in Unity, a 2D sprite animation). Clip export and import (names, loop flags, Humanoid or Generic)
are `unity-export`'s contract and checklist; in a toon-art game, `art-pipeline` builds the model and its clips. This
file starts where the clips exist as imported sub-assets.

Use an Animator for characters and rigs with several states. A one-off pop, slide or squash is a tween or a Feel
feedback (`feel-authoring`), not a controller; never put an Animator on uGUI elements (it writes its properties every
frame and so rebuilds the canvas every frame, `ui-ugui`).

## The controller is built, never hand-edited

`.controller` and `.anim` are Unity YAML: the hook refuses a hand edit while the Editor is open, and the Animator
window is the user's tool, not the agent's. An Editor builder in the game's Editor folder
(`Assets/__GAME__/Editor/<System>/<Name>AnimatorBuilder.cs`, or inside the art builder in a toon-art game) creates or
rebuilds the controller from a list: one state per clip in `animation-contract.json`, and the parameters and
transitions the gameplay needs, written in the builder. Rebuild it after any change to the list; edit the builder, never
the asset. Rebuild **in place** (load the existing asset, remove its states and parameters, add them again), so its
GUID and every prefab's reference to it survive:

```csharp
using System.Linq;
using UnityEditor;
using UnityEditor.Animations;
using UnityEngine;

public static class PlayerAnimatorBuilder
{
    const string Fbx = "Assets/__GAME__/Art/Player/Player.fbx";
    const string Path = "Assets/__GAME__/Game/Player/Player.controller";

    [MenuItem("__GAME__/Build/Player Animator")]
    public static void Build()
    {
        var clips = AssetDatabase.LoadAllAssetsAtPath(Fbx).OfType<AnimationClip>()
            .Where(c => !c.name.StartsWith("__preview__")).ToDictionary(c => c.name);
        var ctrl = AssetDatabase.LoadAssetAtPath<AnimatorController>(Path)
                   ?? AnimatorController.CreateAnimatorControllerAtPath(Path);
        var sm = ctrl.layers[0].stateMachine;
        foreach (var t in sm.anyStateTransitions) sm.RemoveAnyStateTransition(t);
        foreach (var s in sm.states) sm.RemoveState(s.state);
        foreach (var p in ctrl.parameters) ctrl.RemoveParameter(p);
        foreach (var bt in AssetDatabase.LoadAllAssetsAtPath(Path).OfType<BlendTree>())   // RemoveState leaves these
            AssetDatabase.RemoveObjectFromAsset(bt);

        ctrl.AddParameter("Speed", AnimatorControllerParameterType.Float);
        ctrl.AddParameter("Grounded", AnimatorControllerParameterType.Bool);
        ctrl.AddParameter("Land", AnimatorControllerParameterType.Trigger);

        var move = ctrl.CreateBlendTreeInController("Move", out var tree);   // Idle..Run by Speed
        tree.blendParameter = "Speed";
        tree.AddChild(clips["Idle"], 0f); tree.AddChild(clips["Run"], 1f);
        var fall = sm.AddState("Fall"); fall.motion = clips["Fall"];
        var land = sm.AddState("Land"); land.motion = clips["Land"];
        sm.defaultState = move;

        Link(move, fall, t => t.AddCondition(AnimatorConditionMode.IfNot, 0, "Grounded"));
        var toLand = sm.AddAnyStateTransition(land);                      // the edge: any state, always consumed
        toLand.AddCondition(AnimatorConditionMode.If, 0, "Land");
        toLand.hasExitTime = false; toLand.duration = 0.05f; toLand.canTransitionToSelf = false;
        var back = land.AddTransition(move); back.hasExitTime = true; back.exitTime = 1f; back.duration = 0.1f;

        EditorUtility.SetDirty(ctrl); AssetDatabase.SaveAssetIfDirty(ctrl);
    }

    static void Link(AnimatorState from, AnimatorState to, System.Action<AnimatorStateTransition> cond)
    {
        var t = from.AddTransition(to); t.hasExitTime = false; t.duration = 0.1f; cond(t);
    }
}
```

The names, clips and durations are an example; the feel of the timings is `game-feel`'s call. Gameplay-driven
transitions have `hasExitTime = false`, or the state waits for its clip to end before reacting. Character variants
with the same states share the controller through an `AnimatorOverrideController` (built the same way), not a copied
controller.

Run the builder from the agent with a `script run` file whose single method calls `PlayerAnimatorBuilder.Build()`
(check with `--dry_run` first; if the ephemeral assembly cannot resolve the game's Editor types, give the builder a
`[CliCommand]` instead, `unity-cli`'s integration-advanced.md). The user can run the same menu item. Commit the
builder and the asset it writes together.

## Driving it from Core

Core never touches the Animator (`unity-architecture`: Core stays free of presentation). The system's view
(`<System>View`) maps the solver's `State` to parameters in the method the controller calls right after `Step`, in
the same `Update` (the rule for edge flags in `unity-architecture`'s cross-system section). The Animator evaluates
after `Update`, so parameters set there apply in the same frame:

```csharp
static readonly int SpeedId = Animator.StringToHash("Speed");
static readonly int GroundedId = Animator.StringToHash("Grounded");
static readonly int LandId = Animator.StringToHash("Land");

public void Show(in PlayerState s)
{
    animator.SetFloat(SpeedId, Mathf.Abs(s.Velocity.x) / tuning.MaxSpeed);
    animator.SetBool(GroundedId, s.Grounded);
    if (s.Landed) animator.SetTrigger(LandId);
}
```

- Continuous state (speed, grounded, carrying) is a float or bool set every frame; a one-step edge flag (`Landed`,
  `Hit`) is a trigger. A trigger stays armed until a transition consumes it, so give every trigger a transition that
  always takes it (from Any State, as above), or it fires late in some later state.
- Hash parameter names once (`static readonly int`); the string overloads hash on every call
  (`refactor-pass`'s caching-and-hot-paths.md). Keep the names identical in builder and view; a rename changes both.
- **Root motion off when Core owns movement**: `animator.applyRootMotion = false` on the prefab. A clip that travels
  would otherwise move the transform against the solver. Author locomotion clips in place in Blender; if one arrives
  with root travel, bake it into the pose in the importer rather than turning root motion on.
- Update mode `Normal` follows `Time.timeScale`, so the game's pause (time scale 0, `dt` 0) freezes it with the
  solver; only a pause-menu animation uses `UnscaledTime`. Use `AnimatePhysics` only for a solver stepped in
  `FixedUpdate`.
- Culling on mobile: `AnimatorCullingMode.CullUpdateTransforms` for characters that leave the screen (the state machine
  keeps running, so it comes back in the right state; only the pose writes stop). `CullCompletely` also stops the state
  machine and is only for background crowds whose state does not matter.

## 2D

- **Frame-by-frame sprites** are an Animator with sprite-keyframe clips. Aseprite files (the mobile-2d pack's
  Aseprite Importer) generate a clip per tag on import; use those as the states' motions. A clip from a sprite sheet is
  built in the same Editor builder with
  `AnimationUtility.SetObjectReferenceCurve(clip, EditorCurveBinding.PPtrCurve("", typeof(SpriteRenderer), "m_Sprite"), keys)`
  (`ObjectReferenceKeyframe[]`, one per frame), saved with `AssetDatabase.CreateAsset` once and updated in place after.
- **Skeletal 2D** (2D Animation, installed by mobile-2d) uses a `SpriteSkin` on each rigged sprite, from a layered PSB
  through the PSD Importer or bones made in the Sprite Editor's Skinning Editor. Rigging and weight painting are the
  user's hand work in that editor; the agent builds the controller and drives it exactly as above.
- Flip a 2D character by `SpriteRenderer.flipX` (or a scale of -1 on the root for a rig) from the view, not with
  mirrored clips.

## Checking it

The controller is data: an EditMode test can load it and assert one state per contract clip and the parameters the
view sets (`unity-testing`). How it looks and reads in motion is the user's Play Mode check; `play-capture` only shows
the first frames.
