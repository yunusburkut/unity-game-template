# Feel v6.1 — code-facing API

Verified against the copy at `Assets/Feel` (v6.1, `Assets/Feel/readme.txt`), cross-checked with
https://feel-docs.moremountains.com/ and the Doxygen API at http://feel-docs.moremountains.com/API/.

Namespaces: `MoreMountains.Feedbacks` (player, feedbacks, shakers, springs, floating text,
MMTimeManager, MMWiggle), `MoreMountains.Tools` (MMSoundManager, MMRadio, poolers),
`MoreMountains.FeedbacksForThirdParty` (URP post-process shakers and springs, MMCameraZoom). All of them compile
into the **`MoreMountains.Tools`** assembly in this project.

## Contents

- §1 Architecture
- §2 Playing from code
- §3 MMF_Player settings
- §4 MMF_Feedback — shared fields
- §5 Verified defaults worth knowing
- §6 Shakers and events
- §7 Springs
- §8 MMSoundManager
- §9 Writing a custom feedback

---

## 1. Architecture

`MMF_Player : MMFeedbacks` is a single component holding
`[SerializeReference] public List<MMF_Feedback> FeedbacksList`. Each `MMF_Feedback` is a plain
`[Serializable]` C# class — not a MonoBehaviour, not a ScriptableObject. That is why one player with
twenty feedbacks costs one component.

Legacy `MMFeedbacks` / `MMFeedback` (MonoBehaviour-per-effect) still exist as base classes at
`Assets/Feel/MMFeedbacks/MMFeedbacks/Core/Legacy/` for back-compat. **Do not author against them.**
Old tutorial code using `GetComponent<MMFeedbacks>()` or `MMFeedbackScale` needs porting to
`MMF_Player` / `MMF_Scale`.

Key paths:

- `Assets/Feel/MMFeedbacks/MMFeedbacks/Core/MMF_Player/MMF_Player.cs`
- `Assets/Feel/MMFeedbacks/MMFeedbacks/Core/MMF_Player/MMF_Feedback.cs`
- `Assets/Feel/MMFeedbacks/MMFeedbacks/Core/MMFeedbackTiming.cs`
- `Assets/Feel/MMFeedbacks/MMFeedbacks/Core/MMShaker.cs`
- `Assets/Feel/MMFeedbacks/MMFeedbacks/Core/MMChannels/MMChannel.cs`
- `Assets/Feel/MMTools/Core/MMTimeManager/MMTimeManager.cs`
- `Assets/Feel/MMTools/Core/MMAudio/MMSoundManager/`

---

## 2. Playing from code

```csharp
using MoreMountains.Feedbacks;

[SerializeField] private MMF_Player landFeedback;   // wired in the Inspector, never Found

landFeedback.PlayFeedbacks();
landFeedback.PlayFeedbacks(transform.position, intensity);   // intensity scales every feedback
landFeedback.PlayFeedbacks(position, intensity, forceChangeDirection: false);
landFeedback.PlayFeedbacks(position, intensity, false, contextDictionary);  // v6 context overload
StartCoroutine(landFeedback.PlayFeedbacksCoroutine(position, intensity));
StartCoroutine(landFeedback.PlayFeedbacksAfterFrames(2));

landFeedback.PlayFeedbacksInReverse();
landFeedback.PlayFeedbacksTopToBottom();
landFeedback.PlayFeedbacksBottomToTop();
landFeedback.PlayFeedbacksOnlyIfNormalDirection();
landFeedback.PlayFeedbacksOnlyIfReversed();
```

Stopping and state:

