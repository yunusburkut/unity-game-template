# Difficulty rhythm: rules, evidence and the critique procedure

`SKILL.md` is the short version. This file holds the rules with their thresholds (DR01–DR28), the relief palette and
the full critique procedure with its scales and Turkish report template. The IDs are local to this skill and stable:
cite them in reviews, append new ones, never renumber. This file is the canonical, game-agnostic DR catalogue.

**Same IDs, different catalogue.** A game made with the coop-multiplayer pack also has `docs/difficulty-rhythm.md`,
the game-specific research doc this file was distilled from (§D). It uses the same DR01–DR28 numbers, but several rules
and thresholds differ (for example its DR16 is report-only and its DR24 is a refuge rule). In such a game, write this
file's rules as `LBR-DRxx` and that doc's as `doc-DRxx`, never a bare `DRxx`, and never mix one catalogue's ID with the
other's threshold. Where the game doc is stricter or decided for that game, it wins as a `DESIGN.md`-level override:
cite both IDs.

Values marked *(start)* are starting values, not findings: tune them in Play Mode and write the result into
`DESIGN.md`. Source keys in square brackets resolve in §D.

## Contents

- §A Why a sawtooth
- §B DR rules (28)
- §C Critique procedure
- §D Source keys

---

## A. Why a sawtooth

- Flow theory and its game applications agree that challenge has to rise with skill, but a steadily rising line
  leaves no room to consolidate; players need moments of mastery between the climbs [Schell, Hodent].
- Interest curves in level design rise in waves: a hook, then alternating tension and release, a climax near the end
  [Schell].
- Playtest-driven studios pace with deliberate valleys after intense set pieces, so the next peak can land [Valve14,
  Booth09].
- Nintendo's four-step teach (introduce, develop, twist, conclude) is the standard shape of one tooth [Hayashida12].
- Failure that is fast to retry and clearly the player's own is tolerated and even enjoyed; failure that costs time or
  feels arbitrary is not [Juul09, Juul10].
- How people remember an episode is weighted by its peak and its end, not its average [Kahneman93]: design the peak and
  the exit of every unit on purpose.
- Tutorials that teach by doing, once, in a safe space, beat text and repeated prompts [Hodent, Linehan14].

The direction (waves, valleys, short retry, peak and end) is well supported. The magnitudes below are starting values.

---

## B. DR rules (28)

### Shape

| ID | Rule | Threshold |
|---|---|---|
| DR01 | **Rising sawtooth at every scale**: beat, segment, act and world each climb, drop, and climb higher. | Three or more consecutive units at the same peak is flat. |
| DR02 | **Rate challenge (C) and stakes (T) separately.** A hard beat that costs little is a different beat from an easy beat that costs a lot. | Every beat carries both a C and a T in the map. |
| DR03 | **One tooth: teach → develop → twist → lap → checkpoint.** The twist is the peak and the only place tier 2 lives; the lap re-uses the mechanic at low stakes (tier 1 only). | A segment with no identifiable twist has no peak. |
| DR04 | **A valley after every peak, asking a different question.** Use the relief palette below. | A valley is ≥ 1 C step below the peak and lasts ≥ 10 s *(start)*. |

**Relief palette** (what a valley can be): a traversal stretch with a view, a toy to play with that cannot fail, a
collectible detour, a short story or reveal, a rest spot with a visible next goal, a comic beat, a reward or unlock, a
quick easy win on a known mechanic.

### New mechanics

| ID | Rule | Threshold |
|---|---|---|
| DR05 | **New mechanics arrive at a valley, alone.** Never under a timer or a chase, never inside a combination, never at a peak. | First contact at C ≤ 2, T ≤ 1. |
| DR06 | **Combine only what was met alone**: A, B, then AB; never A and AB in the same tooth. | A combination needs each part shown solo earlier. |
| DR07 | **Retire a mechanic before it wears out**: after its twist and one combination, it rests or changes. | No mechanic carries the peak of more than ~3 consecutive segments *(start)*. |

