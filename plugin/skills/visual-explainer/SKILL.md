---
name: visual-explainer
description: Use when asked "açıkla", "anlat", "nasıl çalışıyor", "adım adım göster", "mimarisini çiz", "walk me through", or when Visual Clarity picks VISUAL EXPLAINER. Deep Turkish explanation of a Unity/C# system, algorithm or data flow, with a diagram.
---

# Visual explainer

The procedure for the VISUAL EXPLAINER level of the Visual Clarity output style. Without that style active, still
apply its language rules: Turkish prose, English code terms, one topic per sentence, active voice, one term for one
thing, concrete values, no idioms.

## 1. Read before you draw

Explain the real code, not a textbook version. Find the types, files and call order first (Grep/Read, or the
`gamekit:scout` agent for a wide search). A concept question with no code in the project gets the generic shape;
say so in one line.

## 2. Sections, in order

Keep a section only when it has content.

| Section | Content | Size |
|---|---|---|
| `### Büyük resim` | What it is and the problem it solves, in plain Turkish; one `Benzetme:` line only if the concept is new to a senior Unity developer | 2-3 sentences |
| `### Görsel model` | One diagram (pick the type below) | ≤12 nodes |
| `### Nasıl çalışır` | Numbered steps in execution order; an algorithm gets the state table in 4 | 3-8 steps |
| `### Uygulama` | The key code: signatures and the lines that matter, with file links | ≤30 lines of code |
| `### Kararlar` | Table: choice, alternative, why this one | ≤5 rows |
| `### Performans` | GC, CPU, memory, draw calls; every line labeled **Ölçüldü** or **Teorik** | ≤5 lines |
| `### Çıkarımlar` | What to remember or reuse | ≤3 bullets |

## 3. Pick the diagram

| The question is about | Mermaid | ASCII fallback |
|---|---|---|
| Who calls whom, ownership, asmdef references | `flowchart LR` | boxes with `-->` |
| Order of calls or events over time | `sequenceDiagram` | numbered arrows, one per line |
| Lifecycle (pooled object, game state, UI screen) | `stateDiagram-v2` | `[State] --event--> [State]` |
| Grid, graph or search order | No Mermaid: an ASCII grid with step numbers | the same |

Mermaid when the system prompt says you run in the Claude desktop app or an IDE extension, or when the output is a
Markdown file or artifact. Otherwise ASCII in a `text` block. Labels are short English identifiers or 1-3 Turkish
words. No styling, no colours: the host theme decides them.

## 4. Patterns

**Architecture** (object pool, service, event bus): diagram the owners and the data flow; the steps follow one object
or one message through its whole life; Kararlar compares with the obvious alternative (`Instantiate`/`Destroy`,
singleton, direct reference). Mention the Data / Logic / View split and asmdef boundaries only where the code has them.

**Algorithm** (BFS, A*, flood fill, sorting): a small concrete input (a 4x4 grid or 6 nodes), then a state table, one
row per iteration:

| Adım | Kuyruktan çıkan | Eklenenler | Kuyruk | Ziyaret edilen |
|---|---|---|---|---|

Then complexity in O-notation with what `V` and `E` are here, and the Unity hot-path costs (a `new Queue` per call,
`HashSet` vs a `bool[]`, `Vector2Int` keys).

**Event-driven** (C# `event`, `UnityEvent`, a ScriptableObject channel): a `sequenceDiagram` from publisher to
subscribers; steps cover subscribe (`OnEnable`), raise, unsubscribe (`OnDisable`); Kararlar names the leak risk of a
missing unsubscribe and the delegate allocation on subscribe.

**Multi-file change**: a `flowchart` of the touched modules with new parts marked `(yeni)`; a file table (file,
change, why); Doğrulama as in the output style.

## 5. Check before sending

- The first line answers the question; no preamble.
- The diagram matches the code you read: same type names, same direction of calls.
- Every number has a source in this session, or the line is labeled **Teorik** and has no number.
- Nothing says tested, measured or working that did not run.
