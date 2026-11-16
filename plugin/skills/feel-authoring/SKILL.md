---
name: feel-authoring
description: Use when adding or changing juice, shake, hit stop, particles, sound, music or vibration ("juice ekle", "müzik ekle", "ses", "titreşim") - wiring Feel (MMF_Player, haptics), mixer, volume. Numbers: game-feel; broken feedback: feel-troubleshooting.
---

# Using Feel

Feel (More Mountains) lives at `Assets/Feel`, a vendored paid package (committed in private game repos, gitignored in
older ones); it includes Nice Vibrations.
The full code-facing API is `references/feel-api.md`.

## Step zero: the assembly reference

Feel ships **no `MoreMountains.Feedbacks` assembly**. Every MMFeedbacks folder carries an `.asmref` pointing at
`MoreMountains.Tools`, so all feedbacks, shakers, springs and `MMSoundManager` compile into that one assembly.

The first time Game uses Feel, add `"MoreMountains.Tools"` to `Assets/<Game>/Game/<Game>.Game.asmdef`. Haptics
(`MMF_NV*` feedbacks, `HapticPatterns` / `HapticController`) also need `"Lofelt.NiceVibrations"`. `<Game>.Core` never gets either:
if a Feel type is needed in Core, the design is wrong.

## What compiles

`MoreMountains.Tools.asmdef` turns feedback families on from the package manifest through version defines. In short:
URP post-process feedbacks (`_URP` variants), uGUI and TMP (`ugui` 2.x ships TMP), Input System, Physics2D are on;
Cinemachine, PPv2, HDRP and VFX Graph feedbacks do not exist here. Most Feel tutorials reach for Cinemachine impulses,
use `MMF_CameraShake` with an `MMCameraShaker` instead. The define-by-define table (the single source; re-read it when
the manifest changes) is `references/feedback-catalog.md`, top section. Do not add a package to turn a family on
without asking.

## Where the code goes

The simulation does not know presentation exists (`unity-architecture`). The channel is the solver's one-step edge
flags (`Landed`, `Matched`, `Cleared`), reset at the top of every step: the view polls them right after stepping and
plays a feedback. Continuous values (speed, combo count) are read the same way for intensity.

Practically: the system's `<System>View` MonoBehaviour in its own folder `Assets/<Game>/Game/<System>/` (the
convention is in `unity-architecture`, Cross-system communication) holding serialized `MMF_Player` fields, fed by the
controller after it steps. Do not grow a feedback field per event on the controller itself; do not look up an
`MMF_Player` in a per-frame path.

Scale intensity from the simulation rather than hardcoding it: `PlayFeedbacks(position, intensity)` takes it
directly. Timings and intensities live in one ScriptableObject or in the `MMF_Player`, never as literals in code.

Any static you add (a mute toggle, a "haptics off" switch) needs a
`[RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.SubsystemRegistration)]` reset, or it survives into the next
Play session.

## PC and mobile

- **Haptics are mobile only.** `MMF_NVPreset` / `MMF_NVEmphasis` on the same `MMF_Player` as the visual feedback;
  on PC Nice Vibrations only rumbles a connected gamepad, so no `#if` is needed. Keep a player setting to turn them
  off (`HapticController.hapticsEnabled`, which covers phone and gamepad alike), and keep them
  short: a light preset for taps, a medium one for a win, never a continuous rumble.
- **WebGL has no haptics.** Nice Vibrations does nothing in a browser, phone browsers included, so feedback that
  carries meaning (refused, invalid, fail) must also be visible or audible, never haptic alone.
- **Shake less on a phone.** The screen is in the player's hand and close to the eyes. House rule: the `<System>View`
  scales only the shake, in `Awake` (one player, not two; never by lowering the `PlayFeedbacks` intensity, which also
  quietens sound, squash and haptics and shifts intensity windows). The scale is one float, `tuning.MobileShakeScale` (0.5),
  on the system's `<System>Tuning` SO, applied when the quality tier is Mobile (`platform-targets` Quality tiers):
  `if (QualitySettings.GetQualityLevel() == 0) foreach (var s in player.GetFeedbacksOfType<MMF_CameraShake>()) s.CameraShakeProperties.Amplitude *= tuning.MobileShakeScale;`
  for each player (and `AmplitudeX/Y/Z` if used). `Main` stays loaded, so a tier changed in settings applies from
  the next app launch; say so next to the quality option rather than re-scaling live.
