---
name: unity-code-review
description: Use when asked to review, audit or critique game C# ("kodu incele", "kodu gözden geçir") - correctness, culture, Core/Game boundary, lifecycle, ownership, saves and untrusted input, allocations, PC/mobile/WebGL gaps, pre-Unity-6 API, complexity.
---

# Reviewing code

This file is the checklist of the `gamekit:unity-reviewer` agent. `review et` / `puanla` belong to the `pipeline`
skill's scored review loop, not to this skill. For a diff, a commit range or a card, spawn `gamekit:unity-reviewer`
(or run the pipeline's review step). Reviewing inline instead: follow that agent's steps (getting the change, scope
`Assets/<Game>` only, the compile.log check) and its report format and **[yüksek]** / **[orta]** / **[düşük]** tags;
**[karar]** is defined in `pipeline/references/review-rubric.md`.

Report what materially matters. Do not nitpick style that already matches its surroundings.

## Look for, in rough priority order

1. **Correctness** — off-by-one in timer windows, state flags set but never cleared (one-step edge flags must reset at
   the top of every step), sign errors, order dependencies between systems.
   **Culture:** the player's machine may run tr-TR. A number or date that code writes and parses again (a save,
   PlayerPrefs, JSON, a URL, a parsed log) uses `CultureInfo.InvariantCulture` in both directions: the default culture
   writes `0,5` and reads `"0.5"` as 5. Keys and case-insensitive compares use `StringComparison.Ordinal` /
   `OrdinalIgnoreCase` and `ToUpperInvariant` / `ToLowerInvariant`: on tr-TR `"title".ToUpper()` is `"TİTLE"`, so a
   `switch` or dictionary lookup on it misses. Numbers shown to the player use the current culture on purpose.
2. **Boundary violations** — a `MonoBehaviour`, `Physics` call, `Time` or `Input` access or scene API that has drifted
   into `<Game>.Core`; game rules that have drifted into a MonoBehaviour. Runtime wiring through `GameObject.Find`,
   `FindFirstObjectByType` / `FindAnyObjectByType` / `FindObjectsByType`, `FindWithTag` or `SendMessage` instead of a
   serialized reference (a one-time Editor tool may scan). Game content loaded by string path through
   `Resources.Load`: a rename breaks it only at runtime, and everything under `Resources/` ships in every build.
3. **Lifecycle** — work in `Awake` that depends on another object's `Awake`; `OnEnable` subscriptions with no matching
   `OnDisable`; a mutable `static` with no `SubsystemRegistration` reset (Play Mode reload is disabled, so this only
   breaks on the second Play). Also:
   - An event or delegate subscribed by an object that can die before the publisher, with no unsubscribe: the callback
     then runs on a destroyed object.
   - `SetActive(false)` or `Destroy` stops every coroutine on the object, and re-activation does not resume them
     (disabling only the component does not stop them). A coroutine that must survive starts in `OnEnable`.
   - An `async` / `Awaitable` continuation runs after `Destroy` unless it checks `destroyCancellationToken`; one that
     touches `this` after `OnDisable` is a bug.
   - On a `UnityEngine.Object`, `?.`, `??` and `is null` skip Unity's destroyed check. Use `== null` or the bool
     operator.
   - An `Update` that idles in some state returns early or sets `enabled = false`; it does not poll for nothing.
   - A `DontDestroyOnLoad` object destroys its duplicate when its scene loads again (check the static instance first),
     and that static has a `SubsystemRegistration` reset.
4. **Saves and untrusted input** — a save file, PlayerPrefs value, downloaded JSON or deep link is player-editable.
   - The save has an `int version` from day one. An older version runs one explicit migration step per version and
     never defaults fields silently. Back up the old file before a migration writes the new version.
   - Write atomically: serialize to `<file>.tmp` under `Application.persistentDataPath`, then
     `File.Replace(tmp, file, file + ".bak")` (`File.Move` when no file exists yet). A kill or power loss mid-write
     then leaves the old save.
   - Load parses inside `try`/`catch` and bounds-checks values (level index inside the level list, currency not
     negative, counts below a cap). On failure it tries `.bak`, then starts fresh with a message the player sees:
     never a crash, never a silent wipe.
   - Save paths are `persistentDataPath` plus a fixed name, never built from player text. Never `BinaryFormatter`
     (unsafe on untrusted data, removed from modern .NET). PlayerPrefs holds settings only, never progress or large data.
   - No secret, API key or credential in a save, in code, or in a committed asset.
   - A leaderboard score, IAP unlock or "has paid" flag cannot be trusted from the client: tag it `[karar]` unless a
     server or the store's receipt validation checks it.
   - WebGL: `persistentDataPath` is backed by IndexedDB. A save change is unverified on WebGL until a save survives a
     page reload in a WebGL build.
