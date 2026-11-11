# Packages worth adding, per game

Checked on 2026-11-09 against each project's releases and license. The base manifest stays small: add one of these
when a game needs it, with the line below, and ask first (CLAUDE.md). A pack in `packs/` already wires Steam
(`steam`), the store rating prompt and notifications (`mobile-store`) and CI (`ci-github`).

## Add when needed

| Need | Package | Install line (`Packages/manifest.json`) | Notes |
|---|---|---|---|
| Tweens without Feel | PrimeTween 1.5.2 | scoped registry `{"name":"npm","url":"https://registry.npmjs.org","scopes":["com.kyrylokuzyk"]}` + `"com.kyrylokuzyk.primetween": "1.5.2"` | Zero-allocation. License: free in commercial games, but a template or repo may only depend on it through npm, never vendor its source. The OpenUPM mirror is stale (1.3.3). Try Feel's `MMTween` first. |
| Translations | Unity Localization 1.5.14 | `"com.unity.localization": "1.5.14"` | 2.0 needs Unity 6.7. String tables + Smart Strings; TR/EN player text. |
| In-app purchases | Unity IAP 5.5.0 | `"com.unity.purchasing": "5.5.0"` | Play Billing and StoreKit 2. Initializes Unity Gaming Services first. |
| On-device log console | In-game Debug Console 1.9.1 (yasirkula, MIT) | `"com.yasirkula.ingamedebugconsole": "https://github.com/yasirkula/UnityIngameDebugConsole.git#v1.9.1"` | Shows errors on a phone with no cable. Keep it out of release builds (spawn it only when `Debug.isDebugBuild`). Feel's `MMDebugMenu` may already be enough. |
| Unity-aware code analysis | Microsoft.Unity.Analyzers 1.28.0 (MIT) | NuGet package DLL into `Assets/__GAME__/Analyzers/` with the `RoslynAnalyzer` label and every platform unticked | Flags Unity-specific mistakes (`?.` on UnityEngine.Object, empty Unity messages). Visual Studio Tools for Unity and the VS Code Unity extension already run it in the IDE; vendor it only to see the warnings in Unity's Console too. |

## Release automation, when a game ships

| Need | Tool | Notes |
|---|---|---|
| Play upload from CI | r0adkll/upload-google-play v1.1.5 (MIT) | Not with the shipped `ci.yml`: its `BuildMenu.Android` builds a debug-signed APK and ignores GameCI's `androidExportType` and keystore inputs. Either a separate job on GameCI's default build method (no `buildMethod`) with `androidExportType: androidAppBundle` and the `androidKeystore*` secrets, or upload the AAB built locally from the menu. The first upload of the app is manual in Play Console; start on the `internal` track. |
| TestFlight from CI | fastlane 2.241 (MIT), or Apple-Actions/upload-testflight-build v5.9 | Needs a macOS runner for the Xcode build, an App Store Connect API key and code signing (fastlane `match`). |
| Steam upload from CI | game-ci/steam-deploy v3 (MIT) | See `packs/steam/README.md`. |

## Skipped, and why

| Package | Why not |
|---|---|
| UniTask | Unity 6 has `Awaitable` (`await Awaitable.NextFrameAsync()`, `WaitForSecondsAsync`); add UniTask only when the missing `WhenAll` and cancellation helpers start to hurt. |
| LitMotion | Needs Burst + Collections; PrimeTween or Feel covers the same ground with fewer dependencies. |
| DOTween | Asset Store only, no UPM line, and allocates per tween; PrimeTween does neither. |
| Graphy | `FrameLog` (F3, Development Builds) plus the Profiler covers frame time. |
| ZString | Last release 2024; `TMP_Text.SetText(format, value)` already formats numbers without allocating. |
| Facepunch.Steamworks | Ships as DLLs with no UPM package; Steamworks.NET (`steam` pack) installs by URL. |
| Unity Atoms, DI containers, event buses, pooling and save frameworks | The Core/Game split and `UnityEngine.Pool.ObjectPool<T>` cover them; CLAUDE.md asks before any framework. |
| CoplayDev/unity-mcp, IvanMurzak/Unity-MCP | The Unity CLI with `com.unity.pipeline` (in the base manifest) and the agent bridge already drive the Editor. |
