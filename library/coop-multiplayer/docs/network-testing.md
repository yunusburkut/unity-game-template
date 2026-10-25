# Verifying a network change on one PC

How a networking change is checked without a second PC or a second person (MIX-75). Real internet
between two houses is a separate exercise — that is the playtest issue (MIX-81), not this.

The pieces: **Multiplayer Play Mode 3.0.0** gives a second instance, the **connect panel** drives it
because a second instance has no Inspector, and FishNet's **latency simulator** makes the result
worth judging.

## The 30-second loop

1. Open `Assets/Scenes/Gym.unity`. Warp to **zone 13, Takas Kapısı** — the swap gate is the mechanic
   most sensitive to latency, so it is where a network change shows first. For a change to the
   mechanism list rather than to the swap — plates, crumbling floors, the see-saw, the pushed crate —
   open `Assets/Scenes/Bolum_01.unity` instead and start at segment 3; the gym has no see-saw and no
   crate, and Bölüm 1 is the first level after the main menu.
2. `Window → Multiplayer → Multiplayer Play Mode`. MPPM 3.0 is scenario-based: make a scenario with
   **one extra instance** (two players total) and activate it. Play then opens the main Editor plus
   one virtual player window.
3. Press **Esc** (or F4) in each window to show the connect panel if it is hidden.
4. **Main Editor** → `Doğrudan kur`. **Virtual player** → leave the address at `127.0.0.1:7777` and
   press `Doğrudan bağlan`.
5. Both status lines should read `Bağlandı`; the host's says `Bağlandı   |   Oda sahibi`.

A level opened straight in the Editor plays **Takım**. To test another mode (MIX-301), start Play in
`Assets/Scenes/MainMenu.unity` instead: in the main Editor pick `Oyna → Tek PC`, the mode and the level;
in the virtual player pick `Tek PC` and the same level (its mode does not matter); then connect as in
steps 3–5. The host's mode reaches the joiner through `NetworkLobby`, and F1 shows it on both.

`Doğrudan bağlan` is plain UDP on loopback — no relay, no Unity Gaming Services, no internet. Use it
for everything except testing the relay itself. It is hidden in release builds at runtime
(`ConnectPanelView` shows its section only when `Debug.isDebugBuild`), not compiled out.

To test the **relay** path instead, press `Oda kur` on the host, `Kodu kopyala`, then paste into the
virtual player's code field and press `Koda katıl`. `Oda kur` reloads the level as a room; the code is the
relay's six characters plus one for the level, so a joiner loads the host's scene from it (the main
menu's `Oyna → Oda kur / Odaya katıl` is the same path, MIX-26). This needs the internet and the UGS project
(already linked: `cloudProjectId 0db45902-…`). If Relay is not enabled on the Unity dashboard, the
status line says so rather than hanging.

## Latency

`Mixtrol → Ağ → Gecikme` → **Kapalı**, **80 ms**, **150 ms**, **150 ms + %2 paket kaybı**.

Set it **before pressing Play**. The preset writes `NetworkManager.prefab`, and a virtual player
loads the same prefab from the same project, so both instances get the same conditions. Changing it
mid-session only affects the window you changed it in.

`_simulateHost` stays on deliberately: the host eats its own latency. Without it the one person
judging whether the swap feels good is the one person not feeling the delay.

The simulator is compiled out of release builds — every call site in FishNet's `TransportManager` is
inside `#if UNITY_EDITOR || DEVELOPMENT_BUILD`. It is a development tool, not a game setting.

150 ms is the number to judge against: roughly Istanbul to western Europe, and worse than most real
sessions. If a mechanic survives 150 ms it survives the players.

## Gotchas

- **After a code change, close and reopen the virtual player.** This project runs with domain reload
  off (`m_EnterPlayModeOptions: 3`) and MPPM is known not to reload the domain for extra instances in
  that configuration — the virtual player can keep running the old code while the main Editor runs
  the new one, which looks exactly like a desync bug.
- **A built player keeps ticking while unfocused; the Editor does not.** `runInBackground` is on, so
  two windowed builds on one PC both run. The Editor and its virtual players still freeze when they
  lose focus, so latency measured across a background Editor window is meaningless — put the two
  windows side by side rather than one behind the other.
- **The characters change when a session starts.** Offline, `PlayerSpawner` makes both bodies itself
  and the keyboard is split in two. The moment a window hosts or joins, those bodies are removed and
  the host spawns one per connection: each window drives exactly one character on 1P's keys — the
  left half only, whatever its seat, so the joining player in seat 2 plays on A/D/W too and the arrow
  keys do nothing — and the other one is the partner's mirrored copy. The 2P line in the F1 panel
  only shows while one keyboard really drives two characters. The host alone in a room is one
  character until the client arrives. Leaving reloads the scene, which is the only way back.
- **Don't force a recompile while in Play Mode** — it triggers a mid-session domain reload and throws
  spurious Input System errors. Stop Play first.
- **A build is a snapshot of the scene files, not of the Editor.** Testing a host in the Editor
  against a build made before the change is a desync every time, and it reads as a bug in the change.
  Rebuild after touching a scene or a prefab — see `windows-build.md`.

## Adding or removing a NetworkObject

Both of these bit on 2026-09-20 and neither says what it means.

- **`SceneId of N not found in SceneObjects`, on the client.** FishNet gives every *scene* network
  object an id and writes it into the scene file; the two machines address objects by it. Adding a
  `NetworkObject` to a prefab mints ids only for the instances in scenes that happen to be **open**,
  and only in memory — so a scene that is never saved, or never opened at all, ships without them and
  the client is told about an object it has never heard of. After changing which prefabs carry a
  `NetworkObject`, open and save **every scene that places one**, then rebuild. FishNet's own minter
  is `NetworkObject.CreateSceneId(scene, force: false, out int count)`; `force: false` keeps every id
  that already exists, and renumbering a scene would invalidate every id already written into it.
  Check with `grep -c 'propertyPath: SceneId' Assets/Scenes/*.unity` against the number of network
  objects each scene holds, and make sure none of them is `0`.
- **`MissingReferenceException: The variable _prefabs of DefaultPrefabObjects doesn't exist anymore`,
  followed by a cascade of nulls out of `NetworkSession.OnEnable` and `PlayerSpawner.OnEnable`.**
  Nothing is actually wrong with the asset. FishNet regenerates
  `Assets/DefaultPrefabObjects.asset` whenever the spawnable set changes, which destroys the loaded
  ScriptableObject under the `NetworkManager` that had already resolved it; `NetworkManager.Awake`
  then throws before it builds `ClientManager` and `ServerManager`, and every NRE after that is a
  symptom. A domain reload fixes it — save any script, or `EditorUtility.RequestScriptReload()`.

## Single-player is unaffected

The game with no session started is the game before networking existed. `NetworkManager` opens no
socket until `NetworkSession` is told to start one, and nothing tells it to unless a button is
pressed. Press Esc to dismiss the panel and play as before.
