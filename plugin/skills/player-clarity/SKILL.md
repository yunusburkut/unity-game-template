---
name: player-clarity
description: Players confused, UI text or HUD to write ("oyuncu anlamıyor", "ipucu", "ne oldu", "AI yapmış gibi olmasın"): onboarding, hints, attribution, player strings, localization, colour-blind cues, access, non-template UI. Feel: game-feel; layout: ui-ugui.
---

# Telling players what to do

The rules, numbers and sources are in `references/clarity-rules.md` (CL01–CL38). This skill is the procedure.
`DESIGN.md` Look names the game's own carriers (its characters, world, signature objects) and its voice, on its
`Voice` and `Carriers` lines; if they are missing or TODO, ask once and write the answer there (add the two lines under
Look if the file has none). The same goes for the language: if the player-facing language line in `CLAUDE.md`
Conventions or the `DESIGN.md` Languages row is still TODO (the template ships "TODO (Turkish / English)"), ask once
which language the first release shows and whether a second is planned, and write the answer in both places before the
first string. If a second language stays undecided, build as if it is planned: strings from the string table with
named placeholders (CL27, CL29).

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
   inside the §E word budget, verbs and names over roles, sentence case.
5. **Run the four tests (CL01–CL04):** speakable, muted clip, paste, budget. A muted-clip or paste failure (CL02,
   CL03) goes back to step 3, not to the wording. A line that fails speakable or the budget (CL01, CL04) may be cut
   once; if it still fails, back to step 3.
6. **Show the user two to four options on a decision page**
   (`${CLAUDE_PLUGIN_ROOT}/skills/pipeline/references/decision-page.md`), the recommended one first. They pick. Do not
   build the first idea straight away. Where no page can be made (that file's fallback), use `show_widget`; without
   that either (a terminal session), show
   each option as a short mock: the exact on-screen words, where they sit, what carries them, and when they retire.
7. **Build it (below), then hand over a Play Mode checklist** (`implementation-verification`), on PC and on a phone.
   Write the decision into `DESIGN.md`.

**Unattended (the builder agent or a workflow):** skip step 6 and the placement yes. Take the recommended option,
write it on the spec card's `Assumptions` line, and add the HUD placement as an `Accept` item with evidence
`Play Mode (user)`, so the Play Mode checklist asks it. Carrier and placement questions belong in the card's
`Open questions` before the build starts (`pipeline`).

## Hard rules

- **Screen space is scarce, on a phone most of all.** A new HUD element passes the necessity rule (CL24) and has a
  place in the HUD inventory and its states (CL23, CL25). It needs the user's yes on where it goes, inside the safe
  area and out of the thumb zone (`platform-targets`).
- **The template tells in `clarity-rules.md` §F are out:** no centred modal with a title, a body and an OK button
  (the one exception confirms a destructive action, focus on Cancel, never a hint), no objective tracker, no pulsing
  arrow, no glow on everything touchable, no glass, gradient, emoji or stock icon, no bouncing easing on UI, no
  character who says the solution.
- **Icons come from the game's own art**, never from an icon font or a stock pack.
- **Never colour alone (CL09).** Pair a colour with a shape, a direction, a name or an icon. A set of colours that
  tells categories apart (teams, pieces, liquids) passes the distances in `references/palette-distinguishability.md`.
- **One input per action.** A carrier that needs a new key or gesture is out unless it rides an existing one.
- **Every hint retires (CL17).** A hint with no done-condition is not finished.
- **Name the input for the device in use.** "Tap" on touch, the key or button on PC; the prompt follows the last
  device used (`platform-targets`). Never "click" on a phone.
- **Attribution and key labels sit where a vertical crop keeps them (CL10).** In a landscape game that is the 9:16
  crop window around the action, about the centre 30 % of the width: a 9:16 crop of a 16:9 frame keeps only 31.6 % of
  it, so corner text and even the edges of the middle third are lost. A portrait game keeps its whole width in that
  crop, so it has no width band, only the safe area. On a phone the corners also sit under notches and thumbs.
- **Every game passes the access baseline before launch (§J, CL32–CL37).** A check you could not make is NOT
  ASSESSED, never passed (CL38). `(start)` and CCGS-only numbers (MIT, licence in
  `${CLAUDE_PLUGIN_ROOT}/skills/genre-defaults/LICENSE.md`) in §J are targets: a miss passes only with a reason
  written in `DESIGN.md` Decisions.

## Building it

- **Chrome:** uGUI on a Canvas with Scale With Screen Size, under a `SafeAreaFitter` (`ui-ugui`, `platform-targets`).
  Put the shared look (font, sizes, colours, outline) in one place and reuse it; never style per view.
- **A label pinned to a world object:** project its position to the screen on each frame the object or the camera
  moves, clamp it a margin inside the safe area, and use outlined, backgroundless text that reads over any background.
  A projected point with z <= 0 is behind the camera and comes back mirrored: hide the label then, and when the object
  is off screen (behind or outside the viewport) hide it too, or, if the player must find it, swap it for an edge
  indicator pointing the real way (flip the direction of a behind-camera point before clamping). The label stays with
  its object; in landscape the camera keeps that object inside CL10's crop window, the label is never pulled off it.
- **Retiring a hint:** count successes per player and per verb, saved in the player's save file per profile so a
  relaunch keeps them; stop showing after the done-condition, and bring it back only after the unused stretch CL17
  sets.
- **Moments vs states:** a one-time moment is raised as an event the view listens to; a state is polled.
- **Per-frame cost:** write text only when it changes and build no strings per frame (`unity-performance`). Every
  mutable static gets a `SubsystemRegistration` reset.
- **Strings:** player-facing strings and Inspector text are in the language `CLAUDE.md` names. Once a second language is
  planned they come from the string table with named placeholders; always room for 40 % more length, the player's
  number format, casing in the shown language's culture (tr-TR for Turkish, so i → İ; never invariant or the OS
  culture) and a font that covers ç ğ ı İ ö ş ü (§I, CL27–CL31).
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
- `ui-ugui`, `platform-targets`: layout, scaling, safe area and input prompts per device; screen states and menu
  behaviour (Back, focus, the confirm dialog).
