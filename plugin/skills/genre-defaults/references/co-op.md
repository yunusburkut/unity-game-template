# Co-op

Two or more players work together against the game; the core verb is hand off and help. Like Overcooked, Deep Rock
Galactic or It Takes Two.

**Camera (Unity):** a top-down camera that keeps every player in view and zooms out as they spread; a fixed
orthographic camera for one room that fits the screen; an orthographic side view that frames all players.

**Online:** players share one screen, each seat joined through the Input System's `PlayerInputManager` (one keyboard
or gamepads); played alone, a bot partner takes the second seat. Play across machines is the coop-multiplayer pack
(FishNet + Unity Relay, host and client); a bot stand-in shows whether the idea is fun, never whether the netcode
holds.

## Defaults

- **bot-partner**: Played alone, a bot partner follows, helps and never ruins the plan: it cannot get you caught, does
  not block a door, and revives you. Why: one person can try a co-op game, and the partner feels like help, not a
  burden. Break it when: each player holds half of every puzzle, and the game means nothing without two people.
- **split-the-work**: The job is split so players need each other: one chops while one cooks, one holds the light
  while one shoots, and handing over is quick. Why: the team wins by working together, not by each doing everything.
  Break it when: a horde shooter where everyone does the same job side by side.
- **down-not-out**: A fallen player is down, not out: a partner revives them by holding a button beside them, and a
  short slip of the button does not reset it. The mission fails only when everyone is down. Why: nobody sits out
  watching, and saving a friend is a moment. Break it when: co-op horror, where a lost friend stays lost until the
  next round.

## Feel

- **rise-and-rest**: Pressure builds in waves to a peak, then lets go for a quiet moment to regroup, refill and laugh
  about it. Why: the team gets excitement without wearing out. Break it when: a calm puzzle co-op with no clock.
- **shared-credit**: A kill or a save counts for everyone who helped, not only the last hit, and the end screen shows
  each player's part. Why: teammates welcome help instead of racing each other for it. Break it when: a friendly
  rivalry inside the team is the hook, with a score each.
- **team-signals**: One input cheers and every character cheers with you; another marks a spot or an enemy with a
  sound and a marker, and a bot partner goes there. Why: players say "nice one" and "over here" without stopping to
  talk. Break it when: a horror game where every sound draws the monster.

## Variants

- **slapstick**: a busy job, things dropped and bumped, mistakes the team laughs at.
- **squad**: clear jobs, calls and pings, a mission against waves.
- **dread**: the dark, few tools, the team splitting up and calling out.

## Choices that shape the pitch

- **Work:** a busy job split into handoffs, a kitchen or a moving van (default) · a mission against waves of enemies
  · rooms where each player holds half of the puzzle.
- **Players:** two on one screen, a bot partner when alone (default) · up to four on gamepads · one player and a bot
  partner only.
- **Stakes:** revive a down partner, fail only when all are down (default) · a score at the end, no way to fail · a
  lost friend stays lost until the next round.
- **View:** from above (default) · one room on one screen · side view.
- **Feeling:** the player feels camaraderie by reviving a partner just in time and getting a cheer back, because
  helping is easy and each player's part shows on the end screen.

## Platforms

- PC: two players on one keyboard (WASD and arrows) reach only a few inputs each; gamepads carry the full set.
- Phone: one player per device, so a phone game is solo with the bot partner, or online through the pack. Landscape.
- A round is 3-8 min on both *(guess)*.

## Later

- Online co-op across machines, with drop-in (the coop-multiplayer pack; matchmaking needs a server).
- Voice in the game space, voices that change or cut out in trouble (needs a server).
- Split screen, each player with their own view.
- Monsters that hear the players' microphones.
- New shared tools chapter by chapter.
- A director that reads how the team is doing and changes the pressure.
- Help left for strangers who play later (needs a server).

## In a mashup

Co-op leads the team: roles, revives, the bot partner and shared credit. A shooter leads aiming and the enemies.
Horror leads the threat and what the team cannot see, and co-op leads rescue and recovery. Management leads the
orders and the clock in a kitchen job. A platformer or puzzle half leads movement or rules, and co-op gives each
player half of the tools.
