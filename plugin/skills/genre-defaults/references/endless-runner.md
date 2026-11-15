# Endless runner

The character runs forever; the player jumps, slides or turns.

**Camera (Unity):** orthographic side view that follows the runner, with the runner toward the back of the screen;
for a 3D lane runner, a fixed perspective camera behind and above the runner.

## Defaults

- **best-distance**: The distance counts up at the top, the best distance is saved between visits, and one press
  runs again at once. Why: a run is short, and the next one can beat it. Break it when: a runner with set levels
  and an end, scored by stars.
- **fair-chunks**: The path is hand-made chunks joined in a new order, each one passable at the current speed,
  and the first stretch is always safe. Why: every death is the player's, never an impossible gap. Break it when:
  one hand-made course learned by heart.

## Feel

- **speeds-up**: The run starts slow and gets faster step by step until the player fails, and the view widens
  a little as it does (less with reduced motion). Why: the same few moves get harder with nothing new to learn,
  and the speed is felt. Break it when: a calm runner at one speed, where harder chunks bring the challenge.
- **forgiving-jump**: Late jumps off an edge and early presses before landing still count, and holding jumps
  higher. Why: a miss at full speed is the player's mistake, never the game's. Break it when: each press must
  land on the beat, a rhythm runner.
- **read-ahead**: Each obstacle kind asks for one move, a jump over low ones and a slide under high ones;
  its shape says which, and it comes into view in time to react. Why: the player reads and reacts instead of
  guessing. Break it when: one move only, where every obstacle is jumped.
- **run-rhythm**: Footsteps keep time with the speed, and every jump, slide and landing has its own sound and a
  quick squash of the body. Why: the run has a beat the player falls into. Break it when: the runner is a still
  shape on purpose, an abstract line that never bends.

## Variants

- **tight**: Snappy jumps, fast falls, short runs.
- **flowing**: Speed carries through slides and drops in long, smooth lines.

## Choices that shape the pitch

- **Movement:** a side view where one input jumps (default) · three lanes from behind, with left, right, jump
  and slide · a jetpack or a gravity flip held to rise.
- **Stakes:** one hit ends the run (default) · a first hit slows you and a chaser closes in, a second ends it
  · a few hearts.
- **Pickups:** coins along risky lines, for the score (default) · none, distance only.
- **View:** from the side, orthographic follow (default) · from behind, fixed perspective.
- **Feeling:** the player feels responsive precision by threading a gap at top speed, because the jump forgives
  a late press and the obstacle was readable in time.

## Platforms

- PC: Space or Up jumps, Down slides, Left/Right change lanes.
- Touch: one-input runners take a tap anywhere (Pointer press); lane runners take swipes, with the swipe threshold
  in dp (platform-targets). Portrait suits a lane runner, landscape a side view.
- Session: a run is about a minute; the phone is the home of this genre *(guess)*.

## Later

- Coins spent on characters and upgrades
- Missions and daily goals (local, from the date)
- Power-ups like a magnet or a shield
- Scenery that changes the further you run
- Online leaderboards and ghosts (needs a server)
- A level mode with an end

## In a mashup

The runner leads the generated path, the speed and the score. A platformer leads the jump and its forgiveness. Rhythm
leads timing, and obstacles land on the beat. A roguelite leads upgrades between runs and what carries over. A
racing half leads the rivals, and the runner leads the path.
