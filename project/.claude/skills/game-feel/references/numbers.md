# Game feel: numeric reference

Confidence tag on every row:

- `[SRC]` published primary source or open-sourced game code
- `[COMM]` community measurement, datamine or practitioner blog
- `[CONV]` widely repeated convention with no single authority
- `[EX]` an example starting value from design literature, not a measurement

URLs for all of these are in `sources.md`, in the same section order.

Frame conversions at 60 fps: 1 fr = 16.7 ms · 3 fr = 50 ms · 6 fr = 100 ms · 12 fr = 200 ms. The simulation steps in
`Update` with `dt` clamped (`SimulationStep.Delta`), so author in **seconds**, not frames.

## Contents

- §1 Human response budget
- §2 Platformer forgiveness and jump shape
- §3 Impact feedback
- §4 Secondary motion
- §5 Camera
- §6 Audio
- §7 Input
- §8 Haptics (mobile)
- §9 Accessibility thresholds
- §10 Starting profiles
- §11 If the game is multiplayer: social timing windows

---

## 1. Human response budget

| Stage | Nominal | Range | Tag |
|---|---|---|---|
| Perceptual processor | 100 ms | 50–200 ms | [SRC] |
| Cognitive processor | 70 ms | 30–100 ms | [SRC] |
| Motor processor | 70 ms | 25–170 ms | [SRC] |
| Full perceive → act loop | ~240 ms | — | [SRC] |

Derived rules: response under **100 ms** = comfortable control; ~50 ms = feels like an extension of the hand; over
**240 ms** = real-time control is broken. At 60 fps that allows roughly 5–7 frames of total input-to-pixel latency,
2–3 frames at 30 fps. `[SRC]`

Swink's ADSR framing of a verb: Attack (press → full effect), Sustain (held), Release (let go → back to rest). A jump
cut is the Release stage made visible; a dash is a pure 0 ms Attack. `[SRC]`

---

## 2. Platformer forgiveness and jump shape

### 2.1 Celeste, published constants

Celeste is MIT-licensed, 60 fps fixed step, 320×180, units are pixels and px/s. These are the most reliable published
platformer numbers that exist. `[SRC]`

| Constant | Value | Meaning |
|---|---|---|
| `Gravity` | 900 px/s² | |
| `HalfGravThreshold` | 40 px/s | Below this abs vertical speed, gravity × 0.5: this *is* apex hang |
| `MaxFall` / `FastMaxFall` | 160 / 240 px/s | Terminal, and terminal while holding down |
| `JumpGraceTime` | **0.1 s** | Coyote time |
| `VarJumpTime` | **0.2 s** | Max hold window for variable jump height |
| `JumpSpeed` | −105 px/s | |
| `JumpHBoost` | 40 px/s | Horizontal nudge given on jump |
| `UpwardCornerCorrection` | **4 px** | Head-bump corner correction |
| `MaxRun` / `WalkSpeed` | 90 / 64 px/s | |
| `RunAccel` / `RunReduce` | 1000 / 400 px/s² | ≈0.09 s to top speed, ≈0.22 s to stop |
| `AirMult` | **0.65** | Air control is 65 % of ground control |
| `DashSpeed` / `EndDashSpeed` | 240 / 160 px/s | End speed is 2/3 of dash speed |
| `DashTime` | **0.15 s** | |
| `DashCooldown` | **0.2 s** | |
| `DashCornerCorrection` | 4 px | |
| `DashVFloorSnapDist` | 3 px | Ground snap distance |
| `WallJumpForceTime` | 0.16 s | Input lockout after a wall jump |
| `ClimbNoMoveTime` | 0.1 s | |

Community wikis cite "5 coyote frames": the constant is 0.1 s (6 frames) and the usable window after leaving the
ground is 5. Author 0.1 s, describe it as 5–6 frames. `[COMM]`

### 2.2 Forgiveness windows, general

