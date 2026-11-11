---
name: feel-authoring
description: Wiring the Feel asset (MMF_Player, feedbacks, shakers, springs, Nice Vibrations haptics, MMSoundManager, MMTimeManager) into the game — which assembly reference to add, where the code goes, how the view reads simulation edge flags, and how mobile haptics fit in. Use when adding or changing any juice, screen shake, hit stop, particle, sound or vibration feedback, or when deciding whether an effect belongs in Core, Game, a config asset or the scene. A feedback that misbehaves is feel-troubleshooting.
---

# Using Feel

Feel (More Mountains) lives at `Assets/Feel`, a vendored paid package (committed in private game repos, gitignored in
older ones); it includes Nice Vibrations.
The full code-facing API is `references/feel-api.md`.

## Step zero: the assembly reference

Feel ships **no `MoreMountains.Feedbacks` assembly**. Every MMFeedbacks folder carries an `.asmref` pointing at
`MoreMountains.Tools`, so all feedbacks, shakers, springs and `MMSoundManager` compile into that one assembly.

The first time Game uses Feel, add `"MoreMountains.Tools"` to `Assets/<Game>/Game/<Game>.Game.asmdef`. Haptics
(`MMF_NV*` feedbacks, `MMVibrationManager`) also need `"Lofelt.NiceVibrations"`. `<Game>.Core` never gets either:
if a Feel type is needed in Core, the design is wrong.

## What compiles

`MoreMountains.Tools.asmdef` turns feedback families on from the package manifest: URP post-process feedbacks
(`_URP` variants), uGUI and TMP (`ugui` 2.x ships TMP), Input System, Physics2D are on. Cinemachine, PPv2, HDRP and
VFX Graph feedbacks do not exist here; most Feel tutorials reach for Cinemachine impulses, use `MMF_CameraShake` with
an `MMCameraShaker` instead. Do not add a package to turn a family on without asking.

## Where the code goes

The simulation does not know presentation exists (`unity-architecture`). The channel is the solver's one-step edge
flags (`Landed`, `Matched`, `Cleared`), reset at the top of every step: the view polls them right after stepping and
plays a feedback. Continuous values (speed, combo count) are read the same way for intensity.

Practically: a `<Thing>Feel` MonoBehaviour in `Assets/<Game>/Game/Feel/` holding serialized `MMF_Player` fields, fed
by the controller after it steps. Do not grow a feedback field per event on the controller itself; do not look up an
`MMF_Player` in a per-frame path.

Scale intensity from the simulation rather than hardcoding it: `PlayFeedbacks(position, intensity)` takes it
directly. Timings and intensities live in one ScriptableObject or in the `MMF_Player`, never as literals in code.

Any static you add (a mute toggle, a "haptics off" switch) needs a
`[RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.SubsystemRegistration)]` reset, or it survives into the next
Play session.

## PC and mobile

- **Haptics are mobile only.** `MMF_NVPreset` / `MMF_NVEmphasis` on the same `MMF_Player` as the visual feedback;
  Nice Vibrations does nothing on PC, so no `#if` is needed. Keep a player setting to turn them off, and keep them
  short: a light preset for taps, a medium one for a win, never a continuous rumble.
- **Shake less on a phone.** The screen is in the player's hand and close to the eyes: scale camera shake by a tuning
  value per tier rather than authoring two players.
- **Hit stop** (`MMF_FreezeFrame`) needs an `MMTimeManager` in the scene and makes input timers that run on scaled
  time swallow presses; run those unscaled.
- **Particles** are the first thing to cut on the Mobile tier (`unity-performance`).

## References

- `references/feel-api.md` — `MMF_Player` methods and settings, `MMFeedbackTiming`, channels, events, springs, the
  custom feedback template.
- `references/feedback-catalog.md` (which feedbacks compile here, haptics define per platform) and
  `references/recipes.md` (starting stacks per game event, and a code-side `Haptics` service).
- Official docs: https://feel-docs.moremountains.com/ · API index http://feel-docs.moremountains.com/API/
- Reference scenes shipped with the asset: `Assets/Feel/MMFeedbacks/Demos/MMFeedbacksDemo/MMF_PlayerDemo.unity`
  (every feedback), `Assets/Feel/FeelDemos/Bounce/FeelBounce.unity` (the same jump with and without feedbacks),
  `Assets/Feel/FeelDemos/Toaster/FeelToaster.unity` (20+ shake variations side by side).
