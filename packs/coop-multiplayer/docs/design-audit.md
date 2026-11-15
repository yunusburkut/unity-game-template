# Design audit

__GAME__ as it stands against the design corpus (`docs/design-corpus/`). The pack ships this file empty; the first
audit (`coop-chaos-design`, `mechanic-forge` or `gamekit:level-beat-review` measuring the built game) fills it. It
records facts about this game only: decisions stay in DESIGN.md, the method stays in the corpus.

## Format

- One row per finding, IDs `DA-01`, `DA-02`, … Numbers are stable: a new row gets the next number, a fixed or
  dropped row keeps its number and says so in **Status**.
- Each audit adds a dated section on top (`## YYYY-MM-DD: <what was audited>`); older sections stay as they were.
- **Corpus** cites the rows the finding is measured against by ID (DC, AG, P, RC, FP …), never restates them.
- **Evidence** is a file and line, a scene and object, or a Play Mode observation with its date.
- **Status** is one of `open`, `fixed (<commit or date>)`, `accepted exception (<why, who decided>)`, `retired`.
  An accepted exception is a user decision; record it in DESIGN.md too.

| ID | Finding | Corpus | Evidence | Status |
|---|---|---|---|---|
