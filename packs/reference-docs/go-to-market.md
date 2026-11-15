# Go to market

How this genre actually sells. Same rule as the other documents: sourced numbers are cited, everything
else is marked as a target to be set rather than a fact.

**Not a game's plan file.** This is Mixtrol's genre study. `gamekit:launch-review` creates each game's own
`docs/go-to-market.md` with its own headings, and the launch auditor treats that file's decisions as the baseline;
do not copy this one there. Read it as an example of the research behind such a plan.

## The one economic fact that shapes every decision below

**A co-op game multiplies at the point of sale.** One person buys it, then brings 1–3 friends into a
session, and each of those friends is a candidate buyer of the same $5 game — often within the hour.
A single-player rage game does not do this: one viewer buying it produces one player. That multiplier is
why PEAK passed 2 million sales on a budget under $200 K (Game Developer, in Sources) and both PEAK and
Chained Together went on to roughly 10 million units *(est., unsourced here: verify before quoting)*, while the solo
games in the same design tradition, with comparable streaming fame, did not.

Everything below is downstream of protecting that multiplier.

## Price

| Game | Price |
|---|---|
| Carry The Glass | $2.99 |
| Chained Together | $4.99 |
| PEAK | $7.99 |
| Pico Park | ~$4.99 |

**Target: $4.99, with a launch discount.** PEAK launched at $7.99 with a 38 % launch discount — under $5
effective — and was explicitly designed as an impulse purchase.

The reasoning is not "cheap games sell more". It is that **a group purchase has to clear four wallets, not
one**. At $5 nobody in the group deliberates; at $15 one person says "next week" and the session does not
happen — and a session that does not happen produces no clip, which costs you the next wave of buyers.
The price is a virality parameter, not a revenue parameter.

Do not launch above $7.99. Do not launch free; free removes the impulse-purchase signal and the review
count that carries the store page.

## Copy policy — the decision to make early

Carry The Glass supports Online co-op, LAN, shared/split-screen, **Remote Play Together**, and Family
Sharing simultaneously. With Remote Play Together only the host owns the game; friends join through the
Steam overlay.

The trade is real and it goes both ways:

