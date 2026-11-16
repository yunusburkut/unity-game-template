# Feedback recipes for common game events

Each recipe is a feedback stack for one `MMF_Player`, with starting values and the reason for each
number. They are starting points to tune in Play Mode, not final values; the numbers and the
reasoning behind them (durations, squash bands, shake budgets, forgiveness windows) are in the
`game-feel` skill. Pick the recipes for the events the game actually has.

Conventions used throughout:

- Every `MMF_Player` is a `[SerializeField] private` field on the system's `<System>View` in
  `Assets/<Game>/Game/<System>/` (`unity-architecture`, Cross-system communication), fired by polling a simulation edge flag right after the step.
- Target a **visual child**, never the root a controller writes every frame.
- Pass intensity from the simulation: `PlayFeedbacks(position, intensity)`.
- Anything that must survive a freeze frame or a pause gets `TimescaleMode = Unscaled`.
- Camera feedbacks are event-based and need `MMCameraShaker` on a shaker node that the follow
  script does not move (see `feedback-catalog.md`, Camera).
- On the Mobile tier, shake less (the screen is in the player's hand; the mechanism is SKILL.md, *Shake less on a
  phone*) and cut particles first.

## Contents

- §1 Jump / launch
- §2 Landing / impact
- §3 Dash / burst of speed
- §4 Bump into a wall or ceiling
- §5 Death, fail and respawn
- §6 Interact: available, accepted, refused
- §7 Tap, select and drop (touch-first games)
- §8 Match, clear and combo (puzzle games)
- §9 Win / level complete
- §10 UI
- §11 Mobile haptics service
- Composition notes

---

## 1. Jump / launch

Reads as *release of stored energy*. Nothing here may delay the launch: the solver has already
applied the velocity by the time the flag is visible, and no feedback should add wind-up.

| Feedback | Values | Why |
|---|---|---|
| `MMF_SquashAndStretch` on the visual | axis `YtoXZ`, duration 0.10 s, peak Y ≈ 1.2 | Stretch band 1.15–1.3; 60–120 ms so it is gone before the apex |
| `MMF_Sound` | cached mode, pitch random ±1 semitone (0.944–1.059), `MinVolume` 0.8, `MaxVolume` 1.0 (about -2 dB to 0 dB; linear and clamped to 1, so leave headroom in the clip or mixer) | Round-robin pitch is the cheapest fatigue fix |
| `MMF_ParticlesInstantiation` (dust at feet) | pooled, burst 8–12, lifetime 0.4 s | A jump is not an impact; keep it small |
| optional `MMF_CameraShake` | 0.08 s, tiny amplitude | Usually omit: a shake on every jump becomes invisible and costs readability |

Do **not** add a freeze frame or a camera zoom to an ordinary jump.

## 2. Landing / impact

The event where intensity genuinely matters. Scale by speed at impact: normalise it against the
maximum (terminal fall speed, max projectile speed) and pass that as intensity. A small step and a
long fall must not play the same thing.

| Feedback | Values | Why |
|---|---|---|
| `MMF_ScaleSpring` on the visual, mode `Bump` | damping 0.5, frequency 8 | A spring overshoots into a stretch and settles by itself — better than a tween for squash |
| or `MMF_SquashAndStretch` | 0.12 s, peak Y ≈ 0.8 | Squash band 0.7–0.85, 80–150 ms |
| `MMF_Sound` | pitch ±1 semitone, volume scaled by intensity | A soft landing should be quiet, not just shorter |
| `MMF_ParticlesInstantiation` dust | pooled, burst 10–20 scaled by intensity, lifetime 0.6 s | |
| `MMF_CameraShake`, **heavy impacts only** | `UseIntensityInterval` min 0.6, max above 1 (e.g. 1.01; the window is [min, max) and max defaults to 0), 0.15 s | The intensity interval gives "only when it was a real fall" without branching in code |
| `MMF_FreezeFrame`, **only for an impact that matters** | 0.05 s (3 frames at 60 fps) | Needs `MMTimeManager`. Wrong for routine landings |

The cheapest camera win on a platformer is often not a feedback: snap the camera's vertical follow
to the platform on landing instead of tracking the jump arc.

## 3. Dash / burst of speed

A feedback longer than the dash cooldown overlaps itself; keep the stack shorter than it.