```csharp
landFeedback.StopFeedbacks();                  // stops everything
landFeedback.StopFeedbacks(stopAllFeedbacks: false);  // stop the sequence, let running ones finish
landFeedback.PauseFeedbacks();
landFeedback.ResumeFeedbacks();                // also releases a ScriptDriven MMF_Pause
landFeedback.SkipToTheEnd();
landFeedback.RestoreInitialValues();
landFeedback.ForceInitialValues();
landFeedback.ResetFeedbacks();
landFeedback.ResetAllCooldowns();
landFeedback.Initialization();                 // needed only with InitializationMode.Script

bool busy  = landFeedback.HasFeedbackStillPlaying();
bool going = landFeedback.IsPlaying;
float len  = landFeedback.TotalDuration;
int  count = landFeedback.TimesPlayed;
```

Reaching into individual feedbacks:

```csharp
MMF_Scale scale = landFeedback.GetFeedbackOfType<MMF_Scale>();
MMF_Scale named = landFeedback.GetFeedbackOfType<MMF_Scale>("LandSquash");   // by Label
List<MMF_Scale> all = landFeedback.GetFeedbacksOfType<MMF_Scale>();

scale.AnimateScaleDuration = 0.12f;
landFeedback.ComputeCachedTotalDuration();   // REQUIRED after changing a duration at runtime

scale.Play(transform.position, 1f);          // play one feedback on its own
```

Building at runtime (rarely the right answer — prefer authored prefabs):

```csharp
landFeedback.AddFeedback(typeof(MMF_Scale));
landFeedback.AddFeedback(new MMF_Scale { Label = "LandSquash" });
landFeedback.RemoveFeedback(1);
landFeedback.RefreshCache();
landFeedback.CopyPlayerFrom(other);
landFeedback.AutomaticShakerSetup();
```

Cache the `GetFeedbackOfType<T>()` result in `Awake` if it is read per frame — it walks the list.

---

## 3. MMF_Player settings

Grouped as the inspector groups them. Defaults are the shipped ones.

**Initialization** — `InitializationMode` (`Script` / `Awake` / `Start` / `OnEnable`, default
`Start`), `AutoInitialization` (true; lazily initializes just before a play), `AutoPlayOnStart`
(false), `AutoPlayOnEnable` (false), `RunFirstOnEnableOnlyAfterStart` (6.1, guards the
`OnEnable`-before-`Start` ordering bug).

**Safe Mode** — `SafeMode` (`Nope` / `EditorOnly` / `RuntimeOnly` / `Full`, default `Full`),
`LogMissingTargets` (true). Safe Mode runs an integrity pass over the list catching null and broken
feedbacks. `EditorOnly` is the usual production setting.

**Direction** — `Direction` (`TopToBottom` / `BottomToTop`), `AutoChangeDirectionOnEnd` (false).

**Intensity** — `FeedbacksIntensity` (1f), a global amplitude multiplier for the whole player.

**Timing** — `ForceTimescaleMode` + `ForcedTimescaleMode` (overrides every child feedback),
`PlayerTimescaleMode` (`Scaled`), `DurationMultiplier` (1f), `TimescaleMultiplier` (1f),
`RandomizeDuration` + `RandomDurationMultiplier`, `CooldownDuration` (0f), `InitialDelay` (0f),
`DisplayFullDurationDetails`.

**Range** — `OnlyPlayIfWithinRange`, `RangeCenter`, `RangeDistance` (5f), `UseRangeFalloff`,
`RangeFalloff`, `RemapRangeFalloff`, `IgnoreRangeEvents`. An `MMF_Player` outside range silently does
not play — a common "why is nothing happening".

**Play** — `CanPlay` (true), `CanPlayWhileAlreadyPlaying` (**true** by default, so plays overlap;
uncheck for one-at-a-time effects), `ChanceToPlay` (100), `PerformanceMode` (false),
`KeepPlayModeChanges` (false), `StopFeedbacksOnDisable` (false), `RestoreInitialValuesOnDisable`
(false), `PlayMode` (`Parallel` / `Sequential`) + `SequentialDelay` (6.0 — serial playback without
Pause feedbacks), `PlayCount`, `InPreviewMode`.

**Channel** — `MMF_ChannelMode`, `MMF_Channel` (0), `MMF_ChannelDefinition`.

