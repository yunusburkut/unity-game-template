---
name: feel-troubleshooting
description: "Feel feedback broken (\"feedback çalışmıyor\", \"shake olmuyor\", \"titreşim yok\"): PlayFeedbacks() shows nothing, fires once, MMF_ types won't compile, shake/freeze ignored, value left half-done, juice stopped working or differs on 2nd Play."
---

# When a feedback does nothing

Feel fails quietly by design — a missing listener, a mismatched channel or an out-of-range player
mostly produces no effect and no error (an empty target slot is the one case that may log a warning,
item 2 below). Work down this list in order; the cheap checks are first.

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
2. **The feedback's target is empty.** A newly added `MMF_Scale`, `MMF_Flicker` or similar whose
   target field was never assigned (and whose `AutomatedTargetAcquisition` is off or finds nothing)
   does nothing. Many feedbacks then log `[<Name> Feedback] ... doesn't have an <target>, it won't
   work` to `Logs/agent/console.log` (when the player's `LogMissingTargets` is on, the default), so
   search the log first; others, `MMF_Scale` among them, return without logging, so read the
   feedback's serialized target fields even when the log is clean.
3. **`Active` on the individual feedback**, and `CanPlay` on the player.
4. **The player's GameObject is inactive in the hierarchy** (a pooled or disabled object) — the
   player refuses to play from it.
5. **`CanPlayWhileAlreadyPlaying` is false** and the player is still running from the previous
   call.
6. **`AutoPlayOnEnable` is on and the call lands in the same frame as an earlier play.** Any second
   `PlayFeedbacks` in the same frame as a previous one (the auto-play on spawn included) is dropped,
   even with `CanPlayWhileAlreadyPlaying` true: a pooled object that auto-plays on enable and is then
   played by its spawner with a custom intensity in the same frame shows only the auto-play.
7. **`ChanceToPlay`** on the player or `Chance` on the feedback, if either is below 100.
8. **`CooldownDuration`** on the player or in the feedback's `Timing` — a second call inside the
   cooldown is silently dropped.
9. **`OnlyPlayIfWithinRange`** with a `RangeCenter` that is null or far away. The player just does
   not play.
10. **`UseIntensityInterval`** on a feedback, with the incoming intensity outside
   `IntensityIntervalMin`–`Max`. This is the usual cause of "the heavy landing effect never fires".
   The window is [Min, Max): Max 0 plays nothing, and with intensity normalised to 0..1 Max must be
   above 1 (e.g. 1.01) or the strongest hit is dropped (`feel-authoring/references/feel-api.md`,
   section 4).
11. **`LimitPlayCount` / `MaxPlayCount`** — the feedback has used up its plays.
12. **`MMFeedbacks.GlobalMMFeedbacksActive`** is false, or the feedback class's static
   `FeedbackTypeAuthorized` is false. Both are global kill switches; in Feel 6.1, with Play Mode reload
   disabled, they survive from a previous session (see below). `FeedbackTypeAuthorized` is written from the
   toggles of an `MMFeedbacksAuthorizations` component when one exists: search the scenes and
   prefabs for it (a demo prefab carries one) before searching code.
13. **`MMFeedbacksDirectionCondition`** is `OnlyWhenForwards`/`OnlyWhenBackwards` and the player is
   going the other way.

## No vibration ("titreşim yok")

Haptics fail silently in more places than visuals. Check, in this order:

1. **Where is it tested?** The Editor and a PC build only rumble a connected gamepad; with none, the
   haptic feedbacks do nothing and that is correct. Judge vibration on a phone build.
2. **The define for the phone target.** `MMF_NV*` feedbacks exist only where
   `MOREMOUNTAINS_NICEVIBRATIONS_INSTALLED` is defined, and Feel adds it only for the build target
   active when the Editor loaded. If Android or iOS lacks it, an `MMF_Player` serialized from that
   target has silently lost its NV entries: check the player's list, then the define for each
   platform. The rule and the fix (a project setting; ask first) are in
   `feel-authoring/references/feedback-catalog.md`, *Haptics*.
3. **The haptics toggle.** `HapticController.hapticsEnabled` false (set by the game's haptics
   setting or an `MMF_NVControl`; it is a static, so with Play Mode reload disabled a value from a
   previous Play session survives, see below) mutes
   every haptic, from feedbacks and from `HapticPatterns` alike.
4. **Then the player checklist above** — the NV feedback is an ordinary feedback for `Active`,
   chance, cooldown, intensity interval and play count.

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
| `MMF_Sound` with `PlayMethod` left at the default `Event` | an `MMSoundManager` to catch its `MMSoundManagerSoundPlayEvent` (or legacy `MMSfxEvent`); without one, set `PlayMethod` to `Cached` (`Pool` when the sound overlaps itself) |
| `MMF_Bloom_URP`, `MMF_Vignette_URP`, … | the matching `MM*Shaker_URP` on the Volume object |

The feedback inspector's **Automatic Shaker Setup** button (or `player.AutomaticShakerSetup()`)
creates the listener.

An `MMF_Sound` that plays but ignores the volume sliders has an empty `SfxAudioMixerGroup`: assign
the SFX or UI group (feel-authoring sets both fields when it adds the feedback).

A listener that exists can still drop the event: a shaker whose GameObject is inactive in the
hierarchy ignores every event, and a feedback with `UseRange` on (a field of the feedback itself, in
its Feedback Range group, not in `Timing`) reaches only shakers within `RangeDistance` (5 by default)
of the feedback's position — a camera farther away never shakes.

One extra trap for URP post-process feedbacks: the shaker must exist **and** the Volume profile must
actually contain that override: a Chromatic Aberration shaker on a profile without Chromatic
Aberration has nothing to drive. Read the scene's Volume profile before blaming the feedback.

## The channel does not match

A shaker only reacts when its channel matches the event's. Channel mismatch is silent and is the
single most annoying Feel bug to find, because everything looks correctly wired.

A shaker left on the default channel and a feedback moved to another one never meet; only an event
triggered from code without channel data reaches every shaker. The exact matching rule
(`MMChannel.Match`) is in `feel-authoring/references/feel-api.md`, section 6 *Channels*. If you moved one side to a named `MMChannel` asset or to a
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
- **Freeze frame does nothing when the game is already slowed** — `MMF_FreezeFrame` refuses to fire
  while `Time.timeScale` is below its `MinimumTimescaleThreshold`, i.e. during another freeze or a
  near-zero slow-mo. The default value, and which slow-downs still freeze, are in
  `feel-authoring/references/feel-api.md`, section 5; if the time scale is above the threshold and it
  still does not freeze, look for a missing `MMTimeManager` or a channel mismatch instead.
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
- A sequence cannot outlive its host: when the object is being disabled, move the `MMF_Player` to a
  GameObject that stays active, as for `MMF_Destroy`. (`MMF_PlayerEnabler` does not help here: Feel
  adds it automatically to `AutoPlayOnEnable` players so they can play again when their object is
  re-enabled; it keeps nothing running while the object is off.)
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
- **Runtime duration change ignored** — `TotalDuration` and any Holding Pause are cached; a duration
  written at runtime needs the recompute call shown in `feel-authoring/references/feel-api.md`,
  section 2 (`ComputeCachedTotalDuration()`).

## It behaves differently on the second Play session

**Play Mode domain and scene reload are both disabled in this project.** Every mutable static
survives between sessions. That includes any singleton instance Feel or our code holds and, in Feel
6.1, `MMFeedbacks.GlobalMMFeedbacksActive` and every feedback class's `FeedbackTypeAuthorized`
(Feel 6.4 marks those two `[AutoStaticsCleanup]`; the version is in `Assets/Feel/readme.txt`).

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

Compare against a known-working setup: the Feel demo scenes listed, with their paths and what each
shows, under References in `feel-authoring` (check with Glob first; games made by `new-game.ps1` ship
without them), or the official docs and API index listed in the same place.
