# Physics puzzle

Aim, launch or place things, and let physics solve the level; the core verb is aim and release. Like Angry Birds, Cut
the Rope, World of Goo or mini-golf.

**Camera (Unity):** a fixed orthographic camera that fits the whole level; an orthographic camera that follows a long
shot and pans back; a perspective camera behind the ball for 3D golf.

## Defaults

- **same-shot-same-result**: Physics runs in `FixedUpdate` on the fixed timestep (the default simulation mode), never
  tied to the frame rate, and shots are applied there too (Core still steps in `Update` for aiming, scoring and the
  win check; only the body write sits in `FixedUpdate`, the exception `unity-architecture` names under The split), so
  the same shot does the same thing on the same build.
  Each level keeps a recorded clear, the input that solves it, because no solver can search physics. Across devices
  the result can still differ *(verify)*. Why: a puzzle the player can solve twice, where luck never decides. Break it
  when: chaos is the fun, a sandbox of things to topple. [box2d-1], [matter-1], [fiedler-1]
- **settle-then-judge**: A shot is judged only once every body has come to rest (asleep), so a tower still wobbling
  can still fall, and a retry resets the level at once. Why: the result is what the physics did, and a miss costs
  seconds, not a menu. Break it when: a clock judges the level, a race against time. [box2d-1], [limbo-5]
- **rated-clear**: Any clear wins the level, and a better one (fewer shots, more knocked down) earns a higher rating
  shown on the level select. Why: everyone moves on, and a player who wants more has a reason to replay. Break it
  when: a calm puzzle where any answer is enough. [angry-birds-1]

## Feel

- **aim-preview**: Dragging back aims and sets power, with a dotted line that shows the first part of the flight.
  Why: the player aims by eye and learns the arc, but the landing stays theirs to judge. Break it when: reading the
  arc is the challenge, golf with only a power bar.
- **launch-and-follow**: The launch stretches and snaps with a whoosh, and the view follows the shot, then pans back
  to the level. Why: the player watches their own shot play out. Break it when: the level fits one screen and the
  shot never leaves it.
- **material-crash**: Wood, glass, stone and rubber each sound and break their own way, and a tower falls in a way you
  can read from what held it up. Why: the player learns which piece to hit by watching it fall. Break it when: there
  is one kind of material, a clean abstract puzzle.

## Variants

- **wrecking**: towers that crash down, chain reactions, a score for the wreck.
- **clever**: one exact answer found by a trick, a rope cut at the right moment.
- **golf**: a ball, a course of holes, strokes against par, slopes and walls to bank off.

## Choices that shape the pitch

- **What you do:** launch at a tower to knock it down (default) · cut, drop and swing things so they land in a goal ·
  hit a ball into a hole in few strokes · build a bridge from pieces that hold each other up.
- **Stakes:** a few shots per level, stars for fewer (default) · unlimited tries, a score for the best · par per hole
  over a round of holes.
- **View:** the whole level on one screen (default) · a view that follows the shot · 3D behind the ball.
- **Feeling:** the player feels clever satisfaction by watching a tower fall exactly as planned, because the shot was
  aimed by eye and the physics did what they predicted.

## Platforms

- PC: drag back with the mouse and release. Touch: the same drag with one finger (Pointer), so the verb maps one to
  one; keep the drag start off the target, so the finger does not hide it.
- Phone: landscape for wide towers and courses; portrait for a vertical drop puzzle.
- A level is under a minute on both, and a session is a few levels *(guess)*.

## Later

- Ropes, joints, vehicles and soft bodies beyond simple rigid bodies.
- A level editor that requires a recorded clear before a level is shared (sharing needs a server).
- Worlds of hand-made levels.
- Shots with special powers: split or explode.
- Wind and moving targets.
- Best scores shared online (needs a server).
- Full 3D golf with clubs, lie and wind.

## In a mashup

The physics puzzle leads the shot, the physics and how a level is judged. Puzzle leads the level's one idea and its
teaching, and a recorded clear proves each level. A platformer half leads movement, and the physics serves the
level. A sandbox leads free building, and the goal becomes optional. A sports half leads the ball and the score,
mini-golf or a trick-shot contest.
