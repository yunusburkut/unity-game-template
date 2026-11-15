# Arcade classic

A single-screen game played for a high score (maze chase, snake, breakout, invaders, asteroids, a growth game); the
core verb is steer and survive one more second.

**Camera (Unity):** a fixed orthographic camera that fits the whole play field to the screen; for a growth game, an
orthographic camera that follows the player and zooms out as it grows.

## Defaults

- **best-score**: The score sits at the top beside the best score, which is saved between sessions, and the game-over
  screen says when it is beaten. Why: every run has a number to beat. Break it when: a growth game played for size, or
  a calm toy with no score.
- **lives-and-extra**: A few lives shown as icons, an extra life at a score, and a short safe moment after each death.
  Why: arcade stakes, with a reward for playing well. Break it when: one life a run, with an instant restart.
- **gets-faster**: Each cleared screen or wave comes back faster or busier, and the level number is on screen. Why: the
  same screen stays a challenge as the player improves. Break it when: a growth game, where getting bigger is the
  change.

## Feel

- **instant-turns**: The player moves the moment the input arrives, and a turn pressed a moment early is buffered, so
  a quick pair of turns both count. Why: a death is the player's mistake, never a dropped input. Break it when: a
  drifting ship with momentum, where the slide is the skill.
- **fair-collisions**: The player's hurtbox sits a little inside the sprite, and pickups are caught a little outside
  it. Why: a near miss looks like one, and a grab that looks like a grab counts. Break it when: exact edges are the
  challenge on purpose.
- **score-pops**: Every score pops up where it was earned, and quick kills or pickups in a row raise a multiplier shown
  beside the score. Why: playing fast and close is seen to pay. Break it when: the score is plain counting, as a
  snake's length.

## Variants

- **frantic**: speed climbs quickly, big chains, short runs.
- **steady**: a slow start, a pattern to learn, long runs.
- **snowball**: you grow, and what chased you becomes what you eat.

## Choices that shape the pitch

- **What you play:** a maze chase, eat every dot while enemies hunt you (default) · a snake that grows · ball and
  paddle against bricks · a descending fleet to shoot down · a ship among drifting rocks · eat smaller things to grow.
- **Stakes:** a few lives, then game over (default) · one life, instant restart · no failure, a timed round for score.
- **Speed:** each level faster (default) · speed that rises with the score · the same speed, more enemies.
- **View:** one fixed screen (default) · a camera that follows and zooms out as you grow.
- **Feeling:** the player feels the pull of one more go by beating their best by a little, because the run was short,
  the death was their own and the restart is one press.

## Platforms

- PC: arrow keys or WASD for four-way moves; mouse aim for a ship or paddle. Touch: swipe for four-way turns, drag for
  a paddle or ship (Pointer delta), never a virtual stick for grid moves *(guess)*.
- Phone: portrait fits a maze or brick wall; landscape fits a wide fleet or asteroid field.
- Runs of 1-3 min on both; the phone build must resume after an interruption (pause on focus loss).

## Later

- Initials on the high-score table.
- Each enemy with its own chase rule.
- Two players taking turns or together on one screen.
- An attract demo that plays itself on the title screen.
- Growth through many stages of scale.
- A daily seeded challenge from the date (local; a shared table needs a server).
- An online high-score table (needs a server).
- A level editor.

## In a mashup

The arcade game leads the screen, the score and the lives. A roguelite leads upgrades between runs and what carries
over. A puzzle half leads the rules of the board. Rhythm leads timing, and moves land on the beat. A management half
leads money spent between rounds, and the arcade game keeps each round short.