**Kill switch** — `static MMFeedbacks.GlobalMMFeedbacksActive` disables every player in the project.

**Events** — `Events` (`MMFeedbacksEvents`): `OnPlay`, `OnPause`, `OnResume`, `OnStop`,
`OnComplete`, `OnChangeDirection`, `OnRestoreInitialValues`, `OnSkipToTheEnd`,
`OnInitializationComplete`, `OnEnable`, `OnDisable`. UnityEvents require "Trigger Unity Events";
the global `MMFeedbacksEvent` requires "Trigger MMFeedbacks Events".

```csharp
void OnEnable()  { landFeedback.Events.OnComplete.AddListener(HandleComplete); }
void OnDisable() { landFeedback.Events.OnComplete.RemoveListener(HandleComplete); }
```

---

## 4. MMF_Feedback — shared fields

Every feedback, whatever its type, carries: `Active`, `Label`, `ChannelMode` / `Channel` /
`MMChannelDefinition`, `Chance` (0–100, on the feedback itself, not in Timing), `Timing`,
`AutomatedTargetAcquisition`, `RandomizeOutput` + `RandomMultiplier` (0.8–1),
`RandomizeDuration` + `RandomDurationMultiplier` (0.5–2), `UseRange` + `RangeDistance` +
`UseRangeFalloff` + `RangeFalloff` + `RemapRangeFalloff`, `Owner`, `DebugActive`.

Read-only: `IsPlaying`, `InCooldown`, `PlaysLeft`, `InInitialDelay`, `FeedbackStartedAt`,
`TotalDuration` (initial delay + duration × repeats + delays).

### `MMFeedbackTiming`

| Field | Default | Note |
|---|---|---|
| `TimescaleMode` | `Scaled` | `Unscaled` for anything that must keep moving during a freeze frame or a pause menu |
| `ExcludeFromHoldingPauses` | false | A Holding Pause below will not wait on this feedback |
| `ContributeToTotalDuration` | true | Set false on looping/infinite feedbacks to keep `TotalDuration` finite |
| `InitialDelay` | 0 | |
| `CooldownDuration` | 0 | Minimum seconds between two plays of *this* feedback |
| `InterruptsOnStop` | true | Whether `StopFeedbacks()` reaches it |
| `NumberOfRepeats` | 0 | Extra repeats; 0 plays once |
| `RepeatForever` | false | |
| `DelayBetweenRepeats` | 1 | |
| `IgnoreFeedbackDurationForRepeats` | false | 6.1 — repeat interval becomes purely the delay |
| `LimitPlayCount` / `MaxPlayCount` / `SetPlayCountToZeroOnReset` | false / 3 / false | |
| `MMFeedbacksDirectionCondition` | `Always` | `OnlyWhenForwards`, `OnlyWhenBackwards` |
| `PlayDirection` | `FollowMMFeedbacksDirection` | `Opposite…`, `AlwaysNormal`, `AlwaysRewind` |
| `ConstantIntensity` | false | Ignore the caller's intensity, always play at full |
| `UseIntensityInterval` + `IntensityIntervalMin` / `Max` | false / 0 / 0 | Only play inside an intensity window — how you get "heavy landing only" |
| `Sequence` / `TrackID` / `Quantized` / `TargetBPM` | — / 0 / false / 120 | MMSequence-driven playback |
| `UseScriptDrivenTimescale` / `ScriptDrivenDeltaTime` / `ScriptDrivenTime` | false | |

`ExclusiveMode` does not exist in this version — do not reference it.

### Blocking and sequencing

There is no "hold until complete" boolean. Feel expresses it structurally:

- `MMF_Pause` — `PauseDuration` 1f, `RandomizePauseDuration`, `MinPauseDuration` 1f /
  `MaxPauseDuration` 3f, `ScriptDriven` (resume with `player.ResumeFeedbacks()`), `AutoResume` +
  `AutoResumeAfter` 0.25f. Blocks everything below it in the list.
