# Clarity playbook: telling Mixtrol players what to do

**Status:** draft 1, 2026-10-17, written for MIX-301, where three items are still open: the pre-round screen, the
context hints and the event narration. This is a research and method doc, written in English like
`difficulty-rhythm.md`. Player-facing strings are Turkish. Decisions stay with `docs/gdd.md` and the user: this doc
proposes, and §H lists what is still open. The procedure that applies it is the gamekit plugin skill
`gamekit:player-clarity` (`plugin/skills/player-clarity/SKILL.md`).

**Rule IDs** have one source: the plugin's `plugin/skills/player-clarity/references/clarity-rules.md` (CL01–CL38).
Append new rules there and never renumber. The CL01–CL22 texts below are this game's co-op application of those
rules, written before they were generalised, so their wording is narrower: where the two differ (CL10, CL14, CL19,
CL21, CL22 name seats, screens and blame here), cite the plugin rule and read the text below as Mixtrol's instance
of it.

**Tags:**
- `(src: KEY)` is a source in §I.
- `(repo: …)` is a decided repo rule or existing code.
- `(start)` is a starting value to tune in Play Mode.
- `[inferred]` is our own extrapolation, with no direct source.

The sources were gathered by web search on 2026-10-17. Not every page was re-read after the search; where a claim
rests on a wiki or a third-party blog, the source list says so.

## A. What the research says

1. **The friend-slop hits barely teach. Voice chat does.**
   - We sampled the 100 most helpful negative Steam reviews of five games. Confusion is a minor complaint in all of
     them: R.E.P.O. 16 of 100 mention any confusion, PEAK about 5, Lethal Company 1, Chained Together 0 and
     Content Warning 1. Repetition, bugs and lobbies dominate. (src: STEAM)
   - PEAK's core takes under three minutes to explain, and the rest is learned from a friend shouting right after
     you hit the danger. (src: PEAK-GDC)
   - So the job is not a tutorial. The job is to give the first player one sentence, and the words to pass it on.
2. **Nobody reads.**
   - People read about 20% of the words on a page. (src: NNG)
   - Working memory holds about four chunks. (src: COWAN)
   - WarioWare gives one or two words, and its designer gives the player about five seconds to understand the
     game. (src: WARIO)
3. **Doing beats reading.** Mario 1-1's mushroom, Limbo's cage and Portal's chamber 03 each force the lesson once,
   in a place where failing costs nothing. (src: FORCE)
4. **Information belongs where the eyes already are, on the body.**
   - Celeste's hair shows whether the dash is ready.
   - Splatoon's tank on your back is your ammo.
   - Smash paints the launch trail in the attacker's colour. (src: SMASH)
5. **UI reads as "template" when it could sit in any game.** The usual suspects: the centred modal, the objective
   tracker, the pulsing arrow, yellow paint, glass, gradients, emoji and default fonts. (src: TELLS)

## B. Four tests for every player-facing element

| ID | Test | It passes when |
|---|---|---|
| CL01 | Speakable | someone can say the rule aloud in 5 s |
| CL02 | Muted clip | a stranger names who did what to whom |
| CL03 | Paste | it would not work in another game |
| CL04 | Budget | ≤ 3 new things, readable in time |

- **CL01, speakable.** The rule is one sentence that a player says on Discord in five seconds or less. On screen
  it is six words or fewer. Fall Guys' bar is the same: if they could not explain a round in one sentence, they
  did not build it. (src: FALLGUYS, WARIO)
- **CL02, muted clip.** Take three seconds of a muted clip, cropped to 9:16. A stranger who watches it must be able
  to say who did what to whom. This extends the test `FailureView` already states. (repo: `FailureView` summary;
  src: CLIP)
- **CL03, paste.** If the element would work unchanged in another game, it is not ours. Rebuild it on one of
  Mixtrol's own carriers (§C): the swap, the partner's body, the radio, the seat colour, the ruins.
- **CL04, budget.** No more than three new things at once. (src: HODENT) A line stays on screen long enough to
  read at 17–20 characters a second, so a 40-character line needs about 2.5 s. (src: SUBS)

## C. Where the information lives

**CL05, the carrier ladder.** Use the first rung that can carry the message. Going down a rung needs a reason.