| Window | Range | Failure mode outside it | Tag |
|---|---|---|---|
| Coyote time | 0.08–0.15 s | Over 0.2 s reads as floaty and cheaty; under 0.05 s is imperceptible | [CONV] |
| Jump buffer | 0.08–0.20 s | Over 0.25 s causes unwanted jumps on landing | [CONV] |
| Dash buffer | 0.10–0.15 s | | [CONV] |
| Attack buffer | 0.20–0.30 s | | [CONV] |
| Corner correction | ~4 px at Celeste scale | | [SRC] |

Precision and puzzle games lean to the generous end. In multiplayer, cap any forgiveness that one player's input
grants another at ~0.15 s: past it, one player's grace becomes the other's surprise. `[CONV]`

### 2.3 Jump shape

| Technique | Value | Tag |
|---|---|---|
| Fall gravity vs rise gravity | × 1.5–2.5, 2.0 is the safe default | [CONV] |
| Jump cut (button released while rising) | × 2.0–3.0 extra gravity, or a one-shot `vy *= 0.4–0.5` | [CONV] |
| Apex hang | gravity × 0.5 while abs vy is under ~4–8 % of launch speed | [SRC] |
| Mario, past apex | gravity × 3 | [SRC] |
| Variable-height hold window | 0.2 s | [SRC] |

Pittman's derivation, for designing a jump from level geometry rather than from physics: pick peak height `h`, time to
peak `t_h`, and horizontal distance to peak `x_h`, then `g = -2h / t_h²`, `v0 = 2h / t_h`, `t_h = x_h / v_x`. A good
jump is several parabolic arcs with different `g` stitched together with continuous position and velocity, which is
exactly what rise/fall/cut/apex multipliers produce. `[SRC]`

Reach is horizontal speed × air time. Slowing the vertical makes a jump read as slow motion; to calm a game, slow the
ground speed and keep the arc. `[CONV]`

### 2.4 Super Mario Bros., what is actually documented

16 subpixels per pixel · hard speed cap of 4 px/frame that the engine depends on · max walk to max run is 3:5 · jump
launch velocity scales with current run speed · holding A reduces gravity while rising. Exact hex constants exist only
in the disassembly and are not citable. `[COMM]`

---

## 3. Impact feedback

### 3.1 Hit stop

| Context | Duration | Tag |
|---|---|---|
| Final Fight | 6 frames, universal | [COMM] |
| Captain Commando | 8 frames | [COMM] |
| Melee hitlag | floor(damage/3 + 3), capped at 20 fr | [COMM] |
| Ultimate hitlag | (damage × 0.65 + 6) × modifiers, capped at 30 fr | [COMM] |
| Dead Cells critical | **1 frame** hard freeze, then a few tenths of slow motion | [SRC] |
| Action game convention | 0.05–0.15 s (3–9 fr) | [CONV] |

Hit stop of 1–8 frames reads as *impact and weight* and is short enough to keep input responsive. Slow motion at time
scale 0.1–0.3 for 0.1–0.4 s with an eased return reads as *significance*, and should be rare. Dead Cells chains them,
freeze then slow motion, for crits only.

Rules that matter more than the number: run camera shake and input buffering on **unscaled** time during the freeze,
and rate-limit rather than sum hit stops when several land in the same frame.

An empirical study of impact feel across 19 features found hit stop, sound coherence and camera control to be the three
whose absence most reliably ruins perceived impact. `[SRC]`

### 3.2 Screen shake: trauma model

```
trauma in [0,1], additive, clamped
trauma += 0.15 small / 0.35 medium / 0.6 large
trauma -= decay * dt            // decay ~0.5-1.0 per second
shake   = trauma * trauma       // or trauma^3

roll    = maxRoll   * shake * perlin(seed0, t)
offsetX = maxOffset * shake * perlin(seed1, t)
offsetY = maxOffset * shake * perlin(seed2, t)
```

Why squared: `[SRC]`

| trauma | shake |
|---|---|
| 0.3 | 9 % |
| 0.6 | 36 % |
| 0.9 | 81 % |

(Cubed: 3 %, 22 %, 73 %.)