- `MMF_HoldingPause` — waits until all previously started feedbacks finish. This is the real
  "hold until complete". Feedbacks with `ExcludeFromHoldingPauses` are not waited on.
- `MMF_Looper` / `MMF_LooperStart` — `NumberOfLoops` 2, `InfiniteLoop`, `LoopAtLastPause`,
  `LoopAtLastLoopStart`. Moves the sequence head back to the nearest pause or loop start.
- `PlayMode = Sequential` + `SequentialDelay` (6.0) achieves serial playback without Pause
  feedbacks — usually the cleaner choice.

---

## 5. Verified defaults worth knowing

| Feedback | Defaults |
|---|---|
| `MMF_CameraShake` | duration 0.1, amplitude 0.2, frequency 40, `RepeatUntilStopped` false |
| `MMF_CameraZoom` | mode `For`, FOV 30, transition 0.05 s, hold 0.1 s |
| `MMF_Flicker` | mode `Color`, duration 0.2 s, period 0.04 s (≈5 flickers), colour (255,20,20) |
| `MMF_Scale` | mode `Absolute`, duration 0.2 s, curve keys (0→0, 0.3→1.5, 1→0), remap 1→2 — the canonical punch |
| `MMF_SquashAndStretch` | axis `YtoXZ`, duration 0.2 s, same punch curve, remap 1→2 |
| `MMF_Position` | mode `AtoB`, world space, duration 0.2 s, `RelativePosition` true |
| `MMF_FreezeFrame` | duration 0.1 s, `MinimumTimescaleThreshold` 0.1 (will not stack onto an already-slowed game) |
| `MMShaker` (all shakers) | `ShakeDuration` 0.2 s, cooldown 0 |
| Any `MMSpring*` | `Damping` 0.4, `Frequency` 6 |
| `MMF_ScaleSpring` | mode `Bump`, damping 0.4, frequency 6, bump min/max (20,20,20)–(30,30,30), `DeclaredDuration` 0 |

Feel's own recipe page suggests a heavier camera shake than the feedback default: duration 0.3,
amplitude 2, frequency 40.

---

## 6. Shakers and events

The pattern is feedback → static event → shaker listening on a matching channel. The feedback never
holds a reference to the camera or the Volume, which is what makes an authored player work in any
scene and survive prefab instantiation.

`MMShaker` base (`Assets/Feel/MMFeedbacks/MMFeedbacks/Core/MMShaker.cs`): `ShakeDuration` (0.2),
`PlayOnAwake`, `PermanentShake`, `Interruptible`, `AlwaysResetTargetValuesAfterShake`,
`OnlyUseShakerValues`, `CooldownBetweenShakes`, `TimescaleMode`, channel fields. Lifecycle: event on
matching channel → `StartShaking()` → `ShakeStarts()` → per-frame `Shake()` over `ShakeDuration` →
`ShakeComplete()` → `ResetTargetValues()`.

Shakers present in this copy (`Assets/Feel/MMFeedbacks/MMFeedbacks/Shakers/`): `MMCameraShaker`,
`MMCameraShakerRotation`, `MMCameraZoom`, `MMCameraClippingPlanesShaker`,
`MMCameraFieldOfViewShaker`, `MMCameraOrthographicSizeShaker`, `MMFeedbacksShaker`, `MMFlash`,
`MMBlink`, `MMWiggle`, `MMPositionShaker`, `MMRotationShaker`, `MMScaleShaker`, `MMLookAtShaker`,
`MMLightShaker`, `MMSpriteRendererShaker`, and the five audio-filter plus three AudioSource shakers.
URP post-process shakers live under `MMFeedbacksForThirdParty/URP/Shakers/`.

### Events you can fire directly

