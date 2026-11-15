---
name: genre-defaults
description: The defaults a genre's best games share, one sheet per genre - camera, first-slice defaults, feel rules, the choices that shape the pitch. Use when shaping a new game's idea, when the user names a genre ("tür", "genre", "X gibi bir oyun", "like Celeste"), or before picking the defaults for a genre's core system. Feel numbers are game-feel; level rhythm is level-beat-review.
---

# Genre defaults

A sheet is `references/<genre>.md`. Each line is a hypothesis read from the genre's best games, not a measured number.
The user's words override every line. Numbers come from `game-feel/references/numbers.md`, never from a sheet. A source
key such as `[gungeon-2]` resolves in `references/sources.md`.

## Match the idea to a sheet

Match by meaning, not by keyword, and never show the list as a menu. Take one sheet, or two when the idea joins two
genres. Two sheets: read `references/mashups.md` before anything else. A named game ("Hades gibi") picks the sheet of
that game's genre. No sheet fits: take the nearest one and say which in the Assumptions.

- `action-adventure`: Explore a world, fight by hand and solve its puzzles to open new places
- `action-roguelite`: Real-time runs that end in death; progress carries over
- `action-rpg`: Real-time fighting by hand; levels, gear and builds set the numbers
- `arcade-classic`: A single-screen arcade game played for a high score
- `arcade-sports`: A sport stripped down to fast, exaggerated play
- `auto-battler`: Buy units, arrange a team on a board and watch it fight on its own
- `beat-em-up`: Brawl with many enemies along a scrolling stage
- `board-and-abstract`: Chess, go and other board games, with an AI opponent
- `card-battler`: Duel an opponent with a deck of cards built before the match
- `character-action`: Stylish melee in 3D, with combos, dodges and a rank for style
- `city-builder`: Grow a city from empty land, balancing housing, jobs and services
- `co-op`: Two or more players work together against the game
- `colony-sim`: Colonists' needs and moods drive a small settlement's stories
- `cozy-cleanup`: Clean, tidy, sort or decorate a space until it looks right
- `creature-collector`: Catch creatures, train a team and battle with it
- `detective`: Gather clues and reason out what happened
- `dungeon-crawler`: A party explores a grid dungeon in first person, step by step
- `endless-runner`: The character runs forever; the player jumps, slides or turns
- `factory-automation`: Build machines and belts that make things on their own, then scale them up
- `falling-block-puzzle`: Falling pieces placed so rows or groups clear before the stack tops out
- `farming-life-sim`: Farm through the seasons and build a life in a small town
- `fighting`: Head to head with a move set, life bars and rounds
- `first-person-shooter`: Shooting through the character's eyes in 3D
- `fishing`: Cast, wait, hook and reel in fish, and fill a log of catches
- `flight`: Fly a plane, glider or ship through the air or space
- `grid-puzzle`: Push blocks onto targets (Sokoban); a wrong push can make it unsolvable
- `hidden-object`: Find listed items or characters in a cluttered scene
- `idle-incremental`: Numbers grow exponentially, then reset for permanent bonuses
- `level-maker`: Build levels with an editor and play them; the editor is the toy
- `logic-puzzle`: Pure deduction on a grid of clues, from picture logic to mines
- `management-tycoon`: Run a business or a place (tycoon), balancing money, staff and customers
- `metroidvania`: A connected 2D map opened up by new abilities
- `mining`: Dig down, collect ore, sell it and upgrade to dig deeper
- `parkour`: Move fluidly through 3D spaces with vaults, wall runs, climbs and slides
- `party-game`: Short rounds several people play on one screen, for laughs
- `pet-raising`: Raise and care for a creature that grows from how you treat it
- `physics-puzzle`: Aim, launch or place things and let physics solve the level
- `platformer`: Run and jump past hazards; the jump is the core verb
- `point-and-click`: Explore drawn scenes, click items, solve puzzles to move the story on
- `puzzle-platformer`: Platforming where each level is a puzzle to solve
- `racing`: Drive a vehicle to finish first, or to wreck the others
- `real-time-strategy`: Gather, build a base and command an army in real time
- `rhythm`: Press inputs in time with a song
- `roguelike-deckbuilder`: Build a deck from rewards on a generated map; death ends the run
- `sailing`: Sail a ship with the wind, explore the sea and fight other ships
- `sandbox`: An open space of materials and tools to make, break or play with, and no set goal
- `shoot-em-up`: One craft dodges and fires across a scrolling screen
- `skate-and-surf`: Ride a board or a wave, chain tricks and keep a line going for score
- `soulslike`: Hard, deliberate fights; death drops what you carry near a rest point you return to
- `stealth`: Get past or take out guards unseen by reading their routines
- `survival-crafting`: Gather and craft against hunger and threats, and build a base
- `survival-horror`: A weak player, scarce resources; fleeing matters as much as fighting
- `survivors-like`: Auto-attack hordes; the player moves and picks a build
- `tactical-rpg`: Grid battles fought by a party that grows between fights
- `tower-defense`: Place towers to stop waves before they reach the goal
- `traditional-roguelike`: Turn-based dungeon crawl, generated levels, permanent death
- `trivia-quiz`: Answer factual questions against a clock or other players
- `turn-based-jrpg`: Party battles fought in turns chosen from a menu
- `turn-based-strategy`: Armies and cities moved a turn at a time on a map
- `twin-stick-shooter`: Top-down; one stick moves, the other aims
- `visual-novel`: A story in text boxes over art, with choices and several endings
- `walking-sim`: Walk through a place and find its story, with little or no challenge
- `word-game`: Make or find words from letters under a set of word rules

## Use a sheet

- **Choices that shape the pitch** (failure, progression, view, the feeling sentence): ask only the ones the user's
  words leave open. The feeling sentence goes into the DESIGN.md opening paragraph.
- **Defaults and Feel** feed DESIGN.md Pillars and Rules and the first spec card. A default the user did not confirm is
  an Assumption on the card, with its Break it when. A rule goes into Rules only after it is built.
- **Camera** sets the first scene's camera. **Variety**, where a sheet has it, is the floor of enemy kinds in the first
  slice (a hypothesis; never fewer than the user names).
- **Platforms** feeds the DESIGN.md Platforms table (input, orientation, session length on PC and phone).
- **Variants:** the user's words pick one (else the first, as an Assumption); it tunes the Feel lines.
- **In a mashup:** read it with `references/mashups.md`.
- **Later** items go to PLAN.md Next (at most 5), never into the first slice.
- **Online:** the idea asks for play over a network: read `references/online.md` and record its level.
- **Look:** the user said nothing about the look: read `references/art-directions.md` and mark the pick *guessed*.

## Not covered

`mmo`, `battle-royale`, `moba`, `extraction`, `competitive-multiplayer` and `async-multiplayer` have no sheet. Online
PvP at scale (servers, matchmaking) is out of scope for a solo Unity game. Local versus goes to `fighting` or
`party-game`; async ghosts or leaderboards go to `references/online.md` level 2. For any other of these, say so in one
sentence and offer the nearest covered sheet (`co-op`, `party-game`, `fighting`, `survival-horror`).

Credit: the sheets adapt Claude Code Game Studios (MIT, Copyright (c) 2026 Donchitos); full text in LICENSE.md.
