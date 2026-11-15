# Level maker

Build levels with an editor and play them; the editor is the toy (Super Mario Maker, LittleBigPlanet, Dreams). The core
verb is place a part, then play it.

**Camera (Unity):** an orthographic side view that follows the player in play and pans freely in the editor; an
orthographic top-down camera for a top-down maker; a perspective orbit for a small 3D build.

Levels save locally (one file per level under `Application.persistentDataPath`), played by their maker or a friend on
the same screen. Sharing between devices, browsing, likes and building together need a server.

## Defaults

- **ready-parts**: A small palette of ready parts (ground, a hazard, a coin, an enemy, the goal) that snap to a grid
  and work the moment they are placed. Why: a novice makes a playable level in a minute. Break it when: the user wants
  players to make the parts too, their art and their rules.
- **clear-to-save**: A level saves, with a name, only after its maker plays it through to the goal. Why: every saved
  level is proven winnable. Break it when: a toy with no goal, a scene to play about in.
- **sample-level**: The editor opens on a short level already made, to play first and then change. Why: the first edit
  is a small change, not a blank grid. Break it when: the user asks for a blank canvas.

## Feel

- **play-from-here**: One input plays the level from the cursor or the start, and a death or a second press drops back
  into the editor at that spot. Why: an idea is tried seconds after it is placed. Break it when: the editor makes a
  picture, not a level to play.
- **undo-any-edit**: Every placement and erase can be undone with no limit, and erasing is a quick drag. Why: building
  is trying, and nothing is lost by it. Break it when: each placement counts, a short set where placing is the puzzle.
- **pop-in-place**: Each part pops in with its own sound and a small bounce, and ground joins its neighbours (a Rule
  Tile from 2D Tilemap Extras) so a rough shape looks finished. Why: building feels like play, and the level looks
  good from the first stroke. Break it when: the look is drawn tile by tile on purpose.

## Variants

- **playful**: big chunky parts, silly hazards, a level made and played in a minute.
- **tinkerer**: parts wire together (a switch opens a door, a timer moves a platform), so a level becomes a machine.

## Choices that shape the pitch

- **What you make:** side-view jump-and-run levels (default) · grid puzzles, each saved only once solved · top-down
  mazes and dungeons · a small 3D build.
- **Who plays:** you, then a friend on the same screen (default) · one builds, the other must clear it, then swap ·
  levels shared online (later, needs a server).
- **Start:** a short sample level to change (default) · a blank grid.
- **Feeling:** the player feels creative ownership by playing a level they made a minute ago, because the parts worked
  at once and the switch to play is instant.

## Platforms

- PC: click to place, right click or drag to erase, wheel to zoom, Ctrl+Z to undo, one key to play. Touch: tap to
  place, a mode toggle for erase, two-finger pan and pinch zoom, an on-screen undo and play button *(guess)*.
- Phone: landscape for a side-view maker; the palette must not cover the grid *(guess)*.
- Phone sessions are short edits to one level; PC sessions are long builds. Autosave the open level on pause.

## Later

- Checkpoints in made levels, each start proven winnable.
- A rules editor of events, conditions, camera and screens.
- Parts with their own art and sound, made in the editor.
- Mods that change the game's own data.
- Sharing levels online, with browsing, likes and play counts (needs a server).
- Building one level together on two devices (needs a server).
- Mod versions and downloads when joining a friend (needs a server).

## In a mashup

The maker leads the editor, the palette, saving and the proof that each level can be cleared. The game it makes leads
play: a platformer half leads movement and the jump, a grid-puzzle half leads the rules and undo, a racing half leads
the track and the laps. A sandbox half leads free building with no goal, and the clear-to-save check is dropped.
