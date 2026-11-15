# First-person shooter

Shooting through the character's eyes in 3D; the core verb is aim and fire.

**Camera (Unity):** perspective first-person camera on the player's head, the yaw on the body and the pitch on
the camera; a third-person over-the-shoulder orbit for a third-person shooter.

## Defaults

- **ammo-and-reload**: Each gun holds a magazine and a reserve, shown in a bottom corner beside the health; one
  input reloads, and an empty gun clicks. Why: running dry is a choice the player made, never a surprise. Break
  it when: one gun with endless shots, an arcade shooter for score.
- **enemy-roles**: A few enemy kinds that each ask a different answer: fodder that rushes, a shooter that keeps its
  distance, a tough one that pushes you out of cover. Why: a fight is a quick puzzle of who to shoot first. Break
  it when: a duel against one boss, or waves of one enemy for score.

Variety floor (hypothesis): 3 enemy kinds in the first slice. [doom-manual-1]

## Feel

- **mouse-look**: The mouse turns the view with no smoothing, and the pause screen has a sensitivity setting. The
  Input System's mouse delta is already per frame: never multiply it by `Time.deltaTime`. Lock the cursor
  (`Cursor.lockState = CursorLockMode.Locked`) in play and free it on pause. Why: the aim answers the hand at
  once. Break it when: a rail shooter, where only the crosshair is aimed.
- **hit-confirm**: A hit marker flashes on the crosshair with a crisp tick, and a kill has its own sound. Why:
  the player knows a shot landed without looking away from the target. Break it when: horror or a tactical sim,
  where you are meant to doubt the shot.
- **guns-differ**: Each gun has its own kick, flash and sound, sways as you walk and drops away to reload,
  and a low-ammo sound warns before it runs dry. Why: guns feel different in the hands, and the ear tracks the
  magazine. Break it when: one plain gun on purpose, a puzzle shooter.
- **hurt-direction**: A hit from off to the side marks the screen edge it came from. Why: a hit is something to
  turn and answer, not a mystery. Break it when: the threat is meant to stay unseen, a horror shooter.

## Variants

- **boomer**: Fast and fearless: quick strafing, no cover, health and ammo picked up by pushing in.
- **tactical**: Slower moves, cover, health that comes back out of fire.
- **mech**: A slow, armoured walker that turns with weight, big guns.

## Choices that shape the pitch

- **View:** through the eyes (default) · over the shoulder, with cover to duck behind and a timed reload ·
  from above is a twin-stick shooter instead.
- **Health:** picked up in the level (default) · comes back after a moment out of fire · armour on top of health.
- **Structure:** one level of rooms and arenas to an exit (default) · waves in one arena, for score · a mech
  walking through a city of props it knocks over.
- **Feeling:** the player feels powerful by clearing a room with the right gun for each enemy, because every
  kind asks a different answer and every hit is confirmed.

## Platforms

- PC: WASD plus mouse look is the genre's home; a gamepad needs aim assist (later).
- Touch: a virtual stick bottom-left, drag on the right half to look, fire and reload buttons on the right;
  landscape. Touch look uses Pointer delta scaled by dp, not by frame time.
- Session: a level is 5-15 minutes on PC; a phone wants shorter arenas *(guess)*.

## Later

- Online matches and lag compensation (needs a server)
- A campaign of levels and set pieces
- Enemies that take cover, flank and call to each other
- Squad mates
- Aim assist for gamepads and touch
- Sound shaped by walls and rooms
- Weapon upgrades and mods
- Wall runs and slides
- Vehicles

## In a mashup

The shooter leads aiming, the guns and hit feedback. Horror leads what the player can know and the pace of
threats, and survival leads scarce ammo and the inventory. A roguelite leads the run and its builds. An RPG
leads loot and levels, a looter shooter. Parkour leads movement in a movement shooter. Stealth leads detection.
