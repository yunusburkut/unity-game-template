---
name: game-feel
description: Feels floaty or slow ("his yok", "tok değil", "juice ekle"), adding polish, before any feedback: how an action should feel, with numbers for hierarchy, timing, forgiveness, easing, shake, hit stop, camera, audio, VFX, haptics. Wiring: feel-authoring.
---

# Choosing how the game feels

The genre sets the band before any number is picked. Name it from `DESIGN.md`:

- **Precision games** (platformer, real-time or timing puzzle, rhythm): forgiveness windows at the generous end, shake
  and hit stop at the quiet end, nothing steals control to play an animation.
- **Impact games** (brawler, action, shooter): hit stop, shake and flash carry the weight; still capped (below).
- **Tap games** (mobile casual, turn-based or tap puzzle, idle): the press itself is the verb. UI pop, sound and a
  light haptic on the press frame matter more than any camera effect.

A puzzle game is Precision when a clock or a moving hazard can beat the player, and Tap when nothing moves until the
player acts (match-3, sliding, sorting, most mobile puzzles). A brawler's numbers are wrong in a puzzle game even when
they are correct numbers.

All the concrete values live in `references/numbers.md`: before picking a duration or magnitude, read the section for
the event, not the whole file (Contents at its top; the table below names the section per event, and starting
profiles for platformer, tap puzzle, dodge roll, rhythm and impact games are in `references/numbers.md` §10). Sources
and confidence levels are in `references/sources.md`; the layers, patterns and anti-patterns are in
`references/feedback-stack.md`. Never invent a number that sounds plausible: take it from the reference, from the
game's tuning ScriptableObject, or say it is a starting guess to tune in Play Mode. When the band leaves 2+ real
profiles for a new action (a quiet or a punchy hit, two easings), the user picks on a decision page that plays each
one side by side, before it is wired (`${CLAUDE_PLUGIN_ROOT}/skills/pipeline/references/decision-page.md`).

## The one budget that outranks everything

A player-initiated action must show a visible response within **100 ms**, and the whole perceive-decide-act loop a
human can close is about **240 ms**. Every feel decision is measured against that:

- No anticipation before a player verb. A wind-up on jump, dash or attack is 0–4 frames at most, and usually the
  honest answer is zero: sell the wind-up with squash on frame one instead of delaying the action. A wind-up the
  design deliberately chose is recorded in `DESIGN.md`; do not flag it.
- Hazard and enemy telegraphs are the opposite: they must exceed 240 ms to be reactable.
- Hit stop on something the player did is capped around 8 frames (133 ms). Longer and the game stops answering.
- A freeze must not eat presses: read input in `Update` (never only in `FixedUpdate`, which stops at time scale 0) and
  count buffer and coyote timers on the simulation's scaled step, so they pause with the freeze. Unscaled time is for
  camera shake and UI, not input timers (`references/numbers.md` §3.1).
- On a phone, touch input and the display add their own latency; that is one more reason to acknowledge on the press
  frame, not on release.

## Which half of the problem is it

Sort the complaint before reaching for a fix, because the two halves live in different assemblies and the wrong fix
makes the problem worse.

- **"It doesn't respond / I fell when I shouldn't have / the jump is floaty"** is simulation. Fix it in the Core config
  and step function, in seconds and units per second. Particles on a mushy jump do not fix the jump.
- **"It has no impact / the landing feels like nothing / the hit doesn't read"** is presentation. The simulation is
  right and the player cannot see it. Fix it with feedbacks in `<Game>.Game` (`feel-authoring`). The view reads the
  simulation's one-step edge flags (landed, hit, collected); those flags are the only channel from Core to the view.
- **"It's hard to tell what happened"** is usually neither: it is readability. Check contrast, silhouette, and whether
  an effect covers the thing it announces. Wording and hints are `player-clarity`.

## Feedback is a hierarchy, not a checklist

The order is **mechanic clarity > readable state change > meaningful feedback > decorative juice.** Polish never
rescues a weak mechanic: if it is not satisfying with placeholder feedback, the mechanic is the problem.

- **Walk the eight layers** for every important action: intent cue, input acknowledgement, state transition,
  physical consequence, sensory reinforcement, social attribution, recovery window, resolution
  (`references/feedback-stack.md` §3). A layer may be absent on purpose; say which and why.
- **Stay in the band.** Kao 2020 (N = 3018, an action RPG): no juice *and* extreme juice both did worse than
  medium/high on experience, motivation and performance. Aim medium-high, never maximal.
