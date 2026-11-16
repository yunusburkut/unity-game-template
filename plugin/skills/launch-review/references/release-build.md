# The build you upload

Run this before a store upload, before an itch.io page goes public, and before a build goes to strangers. Scope the
rows from `DESIGN.md` Platforms and the lead store in `docs/go-to-market.md`: write only the rows of the stores the game
ships on (Steam, Google Play, App Store, itch.io; no console rows). No store named: write "mağaza belli değil: mağaza
satırları değerlendirilmedi", say what would decide it, and never imply a pass.

Marks: `[x]` with the evidence on the line, `[ ]` work remains, `[?]` could not check (say why). Verdict: any `[ ]` =
**HAZIR DEĞİL**; else any `[?]` = **BELİRSİZ**; else **HAZIR**. BELİRSİZ is never HAZIR.

## Version

- `PlayerSettings.bundleVersion` is `MAJOR.MINOR.PATCH`: PATCH for fixes, MINOR for content or balance, MAJOR for a big
  content drop.
- Android `bundleVersionCode` (the `versionCode` line in build.log) is higher than the last upload; the iOS build number
  (`PlayerSettings.iOS.buildNumber`) too. Both only ever increase.
- The commit that makes the build is tagged `vX.Y.Z` on main (`git tag -a`). A tag is never moved or reused: a second
  build with other changes ships as the next PATCH. The build can be rebuilt from the tag.

## Build

- `gk-bridge build <target>` without `dev` exits 0, and `Logs/agent/build.log` says `development no`. Check the log,
  not the command: the Development Build box in File > Build Profiles makes every entry a development build. FrameLog
  runs only in a development build, so it is off in this one.
- Google Play: `gk-bridge build aab`; no `WARNING debug-signed` line (the keystore passwords are typed again in each
  Editor session); `targetSdk` meets Play's current target API level (36 in 2026, rule 1 of
  [shipping-2026.md](shipping-2026.md); it moves every August).
- Google Play 16 KB pages: no `16 KB` warning line in build.log, and `zipalign -c -P 16 -v 4` on the APK or
  `bundletool dump config` on the AAB shows 16 KB alignment for every `.so` (rule 3 of shipping-2026.md). From 1 Feb
  2027 an update without it cannot be released; the usual culprit is a third-party SDK's native library.
- Google Play tablets: `appCategory` is `game` in Player Settings (ProjectSetup sets it), or Android 16 ignores the
  orientation lock on screens 600 dp and wider; a portrait game is checked on a tablet emulator (rule 4).
