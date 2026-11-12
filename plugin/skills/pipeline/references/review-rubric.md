# Review rubric (scored out of 10)

Used by every gamekit reviewer when the prompt asks for a score. The reviewer scores; it never edits.

## Score

Start at 10 and subtract. The floor is 0.

| Finding | Points |
|---|---|
| **[yüksek]** a bug (wrong result, crash, data loss, softlock), broken on one target (PC, phone, WebGL), a compile error, a Core/Game boundary break, a gate claimed as passed that did not pass | -3 each |
| **[orta]** a lifecycle risk (`OnEnable`/`OnDisable` asymmetry, an un-reset static), a per-frame allocation on a hot path, an android/ios branch that no Verified line in the range checks (neither `compile <p> PASS` nor `compile <p> unverified (<reason>)`), complexity the next change will trip on | -1 each |
| **[düşük]** naming, a clearer form of the same code | 0 (listed, free) |
| A branch no gate could check, disclosed on a Verified line in the range: WebGL or PC-player-only (`unverified: WebGL` / `unverified: PC player`), android/ios whose compile answered UNKNOWN (`compile <p> unverified (<reason>)`, unless a later line has `compile <p> PASS`); an Inspector/scene step the diff needs (list it under `Inspector/sahne`) | 0 (they go to Pending Play Mode checks) |
| An acceptance item of the spec card not done (the code for it is missing): list it as **[yüksek]** | -3 each |
| An acceptance item ticked without evidence on its line, or with evidence that cannot show it (a compile pass for a behaviour): list it as **[orta]** | -1 each |
| An acceptance item left unticked because its check failed: **[yüksek]**; because its check could not run (and it is not `Play Mode (user)`): **[orta]** | -3 / -1 each |
| An acceptance item whose evidence is `Play Mode (user)`, unticked and listed under Pending Play Mode checks | 0 (count it as pending) |
| An unknown gate (`gk-bridge` exit 2, refresh or compile) not disclosed as unverified | -3 (disclosed: 0) |

Pass = 9 or more: no **[yüksek]**, at most one **[orta]**. The score is exactly this arithmetic on the listed findings.

Reviewers with their own tags map them: a player-facing string that is wrong on a device ("click" on a phone) or an
**Engelleyici** = **[yüksek]**; a failed clarity rule or a **Büyük** = **[orta]**; **Küçük** and **Ayar** =
**[düşük]**. **Karar** (the user's call) and **Ölç** (needs a playtest) are listed as **[karar]**: 0 points, they go
to the user, so their `düzeltme:` names the options and the cost of each, or the playtest to run.

## Rules

- Every finding points at a line: `dosya:satır` or a quoted line. No line, no finding, no points.
- Judge the change against the spec card and the repo's rules (`CLAUDE.md`), not your taste. Matching the
  surrounding code is never a finding.
- A disputed finding (the note gives `dosya:satır` evidence) is re-judged: keep it only if the code
  still shows the problem, and say why in one line.
- Unsure whether something breaks: write the probe that would decide it, score it **[orta]**, not **[yüksek]**.

## Output (Turkish, first in the report)

```
Puan: 6/10
Kapsam: <commit range or files>, <spec card goal>
Kabul: 3/4 kanıtlı, 1 Play Mode'da (eksik: <item> | yok)
Bulgular:
- [yüksek] Game/Ball.cs:41 - <what> - <the input or state that breaks it> - düzeltme: <one line>
- [orta] ...
Inspector/sahne: <steps the diff needs, or "yok">
Önceden: <problems older than the range, unscored, or "yok">
```
