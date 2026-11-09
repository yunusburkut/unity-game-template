# Reference teardowns: why the co-op chaos hits worked

Six games that define the space Mixtrol is moving into. Every number here has a source at the bottom;
where a figure is an estimate rather than a reported one it is marked *(est.)*. Do not quote a number
from this file that is not in the table — and do not invent one that sounds plausible.

The purpose of this document is not admiration. It is to isolate the **one machine** each of these games
built, so that `coop-mechanics-playbook.md` and `level-design-playbook.md` can rebuild that machine on a
horizontal axis.

## The comparison table

| | Chained Together | PEAK | Carry The Glass | Pico Park | Getting Over It / A Difficult Game About Climbing | Only Up |
|---|---|---|---|---|---|---|
| Released | Jun 2024 | Jun 2025 | Oct 2024 | 2016 / 2021 Steam | 2017 / 2024 | 2023 |
| Price | $4.99 | $7.99 | $2.99 | ~$4.99 | $7.99 / $6.99 | ~$9.99 |
| Units | 10 M+ | 10 M+ | 100–200 K *(est.)* | 1 M+ (877 K Steam *(est.)*) | millions, unreported | millions, delisted |
| Team | Anegar Games, French indie | 3 Aggro Crab + 4 Landfall = 7 | 2 devs (Çağatay Demir, Enes Kaplan), pub. SlugShot | 1 dev (TECOPARK) | 1 dev each | 1 dev |
| Budget / time | not reported | < $200 K, ~1 month jam in Seoul | not reported | not reported | not reported | not reported |
| Players | 1–4 | 1–4 | 2 | 2–8 | 1 | 1 |
| Axis | vertical | vertical | vertical-ish, level-based | horizontal | vertical | vertical |
| Coupling | physical chain between all players | none mechanical — shared stamina/afflictions, ropes and spikes left for others | one carried fragile object between two players | mutual dependency — bodies as platforms, shared keys | n/a | n/a |
| Loss engine | gravity + chain drag | gravity + stamina | **object breaks** | shared failure resets the stage | gravity | gravity |
| Reception | 90 % Very Positive, 50 K+ reviews | Best Multiplayer, Golden Joystick 2025 | 76 % positive, 703 reviews | very positive | very positive | mixed |
| Awards | Golden Joystick 2024, Streamer Awards 2024 | Golden Joystick 2025 | — | — | — | — |

## Chained Together — the reference implementation

**The machine.** Every player is on one physics-simulated chain. The chain wraps platforms, catches
edges, and yanks. One player's mistake is transmitted, immediately and visibly, into everyone else's
body. The developers describe resisting "the temptation to add complexity that would have obscured the
fundamental comedy" — the mechanic *is* the joke, not a delivery system for jokes.

**Structure.** A vertical run from the bottom of hell to heaven, each region visually distinct (bone
architecture and lava below, gold and light above), difficulty rising with altitude. The visual contrast
between the start and the end of the run is itself the progress bar.

**Loss tuning, three ways.** Hardcore mode adds rising lava — a chasing hazard that converts a spatial
problem into a time problem. Beginner mode returns players to their highest point instead of the bottom.
Golden wings from the upper regions let you glide a fall instead of eating it. This is the important
lesson: they did not pick one punishment severity, they shipped a **dial**, and the dial is what let both
a streamer audience and a casual friend group buy the same $4.99 game.

**Why it sold.** Every copy sold delivers 2–4 people into the session, and each of those people is a
potential buyer. Visible progress, dramatic failure, intense reactions — the structure is optimised for
the clip, not only for the play. Two years on it moved to publisher Secret Mode for long-term content.

## PEAK — the speed run

**The machine.** Free-form climbing with a stamina bar and "afflictions" that degrade it. There is no
mechanical tether: the coupling is *social and material* — you place ropes and spikes that make the route
easier for whoever comes after you, and you can pull a teammate onto a ledge. Cooperation is an
affordance, not a constraint. Betrayal is therefore also an affordance.

**The production lesson is the loudest one in this document.** Seven people, under $200 K, roughly one
month of in-person jam in Seoul, a fixed launch target they refused to move, and a commitment to ship
whatever was finished at the end of the month. 100 K units in 24 hours; break-even within hours.
Announcement to release was **five days**. Their own note on process: Discord text was a bad medium for
design direction — "text is evil" — and the in-person month is what made the design converge.

**The mountain is pre-generated per run**, which gives every stream a different route and keeps the
watch-value alive past the first week.

## Carry The Glass — the level-based carried-object proof

The most directly relevant game in this list, and the one Mixtrol should study hardest.

**The machine.** Two construction workers carry one fragile pane of glass. Physics runs on every part of
the characters. The glass is the entire design: it is the objective, the fail state, the tension meter,
and the comedy generator, all in one object. Nothing else in the game needs to be difficult, because
holding a shared rigid object between two independently-controlled ragdolls already is.

**This is how you get "visible loss" without relying on a long fall.** The pane breaking is instant,
legible with the sound off, and unambiguously someone's fault. That last property — *attributable* loss —
is what a chain and a fall also have, and what a plain "you died" does not.

