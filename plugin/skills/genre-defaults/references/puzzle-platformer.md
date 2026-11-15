# Puzzle platformer

Platforming where each level is a puzzle to solve (Braid, Limbo, Fez, Monument Valley). Core verb: move
and jump to change the level's state.

**Camera (Unity):** an orthographic side view that follows the player; a fixed orthographic camera when
the level fits the screen; a fixed-angle perspective (or orthographic isometric) camera for a 3D level.

## Defaults

- **one-idea-a-level**: Each level is built around one idea: shown first where it is safe, then used,
  then twisted with something already learned. Why: the player learns the rule by playing, never from
  text. Break it when: one big open level of mixed ideas.
- **fair-jumps**: Jumps forgive a late or early press (coyote time, jump buffer; numbers in game-feel),
  but a gap the puzzle blocks is always out of reach, and every surface you can stand on looks the
  same. Why: the player solves with the head, never by a lucky jump. Break it when: the exact jump is
  the puzzle (a precision platformer).

## Feel

- **undo-anything**: Undo is one input with no limit and takes back a move and all it caused; restart is
  another input, and undo brings a restart back. Both are taught on the first screen. Why: trying an
  idea costs nothing, so the player experiments. Break it when: each try is a run through traps (use
  instant retry instead).
- **no-dead-ends**: A level never becomes unsolvable in silence: a stuck position shows a quiet restart
  prompt, and a death puts you back at the puzzle start at once. Why: the player never works on a level
  that can no longer be solved. Break it when: a strict challenge replayed from the menu.
- **rules-visible**: Every object that matters looks like what it does: a switch and its door share a
  colour or a line, and cause and effect animate. Why: the player reasons from what they see, so the
  answer is fair. Break it when: finding out what things do is the discovery.
- **eureka-click**: The solving move lands with a clear sound and the exit lights at once; the walk from
  the idea to the door is short. Why: the insight is the reward, not the chores after it. Break it
  when: the escape after the idea is the point (a timed run out).

## Variants

- **thoughtful**: no hazards and no clock, time to think, undo on every move.
- **eerie**: traps that kill at once, instant retry, a world that teaches by danger.
- **flowing**: momentum and bounces are part of the answer, puzzles solved on the move.

## Choices that shape the pitch

- **The twist:** push blocks and switches in a side view (default) · turn the world to change what
  connects · two characters with different moves, swapped with one input · rewind time as a move.
- **Failure:** undo and restart, no death (default) · traps that kill and instant retry · a few lives
  per level.
- **View:** a side view that follows (default) · the whole level at once · a 3D level from a set angle
  you can turn.
- **Feeling:** the player feels eureka by seeing the answer all at once after a few wrong tries, because
  the rule was taught fairly and undo made trying free.

## Platforms

- Keyboard+mouse: arrows or WASD, Space to jump, Z or Ctrl+Z to undo, R to restart.
- Touch (Pointer): left/right buttons and a jump button, undo and restart always on screen; a turn-the-
  world puzzle plays well with drag and tap (Monument Valley). Landscape for a side view, portrait for
  a static 3D diorama *(guess)*.
- Session: a level of 1-5 min; phone players stop between levels, so save on each clear *(guess)*.

## Later

- Hints that nudge without giving the answer.
- Hidden extras behind harder optional puzzles.
- A level editor with a required clear before sharing.
- Two-player co-op with tools that only work together.
- A story told through the levels.
- Many worlds of hand-made levels.
- A speedrun timer.

## In a mashup

The puzzle leads rules, undo, level teaching and the solution check; the platformer leads movement and
camera, and its forgiveness never lets a jump bypass the puzzle. A story half leads what the levels
mean. A metroidvania leads the map, and puzzles guard its gates. A physics half leads objects that move
on their own, and each level is checked by a recorded clear.
