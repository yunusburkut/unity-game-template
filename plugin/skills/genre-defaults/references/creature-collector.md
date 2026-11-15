# Creature collector

Catch creatures, train a team and battle with it (Pokémon, Temtem, Cassette Beasts). Core verb: weaken,
then catch.

**Camera (Unity):** a top-down camera that follows the player in the world (orthographic for 2D tiles);
a fixed camera on a separate battle scene or screen.

## Defaults

- **pick-a-starter**: The player picks one of three starter creatures before the first step. Why: the
  first choice makes the team theirs. Break it when: the first creature is part of the story or caught
  in the opening scene.
- **weaken-to-catch**: A wild creature is caught by weakening it, then throwing a capture item; a weaker
  creature is easier to catch. Why: the catch is earned in the fight, at a risk the player picks. Break
  it when: creatures join by being befriended, fed or helped.
- **soft-loss**: A lost battle sends you to the last healing spot, team healed, nothing lost. Why: the
  player keeps exploring instead of grinding back. Break it when: the user asks for hard stakes (a
  fainted creature is gone for good).

## Feel

- **type-loop**: Every creature and move has a type; a few types beat each other in a loop, and the
  battle says when a hit is strong or weak. Why: a battle is something to read, not a race of numbers.
  Break it when: nothing fights (a race or care game).
- **quick-battles**: Four moves on fixed buttons, the enemy turn played fast, battles that start and end
  in seconds. Why: the hundredth battle is as quick as the first. Break it when: battles are real time,
  steered by hand.
- **catch-moment**: The capture item wobbles before it holds or breaks; a catch ends on a jingle and the
  creature's name. Why: the catch is the high point, so it gets suspense and a reward. Break it when:
  creatures join with no catch.

## Variants

- **snappy**: quick menus, fast animations, the next battle seconds away.
- **cozy**: a slower pace, creatures that react to you between battles, nothing rushed.

## Choices that shape the pitch

- **Battles:** turn-based, one creature each, moves from a menu (default) · real time, steered by hand ·
  a team of three that fights on its own from rules you set.
- **Stakes:** back to the healer, nothing lost (default) · lose some money · a fainted creature is gone.
- **Progression:** creatures level up and learn moves (default) · creatures change form at a level ·
  the team grows only by catching.
- **View:** a top-down world and a separate battle screen (default) · one 3D world, battles in place.
- **Goal:** beat the first trainer at the end of the route (default) · catch every creature in one area ·
  help the creatures, no battles (cozy).
- **Feeling:** the player feels attached to their team by winning with a creature they caught
  themselves, because they weakened it and caught it in a fight they chose.

## Platforms

- Keyboard+mouse: WASD or arrows to walk, battle moves on 1-4 or a click on the move button.
- Touch (Pointer): tap or drag to walk, big move buttons in the lower half. Portrait suits a turn-based
  game with menus *(guess)*.
- Session: a few battles and a catch (5-10 min) on a phone; a route or a town on PC *(guess)*. Save on
  every catch and on OnApplicationPause.

## Later

- Evolution trees.
- Breeding.
- A map of towns and a ladder of trainers.
- Shops and items.
- A story.
- Rare variants and protection from long unlucky streaks.
- Raising and caring for creatures between battles.
- Battles with friends (the coop-multiplayer pack); trading and ranked battles with strangers (needs a server).

## In a mashup

The collection leads catching and the party. Turn-based battle leads combat rules and shows the enemy's
next move where the pitch wants planning. An adventure or RPG half leads the world and progression. A
racing half leads the race, and the collection gives the racers. A farming or cozy half leads the daily
rhythm, and creatures help with the work.
