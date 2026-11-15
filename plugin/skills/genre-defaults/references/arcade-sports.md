# Arcade sports

A sport stripped down to fast, exaggerated play (NBA Jam, Mario Tennis, Windjammers). Core verb: hit or
shoot the ball at the right moment.

**Camera (Unity):** a fixed orthographic camera that frames the whole court when it fits; an orthographic
side view that follows the ball for a wider pitch; a fixed-angle perspective camera for a 3D court.

## Defaults

- **short-match**: First to a few points or a short clock. Score and time are big on screen. A results
  screen ends the match. Why: one match is one sitting, and the score shows who leads at a glance. Break
  it when: a season or a league is the point.
- **catch-up**: The trailing side gets a small, visible boost (a hotter shot, a quicker player). It ends
  when the score is level. Why: the match stays open to the final whistle. Break it when: the user wants
  a strict, even duel of skill.

## Feel

- **sweet-spot**: A hit timed to the right moment goes stronger and straighter, and the moment shows
  where the ball meets the hand, foot or racket. Why: timing wins points, not button mashing. Break it
  when: the sport has no timed hit (running and tackling).
- **buffered-actions**: A pass or shot pressed a moment early fires when the ball arrives. A block or
  dive pressed near the right moment counts. Why: intent wins, not an exact frame. Break it when: exact
  timing is the whole challenge (a hardcore sim).
- **power-shot**: Hold to charge a shot that glows and hums; release sends the ball fast with a trail
  and a whoosh. Why: the big exaggerated shot makes it arcade. Break it when: every shot must be
  realistic.
- **instant-pose**: A press snaps the player into the swing, jump or dive at once; the rest of the move
  plays after. Why: a late hit is the player's timing, not the game's. Break it when: slow floppy bodies
  are the joke (a physics sport).

## Variants

- **flowing**: passes and moves link into one long play, a combo you keep alive.
- **duel**: one against one, reads and counters, every shot answered.
- **slapstick**: tackles send players tumbling, the ball surprises.

## Choices that shape the pitch

- **The sport:** a ball over a net, tennis or volleyball (default) · a goal at each end, a few players a
  side · a made-up sport with one strange rule.
- **Players:** you against the AI (default) · two players on one device (local) · two of you against
  the AI.
- **View:** the whole court (default) · a side view that follows the ball · a 3D court from a set angle.
- **Feeling:** the player feels kinetic flow by stringing passes and shots into one play, because each
  press lands at once and a well-timed hit pays off.

## Platforms

- Keyboard+mouse: move on WASD or arrows, hit and power on two keys; the mouse does little here. Gamepad
  fits best, and local two-player needs two gamepads or a split keyboard (PlayerInputManager).
- Touch (Pointer): swipe direction and length set the shot; a tap times the hit *(guess)*. Landscape on
  phones.
- Session: a match of 2-3 min fits a phone; PC players chain matches *(guess)*.

## Later

- Real teams, leagues and seasons.
- Teammates who play positions and tactics.
- Bodies that tumble and get up with physics.
- A commentator.
- Players who improve with practice.
- A replay of a great point.
- Ranked online matches (needs a server).

## In a mashup

Sports leads scoring, the field and the match clock. Fighting leads command reads, recovery and
defence, and any help for one side is the same for both and shown. Racing leads catch-up, and it ends
when the score is level. A party game leads silly rules between matches. An RPG half leads players who
grow between matches.
