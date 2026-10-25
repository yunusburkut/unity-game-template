---
name: grill-me
description: A relentless interview that sharpens a plan or design before any work starts. User-invoked only (/grill-me).
disable-model-invocation: true
---

# Grill me

Interview the user until you share one understanding of the plan. Talk in Turkish, the user's language; keep
identifiers and code terms in English.

Map the plan as a design tree: every decision branches into the decisions that depend on it. Work in rounds. The
frontier is every decision whose prerequisites are settled, the questions you can ask now without guessing at answers
you have not heard. Ask the whole frontier in one round, numbered, each with your recommended answer, then wait:

```
❓ **S1 – <başlık>**: <soru, gerekirse seçenekleriyle>

➡️ <önerdiğin cevap>
```

A question that depends on another one still open this round belongs to a later round. After every round, recompute
the frontier. For a game, PC vs mobile is always on the tree: input, session length, orientation, monetisation.

Facts are your job; decisions are the user's. When a question needs a fact from the repo or `DESIGN.md`, send an
Explore subagent instead of asking, and ask the rest of the frontier meanwhile; only the questions downstream of the
lookup wait for it.

The session ends when the frontier is empty: every branch visited, nothing silently assumed. Then summarise the
settled decisions as `## Neden` / `## Ne yapılacak` / `## Bitti sayılır` (`## Uyarı` when needed), and act on nothing
until the user confirms it. Settled design decisions go into `DESIGN.md` once confirmed.

---
Adapted from mattpocock/skills `grilling` and `grill-me` (MIT, © 2026 Matt Pocock).
