# Logic puzzle

Pure deduction on a grid of clues, from picture logic to mines (Picross, Minesweeper, sudoku). Core
verb: prove a cell, then mark it.

**Camera (Unity):** a fixed orthographic camera; the board fits the screen.

## Defaults

- **one-board-graded**: One board solved in minutes, from a few difficulties graded by the kind of
  reasoning each needs, not only by size. Why: the player picks a challenge that fits. Break it when: a
  hand-made run of boards, each teaching one technique.
- **logic-alone**: A solver proves every board can be solved by reasoning alone from the first move: a
  mine board's first click is safe, and no guess is ever needed. Why: a loss is the player's slip, never
  a coin toss. Break it when: a clearly labelled lucky mode.

## Feel

- **mark-what-you-know**: One input fills a cell, another marks it surely empty, a drag marks a whole
  run, and cells are big enough to hit easily. Why: the player writes down each deduction and builds on
  it. Break it when: cells take numbers, and notes are small pencil numbers.
- **clues-answer**: A clue greys out once its row or region is met; a rule broken by your own marks (two
  of one number in a row) shows in red. Whether a mark is right stays hidden until the board is done.
  Why: each deduction gets an answer without the game solving it. Break it when: a strict mode where
  nothing answers until the end.
- **undo-marks**: Unlimited undo, one mark at a time; restart clears the board; a fatal click on a mine
  board can be undone once. Why: a slip never ruins a half-solved board. Break it when: a strict mode
  where a mine ends the board.
- **picture-reveal**: The last right cell finishes the board at once: the picture colours in or the safe
  cells flip in a wave, with a chime and the time taken. Why: reasoning ends on a beat of payoff. Break
  it when: boards come back to back in a timed race.

## Variants

- **relaxed**: no timer, broken rules shown in red, a hint on request.
- **strict**: a timer and best times, nothing confirmed until the whole board is done.

## Choices that shape the pitch

- **The puzzle:** picture logic, number clues on rows and columns (default) · mines, where a number
  counts the hidden mines next to it · number place, each number once per row, column and box · a logic
  grid of who-owns-what clues.
- **Boards:** generated each game and proven by the solver (default) · a hand-made set, each teaching
  one technique · a daily board from the date, the same on every device.
- **Feeling:** the player feels sharp and independent by proving a cell that no single clue names,
  because two clues together settle it and nothing pointed the way.

## Platforms

- Keyboard+mouse: left click fills, right click marks empty, drag for a run; Ctrl+Z undoes.
- Touch (Pointer): tap fills, a fill/mark toggle button replaces the right click, drag for a run; cells
  at least ~9 mm on screen *(guess)*. Long press is slow for the main mark. Portrait on phones; big
  boards need pinch zoom.
- Session: one board in 3-10 min fits a phone; PC players solve several *(guess)*. Save the board on
  every mark.

## Later

- Hints that point to the next deduction without giving it.
- Big boards in parts, and picture logic in colour.
- Logic grids told as a whodunit, confirmed in batches.
- A campaign of hand-made boards.
- Mixed rules on one board, or rules that change mid-board.
- Daily board times compared online (needs a server).

## In a mashup

Logic leads the board, the clues and the proof that no guess is needed. A mystery or detective half
leads the story, and a logic grid is its deduction, confirmed in batches. An adventure half leads the
world, and boards are its locks. A cozy half leads theme and pace. A roguelike half leads the run, and
what a solved board earns carries over.