### Checkpoints and cost

| ID | Rule | Threshold |
|---|---|---|
| DR08 | **The checkpoint is the first safe ground after the peak**, and nothing after the peak can cost the peak again. | No tier-2 failure between a cleared peak and its checkpoint. |
| DR09 | **Replay to the peak is short.** | Checkpoint (or level start) to the peak ≤ 60 s *(start)* on a clean run. |
| DR10 | **Modes change only knobs**: checkpoint density, timers, hazard speed, hints. No geometry change, no hidden runtime difficulty adjustment without the user's decision. | Every mode plays the same beats in the same order. |

### Ceiling and steps

| ID | Rule | Threshold |
|---|---|---|
| DR11 | **Critical-path ceiling C4.** C5 lives only on optional lines. | No C5 beat a player must clear to finish. |
| DR12 | **Peaks step by at most +1**, and the game starts smooth. | Consecutive segment peaks (or consecutive levels in a pack) differ by ≤ 1 C step; the first two units peak at ≤ C2. |
| DR13 | **Showpieces are rare**, and no two peaks in a row ask the same question. | ≤ 1 showpiece per act *(start)*. |

### Acts and worlds

| ID | Rule | Threshold |
|---|---|---|
| DR14 | **A valley segment between act peaks**, so an act ends and the next one breathes before it climbs. | The first segment of an act peaks ≥ 1 step below the last act's peak. |
| DR15 | **A world opens with a hook below the last finale**: something new to see or play in the first 30 s *(start)*, at low C. | The opening unit of a world peaks below the previous finale. |
| DR16 | **The opening is open**: the first segment of a world offers choice or play, not a gauntlet. | No tier-2 failure in the first ~30 s of a world *(start)*. |
| DR17 | **Set pieces are fixed, use taught moves only, and are followed by low threat.** | A set piece introduces no mechanic; the following unit peaks ≥ 1 step lower. |
| DR18 | **The finale combines everything learned and ends on a win beat** (peak-end). | The last beat of a world is a success the player causes, not a cutscene. |
| DR19 | **The game ratchets**: each world's opening sits above the previous world's opening. | World openings rise monotonically. |
| DR20 | **Optional lines carry the extra difficulty**: stars, par times, collectibles, harder routes. | The critical path never needs an optional skill. |

### Trolls

A troll is a beat that deliberately subverts an expectation the game itself built (a fake floor, a moving goal, a
reversed rule).

| ID | Rule | Threshold |
|---|---|---|
| DR21 | **A troll is a rationed twist**: it replaces the twist of its tooth, never sits on a teach beat, a C ≥ 4 beat, right after a checkpoint, or on the finale. | — |
| DR22 | **A troll is visible in hindsight, cheap and identical on retry.** The second attempt must be winnable by what the first one taught. | Cost ≤ tier 1 or ≤ 15 s replay *(start)*; no randomised troll. |
| DR23 | **Trolls are scarce.** | ≤ 1 per two segments; none in the first two segments of the game or in a finale. |

### If the game is multiplayer

| ID | Rule | Threshold |
|---|---|---|
| DR24 | **A talk window before every peak**: a few seconds of low threat where players can plan aloud. | ≥ 3–5 s *(start)* of T0 directly before each peak [Depping17]. |
| DR25 | **Pace for the most stressed player, and every role wins a beat.** | No player is the only one at C ≥ 3 for a whole segment; each role is the hero of at least one beat per act. |
| DR26 | **Blame stays a joke**: failures are attributable, cheap and funny, never a lecture. | A teammate-caused failure is tier 1, or its replay ≤ 15 s *(start)*. |
| DR27 | **Partner sabotage windows are designed, not accidental**: where one player can hurt the other, the victim can see it coming and recover. | Telegraph > 240 ms; recovery tier 1. |
| DR28 | **Rate at the minimum and the maximum player count.** A beat can be a C2 at two players and a C4 at four. | The map has a C column per supported player count. |

