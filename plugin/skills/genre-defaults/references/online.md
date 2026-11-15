# Online play and other devices

Read this when the user's words ask for play over a network, a leaderboard, VR or a console. Name the cost before the
idea is committed.

## Name the online level

Record one DESIGN.md Decisions line: `YYYY-MM-DD: Online: <level>; built: <what>; stand-in until then: <what>. Why.`
More than one level (co-op with a leaderboard): name the highest level, and each stand-in.

| Level | The user asks for | What gets built |
|---|---|---|
| 1. One screen | friends at one screen, couch co-op, party play | Local players through the Input System `PlayerInputManager`, one device each. No network. Build this first: it proves the co-op idea at no network cost |
| 2. Async | leaderboards, ghosts, daily challenges | A backend: the steam pack's `SteamUserStats` on PC, or the UGS packages in `gamekit:unity-package-management` (references/select-packages.md). Stand-in: a daily seed from the date with a code to share it, a local leaderboard, a ghost of your own best run |
| 3. Session | co-op with friends on their own machines | The `coop-multiplayer` pack: FishNet over Unity Relay, host and client, no dedicated server. Stand-in: bots in the empty seats, named as bots |
| 4. Dedicated servers | ranked or competitive play against strangers, matchmaking | Out of scope for one developer: say so. Offer level 3 with friends, or level 1 |
| 5. Persistent world | an MMO, a shared world | Out of scope: say so |

- **The stand-in never proves the netcode.** A bot shows whether the idea is fun, never whether the game holds over a
  network. The two-machine test in the `coop-multiplayer` pack does that.
- **Every networked object works offline first** (the pack's networking rule), so level 1 and the bots keep working
  after level 3 is added.

## Other devices

The template ships PC (keyboard and mouse), mobile (touch) and WebGL; `platform-targets` covers each.

- **VR:** the template has no XR setup and no checks for it. Build the flat-screen game; VR is a separate decision.
- **Console:** a console build needs the platform holder's developer approval and its private Unity module, or a
  porting partner. The template cannot build or check one. Ship PC first; keep the console goal in DESIGN.md Platforms.