1. **The bodies.** The characters, their feet, their afterimages and the radio in their hand. The eyes are already
   there, and a vertical crop keeps them. (repo: `PlayerSeatMaterialView`, `SwapSignalView`, `ControlSwapView`)
2. **The world.** The ruin's walls and floor, and the device itself. Both stay visible for the whole round.
   (src: BABA, SIGN)
3. **The radio.** This is Mixtrol's own narrator: it already comes out when a held move is played, in the owner's
   colour. Its lines are short and come from a person in the game, not from the game. (repo: `ControlSwapView`;
   src: RADIO)
4. **Sound.** One distinct sound per relationship, for example "someone played my jump". (src: RL)
5. **The HUD pill.** Last. The corners are full, so a new pill needs the user's yes on its place.
   (repo: minimal-hud memory) The time and the progress live here, but instructions do not.

**CL06, let the world enforce it.** If the world can enforce a rule, do not write it down.
- PEAK's Scoutmaster throws back anyone who climbs too far ahead, so "stay together" is never said. (src: PEAK-GDC)
- In Ultimate Chicken Horse, if everyone finishes, nobody scores. (src: UCH)

**CL07, one code everywhere.** A colour or a shape means one thing across the whole game. The seat colour means
ownership, orange means interaction and red means a deadly edge (repo: MIX-299). A code learned once is read
everywhere without words; in Cuphead, anything pink can be parried. (src: FORCE)

**CL08, speakable names.** Everything the screen shows has a word players can shout: the player's name, the seat
colour's name, the verb ("zıplat"). The UI feeds the Discord conversation; it does not replace it.

**CL09, never colour alone.** Pair a colour with a direction, a name or a shape. (src: GAG) Today's pairing is the
direction of the slice plus the online name (repo: minimal-hud). See §H.1: offline there are no names.

**CL10, attribution inside the 9:16 crop window (about the centre 30 %, narrower than the middle third).** Put it in world space, outlined, at least 26 px at 1080p. Corners are
the first thing a vertical crop loses: a 9:16 crop of a 16:9 frame keeps 31.6% of its width.
That holds for a landscape frame; a portrait game keeps its whole width in a 9:16 crop and only needs the safe area
(plugin skill player-clarity, CL10). (src: CLIP, XAG)

## D. The three moments (MIX-301's open items)

### D1. Before the round

**CL11, ready by doing.** The round does not start on a button.
- Each player does the round's verb once in a safe start area, and the partner's body answers.
- When everyone has done it, the round starts.
- The ready check is the forced lesson.

Precedents: the first mushroom in Mario 1-1, the practice round in Mario Party and the indoor climbing wall in PEAK's
airport. (src: FORCE, PARTY, PEAK-WIKI)

**CL12, the rule stays in the world.** One line of six words or fewer, on the ruin wall behind the start, visible for
the whole round. It is never a card that disappears. (src: BABA, SIGN)

**CL13, the full explanation only once.** The first time a rule appears: the wall line, plus a two-second mime by the
players' own bodies. After that, only the line. WarioWare Smooth Moves voices a pose's explanation only the first time
the pose appears. (src: WARIO)

**CL14, each screen speaks its own half, by name.** "Space → Ali zıplar", with the name in Ali's colour; never "your
partner". `TutorialHintView` already reads the live table, so the same place reads differently on the two screens.
(repo: `TutorialHintView`)

**CL15, no timeout on reading.** Text never times out before it can be read: 14% of adults read below age 11.
(src: GAG) The only cap is for a player who is away, (start) 20 s.

**Decided 2026-10-17 (user, from the prototype): all three together.** Prova, Duvar yazısı and Kukla gösterisi
left the pool as one start.
- **The pen.** The start is closed by a gate across the lane. Behind it the players can walk and jump; the run's
  clock does not run.
- **Kukla gösterisi (first round only).** Puppet strings come down onto every body that holds a move. Each player's
  own body presses Space once, in seat order, so the partner hops with the radio, the ring and the afterimages it
  always has. Then a chalk arrow is drawn toward the finish and the bodies take a step that way. Control comes back after
  about 3 s. The presses go through the real keys, so online every screen sees the same hops.