- **Everyone buys** maximises revenue per group, and it is what Chained Together and PEAK do, at an estimated 10 M units
  each *(est.; the cited figure is PEAK's 2 M)*. It only works if the price is low enough that four purchases are trivial.
- **Remote Play Together** maximises the number of sessions that actually happen, which maximises clips —
  at the cost of three of four sales.

**Recommendation: ship online co-op as the primary path with everyone buying, and add Remote Play Together
as well.** They are not mutually exclusive, and the friction it removes ("my friend hasn't bought it yet,
let's play tomorrow") is exactly the friction that kills the first weekend. Steam also runs recurring
Remote Play Together sale and fest events, which is a free visibility slot you are otherwise not eligible
for.

Native online co-op is non-negotiable regardless: Remote Play Together streams video, which makes a
precision platformer feel bad for the non-host, and feeling bad is the one thing that kills a review score.

## Store page

### Tags

Derived from the two closest comparables' live tag sets (Carry The Glass, Chained Together). Order
matters — Steam weights the first few:

`Co-op` · `Online Co-Op` · `Multiplayer` · `Funny` · `2.5D` · `Platformer` ·
`Puzzle Platformer` · `Casual` · `Family Friendly` · `Cartoony` · `Parkour` · `Linear`

*Corrected 2026-09-22:* no `Local Co-Op` — one-keyboard 2P is a test harness and a release build spawns
one local player; `Physics` and `3D Platformer` did not describe the game, `2.5D` does.

Put `Co-op` and `Funny` first. Do not lead with `Puzzle Platformer`: it is accurate to Mixtrol's origins
and it is the wrong shelf — it puts the game next to thoughtful solo games rather than next to the games
people buy to ruin a friendship with.

### Capsule

**This is the single highest-leverage marketing asset you will produce**, and it is chronically
under-budgeted by indie teams. Streamers decide whether to cover a game partly on the capsule, because a
capsule that works is a thumbnail that works, and professional streamers spend hours on thumbnails. A good
enough capsule gets a game covered by people hoping for the click.

Requirements:

- Readable at ~231×87 px (the small capsule), not at the size you design it.
- Show **two or more characters and the swap** — one moving the other, a cord or light in the owner's
  colour between the bodies — because the coupling is the pitch. The cauldron is secondary (decided
  2026-09-22).
- Show the *about to go wrong* moment, not a triumphant one. The genre's promise is failure.
- Strong silhouette, high contrast, no small text.

Budget real money for this. It is cheaper than any other marketing line item and it gates all of them.

### Short description

One sentence, and it must contain the mechanic. Carry The Glass: two workers carrying a fragile pane.
Chained Together: players chained together, climbing. Neither needs a second sentence.

Write Mixtrol's in the same shape: *who*, *what they are carrying*, *what will go wrong*. If it takes two
sentences, the mechanic is not simple enough (see the zero-explanation test in
`coop-mechanics-playbook.md`). *Decided 2026-09-22:* it leads with the swap — *"Your jump is on their
keyboard"* ("Zıplaman onun klavyesinde") — and the cauldron comes second.

## Demo

A demo opens two marketing channels that are otherwise closed: **streamers and festivals**. Zukowski's
data puts the median wishlist yield at roughly **1,500 from a streamer** and **~750 from a festival** —
streamers being the stronger channel of the two.

For this genre specifically the demo is worth more than usual, because the pitch is a social experience
that cannot be conveyed by a trailer. A viewer needs to see their own friend group in the failure.

Demo content: **one complete segment with a full beat arc and one spectacular failure state.** Not a
tutorial, not a slice of the first biome. The demo's job is to produce a clip on the first play.

## Streamer outreach

Three things from the research shape the approach:

1. **Creators follow social proof.** They watch whether other creators did well with a game before picking
   it up; one YouTuber's success pulls in the next. This means the first few placements are worth
   disproportionately more than the next fifty, and it means outreach is a sequence, not a blast.
2. **The 1,000–10,000 concurrent-viewer band is the target.** Streamers watch viewer counts for a game and
   favour that range — big enough that browsers will find them, small enough that they are not competing
   with everyone. Getting a game into that band is what makes mid-size streamers pick it up on their own.
3. **Do not hold back on contacting creators.** There is no advantage to waiting for polish that the
   creator will not notice.

Sequence:

- **Pre-launch, with the demo.** Small and mid creators first, in volume. Do not start at the top.
- **Turkish and regional creators are a real, under-used channel.** Pico Park's spread ran bilibili →
  Western streamers → PewDiePie; it did not start in the West. A concentrated wave in one language
  community produces the viewer-count spike that makes the game visible to everyone else.
- **Launch week is the whole game.** Give keys freely, in fours — a creator needs three friends to play
  this, and a single key is a key that does not get used.
- **Never ask for coverage as a favour.** Send the capsule, a 20-second clip, and four keys.

## The clip pipeline

The product *is* the marketing in this genre, but only if the clips actually get made. Start this before
launch, not after:

- Instrument playtests so every session is recorded. Your own playtests are your first clip library, and
  they are free.
- Post short-form from the earliest playable build. TikTok/Shorts/Reels vertical crops of failure moments.
  A clip that reads at thumbnail size is the same asset as a capsule that reads at thumbnail size — if one
  works, the other will.
- **The muted-clip test from `coop-mechanics-playbook.md` is a marketing test as much as a design test.**
  A mechanic that fails it cannot be marketed on the platforms that sell this genre.

## Steam algorithm: what is true and what is folklore

Getting this wrong causes teams to make bad launch decisions, so it is worth stating plainly:

**True:**
- Steam boosts visibility on sudden spikes in wishlists or revenue, **regardless of when they happen**.
- Launch-specific widgets — Popular Upcoming, New & Trending — are a one-time window. Weak initial
  performance removes a game from them permanently.
- A review score below ~40 % triggers a real visibility penalty.

**Folklore:**
- That there is a wishlist threshold you must hit by a certain date or be buried. There is not.
- That specific revenue milestones ($50 K, $150 K) unlock visibility tiers.
- That "Mixed" reviews reduce visibility. Only below ~40 % does.
- That a missing trailer or a slow launch is algorithmically penalised.

**What this means:** the critical work is all pre-launch and all human. Player perception at launch
largely seals a game's fate — after launch, the concrete has set. Spend the effort on the capsule, the
demo, and the creator sequence, not on gaming an algorithm that mostly is not there.

## Targets to set before launch

These are not predictions, they are the numbers to decide on and then measure against. Fill them in and
date them.

| Metric | Set a target | Reference point |
|---|---|---|
| Wishlists at launch | — | 10,000 is the commonly cited floor for a healthy conversion |
| Units, first 24 h | — | PEAK did 100 K; that is an outlier, not a plan |
| Reviews, first week | — | The review icon appears at 10 reviews |
| Review score | — | Stay well clear of 40 %; the comparables sit at 76–90 % |
| Creator placements, launch week | — | Sequence small → mid → large |
| Peak concurrent viewers | — | Target the 1,000–10,000 band |

## The production lesson worth stealing

PEAK: seven people, under $200 K, roughly one month of in-person work, a fixed launch target they refused
to move, and a commitment to ship whatever was done at the end of the month. Announcement to release was
**five days**. They broke even within hours.

Two transferable pieces:

1. **A fixed date with variable scope beats a fixed scope with a variable date.** It is what kept the
   design from sprawling past the single mechanic that made it funny.
2. **Text is a bad medium for design direction.** Their words. The month in one room is what made the
   design converge. If Mixtrol's co-op pivot is being decided asynchronously, that is a risk worth naming.

## Sources

- [Steam Vs People Algorithms — How To Market A Game](https://howtomarketagame.com/2025/01/20/steam-vs-people-algorithms/) — algorithm truths and folklore
- [How do you get streamers to cover your game? Get a better capsule. — How To Market A Game](https://howtomarketagame.com/2022/07/18/how-do-you-get-streamers-to-cover-your-game-get-a-better-capsule/) — capsule leverage, the 1,000–10,000 viewer band
- [10 Reasons why you shouldn't delay contacting content creators — How To Market A Game](https://howtomarketagame.com/2025/09/16/10-reasons-why-you-shouldnt-hold-back-on-contacting-content-creators/) — social proof between creators
- [Why game demos are key to opening two main marketing doors — Game World Observer](https://gameworldobserver.com/2023/03/10/game-demos-increase-visibility-on-steam) — ~1,500 vs ~750 median wishlists
- [How co-op climbing hit Peak achieved 2 million sales for less than $200,000 — Game Developer](https://www.gamedeveloper.com/production/how-co-op-climbing-hit-peak-achieved-2-million-sales-for-less-than-200-000-) — budget, timeline, pricing, launch discount, "text is evil"
- [Carry The Glass — Steam](https://store.steampowered.com/app/3263320/Carry_The_Glass/) — price, tags, co-op feature matrix
- [Steam Remote Play Together — SteamDB](https://steamdb.info/blog/steam-remote-play-together/) — host-only ownership, sale events
- [PICO PARK sales exceed 1 million units — AUTOMATON WEST](https://automaton-media.com/en/news/20211011-3784/) — the bilibili → West spread
- [Chained Together — GamesRadar+](https://www.gamesradar.com/games/co-op/10000-reviews-90-positive-on-steam-and-only-dollar5-viral-hit-chained-together-uses-the-power-of-co-op-to-ruin-up-to-four-friendships-at-once/) — price and review position