| Parameter | Value | Tag |
|---|---|---|
| Duration, typical hit | 0.1–0.3 s | [CONV] |
| Unreadably short | ≤ 30 ms | [COMM] |
| Reads as blur | ≥ 150 ms for an ordinary hit | [COMM] |
| Amplitude, weak hit | 2–3 px equivalent | [COMM] |
| Amplitude, strong hit | 8–10 px equivalent | [COMM] |
| Noise frequency band | ~20–40 Hz | [CONV] |
| Suggested caps for a 3D rig | max translation (1,1,1), max angular (15,15,10)° | [COMM] |
| Feel `MMF_CameraShake` default | duration 0.1, amplitude 0.2, frequency 40 | [SRC] |
| Feel camera shake *recipe* | duration 0.3, amplitude 2, frequency 40 | [SRC] |
| Feel UI shake recipe | duration 0.5, amplitude 20, frequency 0.03 | [SRC] |
| Feel `MMShaker.ShakeDuration` default | 0.2 s | [SRC] |

Use noise, never per-frame uniform random. In 3D and with a perspective camera prefer rotation-dominant shake: Eiserloh
recommends rotation-only in 3D, and a perspective camera translating sideways exposes the background parallax. On a
phone, shake less: the screen is held close to the eyes. `[CONV]`

### 3.3 Flash, particles, post-FX, ordering

| Effect | Value | Tag |
|---|---|---|
| White hit flash | 50–100 ms | [COMM] |
| Invulnerability blink | ~10 Hz, but never more than 3 screen-filling flashes/s | [CONV] |
| Particle burst per hit | 20–30 particles (fewer on the Mobile tier) | [COMM] |
| Particle lifetime | 0.5–1.0 s | [COMM] |
| Damage / value text | rise and fade over 1–2 s, EaseOutQuad, 0.8 s in dense combat | [COMM] |
| Chromatic aberration pulse | 0 → peak → 0 over ~0.3 s for hits | [COMM] |
| Feel `MMF_Flicker` default | duration 0.2 s, period 0.04 s (≈5 flickers), colour (255,20,20) | [SRC] |

Published ordering for a single impact: rumble or haptic and sound at t=0, flash at +20 ms, particles at +50 ms,
floating number at +100 ms. Audio-to-haptic sync error must stay under 12–15 ms. `[COMM]`

---

## 4. Secondary motion

### 4.1 Squash and stretch

| Use | Magnitude | Duration | Tag |
|---|---|---|---|
| Jump take-off stretch | Y 1.15–1.3 | 60–120 ms | [CONV] |
| Landing squash | Y 0.7–0.85 | 80–150 ms, settle with overshoot | [CONV] |
| Hard landing, scaled by impact speed | down to Y 0.6 / up to 1.6 | 150–250 ms | [CONV] |
| General juice band | 10–30 % deformation | — | [CONV] |
| Button / tile press | scale 0.92, 80–120 ms | — | [COMM] |
| Volume preservation in 3D | scale Y by n ⇒ X and Z by 1/sqrt(n) | — | [SRC] |

A damped spring beats a one-shot tween here: the squash overshoots into a stretch and settles on its own. Spring feel:
damping ratio 0.4–0.6 for visible bounce, 0.7–1.0 for a quick settle.

### 4.2 Anticipation and follow-through

| Beat | Frames @60 | Tag |
|---|---|---|
| Anticipation on a *player* action | 0–4 fr (0–66 ms) | [CONV] |
| Anticipation on an *enemy/hazard* telegraph | 12–30 fr (0.2–0.5 s); must exceed the 240 ms response window | [SRC-derived] |
| Impact / smear frame | 1–2 fr, held during hit stop | [CONV] |
| Follow-through settle | 6–18 fr (0.1–0.3 s), EaseOutBack or Elastic | [CONV] |

### 4.3 Easing per use

| Easing | Use | Duration | Tag |
|---|---|---|---|
| EaseOutCubic | Panel slide, general arrival | 0.30 s | [SRC] |
| EaseOutQuad | Camera follow, damage numbers, arcs | 0.4–0.8 s | [SRC] |
| EaseOutBack | Button press, tactile pop | 0.15 s | [SRC] |
| EaseOutBounce | Object landing, placement | 0.40 s | [SRC] |
| EaseOutElastic | Reveal, dramatic wobble | 0.60 s | [SRC] |
| EaseInOutSine | Loops, idle rotation | 1.0 s | [SRC] |
| EaseInQuad | Things leaving or falling out | 0.2–0.4 s | [SRC] |
| Linear | Only constant-rate things: conveyors, timers | — | [CONV] |

