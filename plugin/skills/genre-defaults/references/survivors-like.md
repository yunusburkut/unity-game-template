# Survivors-like

Auto-attack hordes; the player moves and picks a build. The core verb is steer.

**Camera (Unity):** fixed top-down orthographic camera that stays on the player as the field scrolls; one fixed
camera framing the whole arena for an arena that fits the screen.

## Defaults

- **timed-run**: The run is a clock: survive until it runs out, with a boss at the end, and the time left and
  your level are always on screen. Why: the player knows how far the finish is, and each minute is harder than
  the last. Break it when: an endless run for a high score.
- **level-up-pick**: Each level pauses the horde and offers one of a few weapons or upgrades, each saying what
  it does; a weapon already held goes up a level, and the build has a few slots. Why: the build is the player's
  own. Break it when: the loadout is fixed before the run.
- **evolve-recipe**: A weapon at its top level plus the right passive item evolves into a stronger one with a
  new effect, and the recipe is shown on both. Why: a build goal to chase, and a combo nobody can find is no
  combo. Break it when: the run is too short for any weapon to max out.

Variety floor (hypothesis): 4 enemy kinds in the first slice; a boss or an elite wave counts. [vampire-survivors-1]

## Feel

- **move-only**: You only steer: every weapon fires on its own, at the nearest enemy or in its own pattern, and
  moving starts and stops at once. Why: one hand plays, and where you stand is the whole skill. Break it when:
  aiming by hand is asked for, a twin-stick shooter.
- **gem-magnet**: Beaten enemies drop gems that fly to you once you are near, and an upgrade widens the pull. Why:
  the reward is swept up without breaking the dodge. Break it when: levels come from time alone.
- **horde-swells**: The crowd thickens minute by minute, a new enemy kind arrives every so often, and each kind
  differs in one way you can see: fast, tough or shooting. Why: pressure rises with the build, so the power is
  felt against something. Break it when: a calm run with few enemies.
- **power-shows**: Each weapon level changes what you see: one more blade, a wider ring, a bigger blast, never
  only a number, and your own effects stay paler than the enemies. Why: the build grows where the player looks,
  and danger still reads at the peak. Break it when: a spreadsheet build of hidden numbers is asked for.

## Variants

- **swarm**: A slow walk through huge crowds of weak enemies, a build that clears the screen.
- **arena**: Short timed waves in one arena, fewer and tougher enemies, a shop between waves.
- **dodge**: Fewer enemies that fire patterns, quick movement, weaving between shots.

## Choices that shape the pitch

- **The run:** a timed run on an open field with a boss at the end (default) · short waves in one arena with
  a shop between them · endless, for a high score.
- **Builds:** one of a few on each level-up (default) · a few characters, each with its own starting weapon ·
  items bought in a shop between waves.
- **Between runs:** gold for small permanent upgrades, saved (default) · new characters and weapons unlocked,
  no stat gains · nothing, each run alone.
- **View:** top-down, following (default) · one fixed arena.
- **Feeling:** the player feels power turn into release by walking through a crowd that chased them minutes
  before, because each level added a piece they chose.

## Platforms

- PC: WASD or a gamepad stick; the mouse only picks level-up cards.
- Touch: a floating stick where the thumb lands (Pointer press sets its centre); one thumb plays, so portrait
  works *(guess)*.
- Session: a full run is long on PC (Vampire Survivors runs 30 minutes); a phone run wants to be shorter, or
  saved on `OnApplicationPause` *(guess)*.
- Hundreds of enemies: pool them and keep per-enemy work out of `Update` (unity-performance).

## Later

- Many characters and stages
- A book of evolutions and unlocks found over many runs
- A chest that spins for several rewards at once
- Protection from long runs of bad offers
- A collection screen of every weapon and enemy seen
- Two players on one screen
- Daily seeded runs (a local seed from the date works now; shared leaderboards need a server)

## In a mashup

The survivors-like leads the build and the horde: what the player picks, and how the crowd grows to meet
it. Movement leads the immediate feel, and aim and threats stay readable as the build grows. A roguelite leads
what a death resets and what carries over. A tower defense half leads placement, and the horde walks a path. An
RPG half leads the characters and their stats.
