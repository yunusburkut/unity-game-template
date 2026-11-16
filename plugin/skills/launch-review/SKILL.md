---
name: launch-review
description: Use when writing patch notes, shipping a hotfix, preparing a release build or upload, making store screenshots or capsule art, planning price, tags, demo, soft launch or wishlists (Steam, Play, App Store, itch.io).
---

# Auditing the launch

The plan lives in `docs/go-to-market.md` in the game repo, if it exists. If it does not and the user
wants a plan rather than a one-off answer, create it with the headings in *The doc* below, mark
every number *to be verified* until a source with a date backs it, and ask the user for the
decisions only they can make (price, model, platforms first). `DESIGN.md` holds the pitch and the
genre; read it first. This skill is the audit pass; `launch-auditor` runs it in its own context.

**Store facts change.** Fees, review rules, festival dates, tag lists and visibility behaviour move
every year. Everything in this file marked *(verify)* must be checked against the store's own
documentation or a dated source before it is quoted to the user as current. Claims with no source
are folklore until proven.

## First decision: which store leads

A PC + mobile game rarely launches everywhere at once. Pick the lead from the genre, not the
convenience:

| Genre signal | Lead with | Why |
|---|---|---|
| Session-based, co-op, streamable, "watch a friend fail" | Steam | Streamers and festivals are the discovery channels, and they live on PC |
| Short sessions, one-thumb input, puzzle, idle, casual | Google Play + App Store | Discovery is store search, featuring and paid UA; a PC release is a port |
| Hard to tell yet | itch.io WebGL playtest first | Cheapest way to learn whether strangers finish the first minute |

The other platforms follow once the lead has data. A simultaneous launch splits a small team's
marketing in half.

## Price and business model

- **Premium on Steam:** price is a virality parameter as much as a revenue one, above all for
  group-play games, where one buyer brings friends who must each buy. Compare three to five live
  comparables in the same genre and session length; their price, launch discount and review count
  are the reference, not a rule of thumb. Never free on Steam unless it is a free-to-play design.
- **Mobile:** the realistic models are free with ads, free with IAP (and an ad-removal IAP), or
  premium with no ads. Premium on mobile limits reach; free with interstitials every round kills
  retention. Rewarded ads (the player chooses) are the least hostile. Decide the model before the
  core loop is final: it changes the session shape.
- **Store fees** *(verify)*: Steam's standard revenue share; Google Play and the App Store reduced
  rates for small developers and subscriptions. Quote only after checking the current terms.
- **Cross-buy and parity:** a premium PC version and a free mobile version can coexist; say which
  content each has, so reviews on one do not complain about the other.

## Steam

**Tags** — derived from the live tag sets of the closest comparables; order matters. Lead with the
tags that describe the *experience* the buyer wants (`Co-op`, `Funny`, `Relaxing`, `Difficult`),
then the genre. A technically accurate tag that puts the game on the wrong shelf (next to games its
buyers do not want) costs more than it gains. Do not claim a feature tag (`Local Co-Op`, `Controller`)
the release build does not deliver.

**Capsule** — the highest-leverage asset and the most under-budgeted. Creators decide coverage
partly on it, because a capsule that works is a thumbnail that works. Check:

- Readable at the small capsule size (462×174 px since Steam's late-2024 asset update; header 920×430, main
  1232×706, vertical 748×896 *(verify in Steamworks' current graphical asset rules)*), not at the size it was designed.
- **The core mechanic is visible**, physically, in one image.
- It shows the moment the game is *about* (the near-miss, the chaos, the satisfying clear), not a
  logo on a background.
- Strong silhouette, high contrast, no small text.

**Short description** — one sentence containing the mechanic: who, does what, what goes wrong or
what feels good. If it needs two sentences, the mechanic is not simple enough yet.

**Demo** — opens the two channels that are otherwise closed: **creators and festivals** (Next Fest
*(verify dates and eligibility rules)*). Demo scope: one complete, polished slice that produces its
best moment in the first ten minutes. Not a tutorial, not "the first 20 % of the game".

**Algorithm: true vs folklore** *(verify against the dated sources in `docs/go-to-market.md`)*

- Usually true: Steam responds to sudden wishlist or revenue spikes whenever they occur; Popular
  Upcoming and New & Trending are a one-time window around launch; a very low review score carries
  a real visibility penalty.
- Usually folklore: a wishlist threshold you must hit by a date or be buried; revenue milestones
  unlocking visibility tiers; "Mixed" reviews alone killing visibility; missing trailers being
  algorithmically penalised.

So the critical work is pre-launch and human: capsule, demo, creator sequence.

## Google Play and the App Store

**Listing (ASO):**

- **Icon** is the capsule of mobile: readable at the smallest grid size, one object or face, no
  text, distinct from the top results for the main keyword. Test two or three variants (Play's
  store listing experiments; App Store product page optimization *(verify)*).
- **Screenshots**: the first two do the selling — gameplay with a one-line caption each, portrait
  if the game is portrait. Real gameplay, not mock-ups; both stores reject misleading media.
  Sizes *(verify each on the store's upload page)*: App Store iPhone 6.9" 1320×2868 (landscape 2868×1320), and iPad
  13" 2064×2752 when iPad is supported; Google Play 1080×1920 or 1920×1080 (each side 320–3840 px, long side at most
  twice the short); Steam 1920×1080 (16:9, at least five). To capture: add the size as a Fixed Resolution in the Game
  view's size menu and select it, then `gk-bridge play-capture` (shots are taken at the Game view size, into
  `Logs/agent/capture/`; syntax in `unity-editor-cli`).
- **Title and subtitle / short description** carry the keywords; the keyword field (App Store) and
  long description (Play) carry the rest. Research search terms players actually type for the
  genre; avoid competitor names *(verify each store's metadata rules)*.
- **Preview video**: first three seconds show the core mechanic; most viewers watch muted.

**Soft launch:** release in a few smaller markets first (commonly a mix of a cheap-UA market and an
English-speaking one *(verify current practice)*) to read retention and monetisation before the
global launch. Targets to read, not promise: day-1 / day-7 / day-30 retention, session length,
sessions per day, crash-free rate, ad or IAP conversion. Compare with genre benchmarks from a dated
source.

**Ratings prompt:** use the native in-app review APIs (Play In-App Review, `SKStoreReviewController`
/ `AppStore.requestReview` *(verify)*), never a custom "rate 5 stars" dialog. Ask after a win or a
completed session, never after a loss or on first launch. The OS limits how often the prompt shows.
With the mobile-store pack, call `__GAME__.Store.StoreReview.Prepare(host)` when the level starts and
`StoreReview.Request(host)` at the win (`host` a DontDestroyOnLoad object) instead of writing a new wrapper.

**Review-guideline pitfalls** *(verify against the current App Store Review Guidelines and Google
Play Developer Policy before a submission)*:

- A quit button on iOS (do not ship one), placeholder content, broken links, crashes on launch.
- Ads: interstitials that cannot be closed, ads on the first launch, ads aimed at children without
  the families programme rules.
- Loot boxes must disclose odds; IAP must go through the store's billing for digital goods.
- Privacy: a privacy policy URL, the App Privacy / Data safety forms filled honestly, the iOS
  tracking (ATT) prompt only if the game or an SDK tracks across apps.
- Consent: players in the EEA, UK and Switzerland get a consent form from a Google-certified CMP (Google UMP or the
  mediation SDK's own consent flow) before the first ad request and before personalised ads or analytics start; the
  consent state goes to the ad SDK and to `AnalyticsService.Instance.StartDataCollection()` *(verify current terms)*.
- Restore purchases: non-consumables and subscriptions need a visible Restore Purchases button on iOS, or App Review
  rejects the build; Android restores them on reinstall through the store's purchase query.
- Age ratings questionnaire answered for every store.
- Target API level (Android) and minimum SDK requirements change yearly; the current values and dates (target API,
  16 KB pages, Xcode version, privacy manifest, age rating) are in `references/shipping-2026.md`.

**Device reality:** the store page promises the frame rate and battery behaviour of the weakest
supported device (`platform-targets`, `refactor-pass` low-end reference). A one-star "my phone gets
hot" review costs more than a missing feature.

## itch.io playtests

- WebGL build from `GameKit > Build > WebGL`: a release build (build.log says `development no`; the Development
  Build box in File > Build Profiles is off) gets the itch.io size pass and Brotli, a development build neither. Set the
  embed size to the game's reference resolution, enable fullscreen, and test the uploaded build on a
  phone browser too. An art-heavy build can pass itch's per-file cap: see the itch.io row in
  `references/release-build.md` before `butler push`.
- A playtest page is a research tool: one question you want answered ("do strangers understand the
  mechanic without text?"), a feedback link, and a short devlog. Restricted / password pages keep it
  off search until it is ready.
- Record the sessions you watch; they are the first clip library.

## Creator outreach and clips (all platforms)

- **Creators follow social proof.** One success pulls in the next, so outreach is a sequence, not
  a blast: small and mid-size creators first, in volume, with the demo or playtest build.
- **Do not wait for polish** creators will not notice. Contact when the best moment is reliable.
- **Regional and Turkish-language creators** are a real, under-used channel; a concentrated wave in
  one language community can produce the spike that makes the game visible elsewhere.
- **Give keys in sets** for multiplayer games — one per seat.
- **Clip pipeline:** record every playtest, post vertical short-form from the earliest playable
  build, and apply the muted-clip test: if the moment does not read with the sound off in three
  seconds, it cannot be marketed on the platforms where short clips sell games.

## Targets to set (not predictions)

| Metric | Where | Reference point |
|---|---|---|
| Wishlists at launch | Steam | A commonly cited floor exists *(verify the current figure and its source)* |
| Reviews, first week | Steam | The review score appears after a minimum count *(verify)* |
| Review score | Steam | Stay clear of the low band; comparables' scores are the bar |
| Day-1 / day-7 retention | Mobile | Genre benchmark from a dated source |
| Store rating | Mobile | Keep above ~4.0; prompt only happy players |
| Crash-free sessions | All | Close to 100 %; one launch crash on a popular device is a launch-killer |
| Creator placements, launch week | All | Sequenced small → mid → large |

## Shipping a build

Before a store upload or a public itch.io page, run `references/release-build.md`: version and tag, a release (not
development) build, the code and secrets scan, asset licences from `docs/asset-sources.md` (and Steam's AI-content
disclosure), smoke on the built player, the per-store rows, release day, patch notes, and patching a shipped build
(main only, the next PATCH tag). Its verdict is HAZIR, BELİRSİZ or HAZIR DEĞİL; a row nobody could check is `[?]`
and makes it BELİRSİZ, never HAZIR.

`launch-auditor` cannot run git, ask the user or size a file, so the main session collects these first and passes
them in the brief; without them those rows come back `[?]`:

1. The previous tag: `git describe --tags --abbrev=0 v<this>^` once the build commit carries its tag (on an untagged
   build commit, `git describe --tags --abbrev=0 HEAD`). Then `git log --format="%h %s" <prevTag>..v<this>` (or
   `<prevTag>..HEAD` before tagging), with `<prevTag>` exactly as git printed it (`v0.2.0`, no extra `v`).
2. The user's answer to "Bu build'i bu oturumda açtın mı?" and, if yes, their result for each smoke row.
3. For a WebGL upload, the size on disk of `Builds/WebGL/Build/*.data.br`.

## Production lesson

**A fixed date with variable scope beats a fixed scope with a variable date.** It keeps the design
from sprawling past the one mechanic that made the game work. Name the date in `DESIGN.md`.

## The doc

`docs/go-to-market.md`, created on first use, with these headings: Pitch (one sentence) ·
Comparables (name, price/model, tags, review count, source + date) · Lead platform and order ·
Price and model · Store assets checklist (per store) · Demo / playtest scope · Creator plan ·
Clip pipeline · Targets · Store facts checked (claim, source, date) · Open questions.