Default to ease-out. Ease-in-out 200–500 ms. Bounce and elastic 0.6–1.2 s, used sparingly. EaseOutBack's standard
overshoot constant 1.70158 produces roughly 10 % overshoot.

All of these exist in the project's own `Ease` enum (`Assets/__GAME__/Core/Ease.cs`): `Linear`, `SineIn/Out/InOut`,
`QuadIn/Out/InOut`, `CubicIn/Out/InOut`, `QuartIn/Out`, `QuintIn/Out`, `ExpoIn/Out/InOut`, `CircIn/Out`, `BackIn`,
`BackOut`, `ElasticOut`, `BounceOut`. Back and Elastic deliberately leave the 0–1 range.

### 4.4 UI tween durations

| System | Values | Tag |
|---|---|---|
| Material Design 3 tokens | 50 / 100 / 250 / 300 / 450 / 500 ms | [SRC] |
| MD3 standard easing | cubic-bezier(0.2, 0, 0, 1) | [SRC] |
| Common three-tier tokens | fast 150 / medium 300 / slow 600 ms | [CONV] |
| In-play game UI | 0.10–0.25 s | [CONV] |
| Overshoot amount | 5–20 % | [CONV] |

---

## 5. Camera

### 5.1 Smoothing

Asymptotic averaging, `x += (target - x) * w`, is the cheap workhorse. Blend-weight feel at 60 fps: 0.01 = very heavy,
0.10 = a good default, 0.50 = nearly snapped. The frame-rate-correct form is `t = 1 - pow(1 - w, dt * 60)`. Unity's
`Vector3.SmoothDamp` with `smoothTime` 0.05–0.3 s is the same idea with a velocity term. `[SRC]`

| Parameter | Value | Tag |
|---|---|---|
| Follow smoothTime, X | 0.15–0.3 s | [CONV] |
| Follow smoothTime, Y | 0.05–0.15 s, or platform-snap instead | [CONV] |
| Dead zone, normalized width | 0.1–0.2 | [COMM] |
| Look-ahead distance | 0.5–2.0 × player height, scaled by speed | [CONV] |
| Look-ahead smoothing | 0.2–0.5 s; it must lag, or it induces nausea | [CONV] |
| Landing camera lag | fall behind 0.05–0.1 s, then catch up | [CONV] |
| FOV punch on dash | +2–10°, in over 0.05–0.1 s, out over 0.2–0.4 s | [CONV] |
| Feel `MMF_CameraZoom` default | FOV 30, transition 0.05 s, hold 0.1 s | [SRC] |

### 5.2 Keren's side-scroller camera taxonomy

The techniques worth knowing for a side view, from *Scroll Back*: `[SRC]`

- **Camera window / dead zone**: the camera only moves when the player reaches the window edge. Rastan sized the window
  to exactly one standard jump so routine jumping never scrolls the view.
- **Platform snapping**: the camera's Y only follows when the player *lands*, ignoring jump arcs. The single most
  important trick for platformers, and cheaper than any smoothing tweak.
- **Lerp smoothing** vs **physics smoothing**: ease-out versus ease-in-out; the latter gives the camera its own inertia.
- **Dual forward focus**: the lead offset flips with facing, switching at roughly 2× player speed.
- **Region focus**: per-room anchors blended with player position; Celeste's model and the natural fit for room-based
  games.
- **Projected focus (look-ahead)** is explicitly noted as ineffective for vertical platforming.

In multiplayer with a shared camera, frame the whole group (containment), and cap the spread by level design rather
than by zooming out.

---

## 6. Audio

