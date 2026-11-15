# Action RPG

Real-time fighting by hand; levels, gear and builds set the numbers. The core verb is strike.

**Camera (Unity):** perspective camera angled down from above, following the hero; a third-person orbit behind
the hero (Orbital Follow) for a third-person one; first person for a looter shooter.

## Defaults

- **gear-compare**: Gear drops with its rarity in its colour and its name, and pointing at it shows what it changes
  against what you wear, better or worse, in words and arrows (never colour alone, player-clarity). Why: a pickup
  is a quick choice, not homework. Break it when: there is no gear, and power comes from levels and skills alone.
- **level-points**: Kills fill an experience bar; each level gives a point for a skill or a stat, the first
  choice comes early, and early points can be taken back. Why: the build is the player's own from the first
  minutes. Break it when: power comes only from gear, a pure looter.
- **potion-charges**: Healing is a few potion charges on one input, refilled at checkpoints and a little by
  kills. Why: healing is a choice in the fight, never a hoard. Break it when: health comes back on its own
  between fights, a gentle game.

Variety floor (hypothesis): 3 enemy kinds in the first slice. [dark-souls-manual-1] [miyazaki-1]

## Feel

- **sure-strike**: An attack starts the moment it is pressed and turns toward the nearest enemy in reach, and
  a dodge can cut the end of a swing, never its start. Why: the hero hits what the player meant, and a mistake
  can still be dodged. Break it when: heavy, committed swings are the challenge, a slow duel.
- **loot-burst**: A beaten enemy bursts into gold and gear that scatter and settle; gold flies to you, and a
  rare drop rises in a beam of its colour with its own sound. Why: the reward is seen across the screen, and
  the best one is heard. Break it when: rewards come only at the end of a level.
- **breakpoints**: An upgrade is felt as fewer hits: an enemy falls in one swing fewer, and a pack you fled from
  falls to one blast. Why: growth shows in the fight, not only on the sheet. Break it when: numbers never change,
  a game of skill alone.
- **pack-fights**: Enemies come in packs of weak ones around a tougher one, and an area attack through a pack
  scatters them, its hits added into one rising number. Why: the hero feels strong against many, and one number
  says how strong. Break it when: every fight is a duel.

## Variants

- **horde**: Fast moves, big packs, area skills that clear the screen.
- **heavy**: Few enemies, stamina, committed swings, a dodge that costs.
- **guns**: Weapon families that each handle their own way, shooting from cover.

## Choices that shape the pitch

- **Combat:** click-to-move or WASD from above (default) · behind the hero with a dodge and stamina, orbit
  camera · guns through the eyes, a looter shooter.
- **Loot:** gear of a few rarities with a quick compare (default) · fewer uniques that change the rules · no
  gear, skills only.
- **Death:** back to the last checkpoint with everything kept (default) · gold dropped where you fell, to win
  back · the hero gone for good, a hard mode.
- **Build:** a few skills opened by level (default) · a skill board with keystones · gear that changes how
  the hero moves and fights.
- **Feeling:** the player feels their power grow by clearing a pack that nearly killed them earlier, because a
  level or an item cut the hits each enemy takes.

## Platforms

- PC: click-to-move and click-to-attack on the Pointer, skills on number keys, or WASD plus mouse aim.
- Touch: a virtual stick bottom-left, attack and three or four skill buttons bottom-right, auto-target the
  nearest enemy; landscape. Compare and inventory need tap, not hover.
- Session: PC sessions run long; on a phone one dungeon of a few minutes, saved on `OnApplicationPause` *(guess)*.

## Later

- Crafting that rerolls gear within a budget
- Item slots and affix rules
- A grid inventory where shapes are the puzzle
- A stash and several characters
- Bosses with phases and parts to break
- Endgame maps of rising tiers
- Loot weighted toward the current build
- Enemies that flank and work together
- Co-op and trading with other players (co-op: the coop-multiplayer pack; trading needs a server)

## In a mashup

The action RPG leads loot and the build. Action leads timing, targeting and camera, and the chosen stakes lead
checkpoints. A roguelite leads the run and what a death resets. A survival
half leads gathering and crafting, and the action RPG leads the fights.
