# Verifying a network change on one PC

How a networking change is checked without a second PC or a second person. Real internet between two houses is a
separate exercise (a playtest), not this.

The pieces, all installed by the pack's `packages.json`: **Multiplayer Play Mode 3.0.0** (MPPM) gives a second
instance, a **connect UI the game builds** drives it because a virtual player has no Inspector, and FishNet's
**latency simulator** makes the result worth judging. How Mixtrol ran this loop with its own scenes, menus and
buttons is the last section of `docs/networking-mixtrol-example.md`.

## The 30-second loop

1. Open the scene that holds the mechanic the change touches; if the game has a gym or test scene with a zone for it,
   start there. Pick the mechanic most sensitive to latency (anything a partner's press decides) before a calm one.
2. `Window > Multiplayer > Multiplayer Play Mode`. MPPM 3.0 is scenario-based: make a scenario with **one extra
   instance** (two players total) and activate it. Play then opens the main Editor plus one virtual player window.
3. Open the game's connect UI in each window. Build a **direct** path into it from the first networked commit: host on
   a port, join `127.0.0.1:7777`, a status line that says connected and which side is the host. Show that section only
   when `Debug.isDebugBuild`, at runtime rather than compiled out, so a development build can use it too.
4. **Main Editor** hosts directly; **virtual player** joins `127.0.0.1:7777`. Both status lines show connected and the
   host's says it is the host.

The direct path is plain UDP on loopback: no relay, no Unity Gaming Services, no internet. Use it for everything
except testing the relay itself. The relay path (host a room, copy the join code, join with it on the virtual player)
needs the internet, a UGS project linked in `Edit > Project Settings > Services` and Relay enabled on the Unity
dashboard; when Relay is off, make the status line say so rather than hang.

A WebGL client has no direct path: test it over the relay, with the Editor hosting a room and a WebGL development
build (served locally, `Build And Run`) joining with the code; its transport setup is the Platforms section of
`.claude/rules/networking.md`. A phone host is tested the same way, plus one background-and-return on the phone
while the Editor client watches its status line.

## Latency

FishNet's latency simulator sits on the `TransportManager` component of the `NetworkManager` prefab: **Enabled**,
**Simulate Host**, **Latency** (ms; doubled when acting as host, at least one tick), **Out Of Order** and **Packet
Loss** (percent). Judge at **off**, **80 ms**, **150 ms** and **150 ms + 2 % packet loss**; an Editor menu that writes
these four presets into the prefab is cheap and worth having.

Set it **before pressing Play**. A virtual player loads the same prefab from the same project, so both instances get
the same conditions; changing it mid-session only affects the window you changed it in.

Keep **Simulate Host** on: the host eats its own latency. Without it the one person judging whether a mechanic feels
good is the one person not feeling the delay.

The simulator is compiled out of release builds: every call site in FishNet's `TransportManager` is inside
`#if UNITY_EDITOR || DEVELOPMENT_BUILD`. It is a development tool, not a game setting.

150 ms is the number to judge against: roughly Istanbul to western Europe, and worse than most real sessions. If a
mechanic survives 150 ms it survives the players.

## Gotchas

- **After a code change, close and reopen the virtual player.** GameKit's ProjectSetup turns domain and scene reload
  off (Enter Play Mode options), and MPPM is known not to reload the domain for extra instances in that
  configuration: the virtual player can keep running the old code while the main Editor runs the new one, which looks
  exactly like a desync bug.
- **A built player keeps ticking while unfocused; the Editor does not.** The pack's `CoopSetup` turns
  `runInBackground` on, so two windowed builds on one PC both run. The Editor and its virtual players still freeze
  when they lose focus, so latency measured across a background Editor window is meaningless: put the two windows side
  by side rather than one behind the other.
- **The characters change when a session starts.** Offline, the spawner makes every local body itself (a split
  keyboard, if the game has one). The moment a window hosts or joins, those bodies go and the host spawns one per
  connection: each window drives exactly one character, and the other is the partner's copy. The host alone in a room
  is one character until the client arrives. Leaving reloads the scene, which is the only way back.
- **Don't force a recompile while in Play Mode**: it triggers a mid-session domain reload and throws spurious Input
  System errors. Stop Play first.
- **A build is a snapshot of the scene files, not of the Editor.** Testing a host in the Editor against a build made
  before the change is a desync every time, and it reads as a bug in the change. Rebuild after touching a scene or a
  prefab; building each target is `gamekit:platform-targets`.

## Adding or removing a NetworkObject

Both of these bit Mixtrol, and neither error says what it means.

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
  followed by a cascade of nulls out of the `OnEnable` of every component that reads the `NetworkManager`.**
  Nothing is actually wrong with the asset. FishNet regenerates
  `Assets/DefaultPrefabObjects.asset` whenever the spawnable set changes, which destroys the loaded
  ScriptableObject under the `NetworkManager` that had already resolved it; `NetworkManager.Awake`
  then throws before it builds `ClientManager` and `ServerManager`, and every NRE after that is a
  symptom. A domain reload fixes it — save any script, or `EditorUtility.RequestScriptReload()`.

## Single-player is unaffected

The game with no session started is the game before networking existed. `NetworkManager` opens no socket until the
session owner is told to start one, and nothing tells it to unless a button is pressed. Close the connect UI and play
as before.