| Feedback | Values | Why |
|---|---|---|
| `MMF_SquashAndStretch` on the visual | axis along travel, 0.12 s, peak ≈ 1.25 | Stretch in the direction of motion sells speed |
| `MMF_TrailRenderer` or `MMF_Particles` | enabled for the dash duration | |
| `MMF_Sound` | whoosh, pitch ±1 semitone | |
| optional `MMF_ChromaticAberration_URP` | 0 → peak → 0 over 0.3 s, PC tier only | Needs the shaker on the Volume **and** the override in the profile |

Dash end deserves a separate, quieter player (a small `MMF_ScaleSpring` bump) only if the speed
visibly drops.

## 4. Bump into a wall or ceiling

A bump that silently cancels a move is the classic "the game is broken" report.

| Feedback | Values | Why |
|---|---|---|
| `MMF_Sound` | short dull thud, quiet | Audio alone often suffices |
| `MMF_PositionShake` on the visual | 0.08 s, tiny amplitude | Reads as the body stopping, not the world shaking |
| `MMF_CameraShake` | only above a speed threshold, 0.1 s | |

## 5. Death, fail and respawn

Decide the beat lengths with the design (`game-feel`): a fail that is funny needs a short hold so
the player sees what happened; a fail in a fast retry loop needs to get out of the way.

| Beat | Feedback | Values |
|---|---|---|
| Fail | `MMF_Sound` | descending sting |
| Fail | `MMF_FreezeFrame` (optional) | 0.05–0.1 s, the only place a longer freeze is earned |
| Fail | `MMF_CameraShake` | 0.2 s, medium; half on Mobile (`tuning.MobileShakeScale`, SKILL.md) |
| Hold | none, or a slow `MMF_TimescaleModifier` | 0.3–0.7 s, the time the player needs to read the cause |
| Return | `MMF_Fade` or none | Fast retry loops skip the fade |
| Appear | `MMF_ScaleSpring` bump on the visual | damping 0.5, frequency 10 |

A `CharacterController` must be disabled and re-enabled around a teleport, or it fights the move
(`unity-code-review`).

## 6. Interact: available, accepted, refused

Reserve three distinct players so the states never read the same:

- **Available** — a subtle idle loop on the target: `MMF_ScaleSpring` or `MMF_Wiggle`, very low
  amplitude, or an emissive pulse via `MMF_MaterialSetProperty`. This is state, not an event.
- **Accepted** — the input worked: `MMF_Scale` punch 0.15 s with EaseOutBack, a rising sound, a
  small `MMF_Flash`.
- **Refused** — the input was read but rejected: a different, lower sound plus a 0.1 s
  `MMF_PositionShake` on the target (and a `Warning` haptic on phones). Silence here is the single
  most common puzzle-game feel bug.

Keep all three under 0.25 s. A player repeats these hundreds of times.

## 7. Tap, select and drop (touch-first games)

The finger hides what it touches: feedback has to show *around* the finger and in sound and haptics.

| Event | Feedback | Values |
|---|---|---|
| Select (piece lifts) | `MMF_Position` up + `MMF_Scale` to 1.08 | 0.08–0.12 s, EaseOutBack; offset so the piece clears the fingertip |
| Select | `MMF_Sound` light tick + `Selection` haptic | |
| Invalid target | `MMF_PositionShake` horizontal + low sound + `Warning` haptic | 0.15 s |
| Drop / land | `MMF_ScaleSpring` bump + soft thud + `LightImpact` or `SoftImpact` haptic | damping 0.5, frequency 10 |
| Tap ripple | a pooled ripple sprite or particle at the touch point | 0.25 s; the only feedback the finger cannot hide |

## 8. Match, clear and combo (puzzle games)

| Event | Feedback | Values |
|---|---|---|
| Match | `MMF_Scale` punch on each matched piece, staggered | 0.15 s each, 30–50 ms stagger — the stagger reads as a chain |
| Clear | `MMF_ParticlesInstantiation` burst per piece | pooled, small; cap the total on Mobile |
| Clear | `MMF_Sound` pitch rising with the combo count | +1 semitone per step, capped |
| Combo ≥ N | `MMF_CameraShake` small + `MediumImpact` haptic | Only from the threshold up, so the escalation is felt |
| Board settle | nothing | The quiet after the burst is part of the reward |

## 9. Win / level complete

| Beat | Feedback | Values |
|---|---|---|
| Last move lands | `MMF_FreezeFrame` | 0.08 s |
| Win | `MMF_Sound` fanfare, `Success` haptic | |
| Win | `MMF_ParticlesInstantiation` confetti | pooled; one burst, not a loop |
| Results panel | §10 panel open, delayed 0.4–0.6 s | Let the board moment land before covering it |

## 10. UI

