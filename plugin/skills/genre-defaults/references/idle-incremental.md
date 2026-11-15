# Idle incremental

Numbers grow exponentially, then reset for permanent bonuses; the core verb is buy.

**Camera (Unity):** one fixed orthographic camera; nothing moves the view, and the screen fills up with what
you bought. Most of the game is uGUI.

## Defaults

- **rising-costs**: Each helper costs more every time you buy one, every button shows its price and what it adds,
  and the total and the rate per second sit at the top. Why: the next buy is always a choice between cheap now
  and better later. Break it when: prices are fixed on purpose, a cozy shop with no growth. [pecorella-1]
- **prestige-reset**: When growth slows, a reset trades the run for a lasting bonus that multiplies all output,
  and the button shows what you would gain now. Why: a wall becomes a choice, and each climb is faster than the
  last. Break it when: one long climb with no reset is asked for. [pecorella-2]
- **away-earnings**: The game keeps earning while closed: save a UTC timestamp in `OnApplicationPause(true)` and
  on quit, and on return pay for the time away (clamp a negative gap to zero, the device clock can move back) and
  show how long you were away and what you earned. Why: the game grew without you, so returning is a reward. Break
  it when: the game is about being there, and nothing happens while you are gone. [clicker-heroes-1], [pecorella-2]

## Feel

- **first-click**: The first clicks pay at once, with a number popping from the button, and the first helper
  costs a handful of clicks and then earns on its own. Why: the game turns from working to watching in the first
  minute. Break it when: clicking is the whole game, a tapping race. [dark-room-1]
- **buy-shows**: A buy lands with a click, the helper appears on screen, and the rate jumps where you can see
  it. Why: each purchase answers at once and changes something you can see. Break it when: the game is only
  numbers on purpose, a spreadsheet of growth.
- **numbers-climb**: Totals count up smoothly, never in jumps; big numbers keep short names (thousand, million,
  billion), a setting switches to letters or scientific notation, and the digits do not jitter (TMP monospace
  digits). `double` holds up to about 1e308; past that needs a mantissa-plus-exponent type. Why: the player
  watches growth instead of reading digits. Break it when: numbers stay small and exact. Hypothesis only.
- **milestone-burst**: A bar fills toward the next milestone of one helper, and crossing it multiplies that
  helper's output with a burst and a chime. Why: a small win is always just ahead. Break it when: there is one
  kind of helper and nothing to collect. [pecorella-2]

## Variants

- **clicky**: Clicks stay worth it all game, with short bonuses to catch.
- **idle**: It plays itself; you check in, buy and plan the next reset.
- **vast**: Each stage changes what you make: a stall, then a city, then a planet.

## Choices that shape the pitch

- **What grows:** a business of helpers earning coins (default) · a chain of machines where one feeds the next
  · a story told through the numbers, each stage a new kind of thing.
- **Clicking:** matters early, then helpers take over (default) · matters all game · none, only buying.
- **Reset:** a prestige reset for a lasting multiplier (default) · no reset, one long climb · resets stacked
  on resets (later).
- **Feeling:** the player feels growing power by watching a number that once crawled now race, because each buy
  multiplies the last and every reset climbs faster.

## Platforms

- PC and touch play the same: every action is a Pointer tap on a button, so one input path covers both.
- Phone: portrait, buy buttons in the bottom third for the thumb *(guess)*.
- Session: phone check-ins of a minute or two several times a day; PC sits open in a window for hours. Away
  earnings carry the phone side.

## Later

- Resets stacked on resets
- Achievements and their bonuses
- Research and upgrades that change the rules
- Diminishing returns on stats that could take over
- Timed events
- Paid boosts and ads
- Saves that follow the player across devices (needs a server or the store's cloud save)
- Balance over hours and days of play

## In a mashup

Incremental leads the numbers, the costs and the reset. A management half leads the floor and what customers do,
and the numbers set the prices. An RPG half leads a hero whose upgrades the numbers buy, and its fights must
change as the numbers grow. A roguelite leads the run, and prestige is what carries over. A story half leads
the stages the numbers unlock.
