# Card battler

Duel an opponent with a deck built before the match (Hearthstone, Marvel Snap, Inscryption); the core verb is play a
card from hand.

**Camera (Unity):** a fixed orthographic camera on the table from the player's seat; for cards on a 3D table in a room,
a fixed perspective camera angled down at the table.

## Defaults

- **build-a-deck**: Before the match the player builds a small deck from a pool, with a limit on copies of any one
  card, and a ready-made deck is one button away. Why: the deck is the plan, fewer good cards beat many weak ones, and
  a novice can play at once. Break it when: the deck grows card by card during a run (roguelike-deckbuilder).
  [snap-1], [mtg-starter-1]
- **growing-resource**: Each turn gives a little more to spend than the last, so the match opens with small plays and
  builds to big ones. Why: the resource sets the pace, and every turn brings a new choice. Break it when: resources come
  from cards in the deck on purpose. [rosewater-2], [runeterra-1], [snap-1]
- **second-seat-extra**: Whoever goes second gets a small extra (a card or a one-time boost), and a player who falls
  behind has ways back. Why: neither seat decides the match before it starts. Break it when: both players act at once.
  [hearthstone-1], [rosewater-1]

## Feel

- **telegraphed-intent**: The AI's creatures show what they will hit next turn and for how much. Why: a loss is the
  player's misread, never a surprise. Break it when: bluffing is the point.
- **one-at-a-time**: Each card played, by either side, shows large for a moment, and its effects resolve one by one in
  order; a button speeds up the AI's turn. Why: the player sees why the board changed. Break it when: a speed duel
  where pace is the fun.
- **rising-chain**: When effects chain, each step climbs in pitch and the total counts up, and the winning blow or a
  big total lands with a burst. Why: a combo builds instead of arriving as one number. Break it when: cards never chain.
- **read-any-card**: A card under the pointer lifts; holding on any card, yours or the AI's, shows it large with each
  keyword explained, and most cards say little. Why: the rules are learned in play, never from a manual. Break it when:
  a handful of plain cards that need no words. [rosewater-3], [inscryption-2]

## Variants

- **brisk**: cheap cards, low life, an AI that rushes, a match in a few minutes.
- **combo**: cards that trigger each other, a slow start and one big winning turn.
- **bluff**: raise the stakes or retreat at a price, and an AI that bluffs too.

## Choices that shape the pitch

- **How a match is won:** the other side's life to zero (default) · win more lanes than the AI after a set number of
  turns · best of three rounds from one hand.
- **The deck:** a ready-made deck to tweak (default) · a draft, one of three cards at a time · a pool that grows with
  wins (later).
- **Stakes:** one match (default) · a short ladder of AI opponents, each with its own deck · a mid-match raise with a
  priced retreat.
- **View:** the table from the player's seat, orthographic (default) · cards on a 3D table in a room, perspective.
- **Feeling:** the player feels clever by winning with a turn set up a few turns before, because each effect played out
  in order and the plan was theirs.

## Platforms

- PC: drag a card onto its target with the mouse; hover shows detail. Touch: the same drag through Pointer, and a long
  press replaces hover for card detail.
- Phone: portrait, hand along the bottom, board above *(guess)*; PC landscape.
- A match of 3-5 min on the phone, 5-15 min on PC *(guess)*; save the match state so an interruption does not lose it.

## Later

- A collection grown by opening packs, protected from long bad-luck streaks.
- Crafting cards from spares.
- A campaign of opponents on a map.
- Rewards that change the rules for a skilled player.
- Many card sets and keywords.
- Two players on one screen, with a pass screen that hides hands.
- Online matches, ranking and matchmaking (needs a server).

## In a mashup

The card battler leads the turn, the deck and how effects resolve. A roguelike leads the run, and the deck grows card
by card. Tactics leads a board of positions and pushes. An RPG or adventure half leads the world, and cards come from
exploring. A creature collector leads the collection, and its creatures become the cards.
