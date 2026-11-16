---
name: visual-explainer
description: Use when asked "nasıl çalışıyor", "adım adım göster", "mimarisini çiz", "walk me through", or "açıkla"/"anlat" about a system, algorithm or data flow of 3+ parts, or when Visual Clarity picks VISUAL EXPLAINER.
---

# Visual explainer

The procedure for the VISUAL EXPLAINER level of the Visual Clarity output style
([visual-clarity.md](../../output-styles/visual-clarity.md), the single source of its Language and Visual rules).
Without that style active, read those two sections there and apply them; in short: Turkish prose, English code
terms, one topic per sentence, active voice, one term for one thing, concrete values, no idioms.

## 1. Read before you draw

Explain the real code, not a textbook version. Find the types, files and call order first (Grep/Read, or the
`gamekit:scout` agent for a wide search). A concept question with no code in the project gets the generic shape;
say so in one line.

## 2. Sections, in order

A question about one line, one error message or one member is not this level: answer it in 2-5 sentences without
these sections. Otherwise keep a section only when it has content.

| Section | Content | Size |
|---|---|---|
| `### Büyük resim` | What it is and the problem it solves, in plain Turkish; one `Benzetme:` line only if the concept is new to a senior Unity developer | 2-3 sentences |
| `### Görsel model` | One diagram (pick the type below) | ≤12 nodes |
| `### Nasıl çalışır` | Numbered steps in execution order; a longer flow is split into named phases of at most 5 steps each (ADHD mode allows 5 visible items per group); an algorithm gets the state table in 4 | 3-5 steps per group |
| `### Uygulama` | The key code: signatures and the lines that matter, with file links | ≤30 lines of code |
| `### Kararlar` | Table: choice, alternative, why this one | ≤5 rows |
| `### Performans` | GC, CPU, memory, draw calls; every line labeled **Ölçüldü** or **Teorik** | ≤5 lines |
| `### Çıkarımlar` | What to remember or reuse | ≤3 bullets |
| `### Doğrulama` | Only when the answer reports a change: only what ran in this session, each with its command and result; what did not run goes under **Doğrulanmadı** with the reason | ≤5 lines |

## 3. Pick the diagram

| The question is about | Mermaid | ASCII fallback |
|---|---|---|
| Who calls whom, ownership, asmdef references | `flowchart LR` | boxes with `-->` |
| Order of calls or events over time | `sequenceDiagram` | numbered arrows, one per line |
| Lifecycle (pooled object, game state, UI screen) | `stateDiagram-v2` | `[State] --event--> [State]` |
| Grid, graph or search order | No Mermaid: an ASCII grid with step numbers | the same |

Mermaid or the ASCII fallback follows the host rule in the style's Visual rules (which hosts render Mermaid and
their signals live only there). When neither the style nor that file can be read, use ASCII in a `text` block: a
terminal shows Mermaid source as raw text. Labels are short English identifiers or 1-3 Turkish words. No styling, no
colours: the host theme decides them.

## 4. Patterns

**Architecture** (object pool, service, event bus): diagram the owners and the data flow; the steps follow one object
or one message through its whole life; Kararlar compares with the obvious alternative (`Instantiate`/`Destroy`,
singleton, direct reference). Mention the Data / Logic / View split and asmdef boundaries only where the code has them.

**Algorithm** (BFS, A*, flood fill, sorting): a small concrete input that keeps the trace within the style's 8-row
table cap (a 3x3 grid, a 4x4 grid with walls, 6 nodes or 6 array items), then a state table, one row per iteration.
A longer run is split into named phases of at most 8 rows each, never cut. Pick the header by algorithm:

| Algorithm | Header |
|---|---|
| BFS, flood fill | `Adım \| Kuyruktan çıkan \| Eklenenler \| Kuyruk \| Ziyaret edilen` |
| A* | `Adım \| Çıkan (f) \| Komşular g/h \| Open set \| Closed` |
| Sorting | `Adım \| Karşılaştırma \| Takas \| Dizi` |

Then complexity in O-notation with what `V` and `E` are here, and the Unity hot-path costs (a `new Queue` per call,
`HashSet` vs a `bool[]`, `Vector2Int` keys).

**Event-driven** (C# `event`, `UnityEvent`, a ScriptableObject channel): a `sequenceDiagram` from publisher to
subscribers; steps cover subscribe (`OnEnable`), raise, unsubscribe (`OnDisable`); Kararlar names the leak risk of a
missing unsubscribe and the delegate allocation on subscribe.

**New system from a change** (a change that adds 3+ interacting parts; a plain multi-file change is the style's
STANDARD level): a `flowchart` of the touched modules with new parts marked `(yeni)`; under Uygulama a file table
(file, change, why); `### Doğrulama` last, as in section 2.

## 5. Check before sending

- The first line follows the style's Other instructions: the reader's action first when ADHD mode is on and one is
  left (the answer right under it), otherwise the answer; no preamble.
- The diagram matches the code you read: same type names, same direction of calls.
- Every number has a source in this session, or the line is labeled **Teorik** and has no number.
- Nothing says tested, measured or working that did not run.
- The last line is one concrete next action when one exists (what to open, run or try); no closing recap.
