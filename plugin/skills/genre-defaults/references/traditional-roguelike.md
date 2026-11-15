# Traditional roguelike

Turn-based dungeon crawl on generated levels with permanent death; the core verb is one step, one turn.

**Camera (Unity):** an orthographic camera from above that follows the hero (default); one static orthographic
camera when a whole floor fits the screen.

*Thin sources:* CCGS research had no roguelike entries; turn order, sight and monster habits are guesses from
dungeon-crawl entries. Playtest them early.

## Defaults

- **floors-down**: Each floor is generated with stairs down, you start it with no monster in sight, and deeper
  floors are harder; the depth is on screen. Why: going down is a choice to push your luck. Break it when: the run is
  one big map with no floors.
- **monster-habits**: Monsters act in their own ways: some sleep until you come near, some keep distance and shoot,
  some flee when hurt and come back. Why: each new monster is a small problem to read. Break it when: there is one
  enemy kind and the fight itself is the puzzle.
- **death-ends-run**: A death ends the run: the screen says what killed you and at what depth, and one input starts a
  new dungeon. Why: every choice counts, and a new run is a fresh puzzle. Break it when: the user wants progress
  kept, a roguelite where runs unlock things.

Variety floor (hypothesis): 4 enemy kinds in the first slice, each attacking or moving differently (bosses and
elites count).

## Feel

- **turn-by-turn**: One input is one turn: step, or bump a monster to attack, and every monster answers at once;
  nothing moves while you think, and a held key walks on until a monster comes into view. Why: each danger can be
  weighed, so a death is a mistake you could see. Break it when: the user wants real-time dodging, an action
  roguelite.
- **sight-and-memory**: You see only what is in line of sight; rooms already seen stay on the map, dimmed, and
  monsters out of sight are not drawn. Why: doors and corners hide danger. Break it when: each floor is one small
  room read at a glance.
- **read-the-turn**: A few log lines say what just happened (who hit whom, what you picked up), and a number rises
  over each hit. Why: the player reads what went wrong and what to try next. Break it when: there are few event
  kinds and the pictures say it all.
- **close-call**: Low health shows plainly (the bar turns red, the hero dims), and a healing potion is one input
  away. Why: the player sees the moment to flee or drink. Break it when: health is hidden on purpose, a horror crawl.

## Variants

- **clever**: items and terrain combine (fire in tall grass, a potion at a crowd); a hard fight falls to a trick.
- **brisk**: small floors, many weak monsters, a whole run in a few minutes.
- **dread**: short sight, scarce healing, monsters heard before they are seen.

## Choices that shape the pitch

- **Stakes:** a death ends the run, nothing kept (default) · a few unlocks carry over, a roguelite · one revive item
  found in the dungeon.
- **Items:** named on sight (default) · unknown potions and scrolls, learned by using them · none, growth by levels.
- **Growth:** gear found on the way (default) · levels from kills · one of three boons after each floor.
- **View:** tiles from above (default) · letters on a grid, the classic look · a 3D board from a fixed angle.
- **Feeling:** the player feels clutch survival by escaping a fight they should have lost, because nothing moved
  while they thought and the way out was on the board.

## Platforms

- PC: arrows, numpad or WASD (+ diagonals) for a step, single keys for actions, mouse optional.
- Touch: tap a tile to step toward it, tap a monster to attack, swipe for one step *(guess)*; actions on a bottom bar.
  Turn-based play suits a phone well. Portrait *(guess)*.
- Session: a brisk 5-15 min run fits a phone; save at the `platform-targets` App lifecycle points (pause on a
  phone, focus loss on PC), and delete the save on death (no reload cheat).

## Later

- Hunger and food
- Classes to pick at the start
- Shops and gold
- Allies who follow you and fight
- Unlocks kept between runs
- Bosses at set depths
- Hand-made vaults inside generated floors
- Auto-explore and travel by click
- A daily seed with a ranking (needs a server; a local daily seed from the date does not)
- Stress that changes how the hero acts

## In a mashup

The roguelike leads turns, generated floors and death. A deckbuilder half leads cards that replace the hero's moves,
and the dungeon stays turn by turn. An action half makes it a roguelite: action leads movement and timing, and the
run leads what carries over. An RPG half leads classes and stats. A puzzle half leads hand-made floors with one
answer each, and undo replaces death.
