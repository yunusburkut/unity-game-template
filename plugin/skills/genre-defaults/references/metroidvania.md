# Metroidvania

A connected 2D map opened up by new abilities; the core verb is explore, then come back with the key. Like Hollow
Knight, Metroid or Castlevania.

**Camera (Unity):** an orthographic side view that follows the player with look-ahead and is clamped to each room's
bounds; a perspective third-person camera behind the hero for a 3D one.

## Defaults

- **lock-before-key**: The first minutes show a ledge too high or a wall too strong, then give the move that beats
  it, a double jump or a dash, close enough to go back. Why: the map turns from a wall into a promise. Break it when:
  progress is by knowledge alone, with every tool there from the start.
- **map-fills**: A map fills in room by room as you explore, shows where you are and marks the blocked ways you have
  seen. Why: the player remembers the locks and plans the way back. Break it when: the world is a few screens that
  fit in the head.
- **bench-and-shortcut**: A bench heals you and saves the game, and ordinary enemies come back; a door that opens only
  from the far side later loops a hard route back to it. Why: the bench is a safe home, and opening the shortcut
  makes the map smaller. Break it when: the hero respawns at every door with nothing lost, a short action game.

Variety floor (hypothesis): 3 enemy kinds in the first slice, each attacks or moves differently. [zelda-manual-1]

## Feel

- **forgiving-jump**: Late jumps off a ledge, early presses before landing and clipped corners still count; hold to
  jump higher, and fall faster than you rise (numbers: game-feel). Why: a miss is the player's mistake, and every
  jump can be shaped. Break it when: the hero is heavy and every jump is one fixed arc, the old Castlevania way.
- **quick-slash**: The attack comes out at once, reaches a little past the blade, and a hit pushes the enemy back and
  you back a step. Why: fighting and moving are one skill, and a hit never leaves you stuck in a crowd. Break it
  when: there are no fights, a calm explorer of ruins.
- **new-move-moment**: A new move stops play for a beat with a pose, a jingle and its name, and then it works
  everywhere, in fights too. Why: the player feels stronger, and every old wall is worth a second look. Break it
  when: moves come thick and fast, a new power every minute.
- **room-camera**: The camera leads where you are heading, holds still through ordinary jumps and stops at the edges
  of each room, so the room's shape reads. Why: the next danger is seen in time, and each room is remembered as a
  place. Break it when: each room is one screen.

## Variants

- **nimble**: quick runs, an early dash, light fights you flow through.
- **deliberate**: a slower hero, enemies that hit hard, fights you read.
- **wanderer**: few enemies, more secrets, the map itself the reward.

## Choices that shape the pitch

- **Failure:** back to the last bench with nothing lost (default) · back to the bench, with your money left where you
  fell to win back once · a restart at every door.
- **Growth:** new moves that open new places (default) · levels and gear as well, the Castlevania way · knowledge
  alone, every tool from the start.
- **View:** 2D side view (default) · 3D behind the hero.
- **Feeling:** the player feels discovery by opening a way they passed long ago, because they remembered the lock and
  now carry the key.

## Platforms

- PC: WASD or arrows move, keys for jump, attack and dash; a gamepad suits it best. Touch: a left virtual stick and
  jump, attack and dash buttons; precise platforming loses the most on glass *(guess)*.
- Phone: landscape.
- PC sessions run an hour or more; on a phone, bench to bench is 5-10 min, so benches sit closer *(guess)*.

## Later

- A bigger map of more areas and more moves.
- A boss guarding each new move.
- Sequence breaks and advanced tricks.
- Secret rooms behind odd-looking walls.
- One place reached from above, through and below.
- A second world after the end.
- Badges or charms that change your moves.
- Fast travel between benches.
- Rules learned from clues that open the way.

## In a mashup

The metroidvania leads the map, its gates and the benches. A platformer half leads jumps and movement forgiveness. A
soulslike half leads fights and what a death drops. A roguelite half leads the run, and the map is new each run
while the ability gates stay. An RPG half leads levels and gear.