---

## C. Critique procedure

Use for "bölümü yorumla", a level order, or a level pack. Read-only: never edit a scene or asset during a critique.

### C.1 Evidence tags

Every value in the map carries one tag:

- **M** measured: timed in Play Mode, a recording, or a playtest log.
- **D** documented: written in `DESIGN.md` (`## Levels`) or read from scene/level data (`unity-editor-cli`, read-only).
- **E** estimated: inferred by the reviewer. Every E names the measurement that would replace it.

### C.2 Scales

**Challenge C1–C5** (a beat's demand on a first-time player who has learned what came before):

| C | Meaning |
|---|---|
| C1 | Cannot fail, or failure is obviously avoidable |
| C2 | One action under mild timing or one simple choice |
| C3 | Two actions in sequence, or a tight window, or a choice with a trap |
| C4 | A combination under pressure; most first-timers fail once |
| C5 | Expert: multiple tight windows or a deep chain; optional lines only (DR11) |

**Proxy rule for an unmeasured C** (tag E): start at C1 and add one for each that holds:
(a) the window is under ~500 ms *(start)*; (b) two or more mechanics are needed at once; (c) a failure is not
visible before commitment; (d) a loss engine is running (timer, chase, limited moves). Cap at C5.

These terms fit real-time beats. For the other unit columns of `SKILL.md`, swap the terms, same start and cap:

- **Level-based puzzle** (a beat is one decision or move): add one for each that holds: (a) three or more rules
  interact in the solution; (b) the solution chain is longer than ~4 moves *(start)* before feedback confirms it is
  right; (c) a red herring, a move that looks right and dead-ends, is present; (d) a loss engine is running (move limit,
  timer). Window (ms) is "—" unless the puzzle is timed.
- **Run-based** (a beat is one encounter): rate the encounter as drawn, then add one if it can be drawn from the pool
  before the run has offered the tools that counter it, and one if the player's resources at that point of a typical
  run are below the encounter's intended margin. Rate the run's curve from the pool's weighting per floor, not one seed.

**Which rules apply per unit column**: all DR rules apply to platformer / action. Level-based puzzle: DR08 (the
checkpoint is the level start or an undo) and DR09 (replay to the peak is the instant restart plus the moves before the
failed one) apply as stated; DR24's talk window applies only to timed puzzles. Run-based: DR08, DR09 and DR19 do not
apply as written (the run is the unit and a loss ends it); judge instead run length *(start: the game's target run in
`DESIGN.md`)*, the time from death to the next meaningful choice in a new run, and whether meta-progression raises the
floor of the next run. Name the substitute in the finding.

**Stakes T0–T3** (what a failure costs):

| T | Meaning |
|---|---|
| T0 | Nothing; cannot fail |
| T1 | Tier 1: recovered in place, next decision within 3–8 s |
| T2 | Tier 2: back to the checkpoint, ≤ 60 s replay |
| T3 | Tier 2 with more than 60 s replay, or a lost resource that persists |

### C.3 Intensity map

One row per beat:

| # | Role (teach / develop / twist / lap / valley / set piece / troll / finale) | Question the beat asks | C | T | Pressure (loss engine) | Novelty (new / known / combo) | Window (ms) | Visible before commitment? | Relief after | Checkpoint after? |
|---|---|---|---|---|---|---|---|---|---|---|

Multiplayer adds one C column per supported player count (DR28) and a "who acts" column.

### C.4 Curve

One glyph per segment, its peak C: `▁` C1, `▂` C2, `▃` C3, `▄` C4, `▅` C5. Put `‖` after the tutorial and `|` at act
edges. Example: `▁▂ ‖ ▂▃▂▃▄ | ▂▃▄▃▄`.

### C.5 Checks

| Check | Rules |
|---|---|
| Is there a sawtooth, or a flat line or a wall? | DR01, DR04, DR12 |
| Does every segment have one identifiable twist and a lap? | DR03 |
| Where does each mechanic first appear, and at what C and T? | DR05, DR06 |
| Is any mechanic carrying too many peaks? | DR07 |
| Where are the checkpoints relative to the peaks, and how long is the replay? | DR08, DR09 |
| What is the ceiling on the critical path? | DR11, DR20 |
| Do acts and worlds open low and end on a win? | DR14–DR19 |
| Are trolls rationed, visible and cheap? | DR21–DR23 |
| Multiplayer: talk windows, roles, blame, sabotage, player counts | DR24–DR28 |

### C.6 Severities

| Severity | Meaning |
|---|---|
| **Engelleyici** | Players will quit here, or the level cannot be finished |
| **Büyük** | A rule broken in a way playtesters will feel |
| **Küçük** | A rule bent; noticeable on replay |
| **Ayar** | A number to tune, structure is fine |
| **Karar** | A design choice only the user can make |
| **Ölç** | Cannot judge without a measurement; names the measurement |

### C.7 Turkish report template

```
## Bölüm yorumu: <bölüm / paket adı>

**Durum:** geçici (E ağırlıklı) | ölçülmüş (M ağırlıklı)
**Eğri:** ▁▂ ‖ ▂▃▂▃▄ | ...

### Bulgular (en fazla 7, önem sırasıyla)
1. **<Önem>** — <vuruş #> — <ne yanlış, tek cümle> (<DRxx>, <M/D/E>)
   Öneri: <tek somut değişiklik>
   Geri çekilir eğer: <hangi ölçüm bu bulguyu düşürür>

### Kararlar (kullanıcının)
- <seçenek A> / <seçenek B> — <her birinin bedeli, tek satır>

### Ölçülecekler
- <ölçüm> — <nasıl: Play Mode, kayıt, oyun testi>
```

No single numeric score. Every **Karar** goes to the user.

---

## D. Source keys

Checked against the research doc this was distilled from (`packs/coop-multiplayer/docs/difficulty-rhythm.md` in the
template repo, `docs/difficulty-rhythm.md` in a coop game, keeps the full table; its DR IDs are a separate catalogue, see
the top of this file):

| Key | Source |
|---|---|
| Linehan14 | Linehan, Bellord, Kirman, Morford, Roche, "Learning Curves", CHI PLAY 2014 |
| Gutwin16 | Gutwin et al., "Peak-End Effects on Player Experience in Casual Games", CHI 2016 |
| Kahneman93 | Kahneman, Fredrickson, Schreiber, Redelmeier, "When More Pain Is Preferred to Less: Adding a Better End", *Psychological Science* 4(6), 1993 |
| Finn10 | B. Finn, "Ending on a high note", *JEP: LMC* 36(6), 2010 |
| Juul09 | J. Juul, "Fear of Failing?", *The Video Game Theory Reader 2* (2009) |
| Juul10 | J. Juul, "In Search of Lost Time", FDG 2010 |
| Allart17 | Allart et al., "Difficulty Influence on Motivation over Time…", FDG 2017 (correlational) |
| Roohi20 | Roohi et al., "Predicting Game Difficulty and Churn Without Players", CHI PLAY 2020 (correlational) |
| Depping17 | Depping and Mandryk, CHI PLAY 2017 |

Not in that doc, added as general background; verify before citing:

| Key | Source |
|---|---|
| Schell | Jesse Schell, *The Art of Game Design: A Book of Lenses*: interest curves, flow |
| Hodent | Celia Hodent, *The Gamer's Brain* (2017): learning, attention, onboarding |
| Valve14 | Valve developer commentary (Half-Life 2, Portal series): pacing, teaching through level design |
| Booth09 | Michael Booth, "The AI Systems of Left 4 Dead" (2009): pacing by intensity, relax phases |
| Hayashida12 | Koichi Hayashida on Super Mario 3D Land level design (2012): the four-step teach |

When a claim matters to a decision, verify the source before citing it to the user.
