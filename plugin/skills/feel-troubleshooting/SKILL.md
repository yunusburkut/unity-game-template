---
name: feel-troubleshooting
description: "Feel feedback broken (\"feedback çalışmıyor\", \"shake olmuyor\", \"titreşim yok\"): PlayFeedbacks() shows nothing, fires once, MMF_ types won't compile, shake/freeze ignored, value left half-done, juice stopped working or differs on 2nd Play."
---

# When a feedback does nothing

Feel fails quietly by design — a missing listener, a mismatched channel or an out-of-range player
produces no effect and no error. Work down this list in order; the cheap checks are first.

Compile state is in `Logs/agent/compile.log` (`OK` plus a timestamp means clean; one older than the
edit means no compile has run since, and `gk-bridge refresh` compiles without focus). Console errors and warnings are
mirrored to `Logs/agent/console.log`. See `unity-editor-cli`.

## It does not compile

**`The type or namespace name 'MMF_Player' could not be found`** — the file's assembly does not
reference `"MoreMountains.Tools"`. In Core, Feel never belongs: move the code to Game. In
`<Game>.Game` (or a new asmdef), add `"MoreMountains.Tools"` to its references, plus
`"Lofelt.NiceVibrations"` for haptics. Then check `using MoreMountains.Feedbacks;`. There is no separate
`MoreMountains.Feedbacks` assembly; every feedback compiles into `MoreMountains.Tools` via `.asmref` files.

