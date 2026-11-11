# Taking a Windows build

One menu click (MIX-48). Take one early and often — the first build always breaks something an
Editor session never notices, and launch week is the wrong time to find out.

## The command

`Mixtrol → Build → Windows (sürüm)` — the release build, into `Builds/Windows/Mixtrol.exe`.

`Mixtrol → Build → Windows (development — gecikme simülatörü açık)` — into `Builds/Windows-Dev/`.
**This is the one to take for a playtest.** FishNet's latency simulator is compiled out of a release
build (`#if UNITY_EDITOR || DEVELOPMENT_BUILD` around every call site in `TransportManager`), so a
release build cannot be used to judge how the game feels at 150 ms. The connect panel's
`Doğrudan bağlan` section is behind the same flag, so a release build offers only the relay path.

`Mixtrol → Build → Build klasörünü aç` opens whichever exists.

`Builds/` is already in `.gitignore`; nothing from here is committed.

## What the build contains

The scenes come from the build profile (`File → Build Profiles`), read at build time rather than
hard-coded — the list is where a scene is added or removed, and two places to keep in step is one too
many. Today (2026-10-15, MIX-301 G2) that is **`Assets/Scenes/Test.unity` alone, at index 0** — a build
boots straight into the test level, where F2 and F8–F12 pick the mode and Esc opens a room. `MainMenu`,
`Level_001` and `Gym` stay in the list unticked; tick `MainMenu` back to index 0 and its "Ana menü" keys
return by themselves.

Player settings as they stand: company `Mixtrol Games`, product `Mixtrol`, version `0.1.0`,
`FullScreenWindow`, 1920×1080 default, resizable. `runInBackground` is on, which is what lets two
windowed builds on one PC both keep ticking while only one of them has focus.

## Two players from builds

1. Take the **development** build.
2. Run it on both PCs. One presses `Oda kur` and reads out the code; the other types it into the
   code field and presses `Koda katıl`.
3. Both status lines should reach `Bağlandı`. The host's reads `Bağlandı   |   Oda sahibi`.

The code goes through Unity Relay, so neither player opens a port and neither sees the other's IP.
It needs the internet and the UGS project on both ends.

For two instances on one PC, use Multiplayer Play Mode instead — that is `docs/network-testing.md`,
and it is faster than building.

## Things that only break in a build

- **Editor-only code.** Anything inside `#if UNITY_EDITOR` is gone. `LatencyPresets` and the build
  menu itself are Editor-only by design; the latency simulator is Editor-or-development.
- **Per-frame config re-reads.** `PlayerController`, `CheckpointTracker`, `CoCarriedObject`,
  `MovingPlatform`, `CrumblingFloor` and `ChasingHazard` all re-read their config asset every frame
  under `#if UNITY_EDITOR` so a slider can be dragged in Play Mode. In a build the value is read once,
  at `Awake`. A tuning change that only ever worked because of that re-read will not work in a build.
- **Shader variants.** URP compiles on demand in the Editor and ahead of time for a build; a material
  that looks right in Play Mode can come out pink.
- **Scene list.** A scene reached at runtime but not ticked in the build profile does not exist.

## Verify a build

Run it once and check: the game opens on the test level and is playable; F1 shows the controls panel; F4 shows
the connect panel; the game runs with no session started (single player is the offline game); and
the console log, at `%USERPROFILE%\AppData\LocalLow\Mixtrol Games\Mixtrol\Player.log`, has no errors.
