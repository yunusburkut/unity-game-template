# Tower defense

Place towers to stop waves before they reach the goal (Bloons TD, Kingdom Rush, Plants vs. Zombies).
Core verb: place a tower, then watch the wave meet it.

**Camera (Unity):** an angled perspective (or orthographic) camera you pan and zoom; a fixed camera when
the whole map fits the screen.

## Defaults

- **waves-and-lives**: Enemies come in waves along a path you can see; wave count and lives are on
  screen, and each enemy that gets through costs a life. Why: the player sees where to defend, how far
  they are, and what a leak costs. Break it when: enemies come from every side (a base in the open).
- **enemy-mix**: Enemies differ in ways towers must answer: fast ones, armoured ones, flyers that skip
  the path, a few that shield the others. Why: one tower type is never enough. Break it when: the
  challenge is only numbers (a calm game about one tower kind).
- **sell-back**: A placed tower can be upgraded, or sold back for most of its cost. Why: a misplaced
  tower is a cheap mistake, and a good spot can grow. Break it when: each placement is final on purpose.

## Feel

- **placement-preview**: A tower under the pointer shows its range circle and price, snaps into place
  with a thud, and fires at once. Why: every placement answers straight away, so building is quick and
  a mistake is plain. Break it when: nothing is placed (the defence is a hero you steer).
- **coins-fly**: Each kill pops coins that fly to the money counter, and it ticks up as they land. Why:
  the player sees the defence paying for itself. Break it when: money comes only between waves (a fixed
  budget).
- **arrivals-heard**: A wave and each strong enemy announce themselves with their own sound and a marker
  at the entrance before they come in range. Why: the player has a moment to prepare, not only react.
  Break it when: surprise is the point (hidden waves).
- **wave-breath**: The end of a wave lands with a short fanfare and a pause to build, with a button to
  call the next wave early. Why: pressure and relief come in turn, and a strong defence need not wait.
  Break it when: the waves never stop (an endless flood).

## Variants

- **planner**: a breath between waves, a few strong enemies, each placement weighed.
- **swarm**: crowds fill the path, fast waves, towers popping dozens at once.
- **hands-on**: a hero or a power you aim yourself, between the towers.

## Choices that shape the pitch

- **Where towers go:** open ground beside a set path (default) · a few fixed spots on the path · open
  ground where the towers make the path (a maze).
- **The defence:** towers only (default) · towers and one hero you move · defenders in lanes, one row
  each, against a walking horde.
- **Stakes:** lives lost to leaks, game over at zero (default) · a score for how few got through ·
  endless waves until you fall.
- **View:** an angled map you pan (default) · the whole map in one view.
- **Feeling:** the player feels ongoing planning by watching a wave break on a defence they built, then
  spotting the gap the next wave will find.

## Platforms

- Keyboard+mouse: click a tower in the bar, click to place, right click or Esc to cancel; WASD or edge
  pan, wheel zoom; number keys pick towers.
- Touch (Pointer): no hover, so drag a tower from the bar and show range and price while the finger is
  down, place on release; one finger pans, pinch zooms. Make placement spots bigger than the finger.
  Portrait for a lane game, landscape for a wide map *(guess)*.
- Session: one map (5-15 min) on a phone, with pause and a save between waves *(guess)*.

## Later

- Upgrade trees with several branches per tower.
- A map editor.
- A campaign of maps.
- A hero who levels up across maps.
- Co-op defence on one screen.
- Enemies that find a new way around your towers as you build.
- Endless mode with a shared leaderboard (needs a server; a local best score first).

## In a mashup

Tower defense leads the path, the waves and placement. The economy leads money from kills and prices.
An action half leads a hero you steer, and the towers stay where you put them. A roguelite leads the
run, offering one of a few towers after each wave. A card half leads the towers as cards in a hand.
