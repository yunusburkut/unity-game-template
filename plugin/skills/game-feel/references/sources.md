# Game feel — sources and confidence

Section numbers match `numbers.md`.

## Contents

- §1 Human response budget, foundations
- §2 Platformer physics
- §3 Impact feedback
- §4 Animation, easing, UI
- §5 Camera
- §6 Audio
- §7 Input
- §8 Haptics
- §9 Accessibility
- §11 Social timing windows and the feedback hierarchy
- Known gaps — do not present these as authoritative

## 1. Human response budget, foundations

- Swink, *Game Feel*, chapter 1 (PDF) — http://mycours.es/gamedesign2014/files/2014/10/Game-Feel-Steve-Swink-chapter-1.pdf
- Overview — https://en.wikipedia.org/wiki/Game_feel · https://lizengland.com/blog/review-game-feel-by-steve-swink/
- ADSR of input, the 240 ms model, per-frame latency budgets — https://gamedesignframework.net/designing-game-controls/ · https://www.gamedeveloper.com/design/designing-game-controls
- Designing Game Feel: A Survey — https://arxiv.org/pdf/2011.09201

Juice technique lists, used throughout:

- Jonasson & Purho, *Juice It or Lose It* — colour, tweening, scaling and squash/stretch, SFX, music,
  particles, screen shake, personality. https://www.richtaur.com/GameDevTreasure/post/juice-it-or-lose-it/ ·
  https://cobble.games/wise-inspiring-smart/game-design/juice-it-or-lose-it ·
  https://abagames.github.io/joys-of-small-game-development-en/make_game_juicy.html
- Nijman (Vlambeer), *The Art of Screenshake* — the ~31 iterative steps, from lower enemy HP and
  bigger bullets through hit pause, permanence, camera lerp, camera offset toward aim, screen shake,
  knockback and consequence. https://www.youtube.com/watch?v=AJdEqssNZ-U ·
  https://theengineeringofconsciousexperience.com/jan-willem-nijman-vlambeer-the-art-of-screenshake/
  Reimplementations with measured values: https://www.bloodirony.com/blog/the-art-of-screenshake-in-unity2d ·
  https://github.com/mingrui/ShotgunTom · https://www.bluetengu.com/2014/12/12/art-of-screenshake-experiments/
  The one hard number Nijman states is a 20 ms blocking sleep on enemy death. `[COMM]`

## 2. Platformer physics

- Celeste source (MIT) — https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs ·
  https://deepwiki.com/NoelFB/Celeste/2.3-player-movement-and-physics · https://celeste.ink/wiki/Tech
- Pittman, *Math for Game Programmers: Building a Better Jump* (GDC 2016) —
  https://archive.org/details/GDC2016Pittman · https://www.youtube.com/watch?v=hG9SzQxaCm8 ·
  http://www.mathforgameprogrammers.com/gdc2016/GDC2016_Pittman_Kyle_BuildingABetterJump.pdf
- GMTK Platformer Toolkit (30+ tunables, no published defaults) — https://gmtk.itch.io/platformer-toolkit
- Coyote time background — https://www.thealmightyguru.com/Wiki/index.php?title=Coyote_time ·
  https://gamerant.com/celeste-coyote-time-mechanic-platforming-impact-hidden-mechanics/
- Jump implementation practice — https://gamedevbeginner.com/how-to-jump-in-unity-with-or-without-physics/ ·
  https://pavcreations.com/jumping-controls-in-2d-pixel-perfect-platformers/ ·
  https://error454.com/2013/10/23/platformer-physics-101-and-the-3-fundamental-equations-of-platformers/
- Super Mario Bros. — https://tasvideos.org/GameResources/NES/SuperMarioBros ·
  https://www.speedrun.com/smb1/guides/pbl9d · https://hypertextbook.com/facts/2007/mariogravity.shtml

## 3. Impact feedback

- Eiserloh, *Math for Game Programmers: Juicing Your Cameras With Math* (GDC 2016), the trauma model
  and asymptotic averaging — https://archive.org/details/GDC2016Eiserloh ·
  http://www.mathforgameprogrammers.com/gdc2016/GDC2016_Eiserloh_Squirrel_JuicingYourCameras.pdf ·
  https://gdcvault.com/play/1023146/Math-for-Game-Programmers-Juicing
- Perlin shake reference implementations — https://github.com/IronWarrior/UnityCameraShake ·
  https://roystan.net/articles/camera-shake/ ·
  https://www.gamedeveloper.com/business/different-ways-of-shaking-camera-in-unity
- Feel's own shake documentation and defaults — https://feel-docs.moremountains.com/screen-shakes.html ·
  https://feel-docs.moremountains.com/recipes.html
- Hitlag / hitstop — https://www.ssbwiki.com/Hitlag ·
  https://shane-sicienski.com/blog/blog-post-title-one-55pmn ·
  https://critpoints.net/2017/05/17/hitstophitfreezehitlaghitpausehitshit/
- Dead Cells — https://80.lv/articles/interview-with-the-developers-of-dead-cells ·
  https://www.gamedeveloper.com/production/art-design-deep-dive-using-a-3d-pipeline-for-2d-animation-in-i-dead-cells-i- ·
  https://www.gdcvault.com/play/1025788/-Dead-Cells-What-the
- 19-feature impact study (IEEE GEM 2022) — https://arxiv.org/abs/2208.06155
- Numeric feedback breakdown, impact ordering and sync tolerance —
  https://eastondev.com/blog/en/posts/dev/20260521-game-feedback-feel/

## 4. Animation, easing, UI

