---
name: platform-targets
description: Use when adding input, UI scaling, safe area, orientation, a setting or a build, or it differs on phone or browser ("telefonda", "mobilde çalışmıyor", "build al", "çentik"). PC, mobile, WebGL: Pointer input, gamepad, quality tiers, lifecycle.
---

# PC and mobile from one project

One codebase, one set of rules. The platform shows up in three places only: how input becomes the simulation's
`Input` struct, how the UI is laid out, and which quality tier renders it.

## Input

- Read input through the Input System only (the old `UnityEngine.Input` manager is switched off).
- One actions asset per game: `Assets/<Game>/Settings/<Game>Controls.inputactions`, created by the first input feature
  and assigned as the project-wide actions (Project Settings > Input System Package, so `InputSystem.actions` returns it
  and it is enabled at startup). Pointer, key and gamepad bindings all live in it; gameplay references its actions
  (`InputActionReference` or `InputSystem.actions.FindAction`), never a second ad hoc asset.
- Anything you tap is a **pointer** action: bind to `<Pointer>/press` and `<Pointer>/position`, which covers mouse,
  touch and pen. Never read `Mouse.current` or `Touchscreen.current` for gameplay; that is the most common "works on
  PC, dead on the phone" bug.
- Keys are a PC extra layered on top (shortcuts, Esc for pause), never the only way to do something.
- Multi-touch gestures (pinch, two-finger drag) use `EnhancedTouch` and need a mouse fallback (scroll wheel, right
  drag) on PC.
- Drag thresholds and tap radii in physical units: scale pixel values by `Screen.dpi / 160f` (fall back to 1 when dpi
  is 0), or a tap on a phone reads as a drag.
- UI needs an `EventSystem` with `InputSystemUIInputModule`, not `StandaloneInputModule`.

### Gamepad and remapping (when CLAUDE.md puts a gamepad in scope)

- Every action gets a `<Gamepad>` binding in the same `.inputactions` asset, next to its pointer and key bindings;
  gameplay code still reads only the action, never `Gamepad.current`.
- Every menu works without a pointer: explicit `Navigation` on its selectables and a visible Selected state. Which
  button is selected on open, and re-selection after a switch back from mouse or touch, follow `ui-ugui` (Screens >
  Navigation): selected only when the last input was keyboard or gamepad, never through the EventSystem's First
  Selected.
- Button glyphs follow the last used device: `PlayerInput.onControlsChanged` / `currentControlScheme`, or
  `InputUser.onChange` without a `PlayerInput`. Never hard-code keyboard glyphs in a game that claims controller
  support (Steam Deck checks this).
- Remapping goes through `InputActionRebindingExtensions.PerformInteractiveRebinding` (disable the action while it
  runs, exclude `<Mouse>/position` and similar noise, offer cancel), and the overrides are stored with
  `SaveBindingOverridesAsJson` in the settings save and restored with `LoadBindingOverridesFromJson` at startup.

## UI (uGUI)

- Canvas Scaler: **Scale With Screen Size**, a reference resolution in the game's main orientation (1080x1920 portrait
  or 1920x1080 landscape), Match 0.5 as a start.
- A portrait-locked game on a landscape PC window or WebGL page keeps the phone aspect: a portrait default window size,
  and the gameplay camera's `Camera.rect` capped at the widest aspect the game is designed for. The cap is one-way:
  pillarbox only when `Screen.width / Screen.height` is wider than the cap (9:16 for the 1080x1920 reference, so
  tablets get thin side bars; raise it to 3:4 only if the layout is built to show that extra width). A taller screen,
  such as a 19.5:9 phone, keeps the full screen with no bars and shows more height, with the camera framed so the
  play width fits. Recompute the rect when the window size changes, since PC and WebGL windows resize. A full-screen
  background or a solid-colour camera behind it fills the bars. Otherwise the camera shows far more width than on a
  phone, which changes framing and difficulty. A landscape-locked game does the same mirrored: it caps the height on
  a portrait or near-square window, and an ultra-wide window gets side bars only past the widest aspect it supports.
- The HUD goes on its own **UI camera**: an Overlay camera in the gameplay camera's stack that culls only the UI
  layer, with post-processing off, and the HUD canvas in **Screen Space - Camera** on it. The gameplay camera stops
  rendering the UI layer. URP gives Overlay cameras the base camera's viewport, so the HUD follows the letterbox and
  scales to the play column with the same Match as on the phone, and URP applies the stack's post-processing before
  the UI camera draws, so Bloom, tonemapping, colour grading and vignette never touch the HUD. A canvas on the
  gameplay camera itself is drawn inside that camera's pass and takes all of its post-processing. Use the same setup
  on every target, so the phone and the PC show the same HUD.
