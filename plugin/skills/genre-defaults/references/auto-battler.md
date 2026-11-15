# Auto-battler

Buy units, arrange a team on a board and watch it fight on its own; the core verb is drafting the team.

**Camera (Unity):** one static camera (orthographic or a fixed angle) that fits the board and the shop together
(default); an angled perspective battlefield with pan and zoom for a wider field.

## Defaults

- **draft-then-watch**: Recruit a team between rounds, then the units fight with no attack input. Why: the fight
  tests the team the player chose. Break it when: the player steers a fighter in combat, an action game with
  automatic allies. [teamfighttactics-1]
- **shop-tradeoffs**: Units cost gold from a limited budget, so the opening shop asks what to leave behind. Why:
  buying everything removes the choice. Break it when: the roster is given and the puzzle is where to put it.
  [teamfighttactics-2]
- **formation-matters**: The team is arranged on the board before the fight. Why: where a unit starts is part of the
  plan. Break it when: combat has no positions, only effects that resolve in order. [mechabellum-1]
- **units-combine**: Unit abilities work with other units in the roster. Why: the team offers combinations worth
  trying. Break it when: each unit stands alone and the challenge is only its position. [superautopets-1]
- **stored-opponents**: The first slice fights opponent teams stored with the game. Why: no server, and each fight
  is repeatable to tune. Break it when: live opponents exist (needs a server).

Variety floor (hypothesis): 3 enemy kinds in the first slice, each attacking or moving differently (bosses and
elites count).

## Feel

- **planning-breath**: Shopping and arranging have no countdown; combat starts when the player says so. Why: the
  player can think a change through. Break it when: a shared round clock is part of the contest. [superautopets-2]
- **spells-read**: Abilities have visible effects that can be followed through the fight. Why: watching explains
  which part of the team worked. Break it when: combat is a text report on purpose. [teamfighttactics-3]
- **inspect-a-unit**: Selecting a unit while planning opens its ability and traits. Why: the player can check the
  rules behind a combination. Break it when: each unit's full rules already fit beside it. [teamfighttactics-4]

## Variants

- **planner**: untimed preparation, then watch the formation work. [superautopets-2], [mechabellum-1]
- **combo**: recruit units for how their abilities work together. [superautopets-1]

## Choices that shape the pitch

- **The team:** units bought between rounds (default) · a fixed roster to arrange · items on a board that fight
  through their effects.
- **Positions:** a board with a front and back (default) · an ordered line · a wide field of squads.
- **Stakes:** a short run against stored teams (default) · an isolated formation puzzle · live players (needs a
  server).
- **View:** board and shop together, static (default) · an angled battlefield with pan and zoom.
- **Feeling:** the player feels clever by choosing a team whose abilities work together and seeing it win, because
  the fight shows each ability in the order it goes off. [superautopets-1]

## Platforms

- PC: click to buy, drag to place, a key or button to start the fight.
- Touch: tap to buy, drag to place through Pointer; no hover, so inspect is a tap or a long press *(guess)*.
  Portrait fits a line or a small board; landscape fits a wide board *(guess)*.
- Session: a single round is short on a phone, a full run on PC; save between rounds.

## Later

- A larger roster and more opponent teams
- Equipment crafting and branching unit upgrades
- Interest, streak income and a shared shop pool
- Faster combat playback
- Large armies with their own pathfinding
- Live matches, ranking and uploaded opponent teams (needs a server)

## In a mashup

The auto-battler leads recruiting, placement and automatic fights. A roguelike leads the run and its rewards. A
creature collector leads who joins the roster and how they grow. A card half leads the offers in the shop. An economy
half leads income and prices; combat still tests what the player bought and where they put it.