- **Hit stop** (`MMF_FreezeFrame`) needs an `MMTimeManager` in the scene; how it avoids eating presses (input in
  `Update`, buffers on `SimulationStep.Delta`, unscaled time only for shake and UI) is `game-feel`
  references/numbers.md section 3.1, the single source.
- **Particles** are the first thing to cut on the Mobile tier (`unity-performance`).

## Music, ambience and volume

- **Routing.** One AudioMixer with Master, Music, SFX and UI groups (the four sliders, `player-clarity` CL35). Start
  plain: music is a looped `AudioSource` on the Music group in the `Main` scene, SFX go through `MMF_Sound` with
  `PlayMethod` set to `Cached` (`Pool` when the same sound overlaps itself) and `SfxAudioMixerGroup` set to the SFX
  or UI group. Its default, `Event`, only raises an event that MMSoundManager catches, so without one it plays
  nothing; an empty mixer group skips the volume sliders. Adopt
  `MMSoundManager` (its tracks sit on its own mixer) only when music must cross scenes, crossfade or follow a playlist;
  then play it with `Loop` and `Persistent` set in `MMSoundManagerPlayOptions`, on the `Music` track. The trade-off
  and the API are `references/feel-api.md` section 8. Import settings for music (Streaming, Vorbis) are
  `unity-performance`.
- **WebGL starts silent.** A browser keeps audio locked until the first click, tap or key; Unity resumes it on that
  input by itself, so no unlock code is needed, but anything played before it may be lost. Start the music from the
  title screen and put no essential sound before the first input.
- **Pause and interruption.** `Time.timeScale = 0` does not stop audio. On the game's pause and on focus loss (a
  phone call, the app sent to the background; `platform-targets` App lifecycle) set `AudioListener.pause = true`, and
  false on resume; it covers MMSoundManager's pooled sources too, which do not pause themselves. Pause-menu UI sounds
  play from one dedicated `AudioSource` on the UI group with `ignoreListenerPause = true` (through `MMF_AudioSource`
  or a direct `AudioSource.PlayOneShot`), not through `MMF_Sound`, whose runtime-made sources expose no such field and stay muted.
- **Volume survives restarts.** Volumes are settings, so they go in `PlayerPrefs` with the other settings (never the
  progress save, `unity-code-review` item 4), stored 0-1 and applied in `Start`, not `Awake`: `AudioMixer.SetFloat`
  is ignored in `Awake`. On a plain mixer write decibels,
  `mixer.SetFloat("MusicVolume", Mathf.Log10(Mathf.Max(v, 0.0001f)) * 20f)`; with MMSoundManager call
  `SetVolumeMusic(v)` and friends, and turn the settings SO's `AutoSave` and `AutoLoad` off: they write their own
  file through `MMSaveLoadManager`'s BinaryFormatter, a second store and the format item 4 forbids.

## References

- `references/feel-api.md` — `MMF_Player` methods and settings, `MMFeedbackTiming`, channels, events, springs, the
  custom feedback template.
- `references/feedback-catalog.md` (which feedbacks compile here, haptics define per platform) and
  `references/recipes.md` (starting stacks per game event, and a code-side `Haptics` service).
- Official docs: https://feel-docs.moremountains.com/ · API index http://feel-docs.moremountains.com/API/
- Reference scenes shipped with the full asset, present only if the Feel demos were imported (games made by
  `new-game.ps1` copy Feel without them; check with Glob before citing them, and otherwise import the demos from the
  Package Manager's My Assets or use the online docs): `Assets/Feel/MMFeedbacks/Demos/MMFeedbacksDemo/MMF_PlayerDemo.unity`
  (every feedback), `Assets/Feel/FeelDemos/Bounce/FeelBounce.unity` (the same jump with and without feedbacks),
  `Assets/Feel/FeelDemos/Toaster/FeelToaster.unity` (20+ shake variations side by side).
