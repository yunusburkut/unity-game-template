# Feel v6.x feedback catalogue — what exists in __GAME__

About 200 feedback classes ship in `Assets/Feel`, grouped below by their
`[FeedbackPath("Category/Name")]` attribute, which is also how they appear in the "Add new
feedback" dropdown.

Availability marks:

- **OK** — compiles with the template's package manifest.
- **OFF** — compiled out by a version define, so the type does not exist. Referencing it is a
  compile error, and it will not appear in the dropdown.

Define state derives from `Packages/manifest.json` via the `versionDefines` in
`Assets/Feel/MoreMountains.Tools.asmdef` (path may differ per Feel version; find it with
`Glob **/MoreMountains.Tools.asmdef`). With the template's manifest — URP, uGUI 2.x, Input System,
the Physics2D module — these are **on:** `MM_URP`, `MM_UI`, `MM_UGUI2`, `MM_INPUTSYSTEM`,
`MM_PHYSICS2D`. **Off:** `MM_CINEMACHINE`, `MM_CINEMACHINE3`, `MM_POSTPROCESSING`, `MM_HDRP`,
`MM_VISUALEFFECTGRAPH`. Re-read the asmdef if a package was added or removed since.

`MOREMOUNTAINS_NICEVIBRATIONS_INSTALLED` is a **scripting define**, not a version define: Feel's
`NiceVibrationsDefineSymbols` adds it on Editor load, but only for the build target that is
active at that moment. See *Haptics* below — on a PC + mobile project it must exist for Android
and iOS too.

Source folders: `F/` = `Assets/Feel/MMFeedbacks/MMFeedbacks/Feedbacks/`, `S/` =
`.../MMFeedbacks/Springs/Feedbacks/`, `3P/<Vendor>` =
`Assets/Feel/MMFeedbacks/MMFeedbacksForThirdParty/<Vendor>/Feedbacks/`.

## Contents

- Animation — OK
- Audio — OK
- Camera — mixed
- Debug — OK
- Events — OK
- Feedbacks — OK
- GameObject — OK
- Haptics — needs the define per platform
- Lights — OK
- Loop — OK
- Particles — mixed
- Pause — OK
- PostProcess — mixed
- Renderer — OK
- Scene — OK
- Springs — OK
- TextMesh Pro — OK
- Time — OK
- Transform — OK
- UI — OK
- UI Toolkit — OK but off-stack
- Related non-feedback systems

---

## Animation — OK (5, F/)

`MMF_Animation` (animation parameter: trigger/bool/int/float) · `MMF_AnimationCrossfade` ·
`MMF_AnimatorPlayState` · `MMF_AnimatorSpeed` · `MMF_SpriteSheetAnimation`

## Audio — OK (19)

F/: `MMF_AudioSource` · `MMF_AudioSourcePitch` · `MMF_AudioSourceVolume` ·
`MMF_AudioSourceStereoPan` · `MMF_AudioFilterDistortion` · `MMF_AudioFilterEcho` ·
`MMF_AudioFilterHighPass` · `MMF_AudioFilterLowPass` · `MMF_AudioFilterReverb` ·
`MMF_AudioMixerSnapshotTransition`

3P/MMTools: `MMF_Sound` (instantiation modes event / cached / pooled / on demand — the
no-infrastructure starting point) · `MMF_Playlist` · `MMF_MMSoundManagerSound` ·
`MMF_MMSoundManagerAllSoundsControl` · `MMF_MMSoundManagerSoundControl` ·
`MMF_MMSoundManagerSoundFade` · `MMF_MMSoundManagerTrackControl` · `MMF_MMSoundManagerTrackFade` ·
`MMF_MMSoundManagerSaveLoad`

The MMSoundManager ones need the `MMSoundManager` singleton and a settings SO in the scene.
`MMF_MMSoundManagerSound` carries `MaximumConcurrentInstances`, the fix for machine-gun audio.

## Camera — mixed (12)

