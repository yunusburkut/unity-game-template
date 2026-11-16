---
name: game-ideas
description: What to add to a game ("ne ekleyebiliriz", "fikir ver", "pazarda ne tutuyor"): genre-proven, cross-genre and out-of-the-box mechanics fitted to DESIGN.md as ranked cards. Batch with web: idea-scout.
argument-hint: "[odak: mekanik | ilerleme | sosyal | meta | ekonomi]"
---

# Game ideas: what to add, fitted to this game

The game has a first idea or a DESIGN.md, and the user asks what could go into it. This skill turns that into a short,
ranked list of idea cards the user can pick from. It talks in the main conversation: ask, propose, refine.

Not this skill:

- A game concept from nothing: `gamekit:new-game` (shaping), which offers three starts for a thin idea.
- A verdict on one mechanic already chosen: the `gamekit:design-critic` agent, Mechanic mode.
- Whether an idea is fun: `gamekit:prototype`, with the card's first test.
- A batch of N ideas or a market sweep with web evidence: run the `gamekit:idea-scout` agent with the focus and N.
  It follows steps 1-4 below in its own context; bring its cards back to step 5 here.

## 1 Read the game

1. `DESIGN.md`: Pillars and anti-pillars, Rules (as built), Platforms, Decisions, Open questions. A Decisions line
   that rejected an idea keeps it rejected unless the user brings new evidence.
2. `PLAN.md` Next: an idea already queued is not proposed again. `CLAUDE.md`: genre and targets.
3. The genre sheet: `${CLAUDE_PLUGIN_ROOT}/skills/genre-defaults/references/` holds one file per genre; read the
   game's genre file, and `${CLAUDE_PLUGIN_ROOT}/skills/genre-defaults/references/mashups.md` when two genres join.
4. Write the core loop in one line, then name the weakest of the three loops: the ~30 s action loop, the 5-15 min
   goal-reward loop, or the session loop with its reason to return. Ideas aim at the weakest loop first, unless the
   user names a focus (the argument).

No DESIGN.md and no first idea: this is a concept from nothing; hand over to `gamekit:new-game`.

## 2 Three lanes

An idea list from one lane is the obvious list. Generate at least two candidates in each lane before filtering:

| Lane | What it is | Shape of a candidate |
|---|---|---|
| **A. Türde kanıtlı** | What the genre's best sellers share, or what a recent hit in the genre added that players now expect | "Survivors-likes let two maxed items merge into one evolved item" |
| **B. Türler arası** | A mechanic that carried another genre, moved by its function (what it does to the loop), not by its look | "A deckbuilder's card removal becomes our upgrade shop's sell-back: thinning the build is a choice" |
| **C. Kutu dışı** | A rule bent on purpose: invert the core verb, hand the player the enemy's tool, make failure a resource, an asynchronous trace of other players, a constraint sold as a feature | "Every death leaves a ghost the next run can use" |

Borrow the function, never a game's name, characters, art, levels or text. A reference game is evidence, not a
target.

## 3 Filter: fit before fun

Run each candidate through these gates in order. A failed gate drops it; the report lists drops in one line each.

0. **Pillar:** it serves a named pillar and breaks no anti-pillar.
1. **Verb:** it uses the existing verb and input. A new input costs more on a phone; say so.
2. **Loop:** it strengthens a named loop (action, goal-reward, session, return), ideally the weakest one.
3. **Targets:** it works by pointer (touch and mouse), inside the safe area, at the phone frame rate
   (`gamekit:platform-targets`).
4. **Scope:** an S, M or L in spec-card terms, with the systems it implies (a crafting idea implies item data,
   recipes, UI and save). An L in a small game needs the user's explicit yes.
5. **Evidence:** a lane A or B idea names where it worked and what it did there. A market claim (sales, retention,
   "trending", a store tag's share) needs a web source with its date; with no web, write
   `kanıt: tasarım akıl yürütmesi` and never quote a market number from memory.

## 4 The idea card

Five to seven cards survive. Rank them by value to the weakest loop against cost. Show the top five (ADHD rules);
the rest on request. Each card, in Turkish:

```markdown
### 1. <Ad> — <tek cümlelik kanca>
**Şerit:** A Türde kanıtlı | B Türler arası | C Kutu dışı
**Nereden:** <hangi oyun(lar)da, orada ne işe yaradı> (kaynak: <url>, <tarih> | tasarım akıl yürütmesi)
**Bizim oyunda:** <oyuncunun yaptığı şey, 2-3 cümle>
**Güçlendirdiği:** <pillar> · <döngü>
**Maliyet:** S | M | L · <ima ettiği sistemler>
**Risk:** <yanlışsa fikri öldüren varsayım>
**İlk test:** If the player <does X>, they will feel <Y>; we know it if <observable signal Z>.
```

Close with one line: the top pick and why, then the drops (`Elenenler: <ad> (kapı 0: anti-pillar ...)`).

## 5 Hand off

The user picks. Each pick goes to exactly one place:

| The pick | Goes to |
|---|---|
| Fun or feel is the open question | `gamekit:prototype`, with the card's first-test line as its question |
| Wanted, and how it feels is known | A PLAN.md Next line, `fikir: <Ad> — <kanca> (S|M|L)`; when it reaches Now, `gamekit:pipeline` phase 1 writes its spec card |
| A mechanic to judge before building | The `gamekit:design-critic` agent, Mechanic mode |
| It changes a pillar or a rule | A DESIGN.md Decisions line, after the user's yes |
| Rejected | A DESIGN.md Decisions line `YYYY-MM-DD: Fikir <Ad> reddedildi. <Why>.`, so it is not proposed again |

PLAN.md Next holds at most 5 items; past that, ask which one the new idea replaces. This skill writes no game code and
never edits DESIGN.md Pillars without the user's yes.