- Every interactive element sits under a full-stretch child with `SafeAreaFitter` (GameKit), so notches, camera cut-outs
  and the home indicator never cover a button. Backgrounds stay outside it, full-bleed. Ceiling: it normalises
  `Screen.safeArea` by the full screen, not by the capped `Camera.rect`, so in a letterboxed HUD whose bars hold the
  notch (a landscape game capped at 16:9 on a 20:9 phone) the HUD is still pushed in by the inset. Safe, only wasted
  space; the way up is intersecting the safe area with the UI camera's `pixelRect` before normalising.
- Touch targets at least ~48 dp (about 130 px at the 1080 reference); keep the bottom third for the thumbs on phones.
- Test aspects, not devices: the Game view's Device Simulator covers notch, safe area and dpi. Check a tall phone
  (19.5:9), a tablet (4:3), and the PC window resized freely.
- No hover-only information: a phone has no hover.

## Orientation and window

CLAUDE.md names the phone orientation. Lock it in Player Settings (`defaultInterfaceOrientation`), not at runtime.
The PC window depends on the game's GameKit version (the `#gamekit-vX.Y.Z` tag in `Packages/manifest.json`):

- GameKit 0.1.2 or later: `ProjectSetup` writes the window once, on a fresh project:
  `PlayerSettings.fullScreenMode = FullScreenMode.Windowed`, `resizableWindow = true`, and
  `defaultScreenWidth`/`defaultScreenHeight` from the orientation set at that moment. CLAUDE.md usually names the
  orientation later, so the window starts as 1280x720 landscape. When you lock portrait, set 540x960 in the same change
  (and 1280x720 if you lock landscape on a project that started portrait). Do not re-apply the other two settings.
- Older GameKit: Unity's default (full-screen window, not resizable) stays until you set all three by hand, as above,
  in the game's orientation (540x960 portrait, 1280x720 landscape).

Layout must then follow `Screen.width`/`height` changes (the Canvas Scaler and `SafeAreaFitter` already do).

## Quality tiers and frame rate

- Two quality levels: **Mobile** (0, phones and WebGL) and **PC** (1), each with its own URP asset in
  `Assets/<Game>/Settings`. `ProjectSetup` creates them; tune those assets, add a third tier there if needed.
- Phones run at `Application.targetFrameRate = 60` (`AppStartup`); PC uses vSync. A battery-saver option can drop to
  30 on phones.
- Per-platform texture overrides in the importer (max size, ASTC on mobile) beat runtime branches (rules: unity-performance
  Asset audit).

## App lifecycle

- `OnApplicationPause(true)` is the last reliable moment on a phone: save there, not in `OnApplicationQuit` (iOS
  rarely calls it, Android kills the process).
