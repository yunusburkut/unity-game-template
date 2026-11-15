# Twin-stick shooter

Top-down; one stick moves, the other aims (Geometry Wars, Robotron). Core verb: move one way, shoot
another.

**Camera (Unity):** a top-down camera (orthographic for 2D, or a steep perspective) placed between the
player and the aim point; a fixed camera for one arena that fits the screen.

## Defaults

- **waves-and-score**: One arena, enemies in growing waves, a score with a multiplier on screen that a
  hit resets; the best score is kept. Why: every second alive is worth more than the last. Break it
  when: rooms to clear and a door to reach, with no score.
- **enemy-jobs**: A few enemy kinds, each with its own job: one chases, one wanders, one shoots, one
  splits when hit. Why: the player reads a crowd by its shapes and picks what to shoot first. Break it
  when: one horde of the same enemy is the point (a survive-the-swarm game).

Variety floor (hypothesis): 4 enemy kinds in the first slice, each attacking or moving differently.

## Feel

- **move-and-aim**: One hand moves at the same speed in every direction (normalise diagonals), the other
  aims, and the gun fires where you point while you keep moving; a gamepad gets a small aim assist, a
  mouse none. Why: dodging and shooting are two jobs done at once. Break it when: one button fires the
  way you face.
- **camera-leads-aim**: The camera sits between the player and the aim point, so more of the screen lies
  where you shoot. Why: the threat you aim at is in view before it reaches you. Break it when: the whole
  arena fits the screen and the camera never moves.
- **gun-kick**: Every shot flashes at the muzzle and kicks the player back a little; bullets are big,
  fast and easy to follow. Why: the gun feels strong with no text. Break it when: the weapon is soft and
  silent on purpose.
- **spawn-warning**: New enemies flash in place a moment before they are real and never appear right
  beside the player. Why: a death comes from a choice, never from a spawn. Break it when: enemies walk
  in through set doors at the edges.

## Variants

- **swarm**: neon, one arena, crowds that keep growing, one hit costs a life.
- **bullet-dodge**: rooms of shooters, a dodge roll through their bullets, health that matters.
- **heavy-gun**: slow, strong shots with a big kick, fewer and tougher enemies.

## Choices that shape the pitch

- **Arena:** one arena, endless waves (default) · rooms cleared one by one · a run of generated rooms
  (a roguelite).
- **Stakes:** a few lives and a high score (default) · one life · health, and pickups that heal.
- **Weapons:** one gun that grows with pickups (default) · a few guns with different jobs · ammo earned
  by kills.
- **Players:** one (default) · two on one device (local co-op, PlayerInputManager).
- **View:** from above, following (default) · one arena that fits the screen.
- **Feeling:** the player feels fearless aggression by diving into a crowd to keep the multiplier,
  because each kill keeps it climbing and each enemy reads at a glance.

## Platforms

- Keyboard+mouse: WASD moves, the pointer aims, hold left button to fire. Aim is the world point under
  the cursor, not a direction from screen centre.
- Touch (Pointer): two virtual sticks, left moves, right aims and fires while held; or auto-fire at the
  nearest enemy with one stick *(guess)*. Landscape on phones. Keep thumbs from covering the player.
- Session: a run of 2-5 min fits a phone and PC alike *(guess)*.

## Later

- Enemies that flank, take cover and call to each other.
- Bosses with phases; a bomb that clears the screen.
- Weapons and builds unlocked between runs.
- Cover that breaks apart; shields and weak points that need a different aim.
- Scores shared online (needs a server; a local best score first).
- Online co-op with friends (the coop-multiplayer pack; matchmaking with strangers needs a server).

## In a mashup

The twin-stick leads movement, aim and the arena. A roguelite half leads the run, the rooms and what
carries over. An RPG half leads loot and levels. A tower-defense half leads building between waves, and
the shooting stays by hand. A stealth half leads guards and sight, and the shooting is the plan that
failed.
