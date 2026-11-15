# Platformer

Run and jump past hazards; the jump is the core verb.

**Camera (Unity):** orthographic side view that follows the player, with look-ahead and a dead zone (Cinemachine
Position Composer); in 3D, a perspective third-person orbit (Orbital Follow).

## Defaults

- **instant-retry**: A fall or a hit puts you back at the last checkpoint at once: no lives, no game-over
  screen. Why: failing costs seconds, so the hard jump gets tried again. Break it when: arcade stakes are the
  point, lives and a game over.

Variety floor (hypothesis): 2 enemy kinds in the first slice, +1 kind a level.

## Feel

Numbers for every line below live in game-feel (references/numbers.md), not here.

- **forgiving-jump**: Late jumps off a ledge (coyote time), early presses just before landing (jump buffer)
  and clipped corners still count. Why: a miss is the player's mistake, never the game's. Break it when: exact,
  unforgiving jumps are the challenge.
- **jump-control**: Hold to jump higher, tap for a hop, and fall faster than you rise. Why: the player shapes every
  arc and lands soon enough to act again. Break it when: every jump is the same arc on purpose, a one-button game.
- **jump-land-juice**: Every jump and landing has its own sound and a quick squash of the body, with a puff of
  dust on a hard landing. Why: the body feels its weight without a word on screen. Break it when: the look is
  still and abstract on purpose, shapes that never bend.
- **look-ahead**: The camera shows more of where you are heading and holds still through ordinary jumps. Why:
  the next hazard is seen in time, and the screen does not bob. Break it when: each level is one room that fits
  the screen.
- **fair-hurtbox**: Only the body takes hits, never hair or cape: the hurt collider sits inside the sprite. Why:
  a near miss looks like one. Break it when: the part that can be hit is the hook, a flame or a shadow.

## Variants

- **precise**: Tight and arcade: quick to start and stop, short committed hops, fast falls.
- **flowing**: Speed builds on slopes and carries through slides and wall runs.
- **heavy**: Heavy and grounded: slow to turn, jumps with weight that land with a thud.

## Choices that shape the pitch

- **Failure:** instant retry at checkpoints (default) · lives and a game over, arcade stakes · none, exploring
  at your own pace.
- **Progression:** hand-made screens in order (default) · one connected map opened by new moves, a metroidvania
  · an endless run.
- **View:** orthographic side view that follows (default) · 3D behind the avatar, orbit camera.
- **Feeling:** the player feels precise mastery by clearing a jump they missed a moment ago, because the miss
  was their own and the retry is instant.

## Platforms

- PC: move on A/D or arrows, jump on Space; a gamepad is the natural fit.
- Touch: left/right buttons bottom-left, jump bottom-right, landscape. Precise jumps are harder on glass, so
  widen the forgiveness windows on touch *(guess)*.
- Session: a level is a few minutes on both; a phone needs a checkpoint saved on `OnApplicationPause`.

## Later

- New moves over time
- Bosses
- Collectible hunts and completion
- Checkpoints traded for rewards
- A speedrun timer and ghosts of your own best run (shared ghosts need a server)
- Two-player co-op on one screen
- A level editor

## In a mashup

The platformer leads movement and camera. Puzzle leads rules, undo and level teaching, and movement forgiveness
never lets a jump bypass the puzzle. A metroidvania leads the map and its ability gates. A roguelite leads the
run and what carries over. A management half leads money and building between levels.
