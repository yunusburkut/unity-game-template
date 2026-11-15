---
name: feel-authoring
description: Use when adding or changing juice, shake, hit stop, particles, sound or vibration ("juice ekle", "titreşim") - wiring Feel (MMF_Player, shakers, Nice Vibrations) into the game. A feedback that misbehaves is feel-troubleshooting.
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
  on PC Nice Vibrations only rumbles a connected gamepad, so no `#if` is needed. Keep a player setting to turn them
  off (`HapticController.hapticsEnabled`, which covers phone and gamepad alike), and keep them
  short: a light preset for taps, a medium one for a win, never a continuous rumble.
- **Shake less on a phone.** The screen is in the player's hand and close to the eyes: scale camera shake by a tuning
  value per tier rather than authoring two players.
- **Hit stop** (`MMF_FreezeFrame`) needs an `MMTimeManager` in the scene and does not eat presses as long as input
  is read in `Update` and buffer/coyote timers count the simulation's scaled step (`SimulationStep.Delta`), so they
  pause with the freeze; unscaled time is for camera shake and UI (`game-feel` references/numbers.md section 3.1).
- **Particles** are the first thing to cut on the Mobile tier (`unity-performance`).

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
