---
name: player-clarity
description: Deciding how __GAME__ tells players what to do and what just happened — onboarding, tutorials and the first-time experience ("tutorial", "ilk açılış", "oyuncu anlamıyor"), context hints ("ipucu"), event narration and attribution ("ne oldu", "kim yaptı"), the results screen, the wording of every player-facing string, HUD and world-space labels, colour-blind identification, readability in a muted or vertical clip, and keeping the UI original rather than template-looking ("AI yapmış gibi olmasın", "generic", "özgün", "sade", "net"). Use when adding or changing anything that explains, instructs, labels, announces or attributes, when players "don't get it", or before writing UI text or a HUD element. How an event feels (timing, shake, sound weight) is game-feel; laying out uGUI is ui-ugui.
---

# Telling __GAME__ players what to do

The rules, numbers and sources are in `references/clarity-rules.md` (CL01–CL22). This skill is the procedure.
`DESIGN.md` names the game's own carriers (its characters, world, signature objects) and its voice; if it does not,
ask once and write the answer there.

## Rule zero

Nobody reads. People read about 20 % of the words on a page, working memory holds about four chunks, and the best
onboarding forces the lesson once, by doing, where failing costs nothing. Every element must leave something a player
can say out loud in five seconds.

## Procedure

1. **Name the moment and the reader.**
   - The moment: before play (first launch, level start), during it, or after an event.
   - The reader: the one who must act, everyone, or a viewer who just tuned in (a clip, a store video).
2. **Ask whether the world can enforce it instead (CL06).** If it can, build that and write nothing.
3. **Pick the carrier from the ladder (CL05):** the player's body or piece, then the world, then the game's own
   narrator object if it has one, then sound and haptics, then a HUD element. Each step down needs a reason you can
   state.
4. **Write the line in the game's voice (`clarity-rules.md` §E):** the player-facing language from `CLAUDE.md`,
   one to four words, verbs and names over roles, sentence case.
5. **Run the four tests (CL01–CL04):** speakable, muted clip, paste, budget. If one fails, go back to step 3, not to
   the wording.
6. **Show the user two to four options as an interactive prototype** (`show_widget`), the recommended one first. They
   pick. Do not build the first idea straight away.
7. **Build it (below), then hand over a Play Mode checklist** (`implementation-verification`), on PC and on a phone.
   Write the decision into `DESIGN.md`.

## Hard rules

- **Screen space is scarce, on a phone most of all.** A new HUD element needs the user's yes on where it goes, inside
  the safe area and out of the thumb zone (`platform-targets`).
- **The template tells in `clarity-rules.md` §F are out:** no centred modal with a title, a body and an OK button, no
  objective tracker, no pulsing arrow, no glow on everything touchable, no glass, gradient, emoji or stock icon, no
  bouncing easing on UI, no character who says the solution.
- **Icons come from the game's own art**, never from an icon font or a stock pack.
- **Never colour alone (CL09).** Pair a colour with a shape, a direction, a name or an icon.
- **One input per action.** A carrier that needs a new key or gesture is out unless it rides an existing one.
- **Every hint retires (CL17).** A hint with no done-condition is not finished.
- **Name the input for the device in use.** "Tap" on touch, the key or button on PC; the prompt follows the last
  device used (`platform-targets`). Never "click" on a phone.
- **Attribution and key labels sit in the middle third (CL10).** Corner text does not survive a vertical crop, and on
  a phone the corners sit under notches and thumbs.

## Building it

- **Chrome:** uGUI on a Canvas with Scale With Screen Size, under a `SafeAreaFitter` (`ui-ugui`, `platform-targets`).
  Put the shared look (font, sizes, colours, outline) in one place and reuse it; never style per view.
- **A label pinned to a world object:** project its position to the screen each frame it moves, clamp it a margin
  inside the safe area, and use outlined, backgroundless text that reads over any background.
- **Retiring a hint:** count successes per player and per verb; stop showing after the done-condition, and bring it
  back only after a long stretch unused.
- **Moments vs states:** a one-time moment is raised as an event the view listens to; a state is polled.
- **Per-frame cost:** write text only when it changes and build no strings per frame (`unity-performance`). Every
  mutable static gets a `SubsystemRegistration` reset.
- **Strings:** player-facing strings and Inspector text are in the language `CLAUDE.md` names. If that is Turkish,
  check the font has ç ğ ı İ ö ş ü before shipping it.
- **Reading time:** a line stays up at least as long as 17–20 characters per second needs, and never times out before
  it can be read (CL04, CL15).

## If the game is multiplayer

- **Names, not roles.** "Ali jumps", in Ali's colour; never "your partner".
- **Each screen speaks its own half:** a hint shows only on the screen of the player who must act (CL14, CL16).
- **One rule decides blame**, shown at the victim in the culprit's colour, and the results screen is where blame pays
  off as a joke (CL19–CL22).
- **Offline on one screen there are no names:** colour plus shape carries identity there (CL09).

## Neighbouring skills

- `game-feel`: how long a label stays, how loud a narration is, the timing of an attribution cue.
- `level-beat-review`: where a lesson sits in a level, and the "one new idea per segment" order.
- `ui-ugui`, `platform-targets`: layout, scaling, safe area and input prompts per device.
