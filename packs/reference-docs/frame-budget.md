# Frame budget

60 FPS is 16.6 ms. The target is a **flat** frame time, not a high average: a 0.3 ms GC spike is
worse than a 0.05 ms inefficiency, because the spike is the one the player feels.

This file holds the budget, the method, and what the static audit found. **The measurement itself is
not done** — it needs a modest laptop and a profiler, and it is MIX-53's remaining half.

## Budget at 60 FPS

| | ms | Note |
|---|---|---|
| Simulation (characters, carried object, mechanisms) | 2 | All `Update`, allocation-free |
| Rendering (Synty geometry, draw calls) | 9 | The largest share and the one to measure first |
| Particles and Feel | 2 | Spiky by nature; measure during a swap puff and a death |
| Networking (FishNet tick, 60 Hz) | 1 | Only on tick frames |
| Headroom | 2.6 | |

Networking is deliberately small. Characters are client-authoritative, so there is no prediction or
reconcile pass; the tick rate is 30, not 60; and the only per-frame network work is comparing
already-computed state against what was last sent.

## Method

1. Take a **development build** (`docs/windows-build.md`) — the Editor's own overhead is not the
   game's, and profiling in the Editor measures the wrong thing.
2. Profiler → Deep Profile **off** for timings, **on** only to find a named culprit.
3. Walk Level 1 end to end. Watch three counters: `GC.Alloc` per frame (target **0** during steady
   play), draw calls, and SetPass calls.
4. Record every point that drops below 60, with what was on screen. A point that drops for a known
   reason and stays written down satisfies this issue; a point that drops for an unknown reason does
   not.
5. Repeat once with a session running and the 150 ms latency preset on, to separate render cost from
   network cost.

## Frame log (2026-10-04)

`Game/FrameLog.cs` makes itself in **development players only** (not the Editor) and writes one CSV line per
second to `persistentDataPath/frame-log-*.csv` (`%USERPROFILE%\AppData\LocalLow\<company>\<product>\`; the path
is also in the player log). Columns: average fps, p99 and worst frame ms, frames over 17 ms, scene and camera
x/y/z at the worst frame, GC bytes per frame, draw calls, SetPass calls, CPU/GPU ms, system-used and GC-reserved MB.
**F3** or a three-finger tap shows fps, frame times, GC, draw/SetPass and CPU/GPU ms on screen (not position or
memory). Development players always collect frame timings; GPU ms reads 0 where the
graphics API has no timer queries.

To stand in for a Steam Deck on a desktop: run at 1280×800 windowed, cap the GPU (Afterburner power/clock
limit) and limit the cores (`start /affinity F Mixtrol.exe`, four cores), then walk each level and read the
lines whose `slow_frames` is not 0.

## Static audit of the networking layer (2026-09-18)

Everything added for MIX-74 through MIX-80 was read against the zero-allocation rule. Three things
were found and fixed at the time:

- **`SyncVar<View>` on the carried object** was written every frame. FishNet compares the incoming
  value against the held one before marking it dirty, and a struct with no `IEquatable<T>` is
  compared through `object.Equals` — which **boxes, every frame**. `View` now implements
  `IEquatable<View>`, and the object also compares before publishing, so an object standing still
  costs nothing.
- **`SyncList<Floor>`** had the same problem, twenty-one times a frame (one per crumbling floor in
  the gym). `Floor` is now equatable and only changed entries are written.
- **`SyncList<Seat>`** for the swap table, likewise.

Clean by inspection, no change needed:

- `SwappedControls.Read()` — called up to three times a frame; walks the registry and reads value
  types. No allocation, no boxing.
- `NetworkInput` — sends on the tick, not the frame, and only when the packet changed (three ticks
  running, then a heartbeat every ten); the packet is 11 bytes by hand (`NetworkInputSerializer`:
  held bits, body bits, run speed, twelve counters as nibbles). Nothing in it is allocated or boxed.
- `NetworkMechanisms.WriteTick` — host only, once per tick (MIX-266); compares and writes nothing when
  the level is still.
- `PlayerRegistry` — sorted on insert rather than on read, because reading it is the camera's
  per-frame path. Joining happens twice a session.
- `CameraFollow`, `ControlsHudView`, `ChasingHazard` — the lists they now keep are allocated once on
  join, never per frame. The HUD still rebuilds its string only when a displayed value changes.

## Draw calls (MIX-190, 2026-09-24)

The levels are Parkur kit geometry now, not Synty. Counted in the Editor's Game view with the game camera
parked along each level (`UnityEditor.UnityStats`, every pass counted: four shadow cascades,
depth-normals, opaque), the scenes drew 187–707 calls. Two changes took them to 51–198, with SetPass
calls (35–55) and triangles unchanged and the renders identical:

1. **Static Batching off** in the Windows player settings. `PC_RPAsset` runs the GPU Resident Drawer,
   which instances a repeated mesh in one draw, but 201 of Bölüm 4's 331 renderers were statically
   batched into combined meshes it cannot instance (Unity's GRD guidance: turn Static Batching off).
   −13…−52 %.
2. **The palette atlas** (`docs/level-kit.md`, *Look*): seven colour materials folded into one, so a
   kit part is one submesh instead of up to seven. A further −45…−65 %.

Per level in `docs/level-kit.md`, *Budgets*. These are counts, not milliseconds; the laptop run below
is still the measurement that decides.

## Known suspects, unmeasured

- **Draw calls on the target laptop.** Counted, not timed (above); the Profiler run in *Method* times them.
- **The swap puff and landing dust.** Particles under Feel, played on an edge — the spike to watch.
- **21 crumbling floors in the gym.** Gym only, and the gym is a test bench, not a shipped level.
  Bölüm 1 has eight, in segment 4, plus one see-saw and one pushed crate — all three are in the
  host-owned mechanism list, so on a client they cost an adopt rather than a solve.
- **`Physics.OverlapSphereNonAlloc` per character per frame** plus the carried object's raycast and
  boxcast. Preallocated and bounded, but they are physics queries in `Update`.
