# Shoot 'em up

One craft dodges and fires across a scrolling screen; the core verb is thread a gap while firing. Like Ikaruga,
Gradius or Touhou.

**Camera (Unity):** a fixed orthographic camera while the stage scrolls past underneath; an orthographic camera that
follows a craft flying freely through the stage.

## Defaults

- **waves-then-boss**: One stage of enemy waves, each new or a little harder, never a sudden spike, then a boss with
  a named bar whose named attacks change as it weakens. Why: the stage builds to a peak the player sees coming. Break
  it when: an endless score attack, waves until the last life. [nex-machina-1], [zun-2]
- **readable-patterns**: Enemy shots come in a few bright colours drawn over every effect, each pattern leaves a way
  through, and no spot on the screen is safe from all of them. Why: a hit comes from a misread, never from a shot the
  player could not see or a wall with no gap. Break it when: a few slow shots, with nothing to read.
  [nex-machina-1], [dodonpachi-1], [gungeon-1]
- **graze-pays**: Passing close to a shot without touching it scores, with a spark and a tick. Why: the player is paid
  for the risk they take. Break it when: score does not matter, a gentle shooter about surviving. [graze-counter-1]

Variety floor (hypothesis): 4 enemy kinds in the first slice, each attacks or moves differently; the boss counts.
[gradius-manual-1]

## Feel

- **tiny-hitbox**: Only a small core at the centre of the craft can be hit, and enemy shots are bright and drawn on
  top of everything. Why: a near miss looks like one, so a dense pattern is something to thread. Break it when: few,
  slow shots, a gentle shooter where the whole craft is fair to hit. [significant-bits-1]
- **steady-stream**: Holding fire shoots a steady stream, and the craft moves the moment input arrives and stops when
  it ends. Why: the hands stay free for dodging, and the craft goes exactly where the player meant. Break it when:
  shots are few and charged, a game about timing each one.
- **blink-on-respawn**: After a hit the craft comes back where it was, blinks and cannot be hurt for a moment, and the
  bullets near it vanish. Why: one mistake costs one life, never two in a row, and never a stretch to replay. Break
  it when: one hit ends the run on purpose, a one-life score attack. [zun-1], [sine-mora-1]

## Variants

- **classic**: a few aimed shots at a time, enemies in set formations, power-ups that carry the run.
- **bullet-hell**: dense, patterned walls of shots, a tiny core, a slow input to weave through.
- **score-chase**: quick chains of kills raise a multiplier, so you fly close and fast.

## Choices that shape the pitch

- **Direction:** scrolls upward, the craft at the bottom (default) · scrolls sideways · one screen where the enemies
  come to you (see arcade-classic).
- **Shot:** pickups that power it up (default) · a colour switch that absorbs shots of your colour · weapons picked
  before the stage.
- **Dodging:** a tiny core (default) · a slow input that also shows the core, for dense bullet hell.
- **Failure:** a few lives, then game over (default) · a health bar and checkpoints · one life, for a score attack.
- **Feeling:** the player feels clutch survival by threading a gap in a wall of bullets, because the core is tiny and
  the bomb is there if it fails.

## Platforms

- PC: WASD or arrows move, a held key fires, Shift slows, another key bombs. Touch: the craft follows the finger's
  drag delta (relative, never under the finger), fire is automatic, and a button bombs *(guess)*.
- Phone: portrait for a vertical scroller, landscape for a side scroller.
- A stage is 3-6 min on both *(guess)*.

## Later

- More stages, each with its own boss.
- Score systems: grazing, chains and rank.
- Two players on one screen.
- Ships with different shots, picked at the start.
- A local high-score table with initials.
- A playable credits finale.
- Online leaderboards (needs a server).

## In a mashup

The shoot 'em up leads the craft, the shots and the patterns, and keeps aim and threats readable as anything else
grows. A roguelite leads the run and the upgrades between stages, and combinatorial pieces lead the build. Rhythm
leads timing, and patterns fire on the beat. A survivors-like leads the build and the horde, and the shoot 'em up
keeps the aimed fire. A story leads the scenes between stages.