**A specific `MMF_*` type is not found but others resolve** — that feedback is compiled out by a
version define that `MoreMountains.Tools.asmdef` derives from the package manifest: `MMF_Cinemachine*`
(Cinemachine absent; use `MMF_CameraShake` with an `MMCameraShaker`), the PPv2 post-process family
(use the `_URP` variants), HDRP and VFX Graph feedbacks. The fix is to pick an available feedback, not
to add a package; the small manifest is deliberate, ask first. The full define table (on/off with the
template's manifest, including `MM_TEXTMESHPRO` and `MM_SCREENCAPTURE`) is the top section of
`feel-authoring/references/feedback-catalog.md`, and the per-feedback on/off list follows it there.

**Namespace is wrong** — `MoreMountains.Feedbacks` for the player, feedbacks, shakers, springs,
`MMTimeManager`, `MMWiggle`; `MoreMountains.Tools` for `MMSoundManager`, poolers;
`MoreMountains.FeedbacksForThirdParty` for the URP post-process shakers and `MMCameraZoom`.

**Code from a tutorial does not compile** — it is probably legacy API. `GetComponent<MMFeedbacks>()`
and `MMFeedbackScale` became `MMF_Player` and `MMF_Scale` in Feel 3.0. `MMVibrationManager` is the
pre-v4 Nice Vibrations API and does not exist in Feel 6.1; use `HapticPatterns` / `HapticController`
(`Lofelt.NiceVibrations`).

## `PlayFeedbacks()` runs but nothing happens

Check, in this order:

1. **Is it being called?** A `Debug.LogWarning("[DBG-…]")` at the call site settles it in one Play
   session — warnings reach `Logs/agent/console.log`, a plain `Debug.Log` does not. One-step edge
   flags like `Landed` are reset at the top of every solver step, so polling them anywhere other than
   immediately after the step misses them entirely.
2. **`Active` on the individual feedback**, and `CanPlay` on the player.
3. **The player's GameObject is inactive in the hierarchy** (a pooled or disabled object) — the
   player refuses to play from it.
4. **`CanPlayWhileAlreadyPlaying` is false** and the player is still running from the previous
   call, or `AutoPlayOnEnable` already started it in the same frame as `Start`.
5. **`ChanceToPlay`** on the player or `Chance` on the feedback, if either is below 100.
6. **`CooldownDuration`** on the player or in the feedback's `Timing` — a second call inside the
   cooldown is silently dropped.
7. **`OnlyPlayIfWithinRange`** with a `RangeCenter` that is null or far away. The player just does
   not play.
8. **`UseIntensityInterval`** on a feedback, with the incoming intensity outside
   `IntensityIntervalMin`–`Max`. This is the usual cause of "the heavy landing effect never fires".
9. **`LimitPlayCount` / `MaxPlayCount`** — the feedback has used up its plays.
10. **`MMFeedbacks.GlobalMMFeedbacksActive`** is false, or the feedback class's static
   `FeedbackTypeAuthorized` is false. Both are global kill switches; with Play Mode reload disabled
   they survive from a previous session (see below).
11. **`MMFeedbacksDirectionCondition`** is `OnlyWhenForwards`/`OnlyWhenBackwards` and the player is
   going the other way.

## The listener is missing

Event-based feedbacks have no target and do nothing until something in the scene is listening.
Nothing is logged.

| Silent feedback | Missing from the scene |
|---|---|
| `MMF_CameraShake` | `MMCameraShaker` (+ `MMWiggle`) |
| `MMF_CameraZoom` | `MMCameraZoom` on the camera |
| `MMF_FreezeFrame`, `MMF_TimescaleModifier` | `MMTimeManager` |
| `MMF_FloatingText` | `MMFloatingTextSpawner` with a prefab assigned |
| `MMF_MMSoundManagerSound` and friends | `MMSoundManager` + `MMSoundManagerSettingsSO` |
| `MMF_Bloom_URP`, `MMF_Vignette_URP`, … | the matching `MM*Shaker_URP` on the Volume object |

The feedback inspector's **Automatic Shaker Setup** button (or `player.AutomaticShakerSetup()`)
creates the listener.

A listener that exists can still drop the event: a shaker whose GameObject is inactive in the
hierarchy ignores every event, and a feedback with `Timing` > `UseRange` reaches only shakers within
`RangeDistance` (5 by default) of the feedback's position — a camera farther away never shakes.

One extra trap for URP post-process feedbacks: the shaker must exist **and** the Volume profile must
actually contain that override: a Chromatic Aberration shaker on a profile without Chromatic
Aberration has nothing to drive. Read the scene's Volume profile before blaming the feedback.

## The channel does not match

A shaker only reacts when its channel matches the event's. Channel mismatch is silent and is the
single most annoying Feel bug to find, because everything looks correctly wired.

Channel 0 is only the default: it matches channel 0 and nothing else, so a shaker on 0 and a
feedback on 3 never meet. Only a null channel (an event triggered from code without channel data)
matches every shaker. If you moved one side to a named `MMChannel` asset or to a
non-zero integer, move the other side too. Check `ChannelMode` as well as the value — `Int 0` and
`MMChannel <asset>` do not match.

## The camera does not move even though the shaker fires

A camera script that writes the camera's position every `LateUpdate` overwrites a shaker on the same
GameObject every frame.

The hierarchy that works: **CameraRig (the follow script) → CameraShaker (`MMCameraShaker` +
`MMWiggle`) → Main Camera**. Check the shake landed on `CameraShaker` and not on `CameraRig` or
`Main Camera`, and that its channel matches. Any fix is a scene change — use `unity-editor-cli`, never
hand-edit a `.unity` file while the Editor is open.

## It freezes, stutters, or stops mid-effect

- **Everything stops during a freeze frame** — the feedback's `TimescaleMode` is `Scaled`. UI,
  camera shake, and anything that must play *during* the freeze needs `Unscaled`. The player's own
  `PlayerTimescaleMode` and `ForceTimescaleMode` override children.
- **Freeze frame does nothing when the game is already slowed** — `MMF_FreezeFrame` has a
  `MinimumTimescaleThreshold` of 0.1 and refuses to fire while `Time.timeScale` is already below it,
  i.e. during another freeze or a near-zero slow-mo. A game slowed to 0.5 still freezes; if it does
  not, look for a missing `MMTimeManager` or a channel mismatch instead.
- **Input is eaten during a hit stop** — either presses are read only in `FixedUpdate` (which does
  not run at time scale 0), or the jump buffer and coyote timers count unscaled time and drain during
  the freeze. Read input in `Update` and count those timers on the simulation's scaled step
  (`SimulationStep.Delta`) so they pause with the freeze (`game-feel` references/numbers.md section 3.1).
- **Timescale never returns to 1** — `MMTimeManager` keeps modifiers on a stack. An unbalanced
  `MMTimeScaleEvent.Trigger` needs its `Unfreeze()`; `MMTimeScaleEvent.Reset()` clears the stack.

## The object is left at a half-finished value

A sequence runs on coroutines hosted by the player's own GameObject. Disabling or destroying that
object mid-sequence strands the target at whatever intermediate value it had reached.

- Set `RestoreInitialValuesOnDisable` and/or `StopFeedbacksOnDisable` on the player.
- For "destroy the thing" sequences, put the `MMF_Player` on a separate surviving GameObject and
  make `MMF_Destroy` the last feedback in the list.
- `MMF_PlayerEnabler` exists for the case where the player must keep running on an object that is
  being disabled.
- `player.RestoreInitialValues()` and `ForceInitialValues()` are the manual escape hatches.

## It works the first time and then behaves oddly

- **`AutoPlayOnEnable` plus pooling** — `OnEnable` fires on every retrieval from a pool, so the
  player plays on every spawn. Usually what you want for VFX, usually a bug for UI.
- **`OnEnable` before `Start`** on the first activation, with `InitializationMode = Start`, means
  the first play can hit an uninitialized player. Feel 6.1 added
  `RunFirstOnEnableOnlyAfterStart` for exactly this.
- **Initialization order** — if another script assigns a feedback's target in `Start`, use
  `InitializationMode = Script` and call `Initialization()` after the assignment, or rely on
  `AutoInitialization` deferring to the first play.
- **Runtime duration change ignored** — after writing to a feedback's duration you must call
  `player.ComputeCachedTotalDuration()`, or `TotalDuration` and any Holding Pause stay stale.

## It behaves differently on the second Play session

**Play Mode domain and scene reload are both disabled in this project.** Every mutable static
survives between sessions. That includes `MMFeedbacks.GlobalMMFeedbacksActive`, every feedback
class's `FeedbackTypeAuthorized`, and any singleton instance Feel or our code holds.

If a setting we wrote (an accessibility toggle, a debug kill switch) is not reset in a
`[RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.SubsystemRegistration)]` method, the first
run after a recompile will look right and the second will not. Test the second run. How to write
such a static in the first place is in `feel-authoring`.

## It is slow, or the Inspector is sluggish

- `SafeMode` defaults to `Full`, running an integrity pass in the editor **and** at runtime
  initialization. `EditorOnly` keeps the authoring protection and costs nothing at runtime.
- `PerformanceMode` on the player reduces inspector redraw work; keep long feedback lists folded.
- Non-pooled `MMF_ParticlesInstantiation` / `MMF_InstantiateObject` allocate per play. Switch to the
  pooled mode for anything firing more than a few times a second.
- `LogMissingTargets` spam means real empty target slots — fix them rather than silencing the flag.
- A `GetComponent<MMF_Player>()` or `GetFeedbackOfType<T>()` in a per-frame path is the usual
  culprit for a steady cost. Cache in `Awake` (`unity-performance`).

## Nothing above explains it

Open a reference scene and compare against a known-working setup: the shipped demo scenes, only if the
Feel demos were imported (games made by `new-game.ps1` have no `FeelDemos/` or `MMFeedbacks/Demos/`; check with
Glob first, otherwise use the online docs) (every
feedback, the same jump with and without feedbacks, 20+ shake variations) and the official docs and
API index are listed with their paths under References in `feel-authoring`.