- https://adammadej.com/posts/202403-squashstretch/ ·
  https://www.animationmentor.com/blog/squash-and-stretch-the-12-basic-principles-of-animation/ ·
  https://rebusfarm.net/blog/squash-and-stretch-in-animation-the-essential-principle-for-lifelike-motion
- https://easings.net/ · https://gamedevcheatsheet.com/easing · https://web.dev/articles/choosing-the-right-easing
- Material Design 3 / Carbon motion tokens — https://v10.carbondesignsystem.com/guidelines/motion/overview/

## 5. Camera

- Keren, *Scroll Back: The Theory and Practice of Cameras in Side-Scrollers* —
  https://www.gamedeveloper.com/design/scroll-back-the-theory-and-practice-of-cameras-in-side-scrollers ·
  https://archive.org/details/GDC2015Keren · https://www.gdcvault.com/play/1022243/Scroll-Back-The-Theory-and
- Cinemachine composer damping and dead zone —
  https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/CinemachinePositionComposer.html
- FOV kick — https://docs.zigurous.com/com.zigurous.camerasystem/manual/fov-kick/ ·
  https://www.theastronauts.com/2019/04/the-secrets-of-fov/
- https://docs.unity3d.com/ScriptReference/Vector3.SmoothDamp.html

## 6. Audio

- https://www.gamedeveloper.com/audio/the-power-of-pitch-shifting ·
  https://andrewmushel.com/articles/sound-effect-variation-in-unity/ ·
  https://giannisakritidis.com/blog/Audio-Random-Container/
- https://sfxengine.com/blog/impact-sound-effect · https://pixflow.net/blog/sound-effects-layering/ ·
  https://morphic.com/resources/how-to/how-to-layer-sound-effects

## 7. Input

- https://docs.unity3d.com/Packages/com.unity.inputsystem@1.12/manual/timing-optimize-fixed-update.html
- https://docs.unity.cn/Packages/com.unity.inputsystem@1.1/api/UnityEngine.InputSystem.InputSettings.html
- https://en.wikipedia.org/wiki/Input_lag · https://electron-shepherd.com/blogs/useful-info/retro-gaming-input-lag-guide

## 8. Haptics

- https://nice-vibrations-docs.moremountains.com/transient-continuous-haptics.html
- https://developer.apple.com/documentation/corehaptics/updating-continuous-and-transient-haptic-parameters-in-real-time
- Apple Human Interface Guidelines, Playing haptics — https://developer.apple.com/design/human-interface-guidelines/playing-haptics
- Android `Vibrator.hasAmplitudeControl` and haptics design principles — https://developer.android.com/develop/ui/views/haptics/haptics-principles
- Singhal & Schneider, CHI 2021 (see §11)

## 9. Accessibility

- https://www.w3.org/WAI/WCAG22/Understanding/three-flashes.html ·
  https://w3c.github.io/wcag21/understanding/three-flashes-or-below-threshold.html
- https://learn.microsoft.com/en-us/xbox/accessibility/xbox-accessibility-guidelines/118 (photosensitivity) ·
  https://learn.microsoft.com/en-us/xbox/accessibility/xbox-accessibility-guidelines/117 (motion options)
- https://gameaccessibilityguidelines.com · https://www.hardingfpa.com/

---

## 11. Social timing windows and the feedback hierarchy

The feedback hierarchy and the `[EX]` social windows come from a game-feel research summary, not from re-read papers.
Its research claims come from these papers; read the paper before quoting a number from it. All studied other genres
(action RPG, arena shooter, research games, phone Breakout).

- Swink, S. *Game Feel: A Game Designer's Guide to Virtual Sensation.* CRC Press, 2009. ISBN 9780123743282.
  Vocabulary, not measurements.
- Kao, D. "The effects of juiciness in an action RPG." *Entertainment Computing* 34 (2020) 100359.
  doi:10.1016/j.entcom.2020.100359. N = 3018; None / Medium / High / Extreme: both ends did worse. Basis for the
  "medium-high band" rule.
- Hicks, K., Dickinson, P., Holopainen, J., Gerling, K. "Good Game Feel: An Empirically Grounded Framework for Juicy
  Design." DiGRA 2018. doi:10.26503/dl.v2018i1.936. Developer survey (n = 17) plus commercial-game analysis.
- Hicks, K., Gerling, K., Dickinson, P., Vanden Abeele, V. "Juicy Game Design: Understanding the Impact of Visual
  Embellishments on Player Experience." CHI PLAY 2019, 185–197. doi:10.1145/3311350.3347171. Embellishment raised
  appeal; effects on competence depended on context.
- Singhal, T., Schneider, O. "Juicy Haptic Design: Vibrotactile Embellishments Can Improve Player Experience in Games."
  CHI 2021. doi:10.1145/3411764.3445463. The evidence for haptics on mobile.

---

## Known gaps: do not present these as authoritative

1. **Hollow Knight, Nuclear Throne, Downwell, Super Meat Boy publish no constants.** Every specific number attributed
   to them is a community estimate.
2. **Super Mario Bros. jump and gravity hex constants** exist only in the disassembly; no citable table was found.
   Only the facts listed in `numbers.md` §2.4 are sourced.
3. **Cinemachine default damping and dead-zone values** are not in the public docs: read them from the Inspector in
   the installed version.
4. **Eiserloh's exact trauma decay rate** is not stated in the slides; the 0.5–1.0 per second range is convention.
5. **The "25 Hz Perlin frequency" figure** for shake is repeated widely in tutorials with no primary source. The
   sourced numbers are Feel's frequency 40 and the ~40 Hz haptic figure.
6. **Android haptic quality** varies by device and is not documented per model; test on real low-end hardware.
7. `mathforgameprogrammers.com` PDFs have had TLS failures; use the archive.org mirrors.
