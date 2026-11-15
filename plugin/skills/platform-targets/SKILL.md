---
name: platform-targets
description: Use when adding input, gamepad or remapping, UI scaling, safe area or orientation, a settings option, a build, or anything that may differ on a phone or browser. PC, mobile, WebGL from one project - Pointer input, quality tiers, lifecycle.
---

# PC and mobile from one project

One codebase, one set of rules. The platform shows up in three places only: how input becomes the simulation's
`Input` struct, how the UI is laid out, and which quality tier renders it.

## Input

- Read input through the Input System only (the old `UnityEngine.Input` manager is switched off).
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
- Every menu works without a pointer: set the `EventSystem`'s first selected object (or call
  `EventSystem.current.SetSelectedGameObject` when a screen opens), use explicit `Navigation` on its selectables, and
  show which one is selected. Re-select when a pointer user switches back to the pad.
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
  the gameplay camera's `Camera.rect` letterboxed to the reference aspect (a full-screen background or a solid-colour
  camera behind it fills the bars), and the HUD canvas in **Screen Space - Camera** on that camera, so it scales to the
  play column with the same Match as on the phone instead of stretching across the window. Otherwise the camera shows
  far more width than on a phone, which changes framing and difficulty. A landscape-locked game does the same on a
  portrait or ultra-wide window.
- Every interactive element sits under a full-stretch child with `SafeAreaFitter` (GameKit), so notches, camera cut-outs
  and the home indicator never cover a button. Backgrounds stay outside it, full-bleed.
- Touch targets at least ~48 dp (about 130 px at the 1080 reference); keep the bottom third for the thumbs on phones.
- Test aspects, not devices: the Game view's Device Simulator covers notch, safe area and dpi. Check a tall phone
  (19.5:9), a tablet (4:3), and the PC window resized freely.
- No hover-only information: a phone has no hover.

## Orientation and window

CLAUDE.md names the phone orientation. Lock it in Player Settings (`defaultInterfaceOrientation`), not at runtime.
`ProjectSetup` does not set the PC window, so Unity's default (full-screen window, not resizable) stays until you set
it: `PlayerSettings.fullScreenMode = FullScreenMode.Windowed`, `resizableWindow = true`, and
`defaultScreenWidth`/`defaultScreenHeight` in the game's orientation (for example 540x960 portrait, 1280x720
landscape). Layout must then follow `Screen.width`/`height` changes (the Canvas Scaler and `SafeAreaFitter` already
do).

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
- Pause the game on focus loss on both targets.
- Android back button arrives as `Keyboard.current.escapeKey`: treat it like Esc (back / pause menu). On Android 16
  the back gesture may not arrive as `Keyboard.current.escapeKey`; test back navigation on a phone before relying on it.
- Never `Application.Quit()` on iOS; hide the quit button there.
- WebGL: closing the tab raises neither `OnApplicationPause` nor `OnApplicationQuit` reliably. Save at checkpoints and
  on `OnApplicationFocus(false)`, and call `PlayerPrefs.Save()` explicitly after writing. WebGL has no quit either, so
  the quit button is hidden on iOS and WebGL alike (`ui-ugui` screen stack rule).

## Building

**GameKit > Build > Windows / Android / iOS / WebGL**, or `gk-bridge build windows|android|aab|ios|webgl [dev]` in a
background Bash call (it prints the head of `Logs/agent/build.log`; exit 0 is the only pass). A build switches platforms
and reimports, which takes minutes: ask before starting one.

- Android needs the Android Build Support module (with OpenJDK and SDK/NDK) in Unity Hub; `BuildMenu` reports when it is
  missing. IL2CPP, ARM64 only. Store releases need a keystore, which is the user's to create and keep out of git.
- iOS produces an Xcode project in `Builds/iOS`; it is signed and built on a Mac. Without a Mac, a macOS CI runner
  (GitHub `macos-latest` with an App Store Connect API key, for example through fastlane) or Unity Build Automation
  builds, signs and uploads it to TestFlight (`launch-review`, `references/release-build.md`). If the game's own code
  calls a required-reason API (for example `File.GetLastWriteTime` on a save), it needs
  `Assets/Plugins/PrivacyInfo.xcprivacy`, or App Store Connect rejects the upload.
- `ProjectSetup` writes the itch.io size settings once, on a fresh project (Brotli with `decompressionFallback` off,
  which itch.io serves; the Responsive template; high managed stripping; URP post-processing variant stripping for
  every target), and a game may change them. `BuildMenu` sets disk-size LTO on each release WebGL build;
  `build webgl dev` builds uncompressed with the fastest code optimization, so it loads from any local static server.
  The web target is WebGL 2.
- Test a WebGL build over http(s), never by double-clicking `index.html`: from `file://` the browser blocks its
  requests, and Brotli without the fallback also needs a server that sends `Content-Encoding: br`. An itch.io draft
  page is the simplest real check.
- A headless shot exists on every Windows machine: `& "${env:ProgramFiles(x86)}\Microsoft\Edge\Application\msedge.exe" --headless --screenshot=<png> --window-size=1280,720 <url>`
  (msedge is not on PATH).
  Headless often falls back to software WebGL, which is often many times slower than the GPU, so a shot needs the GPU
  or a cheap scene. No script ships for this; write one only when a second WebGL check needs it.

## Platform code

`#if UNITY_ANDROID || UNITY_IOS` only for a real platform API (haptics settings, store review, notch-specific fixes),
inside Game, kept to one small file per concern. Rules and tuning never branch on the platform; a value that differs
per platform is a tuning field.

`gk-bridge refresh` compiles the Editor's platform only, so it never sees that code. Type-check it with
`gk-bridge compile android` / `gk-bridge compile ios` (`Logs/agent/compile-player.log`); no build or platform switch is
needed for that.
