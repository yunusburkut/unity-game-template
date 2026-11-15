# Word game

Make or find words from letters under a set of word rules; the core verb is spell.

**Camera (Unity):** one fixed orthographic camera, or a uGUI screen only: the letters and the current word fit
the screen. A first slice uses a small prepared letter set and an explicit list of accepted words.

## Defaults

- **letters-to-words**: Give the player a prepared bank of letters and ask for words made from it. Why: the
  same letters can reveal fresh possibilities. Break it when: the goal is to guess a hidden word from feedback
  on earlier guesses. [spellingbee-1]
- **known-word-rules**: Check submissions against the chosen word list (a TextAsset loaded once into a
  `HashSet<string>`), and accept each word only once per puzzle. Why: success comes from finding something new
  under consistent rules. Break it when: repeated words on a changing board are allowed on purpose. [letterpress-1],
  [letterpress-2]
- **culture-safe-letters**: Upper- and lower-case with the language's culture, never the default one: Turkish
  `i`/`İ` and `ı`/`I` break with `ToUpperInvariant`. Normalize the list and the input the same way, and give
  the TMP font every letter of the language. Why: a valid word rejected for its casing is a bug the player blames
  on the game. Break it when: never.

## Feel

- **rejection-explained**: When a word cannot be played, show why (too short, not in the list, already found). Why:
  a rejected word teaches the rule instead of feeling arbitrary. Break it when: dictionary challenges are part
  of a contest between players. [letterpress-3]
- **fresh-arrangement**: Let the player shuffle the letter bank into a new order. Why: a fresh arrangement
  can suggest another word. Break it when: letter positions are part of the puzzle, such as connected paths or
  captured territory. [wordwheel-1]
- **word-means-something**: Selecting a played word shows its definition. Why: an unfamiliar accepted word
  becomes something the player can learn. Break it when: the puzzle uses an invented language and discovering
  meanings is the goal. [letterpress-4]

## Variants

- **discovery**: Turn the letter bank around and look for fresh combinations. [spellingbee-1], [wordwheel-1]
- **learning**: Explain rejected words and offer meanings for accepted ones. [letterpress-3], [letterpress-4]

## Choices that shape the pitch

- **The puzzle:** find words in a letter bank (default) · guess a hidden word · trace connected letters ·
  place words across a shared board.
- **Word rules:** a prepared accepted list (default) · a broader dictionary · a themed list with its restrictions
  explained.
- **Goal:** find as many different words as you can (default; [spellingbee-1]) · uncover the hidden answer ·
  score more than a local opponent.
- **View:** letters and an entry area (default) · a board of tiles whose positions constrain the words.
- **Feeling:** the player feels a small spark of discovery by seeing a new word in letters they have stared at
  for a while, often just after a shuffle ([spellingbee-1], [wordwheel-1]).

## Platforms

- PC: type on the physical keyboard, Enter submits, Backspace deletes; tapping letters with the mouse also works.
- Touch: tap or drag across letter tiles on the Pointer; never the system on-screen keyboard. Portrait, letters
  in the bottom third *(guess)*.
- Session: one puzzle is a few minutes; a phone plays it in short visits, so save found words on
  `OnApplicationPause`.

## Later

- More prepared puzzles and themed word lists
- A generator that checks playable words before offering letters
- A shared board with letter values and placement bonuses
- A local opponent that chooses words from the same dictionary
- A faster way to edit the current word
- Daily puzzles (a local seed from the date works now; shared scores need a server)
- Remote opponents (needs a server)

## In a mashup

The word game leads which letters make a legal word. A puzzle half leads paths and placement on the board. An
RPG half turns accepted words into actions while keeping word validation consistent. A party half leads turns
and scoring. A story half supplies a theme for the word list; it must explain any restrictions that differ from
ordinary word play.
