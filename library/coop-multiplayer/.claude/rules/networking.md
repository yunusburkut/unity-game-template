---
paths:
  - "Assets/__GAME__/Game/**/*.cs"
  - "Assets/__GAME__/Editor/Level/**/*.cs"
  - "Assets/__GAME__/Game/Prefabs/Net/**"
  - "docs/network-testing.md"
---

> Written for Mixtrol (2–4 player 2.5D co-op platformer, FishNet over Unity Relay). Where this file states a
> Mixtrol fact (its keys, devices, levels, decisions), treat it as a worked example and use __GAME__'s own from
> DESIGN.md and CLAUDE.md instead.

# Networking (FishNet)

FishNet 4.7 (immutable git package) with FishyUnityTransport's `UnityTransport` over Unity Relay: host + client, no
dedicated server. API: context7 `/websites/fish-networking_gitbook_io` (give the ID directly; search does not find it).
The FishNet source is under `Library/`, which is not read.

## Session lifecycle

- `Game/Prefabs/Net/NetworkManager.prefab` sits in every playable scene (not the `Hedef_Harabe` look benchmark) and
  never starts on its own. Single-player is the game
  with no session started; `NetworkSession` (same object) is the only place a host or client starts or stops.
- Not DontDestroyOnLoad: every session ends in a scene reload, because FishNet leaves a stopped session's scene network
  objects (`Systems` included) switched off. A scene load goes through `NetworkSession.LoadScene`, which ends the session.
- FishNet switches every networked object off in its own `Start` while nothing runs. The offline game exists because
  `NetworkSession` switches the scene's back on at the end of the first frame and `PlayerSpawner` spawns offline bodies
  with `SetIsNetworked(false)`. So a scene `NetworkBehaviour` also runs offline, uninitialized: ask
  `this.Live()` before `IsServerStarted` in anything reached every frame, or it is a null dereference.
- `SessionLauncher` owns everything that needs the internet (UGS init, anonymous sign-in, relay allocation) and hands
  the result to `NetworkSession`, which knows nothing about relays. Relay data goes onto the transport through its
  byte-array overloads, never by constructing `RelayServerData`: FishyUnityTransport is compiled against
  `com.unity.transport` 1.3.1 and this project resolves the built-in 6.6.0.

## Authority

- Characters are client-authoritative (the owner steps `PlayerController` per frame and decides its deaths, hazards
  and throws; every other machine predicts a copy, below). The world —
  carried object, plates, doors, chasing walls, checkpoints, deaths — is host-authoritative. Spikes and the launch pad
  gate nothing and are decided locally from a position that has already travelled.
- A SyncType `OnChange` filters the host with **`asServer || IsServerStarted`**, never `asServer` alone: a client host
  runs both halves and would adopt its own answer a second time as a client.

## Characters

- `PlayerSpawner` on `Systems` makes the characters in both modes; scenes hold spawn points, never characters (a placed
  one would be a scene network object *and* the connection's spawn). Offline it instantiates them itself; online the
  host spawns one per connection, owned by it — at the banked checkpoint once there is one
  (`CheckpointTracker.TryJoinPoint`), so a mid-run joiner is not born, and respawned, at the level's start.
- `NetworkLobby` sends the host's `Application.buildGUID`; a joiner on another build leaves with "Sürümler farklı".
  An Editor has no build GUID, so Editor against a build is still allowed.
- `NetworkPlayer` carries the seat as a `SyncVar` (colours and the swap table index by it) and the name its owner
  typed in the main menu (host-cleaned `SyncVar<string>`, shown over the body), and marks a body somebody
  else plays as not `Driven`. **A copy is predicted, not carried:** there is no
  `NetworkTransform` on a character. The owner's `NetworkInput` packet carries its keys (presses as counters, a key
  change the frame it happens) and its body — position plus the `MovementState` its solver carries between steps, 65
  bytes, every other tick while it moves. Every machine steps the copy through the same `PlayerController.Step` as
  the owner; each state that lands rebases it and steps it on by the packet's age (measured from the network tick it was stamped on), and
  the mesh closes the correction over 0.05 s (`_shown` on the `Pose` node). The tick is 120 Hz (2026-10-11).
