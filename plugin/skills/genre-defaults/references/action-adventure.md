# Action-adventure

Explore a world, fight by hand and solve its puzzles to open new places; the core verb is finding the way in.

**Camera (Unity):** a perspective camera from above that follows the hero (default); a fixed-angle 3D view that
follows without rotating (as in Tunic); or a free perspective third-person orbit behind the hero.

## Defaults

- **lock-before-key**: A locked door or blocked path is in view early; the key or tool that opens it is found later,
  in a fight or a puzzle, and a new tool works elsewhere too. Why: the player sees the goal before the way to it.
  Break it when: the world is open from the start, a ride across a field with nothing locked.
- **puzzle-rooms**: Between fights, a few rooms hold a small puzzle (push a block, light the torches, hit a switch),
  and leaving a room resets its puzzle. Why: thinking and fighting take turns, and no puzzle is stuck for good.
  Break it when: the adventure is all fighting and riding, a straight run of set pieces.
- **hearts-and-retry**: Health is a row of hearts; losing them all puts you back at the room's door with full hearts,
  and cleared rooms stay clear. Why: health reads at a glance, and a loss costs a room, never the adventure.
  Break it when: the user asks for hard stakes, a rest spot far behind with the enemies back.

## Feel

- **sword-swing**: The swing starts at once, sweeps a wide arc in front, and a hit knocks the enemy back a step.
  Why: a swing that reaches and pushes gives the player room to think. Break it when: there is no sword.
- **roll-or-block**: A quick roll or a raised shield answers an attack, and a press a little early or late still
  counts. Why: the player wins by reading the attack, not by trading hits. Break it when: the hero is fragile on
  purpose, a chase where running is the only answer.
- **item-get**: An opened chest or a new tool stops play for a beat: the hero holds it up, a jingle plays, its name
  shows. Why: every find is a small event. Break it when: finds come so often that a beat each drags, a loot game.
- **world-reacts**: Grass cuts, pots break and bushes shake under the sword, and some drop a heart. Why: the world
  answers the sword, and a hurt player finds health nearby. Break it when: the world is stone and still on purpose.

## Variants

- **nimble**: fast steps, quick swings, a roll to dodge, enemies down in a few hits.
- **weighty**: committed swings, a shield to block, enemies that take patience.
- **curious**: rare, easy fights, more to find, puzzles that give the eureka.

## Choices that shape the pitch

- **The world:** a small dungeon of connected rooms (default) · an open field with a landmark and a few things to
  find · a straight path of set pieces.
- **Fights:** sword and roll (default) · rare fights, mostly finding and puzzles · riding a mount across the field.
- **Stakes:** back to the room's door with full hearts (default) · back to the last rest spot, enemies back too.
- **View:** from above, following (default) · a fixed 3D angle · a third-person orbit.
- **Feeling:** the player feels clever and brave by opening the door they saw at the start, because the key was won
  in a fight and a puzzle they solved.

## Platforms

- PC: WASD moves, mouse or keys swing and roll; an orbit camera adds mouse look.
- Touch: a virtual stick on the left, swing and roll buttons on the right *(guess)*; an orbit camera on touch needs a
  drag zone, so the top-down or fixed view suits phones better. Landscape.
- Session: one room or dungeon section on a phone (5-10 min), a whole dungeon on PC *(guess)*.

## Later

- A world map with markers and fast travel
- New tools over time that open old places
- A boss with phases
- Several dungeons and a quest line
- Companions who help in fights
- Caring for a mount
- Shortcuts that loop back to a safe spot
- Locking on to one enemy in 3D
- Townsfolk who notice what you did

## In a mashup

The action-adventure leads the world, movement and fights. A puzzle half leads the room puzzles' rules and their
resets. An RPG leads levels and gear. A metroidvania leads the map and its ability gates. A detective half leads the
clues, and knowledge can open a door the way a tool does. A survival half leads hunger and crafting.