- **Contrast by magnitude.** Tag each action routine (many per minute), notable (a few per minute) or rare (per level).
  Routine verbs may use shake, freeze or bloom at small magnitude; the rare events (the win, the big save, the final
  failure) get the largest. A silent win is a bigger bug than a loud jump.
- **One event, one peak.** Audio, particles, camera, haptics and UI agree on timing and on one light/heavy threshold.
  This skill picks what each sound must do; where the sound file comes from is the game CLAUDE.md `## Art` rule (ask
  the user: own files, a licensed or CC0 pack, an approved generator; never a synthesised placeholder as final; a
  `docs/asset-sources.md` row for anything not ours).
- **Name what each effect communicates** and what breaks if it is removed. Remove anything that fails that question
  first.

## If the game is multiplayer

- **Attribution is a feel job.** A shared-world consequence shows who caused it: the player's colour on the effect, a
  cause tag, a signature for deliberate interference. A blame label names the cause, not only the victim.
- **Ownership changes get a matched pair.** When control or an object changes hands, the outgoing and incoming owners
  get opposite cues.
- **Private stays private.** Anything only one player may know never drives a global effect.
- **A remote body is not your screen.** A mirrored character never fires screen-space effects (FOV, bloom, vignette,
  shake, haptics) on the local player's camera or phone. World-space effects play for every body; screen-space ones
  only for the locally driven one.
- **Celebrate after the authority decides.** Checkpoint, goal and death feedback fire on the confirmed edge, not the
  local guess.
- **Recovery is as loud as failure.** A catch or a save gets its own, smaller pop; a recovery nobody sees does not
  exist.
- **Let the joke land.** A spectacular failure gets a brief hold of the framing (not of time scale) and harmless
  aftermath. Never a long freeze on movement online.
- **Any window two machines must agree on is ≥ 1 s** (about three round trips on a poor connection).

## Durations and magnitudes, at a glance

Full tables with sources in `references/numbers.md`; these are the bands to stay inside. Every value here is a copy
of the `numbers.md` section in the § column, which owns it: retune there first, then here.

| Event | Reach for | § | Notes |
|---|---|---|---|
| Jump launch stretch | Y 1.15–1.3, 60–120 ms | 4.1 | Volume preserving: X and Z by 1/sqrt(Y) |
| Landing squash | Y 0.7–0.85, 80–150 ms | 4.1 | Scale by impact speed; a spring settles better than a tween |
| Button / tap press | scale 0.92, 80–120 ms | 4.1 | On the press frame, EaseOutBack on release |
| Dash start | freeze 0–3 frames, FOV +2–10° | 3.1, 5.1 | Input stays live through the freeze |
| Hit stop, light | 0.05 s (3 frames) | 3.1 | Anything the player initiated |
| Hit stop, heavy | 0.10 s (6 frames) | 3.1 | Rare, meaningful events |
| White flash | 50–100 ms | 3.3 | Counts toward the 3 flashes per second limit |
| Screen shake | ordinary hit 0.1–0.15 s, notable 0.15–0.25 s, rare up to 0.3 s | 3.2 | ≤ 30 ms is unreadable, over 150 ms on an ordinary hit blurs; rotation-dominant with a perspective camera, see below |
| UI tween | 0.10–0.25 s in play, up to 0.3 s in menus | 4.4 | EaseOut by default |
| Value / damage text | 1–2 s rise and fade | 3.3 | EaseOutQuad |
| Coyote time | 0.08–0.15 s | 2.2 | Precision games lean generous |
| Jump / action buffer | 0.08–0.20 s | 2.2 | Over 0.25 s causes unwanted actions |
| Haptic on a tap | the lightest preset | 8 | One per meaningful press, never per frame |

## Screen shake: prefer the trauma model

A per-event `MMF_CameraShake` at small magnitude, as in `feel-authoring`, is fine. When shakes can overlap, use the
trauma model: accumulate `trauma` in 0–1, decay it linearly, drive the offset by `trauma` squared sampled from Perlin
noise. Squaring makes small events nearly invisible and large ones dominant, and the tail dies smoothly. Simultaneous
events add trauma and clamp at 1 rather than stacking full shakes. Never sample uniform random per frame: it reads as a
rendering glitch.

- With a perspective camera, translation-only shake parallaxes the background and gives the trick away: prefer
  rotation (roll) with a small translation component.