OK, F/: `MMF_CameraShake` · `MMF_CameraZoom` · `MMF_CameraClippingPlanes` ·
`MMF_CameraFieldOfView` · `MMF_CameraOrthographicSize` · `MMF_Flash`
OK, 3P/MMTools: `MMF_Fade`

**OFF, 3P/Cinemachine:** `MMF_CinemachineImpulse` · `MMF_CinemachineImpulseClear` ·
`MMF_CinemachineImpulseSource` · `MMF_CinemachineTransition` · `MMF_CinemachineCameraDutch`

Cinemachine is not installed. Most Feel tutorials and the official landing-impact recipe use
Cinemachine Impulse — translate those to `MMF_CameraShake` plus an `MMCameraShaker` on the camera
rig. `MMF_CameraShake` and `MMF_CameraZoom` are event-based and need their shaker in the scene;
`MMF_CameraFieldOfView` and `MMF_CameraOrthographicSize` target a camera directly. If a script
moves the camera every frame (a follow camera), put the shaker on a **child** of the moved node, or
the follow overwrites the shake.

## Debug — OK (3, 3P/MMTools)

`MMF_DebugBreak` · `MMF_DebugComment` (inspector notes, free at runtime — use them to document long
lists) · `MMF_DebugLog`

## Events — OK (3)

F/: `MMF_Events` (UnityEvents) · 3P/MMTools: `MMF_MMGameEvent` · `MMF_RandomEvents` (weighted)

## Feedbacks — OK (4, F/)

`MMF_Feedbacks` (play other MMF_Players, by reference or within range) · `MMF_PlayerChain` ·
`MMF_PlayerControl` · `MMF_ReferenceHolder`

## GameObject — OK (13)

F/: `MMF_Collider` · `MMF_Collider2D` · `MMF_Destroy` · `MMF_Enable` · `MMF_InstantiateObject` (has
a pooling option — use it) · `MMF_Rigidbody` · `MMF_Rigidbody2D` · `MMF_SetActive`
3P/MMTools: `MMF_Broadcast` · `MMF_FloatController` · `MMF_Layer` · `MMF_RadioSignal` ·
`MMF_Property` (drive any field or property on any component over time)

The 2D ones need `MM_PHYSICS2D` (on while the Physics2D module is in the manifest).

A `MMF_Destroy` targeting the `MMF_Player`'s own GameObject kills the sequence. Put it last, and put
the `MMF_Player` on a surviving object.

## Haptics — needs the define per platform (6, 3P/NiceVibrations)

`MMF_NVClip` · `MMF_NVContinuous` · `MMF_NVControl` · `MMF_NVEmphasis` · `MMF_NVPreset` ·
`MMF_Haptics` (**deprecated**, do not use)

Gated by `MOREMOUNTAINS_NICEVIBRATIONS_INSTALLED`. Feel writes it only for the build target active
when the Editor loads, so a project that opened on Standalone has it for Standalone alone: the
`MMF_NV*` types then do not exist on Android or iOS, and an `MMF_Player` holding them **loses those
entries when it is serialized from the mobile target**. Before authoring the first haptic feedback,
check *Player Settings > Other Settings > Scripting Define Symbols* for Android and iOS and add the
symbol where it is missing (ask the user; it is a project setting).

On PC, Nice Vibrations drives gamepad rumble only; with no gamepad in scope the feedbacks do
nothing there, which is fine — no `#if` needed. Code-driven haptics (`HapticPatterns`) compile
without the define; see the recipes file, *Mobile haptics service*.

## Lights — OK (2)

F/: `MMF_Light` · 3P/URP: `MMF_Light2D_URP`

## Loop — OK (2, F/)

`MMF_Looper` · `MMF_LooperStart` (both derive from `MMF_Pause`)

## Particles — mixed (4)

OK, F/: `MMF_Particles` (play/pause/stop/resume an existing system) · `MMF_ParticlesInstantiation`
(on-demand or pooled)
**OFF, 3P/VisualEffectGraph:** `MMF_VisualEffect` · `MMF_VisualEffectSetProperty`