- Pause the game on focus loss on both targets, except during an online co-op session, which keeps running
  (coop-multiplayer's networking.md, Platforms).
- Back is one action in the game's actions asset, bound to `<Keyboard>/escape` and `<Gamepad>/buttonEast`: the Android
  back button arrives as the Escape key, so the same action covers Esc, the pad and the phone (back / pause menu). Code
  reads the action, never `Keyboard.current`; UI cancel goes through `InputSystemUIInputModule`'s Cancel action.
- `ProjectSetup` targets API 36 (Android 16), where predictive back is on by default and the system may stop sending
  the back key event, so the action can stay silent. The switch is Unity's `PlayerSettings.Android.predictiveBackSupport`
  (Player Settings > Android); whether back still arrives as Escape is unverified either way. On an Android 16 phone,
  test the back action with it off and on, keep the value that works, and report it so `ProjectSetup` sets it for every
  game (`launch-review` `references/shipping-2026.md` tracks this). Only if that setting is missing: enable **Custom
  Main Manifest** (Publishing Settings) and add `android:enableOnBackInvokedCallback="false"` to its `<application>`
  element, then build and test again.
- Never `Application.Quit()` on iOS; hide the quit button there.
- WebGL: closing the tab raises neither `OnApplicationPause` nor `OnApplicationQuit` reliably. Save at checkpoints and
  on `OnApplicationFocus(false)`, and call `PlayerPrefs.Save()` explicitly after writing. WebGL has no quit either, so
  the quit button is hidden on iOS and WebGL alike (`ui-ugui` screen stack rule). A save file under
  `Application.persistentDataPath` lives in IndexedDB and survives a reload only because the template's Responsive
  `index.html` sets `autoSyncPersistentDataPath: true` in its loader config; a custom WebGL template must keep that
  line, or the page must call `JS_FileSystem_Sync()` after each write. Check by saving, reloading the page and loading.

## Building

**GameKit > Build > Windows / Android / iOS / WebGL**, or `gk-bridge build windows|android|aab|ios|webgl [dev]` in a
background Bash call (it prints the head of `Logs/agent/build.log`; exit 0 is the only pass). A build switches platforms
and reimports, which takes minutes: ask before starting one.

- Android needs the Android Build Support module (with OpenJDK and SDK/NDK) in Unity Hub; `BuildMenu` reports when it is
  missing. IL2CPP, ARM64 only. Store releases need a keystore, which is the user's to create and keep out of git.
- To put an Android build on the test phone (USB debugging on, the phone listed by `adb devices`), ask first, then run
  `adb install -r "Builds/Android/<product>.apk"` and launch it with `adb shell monkey -p <bundle id> 1`. In Git Bash,
  prefix the `adb shell` call with `MSYS_NO_PATHCONV=1`, as for the FrameLog pull in CLAUDE.md. An `.aab` does not
  install this way; build `android` for the phone.
- iOS produces an Xcode project in `Builds/iOS`; it is signed and built on a Mac. Without a Mac, a macOS CI runner
  (GitHub `macos-latest` with an App Store Connect API key, for example through fastlane) or Unity Build Automation
  builds, signs and uploads it to TestFlight (`launch-review`, `references/release-build.md`). If the game's own code
  calls a required-reason API (for example `File.GetLastWriteTime` on a save), it needs
  `Assets/Plugins/PrivacyInfo.xcprivacy`, or App Store Connect rejects the upload.
- The WebGL size settings are the itch.io set: Brotli with `decompressionFallback` off (itch.io sends the header), the
  Responsive template, high managed stripping, URP post-processing variant stripping, disk-size LTO. The web target is
  WebGL 2. Who sets them depends on the game's GameKit tag (`Packages/manifest.json`):
  - GameKit 0.1.2 or later: `ProjectSetup` writes all but LTO once, on a fresh project, and a game may change them.
    `BuildMenu` sets disk-size LTO on each release WebGL build; `build webgl dev` builds uncompressed with the fastest
    code optimization (then puts the project's compression back), so it loads from any local static server.
  - GameKit 0.1.1 and older: `BuildMenu` forces the whole set on every WebGL build, dev builds included. A change in
    Player Settings (the fallback on for a host without the header, a lower stripping level) is overwritten by the
    next build, and a dev build is still Brotli without the fallback and LTO: slow to build, and it needs a server
    that sends `Content-Encoding: br`. To keep such a change, the game moves to a newer GameKit tag (the user's call).
- Test a WebGL build over http(s), never by double-clicking `index.html`: from `file://` the browser blocks its
  requests, and Brotli without the fallback also needs a server that sends `Content-Encoding: br`. An itch.io draft
  page is the simplest real check.
- A headless shot exists on every Windows machine: `& "${env:ProgramFiles(x86)}\Microsoft\Edge\Application\msedge.exe" --headless --screenshot=<png> --window-size=1280,720 --virtual-time-budget=20000 <url>`
  (msedge is not on PATH). Without the time budget the shot is taken at page load, while the Unity loader is still
  downloading. Open the PNG: a loader or progress bar proves nothing, only the game's first frame passes.
  Headless often falls back to software WebGL, which is often many times slower than the GPU, so a shot needs the GPU
  or a cheap scene. No script ships for this; write one only when a second WebGL check needs it.

## Platform code

`#if UNITY_ANDROID || UNITY_IOS || UNITY_WEBGL` only for a real platform API (haptics settings, store review,
notch-specific fixes, a WebGL `.jslib` call), inside Game, kept to one small file per concern. A `.jslib` import and
the WebGL-only lifecycle code go under `#if UNITY_WEBGL && !UNITY_EDITOR`, since the Editor cannot call into the page.
Rules and tuning never branch on the platform; a value that differs per platform is a tuning field.

`gk-bridge refresh` compiles the Editor's platform only, so it never sees that code. Type-check Android and iOS code
with `gk-bridge compile android` / `gk-bridge compile ios` (`Logs/agent/compile-player.log`, every GameKit release);
no build or platform switch is needed for that. `gk-bridge compile webgl` does the same for WebGL-only code where the
game's GameKit takes it (AgentBridge's usage line lists `compile ios|android|webgl`, 0.1.3 or later). Where it does
not (a usage error from gk-bridge or AgentBridge), WebGL-only code is checked only by `gk-bridge build webgl dev`
(minutes, ask first): keep it in that one small file. With the ci-github pack, CI runs the same compile for Android,
iOS and WebGL on every push (`AgentBridge.CompilePlayerScriptsBatch`, GameKit 0.1.3 or later).
