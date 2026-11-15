# Grid puzzle

Push blocks onto targets (Sokoban); a wrong push can make the level unsolvable. The core verb is the push.

**Camera (Unity):** one static orthographic camera sized to fit the whole level (default); an orthographic camera
that follows the player for a level bigger than the screen; or a fixed-angle perspective view of a 3D grid.

## Defaults

- **few-teaching-levels**: A handful of hand-made levels in order: the first teaches the push where nothing can go
  wrong, each next one adds or twists one thing, the last combines them, and solved levels are kept. Why: the player
  learns every rule by pushing, never from text. Break it when: one big level, or a fresh generated puzzle each day.
- **board-shows-rules**: Walls, pushable pieces and targets each look like what they are, and a target lights up
  when covered. Why: the player plans from what they see, so the answer is fair. Break it when: finding out what
  things do is the discovery, hidden rules learned by trying.
- **solver-proof**: Every shipped level has a solution on record (a solver run or a recorded move list). Why: an
  unsolvable level is a [yüksek] bug, the player cannot progress. Break it when: never.

## Feel

- **crisp-steps**: Each press moves one square in a quick slide that lands with a soft thud, a held key repeats
  steadily, and a press during a move is buffered for the next. Why: moves come as fast as the player thinks them.
  Break it when: slowness is the theme, a heavy stone that takes effort to shove.
- **undo-every-push**: Undo has no limit and takes back one move with all it pushed; restart is separate, and undo
  brings a restart back. Both are shown on the first level. Why: a bad push costs nothing, so the player tries ideas.
  Break it when: the user wants a strict move limit with no take-backs.
- **dead-end-shown**: A push that makes the level unsolvable (a box in a corner) is noticed: the box dims and a quiet
  prompt offers undo. Why: the player never keeps pushing in a level that can no longer be won. Break it when:
  spotting your own dead end is the challenge, a strict mode the user asked for.
- **eureka-solve**: Each level turns on one fair surprise about a rule the player thought they knew; once seen, the
  solution is a few moves. The last box rings and the next level opens at once. Why: the insight is the reward.
  Break it when: the levels are calm tidying with no trick.

## Variants

- **clever**: small boards, few pieces, one surprising move a level.
- **wordplay**: the rules are word tiles on the board; pushing them into new sentences changes what things do.
- **cozy**: gentle levels about putting things where they belong, each push tidying a little more.

## Choices that shape the pitch

- **The pieces:** boxes onto targets (default) · rules as word tiles · pieces longer than one square that roll and
  turn · ice, where whatever moves slides until it hits something.
- **Failure:** undo and restart, no death (default) · a move limit per level, stars for fewer moves · hazards that
  end the level, taken back with one undo.
- **View:** the whole level at once (default) · a bigger level that scrolls · a 3D grid from a fixed angle.
- **Feeling:** the player feels eureka by seeing that a rule they trusted works another way, because the levels
  taught it fairly and undo made every try free.

## Platforms

- PC: arrow keys or WASD for one step, Z (or Ctrl+Z) to undo, R to restart.
- Touch: a swipe is one step, held swipe repeats; undo and restart are big buttons in thumb reach *(guess)*. Tap a
  square to path there is a later option, never a replacement for the swipe *(guess)*. Portrait.
- Session: one level is 1-5 min, so a phone session is a few levels; PC players chain many. Save on every solve.

## Later

- Hints that nudge without giving the answer
- A move count and a par per level
- Optional harder levels hidden in plain sight
- Many worlds of hand-made levels
- A story told through the levels
- A level editor where a level saves only once cleared
- Two players pushing together with different moves

## In a mashup

The grid puzzle leads the rules, undo, the order of levels and the solver's proof that each level can be won. A
platformer half makes it a puzzle-platformer, where movement serves the grid and never skips it. A dungeon or
roguelike half leads the run, and each room's lock is a small push puzzle. A story half leads what the levels mean.
A cozy half leads theme and pace, and the puzzles turn to tidying.
