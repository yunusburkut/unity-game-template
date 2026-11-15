# Dungeon crawler

A party explores a grid dungeon in first person, step by step; the core verb is step into the next square. Like
Legend of Grimrock or Etrian Odyssey.

**Camera (Unity):** a first-person perspective camera that moves one grid square per step and turns 90 degrees per
turn, each move a short tween; a top-down camera over the grid for a crawl seen from above.

*Thin sources:* the sources cover generated floors and rest that brings monsters back, not grid steps, the party
or fights in the crawl view. Treat the rest as the model's reading.

## Defaults

- **auto-map**: A small map draws itself square by square as you walk, with an arrow for the way you face. Why: the
  player always knows where they have been, so the blank squares pull them on. Break it when: mapping by hand is the
  challenge, an old-school crawl with no map.
- **stairs-down**: Each floor has stairs down to a harder one, and the floor number is on screen. Why: going deeper is
  a choice, and the depth is the score. Break it when: the dungeon is one hand-made floor and the way out is the goal.
- **camp-rest**: Resting in a safe room heals the party and saves the game, but ordinary monsters come back. Why: a
  safe room is a goal to reach, and rest has a price. Break it when: the crawl is one short dive with no way to rest.

## Feel

- **dark-ahead**: The corridor fades to dark a few squares ahead, and monsters are heard before they are seen, from
  the side they are on. Why: each step into the dark is a small dare. Break it when: the dungeon is bright and
  friendly, a cozy crawl for young players.

## Variants

- **brisk**: quick steps, quick fights, small floors and the stairs never far.
- **tactical**: fewer, harder fights where the front and back rows matter and the monster's next move is shown.
- **dread**: a torch that burns down, scarce healing, sounds behind every wall.

## Choices that shape the pitch

- **Fights:** turn by turn, the monster's next move shown (default) · real time on the grid, stepping aside from a
  blow as it lands.
- **Dungeon:** generated floors (default) · one hand-made floor of keys, levers and locked doors · a single tower to
  climb.
- **Party:** a ready-made party (default) · pick each hero's class at the start · one hero alone.
- **View:** through the party's eyes (default) · from above.
- **Feeling:** the player feels dread and discovery by stepping into a dark square where they heard something,
  because the map shows what is known and the dark hides the rest.

## Platforms

- PC: WASD steps, Q and E turn, the mouse picks party actions in a fight. Touch: an on-screen step and turn pad, and
  taps on party actions.
- Phone: portrait works, with the view on top and the party and map below *(guess)*; landscape for a wide view.
- A floor is 10-20 min on PC; on a phone, save at each staircase *(guess)*.

## Later

- Classes and a party built from them.
- Orders the party follows on its own.
- Gear that teaches skills.
- Traps, pressure plates and lever puzzles.
- Hidden walls and secret rooms.
- Food and torches that run out.
- A town with shops between dives.
- More hand-made floors with a story.

## In a mashup

The crawler leads grid movement, the party and the map. A roguelike half leads generated floors and what a death
costs. A card battler half leads fights as cards the party plays, and the grid stays. A horror half leads dread and
sound. A puzzle half leads lever and pressure-plate rooms with one answer each.
