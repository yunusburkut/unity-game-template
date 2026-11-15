# Selecting packages

Turn a game concept — genre, look, target platforms, monetization — into a concrete package
list, then install it via the C# PackageManager Client API (see the main `SKILL.md`).

**Check `packs/` in unity-game-template first.** A pack's `packages.json` is the source for its dependencies (pinned
versions, scoped registries); `new-game.ps1 -Packs <name>` merges it into a new game's manifest. For an existing game,
copy those exact lines into `Packages/manifest.json` rather than resolving a second, different set. Never add a package
that duplicates or competes with a pack's. Packs with dependencies: `mobile-2d` (the 2D packages), `mobile-store`
(Play review, notifications), `steam` (Steamworks.NET), `coop-multiplayer` (FishNet, FishyUnityTransport,
Multiplayer Services, Transport, Multiplayer Play Mode). Ask the user before adding any package.

**Principle:** install what the concept actually needs, not everything. A hyper-casual 2D
prototype needs far less than a 3D multiplayer RPG. Prefer packages already provided by the
chosen template (URP templates already include the render pipeline, Input System, etc.) — only
add what's missing. Don't pin exact versions unless a minimum is required; `Client.Add` without
a version resolves the latest compatible release. The exception is the [checked extras](#checked-extras-with-pinned-install-lines):
their lines pin the version that was checked (a git URL or npm-scoped package has no "latest compatible" resolution anyway).

The tables below are a starting point, not the whole registry. **Search the registry** to
discover packages beyond this list, confirm an id exists, or check available versions before
installing — see [Discovering and verifying packages](#discovering-and-verifying-packages).

## Discovering and verifying packages

Two ways to search, depending on whether the Editor is involved:

**In-Editor — the PackageManager Client API (preferred).** `Client.SearchAll()` returns every
package available in the project's configured registries (the Unity registry plus any scoped
registries), each with all its versions and metadata — this is what the Package Manager
window's search filters over. `Client.Search("<id>")` inspects a single package. Use the
ready-to-run `PackageSearch` script in the main `SKILL.md` to discover candidates and verify
ids/versions before building the install list.

**Terminal — query the npm-compatible registry directly** (no Editor needed) to confirm a
**known** id exists and list its versions:

```powershell
# Full metadata for one package: versions{}, dist-tags.latest, description, dependencies.
# Invoke-RestMethod throws on HTTP errors (a 404 for a bad id) instead of returning an error page.
$pkg = Invoke-RestMethod 'https://packages.unity.com/<id>'

# Just the latest published version
$pkg.'dist-tags'.latest

# Every published version, and the description
$pkg.versions.PSObject.Properties.Name
$pkg.description
```

This machine has no Python; in Git Bash, `curl -fsSL https://packages.unity.com/<id> | grep -o '"latest":"[^"]*"'`
prints the latest tag.

Note: the registry supports fetching a **known** package id, but **not** free-text search over
HTTP (the npm `-/v1/search` endpoint is not available — it 404s). For keyword discovery, use
`Client.SearchAll()` in-Editor, the Package Manager window, or the
[Unity package documentation](https://docs.unity3d.com/Manual/pack-keys.html).

## Foundation (almost every project)

| Need | Package | Notes |
|---|---|---|
| Modern input | `com.unity.inputsystem` | Preferred over the legacy Input Manager. |
| Text / UI | `com.unity.ugui` | uGUI + TextMeshPro (bundled). UI Toolkit ships with the Editor. |
| Camera framing | `com.unity.cinemachine` | Great for almost any 3D and many 2D games. Unity 6 uses Cinemachine 3.x (`Unity.Cinemachine` namespace); 2.x samples do not apply. |
| Testing | `com.unity.test-framework` | Enables `unity test`; usually already present. |
| Large/streamed assets | `com.unity.addressables` | Add when the game has many assets or needs content updates. Rules below. |

**When Addressables is added:** store every `LoadAssetAsync` handle and call `Addressables.Release` on it in the
owner's `OnDestroy` (only if a load started); release every `InstantiateAsync` result with
`Addressables.ReleaseInstance`. Check `handle.Status == AsyncOperationStatus.Succeeded` before reading `Result`. Group
by loading context (menu, level N, shared, always loaded), not by asset type. LZ4 for local bundles, LZMA for remote
downloads. Load scenes with `Addressables.LoadSceneAsync` and release them on unload. Test in both the "Use Asset
Database" and "Use Existing Build" play modes: only the second matches the device.

## Render pipeline (pick one; usually set by the template)

| Choice | Package | Use when |
|---|---|---|
| **URP** (Universal) | `com.unity.render-pipelines.universal` | Default for most 2D/3D, mobile, and WebGL. Broadest platform reach. |
| **HDRP** (High-Definition) | `com.unity.render-pipelines.high-definition` | High-fidelity PC/console only. Not for mobile/WebGL. |
| **Built-in** | (none) | Simplest/legacy; fine for tiny prototypes. |

## By dimension & look

| Look | Packages |
|---|---|
| **2D** (any) | The `mobile-2d` pack's packages (sprite, tilemap, tilemap extras, animation, PSD and Aseprite importers, tooling). Outside the template: `com.unity.2d.feature`. Do not add both. |
| **2D pixel-perfect** | With URP, the Pixel Perfect Camera ships in URP itself (`UnityEngine.Rendering.Universal.PixelPerfectCamera`); `com.unity.2d.pixel-perfect` is the Built-in pipeline's |
| **3D navigation** | `com.unity.ai.navigation` (NavMesh for AI/pathfinding) |
| **Cutscenes / sequencing** | `com.unity.timeline` |
| **No-code logic** | `com.unity.visualscripting` |

## By genre (starting points, combine with the above)

| Genre | Typical additions |
|---|---|
| Platformer / action | URP, Input System, Cinemachine, 2D packages (if 2D), AI Navigation (if 3D) |
| Puzzle / match / card | URP or 2D packages, Input System, uGUI/TextMeshPro, Timeline (juice) |
| Top-down / twin-stick | URP, Input System, Cinemachine, AI Navigation |
| RPG / adventure | URP, Input System, Cinemachine, AI Navigation, Addressables, Timeline |
| Racing / physics | URP, Input System, Cinemachine; Physics is built in |
| Idle / hyper-casual | 2D packages or URP, Input System, uGUI/TextMeshPro (keep it lean) |
| Multiplayer (any) | The `coop-multiplayer` pack (FishNet + Unity Relay through Multiplayer Services). `com.unity.netcode.gameobjects` is Unity's own stack and **not** the template default: never add it next to FishNet. |

## By target platform

Platform support is mostly Editor **modules** (installed with `unity install --module …`, see
the **`unity-cli`** skill), not packages. Package-wise:

| Platform | Consider |
|---|---|
| Mobile (iOS/Android) | Keep dependencies lean; URP over HDRP; Addressables for download size; the `mobile-store` pack; monetization below |
| WebGL | URP (not HDRP); small footprint; avoid heavy packages |
| Desktop / Console | URP or HDRP depending on fidelity target; the `steam` pack for Steam |

## By monetization

| Goal | Package | Where the guidance is |
|---|---|---|
| In-app purchases | `com.unity.purchasing` | Model and price: **`gamekit:launch-review`**. Wiring: Unity IAP docs for the installed version |
| Ads / mediation | `com.unity.services.levelplay` | Model and ad placement: **`gamekit:launch-review`**. Wiring: Unity LevelPlay docs |
| Accounts, cloud save, economy, remote config, leaderboards, analytics | the UGS packages (`com.unity.services.core`, `authentication`, `cloudsave`, `cloudcode`, `economy`, `remote-config`, `analytics`, ...) | Unity Gaming Services docs per package |
| Store review prompt, local notifications | the `mobile-store` pack | Its README |

The upstream integration skills (implement-in-app-purchases, levelplay-unity-integration,
build-live-game) belong to the official Unity plugin, which stays **off** in gamekit games: do not
invoke them. Decide the model with the user first, then install the package(s) here and wire
them against the docs for the installed version, keeping these guardrails:

- Initialize UGS once at startup (`await UnityServices.InitializeAsync()` from `com.unity.services.core`) before any
  UGS-backed call, and handle its failure (offline start) without blocking the game.
- Analytics collects nothing before the player's consent: call `AnalyticsService.Instance.StartDataCollection()` only
  after consent, and give a way to withdraw it.
- Digital goods go through the store's billing; grant purchases from the purchase callback only, and validate
  receipts (the package's validator or a server) before granting anything of value.
- Ads: no ad on the first launch, rewarded ads only on the player's choice, and the platform's consent and
  child-audience rules (see **`gamekit:launch-review`**).
- Record in the handoff every API detail you could not confirm in the docs; never fill it from memory.

## Checked extras, with pinned install lines

These lines were checked on 2026-11-09 against each project's releases and license; they are the template's single
source for them (`packs/reference-docs/packages.md` points here). The base manifest stays small: add one when a game
needs it, with the line below, and ask first. These carry a pinned version because that version was checked; before
installing, confirm a newer release with the registry query above and re-check its notes. A pack in `packs/` already
wires Steam (`steam`), the store rating prompt and notifications (`mobile-store`) and CI (`ci-github`).

### Add when needed

| Need | Package | Install line (`Packages/manifest.json`) | Notes |
|---|---|---|---|
| Tweens without Feel | PrimeTween 1.5.2 | scoped registry `{"name":"npm","url":"https://registry.npmjs.org","scopes":["com.kyrylokuzyk"]}` + `"com.kyrylokuzyk.primetween": "1.5.2"` | Zero-allocation. License: free in commercial games, but a template or repo may only depend on it through npm, never vendor its source. The OpenUPM mirror is stale (1.3.3). Try Feel's `MMTween` first. |
| Translations | Unity Localization 1.5.14 | `"com.unity.localization": "1.5.14"` | 2.0 needs Unity 6.7. String tables + Smart Strings; TR/EN player text. |
| In-app purchases | Unity IAP 5.5.0 | `"com.unity.purchasing": "5.5.0"` | Play Billing and StoreKit 2. Initializes Unity Gaming Services first. Guardrails: [By monetization](#by-monetization). |
| On-device log console | In-game Debug Console 1.9.1 (yasirkula, MIT) | `"com.yasirkula.ingamedebugconsole": "https://github.com/yasirkula/UnityIngameDebugConsole.git#v1.9.1"` | Shows errors on a phone with no cable. Keep it out of release builds (spawn it only when `Debug.isDebugBuild`). Feel's `MMDebugMenu` may already be enough. |
| Unity-aware code analysis | Microsoft.Unity.Analyzers 1.28.0 (MIT) | NuGet package DLL into `Assets/__GAME__/Analyzers/` with the `RoslynAnalyzer` label and every platform unticked | Flags Unity-specific mistakes (`?.` on UnityEngine.Object, empty Unity messages). Visual Studio Tools for Unity and the VS Code Unity extension already run it in the IDE; vendor it only to see the warnings in Unity's Console too. |

### Release automation, when a game ships

| Need | Tool | Notes |
|---|---|---|
| Play upload from CI | r0adkll/upload-google-play v1.1.5 (MIT) | Not with the shipped `ci.yml`: its `BuildMenu.Android` builds a debug-signed APK and ignores GameCI's `androidExportType` and keystore inputs. Either a separate job on GameCI's default build method (no `buildMethod`) with `androidExportType: androidAppBundle` and the `androidKeystore*` secrets, or upload the AAB built locally from the menu. The first upload of the app is manual in Play Console; start on the `internal` track. |
| TestFlight from CI | fastlane 2.241 (MIT), or Apple-Actions/upload-testflight-build v5.9 | Needs a macOS runner for the Xcode build, an App Store Connect API key and code signing (fastlane `match`). |
| Steam upload from CI | game-ci/steam-deploy v3 (MIT) | See the `steam` pack's README (`packs/steam/README.md` in unity-game-template). |

### Skipped, and why

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
