# Clarity rules: telling players what to do

**Rule IDs** are **CL01–CL22**, local to this skill. Append new ones and never renumber.

**Tags:**
- `(src: KEY)` is a source in §H.
- `(start)` is a starting value to tune in Play Mode.
- `[inferred]` is an extrapolation with no direct source.

Not every page was re-read after it was found; where a claim rests on a wiki or a third-party blog, the source list
says so.

## A. What the research says

1. **Hits barely teach; the first explanation matters most.**
   - In a sample of the 100 most helpful negative Steam reviews of five popular co-op games, confusion was a minor
     complaint in all of them; repetition, bugs and lobbies dominated. (src: STEAM)
   - PEAK's core takes under three minutes to explain, and the rest is learned from a friend right after you hit the
     danger. (src: PEAK-GDC)
   - So the job is rarely a long tutorial. It is one sentence the first player understands, and the words to pass on.
2. **Nobody reads.**
   - People read about 20 % of the words on a page. (src: NNG)
   - Working memory holds about four chunks. (src: COWAN)
   - WarioWare gives one or two words, and its designer gives the player about five seconds to understand the game.
     (src: WARIO)
3. **Doing beats reading.** Mario 1-1's mushroom, Limbo's cage and Portal's chamber 03 each force the lesson once, in a
   place where failing costs nothing. (src: FORCE)
4. **Information belongs where the eyes already are, on the body.**
   - Celeste's hair shows whether the dash is ready.
   - Splatoon's tank on your back is your ammo.
   - Smash paints the launch trail in the attacker's colour. (src: SMASH)
5. **UI reads as "template" when it could sit in any game.** The usual suspects: the centred modal, the objective
   tracker, the pulsing arrow, yellow paint, glass, gradients, emoji and default fonts. (src: TELLS)
6. **Context beats front-loading.** In a test with 45,000+ players and eight tutorial designs, tutorials tied to the
   moment they apply helped; front-loaded ones did not. (src: ABTEST)

## B. Four tests for every player-facing element

| ID | Test | It passes when |
|---|---|---|
| CL01 | Speakable | someone can say the rule aloud in 5 s |
| CL02 | Muted clip | a stranger names who did what (to whom) |
| CL03 | Paste | it would not work in another game |
| CL04 | Budget | ≤ 3 new things, readable in time |

- **CL01, speakable.** The rule is one sentence a player can say in five seconds or less. On screen it is six words or
  fewer. Fall Guys' bar is the same: if they could not explain a round in one sentence, they did not build it.
  (src: FALLGUYS, WARIO)
- **CL02, muted clip.** Take three seconds of a muted clip, cropped to 9:16. A stranger who watches it can say what
  happened and who did it. Many phone players play muted, so this is also the in-game test. (src: CLIP)
- **CL03, paste.** If the element would work unchanged in another game, it is not ours. Rebuild it on one of the game's
  own carriers (§C).
- **CL04, budget.** No more than three new things at once. (src: HODENT) A line stays on screen long enough to read at
  17–20 characters a second, so a 40-character line needs about 2.5 s. (src: SUBS)

## C. Where the information lives

**CL05, the carrier ladder.** Use the first rung that can carry the message. Going down a rung needs a reason.

1. **The body.** The character or the piece the player controls: its pose, colour, trail, the thing in its hand. The
   eyes are already there, and a vertical crop keeps it.
2. **The world.** Walls, floors, the device itself. They stay visible the whole time. (src: BABA, SIGN)
3. **The game's own narrator**, if it has one: a character, a radio, a sign-holder. Short lines from a person in the
   game, not from the game. (src: RADIO)
4. **Sound and haptics.** One distinct sound (and on mobile one distinct haptic) per relationship. (src: RL)
5. **The HUD.** Last. Time, score and progress live here; instructions do not.

**CL06, let the world enforce it.** If the world can enforce a rule, do not write it down.
- PEAK's Scoutmaster throws back anyone who climbs too far ahead, so "stay together" is never said. (src: PEAK-GDC)
- In Ultimate Chicken Horse, if everyone finishes, nobody scores. (src: UCH)

**CL07, one code everywhere.** A colour or a shape means one thing across the whole game (for example: the player's
colour means ownership, one accent means "interactable", red means deadly). A code learned once is read everywhere
without words; in Cuphead, anything pink can be parried. (src: FORCE)

**CL08, speakable names.** Everything the screen shows has a word players can say: the verb, the object, the colour's
name, the player's name.

**CL09, never colour alone.** Pair a colour with a direction, a name, an icon or a shape. (src: GAG) About 1 in 12 men
has a colour vision deficiency; check every colour code with a colour-blind simulation.

**CL10, key information in the middle third.** Put attribution and key labels in world space or near the action,
outlined, at least 26 px at 1080p. Corners are the first thing a vertical crop loses: a 9:16 crop of a 16:9 frame keeps
31.6 % of its width. On a phone, corners also sit under notches and thumbs. (src: CLIP, XAG)

## D. The three moments

### D1. Before play

**CL11, ready by doing.** Play does not start on an OK button. The player does the core verb once in a safe space; when
they have, play starts. The ready check is the forced lesson. Precedents: the first mushroom in Mario 1-1, the practice
round in Mario Party, the climbing wall in PEAK's airport. (src: FORCE, PARTY, PEAK-WIKI)

