# Board and abstract

Chess, go and other board games, with an AI opponent; the core verb is move a piece.

**Camera (Unity):** one fixed orthographic camera with the board or table filling the screen; a fixed perspective
camera for a 3D board on a table. A first slice is one full game against the AI, or one deal of a solo card game.

Thin research: no sourced entry for lighting a piece's legal moves, taking a move back against the AI, or an AI
that plays at the player's level.

## Defaults

None sourced yet. The rules live in a pure C# Core solver (unity-architecture), so the AI search can run off
the main thread or spread over frames and never stalls a frame.

## Feel

- **read-the-board**: The AI moves after a short, steady pause, its move stays marked until you have moved,
  and one input lights your pieces under attack and the places it threatens. Why: the player sees what changed
  and what is coming, so a loss is a misread they could have seen. Break it when: an expert game with every aid off.
- **piece-snap**: A held piece lifts with a shadow, a drop a little off still lands in the nearest legal place
  with a click, and a capture knocks the taken piece aside with a heavier sound. Why: moving a piece feels like
  the real thing, and a sloppy drop is never a wrong move. Break it when: moves are typed or picked from a list.
- **count-up**: Where the game scores, the count plays out one item at a time, each a step higher in pitch, and
  a solitaire's last cards fly home in a rising run. Why: the total builds where the player can follow it. Break
  it when: nothing is counted, a game won by one position, as chess is by checkmate.
- **game-end**: The end is shown on the board: the winning line lit or the beaten king tipped over, a short
  fanfare, then a rematch on one press. Why: the win lands, and the next game is one press away. Break it when:
  an endless solo game that never ends.

## Variants

- **classic**: A known game at full size, a strong AI, time to think.
- **luck**: Dice or a shuffled deck, the odds shown, a bet or a bluff.
- **calm**: A patience game with no opponent and no clock, each move putting a little more in order.

## Choices that shape the pitch

- **The game:** a known game played by its rules, chess, draughts or reversi (default) · a new abstract game
  with a few simple rules · a classic card game, solitaire or poker.
- **Opponent:** an AI at a level the player picks, that makes small human mistakes (default) · no opponent,
  a solo game · two players taking turns on one device.
- **Luck:** none, pure skill (default) · dice with the odds shown · hidden cards and bets.
- **View:** the board from above, fixed camera (default) · a 3D board on a table.
- **Feeling:** the player feels clever by seeing a few moves ahead and watching the plan work, because the board
  showed every threat and the AI played fair.

## Platforms

- PC and touch play the same: drag or tap-then-tap a piece on the Pointer; tap-then-tap is the safer default on
  small screens, since a finger hides the piece it drags.
- Phone: portrait for a square board, landscape for a card table *(guess)*.
- Session: one game is 5-20 minutes; save the position on `OnApplicationPause` so a phone call does not lose it.

## Later

- Online play and a rating (needs a server)
- A book of set positions to solve
- A hint that names the best move, and a review of the game after
- A clock for each side
- Variants and house rules
- Rule-changing rewards for a master of the game
- An opening book and endgame tables for a strong AI
- A board game inside a bigger game, found while exploring

## In a mashup

The board game leads the rules, the turn and the AI's move. A puzzle leads set positions with one answer, and
the board leads how they are played. An RPG or adventure half leads the world, and the board game is found in
it. A roguelike leads a run of games, with pieces won between them. A card battler leads a duel of built decks,
and the board leads the table.
