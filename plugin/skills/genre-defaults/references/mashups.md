# Two genres in one idea

Read this when the idea joins two or more sheets. A mashup takes the lines of every joined sheet, then settles each
system on its own. One genre does not run the whole game. Each sheet's "In a mashup" paragraph says what that genre
leads.

## Who leads which system

The user's words lead first. Without them, each system has one leader:

- **Input and camera:** the genre whose verb the player repeats most.
- **Death, checkpoints and saving:** the genre whose stakes the idea wants.
- **Progression, builds and economy:** the genre whose decisions shape the run or the day.
- **Rules** (what a move does, what wins, undo): the genre that owns the puzzle or the duel.
- **Enemies and threat:** the genre whose danger the idea is about.
- **Structure** (levels, runs, days, one open place): the genre that sets the session shape.
- **Who acts and who talks**, when more than one person plays: the genre with the social format.

A look, a theme or a setting decides none of these. Record the result as one DESIGN.md Decisions line:
`YYYY-MM-DD: Leads: input/camera <genre>, rules <genre>, ... Why.` For each led system, take that genre's lines and
leave out the other genre's lines about it. Never drop a genre's lines wholesale.

## The seam

The seam is the one moment where one parent's verb changes the other parent's system. The first spec card's slice ends
on the seam, so the seam works before either half is built alone. Examples:

- `platformer` + `grid-puzzle`: a jump lands on a tile that moves the puzzle's pieces.
- `rhythm` + `action-roguelite`: an attack on the beat fills the meter that picks the run's next song.
- `turn-based-strategy` + `management-tycoon`: a worked tile's goods reach a market whose prices a law changes.

DESIGN.md Look takes something from each parent: the figures, ground or palette its players know it by.

## Known mashups

Each line: who leads what, then the Watch item that breaks first.

- `platformer` + `grid-puzzle` or `logic-puzzle`: platformer leads movement and camera; the puzzle leads rules, level
  teaching, undo and the solution check. Watch: forgiving movement never lets a jump skip the puzzle. (`puzzle-platformer`
  is this blend as one sheet.)
- `metroidvania` + `detective`: metroidvania leads traversal and the joined map; detective leads evidence and what
  knowing opens. Watch: tell an ability you lack apart from a rule you could already work out.
- `action-rpg` or `soulslike` + `character-action`: action leads timing, targeting and camera; the RPG leads builds,
  levels and gear; the stakes lead checkpoints. Watch: hits and survival still matter after upgrades.
- `twin-stick-shooter` + `action-roguelite` or `survivors-like`: shooting and movement lead the feel; combinations
  lead the build; the run leads what is kept and lost. Watch: aim and threats stay readable as builds grow.
- `roguelike-deckbuilder` + `tactical-rpg`: tactics leads space and enemy intent; the deck leads draw, removal,
  exhaust and the build. Watch: show exactly what an action does; a card spent for the fight looks different from one
  gone for good.
- `city-builder` + `action-roguelite`: the city leads placement, workers, services and what is going wrong; the run
  leads endings and what carries over. Watch: a clear ending without a throwaway city.
- `survival-crafting` + `cozy-cleanup` or `sandbox`: survival leads needs and the danger outside; cozy building leads
  placement and decorating. Watch: the player chooses how much danger reaches home.
- `farming-life-sim` + `management-tycoon`: the life sim leads the day and the people; management leads the flow of
  goods. Watch: stopping after a day stays safe.
- `stealth` + `physics-puzzle` (a heist with destruction): stealth leads what is known and seen; the heist leads
  planning and committing; destruction leads changing the route. Watch: the switch from plan to escape is clear, and
  what the player broke stays broken.
- `survival-horror` + `first-person-shooter`: horror leads what you can know and the tension; the shooter leads aim and
  gun feedback; survival leads scarcity and the inventory. Watch: never stack every mercy rule, or every penalty.
- `co-op` + `survival-horror` or `party-game`: horror leads the nearby threat; co-op leads talking, rescue, each
  player's part and getting back up. Watch: comedy needs consequences everyone can follow.
- `racing` + `action-rpg` or `sandbox`: racing leads handling and fair time trials; the RPG leads progression; the
  sandbox leads things to do in the world. Watch: catch-up rules stay out of time trials.
- `arcade-sports` + `fighting`: sports leads scoring and the flow of play; fighting leads command input, recovery and
  defence. Watch: help and input tolerance are the same for both sides, and both can see them.
- `rhythm` + `character-action` or `beat-em-up`: rhythm leads timing judgement; action leads quick input and what a
  hit does; sound follows the music's clock. Watch: never delay input so the visuals land on the beat.
- `logic-puzzle` or `grid-puzzle` + `visual-novel` or `walking-sim`: the puzzle leads rules that hold; the story leads
  what a repeated action means. Watch: teach a control before its meaning changes.
- `turn-based-strategy` + `visual-novel`: strategy leads economy and territory; the characters lead stress, bonds and
  events. Watch: what the player knows stays apart from what a character knows.
- `level-maker` + `physics-puzzle` or `sandbox`: the editor leads editing, undo and checking a level before it is
  shared; physics leads the shared rules. Watch: the maker's own clear proves a route exists, not that it is fair.
- `sailing` + `survival-crafting` + `co-op`: sailing leads wind, the boat's motion and aiming; survival leads exposure
  and supplies; co-op leads upkeep and talking. Watch: the water the player sees is the water that moves the boat.
- `cozy-cleanup` + `detective` + `visual-novel`: cozy play leads forgiving handling and finishing without pressure;
  deduction leads evidence; the story leads what objects and places mean. Watch: hints keep the reasoning.

## When two genres want opposite things

The Leads line settles it: what each genre wanted and what this game does.

- **Heavy commitment vs instant cancel:** choose per move, and show when a move can be cancelled.
- **Failure that matters vs easy retries:** say what resets, what stays, and how a session can end safely.
- **Helpers vs a party that plays itself:** keep a hit, a save or a finishing blow for the player where the idea needs it.
- **Endless growth vs readable numbers:** cap the arithmetic and the chains that trigger each other.
- **Not knowing vs solvable planning:** say what is shown, committed, left to chance or hidden.
- **Atmosphere camera vs player control:** framing the player can take over, with every warning still in view.
- **Spectacle vs quick replays:** keep the order of events, and let them speed up or skip.
- **Free building vs checked challenges:** check completion where finishing is the point; leave free building free.
