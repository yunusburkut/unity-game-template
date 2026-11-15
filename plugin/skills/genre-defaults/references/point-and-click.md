# Point and click

Explore drawn scenes, click items and solve puzzles to move the story on (Monkey Island, Myst, Machinarium); the core
verb is use this on that.

**Camera (Unity):** a fixed orthographic camera, one drawn screen at a time; an orthographic side view that scrolls
with the hero across a wide scene; or a first-person perspective camera for a Myst-like 3D place.

First slice: a few screens and one chain of puzzles, each proved solvable. Large authored content comes later.

## Defaults

- **items-and-locks**: Picked-up items wait in a bar along the bottom, to use on the scene or on each other, and every
  lock (a door, a guard, a machine) is seen before the thing that opens it. Why: the player knows what a find is for
  the moment they find it. Break it when: all puzzles are in the scene, levers and codes (Myst-like, escape room).
- **hints-on-ask**: A Hint button gives a small nudge first, then a bigger one, never the answer at once. Why: no one
  quits for a walkthrough, and the idea stays theirs. Break it when: the user wants it hard and pure, with no help.

## Feel

- **show-hotspots**: The cursor changes over anything usable, hotspots are generous, and one input briefly lights up
  everything clickable. Why: the puzzle is in the thinking, never in hunting for pixels. Break it when: finding the
  hidden thing is the puzzle (hidden-object).
- **every-click-answers**: Click a thing to use it, right click or a Look input to hear what the hero thinks of it, and
  a wrong try gets its own line, often a joke. Why: every try teaches or amuses, and nothing meets silence. Break it
  when: a wordless game that shows thoughts in pictures.
- **eureka-plays-out**: When the right thing meets the right lock, it plays out at once with a sound and a short
  animation, and a solved step never has to be done again. Why: the idea is the reward, so it lands loud and costs
  nothing to carry out. Break it when: carrying out the plan is the challenge, a timed escape.
- **never-stuck**: No death and no dead end: an item the story needs cannot be lost or used up, and a double click on
  an exit goes straight to the next screen. Why: a stuck player is thinking, never doomed, and never walks the same
  path twice. Break it when: the user wants old-school deaths; then a death restarts the screen at once.

## Variants

- **comic**: characters to chat with, odd item combinations, a joke for every wrong try.
- **mysterious**: alone in an odd place, machines and codes in the scene, few words, clues in the walls.

## Choices that shape the pitch

- **Puzzles:** items used on the scene and on each other (default) · machines and codes in the scene (Myst-like) · one
  locked room to escape against a clock (escape room).
- **Talk:** a few characters who help when asked about things (default) · no one to talk to, a lone explorer · talk is
  the puzzle, the right line to the right person.
- **Failure:** none, you cannot die or get stuck (default) · deaths that restart the screen at once.
- **View:** drawn screens (default) · a wide scene that scrolls · a 3D place in first person.
- **Feeling:** the player feels the eureka of using the right thing on the lock they saw first, because the answer was
  in plain view all along.

## Platforms

- PC: left click to use, right click to look, hover shows the hotspot name. Touch: tap to use, a long press to look;
  with no hover, the light-up-hotspots button carries the job *(guess)*.
- Phone: landscape for drawn wide scenes; portrait suits a single escape room *(guess)*.
- One puzzle per phone session, a chapter per PC session; autosave after every solved step.

## Later

- Many screens and a long puzzle chain.
- Conversations whose choices change the story.
- Several ways past the same lock.
- A list of verbs (push, pull, talk to).
- A story that turns midway into a different problem.
- A world whose walls hide a language you learn to read.
- Switching between a few heroes.

## In a mashup

Point-and-click leads the scenes, the items and the hints. A puzzle half leads the rules and proves each puzzle can be
solved. A visual novel leads the conversations. A detective half leads the evidence and what counts as solved. An
action half leads its fights, and a lost fight sends you back to the screen, never to a dead end.