Keep ParticleSystem prefabs under `Assets/__GAME__/Game/Prefabs/FX/` and reuse them; particles are
the first thing to cut on the Mobile tier.

## Pause — OK (2, F/)

`MMF_Pause` · `MMF_HoldingPause`

## PostProcess — mixed (32)

**OK, 3P/URP (12):** `MMF_Bloom_URP` · `MMF_ChannelMixer_URP` · `MMF_ChromaticAberration_URP` ·
`MMF_ColorAdjustments_URP` · `MMF_DepthOfField_URP` · `MMF_FilmGrain_URP` · `MMF_LensDistortion_URP` ·
`MMF_MotionBlur_URP` · `MMF_PaniniProjection_URP` · `MMF_Vignette_URP` · `MMF_WhiteBalance_URP` ·
`MMF_GlobalPPVolumeAutoBlend_URP`

**OFF:** all seven PPv2 feedbacks (`MMF_Bloom`, `MMF_Vignette`, `MMF_ChromaticAberration`,
`MMF_ColorGrading`, `MMF_DepthOfField`, `MMF_LensDistortion`, `MMF_GlobalPPVolumeAutoBlend`) and all
twelve HDRP ones. `MMF_PPMovingFilter` (3P/MMTools) also targets PPv2.

Each URP feedback needs its matching `MM*Shaker_URP` component on the Volume GameObject of every
scene that plays it, **and** the matching override in that scene's Volume profile — a shaker for an
override the profile does not have does nothing. On the Mobile tier, prefer Vignette, Color
Adjustments and Bloom; depth of field, motion blur and lens effects are full-screen passes a phone
should not pay for (`urp-postprocessing`, `unity-performance`).

## Renderer — OK (15)

F/: `MMF_Flicker` · `MMF_Material` · `MMF_MaterialSetProperty` · `MMF_ShaderGlobal` · `MMF_Skybox` ·
`MMF_Sprite` · `MMF_SpriteRenderer` · `MMF_SpriteRendererAlpha` · `MMF_TextureOffset` ·
`MMF_TextureScale`
3P/MMTools: `MMF_Blink` (path "Renderer/MMBlink") · `MMF_Fog` · `MMF_LineRenderer` ·
`MMF_ShaderController` · `MMF_TrailRenderer`

`MMF_Flicker`, `MMF_MaterialSetProperty` and `MMF_Blink` are the useful ones for a hit flash in 3D;
the sprite feedbacks for a 2D game. `MMF_Flicker` has a `UseMaterialPropertyBlocks` option — prefer
it to avoid material instancing.

## Scene — OK (2)

F/: `MMF_UnloadScene` · 3P/MMTools: `MMF_LoadScene`

## Springs — OK (5, S/)

`MMF_SpringFloat` · `MMF_SpringVector2` · `MMF_SpringVector3` · `MMF_SpringVector4` ·
`MMF_SpringColor`

Plus the four Transform spring feedbacks listed under Transform. Spring *components* (31 in
`.../Springs/Springs/`, 14 URP post-process springs) are separate MonoBehaviours.

## TextMesh Pro — OK (15, 3P/TextMeshPro)

`MMF_TMPAlpha`, `MMF_TMPCharacterSpacing`, `MMF_TMPColor`, `MMF_TMPCountTo`, `MMF_TMPCountToLong`,
`MMF_TMPDilate`, `MMF_TMPFontSize`, `MMF_TMPLineSpacing`, `MMF_TMPOutlineColor`,
`MMF_TMPOutlineWidth`, `MMF_TMPParagraphSpacing`, `MMF_TMPSoftness`, `MMF_TMPText`,
`MMF_TMPTextReveal`, `MMF_TMPWordSpacing`

They guard on `MM_UGUI2` (uGUI 2.x carries TMP). They need TMP text in the scene to target: if the
UI uses `UnityEngine.UI.Text`, use the uGUI text feedbacks under UI instead, and use the plain
`MMFloatingText` prefab rather than `MMFloatingTextMeshPro`.