**Structure.** Two large levels (Skyscraper, Lighthouse) rather than many small ones, and three
difficulty modes that change only checkpoint density: Normal, Hard (fewer checkpoints), Impossible
(none). The same content is sold three times, and the hardest cut is the one streamers attempt.

**Distribution.** $2.99. Online co-op *and* LAN *and* shared/split screen *and* Remote Play Together
*and* Family Sharing. Leaderboards and 19 achievements. They removed every reason a pair of friends could
not play tonight.

## Pico Park — horizontal, and viral anyway

**The machine.** 2–8 players, one key per stage, a goal door. Mutual dependency: you stand on each
other's heads, you form chains of bodies, you divide a puzzle that one player physically cannot solve.
Simple to present, deliberately vicious in level design.

**The hidden engine is sabotage.** The game "allows you to deliberately prank other players for kicks."
Accidental chaos is funny once; *intentional* betrayal is funny forever, because it is authored by the
players and therefore never repeats. Any co-op design that makes griefing impossible has removed its own
best content generator.

**The spread.** A gameplay tweet with 12 K+ retweets; a bilibili let's-play past 1 M views within days;
then eight Western streamers including Sykkuno and Valkyrae; then PewDiePie. Note the shape: it did not
start in the West, and it did not start with paid marketing. It started with one clip that read clearly
at thumbnail size.

## Getting Over It / A Difficult Game About Climbing — the solo control group

Included to mark the boundary of what Mixtrol should *not* copy.

Both are single-player, both remove checkpoints to maximise setback, both put the difficulty in an
awkward input mapping rather than in the level. A Difficult Game About Climbing maps mouse or stick input
to force vectors on the character's arms; one degree of error changes the outcome. Its one concession is
that bodies of water act as per-area checkpoints, so a fall costs an area, not the run.

The retention mechanism is loss aversion plus sunk cost: the pain of losing progress is felt more sharply
than the pleasure of gaining it, so players keep going to un-lose. Foddy's framing — a game made for a
certain kind of person, to hurt them — plus his constant asynchronous narration keeps the player in a
relationship with the designer.

**Why it does not transfer.** The watch-appeal is "someone suffering alone", which produces long streams
but no sales multiplier: one viewer buying it brings one player. The co-op games multiply by 2–4 at the
point of sale. Mixtrol is choosing the multiplier.

## Only Up — the cautionary one

Vertical, single player, an enormous Twitch spike in 2023, and then delisted by its own developer. The
lesson is not the removal; it is that a pure virality spike with a thin body of game behind it converts
into a short burst and a mixed review score. Chained Together and PEAK held 90 %+ across tens of thousands
of reviews and kept selling for years. **Spike is the marketing outcome; retention is the design outcome.
Do not plan for one and hope for the other.**

## What all six share

1. **Loss is instant, visible, and attributable.** A viewer with the sound off knows what was lost and
   roughly whose fault it was, within one second.
2. **One mechanic carries the whole game.** No second system competes for the player's attention at the
   moment of failure.
3. **The price is below the threshold where a group deliberates.** $3–8, every one of them.
4. **Failure is replayable in place.** You are never taken out of the world to a menu to try again.
5. **Punishment is a dial, not a constant** — Carry The Glass and Chained Together both shipped a
   difficulty dial.
6. **Progress is legible in the frame itself** — altitude, a biome change, a pane still intact.

## Sources

- Game Developer — [How co-op climbing hit Peak achieved 2 million sales for less than $200,000](https://www.gamedeveloper.com/production/how-co-op-climbing-hit-peak-achieved-2-million-sales-for-less-than-200-000-)
- indiegame.com — [Chained Together Two Years On: 10 Million Sales](https://indiegame.com/en/archives/28817)
- GamesRadar+ — [10,000 reviews, 90% positive on Steam, and only $5 — viral hit Chained Together](https://www.gamesradar.com/games/co-op/10000-reviews-90-positive-on-steam-and-only-dollar5-viral-hit-chained-together-uses-the-power-of-co-op-to-ruin-up-to-four-friendships-at-once/)
- Steam — [Carry The Glass store page](https://store.steampowered.com/app/3263320/Carry_The_Glass/) (price, tags, modes, features)
- SteamSpy — [Carry The Glass](https://steamspy.com/app/3263320) (owner estimate)
- AUTOMATON WEST — [PICO PARK sales exceed 1 million units](https://automaton-media.com/en/news/20211011-3784/)
- TheGamer — [How Difficult Games Like Getting Over It Become Twitch Hits](https://www.thegamer.com/new-twitch-genre-train-wreck/)
- Critical Video Game Studies — [Getting Over It: Driving Forces in Rage Games](https://criticalvideogamestudies.com/getting-over-it-driving-forces-in-rage-games/)
- Wikipedia — [A Difficult Game About Climbing](https://en.wikipedia.org/wiki/A_Difficult_Game_About_Climbing) · [Peak](https://en.wikipedia.org/wiki/Peak_(video_game)) · [Chained Together](https://en.wikipedia.org/wiki/Chained_Together) · [Pico Park](https://en.wikipedia.org/wiki/Pico_Park)
- The Psychology of Games — [Loss Aversion and Game Design](https://www.psychologyofgames.com/2020/09/podcast-63-loss-aversion-and-game-design/)
