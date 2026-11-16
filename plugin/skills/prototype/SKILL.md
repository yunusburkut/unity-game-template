---
name: prototype
description: Use on "prototip", "prototipini yap", "dene bakalım", "hissettiriyor mu", "eğlenceli mi", "spike", "would X feel good / be fun?" - one falsifiable question in throwaway code, timeboxed, PROCEED/PIVOT/KILL, then deleted. Not "does this code work?".
---

# Prototype: answer one question, then throw the code away

A prototype is not the feature. It answers one question, and the feature is then built properly through a spec card
(`gamekit:pipeline`). The router gives a design question no size and sends it here, as does pipeline phase 1: no
spec card, no review loop.

## 1 The question

Write it in one sentence before any code, at the top of each prototype file and in the reply:

`If the player <does X>, they will feel <Y>; we know it if <observable signal Z>.`

- Good: "If the player swings from hook to hook, chaining feels like flow; we know it if they chain 3+ swings within
  2 minutes without being told."
- Rejected: "Is it fun?" There is no signal that can say no. Rewrite it until one can.
- Test the riskiest assumption first: the one that kills the idea if it is false.
- A co-op mechanic in a game with the `coop-chaos-design` skill (the coop-multiplayer pack) passes that ship gate
  first; the prototype then measures only the row the gate leaves open, never the whole mechanic.
- Feel, timing or physics is the question: a Unity scene. Logic, economy, cards, idle or strategy maths: a table or a
  spreadsheet first; it is often enough. A table prototype lives in the reply, or in
  `Assets/<Game>/Prototypes/<Name>/<Name>.md` when it must survive the session (no asmdef, no scene); the user
  "plays" it by reading the outcomes for the inputs they pick. It skips section 3's asmdef, compile gate, scene and
  Build Settings steps; its hand-off is the inputs the user picks and the signal to watch for. Sections 4 and 5 apply
  to it unchanged.

## 2 Timebox

- One mechanic, one sitting. All times count from the first line of prototype code.
- Not playable 2 h after starting: stop. Make the question smaller or switch approach; never push on.
- Playable: iterate on the question up to 4 h in all. Nothing goes past one day, whatever the state.
- Build only what the question needs: no menus, saves, music, game over, juice or UI unless that is the question.

## 3 Where it lives

`Assets/<Game>/Prototypes/<Name>/` with its own asmdef (`<Game>.Prototypes.<Name>`), and its own scene there.

- The asmdef sets `"autoReferenced": false` and `"defineConstraints": ["UNITY_EDITOR"]`: it compiles and plays in the
  Editor but never enters a player build, so throwaway code (PC-only input, a Feel call) never blocks an Android or
  WebGL build.