## Time — OK (2, F/)

`MMF_FreezeFrame` · `MMF_TimescaleModifier`

Both require an `MMTimeManager` in the scene and do nothing without one. A freeze makes any input
timer on scaled time swallow presses; run input timers unscaled.

## Transform — OK (16, F/)

`MMF_Position` (AtoB / AlongCurve / ToDestination) · `MMF_PositionShake` · `MMF_PositionSpring` ·
`MMF_Rotation` · `MMF_RotationShake` · `MMF_RotationSpring` · `MMF_RotatePositionAround` ·
`MMF_Scale` · `MMF_ScaleShake` · `MMF_ScaleSpring` · `MMF_SquashAndStretch` (mass conserving) ·
`MMF_SquashAndStretchSpring` · `MMF_DestinationTransform` · `MMF_LookAt` · `MMF_SetParent` ·
`MMF_Wiggle`

The core of most juice lives here. Point these at a **visual child** of the object, never at the
root a controller writes every frame — a feedback scaling or moving that root fights the controller
(one writer per transform node, `refactor-pass` / `unity-architecture`).

## UI — OK (21)

F/: `MMF_Image` · `MMF_ImageMaterial` · `MMF_ImageRaycastTarget` · `MMF_ImageSprite` ·
`MMF_ImageTextureOffset` · `MMF_ImageTextureScale` · `MMF_Graphic` · `MMF_GraphicCrossFade` ·
`MMF_CanvasGroupBlocksRaycasts` · `MMF_Text` · `MMF_TextColor` · `MMF_VideoPlayer`
3P/MMTools: `MMF_CanvasGroup` · `MMF_FloatingText` · `MMF_ImageAlpha` · `MMF_ImageFill` ·
`MMF_RectTransformAnchor` · `MMF_RectTransformOffset` · `MMF_RectTransformPivot` ·
`MMF_RectTransformSizeDelta` · `MMF_TextFontSize`

`MMF_Text` / `MMF_TextColor` / `MMF_TextFontSize` target `UnityEngine.UI.Text`. `MMF_FloatingText`
needs an `MMFloatingTextSpawner` in the scene.

UI feedbacks almost always want `TimescaleMode = Unscaled` so they keep running during a freeze
frame or a paused game.

## UI Toolkit — OK but off-stack (17, 3P/UIToolkit)

`MMF_UIToolkitBackgroundColor`, `…BorderColor`, `…BorderRadius`, `…BorderWidth`, `…Class`,
`…FontSize`, `…ImageTint`, `…Opacity`, `…Rotate`, `…Scale`, `…Size`, `…Stylesheet`, `…Text`,
`…TextColor`, `…TransformOrigin`, `…Translate`, `…Visible`

The template's UI is uGUI. Ignore these unless the UI stack changes.

---

## Related non-feedback systems

Shakers (`Assets/Feel/MMFeedbacks/MMFeedbacks/Shakers/`) · Springs (core + components +
post-process springs) · `MMFloatingText` / `MMFloatingTextSpawner` · `MMSequencer` / `MMSequence` ·
`MMTimeManager` · `MMSoundManager` (+ playlists, audio analyzer) · `MMRadioBroadcaster` /
`MMRadioReceiver` / `MMRadioSignalGenerator` · `MMObjectPooler` / `MMSimpleObjectPooler` /
`MMMultipleObjectPooler` · `MMProgressBar` · `MMHealthBar` · `MMFollowTarget` · `MMAutoRotate` ·
`MMSquashAndStretch` · `MMBlink` · `MMWiggle` · `MMTween` · `MMEventManager` / `MMGameEvent` ·
`MMSaveLoad` · `MMSceneLoading` · `MMDebugMenu`.

Many MMTools subsystems duplicate something a project either already has or deliberately refuses
(a save system, a scene loader, an event bus, a pooler). CLAUDE.md's "ask before adding a framework"
applies to adopting an MMTools subsystem just as much as to a package.