**CL12, the rule stays in the world.** One line of six words or fewer, placed in the world where it applies and visible
the whole time. Never a card that disappears. (src: BABA, SIGN)

**CL13, the full explanation only once.** The first time a rule appears: the world line plus a short demonstration by
the game's own pieces. After that, only the line. WarioWare voices a pose's explanation only the first time it
appears. (src: WARIO)

**CL14, speak to the one who acts.** A prompt names the input for the device in use ("Tap", the key, the button) and,
in multiplayer, the player by name, on that player's screen.

**CL15, no timeout on reading.** Text never times out before it can be read: 14 % of adults read below age 11.
(src: GAG) The only cap is for a player who is away, (start) 20 s.

### D2. During play

**CL16, only to the one who must act.** A hint shows only when it applies, and only for the player who must act. It
sits on the body or in the world. Celeste's bird shows the dash as the bridge falls. (src: CELESTE, ABTEST)

**CL17, every hint retires.** Each hint has a done-condition, counted per player. After (start) 2–3 successes it stops
showing, and it may come back after a long stretch unused. Valve's game instructor works this way. (src: VALVE)

**CL18, never repeat the world.** No hint says what the world already shows.

### D3. After an event

**CL19, one rule decides the cause.** Pick one rule for who or what caused a failure, and show it the same way every
time. In multiplayer: the last player whose action acted on you, cleared once you are safe again. Smash credits a KO the
same way. (src: SMASH)

**CL20, the cost decides the size.**
- **Recovered in place:** a small label at the body, three words or fewer.
- **A real failure:** the cause named over the body, and the moment kept for the results.

**CL21, failure is a story, not a fine.** The results screen is where failures pay off: what happened, the best moment,
the near miss. In Ultimate Chicken Horse the score bar is built from who trapped whom. (src: UCH)

**CL22, paint the cause on the victim.** The victim carries the cause's colour or mark, as with Smash's launch trail.
(src: SMASH)

## E. The game's voice

Write it into `DESIGN.md` once; these are the defaults:

- Second person, an order or a bare fact. Start with the verb or a name.
- Names, not roles.
- One to four words. An arrow (→) and a colour count as words.
- Sentence case. Capitals only for the shout of a moment.
- Numbers only when they are the stake or the joke.
- Never: "Congratulations", "Mission:", "Objective:", "Are you ready?", stacked exclamation marks, "you can …"
  sentences.

| Template | Better |
|---|---|
| Press Space to make your character jump! | Space → jump |
| Objective: reach the finish first | First one there wins |
| Congratulations, you won! | Ali wins |
| Your partner made you fall | Veli did it |
| ARE YOU READY? [Yes] | Nothing: you are ready when you have done it once (CL11) |
| Tap anywhere to continue | Nothing, or the next screen's first action |

## F. Never: the template tells

Each of these is a sign that the UI could sit in any game (src: TELLS):

- a centred modal with a title, a body and an OK button;
- an objective tracker, a checklist or a "Mission:" line;
- a pulsing arrow, or a glow on everything that can be touched ("yellow paint");
- glass, blur, gradients, or a hairline border with a wide shadow;
- emoji, a stock icon set or a default font;
- bouncing or elastic easing on UI;
- a character who says the solution out loud;
- the same kind of action on two different inputs. In PEAK, a friend kept left-clicking to revive when it needed
  right-click. (src: AVCLUB)

## G. Carrier ideas worth prototyping

None of these is a rule; each is a precedent to offer as a prototype option.

| Name | What | Precedent |
|---|---|---|
| Narrator | A character or object in the world speaks the instructions as a short transcript | Firewatch, We Were Here |
| Evidence photo | The frame of a failure is captured and pinned on the results screen | Content Warning, Ultimate Chicken Horse |
| Chalk outline | A mark stays where someone failed this session (capped, cleared on restart) | Dark Souls, Portal |
| Sound signature | A distinct sound when something happens to you that you did not do | Rocket League |
| Wrong screen (multiplayer) | Your hint shows on the partner's screen, so they have to say it | Spaceteam, Keep Talking |
| Shared countdown (multiplayer) | A 3-2-1 for a synchronised action, riding an existing input | Bread & Fred |

## H. Sources

- **ABTEST:** Andersen et al., CHI 2012, 45,000+ players and 8 tutorial designs.
  https://grail.cs.washington.edu/projects/game-abtesting/chi2012/
- **AVCLUB:** https://www.avclub.com/not-every-co-op-game-is-friendslop
- **BABA:** https://www.gamedeveloper.com/disciplines/road-to-the-igf-hempuli-oy-s-i-baba-is-you-i-
- **CELESTE:** https://digitaltrends.com/gaming/celeste-review
- **CLIP:**
  - Zach Gage's "three reads" (GDC 2018): https://gigazine.net/gsc_news/en/20180501-game-design-subway-legibility
  - TikTok safe zones: https://adkit.so/tools/safe-zones/tiktok
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
- **STEAM:** a sample taken on 2026-10-17: the 100 most helpful English negative reviews per game, from
  `store.steampowered.com/appreviews/<id>?json=1&review_type=negative`. Survivorship bias: confused players may refund
  rather than review.
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