- If a follow camera writes its position every `LateUpdate`, the shake composes with that write rather than fighting
  it (`feel-authoring`).
- Shake runs on unscaled time, or a freeze frame stops it mid-swing.
- On a phone the screen is in the hand: scale shake down on the Mobile tier through a tuning value.

## Haptics (mobile)

Nice Vibrations ships inside Feel and does nothing on PC. Treat haptics as the scarcest channel:

- One distinct preset per event class: selection or light impact for a tap, success for a win, warning or failure for a
  wrong move, a heavy impact only for rare events. Never a buzz on every tap, scroll or UI hover.
- Fire the haptic on the same frame as the sound (one practitioner puts the felt drift at ~12–15 ms, `[COMM]` in
  `references/numbers.md` §3.3).
- A player setting turns haptics off, and the game reads it before every play.

## Anti-patterns, with the threshold that defines each

- Rare-event shake on a trivial event, or linear (unsquared) trauma.
- Any freeze longer than ~8 frames on a player action, or one that drops buffered input.
- Effects that hide what they announce: a burst covering the platform you must land on, or the tile you must tap next.
- Full-screen flashes more than 3 times per second.
- Feedback that lasts longer than the cooldown of the action that fires it, so instances pile up.
- Tuning numbers duplicated in code when they belong in the config ScriptableObject.
- A routine verb at rare-event magnitude, or a rare event quieter than a routine one.
- The same sound or haptic for every event class; confetti on every action; every channel stacked on one event.
- Decorative squash or trails that suggest a hitbox or timing that is not real.
- Vibration on every UI interaction.

The full list, with what each looks like, is `references/feedback-stack.md` §6 (FX01–FX10).

## Accessibility is part of the tuning, not a later pass

- No more than 3 flashes in any one second, and no saturated-red flashing.
- Sliders, not toggles, for screen shake and full-screen effects (0–100 %, 100 default), plus a haptics switch.
- The slider scales the shake path only: store each shake's authored base amplitude once, and on every slider change
  set `MMF_CameraShake.CameraShakeProperties.Amplitude = baseAmplitude * slider * mobileShakeScale`. Never multiply in
  place as `feel-authoring` does for the tier ("Shake less on a phone", applied once in `Awake`): re-applying an in-place
  multiply compounds (50 % twice gives 25 %), and applying it only in `Awake` ignores a live slider change. With the
  trauma model above, the same product multiplies the shake code's maximum offset and maximum roll instead, since that
  code never reads `MMF_CameraShake` amplitude. Never route it through `PlayFeedbacks(position, intensity)` or `MMF_Player.FeedbacksIntensity`: that
  intensity scales every feedback on the player (sound, dust, squash, haptics), carries the simulation's impact
  magnitude, and gates `UseIntensityInterval` windows, so a 50 % slider would quieten the landing and drop heavy
  shakes below their interval. `FeedbacksIntensity` is safe only on a player that holds nothing but screen effects.
- Each Feel feedback class has its own static `FeedbackTypeAuthorized`: `MMF_CameraShake.FeedbackTypeAuthorized =
  false` disables that one class, not every screen effect. For the 0 % end of the slider switch off together every
  screen-motion class the game uses (`MMF_CameraShake`, `MMF_CinemachineImpulse`, `MMF_CameraZoom`,
  `MMF_CameraFieldOfView`, `MMF_CameraOrthographicSize`, and `MMF_Flash` under the full-screen-effects slider), and
  reset them in a `SubsystemRegistration` method, since Play Mode domain reload is off.

## Curves: which system for which job

The project has its own `Ease` enum (`Assets/<Game>/Core/Ease.cs`) evaluated by `Easing.Evaluate`, so tuning stays
a plain value type with identical results everywhere.

- Anything the simulation reads (gravity ramps, dash falloff, a timer's curve) uses `Ease` / `Easing`, never
  `AnimationCurve` in a Core struct.
- Pure presentation that Core never reads (a Feel feedback's own curve) may use whatever that library offers.

Default to ease-out for arrivals: a fast start reads as responsive. Elastic and bounce are 0.6–1.2 s effects for rare,
deliberate moments; used often they read as comedy.

## Neighbouring skills

- `feel-authoring`: putting the chosen numbers into an `MMF_Player`; `feel-troubleshooting` when one does nothing.
- `player-clarity`: what a label or hint says and where it sits.
- `level-beat-review`: where in a level the loud moments go.
- `unity-performance`: particles and post-processing cost on the Mobile tier.