- It may reference `<Game>.Core` and the engine and package assemblies the question needs (Unity.InputSystem,
  UnityEngine.UI, Feel's MoreMountains.* when feel is the question), never `<Game>.Game`. `<Game>.Game`, Core and the test assemblies never reference it.
- Each file starts with `// PROTOTYPE - NOT FOR PRODUCTION`, `// Question: <the sentence>`, `// Date: YYYY-MM-DD`.
- Its code runs only from its own scene: no `[RuntimeInitializeOnLoadMethod]`, no static hooks, and the scene stays
  out of Build Settings unless the question needs a device.
- The question needs a device (touch feel, phone frame rate): drop the `UNITY_EDITOR` constraint for that build, and
  put the scene first in `EditorBuildSettings.scenes` through `unity command script run` (`unity-editor-cli`), never
  by hand-editing `ProjectSettings/EditorBuildSettings.asset` while the Editor runs. Write the original first scene
  in the reply and in the PLAN.md prototype line (section 5). While the constraint is off, the asmdef compiles into
  every player build, so it must build for every target (PC, mobile, WebGL).
- That device state lasts for the device session only. Once the user has played the build, and before any commit
  (the verdict, a PIVOT, a park, or a stop mid-session), put the `UNITY_EDITOR` constraint back and restore
  `EditorBuildSettings.scenes` (prototype scene out, the recorded original first scene back at index 0) through
  `unity command script run`, then pass the gate below. GameKit's build passes every enabled entry to the player
  build, so a left-over state boots every later build into the prototype and ships its code. The next device play
  applies it again.
- Gate before the commit: `gk-bridge refresh` exit 0 (1 = fix it, 2 = unknown, never a pass; the same three answers
  as `gamekit:pipeline`). A compile error anywhere blocks Play Mode for the whole project.
- Commit it to main like any work: git is the archive.
- Hand off in one line: `open Assets/<Game>/Prototypes/<Name>/<Name>.unity, controls: <keys / touch>, watch for
  <signal Z>`.

| Allowed to be ugly | Never allowed |
|---|---|
| Hardcoded numbers in one place (a `const` block or one config object) | Edits to Core or Game to make the prototype work |
| No tests, no `[FormerlySerializedAs]`, no pooling | A Game or Core type that depends on prototype code |
| Placeholder art: primitives, Unity default sprites | Promoting prototype code: anything kept is rewritten under the Core/Game rules (`unity-architecture`) |

## 4 Play it and judge

The user plays it; their observations decide, not your reading of the code. Nobody played it: the verdict is NOT
ASSESSED, never PROCEED.

Ask one question at a time and push back on vague answers ("it was fine" -> "what did you do in the first minute?"):
was the signal seen (CONFIRMED / PARTIAL / REFUTED), the best moment, the worst moment, the surprise.

- **PROCEED**: the signal was seen. The feature is built through a spec card; the prototype is reference only.
- **PIVOT**: part of it worked. Write what to keep, what to change and the revised question, then prototype again.
  The third PIVOT on one idea asks the user for a KILL decision.
- **KILL**: sound when 2 or more hold: still unclear after 2+ plays; no fun moment at all; 3+ pivots; works only
  when explained; feels like an obligation.

Solo testing: replay it after 2-3 days with fresh eyes, or think aloud while playing. With other testers, watch in
silence and ask only "what was confusing?"; 3+ testers hitting the same confusion means the rule is wrong, not the
tester. A network-feel question is never answered in one local instance: play it on two clients (Multiplayer Play
Mode or two builds) with the transport's latency simulator at the target latency and loss, the host simulating its
own latency too (the coop-multiplayer pack's `docs/network-testing.md` has the setup and presets). A performance
question needs a number on the weakest target device.

## 5 Record and delete

Log each play session the user reports under DESIGN.md Playtests first (CLAUDE.md). Then one DESIGN.md Decisions
line that points to that entry, then delete the prototype folder (with its `.meta` files) in the same commit:

`YYYY-MM-DD: prototype <Name>: KILL. <evidence: what was seen>. Worked: <x>. Failed: <y>. Next time: <z>.`

(PROCEED or PIVOT in place of KILL; a PIVOT keeps the folder until the next verdict, and a later verdict on the same
prototype edits its line, the old text kept as `was: ...`. NOT ASSESSED writes no line and keeps the folder; the
verdict waits until someone plays it.) The scene went into Build Settings for a device test: before this commit,
check that section 3's device-state restore was done (constraint back, prototype scene out of
`EditorBuildSettings.scenes`, the original first scene at index 0); a deleted scene left in the list fails the next
build.

Until the folder is deleted, PLAN.md Now holds one line, `prototype <Name>: <the question>` (plus `, first scene was
<path>` after a device test), so `devam` finds it; when the folder is deleted, Now goes back to its TODO line. Now
already holds a card: ask whether to finish it (`devam`) or park it first, exactly as `gamekit:pipeline` phase 1
does; never overwrite a card. A new M/L task while this line holds Now, and parking a spike, follow
`gamekit:pipeline` phase 1 too; a spike with a `first scene was` note is parked only after section 3's device-state
restore. Asked to keep or promote the prototype code after PROCEED: decline and point at that
Decisions line; `git show <sha>:<path>` still has the code.

## Vertical slice (after PROCEED)

The next step before building content: one level or one full loop at shipping quality, 3-5 minutes of play. Cut
scope, never quality. It goes through `gamekit:pipeline` as an L card.

It passes on the DESIGN.md Playtests first-playable criteria, plus two, each a yes:

- The core mechanic still feels good, by the player's word, with real art, sound and juice (`game-feel`).
- It holds the frame target on the weakest target device (`unity-performance`).

Any KILL condition above still applies.
