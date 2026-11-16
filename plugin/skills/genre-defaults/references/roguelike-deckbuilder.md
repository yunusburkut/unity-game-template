# Roguelike deckbuilder

Build a deck from rewards on a generated map; death ends the run (Slay the Spire, Balatro, Monster Train). The core
verb is play a hand, then pick a card. Unlike the card battler, the deck grows during the run, not before it.

**Camera (Unity):** a fixed orthographic camera on the fight from the player's side; for cards on a 3D table, a fixed
perspective camera angled down at the table.

## Defaults

- **small-start**: The run starts with a small deck of plain attacks and blocks and the same energy every turn; each
  turn draws a fresh hand, and the draw and discard piles show their counts. Why: every card added later is felt, and
  the player sees what is left to draw. Break it when: a scoring run that plays hands from a full standard deck.
- **pick-or-skip**: After each fight, take one of a few cards or skip them all; a shop or a rest can remove a card.
  Why: the deck gets sharper, not only bigger, and a lean deck can win. Break it when: the deck is fixed and the run
  grows only through relics.
- **branching-map**: A generated map of fights, harder elite fights, events, rests and a shop, with the path picked by
  the player and a boss at the top. Why: the route is a plan: risk a hard fight for a better reward, or rest. Break it
  when: one ladder of fights in a row.

Variety floor (hypothesis): 4 enemy kinds in the first slice, one of them an elite, each with its own intents (the number is not in
the sources).

## Feel

- **intent-shown**: Each enemy shows what it will do next turn and for how much (attack, block or buff), and the damage
  shown already counts your block. Why: each turn is a puzzle, and a loss is the player's misread. Break it when:
  surprise is the point, a gamble every turn.
- **play-in-order**: A played card flies to its target and its effects resolve one at a time in order; the enemy turn
  and long chains speed up on a button. Why: the player sees why each number changed. Break it when: a speed run where
  cards resolve at once on purpose.
- **rising-count**: Damage and score count up one hit or trigger at a time, each step higher in pitch, and a kill or a
  beaten target lands with a burst. Why: a good turn builds, and the big total feels earned. Break it when: every card
  does one plain thing and nothing chains.
- **hand-feel**: The hand fans out, a card under the pointer lifts and explains its keywords, it is dragged onto its
  target along an arrow, and a card that cannot be played says why. Why: cards feel like things in the hand, and a
  mistake is caught before it happens. Break it when: cards are picked from a plain list on purpose.

## Variants

- **fights**: enemies with intents, block against damage, a boss at the top.
- **score**: hands played for a target that rises each round, jokers that multiply, a shop between rounds.
- **dice**: rolled dice placed into the cards' slots, luck shaped by what is on the faces.

## Choices that shape the pitch

- **What a fight is:** a few enemies with intents, beaten turn by turn (default) · a hand scored against a target, no
  enemy · units placed on lanes that fight on their own.
- **Rewards:** a card from a few, or skip (default) · relics that change the rules · upgrading a card already held.
- **Stakes:** death ends the run, and a new run is a new map (default) · a few lives across the run · cards unlocked
  for later runs.
- **View:** the fight from the player's side, orthographic (default) · cards on a 3D table, perspective.
- **Feeling:** the player feels clever by winning with a deck they trimmed, because they skipped weak rewards and the
  winning turn played out in order.

## Platforms

- PC: drag a card to its target, or click the card then the target; hover for keywords; E ends the turn *(guess)*.
  Touch: the same drag through Pointer, a long press for keywords, and a large End Turn button.
- Phone: portrait fits the hand, the enemies and the map well *(guess)*; PC landscape.
- One fight is 1-3 min, a full run 30-60 min *(guess)*: save the run after every fight and every map step, so a phone
  session can stop anywhere.

## Later

- Several characters, each with its own cards. [slay-7]
- Written events with choices.
- Harder levels opened by a win.
- Card upgrades at rests.
- Cards exhausted for the fight, apart from removal.
- Potions and other one-use items.
- Cards and relics unlocked over many runs.
- A daily seeded run from the date (local; sharing results needs a server).

## In a mashup

The deckbuilder leads the run and the deck: rewards, removal and the draw. A card battler leads a duel between two
built decks. Tactics leads a board of positions and pushes, and the cards are the moves. An action roguelite leads
real-time fights, and cards become the rewards. An RPG half leads the world, and cards are found in it.
