# Skate and surf

Ride a board or a wave, chain tricks and keep a line going for score; the core verb is chain.

**Camera (Unity):** perspective chase camera behind the rider (Cinemachine Follow with damping); an orthographic
side view that follows the rider for a 2D one.

Thin research: sourced entries cover the manual and revert that carry a combo, speed from slopes and grind routes,
not flips and grabs on a press or a timed run with listed goals.

## Defaults

- **bank-on-landing**: Tricks chain into a combo whose points and multiplier grow on screen; a clean landing
  banks it, a bail loses it, and the same trick twice in one combo scores less. Why: every combo is a gamble on
  one more trick, and variety pays. Break it when: a calm ride with no score, surfing for the view.

## Feel

- **keep-the-line**: A balance move on flat ground, a manual or a carve along the wave's face, keeps a combo
  alive between ramps and rails, with a balance meter that tips if held too long. Why: the whole park becomes
  one route. Break it when: each trick is scored on its own, a contest of single jumps.
- **forgiving-landing**: Landing near level counts as clean and snaps the board straight, a sloppy landing is
  a wobble, not a bail, and a bail rights you in a moment. Why: tricks are tried, not feared. Break it when:
  a sim where every landing must be exact is asked for.
- **slopes-give-speed**: Dropping into a ramp or down a wave's face builds speed, and a pump at the bottom
  carries it on. Why: speed is earned from the ground, so a line has a rhythm. Break it when: speed is set,
  a side-view run that scrolls on its own.
- **rail-catch**: A rail or ledge close under the board catches a grind on a press, with a scrape that runs
  while you hold it. Why: catching a rail feels sure, so lines are planned, not hoped for. Break it when:
  surf or snow with no rails, where the wave's lip or a log takes that part.

## Variants

- **arcade**: Big air, quick spins, tricks on a press, combos across the whole park.
- **flowing**: No clock, long carves on a wave or a slope, style over points.
- **timing**: Each trick lands on a press made just before touchdown, and a perfect press scores more.

## Choices that shape the pitch

- **What you ride:** a skateboard in a park (default) · a surfboard on a moving wave · a snowboard down a
  mountain · a bike.
- **Stakes:** a timed run for score and goals (default) · a race downhill, with tricks filling a boost · a
  free ride with no clock.
- **View:** behind the rider, chase camera (default) · a side view.
- **Feeling:** the player feels kinetic flow by linking a grind, a manual and a ramp into one combo, because
  the balance move keeps the line alive and the landing forgives.

## Platforms

- PC: a gamepad is the genre's home; on keyboard, WASD steers and four keys hold flip, grab, grind and manual.
- Touch: steer by drag on the left half, tricks by swipe direction on the right, hold to grind *(guess)*;
  landscape for the chase view, portrait for a side-view 2D one *(guess)*.
- Session: a timed run is about 2 minutes on both.

## Later

- A park editor
- A career of parks and pro goals
- Real board physics with flips and spins
- A rider and board to dress up
- Music that builds with the combo
- Two players taking turns on one screen, copying each other's tricks
- Shared high scores (needs a server)
- Online sessions (needs a server)

## In a mashup

Skate leads movement, tricks and the combo score. A racing half leads the course and the rivals, and tricks fill
the boost. A platformer half leads the level's goals, and the board is how you move. A level-maker half leads
the park editor. An arcade-classic half leads one screen and the high score.
