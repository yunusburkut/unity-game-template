---
name: platform-targets
description: Making the game work the same on PC (keyboard + mouse), mobile (touch) and WebGL — Pointer input, uGUI scaling and safe area, orientation, quality tiers, frame rate, app lifecycle (pause, back button), building each target. Use when adding input, any UI, a screen, a settings option, a build, or anything that may differ on a phone.
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

## UI (uGUI)

- Canvas Scaler: **Scale With Screen Size**, a reference resolution in the game's main orientation (1080x1920 portrait
  or 1920x1080 landscape), Match 0.5 as a start.
- Every interactive element sits under a full-stretch child with `SafeAreaFitter` (GameKit), so notches, camera cut-outs
  and the home indicator never cover a button. Backgrounds stay outside it, full-bleed.
- Touch targets at least ~48 dp (about 130 px at the 1080 reference); keep the bottom third for the thumbs on phones.
- Test aspects, not devices: the Game view's Device Simulator covers notch, safe area and dpi. Check a tall phone
  (19.5:9), a tablet (4:3), and the PC window resized freely.
- No hover-only information: a phone has no hover.

## Orientation and window

CLAUDE.md names the phone orientation. Lock it in Player Settings (`defaultInterfaceOrientation`), not at runtime. On
PC the game runs windowed and resizable; layout must follow `Screen.width`/`height` changes (the Canvas Scaler and
`SafeAreaFitter` already do).

## Quality tiers and frame rate

- Two quality levels: **Mobile** (0, phones and WebGL) and **PC** (1), each with its own URP asset in
  `Assets/<Game>/Settings`. `ProjectSetup` creates them; tune those assets, add a third tier there if needed.
- Phones run at `Application.targetFrameRate = 60` (`AppStartup`); PC uses vSync. A battery-saver option can drop to
  30 on phones.
- Per-platform texture overrides in the importer (max size, ASTC on mobile) beat runtime branches.

## App lifecycle

- `OnApplicationPause(true)` is the last reliable moment on a phone: save there, not in `OnApplicationQuit` (iOS
  rarely calls it, Android kills the process).
- Pause the game on focus loss on both targets.
- Android back button arrives as `Keyboard.current.escapeKey`: treat it like Esc (back / pause menu). On Android 16
  the back gesture may not arrive as `Keyboard.current.escapeKey`; test back navigation on a phone before relying on it.
- Never `Application.Quit()` on iOS; hide the quit button there.

## Building

**GameKit > Build > Windows / Android / iOS / WebGL**, or `gk-bridge build windows|android|aab|ios|webgl [dev]` in a
background Bash call (it prints the head of `Logs/agent/build.log`; exit 0 is the only pass). A build switches platforms
and reimports, which takes minutes: ask before starting one.

- Android needs the Android Build Support module (with OpenJDK and SDK/NDK) in Unity Hub; `BuildMenu` reports when it is
  missing. IL2CPP, ARM64 only. Store releases need a keystore, which is the user's to create and keep out of git.
- iOS produces an Xcode project in `Builds/iOS`; it is signed and built on a Mac.
- WebGL uses the itch.io size pass from Magic Sort and Pixel Volley (Brotli compression with `decompressionFallback`
  off, which itch.io serves; the Responsive template, high stripping, disk-size LTO). The web target is WebGL 2.
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