```csharp
using MoreMountains.Feedbacks;
using MoreMountains.Tools;

MMCameraShakeEvent.Trigger(duration, amplitude, frequency,
                           amplitudeX, amplitudeY, amplitudeZ,
                           infinite: false, channelData: null, useUnscaledTime: true);

MMFreezeFrameEvent.Trigger(0.05f);

MMTimeScaleEvent.Trigger(MMTimeScaleMethods.For, 0.5f, 1f, true, 50f, false);
// method, timescale, duration, lerp?, lerpSpeed, infinite?
MMTimeScaleEvent.Unfreeze();   // pop one modifier
MMTimeScaleEvent.Reset();      // clear the stack

MMF_PlayerEvent.Trigger(channelData, usePosition: true, position,
                        MMF_PlayerEvent.Modes.PlayFeedbacks);

MMSoundManagerSoundPlayEvent.Trigger(clip, MMSoundManager.MMSoundManagerTracks.Sfx, position);
```

`MMTimeManager` keeps timescale modifiers on a **stack**, so simultaneous slow-downs coexist and
unwind individually. Anything that must keep animating through a freeze needs
`TimescaleMode = Unscaled`.

`MMF_PlayerEvent.Modes` covers `PlayFeedbacks`, `StopFeedbacks`, `PauseFeedbacks`,
`ResumeFeedbacks`, `Initialization`, the direction variants, `RestoreInitialValues`, `SkipToTheEnd`,
`RefreshCache`.

### Channels

```csharp
var byInt     = new MMChannelData(MMChannelModes.Int, 12, null);
var byAsset   = new MMChannelData(MMChannelModes.MMChannel, 0, myMMChannelAsset);
```

`MMChannel.Match(a, b)` is the comparison; a null channel matches everything. Channel 0 is the
default catch-all. Prefer named `MMChannel` ScriptableObjects (Create ▸ MoreMountains ▸ MMChannel);
sample assets ship at `Assets/Feel/MMFeedbacks/MMFeedbacks/Core/MMChannels/`.

### `MMFeedbacksShaker`

A shaker that plays an attached `MMF_Player` when it receives `MMFeedbacksShakeEvent`. This is the
bridge for firing an arbitrary authored sequence from a fully decoupled event, with optional
spatial range gating.

---

## 7. Springs

Introduced in 4.1, ~70 components in this copy. A spring is a serializable class you can declare as
a field, or a ready-made component that owns one and writes it into a property.

```csharp
public MMSpringVector3 _scaleSpring;   // Damping 0.4, Frequency 6 by default

void Update()
{
    _scaleSpring.UpdateSpringValue(Time.deltaTime);   // you must drive a raw spring yourself
    _visual.localScale = _scaleSpring.CurrentValue;
}
```

Methods: `MoveTo`, `MoveToAdditive`, `MoveToSubtractive`, `MoveToInstant`, `MoveToRandom`, `Bump`,
`BumpRandom`, `Stop`, `Finish`, `SetInitialValue`, `SetCurrentValueAsInitialValue`,
`RestoreInitialValue`, `UpdateSpringValue`.

**`MoveTo` vs `Bump`**: `MoveTo` changes the rest target and springs toward it. `Bump` injects
velocity — the value shoots out and returns to the existing rest position. **Bump is what you want
for landing squash, hit reactions and button presses.**

Parameters: `Damping` (0–1; near 0 oscillates a long time and reads gelatinous, near 1 settles
almost immediately), `Frequency` (oscillations per second while settling). House default 0.4 / 6
gives a visible 2–3 wobble settle over roughly half a second. Damping 0.7–0.9 with frequency 8–15 is
a crisp UI pop; damping 0.15–0.3 with frequency 3–6 is a rubbery cartoon bounce. `UnifiedSpring`
shares one damping/frequency across all axes of a vector spring.