| Case | Feedback | Values |
|---|---|---|
| Panel open / close | `MMF_CanvasGroup` alpha + `MMF_RectTransformOffset` | 0.15–0.2 s, EaseOutCubic, Unscaled |
| Button press | `MMF_Scale` to 0.92 and back; a `Selection` haptic only on confirm / commit buttons, never on every tap (`game-feel` numbers.md section 8) | 0.08–0.12 s, EaseOutBack |
| Value change | `MMF_TextColor` flash + `MMF_TextFontSize` punch | 0.15 s |

All UI feedbacks get `TimescaleMode = Unscaled` (Conventions above). Use the uGUI text feedbacks if the UI uses
`UnityEngine.UI.Text`, the TMP ones if it uses TextMeshPro. A closed panel is disabled, not alpha 0,
so it costs no overdraw on a phone.

## 11. Mobile haptics service

For haptics fired from code rather than from an `MMF_Player` (a solver edge with no visual
feedback, or one place to honour the player's "vibration off" setting), wrap Nice Vibrations'
presets in one small static class in Game. The presets are already tuned per platform — Core
Haptics on iOS, amplitude control on Android — so they beat a raw `Handheld.Vibrate()` buzz, and
they do nothing on PC without a gamepad.

`Assets/<Game>/Game/Feel/Haptics.cs` (needs `"Lofelt.NiceVibrations"` in `<Game>.Game.asmdef`;
`HapticPatterns` does not need the `MOREMOUNTAINS_NICEVIBRATIONS_INSTALLED` define):

```csharp
using Lofelt.NiceVibrations;

namespace <Game>.Game
{
    // Haptics through Nice Vibrations' presets, which are tuned per platform (Core Haptics on iOS,
    // amplitude control on Android). One method per game event, named for the event, so the
    // mapping from event to strength lives in one file.
    public static class Haptics
    {
        // the player setting; HapticController keeps it across Play sessions (domain reload is off),
        // so AppStartup or the settings screen writes it at startup from the saved value
        public static bool Enabled
        {
            get => HapticController.hapticsEnabled;
            set => HapticController.hapticsEnabled = value;
        }

        public static void Select() => HapticPatterns.PlayPreset(HapticPatterns.PresetType.Selection);
        public static void Invalid() => HapticPatterns.PlayPreset(HapticPatterns.PresetType.Warning);
        public static void Land() => HapticPatterns.PlayPreset(HapticPatterns.PresetType.SoftImpact);
        public static void Drop() => HapticPatterns.PlayPreset(HapticPatterns.PresetType.LightImpact);
        public static void Hit() => HapticPatterns.PlayPreset(HapticPatterns.PresetType.RigidImpact);
        public static void Win() => HapticPatterns.PlayPreset(HapticPatterns.PresetType.Success);
        public static void Fail() => HapticPatterns.PlayPreset(HapticPatterns.PresetType.Failure);
    }
}
```

The presets available are `Selection`, `Success`, `Warning`, `Failure`, `LightImpact`,
`MediumImpact`, `HeavyImpact`, `RigidImpact`, `SoftImpact`. Rules of use:

- Rename the methods for the game's events and delete the ones it does not have.
- Light presets for frequent events (select, drop), strong ones for rare events (win, fail). A
  heavy preset on every tap is the fastest way to get vibration turned off.
- Never a continuous rumble; never more than a few haptics per second.
- Fire the haptic in the same frame as the visual feedback it belongs to, or it reads as lag.
- Do not also author an `MMF_NV*` feedback for the same event: one source per event.

---

## Composition notes

- **One player per event**, not one player per object. A `<System>View` holding five
  `MMF_Player` fields is clearer than one player with thirty feedbacks and direction conditions.
- **Sequential vs Parallel**: `PlayMode = Sequential` with `SequentialDelay` is cleaner than
  inserting `MMF_Pause` feedbacks for a beat-by-beat sequence.
- **Overlap policy**: `CanPlayWhileAlreadyPlaying` defaults to true. For a landing that is right
  (rapid landings should retrigger); for a death or win sequence it is wrong.
- **Cooldowns**: `CooldownDuration` on the player guards against an event that can fire many times
  a second. Set it shorter than the game's own cooldown so it never swallows a legitimate play.
- **Budget check**: before adding a fourth simultaneous effect to one event, ask which of the three
  existing ones the player would actually miss. Feel's *Bounce* demo (the same jump with and without
  feedbacks) is worth opening as a calibration reference, and *Toaster* for shake variations; paths and
  when they exist are in SKILL.md, *References*.
