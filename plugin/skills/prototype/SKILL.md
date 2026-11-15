---
name: prototype
description: Answering one design question in throwaway code before building the feature - a falsifiable question, a timebox, the PROCEED / PIVOT / KILL verdict, then deleting the code. Use when the question is "would X feel good or be fun?" rather than "build X" ("prototip", "prototipini yap", "hissettiriyor mu", "eğlenceli mi", "spike"). Not for "does this existing code work?", which is a bug or a check.
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
- Feel, timing or physics is the question: a Unity scene. Logic, economy, cards, idle or strategy maths: a table or a
  spreadsheet first; it is often enough.

## 2 Timebox

- One mechanic, one sitting (about 2-4 h), at most one day.
- Not playable after about 2 h of iteration: stop. Make the question smaller or switch approach; never push on.
- Build only what the question needs: no menus, saves, music, game over, juice or UI unless that is the question.

## 3 Where it lives

`Assets/<Game>/Prototypes/<Name>/` with its own asmdef (`<Game>.Prototypes.<Name>`), and its own scene there.

- It may reference `<Game>.Core`. `<Game>.Game`, Core and the test assemblies never reference it.
- Each file starts with `// PROTOTYPE - NOT FOR PRODUCTION`, `// Question: <the sentence>`, `// Date: YYYY-MM-DD`.
- Commit it to main like any work: git is the archive.

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
tester. A network-feel question is never answered locally, and a performance question needs a number on the weakest
target device.

## 5 Record and delete

One DESIGN.md Decisions line, then delete the prototype folder (with its `.meta` files) in the same commit:

`YYYY-MM-DD: prototype <Name>: KILL. <evidence: what was seen>. Worked: <x>. Failed: <y>. Next time: <z>.`

(PROCEED or PIVOT in place of KILL; a PIVOT keeps the folder until the next verdict, and a later verdict on the same
prototype edits its line, the old text kept as `was: ...`. NOT ASSESSED writes no line and keeps the folder; the
verdict waits until someone plays it.) Until the folder is deleted, PLAN.md Now holds one line, `prototype <Name>:
<the question>`, so `devam` finds it. A play session the user reports is logged under DESIGN.md
Playtests first (CLAUDE.md); the Decisions line points to it. Asked to keep or promote the prototype code after
PROCEED: decline and point at that Decisions line; `git show <sha>:<path>` still has the code.

## Vertical slice (after PROCEED)

The next step before building content: one level or one full loop at shipping quality, 3-5 minutes of play. Cut
scope, never quality. It goes through `gamekit:pipeline` as an L card.

It passes on the DESIGN.md Playtests first-playable criteria, plus two, each a yes:

- The core mechanic still feels good, by the player's word, with real art, sound and juice (`game-feel`).
- It holds the frame target on the weakest target device (`unity-performance`).

Any KILL condition above still applies.