5. **Platform gaps** — input that only works with a mouse or only with keys, UI placed outside the safe area or sized
   in pixels instead of through the `CanvasScaler`, `#if UNITY_EDITOR` logic the build depends on, a feature with no
   path on one of the targets (`platform-targets`).
   - WebGL has no threads by default: `Task.Run`, `new Thread` and `System.Threading.Timer` work run on PC and mobile
     but stall or never run there. Keep Unity-facing and WebGL-reached work on the main thread with `Awaitable` or a
     coroutine, and split long work across frames.
   - `async void` only for event handlers, with a `try`/`catch` inside: an exception thrown in it is not observed by
     any caller. Everything else returns `Awaitable` (or `Task`).
6. **Ownership** — two objects mutating the same state, or state duplicated across a view and its simulation. A
   `DontDestroyOnLoad` singleton that holds game state other systems write. UI that writes game state instead of
   reading it and sending a command.
7. **Hidden allocations** in anything reached per frame (`unity-performance`).
8. **Unnecessary complexity** — an interface with one implementation, a wrapper that only forwards, a factory for a
   single `new`, defensive null checks on Inspector-guaranteed dependencies, `try`/`catch` around code that cannot
   throw, unreachable fallback branches.
9. **Duplicated logic** — especially a second copy of a tuning number that already lives in a ScriptableObject.
10. **Inspector consequences** — a renamed serialized field silently loses its scene value unless it carries
    `[FormerlySerializedAs]`. Flag it, and say which assets need re-checking.
11. **Pre-Unity-6 API** — obsolete calls compile with only a CS0618 warning, so the compile gate passes them. Flag
    them and write the new form:
    - `Rigidbody` / `Rigidbody2D`: `.velocity` → `.linearVelocity`, `.drag` → `.linearDamping`, `.angularDrag` →
      `.angularDamping`. `PhysicMaterial` → `PhysicsMaterial` (`PhysicMaterialCombine` → `PhysicsMaterialCombine`).
      `CharacterController.velocity` and `NavMeshAgent.velocity` are not renamed.
    - `FindObjectOfType` / `FindFirstObjectByType` / `FindObjectsOfType` / the `FindObjectsSortMode` overload in
      runtime code: the fix is an Inspector reference (item 2), not a renamed lookup. Only in an Editor tool or a
      one-time bootstrap scan do they become `FindAnyObjectByType` and `FindObjectsByType<T>()` /
      `FindObjectsByType<T>(FindObjectsInactive)`. 6000.6 marks `FindFirstObjectByType` and the sort-mode overload
      obsolete too.
    - Any `UnityEngine.Input` call (`Input.GetKey`, `Input.GetMouseButton`, `Input.mousePosition`, `Input.touches`,
      `Input.GetAxis`) compiles with no warning but throws `InvalidOperationException` at runtime on every target:
      Active Input Handling is the Input System only. Rewrite it with an `InputAction` or the `Pointer` API
      (`platform-targets`).
    - Unity 6.4+: `InstanceID` → `EntityId`; `GetInstanceID()` → `GetEntityId()`; `InstanceIDToObject` →
      `EntityIdToObject`. A dictionary keyed on an instance ID becomes keyed on `EntityId`.
    - Cinemachine 3: namespace `Unity.Cinemachine`; `CinemachineVirtualCamera` → `CinemachineCamera`; Transposer →
      `CinemachineFollow`; FramingTransposer → `CinemachinePositionComposer`; Composer →
      `CinemachineRotationComposer`; FreeLook → `CinemachineCamera` + `CinemachineOrbitalFollow`; no `m_` fields
      (`m_Follow` → `Follow`).
    - URP custom pass: `Execute(ScriptableRenderContext, ref RenderingData)` and `OnCameraSetup` →
      `RecordRenderGraph(RenderGraph, ContextContainer)` with `renderGraph.AddRasterRenderPass`; read the camera
      colour from `frameData.Get<UniversalResourceData>().activeColorTexture`, not `cameraColorTargetHandle`. The old
      path runs only in URP Compatibility Mode, which URP 17.6 (Unity 6000.6) no longer offers:
      `RenderGraphSettings.enableRenderCompatibilityMode` is hard-wired to `false` there.
    - `WWW` → `UnityWebRequest`; `Application.LoadLevel` → `SceneManager.LoadScene`.

    This list is the source; the mechanical grep that mirrors it is the "obsolete API" section of
    `bash "${CLAUDE_PLUGIN_ROOT}/skills/refactor-pass/scripts/survey.sh" --all` (its "Old Input manager" and
    "Scene scans" sections cover the `Input` and item 2 hits). Run it before reading the diff by eye. A rename added
    here is added to that regex too, with a matching line in `refactor-pass/scripts/test-survey.sh`'s `Obsolete.cs`
    fixture.

## Convention checks

Player-facing and Inspector-facing strings in the language CLAUDE.md names, English for everything else. Comments carry
non-obvious intent, an invariant, or a performance reason, never a restatement of the line below. Flag comments that
do restate it.