Spring components live at `Assets/Feel/MMFeedbacks/MMFeedbacks/Springs/Springs/` — `MMSpringPosition`,
`MMSpringRotation`, `MMSpringScale`, `MMSpringSquashAndStretch`, `MMSpringCameraFieldOfView`,
`MMSpringMMTimeScale`, plus UI, light, audio and shader variants, and 14 URP post-process springs.
Using a component means you never call `UpdateSpringValue` yourself.

A spring's settle time is emergent, so `DeclaredDuration` on a spring feedback exists only to keep
`TotalDuration` and Holding Pause sane — it does not shorten the spring.

---

## 8. MMSoundManager

`MMSoundManager : MMPersistentSingleton<MMSoundManager>`, built on Unity's AudioMixer. Tracks:
`Master`, `Music`, `Sfx`, `UI`, `Other` (6.0 added custom tracks). Configuration lives in an
`MMSoundManagerSettingsSO`. It pools AudioSources rather than creating and destroying them; the
pool must exceed peak simultaneous sounds.

```csharp
MMSoundManagerPlayOptions options = MMSoundManagerPlayOptions.Default;
options.Volume = 0.5f;
options.Pitch  = Random.Range(0.94f, 1.06f);     // ~1 semitone, see game-feel numbers
options.MmSoundManagerTrack = MMSoundManager.MMSoundManagerTracks.Sfx;
options.ID = 50;
MMSoundManagerSoundPlayEvent.Trigger(clip, options);

MMSoundManagerSoundFadeEvent.Trigger(50, 5f, 0f, fadeTween);
MMSoundManagerTrackEvent.Trigger(MMSoundManagerTrackEventTypes.PauseTrack,
                                 MMSoundManager.MMSoundManagerTracks.UI);
```

A new project starts with no mixer and no MMSoundManager, and that is a fine place to stay. Adopting MMSoundManager is a decision to
make deliberately (it brings a mixer asset, a settings SO and a scene singleton), not something to
slip in with the next sound. The plain `MMF_Sound` feedback needs none of it and is
the right starting point; `MMF_MMSoundManagerSound` gains tracks, fades, concurrency limits and
save/load when there is a reason for them.

---

## 9. Writing a custom feedback

Inherit from an existing feedback rather than editing it — edits are lost on asset update.

```csharp
using MoreMountains.Feedbacks;
using UnityEngine;

[AddComponentMenu("")]
[System.Serializable]
[FeedbackHelp("What this feedback does.")]
[FeedbackPath("__GAME__/My Feedback")]
public class MMF_MyFeedback : MMF_Feedback
{
    public static bool FeedbackTypeAuthorized = true;     // the accessibility kill switch
    public override float FeedbackDuration => Duration;

    [MMFInspectorGroup("My Feedback", true, 12)]
    public float Duration = 0.2f;

    protected override void CustomInitialization(MMF_Player owner)
    {
        base.CustomInitialization(owner);
    }

    protected override void CustomPlayFeedback(Vector3 position, float feedbacksIntensity = 1f)
    {
        if (!Active || !FeedbackTypeAuthorized) { return; }
        float intensity = ComputeIntensity(feedbacksIntensity, position);
        // ...
    }

    protected override void CustomStopFeedback(Vector3 position, float feedbacksIntensity = 1f) { }
    protected override void CustomRestoreInitialValues() { }
}
```

Other hooks: `CustomSkipToTheEnd`, `CustomPlayerComplete`, `CustomReset`. Helpers:
`ApplyTimeMultiplier(duration)`, `ApplyDirection(normalizedTime)`, `Owner.StartCoroutine(...)`.
Inspector attributes: `[MMFInspectorGroup(name, bool, colorIndex)]`, `[MMFCondition("Field", true)]`,
`[MMFEnumCondition("Field", (int)Enum.Value)]`, `[MMFInspectorButton("Method")]`, `[MMFReadOnly]`.

A custom feedback belongs in `__GAME__.Game`, which means adding it to a folder covered by
`__GAME__.Game.asmdef` (with the `MoreMountains.Tools` reference), not inside `Assets/Feel`.
