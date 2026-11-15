# Character action

Stylish melee in 3D, with combos, dodges and a rank for style (Devil May Cry, Bayonetta, Sifu). Core
verb: attack, then dodge out of the attack.

**Camera (Unity):** a perspective third-person orbit behind the hero, with a lock-on that keeps the
target in view; a fixed perspective angle per room; an orthographic side view for a 2D version.

## Defaults

- **style-rank**: A rank on screen rises with varied hits and falls when you repeat a move or get hit.
  Each fight ends on a grade. Why: the player is pushed to fight well, not only to win. Break it when:
  the fight is about survival, not show (a grim duel).
- **arena-waves**: Each fight closes you into an arena with a few waves; the last wave is the hardest.
  Why: a fight has a shape, and the last wave tests what it taught. Break it when: enemies roam an open
  world and a fight starts anywhere.

Variety floor (hypothesis): 3 enemy kinds in the first slice, each attacking or moving differently.

## Feel

- **combo-strings**: Taps string a combo, a pause mid-string changes it, and an early press comes out
  the moment the last hit ends (input buffer). Why: the player writes the combo with timing. Break it
  when: there is one attack (a game of the single perfect strike).
- **dodge-cancel**: A dodge comes out of any attack's follow-through and is safe from its first frame.
  A last-moment dodge slows time for a beat. Why: defence never waits for an animation, and a close
  dodge pays. Break it when: a swing commits you on purpose (a heavy duel).
- **launch-juggle**: An uppercut launches an enemy, a jump follows, air hits keep it up. Why: the air is
  a second stage for the combo. Break it when: fights stay on the ground (a stance duel).
- **soft-lock**: Attacks turn you toward the enemy you push toward and close a short gap; one input
  locks the camera on it. Why: the hit goes where the player meant. Break it when: aiming each swing by
  hand is the skill.

## Variants

- **stylish**: long combos, launches, a slowdown on every perfect dodge.
- **duelist**: fewer, tougher enemies; a block at the moment of a hit breaks their guard.
- **mighty**: a hero of great power who sends whole crowds flying.

## Choices that shape the pitch

- **Defence:** dodges (default) · last-moment blocks that break guard · health won back by hitting back.
- **Structure:** a few graded arenas in a row (default) · one boss to master · endless waves for score.
- **Hero:** a sword fighter (default) · bare hands and martial arts · a superhero with powers.
- **View:** behind the hero, orbit (default) · set angles · side-on 2D.
- **Feeling:** the player feels fearless aggression by dodging through a blow and straight into a combo,
  because a close dodge pays and the style rank climbs.

## Platforms

- Keyboard+mouse: WASD move, mouse turns the camera, left and right button for light and heavy attack,
  Space or Shift to dodge. A gamepad fits best.
- Touch (Pointer): a left virtual stick, attack and dodge buttons on the right; swipe to dodge
  *(guess)*. Landscape on phones. The orbit camera is hard on touch; prefer soft-lock and an auto camera.
- Session: one arena (3-5 min) per phone sitting; several arenas on PC *(guess)*.

## Later

- Weapons switched in the middle of a combo.
- Upgrades that add new moves.
- Music that grows with the style rank.
- Giant bosses with a camera of their own.
- Finishers driven by repeated presses.
- Cutting objects along a line you choose.
- Enemy groups that combine attacks as a team.
- Cutscenes and dramatic camera moments.

## In a mashup

Character action leads combos, dodges and the style rank. An RPG half leads levels and gear, and gear
never replaces skill. A rhythm half leads timing, and attacks land on the beat. A roguelite half leads
the run and what carries over. A platformer half leads the jumps between arenas, and a beat-em-up half
leads crowds along a stage.
