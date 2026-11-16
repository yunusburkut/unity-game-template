---
paths:
  - "Assets/__GAME__/Game/Net/**"
  - "Assets/__GAME__/Game/Prefabs/Net/**"
  - "docs/network-testing.md"
---

# Networking (FishNet)

FishNet 4.7 (an immutable git package, pinned with FishyUnityTransport and `com.unity.services.multiplayer` in the
pack's `packages.json`) with FishyUnityTransport's `UnityTransport` over Unity Relay: host + client, no dedicated
server. API: context7 `/websites/fish-networking_gitbook_io` (give the ID directly; search does not find it). The
FishNet source is under `Library/`, which is not read.

Networked code lives in `Assets/__GAME__/Game/Net/` so this file loads with it; a `NetworkBehaviour` written anywhere
else follows it all the same. The type names below are roles: create each one when you build that part, named for
__GAME__. How Mixtrol built every role, with the prediction and mechanism detail, is
`docs/networking-mixtrol-example.md`: read it on demand, never as the contract.

## Session lifecycle

- One `NetworkManager` prefab sits in every playable scene and never starts on its own. Single-player is the game
  with no session started. One session owner on that object is the only place a host or client starts or stops.
- Not DontDestroyOnLoad: end every session with a scene reload. FishNet leaves a stopped session's scene network
  objects switched off, and a scene load mid-session goes through the session owner, which ends the session first.
- FishNet switches every scene network object off in its own `Start` while no session runs. For the offline game to
  exist, the session owner switches them back on after the first frame, and offline bodies are spawned with
  `SetIsNetworked(false)`. So a scene `NetworkBehaviour` also runs offline, uninitialized: ask
  `NetworkObject != null && NetworkObject.IsSpawned` (one extension method) before `IsServerStarted` in anything
  reached every frame, or it is a null dereference.
- Everything that needs the internet (UGS init, anonymous sign-in, relay allocation) lives in one launcher that hands
  the result to the session owner, which knows nothing about relays. On UDP targets relay data goes onto the
  transport through its byte-array overloads (`SetHostRelayData` / `SetClientRelayData`), never by constructing
  `RelayServerData`: FishyUnityTransport is compiled against `com.unity.transport` 1.3.1 and Unity 6000.6 resolves the
  built-in 6.6.0. WebGL is the one exception (Platforms below).

## Platforms

- **WebGL.** A browser opens no UDP socket: the build talks to Relay over secure WebSockets or not at all. Read the
  allocation's (and the join allocation's) `ServerEndpoints` entry whose `ConnectionType` is `"wss"`, set the
  transport's `UseWebSockets` in that build, and hand the data over with `SetRelayServerData(new RelayServerData(host,
  port, allocationIdBytes, connectionData, hostConnectionData, key, isSecure: true, isWebSocket: true))`
  (`Unity.Networking.Transport.Relay`). The byte-array overloads cannot carry the WebSocket flag, and
  `com.unity.transport` 6.6's `NetworkDriver` throws "Mismatched Relay configuration" when a WebSocket driver gets
  UDP relay data. There is no direct path (the loopback join in `docs/network-testing.md` is UDP), so hide it in a
  WebGL build. Ship WebGL as a client only until a WebGL host has been verified, and verify that a desktop host on a
  UDP allocation accepts the WebGL client before promising cross-play.
- **Mobile.** `runInBackground` (the pack's `CoopSetup`) works on desktop and WebGL only; iOS and Android suspend a
  backgrounded app, and FishNet has no host migration. When a phone host goes to the background
  (`OnApplicationPause(true)`), the session ends for everyone: the session owner stops it and each client's status
  line says the host left, rather than letting clients time out on a frozen host. A paused phone client is dropped and
  rejoins as a new connection (it spawns at the last banked checkpoint, as above). The lifecycle hooks themselves (pause,
  focus, back button) are `gamekit:platform-targets`; its "pause the game on focus loss" applies to the offline game,
  never to a running session.

## Authority

- Write the split in CLAUDE.md's Networking section before the first networked object. The default for a co-op
  platformer: characters are client-authoritative (the owner steps and decides its deaths, hazards and throws; other
  machines see a copy), the world (carried objects, plates, doors, checkpoints, shared deaths) is host-authoritative.
- A SyncType `OnChange` filters the host with **`asServer || IsServerStarted`**, never `asServer` alone: a client host
  runs both halves and would adopt its own answer a second time as a client.
- A client asks for a world change through a `[ServerRpc]`; the host checks the caller may act, then acts. A key
  press never travels as a world change.

## Characters and world objects

- A spawner makes the characters, offline and online; scenes hold spawn points, never characters (a placed one would
  be a scene network object *and* the connection's spawn). Online the host spawns one per connection, owned by it,
  at the last banked checkpoint so a mid-run joiner is not born at the level's start.
- Refuse a joiner on another build: the host sends `Application.buildGUID` and the client compares. An Editor has
  no build GUID, so allow an empty one.
- Prefer few `NetworkObject`s: a registry that addresses a level's moving parts by index needs a **total** order
  (hierarchy path including each sibling index; scenes repeat names), or the client moves the wrong object. The host
  writes shared state on the tick, never the frame.
- Prefer a discrete state the host decides over shared physics; never gate a beat on two machines agreeing inside
  1 s.

## FishNet gotchas

- `Assets/DefaultPrefabObjects.asset` is FishNet's generated spawnable-prefab list at the path its configuration
  expects: leave it.
- FishNet's ILPostProcessor rewrites `__GAME__.Game`: a `[ServerRpc]` gains `RpcWriter___` / `RpcReader___` methods;
  their absence means codegen did not run.
- Turn the `ServerManager` / `ClientManager` frame-rate override off in the prefab; FishNet would otherwise write
  `Application.targetFrameRate` when a session starts and fight the game's quality tier.
- Domain and scene reload are off (GameKit's ProjectSetup): a mutable static in networked code (a session
  singleton, a registry, a cached `NetworkManager`) needs a
  `[RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.SubsystemRegistration)]` reset, or the second Play session
  starts with the first one's state.
- A text field in the connect UI (a room code, a name) disables the Gameplay action map while it has focus: letters
  and Space are moves.
- Adding or removing a `NetworkObject` on a prefab: `docs/network-testing.md` has the SceneId and
  DefaultPrefabObjects traps.

Testing a network change on one PC: `docs/network-testing.md`.