- A copy's input is `SwappedControls.ReadPredicted`: every seat's held keys, but presses only from this keyboard — a
  press from the wire is already in the owner's state. So a partner's taken move plays on the copy the frame Space goes
  down; until the owner's packet says it has played the press (`Played`, a nibble per seat), a rebase plays it again.
  The owner shortens a wind-up armed by a press from the wire by that press's trip (`TripOf`), so the jump leaves when
  the presser saw it leave; the hold is timed from the press, so the arc is the same. Deaths, hazards, pad throws and
  knocks stay the owner's (`Kill` / `Launch` refuse a copy) and reach it as the next state.
- `PlayerAnimator` runs on the copy's own stepped state as offline; the hop's verdict is the owner's (`NetworkInput.Hop`)
  unless the jump was played from this keyboard (`JumpedHere`). There is no `NetworkAnimator`: the `Pose` node's yaw and
  somersault are composed locally, because an interpolated rotation swings a 180 flip through the camera.
- The `CharacterController` stays on and a copy moves through it, so the host sees a remote character stand on a plate
  where it is now. Ceiling: a copy is a few centimetres ahead of the truth when its owner stops, so a host trigger at
  the edge of where they stopped can see them for a frame.

## Level mechanisms

- `NetworkMechanisms` addresses plates, floors, see-saws, pushable crates (`Pushable`), moving platforms (a pulley's
  pan and cabin are two, driven by one plate), treadmills, decoy checkpoints, door latches, chasing walls (the rising
  goo is one) and Parkur obstacles by index into lists ordered by
  hierarchy path *including each level's sibling index* — scenes repeat names (`CrumblingFloor` ×8), so an order that is
  not total moves the wrong object on the client.
- Everything in a level that moves goes through it and carries no `NetworkObject` of its own. Input-less devices are in
  it because a solver with no input is a clock: a clocked obstacle, platform or treadmill keeps its own clock on the
  client and is corrected four times a second, run on by half the round trip so it shows the host's now (a running
  chase too); a plate-driven platform is told every tick. A throw is decided where the
  body is driven.
- The host writes the lists on the tick, never the frame. A latching door's latch is the one door state that
  travels.
- Levers are the one device a client asks for: a key press does not travel, so the presser's machine sends
  `PullServer`, the host checks the seat (`SeatAuthority`) and pulls; doors follow their inputs.
- Exceptions: the carried objects — carry boxes and the cauldron — ride a server-authoritative `NetworkTransform`
  (`_clientAuthoritative` off) — the only `NetworkTransform`s left; a character has none.

## FishNet gotchas

- `Assets/DefaultPrefabObjects.asset` is FishNet's generated spawnable-prefab list at the path its configuration
  expects: leave it.
- FishNet's ILPostProcessor rewrites `__GAME__.Game`: a `[ServerRpc]` gains `RpcWriter___` / `RpcReader___` methods;
  their absence means codegen did not run.
- The `ServerManager` / `ClientManager` frame-rate override is off in the prefab; FishNet would otherwise write
  `Application.targetFrameRate` when a session starts.
- A room is a level. `SessionLauncher.HostAsync` / `JoinAsync` make the relay allocation first — from the main
  menu or a level's room screen — then load the level, which applies it and starts the session one frame in; the
  allocation is the only thing carried across the load. The room code is the relay's six characters plus one for the
  level's build index, so a joiner loads the host's scene from the code alone.
- `Game/Prefabs/Net/ConnectPanel.prefab` is the room screen and the in-level menu (Devam / Ana menü) in every playable
  scene. It toggles on Esc or F4, polled from `Keyboard` like F2/F3, not bound in `__GAME__Controls.inputactions`. While its code field has focus it
  disables the Gameplay map through `PlayerInputReader.SetGameplayEnabled` — Space and every letter are moves.

Testing a network change on one PC: `docs/network-testing.md`.