- **Duvar yazısı.** "Space → öteki zıplar" and "İlk varan kazanır" stay chalked over the pen all round. Under them
  is each player's name; the name is drawn in their colour and struck under once they have done the Prova.
- **Prova.** Each player presses Space once. On the first round a line over their own body says it with the
  partner's name: "Space → Veli zıplar". When everyone holding a move has pressed, the gate drops and the clock
  starts. The away cap is 20 s from the first press. A Tekrar skips the mime and the line; the Prova stays.
  A player alone holds no move: offline the gate drops at once; a host alone waits the same 20 s for a partner,
  and a partner who joins in time gets the Prova (decided 2026-10-17).

### D2. During the round

**CL16, only to the one who must act.** A hint shows only when it applies, and only on the screen of the player
who must act. It sits on the body or in the world. Celeste's bird shows the dash as the bridge falls. In a test with
45,000 players, hints tied to the context helped and front-loaded ones did not. (src: CELESTE, ABTEST)

**CL17, every hint retires.** Each hint has a done-condition, counted per player. After (start) 2–3 successes it
stops showing, and it may come back after (start) 3 rounds unused. Valve's game instructor and `InteractPromptView`
both work this way. (src: VALVE; repo: `InteractPromptView.lessons` = 3)

**CL18, never repeat the world.** No hint says what the world already shows.

### D3. After the moment

**CL19, one rule decides the blame.** The blame goes to the last player whose move acted on you, and it clears once
you land and stand. Smash credits a KO the same way. (src: SMASH; repo: DA-11, the partner who launched is named
first)

**CL20, the cost decides the size.**
- **Tier 1, recovered in place.** A small label at the body, three words or fewer. (repo: `NearMissView`,
  "−12 m · 2P zıplattı")
- **Tier 2, shared death.** The culprit's name over the body (repo: `FailureView`), and the moment is kept for the
  results.

**CL21, blame is a party, not a fine.** The results screen is where the blame pays off. In Ultimate Chicken Horse,
the score bar is built from who trapped whom. (src: UCH)

**CL22, paint the culprit on the victim.** The victim carries the culprit's colour, as with Smash's launch trail.
(src: SMASH) Mixtrol's afterimages already take the colour of the player who pressed. (repo: `SwapSignalView`)

## E. Mixtrol's voice

- Turkish, second person, an order or a bare fact. Start with the verb or with a name.
- Use names, not roles: "Ali", never "arkadaşın" or "rakip".
- One to four words. The arrow (→) and the colour count as words.
- Sentence case. Capitals only for the shout of a moment, like "KIL PAYI!". (repo: user decision 2026-10-15)
- Numbers only when they are the stake or the joke: "−12 m", "1:23.45".
- Never: "Tebrikler", "Görev", "Hedef:", "Hazır mısın?", stacked exclamation marks, "… yapabilirsin" sentences.

| Template | Ours |
|---|---|
| Space tuşuna basarak arkadaşının zıplamasını kontrol edebilirsin! | Space → Ali zıplar |
| Görev: Bitişe ilk sen ulaş | İlk varan kazanır |
| Tebrikler, kazandın! | Ali kazandı |
| Arkadaşın seni zıplattı ve düştün | Veli zıplattı |
| HAZIR MISIN? [Evet] | Nothing: you are ready when you have done it once (CL11) |

## F. Never: the template tells

Each of these is a sign that the UI could sit in any game (src: TELLS):

- a centred modal with a title, a body and an OK button;
- an objective tracker, a checklist or a "Görev:" line;
- a pulsing arrow, or a glow on everything that can be touched ("yellow paint");
- glass, blur, gradients, or a hairline border with a wide shadow;
- emoji, a stock icon set or a default font;
- bouncing or elastic easing on UI;
- a character who says the solution out loud;
- the same kind of action on two different keys. In PEAK, a friend kept left-clicking to revive when it needed
  right-click. (src: AVCLUB)

## G. Candidate pool: carriers we have not built

None of these is decided. The user picks, through an interactive prototype. Prova, Duvar yazısı and Kukla
gösterisi were chosen together on 2026-10-17 and left the pool (D1).