| Parameter | Value | Tag |
|---|---|---|
| Pitch randomization, recommended | 0–2 semitones total (≈ ±1 st ⇒ ×0.944–1.059) | [SRC] |
| Pitch randomization, common in engines | ±5–15 % | [CONV] |
| Volume randomization | ±1–3 dB | [CONV] |
| Round robin | 3–8 variants, shuffled, never repeating back to back | [SRC] |
| Impact layer structure | transient + body + tail | [SRC] |
| Transient | 1–20 ms attack, broadband; this is what conveys impact | [SRC] |
| Body | 50–300 ms, material character | [SRC] |
| Tail | 200 ms–2 s, conveys the space | [SRC] |
| Sub-bass weight layer | 40–120 Hz, sidechained so it doesn't mask the transient (inaudible on phone speakers) | [SRC] |
| Ducking on impact | −3 to −6 dB, attack 5–20 ms, release 150–400 ms | [CONV] |
| Audio ↔ haptic sync tolerance | < 12–15 ms | [COMM] |

Fire audio on the same frame as, or before, the visual. Audio latency is what players perceive as input lag. Many
phone players play muted: every event must still read without sound.

---

## 7. Input

| Budget | Value | Tag |
|---|---|---|
| Button to pixel, ideal | < 50 ms | [CONV] |
| Acceptable | < 100 ms | [SRC] |
| Broken | > 240 ms | [SRC] |
| Perceptible difference in twitch genres | 10–20 ms | [COMM] |
| Unity `FixedUpdate` default | 0.02 s (50 Hz) | [SRC] |
| Press-vs-hold threshold | ~0.2 s (Unity's `Hold` default is 0.4 s; lower it) | [CONV] |

Read presses in `Update`, latch to a bool, consume where the simulation steps, and expire the latch at the buffer
window rather than "next step", so a press is never silently eaten. Stepping the simulation in `Update` (as this
template does) avoids the `FixedUpdate` press-loss trap. On touch, acknowledge on press, act on press for verbs and on
release only for UI that can be cancelled by dragging off.

---

## 8. Haptics (mobile)

Nice Vibrations ships inside Feel (`MMF_NVPreset`, `MMF_NVEmphasis`, `MMF_NVContinuous`) and does nothing on PC.

| Rule | Value | Tag |
|---|---|---|
| Transient vs continuous | Transient for discrete events (tap, hit, land); continuous only for a held state, and rarely | [SRC] |
| Presets | Selection / light impact for taps; success, warning, failure for outcomes; medium and heavy impact for notable and rare events | [SRC] |
| Parameters | Intensity and sharpness are 0–1; sharpness separates a crisp click from a dull thud | [SRC] |
| Sync with audio | < 12–15 ms | [COMM] |
| Budget | One haptic per meaningful event; none on scroll, hover or every UI tap | [CONV] |
| Platform difference | iOS Core Haptics renders intensity and sharpness; Android support varies by device (amplitude control on newer devices, on/off buzz on old ones). Test on a low-end Android | [SRC] |
| Setting | A haptics on/off switch in settings, read before every play | [CONV] |

Evidence that it helps: Singhal & Schneider (CHI 2021) found vibrotactile embellishment improved player experience in a
phone game. `[SRC]`

---

## 9. Accessibility thresholds

| Rule | Threshold | Tag |
|---|---|---|
| WCAG 2.x SC 2.3.1 | No more than 3 flashes in any 1-second period | [SRC] |
| WCAG small-area safe harbour | Flashing area under ~25 % of a 10° visual field | [SRC] |
| Xbox AG 118, luminance | ≥10 % luminance change with the darker value below 0.8 is a flash | [SRC] |
| Xbox AG 118, frequency | more than ~3 flashes/second fails | [SRC] |
| Xbox AG 118, area | flash covering ≥ ~20 % of screen fails | [SRC] |
| Xbox AG 118, red | saturated red where R/(R+G+B) ≥ 0.8 | [SRC] |
| Prevalence | ~1 in 4000 people are photosensitive | [SRC] |

Ship 0–100 % sliders rather than on/off toggles for screen shake, motion blur, full-screen effects and rumble; a global
"reduce motion" that damps camera smoothing and zeroes shake is the documented reference implementation.

---

## 10. Starting profiles

Not authority: defensible starting points assembled from the tables above, to be tuned in Play Mode. Write the tuned
values into the game's config assets and note them in `DESIGN.md`.

### 10.1 Side-view or 2.5D platformer

```yaml
jump:
  variableJumpWindow:  0.20 s
  riseGravityScale:    1.0
  fallGravityScale:    1.5 -> 2.5 (ramped)
  jumpCutMultiplier:   2.0-3.0
  apexHang:            gravity x 0.5 under ~8 % of launch speed
forgiveness:
  coyoteTime:          0.12 s
  jumpBuffer:          0.12-0.15 s
  groundSnap:          ~0.1 m
dash:
  duration:            0.15 s
  cooldown:            0.20 s
  endSpeed:            0.66 x dashSpeed
camera:
  followSmoothTimeX:   0.20 s
  followSmoothTimeY:   platform-snap on land, else 0.30 s
  lookAhead:           1.2 x player height, smoothing 0.35 s
  fovPunchOnDash:      +4 deg, in 0.06 s, out 0.30 s
  shake:               trauma^2, decay 1.0/s, maxRoll 2.5 deg, maxOffset 0.12 m,
                       perlin ~25 Hz, unscaled time
feedback:
  hitStopLight:        0.05 s
  hitStopHeavy:        0.10 s
  whiteFlash:          0.07 s
  landSquash:          Y 0.80 -> 1.0, spring damping 0.5, frequency 8
  jumpStretch:         Y 1.20 -> 1.0 over 0.09 s
  particlesPerImpact:  18-26 (PC), about half on the Mobile tier, lifetime 0.6 s
audio:
  pitchRandom:         +/- 1 semitone
  volumeRandom:        +/- 2 dB
  roundRobin:          >= 4 variants
  duckOnImpact:        -4 dB, attack 10 ms, release 250 ms
```

### 10.2 Tap-driven mobile puzzle or casual game

```yaml
press:
  acknowledge:         on the press frame, scale 0.92 over 0.08 s, release EaseOutBack 0.15 s
  sound:               short click, pitch +/- 1 semitone, round robin >= 3
  haptic:              selection or light impact preset
validMove:
  motion:              EaseOutCubic 0.20-0.30 s
  settle:              EaseOutBack or a spring, 0.10-0.20 s
invalidMove:
  objectShake:         object-local, 0.2-0.3 s, never the camera
  haptic:              warning or failure preset
chain / combo:
  pitchStep:           +1 semitone per link, reset on break
levelComplete:
  successBreath:       0.3-0.5 s quiet settle, then the largest stack in the level
  haptic:              success preset
ui:
  panelSlide:          EaseOutCubic 0.25-0.30 s
  flashes:             <= 3 per second
```

---

## 11. If the game is multiplayer: social timing windows

Individual input timings stay as above. These are the windows *between* players. All are `[EX]` starting values from
co-op design literature: start there, tune in Play Mode, write the result back.

| Window | Starting value | Notes |
|---|---|---|
| Recoverable failure: mistake → next decision | 3–8 s | A mistake that is fixed in place, not a restart |
| Comeback / catch window | ~2 s | Floor 240 ms; ≥ 1 s if two machines must agree |
| Two-player reset (crank, re-grab) | ~3 s | Long enough to cost, short enough not to be labour |
| Synchronised commitment (everyone presses within) | ~1 s | Server-tolerant; never frame-tight |
| Input echo / delayed replay | ~2 s, telegraphed | Show the pairing and the delay |
| Control debt (a strong move lends a control) | ~5 s | Short and recoverable |
| Expiring state (bridge, door) | 4–5 s with a visible timer | |
| Remote operator lag | 2–5 s | Only as a designed delay, never as netcode |
| Any call a beat needs | < 3 s to say | One word or one gesture |
| Clip: setup → payoff | 5–10 s | Muted, a stranger follows it |
| Delayed consequence | ≤ ~10 s, with a visible trace | Past that, the cause is forgotten |
| Ownership lockout after a transfer | ~0.5 s | Stops churn |

**Latency rule:** any window that needs two machines to agree is **≥ 1 s**. A 150 ms one-way connection is a ~300 ms
round trip, and 1 s is about three of those.
