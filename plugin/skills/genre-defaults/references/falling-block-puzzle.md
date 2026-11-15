# Falling-block puzzle

Falling pieces placed so rows or groups clear before the stack tops out; also match-three swap boards
(Tetris, Puyo Puyo, Bejeweled). Core verb: move, turn and drop a piece.

**Camera (Unity):** a fixed orthographic camera; the well or the board fits the screen.

Research gap: the CCGS sources had no entry on topping out as speed rises, lock delay with a ghost piece, or
the bonus for several rows at once. Treat those numbers as open.

## Defaults

- **next-and-fair**: The next piece shows beside the well. The deal keeps the same shape from coming
  twice running and no shape missing for long (a shuffled bag). Why: the player plans one piece ahead,
  and a drought never decides the run. Break it when: the board refills from above (a swap game with
  nothing to preview).

## Feel

- **sharp-shift**: A tap moves a piece one column; a held input slides it fast after a short delay; a
  turn is instant; a turn pressed just before a piece appears is kept. Why: the hands keep up with the
  head at any speed. Break it when: one tap places a piece (a slow casual game).
- **clear-beat**: Cleared rows flash and hold a beat before the stack drops with a thud. In a chain each
  step plays in order, louder than the last, at a rising pitch. Why: the player watches the payoff they
  set up. Break it when: speed is everything (clears vanish at once).

## Variants

- **classic**: falling shapes, quick hard drops, a speed that climbs to a frantic end.
- **chain**: coloured blobs that pop in groups of one colour; setting up a cascade is the skill.
- **calm**: nothing falls and no clock runs; two gems swap on a board that refills, matches cascade.

## Choices that shape the pitch

- **Pieces:** four-square shapes that clear full rows (default) · coloured blobs that pop in groups ·
  gems swapped into rows of three on a board that refills.
- **Stakes:** endless until the stack tops out, for a best score (default) · a sprint to clear a set
  number of lines · a set number of moves to reach a score.
- **Opponent:** none (default) · a bot whose clears push garbage rows into your well · two players on
  one device, each clear sending garbage to the other.
- **Feeling:** the player feels a clutch rescue by clearing a tall stack just below the top, because the
  danger was plain and one big clear turned the run.

## Platforms

- Keyboard+mouse: arrows or A/D to shift, two keys to turn, Down for soft drop, Space for hard drop.
  Keys, not the mouse, for falling pieces; a swap board plays with the mouse.
- Touch (Pointer): drag to shift by column, tap to turn, swipe down to drop; a swap board is a drag
  between two cells. Portrait on phones.
- Session: 2-5 min runs fit a phone and a PC alike *(guess)*. Pause on OnApplicationPause.

## Later

- A hold slot that keeps one piece for later.
- Spins and other trick clears scored as specials.
- Boosters and special gems in a swap game.
- Hand-made boards to clear in few moves.
- A daily challenge with a small reward (a local daily seed from the date).
- Online versus and ranked play (needs a server).

## In a mashup

The falling-block puzzle leads the well, the input, the deal and the clear. A battle or RPG half leads
damage and enemies, and each clear sends an attack. A story half leads what happens between rounds. A
versus half leads the match, and garbage rows are the attack. A rhythm half leads the beat, and pieces
fall on it.
