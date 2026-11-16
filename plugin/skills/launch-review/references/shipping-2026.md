# Shipping in 2026: store rules that break a build

Checked on 2026-11-09 against the Google Play, Apple, Unity 6000.6 and itch.io documentation. These rules change
every year; recheck the dates before a release.

## Google Play

1. **Target API 36.** New apps and updates must target Android 16 (API 36) since 31 Aug 2026 (the extension ended
   1 Nov 2026). `ProjectSetup` raises `targetSdkVersion` to 36; Unity 6000.6 can target up to 37, ProjectSetup only enforces the minimum. The
   requirement moves every August.
2. **AAB, signed with your upload key.** New apps must ship an Android App Bundle. Use **GameKit > Build > Android (AAB, Google
   Play)** or `build aab`. Set the keystore in **Player Settings > Publishing Settings**; keep the `.keystore` and its
   passwords out of git (`.gitignore` covers `*.keystore`, `*.jks`) and backed up. `build.log` warns when the bundle
   is debug-signed. Raise **Bundle Version Code** for every upload; `build.log` prints the one used.
3. **16 KB memory pages.** Apps targeting API 35+ must support 16 KB pages; from 1 Feb 2027 an update without it
   cannot be released. Unity 6 itself is aligned. The risk is a third-party `.so` (ads, analytics, networking SDK):
   Unity warns about a 4 KB-aligned plug-in during the build, and `build.log` keeps that warning. Check a build with
   `zipalign -c -P 16 -v 4 <game>.apk`, or `bundletool dump config --bundle=<game>.aab | grep alignment`
   (expects `PAGE_ALIGNMENT_16K`). On a Pixel 8 or newer, the developer option "Boot with 16KB page size" makes
   `adb shell getconf PAGE_SIZE` return 16384.
4. **Orientation on tablets.** With target API 36, Android 16 ignores the orientation lock on screens 600 dp and wider
   (tablets, open foldables) unless the app category is Game. `ProjectSetup` sets `appCategory = "game"`; test a
   portrait game on a tablet emulator.
5. **Back gesture.** With target API 36 on Android 16, `KEYCODE_BACK` is no longer dispatched; Unity's
   `PlayerSettings.Android.predictiveBackSupport` switches to `OnBackInvokedCallback`. Whether the back gesture still
   arrives as `Keyboard.current.escapeKey` is **unverified**: on an Android 16 phone, test a pause menu bound to Escape
   with `predictiveBackSupport` off and on, then write the working value into `ProjectSetup`. Input-side handling and
   the manifest fallback: `platform-targets`, App lifecycle.
6. **Size.** The base module may be 500 MB compressed; above 200 MB Play only shows a mobile-data warning. Play Asset
   Delivery (`PlayerSettings.Android.splitApplicationBinary`) is needed only past 500 MB.

## App Store

1. **Xcode 26.** Uploads must be built with Xcode 26 and the iOS 26 SDK since 28 Apr 2026; the minimum deployment
   target is iOS 13 since 9 Sep 2026. Build the Xcode project from **GameKit > Build > iOS (Xcode project)** on a Mac.
2. **Privacy manifest.** Unity declares its own required-reason APIs (file timestamps, `PlayerPrefs` user defaults,
   boot time, disk space). The game needs `Assets/Plugins/PrivacyInfo.xcprivacy` only when its own C# calls
   `File.GetLastWriteTime`, `FileInfo.LastWriteTime`, `CreationTime`, `LastAccessTime` and the like (a save system that
   compares file dates), or adds native code. Third-party SDKs ship their own manifest.
3. **Age rating.** The new age-rating questions in App Store Connect must be answered (since 31 Jan 2026).
4. **Tracking.** App Tracking Transparency is needed only when an ads or attribution SDK tracks the player.

## Phones in general

- **Frame rate.** Android and iOS run at a fixed 30 fps unless `Application.targetFrameRate` is set; `AppStartup`
  sets 60. A target that does not divide the refresh rate rounds down (50 on a 120 Hz panel gives 40). For 90/120 Hz,
  offer it as a battery-costly option: `Application.targetFrameRate = (int)Screen.currentResolution.refreshRateRatio.value;`,
  and on iOS enable ProMotion in Player Settings (off by default, so iPhones run at 60 Hz).
- **Screen sleep.** Phones dim and lock after the system timeout when nobody touches the screen. A game with tilt,
  gamepad or idle play sets `Screen.sleepTimeout = SleepTimeout.NeverSleep` when play starts and
  `SleepTimeout.SystemSetting` in menus and on pause.
- **Heat.** Adaptive Performance is a built-in module since Unity 6.3. Enable it only for a game that throttles in
  long sessions: **Project Settings > Adaptive Performance**, one provider per platform (Android, Apple).
- **Ratings and notifications.** The `mobile-store` pack: the native rating prompt after a win, local notifications
  with inexact scheduling and the Android 13 permission asked after the player has seen value.

## WebGL on itch.io

- A release WebGL build (ProjectSetup writes the setting once; `BuildMenu` dev builds are uncompressed) ships
  Brotli-compressed files with no JavaScript decompressor: itch.io serves `.br` files with
  `Content-Encoding: br` over HTTPS. A host that does not set that header needs `decompressionFallback = true`.
- WebGL2 stays the default graphics API. WebGPU is supported in Unity 6.6 but opt-in; add it only with WebGL2 kept as
  the fallback (`PlayerSettings.SetGraphicsAPIs(BuildTarget.WebGL, ...)`) and test Safari and Firefox.
- Push a build with butler (itch.io's CLI): `butler push Builds/WebGL <user>/<game>:html5 --userversion 0.3`. The
  `ci-github` pack does it on every `v*` tag when the `ITCH_GAME` variable (`user/game`) and the `BUTLER_API_KEY`
  secret are set; with `ITCH_GAME` empty the step is skipped and CI still passes green. Every job also needs the
  `GAMEKIT_TOKEN` secret (a fine-grained PAT, Contents read-only on `unity-game-template`); the pack README's table
  lists them all. After the first push, mark the html5 channel "Playable in browser" on the
  game's edit page once.

## Steam

The `steam` pack adds Steamworks.NET and a bootstrap; `go-to-market.md` covers the store page and wishlists.