| Name | What | Precedent | Cost |
|---|---|---|---|
| Telsiz anonsu | the radio speaks the line | Firewatch, We Were Here | one more thing at the body |
| Kanıt fotoğrafı | the blame frame on the results | Content Warning, UCH | a RenderTexture grab |
| Tebeşir izi | chalk outline where someone fell | Dark Souls, Portal | clutter, needs a cap |
| Ses imzası | a sound when your jump is played | Rocket League | one audio clip |
| Yanlış ekran | your hint shows on their screen | Spaceteam, Keep Talking | breaks on one PC |
| Geri sayım | a shared 3-2-1 for a held jump | Bread & Fred | needs a key |

- **Telsiz anonsu.** The radio becomes the game's only narrator. Instructions and narration come out of it as a
  short transcript at the speaker, in their colour. It gives the game a voice no other game has.
- **Kanıt fotoğrafı.** The frame where someone's press killed someone else is captured locally and pinned on the
  results, with a caption like "Ali → Veli". The results screen becomes a blame album, which is the clip people
  share.
- **Tebeşir izi.** A chalk body outline with the name stays where someone fell in this session. It marks the danger
  and keeps the joke going. It must be capped, (start) at 5, and cleared on Tekrar.
- **Ses imzası.** Your radio crackles in a distinct way when someone else plays your jump, so you know without
  looking.
- **Yanlış ekran.** The hint for what Ali must do shows on Veli's screen, so Veli has to say it out loud. It turns
  instructions into Discord talk. Offline on one PC both halves are visible, so it does nothing there.
- **Geri sayım.** A shared 3-2-1 so a held jump can be timed. It needs a key, which breaks "one key per action"
  (CLAUDE.md). It only works if it rides an existing key.

## H. Open decisions (the user's)

1. **Seat shapes and colour blindness.** CL09 says never colour alone. The seat shapes were removed on 2026-10-14
   (MIX-155), and today the slice direction and the online name carry the identity. Offline on one PC there are no
   names. Overcooked made its shapes permanent rather than optional. (src: OVERCOOKED) Do the shapes come back
   somewhere, for example only on the results screen and the blame label?
2. **The pill and the instruction.** A rounded pill with a sans label sits close to the web's template family
   [inferred]. As chrome (the time, the progress) it is quiet and fine. The question is whether instructions leave
   the pills entirely, per CL05: `TutorialHintView` and `InteractPromptView` are pills today.
3. ~~**Where the Prova happens in Test.**~~ Decided 2026-10-17 with the prototype: the start line as it is, closed
   by a gate that drops (D1).

## I. Sources

- **ABTEST:** Andersen et al., CHI 2012, 45,000+ players and 8 tutorial designs.
  https://grail.cs.washington.edu/projects/game-abtesting/chi2012/
- **AVCLUB:** https://www.avclub.com/not-every-co-op-game-is-friendslop
- **BABA:** https://www.gamedeveloper.com/disciplines/road-to-the-igf-hempuli-oy-s-i-baba-is-you-i-
- **CELESTE:** https://digitaltrends.com/gaming/celeste-review
- **CLIP:**
  - Zach Gage's "three reads" (GDC 2018): https://gigazine.net/gsc_news/en/20180501-game-design-subway-legibility
  - TikTok safe zones: https://adkit.so/tools/safe-zones/tiktok
  - The 3-second hook figure comes from a third-party blog:
    https://houseofmarketers.com/importance-of-tiktok-ad-hooks-first-3-seconds/
- **COWAN:** Cowan 2001, "The magical number 4".
  https://www.cambridge.org/core/journals/behavioral-and-brain-sciences/article/magical-number-4-in-shortterm-memory-a-reconsideration-of-mental-storage-capacity/44023F1147D4A1D44BDC0AD226838496
- **FALLGUYS:** https://www.pcgamesinsider.biz/feature/69833/how-mediatonic-made-the-takeshis-castle-of-video-games-in-fall-guys/
- **FORCE:**
  - Mario 1-1: https://gamedeveloper.com/design/how-miyamoto-built-i-super-mario-bros-i-legendary-world-1-1
  - Limbo: https://www.gamedeveloper.com/game-platforms/gdc-europe-i-limbo-i-s-carlsen-on-making-players-your-worst-enemy-and-your-best-friend
  - Portal developer commentary (wiki): https://theportalwiki.com/wiki/Portal_developer_commentary
  - Cuphead's pink parry (blog): https://cyberpost.co/can-you-only-parry-pink-things-in-cuphead/
