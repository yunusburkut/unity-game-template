# Hidden object

Find listed items or characters in a cluttered scene; the core verb is look and point. Like Hidden Folks, Mystery
Case Files or Where's Waldo.

**Camera (Unity):** a fixed orthographic camera that fits the scene and the target strip to the screen; an
orthographic camera with drag-pan and zoom for a larger scene; a perspective orbit around a rotatable diorama.

## Defaults

- **targets-in-view**: A strip of targets sits beside the cluttered scene, so the player sees what to seek. Why: the
  search has a clear purpose. Break it when: the scene is open exploration with no required finds. [hiddenfolks-1]
- **unhurried-search**: The player takes their time and explores objects with no penalty for an empty click. Why:
  curiosity keeps the scene pleasant to search. Break it when: a timed contest is the stated challenge.
  [hiddenfolks-3]

## Feel

- **hint-on-request**: Selecting a target gives a clue that helps find it. Why: a stuck player can ask for help and
  keep control of the search. Break it when: the target's written clue is already the main instruction.
  [hiddenfolks-2]
- **scenery-answers**: Flaps open and bushes part when the player pokes them. Why: searching changes the scene instead
  of only testing the pointer. Break it when: every target is visible from the start, a pure observation puzzle.
  [hiddenfolks-4]
- **quiet-and-busy**: Different parts of the scene have sparse or busy ambient sound. Why: the player gets relief from
  constant noise while looking around. Break it when: the scene is silent by design. [hiddenfolks-5]

## Variants

- **gentle**: unhurried looking, harmless exploration, clues on request. [hiddenfolks-2], [hiddenfolks-3]
- **playful**: poke at the scenery and enjoy how it changes. [hiddenfolks-4]

## Choices that shape the pitch

- **What to find:** pictured targets (default) · names in a list · short riddles that describe the targets.
- **The search:** clutter with interactive hiding places (default) · a still picture · a diorama whose viewpoint
  reveals differences.
- **Stakes:** no clock and no penalty (default; [hiddenfolks-3]) · a timed score challenge.
- **View:** a scene that fits the screen (default) · a larger scene explored by panning · a rotatable diorama.
- **Feeling:** the player feels a small delight of discovery when a hint makes a hidden detail stand out of the
  clutter ([hiddenfolks-2]).

## Platforms

- PC: click to find and poke, scroll wheel zooms, drag pans. Touch: tap, pinch zoom, one-finger drag pans; a tap and
  a pan must not be confused, so a tap counts only under a small move threshold *(guess)*.
- Phone: zoom matters more than on PC, because small targets must stay tappable; portrait or landscape follows the
  scene art.
- A scene is 5-15 min on both, and it saves its finds *(guess)*.

## Later

- More scenes and larger illustrations.
- A story that connects the finds.
- Inventory puzzles that unlock new parts of a scene.
- A rotatable diorama with finds hidden by depth.
- Stronger hints for the spots where players get stuck.
- A scene editor with shared puzzles (sharing needs a server).

## In a mashup

The hidden-object half leads the target list and the search. A detective half leads what the found evidence proves.
A point-and-click half leads inventory and locks. A word half turns target descriptions into riddles. A cozy half
leads the pace and atmosphere, while the search gives the player a reason to look closely.