- iOS: built with Xcode 26 and the iOS 26 SDK, deployment target iOS 13 or higher (shipping-2026.md, App Store rule 1).
  The Xcode project in `Builds/iOS` is signed for distribution on a Mac. With no Mac (this Windows machine), the
  route is a cloud Mac: with the `ci-github` pack, uncomment its `ios` job and the iOS matrix entry in `ci.yml`
  (archive, cloud-managed signing and TestFlight upload with an App Store Connect API key; the secrets are listed in
  the pack README's table and live in CI, never in the repo; *verify the runner image ships Xcode 26*); without the
  pack, Unity Build Automation. Either way the build reaches TestFlight before review.
- iOS privacy manifest (what Unity and SDKs already declare: App Store rule 2 of shipping-2026.md): search
  `Assets/<Game>` for `File.GetLastWriteTime`, `FileInfo.LastWriteTime`, `CreationTime` and `LastAccessTime`; when
  the game's own C# calls one or adds native code, `Assets/Plugins/PrivacyInfo.xcprivacy` exists and gives a reason
  for each.
- App Store Connect: the age-rating questions are answered, and App Tracking Transparency is present only when an ads
  or attribution SDK tracks the player (App Store rules 3 and 4 of shipping-2026.md, with their dates).
- Note the `size` line. WebGL for itch.io: see the itch.io row below.

## Code and content scan

Scan `Assets/<Game>` (never `Assets/Feel`). State the denominator, "N dosya tarandı, M bulgu"; zero files is `[?]`.

- TODO / FIXME / HACK: the count and each location; one that stays has its reason on the line.
- `Debug.Log` on a hot path outside `#if UNITY_EDITOR || DEVELOPMENT_BUILD`; cheat or debug keys not gated the same way.
- Test values: test ad unit IDs, sandbox or test IAP keys, `localhost`, hard-coded test levels or currency. Test and
  live IDs switch by build type (`Debug.isDebugBuild` or a define), never by hand.
- Secrets: no API key, store secret or keystore password in code, committed config or a ScriptableObject (search
  `api_key`, `secret`, `token`, `password`, `BEGIN PRIVATE KEY`). No `*.keystore`, `*.jks` or `*.p12` in git.
- No asset named `placeholder`, `temp_` or `WIP`, and no test scene in the build list.
- No player-facing text hard-coded in code, if the game is localised.

## Assets and licences

- `docs/asset-sources.md` has a row for every shipped asset that is not ours or that an AI made. A row with an
  unknown licence is `[ ]`.
- Each licence allows a commercial release on this store. Every row with attribution `yes` is on the credits screen,
  and bundled fonts and packages carry their licence notice.
- Steam: the Content Survey's AI-generated content disclosure (pre-generated and live-generated) matches the AI rows.
  Other stores: check their current AI-content policy at release *(verify)*.
- Mobile: privacy policy URL and the Data safety / App Privacy forms (see the review pitfalls in `SKILL.md`).

## State

- PLAN.md Pending Play Mode checks is empty, or the user accepted each check that stays.
- No `[yüksek]` bug in PLAN.md Known issues (crash, data loss, cannot progress, or blocks a build/ship). A
  `review <Base>: ` line carries the review rubric's tag: it counts only when it is one of these.
- A spot where more than half of the playtesters got stuck (DESIGN.md Playtests) is fixed or accepted on a Decisions
  line.
- Crash reporting decided: Play Console's Android vitals and App Store Connect's crash reports come with the store; a
  PC or WebGL build reports nothing unless a crash reporter is added. Say which applies: without one, a launch crash
  is invisible. The options: Unity's Cloud Diagnostics (crash and exception reports, in Unity Cloud) or the Sentry
  Unity SDK (`io.sentry.unity`), in a release build, named in the privacy policy and, where the store or the law asks
  for it, behind the player's consent *(verify current packages and terms)*. "None" is a valid choice only when it is
  on record. For playtests without one, tell testers where the log is: Windows
  `%USERPROFILE%\AppData\LocalLow\<Company>\<Product>\Player.log`; WebGL errors are in the browser console (F12).
- Patch notes for this build exist (below), and the rollback is named (below).

## Smoke on the built player

The user runs this on the built player, not in the Editor. Ask first: "Bu build'i bu oturumda açtın mı?" If not,
every item is `[?]`. A failure becomes a Known issues line with its repro.

- It launches to the first screen with no error, and a new session or level starts.
- Menu and pause respond to the mouse and to touch.
- No crash or hang in 5 minutes of play.
- The mechanic this version changed works, and one older feature still works.
- First launch with no save (clear the app data or PlayerPrefs); save, quit and relaunch restores the state.
- No network (airplane mode), if an SDK calls home; low storage, if the game writes files.
- Suspend and resume mid-level (app switch, phone call) comes back paused.
- Text is readable on the smallest supported phone; no cue is colour only (`player-clarity`).
- PC: windowed and fullscreen; a window resize keeps the layout.
- Mobile: touch only; the orientation lock holds; the back gesture or button behaves (`platform-targets`); no heat
  after 10 minutes. The frame target holds on the weakest phone (FrameLog on F3 or a three-finger tap, in a
  Development Build of the same commit).
- WebGL: it loads from the itch.io page itself (not a local file) in a desktop and a phone browser; fullscreen works.

## Per store, before you press submit

- **Steam:** the depot build installs and runs on a clean machine or account, not the dev machine. Achievements
  unlock in that build (if any). Steam Cloud saves round-trip between two machines (if on). Steam Deck is checked if
  the page claims it: controller glyphs, text readable at 1280x800, no launcher. The page is complete: capsule,
  trailer, description, system requirements.
- **Steam, with the steam pack:** `SteamBootstrap.AppId` and `steam_appid.txt` hold the game's App ID, not `480`
  (Valve's Spacewar test app; with 480 the restart-through-Steam check is skipped). The depot does not ship
  `steam_appid.txt` *(verify Steamworks' current guidance)*. Player Settings > Windows > Scripting Backend is IL2CPP
  (`SteamSetup` sets it on its first run).
- **itch.io Windows, with the steam pack:** that build came from GameKit > Build > Windows (no Steam, itch.io)
  (`packs/steam` README), which adds `DISABLESTEAMWORKS` for that build only; the Standalone Scripting Define Symbols
  do not hold `DISABLESTEAMWORKS`.
- **Google Play:** the AAB from the Build rows; the first release goes to a closed or open testing track first, and
  updates go out as a staged rollout.
- **App Store:** the build number is higher; the first version reaches everyone at once, so turn phased release on
  for updates.
- **itch.io:** an HTML game stays inside itch's limits *(verify, itch.io/docs/creators/html5)*: at most 1,000 files,
  500 MB unpacked, 200 MB for one file, and `index.html` at the top of the upload. `Builds/WebGL/Build/*.data.br` hits
  the per-file cap first: check its size on disk before `butler push`; if it is over, cut texture sizes or move content
  to Addressables. Cover, screenshots, description and tags are filled; age and content tags are honest. One butler
  channel per platform (`html5` is the one the `ci-github` pack pushes; `windows` and `android` are the convention
  for manual pushes), the
  `html5` upload set to play in the browser, and each build tested from the itch.io page.

## Release day

- Download the build from the store and play it on a real device, not the local build.
- The store page shows the right price, text and media.
- Crash reports arrive (or "none" is on record).
- At 24 h and at 72 h, read crash-free sessions, reviews and ratings. Only a decision they lead to (halt the
  rollout, hotfix X) becomes a dated DESIGN.md Decisions line.

## Patch notes

Source: `git log --format="%h %s" <prevTag>..v<this>`, where `<prevTag>` is `git describe --tags --abbrev=0 v<this>^`
exactly as printed (describing `HEAD` on the tagged build returns `v<this>` itself and an empty range). No previous tag: ask for the start ref, never use the whole log.

- Keep `game`, `ui`, `input` and `art` commits, and `core` or `build` commits whose subject changes what the player
  sees. Drop `tools`, `design`, refactors and template syncs. Say "N/M commit kullanıldı"; zero kept: say so, never
  invent.
- Order: the biggest change as the headline, then New, Changes (balance as before -> after from the ScriptableObject
  diff: "jump 4.0 -> 4.5"), Fixes (what the player saw: "Fixed a freeze when opening the shop", never a class name,
  sha or stack-trace word), Known issues (from PLAN.md, in player words).
- A fix or a feature is listed only with a commit on the shipped tag and a Play Mode check the user confirmed. Done
  checks leave PLAN.md, so the record is: the check is no longer in Pending Play Mode checks and its commit is on the
  tag, or a later commit's `Verified:` line or a DESIGN.md Playtests entry names it. A check still pending is not
  confirmed. A claim nobody can check is left out, not softened. Never promise a feature or a date.
- Write in the store listing's language. Google Play's "What's new" takes about 500 characters and the App Store's
  "What's New" about 4,000 *(verify)*: give a short version for those and a long one for a Steam or itch.io devlog.
  Show the draft; the user posts it.

## After release: patching a shipped build

- A hotfix is only for a `[yüksek]` bug (as in State above) on a shipped build or a store-review rejection. An `[orta]` or `[düşük]` bug
  waits for the next version.
- Smallest change: no cleanup, refactor or feature; a data or tuning fix beats a new code path. More than about half
  a day of work is the next version, not a hotfix.
- Main only. If main has no unshipped work since the release tag, fix on main as usual. If it has, finish that work or
  gate it off first.
- Bump the bundleVersion PATCH and the versionCode or build number, then tag `vX.Y.(Z+1)` on main. The commit body
  names the confirmed cause; the patch notes carry the player's line.
- Verify like any bug: the user plays the repro on the new build, then runs the smoke list above.
- Name the rollback before upload *(verify each)*:
  - Steam: set the previous build live on the default branch in Steamworks.
  - itch.io: `butler push` the previous build again to the same channel (`html5` for WebGL).
  - Google Play: a versionCode cannot roll back; for an update, halt the staged rollout and ship a higher versionCode built from the
    previous tag.
  - App Store: no rollback; for an update, pause the phased release and submit a fixed build.
- So keep a copy of the previous release build (the next build overwrites `Builds/`), or its tag to rebuild from,
  until the new one has held for a few days.