- **GAG:** Game Accessibility Guidelines.
  - Colour: https://gameaccessibilityguidelines.com/ensure-no-essential-information-is-conveyed-by-a-colour-alone/
  - Reading age: https://gameaccessibilityguidelines.com/?p=3347
- **HODENT:** https://celiahodent.com/gamers-brain-ux-onboarding/
- **NNG:** https://www.nngroup.com/articles/how-little-do-users-read/
- **OVERCOOKED:** https://blog.playstation.com/?p=340908
- **PARTY:** Mario Party practice (wiki): https://www.mariowiki.com/Minigame
- **PEAK-GDC:** https://media.gdcvault.com/gdc2026/GNR/Papers/Zac+Millman+-+GDCReview_2026_Peak_Millman.pdf
- **PEAK-WIKI:** https://peak.wiki.gg/wiki/Airport
- **RADIO:**
  - Firewatch (GDC 2017): https://gdconf.com/news/come-gdc-2017-hear-firewatchs-unique-dialog-system-works
  - We Were Here: https://www.gamedeveloper.com/game-platforms/road-to-the-igf-total-mayhem-games-i-we-were-here-i-
- **RL:** Rocket League v2.40 patch notes. https://www.rocketleague.com/news/patch-notes-v2-40
- **SIGN:** Portal test sign. https://developer.valvesoftware.com/wiki/Test_Sign
- **SMASH:** fan wiki.
  - KO credit: https://www.ssbwiki.com/KO
  - Launch trail: https://www.ssbwiki.com/List_of_tips_(SSBU)/Other
- **STEAM:** our own sample, 2026-10-17: the 100 most helpful English negative reviews per game, from
  `store.steampowered.com/appreviews/<id>?json=1&review_type=negative`. Survivorship bias: confused players may
  refund rather than review. The genre view behind it: https://appmagic.rocks/blog/friendslop-steam-games-2025
- **SUBS:** subtitle reading speeds. https://titlevision.dk/sm/reading_speed.htm
- **TELLS:**
  - Web "AI tells", applied to games [inferred]: https://www.impeccable.style/slop
  - Yellow paint: https://vice.com/en/article/5d9zbx/resident-evil-4s-yellow-boxes-are-not-a-betrayal-theyre-a-symptom
  - UI as identity (Edd Coates): https://www.pocketgamer.biz/pg-connects-london-the-untapped-artistry-of-ui/
  - A protagonist who says the solution: https://pushsquare.com/news/2022/11/talking-point-what-are-your-thoughts-on-protagonists-discussing-puzzles
  - Diegetic, spatial and meta UI: https://www.gamedeveloper.com/design/game-ui-discoveries-what-players-want
- **UCH:** https://www.cleverendeavourgames.com/blog/2015/11/5/dont-fear-game-design-change
- **VALVE:** game instructor (wiki, read through search snippets).
  https://developer.valvesoftware.com/wiki/List_of_L4D2_Instructor_Messages
- **WARIO:**
  - Microgames: https://www.mariowiki.com/Microgame
  - Iwata Asks: https://iwataasks.nintendo.com/interviews/wii/warioware_smooth_moves/0/2
- **XAG:** Xbox Accessibility Guideline 101.
  https://learn.microsoft.com/en-us/gaming/accessibility/xbox-accessibility-guidelines/101
- **Candidate precedents not cited above:**
  - Half-Life 2 Dog: https://developer.valvesoftware.com/wiki/Dog/Playing_fetch
  - Cocoon: https://tryhardguides.com/cocoon-developer-explains-why-tutorials-arent-needed/
  - Content Warning: https://contentwarning.wiki.gg/wiki/Diving_Bell
  - Spaceteam: https://episodiccontentmag.com/2016/01/29/everybodyshake2/
  - Bread & Fred: https://www.shacknews.com/article/135585/bread-and-fred-review-score
  - Rattmann's scrawls: https://theportalwiki.com/wiki/Doug_Rattman/cs
