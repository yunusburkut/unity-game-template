# Fighting

Head to head with a move set, life bars and rounds; the core verb is read the opening and punish it. Like Street
Fighter, Tekken or Smash Bros.

**Camera (Unity):** a fixed orthographic camera for one stage that fits the screen; an orthographic side view that
keeps both fighters in frame for a wider stage; a perspective side camera for a 3D fighter.

## Defaults

- **rounds-and-bars**: Mirrored health bars in the top corners with a round timer between them, best of three rounds,
  then a winner screen. Why: the state of the fight reads at a glance, and a lost round is not a lost match. Break it
  when: a platform fighter, where damage builds up and a fall off the stage decides.
- **cpu-rival**: The computer fights at a level picked on the title screen: it reacts after a short, human delay,
  blocks some of the time and never reads a press before it happens. Why: a rival that can be beaten and still feels
  like a person. Break it when: the game is for two players only.
- **move-list**: The pause screen lists each fighter's moves and inputs, and every special also has a one-button
  shortcut. Why: a new player finds and throws the special in the first round. Break it when: every move is already
  one button, a party brawler with nothing to look up.

Variety floor (hypothesis): 1 opponent with a full set of moves in the first slice. [street-fighter-2]

## Feel

- **light-and-heavy**: A light attack comes out at once; a heavy winds up, commits you and hits hard; every press shows
  its pose straight away. Why: the choice between quick and safe or slow and strong is felt in the hands. Break it
  when: everyone shares one simple attack, a party game for people who never played a fighter.
- **forgiving-inputs**: A special is a short direction-then-button motion that forgives small slips, and a press made
  just before a move ends comes out the moment it ends. Why: the move the player meant is the move they get. Break
  it when: specials are one direction and one button, as in Smash Bros.
- **face-and-block**: Fighters always turn to face each other; holding away blocks with a solid guard sound and a
  small slide back, and a blocked heavy leaves its user open for a moment. Why: defence is a choice from the first
  exchange, and a careless heavy costs. Break it when: fighters roam an open arena and dodge instead of facing off.

## Variants

- **combo**: quick walks, short moves, light into heavy into special.
- **heavy**: slow, big blows that commit; a few clean hits win a round.
- **duel**: a well-timed block turns into a counter and breaks the other's guard.

## Choices that shape the pitch

- **Format:** one on one on a flat stage, bars and rounds (default) · a platform fighter where hits build knockback
  and a fall off the stage loses a life · a weapon duel where a few clean hits win.
- **Opponent:** the computer (default) · a friend on the same keyboard or a gamepad · a ladder of computer rivals.
- **Fighters:** two who play differently, picked on a select screen (default) · the same fighter on both sides.
- **View:** 2D side view (default) · 3D from the side, with a sidestep.
- **Feeling:** the player feels sharp mastery by blocking a heavy and punishing it, because the opening was readable
  and the counter came out on the press.

## Platforms

- PC: gamepads are the real target. Two players on one keyboard hit key rollover limits (many keyboards drop some
  key combinations held at once), so test the two key sets together.
- Touch: a left virtual stick and 2-3 buttons, with one-tap specials; motion inputs do not survive glass *(guess)*.
  Phone: landscape.
- A match is 1-3 min on both *(guess)*.

## Later

- Online versus with rollback, ranked ladders and matchmaking (needs a server).
- A bigger roster of fighters.
- A super meter that fills as you fight.
- A training mode with an input display.
- Long combos, juggles and cancels.
- An arcade ladder with a story for each fighter.

## In a mashup

Fighting leads the duel: moves, blocking, inputs and rounds. Sports leads scoring and the field, and fighting leads
command input, recovery and defence, kept the same for both sides. A beat 'em up leads the crowd and the stage, and
fighting leads a boss duel. An RPG leads progression between fights. Rhythm leads timing, and inputs are never
delayed to land on the beat.
