# Visual novel

A story in text boxes over art, with choices and several endings; the core verb is choosing what to say.

**Camera (Unity):** one static orthographic camera; the art changes by scene and nothing moves the view. Most of the
screen is uGUI (text box, name plate, choices) over background and character sprites.

## Defaults

- **one-short-scene**: The first slice is one short scene with a few choices and a few endings. Why: long branching
  stories grow from one scene that works. Break it when: never for the first slice.
- **choices-remembered**: Each choice changes what someone says later in the scene, and the scene shows it
  remembered. Why: a choice feels real when the story answers it. Break it when: the choices are only flavour on
  purpose, a set story with a few asides. [telltale-1]
- **every-path-ends**: A wrong answer never ends the game early: branches fold back together, every path reaches one
  of a few endings, the end screen names it and says how many there are, and play again starts at the first choice.
  Why: the player chooses for the character, not to dodge a game over. Break it when: sudden bad ends are the charm.
  [ashwell-1], [emshort-2]
- **save-anywhere**: The game saves at every choice and from the pause screen, and continue picks up at that line.
  Why: a story is read in sittings. Break it when: the scene is always read in one go. [renpy-1]
- **reading-screen**: Lines appear at a speed the player sets, never on a clock they cannot stop, and a log shows the
  lines already read. Why: the player reads at their own pace and can look back. Break it when: a timed scene where
  the clock is the point, and even then the speed setting stays. [gag-2], [renpy-1], [yarn-1]

## Feel

- **voices-and-faces**: Each speaker has a name on the box, a face that changes with the line, and a soft blip as the
  letters appear. Why: the player hears who talks and sees how they feel. Break it when: one narrator tells it all.
- **choice-lands**: A picked choice answers at once: the face reacts, a sound marks it, and the next line is about it.
  Why: the player feels heard before any later payoff. Break it when: the choice is meant to sink in silently and
  come back much later. [telltale-1]
- **mood-music**: Music and background change with the scene's mood at a natural break, and a hard line can land in
  silence. Why: the player feels the turn before reading it. Break it when: the piece is silent on purpose.

## Variants

- **warm**: gentle text, no timers, choices about how close to get to someone.
- **tense**: some choices run on a timer, and saying nothing is an answer too.
- **sharp**: some lines test a skill, and failing one opens its own scene.

## Choices that shape the pitch

- **What you choose:** what to say, line by line (default) · who to spend time with, a dating sim with a heart for
  each person · where to go next, a text adventure.
- **Stakes:** every path reaches an ending (default) · some bad ends, a replay to fix them · choices on a timer.
- **What the player sees:** drawn characters over a background (default) · text only, interactive fiction · a phone
  screen of messages.
- **Feeling:** the player feels responsible for someone by choosing what to say, because the story answers that
  choice before the scene ends.

## Platforms

- PC: click or Space/Enter to advance, mouse to pick a choice, a key for the log, Escape for pause and save.
- Touch: tap anywhere to advance, tap a choice; choice buttons sized for a thumb, and the log opens by a button or a
  swipe *(guess)*. Portrait suits the messages view and a phone read; landscape suits wide art. Pick one in CLAUDE.md.
- Session: a phone reader stops every few minutes, so save-anywhere carries it; PC reads whole chapters.

## Later

- Routes that split and rejoin with what you chose
- Consequences that show up chapters later
- Many chapters and a full cast
- Skills that talk back as voices in your head
- A skip key for lines already read
- A gallery of unlocked art and a chart of endings
- Characters made by the game who remember and change

## In a mashup

The visual novel leads scenes, choices and what the story remembers. A life sim leads the days and the visual novel
leads the talks between them. A detective half leads the evidence and the visual novel leads the questioning. An RPG
or action half leads its fights, and a lost fight leads to a scene, not a reload. A puzzle half leads its rules, and
the story leads what solving them means.
