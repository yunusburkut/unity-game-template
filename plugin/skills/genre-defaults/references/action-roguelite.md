# Action roguelite

Real-time runs that end in death, while some progress carries over; the core verb is fight a room, then pick an
upgrade. Like Hades, Dead Cells or Enter the Gungeon.

**Camera (Unity):** a top-down camera that follows the player and sits between the player and the aim point; an
orthographic side view that follows the player for a side-scrolling run.

## Defaults

- **pick-a-boon**: Clearing a room offers one of a few upgrades, each saying what it does, and the build grows from
  them. Why: every room changes the run, so no two runs play the same. Break it when: the build is a loadout chosen
  before the run.
- **meta-progress**: Death keeps a currency spent between runs on small permanent upgrades, and the game saves it.
  Why: a lost run still moves the player forward. Break it when: only skill carries over, pure runs on request.
- **generated-floors**: Each run lays out its floors from hand-made rooms in a new order, with a safe first room, and
  the run's seed is shown at its end. Why: every run is new, and every room is still fair. Break it when: one fixed
  route learned run after run.

Variety floor (hypothesis): 4 enemy kinds in the first slice, each attacks or moves differently; a mini-boss or a
boss counts. [isaac-2], [gungeon-2]

## Feel

- **dodge-dash**: A dash on its own input is untouchable from its first moment, and an attack pressed during it comes
  out as it ends. Why: a mistake can be dodged, so skill beats numbers. Break it when: defence is a block or a
  parry, a duel.
- **loot-pops**: Coins and pickups burst out of a beaten enemy, then fly to the player on their own. Why: the reward
  is seen and caught without breaking the fight. Break it when: rewards come only at the room's end.
- **room-clear**: The last enemy of a room goes down harder, then a quiet beat; the doors unlock with a clear sound
  and the reward appears. Why: each room ends on a small high, and the way on is plain. Break it when: one open
  level with no rooms, where fights flow into each other.

## Variants

- **aggressive**: fast dashes, quick hits, health won back by attacking.
- **gunplay**: a gun always firing, rolls through bullet patterns.
- **heavy**: slow weapons that commit, fewer enemies, each fight a duel.

## Choices that shape the pitch

- **Combat:** melee with a dash (default) · guns and a dodge roll · a side view that runs and jumps.
- **Builds:** one of a few upgrades after each room (default) · items found in rooms, the strongest with a drawback
  · a loadout picked before the run.
- **Between runs:** a currency for small permanent upgrades (default) · new weapons and starts unlocked, no stat
  gains · nothing, pure skill.
- **View:** from above (default) · from the side.
- **Feeling:** the player feels clever and strong by finding upgrades that combine, because each room offers a
  choice and the build shows how they stack.

## Platforms

- PC: WASD moves, the mouse aims, Space dashes. Touch: a left virtual stick, a dash button on the right, and aim
  assist toward the nearest enemy *(guess)*.
- Phone: landscape.
- A PC run is 20-40 min; on a phone, save the run at each room clear, or make runs shorter *(guess)*.

## Later

- A hub between runs with characters and a story.
- More biomes and bosses.
- Difficulty modifiers after a win.
- A shop in the middle of a run.
- Upgrades that multiply each other.
- Rare items, with protection from long unlucky streaks.
- Co-op runs on one screen.
- A daily seeded run from the date (local; a shared table needs a server).

## In a mashup

The roguelite leads the run: what a death resets and what carries over. The action half leads the immediate feel,
combinatorial pieces lead the build, and aim and threats stay readable as the build grows. A deckbuilder leads the
build as cards. A platformer leads movement in a side view. A management half leads the hub between runs.
