# Difficulty rhythm

**Status:** draft, revision 2, 2026-10-01. This is a research and method doc, written in English. Decisions stay with `docs/gdd.md` and the user (`docs/design-corpus/README.md:42-54`). Where this doc disagrees with a decision, it proposes a change in §E and does not override the decision.

**Rule IDs.** The rules are **DR01–DR28**. The DR prefix is not used anywhere else in the repo. Catalogs are appended to and never renumbered. DR16 is open and DR20 is frozen, but both keep their IDs.

**Tags on numbers**

| Tag | Meaning |
|---|---|
| `(src: KEY)` | The number comes from a verified source in §D, for a unit comparable to the one it is used on. |
| `(repo: file:line)` | A decided repo rule or a measured repo value. |
| `(repo-start: file:line)` | A starting value already in a repo doc. |
| `(start)` | A new starting value. Tune it in Play Mode, then write the measured value back here. |
| `(start, after KEY)` | A starting value informed by a source whose unit differs from ours, for example a Mario stage or an L4D spawn phase. |

When two findings have the same severity, the ranking is `src` > `repo` > `repo-start` = `start` (§C.6).

**Short names for repo files**

| Short name | File |
|---|---|
| *playbook* | `docs/level-design-playbook.md` |
| *LBR* | `~/.claude/skills/level-beat-review/SKILL.md` |
| *GDD* | `docs/gdd.md` |
| *B1 beats* | `docs/bolum-01-beats.md` |
| *B3 beats* | `docs/bolum-03-beats.md` |
| *README* | `docs/design-corpus/README.md` |
| *coop* | `docs/coop-mechanics-playbook.md` |

**Group size.** Mixtrol is for 2–4 players, and content is built for 2 first (GDD:157-160). "The group" below means everyone playing. The rules that change with the player count are in DR28.

---

## A. The answer: do these games give an easier obstacle after a hard one?

**It depends on who you ask. The games you named are the weakest evidence.**

### The games you named: no documented rule

No developer of Chained Together, Carry The Glass or Bread & Fred has explained their obstacle order. What exists is:
- press descriptions and guides;
- Steam achievement funnels, which mix difficulty with players stopping for the day and with content added later;
- one designer FAQ for the troll games.

Game by game:

- **Chained Together** changes verb or scenery at zone boundaries: a car ride, a swim, the Subway's open sky, the Temple's exploration, and a victory-lap ride at the end of the Deities (CT-TheGamer).
  - But the zones the press calls breaks lose about as many players as the hard ones: Vault and Aqua Maze 15.2%, Subway 15.3%, Harbor 14.7% (CT-ach, derived and confounded).
  - A two-post Steam thread calls the first act the hardest (CT-threads). TheGamer calls it a warm-up, and says the game ends on its two "brutal" challenges (CT-TheGamer).
- **Carry The Glass** changes checkpoint density between its modes, not obstacle order (CTG-store). Four days after launch it added a checkpoint in front of its falling spike balls (CTG-news).
- **Bread & Fred** puts its hardest stretch, the wind, in the middle, and its attrition sits there too (BF-ach, BF-reviews).
- **Troll games** relieve through the retry itself, which is instant, identical and cheap (HG101). IWBTG's author says that relentless brutal deaths make players stop caring, so they need room to breathe (Kayin).

### The designers who wrote about pacing: yes, a rising sawtooth

Nintendo, Valve and a content analysis of four puzzle games describe the same shape:
- The load climbs inside a unit (a stage, a segment, a zone), peaks, and drops at the unit's boundary.
- The next unit opens below that peak but above the previous opening.
- The drop comes *after* the peak.
- The drop is usually a *different kind* of beat: the next mechanic at its simplest, a change of verb or view, a stretch where nobody can die, or a cheap retry. It is rarely the same obstacle tuned down.

### Research: mixed

- **Shape.** Peaked difficulty curves moved motivation more than flat ones, but the abstract does not say in which direction (RaoFernandes22).
- **Peak and end.** The worst moment and the ending shape how hard the whole game is remembered (Gutwin16). Enjoyment and replay moved in only one of the three games tested. Adding a milder tail made people choose the longer experience (Kahneman93, Finn10).
- **Quitting.** In Ubisoft's data, harder play went with *lower* quitting within a 15–30% failure range, while sharp early swings in Rayman Legends went with more quitting (Allart17). Quitting on hard levels is more common early in a game (Roohi20). Both findings are correlational.
- **Chosen versus assigned difficulty.** Easier versions, when assigned blindly, were played longer. Moderate challenge won only when players chose it (Lomas; an educational math game).

### What Mixtrol takes from each

- From the designers: the sawtooth.
- From the troll games: the cheap, identical retry.
- From the co-op climbers: the checkpoint as the reward for a peak.

### The families side by side

| Family | Easier beat after a hard one? | What the relief is | Where it sits | Evidence |
|---|---|---|---|---|
| **Nintendo-style and puzzle platformers** (Mario 3D Land/World, Celeste, Portal, Braid) | Yes, by design, at every scale | **Stage:** teach, develop, twist, then a run through the learned skills to the goal (Hayashida12, Brown-3DW). **Game:** complexity drops where a new skill arrives in its simplest form, and the drops step upward (Linehan14). **Chapter:** Celeste follows a chase peak with a stretch where you cannot die (*Awake*), and ends with the Epilogue (CelesteWiki). | Right after the peak, at the boundary | Strong: developer statements plus a content analysis |
| **Valve** (Left 4 Dead, Half-Life 2, Portal) | Yes, scheduled | L4D's spawner holds a peak for 3–5 s, then relaxes for 30–45 s (Booth09). HL2 switches activity, and White Forest Inn is a whole map inserted as a break from driving (Valve14). Portal 2 added a funnel ride where testers tired (Portal2-dev). | After every peak. The *frequency* of peaks varies; their height does not | Strong: official talks and commentary |
| **Co-op rage and physics climbers** (Chained Together, Carry The Glass, Bread & Fred, PEAK) | Partly, and only at zone boundaries. The attrition data do not show the breaks working | A change of verb or scenery (CT-TheGamer). A checkpoint moved in front of a spike (CTG-news). PEAK's campfire, which needs everyone present and pauses hunger and fog (PEAK-wiki, PEAK-news). Failure staged as comedy (BF-pentopixels). | Between zones; inside a zone the load mostly rises | Weak: press, guides and confounded funnels |
| **Troll platformers** (IWBTG, Kaizo, Cat Mario, Mario Maker trolls, Level Devil) | No source prescribes it | The cheap retry itself. IWBTG saves about every two rooms on its default setting (src: HG101). Then comes the "now I get it" pass. The hardest parts are those where the traps step back (HG101). "Room to breathe" (Kayin). | Inside the beat, in seconds | Medium: a designer FAQ, analyses and community norms; no data |
| **Research** | Mixed | See above | — | Mixed. The only published relief duration is L4D's spawner phase |

### Where games break the pattern on purpose

- **Getting Over It.** The relief is the bait: a safe-looking moment turns into a fall (Foddy18). Foddy rewrote his narration from goading to mostly encouraging. It is a solo game with no checkpoints, and the repo already notes that it does not transfer (`reference-teardowns.md:105-117`).
- **Trap Adventure 2 and Only Up.** Neither has checkpoints. They spread through clips and streamers' rage-quits. Only Up's developer delisted it, citing stress (TA2-OnlyUp). That they were "watched rather than finished" is an interpretation.
- **Kaizo post-goal traps, and IWBTG's trap right after a hard section.** Here denying relief is the joke. That only works because a death costs seconds (HG101, WilsonSicart10). Mixtrol's rules forbid learning by dying (GDD:219), so this does not transfer (E14).
- **Chained Together's opening act.** Players in a two-post thread call Hell the hardest part. Loss per minute of play, derived from achievements, is highest at the bottom, but survivorship and casual quitters confound that figure (CT-threads, CT-ach). A $4.99 streamer game whose failure is the content may be able to afford an early filter (CT-03 inference; price from indiegame26). Mixtrol teaches one idea per segment and cannot.
- **Bread & Fred's middle and ending.** The midpoint wind makes players wait for gaps while a single fall can cost over 100 m, about a fifth of the climb. One reviewer felt the game tipped there "from unforgiving to broken" and switched on infinite jumps (BF-reviews). The game ends on a troll, the carried letter blowing away, and a handful of recent reviews resent it (BF-ending).
- **Lemmings.** It introduced new obstacles inside puzzles that were already demanding. The authors suggest its age (1991) may explain this (Linehan14).

### Where the evidence is thin

- No study measures how often troll beats should come.
- Valve's White Forest Inn intensity graph exists only as images, so this doc uses none of its values.
- The exact ratios are weak. The only "N build, 1 peak, M rest" cycle comes from a pilot with seven children (Mossmann19). N++'s mix of three easy, one easy-medium and maybe one medium level is stated for an *easy* episode only (Sheppard14).
- Adams indexes a "sawtooth difficulty progression" (Adams-FGD, p. 424), but that page's text was not read.

### The tooth, in one line

`teach (C≤2, no tier-2) → develop → twist (the peak; tier-2 lives here) → lap (tier 1 only) → checkpoint → next teach (below this peak, above this teach)`

Valley segments, set pieces and tower storeys have exceptions (DR03).

---

## B. The Mixtrol difficulty rhythm

### B.0 Terms

#### Units

- **Beat.** One authored moment (playbook:143-155). Its *commit point* is where backing out stops being free (playbook:149-150).
- **Segment (tooth).** Runs from one checkpoint to the next.
  - 45–90 s clean (repo-start: playbook:106) and 3–5 beats (repo-start: playbook:110).
  - In the towers, the tooth is a storey (B2) or a kademe (B3), and the landing is its checkpoint.
- **Tutorial.** A segment with no tier-2 failure, placed before the first device (B1's S0). It sits outside the acts and is exempt from DR05, DR12 and DR15.
- **Act.** See "Acts" at the end of this section.
- **Bölüm.** A chapter. For pacing purposes it is also the "biome" (E8).
- **Finale.** The segment that holds `LevelGoal`.
- **Set piece.** A chase or rising-goo segment (`clk`), or a ride of ≥ 10 s that the group cannot steer (start).
- **Showpiece.** A segment the level doc declares as one. If the doc declares none, only set pieces count.

#### Derived from the scales in §C.2

- **Peak.** The beat with a segment's highest C. On a tie, the later beat.
- **Valley beat.** A beat at C ≤ 2 and T ≤ 1.
- **Valley segment.** A segment whose peak is ≤ C2 and where every beat is at T ≤ 1.
- **Slip.** A failure outside the beat's question: before its commit point, or on an action its clip sentence does not name.

#### Vocabularies (the map uses only these words)

**Tooth role (per beat)**

| Key | Meaning |
|---|---|
| `teach` | A device's first beat, shown alone |
| `develop` | The device in a harder form |
| `twist` | A known device used in a way its teach did not show |
| `lap` | An easy run on what was just learned, ending at the checkpoint |
| `valley` | A low beat (C ≤ 2, T ≤ 1) |
| `set` | A set-piece beat |
| `move` | A tower move |

**Question: what the beat asks.** This is also a beat's "type" for DR04 and DR13.

| Key | Meaning |
|---|---|
| `pw` | Partner-window jump: someone else's Space moves you, on a call |
| `hold` | Hold and release: a plate, pedal, button or seesaw end |
| `cyc` | Count a timed device's cycle |
| `sync` | Everyone at once |
| `carry` | Carry a load |
| `blind` | A blind call (the colour tunnel) |
| `read` | Choose the right path, tile, owner or door |
| `walk` | Nothing to solve: traversal, a ride, a view |

**Device family (of a segment's new device)**

| Key | Members |
|---|---|
| `swap` | The swap core, SwapGate |
| `device` | Carry, plate, door, lever, button, moving platform, crumbling floor, pushable, launch pad, seesaw, pulley, ice, goo ceiling, safety plate, crumbling shelf, eye |
| `obstacle` | The Parkur obstacles and lethal iron (MIX-253): bumper, propeller, hammer, belt, rotating bar, piston, swing, metronome, saws, press, spikes |
| `set` | Chase, rising goo |
| `tunnel` | Colour tunnel |

**Co-op role (per beat)**

| Key | Meaning |
|---|---|
| `jumper` | The body that crosses |
| `presser` | Whose Space moves the jumper |
| `holder` | On a plate, pedal, button or seesaw end |
| `carrier` | Carrying a load |
| `caller` | The tunnel owner calling moves |
| `runner` | Everyone, in a set piece |

**Troll.** A *visible, tempting* break of a rule the level taught earlier (DR21–DR22). Visible hazards are not trolls, and a re-deal is a twist, not a troll.

| Key | Meaning |
|---|---|
| `bait` | A tempting wrong path that costs a walk |
| `bet` | A one-shot betrayal: LBR:152's decoy checkpoint, twin shuttle and bait crate, and any new one-shot |
| `p2p` | A partner's sabotage window (DR27) |

**Other terms**

- **Honest segment.** A segment with no `bait` or `bet`. `p2p` windows are allowed.
- **Designed faller.** The role whose miss the peak's failure is built around: the jumper at a `pw` peak, the crosser under a `hold`.
- **Wins a beat.** A role's own input completes the beat's commit action on a clear.
- **Hook.** The first clip sentence after the tutorial.
- **First third.** The first ⌈n/3⌉ segments after the tutorial, where n is the number of segments after the tutorial. In B1 that is S1–S5.

#### Acts

The level doc declares its acts, either as a `Perde` column in the beat doc or in the segment notes in `LevelNotes.asset`. If it declares none, a fixed rule decides, and the critic never chooses:
1. The tutorial is outside the acts.
2. An act boundary is a checkpoint where the device family of the segment's new device changes.
3. A set piece and the finale after it form one act.
4. A level with ≤ 5 teeth is one act (B3's four kademe).

Acts of 3–5 segments are a starting target (start). A longer act is a Tune finding, not a reason to move the boundary.

### B.1 Shape

**DR01: a rising sawtooth at every scale.**
- *Rule:* every segment, act, Bölüm and the game as a whole climbs to a peak and drops at its boundary. The next unit opens below that peak but above the previous opening. The load is never a flat line and never a pure ramp. The tutorial and valley segments are exempt.
- *Why:*
  - Schell's interest curve: a hook, rising interest punctuated by rests, a finale, and the same shape nested at smaller scales. He calls the cycle tense and release (Schell).
  - Hodent: a straight ramp means players never feel extra challenged or extra competent (Hodent).
  - Koster describes a rising sine wave (Koster25).
  - Stout: if everything is at maximum, the maximum becomes the new normal (Stout15).
  - Linehan: in Portal, Portal 2 co-op and Braid, complexity rises, drops at each new skill, and the drops step upward (Linehan14).
  - Peaked curves moved motivation more than flat ones. This is weak evidence, and the direction was not reported (RaoFernandes22).
- *Thresholds:*
  - no three consecutive segments at the same peak C (start);
  - every segment's opening beat at ≤ C2 (start).

**DR02: rate challenge and stakes separately.**
- *Rule:* challenge (C) is execution and understanding. Stakes (T, Loss) are what failure costs: the tier, the height at risk, a clock. A peak may be high on one and modest on the other, and a valley may lower either.
- *Why:*
  - Intensity is not difficulty (LDB).
  - Portal's fire-pit escape at the end of Test Chamber 19 felt climactic, although Wolpaw called it about the easiest puzzle in the game. It got its weight from time pressure and visual impact (Portal-GDC08).
  - Height stored up raises tension at a constant difficulty (Foddy18).
- *Threshold:* the map (§C) always carries both columns. A finale may carry maximum stakes at ≤ C4 (start).

### B.2 Beat and segment

**DR03: a segment is one tooth: teach → develop → twist (the peak) → lap → checkpoint.**
- *Rule:* every tooth has a twist, and the peak sits on it, not on the last beat. The last beat is an easier mastery run that uses what was just learned and ends at the checkpoint.
- *Exceptions:*
  - (a) A valley segment has no twist and no peak above C2 (DR14).
  - (b) A set piece, or a tower storey or kademe, may end on its peak when the checkpoint or landing is reached ≤ 5 s clean after the commit point (start). The walk onto it is the lap. This matches `level-kit.md:295-296`, where the gap under a storey's last move is left open.
- *Why:*
  - Hayashida uses four steps: learn, a slightly harder version, a twist in the third step, then a show of mastery. A Mario stage lasts minutes, so applying this to a 45–90 s segment is our transfer (Hayashida12).
  - 3D World's Cakewalk Flip peaks at its twist and ends with a run through the learned skills to the flag (Brown-3DW).
  - A milder tail makes the whole experience remembered better and chosen again (Kahneman93, Finn10).
  - A level component "often" pairs an obstacle with a resting spot (RhythmGroups).
  - B1's S7–S11 already open each segment with a harmless teach (B1 beats:46-47).
- *Thresholds:*
  - the four roles spread across 3–5 beats (start, after Hayashida12; beat count repo-start: playbook:110);
  - setup 2–4 s (repo: playbook:146);
  - the peak in the second half of the segment (start);
  - a lap of 5–15 s at T ≤ 1 (start).

**DR04: a valley after every peak, asking a different question.**
- *Rule:* between any two beats at C4 or above there is at least one valley beat. After a segment's peak come the consequence quiet, the lap, the checkpoint, then the next teach. The valley asks a different question from the peak. It is not the same device dialled down straight after its own peak.
- *Why:*
  - Valve relieves fatigue by switching activity (Valve14). It inserted a ride and a whole break map where testers tired (Portal2-dev, Valve14).
  - Relentless deaths make players stop caring (Kayin).
  - A low-intensity stretch after an intense one reads as a reward (LDB).
  - Calm, ordinary play is itself valued (Bopp/Tyack).
  - Novelty can stand in for a dip (GDC17-LD).
- *Thresholds:*
  - at least 1 valley beat between two C4+ beats (start);
  - 2–3 s of consequence quiet (repo-start: playbook:153-155);
  - the valley's question differs from the peak's (start).

**The relief palette.** These keys go in the map's Relief column. Every key keeps the swap as the floor (DR25).

| Key | What it is | Mixtrol form | Evidence |
|---|---|---|---|
| `teach` | The next device alone, with no tier-2 | The first beat of every segment | Linehan14, Valve14, Portal2-dev |
| `easy` | An earlier, mastered device the group now clears easily: "we used to die here" | A callback from at least 2 segments back, never the device of the peak just cleared (start) | Hodent (reference point), CelesteWiki (the Summit revisits earlier chapters' mechanics) |
| `verb` | A change of verb or vehicle, under the swap | The carry, the ice slide (MIX-287), a pulley ride, a launch pad | CT-TheGamer (car ride, swim), Valve14 |
| `vista` | A view or spectacle with no input challenge | A lift or ride that reveals the next act | Valve14, Portal2-dev, CT-TheGamer (the Subway's open sky) |
| `talk` | A regroup spot: everyone safe, no clock | The refuge in DR24 | PEAK-wiki, PEAK-news, Portal2-dev, Depping17 |
| `comedy` | A failure or joke on safe ground | A tier-1 pratfall, or a fake-out that misses | BF-pentopixels, SMB-post |
| `lap` | An easy run on the skill just learned | DR03's last beat | Brown-3DW, CT-TheGamer (the thunderbolt ride) |
| `checkpoint` | The save itself, on the first safe ground after the peak | DR08 | Booth09 (relax until the next safe room), CTG-news |
| `retry` | An instant, identical, cheap retry | Tier 1, recovered in 3–8 s (repo: LBR:33) | HG101, SMB-post |

These do **not** count as a valley:
- an empty corridor longer than ~15 s (repo-start: playbook:252);
- a valley beat with no clip sentence of any kind (E7).

**DR05: new devices enter at a valley.**
- *Rule:* a device's first contact is at C ≤ 2 and T ≤ 1, with no clock, and not inside a combination. There is one new idea per segment. The tutorial is exempt. A new device in the finale is conflict E15.
- *Why:*
  - In Linehan's analysis, drops in complexity coincide with new skills. Lemmings' new obstacles inside demanding puzzles are the exception (Linehan14).
  - Valve introduces mechanics in puzzles because puzzles carry no pressure (Valve14).
  - Portal 2 taught pipe-breaking one level before Wheatley's lair, with no time pressure, because playtesters were confused in the lair (Portal2-dev).
  - Players don't learn under stress (Brown23).
  - Don't punish players while they learn, and keep new items to about three at most (Hodent).
  - A new thing should add only a small gap over what players already understand (vanLankveld08).
  - Nintendo took mean placements out of the main courses because curveballs look mean-spirited to beginners (IwataAsks-3DL).
- *Thresholds:*
  - one new idea per segment (repo: GDD:174), which is stricter than Hodent's ~3 (src: Hodent);
  - the first-contact beat at C ≤ 2 and T ≤ 1 (start).

**DR06: combine only what was met alone, and never repeat a combination.**
- *Rule:* introduce devices in the order A | B | AB | C | AC | BC | ABC. The finale is the full combination.
- *Why:*
  - Stout's ramp gives each element alone before any combination and never reuses a combination (Stout15).
  - A composite pattern comes after its parts (RhythmGroups).
  - Pico Park's last set combines every earlier gimmick (PicoPark).
- *Threshold:* no combination repeated within a Bölüm (start, after Stout15; his unit is a ramp).

**DR07: retire a device before it wears out.**
- *Rule:* a device is the focus of the segment that introduces it. After that it is only an ingredient. Bringing it back as the focus needs a new twist. Lengthening a segment on the same question is not pacing.
- *Why:*
  - 3D World teaches, develops, twists and throws away a mechanic (MCV15). It does so in about five minutes, which is closer to a Mixtrol act than a segment, so that number is not used here.
  - One critic found some Celeste chapters' twists wore out before the level ended (Bycer18).
  - Hazelight avoids repeating a major mechanic (GDC17-LD).
- *Threshold:* a device is the focus of 1 segment (start).

### B.3 Checkpoints and failure cost

**DR08: the checkpoint sits on the first safe ground after the peak. Nothing after a peak can cost the peak.**
- *Why:*
  - In one Carry The Glass review, the group beat the crab boss three times without reaching the checkpoint (CTG-reviews, a single review).
  - L4D's Relax phase lasts until the survivors near the next safe room (Booth09).
  - Two of Chained Together's three Beginner checkpoints follow a hard stretch (CT-TheGamer; weak).
- *Thresholds:*
  - nothing between the peak's commit point and the next checkpoint or landing is at T ≥ 2 (start);
  - that stretch is ≤ 15 s clean (start).

**DR09: keep the peak's replay cheap.**
- *Rule:* the lead-in from the checkpoint to the peak is made of beats that become trivial on retry. B3 is excluded until E17 is decided.
- *Why:*
  - The cost of failure is the playtime it takes away (Juul10).
  - Bread & Fred reviewers resented losing 5–15 min to one fall (BF-reviews).
  - A Carry The Glass Impossible attempt, with no checkpoints, failed at about 95% of the course after 30–35 h (CTG-threads).
  - Carry The Glass added a checkpoint in front of its falling spike balls four days after launch (CTG-news).
- *Threshold:* ≤ 60 s clean from the checkpoint to the peak's commit point (start), inside the 45–90 s band (repo-start: playbook:106).

**DR10: modes change only the decided knobs.**
- *Rule:*
  - Kolay and Normal change only these knobs: checkpoint density, chase speed, door type and SwapGate density (repo: playbook:122-131).
  - They never reorder beats and never change geometry.
  - They never adapt at runtime (no DDA).
- *Why:*
  - Carry The Glass sells each course in three modes that differ in checkpoint density (CTG-store).
  - Chained Together players asked for a middle mode with moderately spaced checkpoints (CT-threads).
  - Perfect dynamic difficulty would erase the designed pacing, and players game it (Adams08).
  - L4D varies how often peaks come, not how high they are, and keeps its crescendos and finales fixed (Booth09, Valve14).
  - Difficulty choices built into play beat system-driven adjustment (Chen).
- *Threshold:* Kolay's mid-segment checkpoint (repo: playbook:128) goes directly before the peak (start).

### B.4 Spike limits

**DR11: the critical-path ceiling is C4.**
- *Rule:* a first-time group fails a peak 1–3 times and then clears it. C5 has no place on the critical path. Optional lines are frozen (DR20).
- *Why:*
  - In Juul's test, players who failed some and then finished rated the game highest. This was near-significant across three performance groups. Players who blamed their own mistake rated it higher than players who blamed the game (Juul09).
  - Easier versions, assigned blindly, were played longer (Lomas).
  - PEAK removed hazards that ended whole runs and at the same time made its small deaths more dangerous (PEAK-news).
  - The four-loss rule (repo: playbook:112).
- *Thresholds:*
  - a median of ≤ 3 tier-2 losses per segment on first play (start);
  - a partner window < 1 s online is not rated on C. It is conflict E16.

**DR12: small steps and a smooth start.**
- *Rule:* a segment's peak rises at most one level above the previous segment's peak; drops are free. The first third has no C4 and no T3.
- *Why:*
  - In Rayman Legends, sharp early swings in difficulty went with more quitting. This is correlational (Allart17).
  - Quitting on hard levels is more common early in a game. This is correlational and model-based (Roohi20).
  - A game should not start out too difficult (GameFlow).
  - No sudden walls (Branyiczky16).
- *Thresholds:*
  - at most +1 C per segment (start);
  - in the first third, C ≤ 3 and T ≤ 2 (start).

**DR13: showpieces are rare, and two peaks in a row never ask the same question.**
- *Rule:*
  - About one segment in four or five is a showpiece.
  - Two consecutive segment peaks never ask the same question (B.0 vocabulary).
  - Two set pieces never follow each other.
- *Why:*
  - L4D deals a Tank, a Witch or nothing along the route, and never a Tank straight after a Tank (Booth09).
  - Standout moments sit among ordinary ones (Totten10).
  - An easy N++ episode mixes three easy levels, one easy-medium and maybe one medium (Sheppard14).
  - Vary the kind of challenge: performative, cognitive, decision-making, emotional (GameFlow).
- *Thresholds:*
  - ≤ 1 showpiece in any 4 consecutive segments (start);
  - no two consecutive peaks with the same question (start).

### B.5 Act and Bölüm

**DR14: a valley segment between act peaks.**
- *Rule:*
  - Between the peak of one act and the first peak of the next there is at least one valley segment.
  - Its one new idea is a verb, a view, or the next device's teach (E4).
  - Fix fatigue with a valley, not by shortening the journey.
  - Valley segments are exempt from DR03's twist.
- *Why:*
  - Valve kept the long drive and inserted White Forest Inn as a break instead of shortening it (Valve14).
  - A rising sine's breather falls back, but not all the way (Koster25).
  - Eugene Jarvis on Defender: easier waves act as "redemption" (Grannell12). Christopher Phin, quoted in the same article: the next set of levels eases off.
  - One pilot used a cycle of 5 building levels, 1 peak and 3 rest levels (Mossmann19; weak).
  - *Counter-evidence:* Chained Together's break zones lose about as many players as its hard ones (CT-ach; confounded). A valley that still costs a lot is not relief.
- *Thresholds:*
  - ≥ 1 valley segment between act peaks (start);
  - the valley segment has a shorter clean time than the segment before it, and is ≥ 45 s (start; the 45 s floor is repo-start: playbook:106).

**DR15: a Bölüm opens with a hook, below the previous Bölüm's finale.**
- *Rule:* the first segment after the tutorial opens below the previous Bölüm's finale. Its hook is a clip, not a wall.
- *Why:*
  - Schell puts the hook first (Schell). Lopez puts one of the more exciting events at the front (Lopez08).
  - Phin: the next set of levels eases off (Grannell12).
  - In Portal, Portal 2 co-op and Braid, each new skill arrives in a relatively simple level (Linehan14).
  - Super Mario Bros. 1-1 opens with a Goomba, chosen over a harder Koopa, and the first reward comes right after it (SMB1-1).
  - About one in six Carry The Glass players who finished its first level finished its second (CTG-ach). This is confounded: the second level shipped 10 months later.
- *Thresholds:*
  - the first segment's peak ≤ C2 (start);
  - the hook within the first 60–90 s (repo-start: playbook:176).

**DR16: where the hardest execution check sits (open; the evidence is split).**
- *For "before the end":*
  - A climax need not be the hardest check; a falling action follows it (LDB).
  - Portal's fire-pit escape felt climactic although it was about its easiest puzzle (Portal-GDC08).
  - Celeste's Summit reviews earlier mechanics (CelesteWiki).
- *For "at the end":*
  - Schell's grand finale (Schell).
  - Lopez puts the most exciting event at the end (Lopez08).
  - L4D's finale is the campaign's highest-intensity challenge (Valve14).
  - Chained Together's Garden ends on two brutal challenges (CT-TheGamer).
- *A counterexample, not support:* Bread & Fred's hardest stretch is in its middle, and so is the loss of half its players (BF-ach). A reviewer called it "from unforgiving to broken" (BF-reviews).
- *What survives* is folded into DR18: the finale's intensity comes from stakes and pressure at ≤ C4.
- *No threshold.* The critique only reports where the hardest beat sits, by segment index and % by x. B3's K2, "en sert kademe" (B3 beats:59), is reported the same way.

**DR17: set pieces are fixed, use only taught moves, and are followed by low threat.**
- *Rule:*
  - A set piece is authored and fixed.
  - It may debut only if it asks for moves the group already knows.
  - After it comes a stretch of ≥ 30 s at C ≤ 2 and T ≤ 1 before the next C ≥ 3 beat. That stretch counts inside the next segment, as its teach and valley beats; it is not added on top.
- *Why:*
  - L4D's spawner relaxes for 30–45 s after a peak. This is an enemy-spawn phase, transferred here (Booth09).
  - Crescendos and finales are authored and fixed (Valve14).
  - Celeste's first chase is followed by a stretch where you cannot die (CelesteWiki).
  - Portal 2 taught the lair's key action one level earlier (Portal2-dev).
- *Thresholds:*
  - ≥ 30 s (start, after Booth09);
  - ≤ 2 chase segments per level (repo-start: playbook:74).

**DR18: the finale.**
- *Rule:*
  - The finale is the full combination at the highest stakes, winnable, at ≤ C4.
  - It is never a troll, and it is followed by a no-fail win beat.
  - Save the strongest twist for it.
  - When the finale follows a set piece, DR17's stretch and the win beat both count inside its 45–90 s. If they don't fit, the finale is two segments.
  - "No new device in the finale" conflicts with GDD:187 (E15).
- *Why:*
  - The worst moment and the ending shape memory (Gutwin16).
  - 22 of 32 subjects (69%) chose to repeat the longer trial with the milder end (Kahneman93). Finn found the same with learning tasks (Finn10).
  - Portal's final boss copied the fire pit's recipe: an easy puzzle under a countdown (Portal-GDC08).
  - Celeste's Epilogue has no way to die and pays out the strawberries collected (CelesteWiki).
  - Chained Together follows its hardest set piece with two puzzles and a spectacle exit (CT-TheGamer).
  - Bread & Fred's summit troll soured some reviews (BF-ending).
  - Split Fiction kept its most novel idea for the last level (SplitFiction26).
- *Thresholds:*
  - finale peak ≤ C4 (start);
  - a win beat of 10–20 s at C1 (start).

### B.6 Whole game

**DR19: the game ratchets, and harsh fall costs come after confidence.**
- *Rule:*
  - Each Bölüm opens below the previous finale but sits higher on average.
  - The towers' fall costs (B2, B3) come after Bölüm 1.
  - In a tower, a storey or kademe is a tooth and its landing is the refuge.
- *Why:*
  - Allart17, Roohi20 (both correlational).
  - Height is the stake (Foddy18).
  - Bread & Fred's studio pulled back from a pure rage game after its cute look drew a casual audience (BF-studio).
  - Reviewers resented losing 5–15 min to one fall (BF-reviews).
  - Each breather sits higher than the last (Koster25).
  - `level-kit.md:295-296` already puts a storey's costly fall at its last move.
- *Thresholds:*
  - a failure never costs more than one segment, in any mode (repo: GDD:172);
  - a tower fall never goes below the storey or kademe landing (repo: GDD:307-308);
  - worst-case Loss per fall ≤ ~3 min (start, after BF-reviews).

**DR20: optional harder lines (frozen until E9).**
- *Proposal:* strong groups raise their own difficulty on optional lines, and the critical path stays within DR11.
- *Why:*
  - Moderate challenge motivates when players choose it (Lomas).
  - Celeste's harder side chapters, and Nintendo's special courses and "three pipes" (CelesteWiki, IwataAsks-3DL, Brown24).
  - Heave Ho's optional coins (HeaveHo19).
  - Difficulty choices built into play (Chen).
  - Only 3.1% of Chained Together players collected all ten wings (CT-ach). This shows how rare such players are; it does not set a threshold.
- *Needed before adoption:*
  1. A decision on replay levers. GDD:584 makes best time the only one; a harder line that only saves time stays inside that.
  2. No pickups or side systems that spill into the run (the user's rule that side mechanics stay self-contained).
  3. Co-op rules. The whole group takes the line, or every role has a job on it (idle ≤ ~10 s, AP13). A line that splits the group in a single lane is out.

### B.7 Twists and trolls

**DR21: every tooth has a twist; a troll is a rationed kind of twist.**
- *Rule:*
  - The twist is required in every tooth (DR03). A troll is optional and rationed (DR23).
  - A troll breaks a rule the level taught earlier, in this segment or before.
  - A troll may *be* the twist beat when that beat's execution is ≤ C3 and its cost is ≤ a walk or tier 1 (DR22).
  - A troll is never on a teach beat and never on a beat at C ≥ 4.
  - It never comes after a goal or a real checkpoint, and never on the finale's last beat.
  - One troll channel per beat: the designer's (`bait`/`bet`) or the partner's (`p2p`), not both.
- *Why:*
  - IWBTG teaches that fruit falls down, then one falls up. Its hardest parts are the ones where the traps step back (HG101).
  - Kishōtenketsu's twist step (Hayashida12).
  - No mean curveballs for beginners (IwataAsks-3DL).
  - The best-documented fair troll level puts the obvious trolls first and the real deception late, with the answer available all along (EGM20).
  - Abusive design works as a dialogue with the designer (WilsonSicart10).
  - Bread & Fred's summit troll (BF-ending).
- *Threshold:* a troll sits on the twist or on a develop beat (start, after Hayashida12).

**DR22: a troll is visible, cheap and identical on retry.**
- *Rule:*
  - Everything that can cost is visible from the previous beat. The trick is which choice is right, not what is there (repo: GDD:219; B1 beats:73-74; LBR:187, AP02). A cause first found by dying is an ambush, not a troll.
  - A troll's own cost is a walk or tier 1. The decoy checkpoint never kills (repo: GDD:256); its price is the replay from the real checkpoint after a later death.
  - A troll is identical on retry.
  - Reusing a joke elsewhere in the game needs a new twist.
- *Why:*
  - A violation is funny only while it stays benign (McGraw10).
  - A small jump in incongruity drives interest; a large one drives avoidance (vanLankveld08).
  - IWBTG saves about every two rooms, so each troll death is cheap (HG101).
  - In Getting Over It every setback is intentional and the player is always responsible (Doucet17).
  - Failure blamed on oneself is enjoyed; failure blamed on the game is not (Juul09).
  - The Mario Maker troll norm is to laugh with the player. Defender1031's guide, as EGM reports it, counts these as "hot garbage": random hidden blocks, enemy spam, pick-a-path choices, and doors or pipes that lead to instant death (EGM20).
  - "Twice twice" rooms rebuild a section with subtle differences (fasterthanli19).
  - DA-45 records that B1's fixed traps are funny once, and that B2 repeated B1's decoy.
- *Thresholds:*
  - cost ≤ a walk or tier 1 (start, bounded by GDD:219 and GDD:256; anything more needs the user, E11 and E14);
  - a first-time group can name the cause after one encounter (start);
  - no joke reused in the game without a new twist (start; DA-45 open).

**DR23: ration the designer's trolls.**
- *Rule:*
  - At most one designer troll (`bait` or `bet`) per two segments.
  - `bet`s stay under the open cap (README:62, DA-45) and sit in the second half.
  - No `bet` in the first two segments after the tutorial or in the finale.
  - An honest segment follows every `bet`.
  - The partner is the renewable troll; DR27 places p2p windows.
- *Why:*
  - Kayin (room to breathe).
  - The obvious-first, real-one-late order (EGM20).
  - Valve calls combat during a scripted scene powerful because players drop their guard, and uses combat sparingly (Valve14).
  - Repeated violations of what players expect lead them to cut back or quit (Ballou23; applied here by inference).
  - README:62 (Open) and LBR:152-153.
  - Deliberate betrayal between players is funny forever, because the players author it (`coop-mechanics-playbook.md:159-161`).
- *Thresholds:*
  - ≤ 1 designer troll per 2 segments (start);
  - the `bet` count is open: README:62 proposes one per level (DA-45, E18);
  - no `bet` in the first two segments or the finale (start).

### B.8 Co-op

**DR24: a talk window in every tooth.**
- *Rule:* before the peak, the whole group can stand safe, see the hazard, and count it out, with no clock running.
- *Why:*
  - Totten's refuge → prospect → secondary refuge. A refuge is a safe lookout from which the crossing can be planned (Totten).
  - Interdependence builds closeness through conversational turns (Depping17).
  - Valve's co-op writing split story beats into smaller pieces and left room for players to talk (Portal2-dev).
  - PEAK's campfire needs every player within 19.2 m and pauses hunger and fog. Since *Play It Your Way*, groups may stay as long as they like (PEAK-wiki, PEAK-news).
  - The GDD's talk-window rule (GDD:220-223) and its "a breath to talk" (GDD:212).
- *Thresholds:*
  - at least 1 refuge per segment before its peak, holding the whole group safe with the hazard in frame, with ≥ 3 s of standing room (start);
  - the call it needs is < 3 s (repo: LBR:36; RX14).

**DR25: pace for the most stressed player, give every role a win, and build valleys under the swap.**
- *Rule:*
  - Rate each beat by the seat it is hardest for.
  - Each role, not each seat, wins at least one beat per segment.
  - Valleys lower C, T or P *under* the swap; they never lift it. Three existing rules require this:
    - The swap is the always-on floor (repo: playbook:43-44; LBR:55).
    - A beat one player can finish alone fails (repo: LBR:90-91; B1 beats:77-78).
    - The jump swap stays the floor in S7–S11 and in every tower (the user's constraint, 2026-09-27).
- *Why:*
  - L4D reads the group's intensity from its most stressed member (Booth09).
  - In one couple, the partner who was enjoying it less ended the session (BF-pentopixels).
  - Shared control lowered felt competence and autonomy, while interdependence lowered frustration (Emmerich17). Reading the swap as "shared control" is an interpretation; the answer here is a success under the swap, not its removal.
  - PEAK keeps dead players in the conversation (AggroCrab26).
- *Thresholds:*
  - each role wins ≥ 1 beat per segment (start);
  - idle ≤ ~10 s (repo-start: LBR:194).

**DR26: blame stays a joke.**
- *Rule:*
  - Every tier-2 death has one cause that a stranger can attribute within 1 s (repo: coop:260).
  - The designed faller rotates.
  - A tier-1 failure recovers in 3–8 s (repo: LBR:33).
  - The sound or line that plays on a wipe belongs to game-feel (FP22, §F row 13), not to the level check. GDD:256's mocking decoy and GDD:258's blame table stand.
- *Why:*
  - A positive Chained Together review describes shouting "jump", blaming each other and laughing (CT-reviews).
  - Chained Together's patch 1.8.0 added a "3,2,1 Go!" key to sync jumps (CT-news).
  - Juul09.
  - Super Meat Boy's replay of all your deaths turns failure into the reward (SMB-post).
  - In a Bread & Fred preview, failure felt almost as good as success (BF-pentopixels).
  - Escaping failure is itself the enjoyment (Juul13).
- *Thresholds:*
  - no seat is the designed faller in 2 consecutive segments (start);
  - at 3–4 players, every seat once before any seat twice (start).

**DR27: partner sabotage windows.**
- *Rule:*
  - Every segment has at least one p2p window.
  - A p2p window never sits on the teach beat. RX09 orders teach → dependency → sabotage (LBR:66-68).
  - It never shares a beat with a designer troll (DR21).
  - The saboteur pays too, through shared death (B1 beats:79-81), or the cost is tier 1.
  - On a device's first segment, its p2p cost is tier 1, "recoverably" (LBR:68).
- *Why:*
  - Deliberate betrayal is funny forever (coop:159-161).
  - The beat table's sabotage column (LBR:87).
  - Shared death makes sabotage punish the saboteur (B1 beats:79-81).
  - The Pico Park 2 review: trolling teammates is tempting, but the team has to work together eventually (PicoPark).
- *Thresholds:*
  - ≥ 1 p2p window per segment (start, after LBR:87);
  - the p2p cost in a device's first segment ≤ tier 1 (start).

**DR28: rate at 2 and at 4.**
- *Rule:*
  - Write beats for "at least two" or "everyone" (repo: GDD:159-160; README:67).
  - Rate C at 2 and at the level's maximum player count, and keep the higher value (start).
  - Pace by the most stressed seat (Booth09).
  - Rotate the designed faller across every seat (DR26).
  - A talk window holds everyone: one caller, one count, under 3 s (repo: LBR:36).
  - A beat untested at 4 is an anti-pattern (repo: LBR:199).
- *Scope:* B1 is built for 2 (GDD:157-158). Its critique rates at 2 and lists 4-player behaviour under "Ölçülecekler".

### B.9 How the rhythm fits the existing doctrine

| Existing doctrine | Where | Under the rhythm |
|---|---|---|
| Two-tier failure | LBR:46-53 | Tier 1 is the valley inside a beat (`retry`). Tier 2 lives only at the twist or peak (DR03, DR08). A troll's own cost is a walk or tier 1 (DR22). |
| The swap is the always-on floor | playbook:43-44; LBR:55 | Valleys lower C, T or P under it and never lift it (DR25). |
| Segment band 45–90 s, 3–5 beats (starting values) | playbook:104-110 | One segment is one tooth (DR03). The replay to the peak, ≤ 60 s, sits inside the band (DR09). |
| One clip per 60–90 s (starting value) | playbook:174-180 | The peak is the segment's clip. Valleys carry relief clips (`comedy`, `lap`, `vista`), so they are not corridor (DR04, E7). |
| 2–3 s of consequence quiet; FR14, FP20 | playbook:153-155; feedback-stack | The smallest valley (DR04). |
| Teaching arc RX09 | recipes.md:20; LBR:62-72 | RX09 orders the *ideas* across a Bölüm; DR sets the *load*. Its sabotage step is where DR27 places p2p windows. Recovery chaos stays RX09's step 5. |
| One new idea per segment | GDD:174; B1 beats:82 | Kept. A segment's opening valley *is* its new idea's safe teach (DR05). A pure valley segment's idea being a verb or a view needs the user's approval (E4). |
| At most one loss engine | LBR:55-60 | One stressor per peak. The chase plus the gate's re-deal is the GDD's own open case (GDD:205-213). |
| Chase in the last third, at most 2 segments | playbook:72-74 | Set-piece rules (DR17). |
| Kolay/Normal knobs | playbook:122-136 | DR10 follows them. |
| One-shot traps: at most one per level | README:62 (Open); LBR:152-153 | Open. DR23 places the traps and does not set the cap (E18). |
| Nothing is learned by dying; the decoy never kills | GDD:219, :256 | DR22 follows both (E14). |
| A storey's last move is the costly fall | `level-kit.md:295-296` | The storey's peak is its last move and the landing is its checkpoint, which is DR03's exception (b). |
| Beats for "at least two" | GDD:159-160; README:67 | DR28. |

---

## C. Level-critique procedure

### C.1 Inputs, evidence and honesty

**Where each column comes from**

| Column | Source |
|---|---|
| Segment names, clip sentences, clean run, acts if declared | `Assets/Mixtrol/Editor/Data/LevelNotes.asset` (level-editor.md:165-166) and the beat doc |
| Checkpoint and decoy positions; device parameters (door close time, cycle times, chase speed, pad height) | Read from the scene through `unity-editor-cli`, read-only |
| Windows, reach, fall lines, trolls, sabotage windows | The beat docs (`bolum-0N-beats.md`) and `level-kit.md` *Sizing against the movement* |
| C, attempts per pass, audible reactions, where each session stopped | Recorded first-time outside groups |

**Evidence tags.** Every value and every finding is tagged **M** (measured in Play Mode), **D** (documented in a beat doc or read from the scene) or **E** (estimated). A critique with no M values is labelled *provisional*.

**Who counts as M:**
- C and attempts per pass come only from first-time outside groups, at least 3 groups (start).
- The developer's own runs (both seats on one keyboard, or an online self-test) count as M for clean time and passability only, never for C.

**Every finding carries a falsifier:** the measurement that would withdraw it.

**Other rules:**
- **Record where each playtest session stopped.** A session cut off inside the hardest segment inflates the difficulty reports (Gutwin16).
- **Watch rather than ask.** Valve brought a random outside volunteer in every week, watched them play, took notes, then interviewed them. Hayashida reads testers' faces because direct questions get polite answers (Valve14, Brown23, Hayashida12).
- **Treat the order itself as a design variable.** The order of levels has a measurable effect on how many are attempted and completed (Sarkar17).

### C.2 Scales

#### Challenge C (per beat)

C is an integer from 1 to 5 plus a confidence of **H**, **M** or **L**. It is the number of failures a first-time group of the stated size can expect before its first clear.
- The measured replacement for C is attempts per pass, because difficulty can be defined as the probability of failure (Aponte11).
- Read felt difficulty separately, at the peak and the end moments (Gutwin16).
- Baits are not rated on C; they go in the Troll column.

**Proxy when the beat is unmeasured.** A beat with no failure state is C1. Otherwise start at C2 and add 1 per condition below, up to C5 (start):

- **(a) A counted timing window:** a partner window of 1–2 s online, or an own-movement window under 1 s.
- **(b) A tight required gap:** margin < 30% of the reach of the move the beat asks for. A margin < 10% counts as two conditions.
- **(c) A read:** which path, tile, owner or door is right, or a call made blind.
- **(d) Two demands at once:** two demands that must be met at the same moment, for example holding a plate while another jumps on a call.

Two cases are not rated:
- A **partner window under 1 s online** is not rated on C. The beat is marked `!` and goes to E16.
- **Geometry the docs call impassable** is not C5. It is a repo Blocker.

**Anchor table.** Every anchor is rated E until measured. Replace each anchor with its M value.

| C | Anchor beat (D) | Proxy reading |
|---|---|---|
| C1 | B1 S0: walking through the first gate (B1 beats:31) | No failure state |
| C2 | B1 S1: carrying the cauldron to the delivery plate (B1 beats:32) | Untimed, no hazard |
| C3 | B1 S2: boarding the moving platform together over the x88–104 pits (B1 beats:33) | One own-movement timing |
| C4 | None yet | The first beat measured at 1–3 attempts per pass becomes the anchor |
| C5 | None yet | The first beat measured at ≥ 4 |

#### Stakes T and Loss

| T | Meaning |
|---|---|
| T0 | Nothing is lost. |
| T1 | Tier 1, recovered in place within 3–8 s (repo: LBR:33), or a walk back. |
| T2 | Tier 2, on the beat's real failure. |
| T3 | Tier 2 on a slip, or tier 2 between a peak's commit point and the next checkpoint. T3 is an anti-pattern. |
| Tf | A tower fall (B2, B3). Its price is the Loss column. |

**Loss (s).** The clean replay time a failure takes away (Juul10):
- for tier 2, from the checkpoint to the failed beat's commit point;
- for a tower fall, from the landing point back to the move.

Tower thresholds (start):
- A storey or kademe is a tooth, and its landing is the refuge and checkpoint.
- The worst fall in each band is reported per band.
- B2's Loss per fall ≤ one storey's clean climb.
- B3's cap waits for E17.

#### Other columns

- **Question Q** and **tooth role:** from B.0.
- **Pressure P:** `—` none; `cyc` a device cycle that can be counted; `clk` a chase, rising goo or a timer.
- **Novelty N:**
  - `N0` reuse;
  - `N1` a new device;
  - `N2` a new combination, or a twist on known devices;
  - `N1!` first contact at C ≥ 3, under `clk` (except a set piece that asks only taught moves), or inside a combination. `N1!` is an anti-pattern.
- **Co-op load L:**
  - `own` each player on their own moves (a peak at `own` is solo-solvable: DC02, LBR:90-91);
  - `hand` a one-way dependency;
  - `swap` the partner's Space on a window;
  - `sync` everyone at once;
  - `idle` one player waits more than ~10 s.
- **Win (ms):** the tightest window the beat needs, as it plays online, with the test preset of 150 ms each way (playbook:135). A partner window under 1000 ms is marked `!`.
- **Margin (%):** (reach − gap) ÷ reach of the move asked. Reach comes from `level-kit.md` *Sizing against the movement*; for example, a solo dash reaches 6 m (B1 beats:53). A negative margin means the partner is required.
- **Vis:** Y/N. Is the hazard or bait visible from the previous beat (GDD:219)?
- **Attr:** Y/N. Can a stranger name the culprit within 1 s (coop:260)?
- **Troll:** `bait`, `bet` or `p2p`, from B.0.
- **Relief:** a palette key from DR04.
- **CP:** `◀` a checkpoint at the beat's start; `▶` a checkpoint at its end.

### C.3 The intensity map

One row per beat. The format follows Filatov's beat chart (Filatov15).

| Seg | Beat | Role | Clean s | C (conf) | T | Loss s | P | N | Q | L | Win ms | Margin % | Vis | Attr | Troll | Relief | CP | Clip? | Tag |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| S_ | b1 | teach | `<s>` | `<1–5> (H/M/L)` | `<T0–T3, Tf>` | `<s>` | | | | | | | Y/N | Y/N | | | ◀ | Y/N | M/D/E |

**Per-segment summary:**
- opening C;
- peak C (confidence), the peak beat, its role and its question;
- peak position (% of clean time, or % by x when there is no time);
- replay to the peak (s);
- the tail after the peak (s, T);
- the valley's question after the peak;
- talk window (Y/N);
- trolls (channel, cost);
- p2p windows;
- rated group size.

### C.4 The curve

- Write each segment's peak C as `▁▂▃▄▅` for C1–C5.
- `?` means unknown.
- `!` after a glyph means the peak needs a partner window under 1 s online (E16).
- `‖` follows the tutorial; `|` separates acts.
- Acts come from the level doc or from B.0's rule. The critic never picks them.

### C.5 Checks

With only D or E evidence, a finding is at most Major. Blocker needs M evidence or documented impassable geometry (C.6).

| DR | Test on the map | Severity if it fails |
|---|---|---|
| DR01 | ≥ 3 consecutive segments at the same peak C; any opening beat > C2 | Major |
| DR03 | No twist; the peak is the last beat and no checkpoint or landing follows within 5 s; fewer than 3 beats. Valley segments, set pieces and storeys are exempt from the lap. | Major / Minor |
| DR04 | Two C4+ beats with no valley beat between them; the valley after a peak asks the same question as the peak | Major |
| DR05 | `N1!`; more than one N1 in a segment (tutorial exempt); N1 in the finale (E15) | Major / Karar |
| DR06 | A combination whose parts were never met alone; a repeated combination | Major |
| DR07 | The same question as the focus for ≥ 2 segments with no new twist | Major |
| DR08 | T ≥ 2 between the peak's commit point and the next checkpoint or landing | Blocker (with M) / Major |
| DR09 | Replay to the peak > 60 s (B3: E17) | Tune |
| DR11 | C5 on the critical path | Blocker (with M) / Major |
| DR12 | A peak step > +1; C4 or T3 in the first third | Major |
| DR13 | Two consecutive peaks with the same question; two set pieces in a row; > 1 showpiece in any 4 consecutive segments | Major / Minor |
| DR14 | No valley segment between two act peaks | Major |
| DR15 | The first segment's peak > C2; no hook within 60–90 s | Major / Minor |
| DR16 | Report only: the hardest beat's position (segment index, % by x) | — |
| DR17 | A set piece that needs an untaught move; < 30 s at C ≤ 2 and T ≤ 1 after it before the next C ≥ 3 | Blocker (with M) / Major |
| DR18 | A troll or a C5 in the finale; a finale peak > C4; no win beat | Major |
| DR21 | A troll on a teach beat, on a beat at C ≥ 4, after a goal or checkpoint, or on the finale's last beat; two troll channels on one beat | Major |
| DR22 | A troll not visible from the previous beat; a cost above a walk or tier 1; a cause that cannot be named; a troll that changes on retry | Major |
| DR23 | > 1 designer troll per 2 segments; a `bet` in the first two segments or the finale; no honest segment after a `bet`; the `bet` count against the open cap | Major / Karar |
| DR24 | No refuge before the peak, or one that cannot hold the whole group | Major |
| DR25 | A role with no win in a segment; idle > ~10 s; a valley that lifts the swap | Minor / Major |
| DR26 | A tier-2 death with no cause attributable within 1 s; the same seat as designed faller twice in a row | Major / Minor |
| DR27 | A segment with no p2p window; a p2p window on the teach beat or on a troll beat | Minor / Major |
| DR28 | A beat written for "exactly two"; a beat unrated at 4 | Minor / Measure |
| `!` | A partner window < 1000 ms online | Karar (E16) + Measure |
| (repo) | Documented impassable geometry | Blocker |
| (repo) | Unmeasured windows or clean times | Measure |

### C.6 Severity and scoring

| Severity | Turkish | Meaning |
|---|---|---|
| Blocker | *Engelleyici* | Backed by M evidence of quitting or unfairness, or by documented impassable geometry. Change it before the next playtest. |
| Major | *Büyük* | The rhythm is broken. Change it or argue the case. With D or E evidence this is the ceiling. |
| Minor | *Küçük* | Polish. |
| Tune | *Ayar* | Fails a `(start)` or `(repo-start)` threshold by a small margin, within 25% of the value (start). Tune it in play; don't redesign. |
| Decision | *Karar* | The finding hits a repo decision or an open conflict (§E). The user decides. |
| Measure | *Ölç* | Cannot be judged until measured. |

**Ranking.** At equal severity: `src` > `repo` > `repo-start` = `start`.

There is **no single numeric score.** Most thresholds are starting values, so a composite number would look more precise than it is. The verdict is:
- the count of findings per severity, per segment and per act;
- the curve;
- at most 7 top findings, each with its evidence tag and falsifier.

### C.7 Output format for the user (Turkish, DR IDs kept)

```
### <Bölüm adı> — zorluk ritmi eleştirisi
**Durum:** geçici — dokümandan, oynanmadı | ölçülmüş — <tarih>, <n> yabancı grup (<oyuncu sayısı> kişilik)
**Perdeler:** bölüm dokümanından | mekanik kuraldan (B.0)
**Kısaca:** eğrinin şekli ve en büyük sorun, en fazla üç cümle.

**Eğri** (segment zirvesi C1–C5; `?` bilinmiyor; `!` çevrimiçi 1 s altı ortak penceresi, E16; `‖` eğitimden sonra; `|` perde sınırı)
`S0▂ ‖ S1▂ S2▃ … | …`

**En önemli bulgular** (önem sırasıyla, en fazla yedi)
1. **[Engelleyici | Büyük | Küçük | Ayar | Karar | Ölç] <segment> — <DR ID'leri>.**
   - *Ne:* …
   - *Kanıt:* M | D | E — …
   - *Neden:* … (kaynak anahtarı, §D)
   - *Öneri:* …
   - *Geri çekilir, eğer:* … (bulguyu düşürecek ölçüm)
   - *Karar:* kullanıcı / GDD / gerekmez

**Geçenler:** <DR ID'leri ve segmentler>
**Ölçülecekler:** segment başına temiz süre, zirvenin taahhüt anı, geçiş başına deneme (yalnız ilk kez oynayan dış gruplar), dakikada sesli tepki, çevrimiçi pencere (ms), 4 kişide davranış, oturumun nerede bittiği.
```

Sample finding (see §G):

> 1. **[Büyük] S7–S11 — DR13, DR14.**
>    - *Ne:* beş segmentin zirvesi aynı soruyu soruyor: sıvı çukurunun üstünde ortağın Space'i (`pw`). Aralarında vadi segmenti yok.
>    - *Kanıt:* D — segment tablosu ve bölümün kendi notu (bolum-01-beats.md:38-42, :104-105).
>    - *Neden:* aynı tipte iki zirve arka arkaya gelmez; L4D bir Tank'ın hemen ardından ikinci bir Tank dağıtmaz (Booth09).
>    - *Öneri:* perdenin zirvesi S9–S10'da kalsın. Zaten yeniden kurulacak S11 perdenin vadi segmenti olsun: zıplama takası zemin olarak kalır, ama pencere sayılabilir ve ≥ 1 s, altında tier-1 şerit var.
>    - *Geri çekilir, eğer:* ilk kez oynayan dış gruplar S9–S11'de S7'dekiyle aynı dakikada sesli tepkiyi veriyor ve geçiş başına deneme düşmüyorsa.
>    - *Karar:* kullanıcı.

---

## D. Evidence (verified sources only)

The "Supports" column names the DR rules each source backs. §-references point to other sections of this doc.

| Key | Source | Type | Supports |
|---|---|---|---|
| Schell | J. Schell, *The Art of Game Design*: Lens of the Interest Curve, and the zig-zag through the flow channel. Read via a lens transcription (gamefroot-developer.gitbooks.io/…/061.html), Notes by Lex, Amy's blog and T. Sala (2013) | book (secondary) | DR01, DR15, DR16 |
| Adams-FGD | E. Adams, *Fundamentals of Game Design*, 3rd ed. (2014), publisher sample. The index lists "sawtooth difficulty progression" on p. 424; the text was not read | book | §A (existence only) |
| Adams08 | Adams, "Difficulty Modes and Dynamic Difficulty Adjustment" (2008), gamedeveloper.com | industry | DR10 |
| Hodent | C. Hodent, "The Gamer's Brain", GDC16 and GDC17 talks (celiahodent.com) | industry | DR01, DR04 (`easy`), DR05 |
| Chen | J. Chen, *Flow in Games* (MFA thesis), jenovachen.com | academic | DR10, DR20 |
| Koster25 | R. Koster, "Game design is simple, actually" (2025) | industry | DR01, DR14, DR19 |
| Totten | C. Totten, *An Architectural Approach to Level Design*, 2nd ed. (2019; contents and introduction); "Designing Better Levels Through Human Survival Instincts" (2011) | book / industry | DR24 |
| Totten10 | Totten, "What Old Issues of Nintendo Power Can Teach Us About Level Design" (2010) | industry | DR13 |
| Stout15 | M. Stout, "Trinity, Part 7: Ramps, Part 2" (2015) | industry | DR01, DR06 |
| Lopez08 | M. Lopez, "Harnessed Pacing & Intensity" (2008) | industry | DR15, DR16 |
| Grannell12 | C. Grannell, "Bashing your head against the difficulty wall" (2012), quoting C. Phin and E. Jarvis | industry | DR14, DR15 |
| LDB | The Level Design Book, "Pacing" | industry | DR02, DR04, DR16 |
| Filatov15 | N. Filatov, "Beat-chart: game designer's best friend" (2015). The per-location beat table is Filatov's own format | industry | §C.3 |
| Branyiczky16 | A. Branyiczky, "Doing Difficulty Right: Fractal Curves" (2016) | industry | DR12 |
| Hayashida12 | C. Nutt interviewing K. Hayashida: "The secret to Mario level design" and "The Structure of Fun" (2012) | official (interview) | DR03, DR21, §C.1 |
| IwataAsks-3DL | Iwata Asks: Super Mario 3D Land, Vol. 1, part 6 (2011), nintendo.com | official | DR05, DR20, DR21 |
| Brown-3DW | M. Brown (GMTK), "Four components of game design in Super Mario 3D World", translated, wnhub.io (2016) | industry | DR03, relief palette (`lap`) |
| MCV15 | MCV on Mark Brown, "Nintendo's level design secrets in four steps" (2015) | industry | DR07 (retirement only; its "five minutes" is not used) |
| Brown24 | Brown, "Super Mario's Invisible Difficulty Settings" (2024) | industry | DR20 |
| SMB1-1 | C. Kerr, "How Miyamoto built World 1-1" (2015); Wikipedia, "World 1-1". The Goomba-over-Koopa detail is from Wikipedia's Goomba article, citing Eurogamer's 2015 video | official / community | DR15 |
| Valve14 | M. Scott, "Level Design Workshop, Section Three: Pacing", GDC China 2014 (media.gdcvault.com …833762…Pacing_EN.pdf) | official | DR04, DR05, DR10, DR14, DR16, DR17, DR23, §C.1 |
| Booth09 | M. Booth (Valve), "The AI Systems of Left 4 Dead" (2009), steamcdn-a.akamaihd.net | official | DR08, DR10, DR13, DR17, DR25, DR28 |
| Portal2-dev | Valve, Portal 2 developer commentary (theportalwiki.com): "Preparing For Wheatley's Lair", "Elevator Fatigue", "Writing for Co-Op" | official | DR04, DR05, DR17, DR24 |
| Portal-GDC08 | M. Kumar, "The Secrets of Portal's Huge Success" (Swift and Wolpaw, GDC 2008) | official (reported) | DR02, DR16, DR18 |
| Brown23 | M. Brown, "Valve's Secret Weapon" (2023) | industry | DR05, §C.1 |
| SMB-post | E. McMillen and T. Refenes, "Postmortem: Super Meat Boy" (2011) | official | DR26, relief palette (`comedy`, `retry`) |
| Sheppard14 | M. Sheppard, "Designing N++ levels", PlayStation Blog (2014) | official | DR13 |
| GDC17-LD | J. Burgess, "GDC 2017 Level Design Workshop" report; J. Fares (GamingBolt, 2021) | industry / official | DR04, DR07 |
| SplitFiction26 | D. Riendeau reporting H. Gille, "Split Fiction's final level concept…" (2026) | official (reported) | DR18 |
| Foddy18 | J. Couture, "Road to the IGF: Getting Over It"; A. Wiltshire, "The aesthetics of frustration in Getting Over It" (2018) | official (interviews) | DR02, DR19, §A, §F row 13 |
| Doucet17 | L. Doucet, "Pain, Difficulty, and Getting Over It" (2017) | industry | DR22 |
| CelesteWiki | celeste.ink pages: Old Site, Reflection, The Summit, Epilogue, Golden Ridge, B-Sides | community | DR04, DR16, DR17, DR18, DR20 |
| Bycer18 | J. Bycer, "Celeste is a Game of Many Ups and Some Downs" (2018) | industry | DR07 |
| HeaveHo19 | P. Hancock, "Review: Heave Ho", Destructoid (2019) | industry | DR20 |
| CT-ach | Steam global achievements, app 2567870 (derived per-zone attrition) | official | §A, DR14 (counter-evidence), DR20 |
| CT-sr | speedrun.com API: Chained Together levels and per-level records | community | E12 only |
| CT-TheGamer | M. McKeown, "How Many Meters Tall Is The Chained Together Map?" (2024); E. Pala, checkpoint and max-height guides (2024) | industry | §A, DR04, DR08, DR16, DR18 |
| CT-threads | Steam discussions: "Hell difficulty", "I hope to add a new difficulty level" (2024) | community | §A, DR10 |
| CT-news | Steam store page and Steam News API: patches 1.7.8, 1.8.0 ("3,2,1 Go!") and 1.10.19 | official | DR26, E12 |
| CT-reviews | Steam reviews API, English, app 2567870 | community | DR26 |
| CT-wings | U. Ali (GameRant) and E. Pala (TheGamer), Wings of Freedom locations (2024) | industry | DR20, E12 |
| indiegame26 | indiegame.com editorial, "Chained Together Two Years On: How a $4.99 French Indie Platformer…" (2026). The "complexity" line is the writer's analysis | industry | §A (price), E12 |
| CTG-store | Steam store page, app 3263320 | official | §A, DR10 |
| CTG-news | Steam News API, app 3263320: patch of 27 Oct 2024, Baby Mode (28 Oct 2024), update 2.0 (15 Aug 2025) | official | §A, DR09, DR10, relief palette (`checkpoint`) |
| CTG-ach | Steam achievements, app 3263320 | official | DR15 |
| CTG-reviews | Steam reviews API, English, app 3263320 (the crab review is one review) | community | DR08 |
| CTG-threads | Steam discussion, "Immortal Buddy achievement" (the 30–35 h attempt that reached 95%) | community | DR09 |
| BF-studio | Sand Castles Studio: game page; blog post "cooperative rage game" (2024) | official | §A, DR19 |
| BF-ach | Steam achievements, app 1607680 | official | §A, DR16 |
| BF-reviews | Punished Backlog (2024); CGMagazine (2024); Shacknews (2023) | industry | §A, DR09, DR16, DR19 |
| BF-pentopixels | J. Garcia, Pentopixels: PAX East preview and impressions (2023) | industry | DR25, DR26, relief palette (`comedy`) |
| BF-ending | Steam reviews API, app 1607680; Laboratory update post (2025) | community / official | §A, DR18, DR21 |
| PEAK-wiki | peak.wiki.gg, "Campfire" | community | DR24, relief palette (`talk`) |
| PEAK-news | Steam announcements: Hotfix 1.42.a, Patch 1.1.a, "The Final Ascent" (2026), "Play It Your Way" (2026) | official | DR11, DR24 |
| AggroCrab26 | C. Kerr, "Peak co-developer Aggro Crab shares lessons in friendslop" (GDC 2026) | industry | DR25 |
| Kayin | M. O'Reilly, IWBTG FAQ (kayin.moe) | official | §A, DR04, DR23 |
| HG101 | E. Mack, "I Wanna Be the Guy", Hardcore Gaming 101 (2022) | industry | §A, DR21, DR22 |
| EGM20 | M. Goroff, "These Super Mario Maker Level Designers Have Elevated Trolling Into an Artform", EGM (~2020), including Defender1031's "Trolling for Dummies" as reported | industry | DR21, DR22, DR23 |
| LevelDevil | Poki, Level Devil game page | official | §A |
| fasterthanli19 | "Celebrating Mario Maker" (2019) | community | DR22 |
| TA2-OnlyUp | Wikipedia, "Trap Adventure 2" and "Only Up!" | community | §A |
| PicoPark | Wikipedia, "Pico Park"; *Pico Park 2* review (Xbox Tavern) | community / industry | DR06, DR27 |
| Linehan14 | Linehan, Bellord, Kirman, Morford, Roche, "Learning Curves", CHI PLAY 2014 (ben.kirman.org PDF) | academic | §A, DR01, DR05, DR15 |
| Gutwin16 | Gutwin et al., "Peak-End Effects on Player Experience in Casual Games", CHI 2016 | academic | §A, DR18, §C.1, §C.2 |
| Kahneman93 | Kahneman, Fredrickson, Schreiber, Redelmeier, "When More Pain Is Preferred to Less: Adding a Better End", *Psychological Science* 4(6), 1993. Full text: 22 of 32 subjects (69%) chose to repeat the long trial | academic | §A, DR03, DR18 |
| Finn10 | B. Finn, "Ending on a high note", *JEP: LMC* 36(6), 2010 | academic | §A, DR03, DR18 |
| Juul09 | J. Juul, "Fear of Failing?", *The Video Game Theory Reader 2* (2009) | academic | DR11, DR22, DR26 |
| Juul10 | Juul, "In Search of Lost Time", FDG 2010 | academic | DR09, §C.2 (Loss) |
| Juul13 | Juul, *The Art of Failure*, MIT Press 2013 (about page) | book | DR26 |
| Allart17 | Allart et al., "Difficulty Influence on Motivation over Time…", FDG 2017 | academic | §A, DR12, DR19 |
| Roohi20 | Roohi et al., "Predicting Game Difficulty and Churn Without Players", CHI PLAY 2020 (arXiv 2008.12937) | academic | §A, DR12, DR19 |
| Lomas | Lomas et al., CHI 2013 (abstract) and "Is difficulty overrated?", CHI 2017 | academic | §A, DR11, DR20 |
| RaoFernandes22 | Rao Fernandes and Levieux, "Difficulty Pacing Impact on Player Motivation", ICEC 2022 (abstract) | academic | §A, DR01 (weak) |
| Mossmann19 | Mossmann et al., *Frontiers in Psychology* 2019 (pilot, n = 7) | academic | §A, DR14 (weak) |
| RhythmGroups | Compton and Mateas, AIIDE 2006 (full text); Smith et al., FDG 2009 and TCIAIG 2010; Sorenson et al., TCIAIG 2011 (abstracts) | academic | DR03, DR06 |
| GameFlow | Sweetser and Wyeth, *Computers in Entertainment* 2005; Denisova et al., CORGIS, IJHCS 2020 | academic | DR12, DR13 |
| vanLankveld08 | van Lankveld, Spronck, Rauterberg, "Difficulty Scaling through Incongruity", AIIDE 2008 | academic | DR05, DR22 |
| Aponte11 | Aponte, Levieux, Natkin (2011), formal definition of difficulty (abstract) | academic | §C.2 |
| Sarkar17 | Sarkar et al., FDG 2017 (abstract) | academic | §C.1 |
| Emmerich17 | Emmerich and Masuch, CHI PLAY 2017 (abstract) | academic | DR25 |
| Depping17 | Depping and Mandryk, CHI PLAY 2017 (abstract) | academic | DR24 |
| WilsonSicart10 | Wilson and Sicart, "Now It's Personal: On Abusive Game Design", FuturePlay 2010 | academic | §A, DR21 |
| McGraw10 | McGraw and Warren, *Psychological Science* 21(8), 2010; McGraw's summary page on benign violation theory | academic | DR22 |
| Ballou23 | Ballou and Deterding, CHI PLAY 2023 (need frustration; applied here by inference) | academic | DR23 |
| Bopp/Tyack | Bopp et al., CHI 2016 and CHI 2018; Tyack and Mekler, CHI 2021 (abstracts) | academic | DR04 |

**Not used:**
- the claims dropped as unverified: CarlSagan42's contest judging criteria, Jump King's area structure, and the "laughter clusters around rescues" result;
- the numbers from Valve's White Forest Inn intensity graph;
- the Getting Over It snake troll;
- the claim that Braid's worlds "open low".

---

## E. Conflicts with existing repo doctrine

| # | Doctrine (file:line) | Conflicts with | Proposed resolution | Needs a decision? |
|---|---|---|---|---|
| E1 | playbook:220-221 "Difficulty rises with biome, not within it."; LBR:170 "difficulty rises between biomes, flat inside one" | DR01 | Separate the rule from the load. The coupling *rule* stays flat inside a biome; the *load* is a sawtooth whose valleys rise. The playbook's reason (master one rule before the next arrives) stays. | User |
| E2 | playbook:254 anti-pattern "Difficulty inside a biome" | DR01 | Rename it "Rule change inside a biome". Its threshold, "the rule changes before it has been mastered", already says this. Add a "Flat load" row (DR01) beside it. | User |
| E3 | level-01-beats.md:70 "difficulty flat inside each" | DR01, DR03 | A historical doc. Leave it. | None |
| E4 | GDD:174 "segment başına tek yeni fikir"; B1 beats:82 rule 5; LBR:64 | DR05, DR14 | Compatible: a segment's valley is its new idea's safe teach. Only a *pure* valley segment needs the user to accept a verb or a view as its one idea. | User (GDD) |
| E5 | recipes.md:20 RX09 (the six-step order); LBR:62-72 | DR01, DR14 | Orthogonal: RX09 orders ideas and DR sets load. Leave RX09 and add RX27, a "rhythm pass" (§F). | None |
| E6 | grammar.md:193 "change only one operator per segment"; EO01–EO12 only escalate | DR04 | Don't add a catalog to the corpus. The DR04 palette is Mixtrol's de-escalation list. Add a row under the corpus README's Known conflicts. | None (listing only) |
| E7 | playbook:110 "Below 3 the segment is corridor"; :252 corridor over ~15 s; LBR:30, :39, :195; GDD:217-218 "o beat koridordur, silinir" | DR04 valleys | A valley beat needs a relief clip sentence (a joke, a view, a lap). Without one, the 15 s cap holds. | User (wording of the GDD test) |
| E8 | GDD:446-450: one Harabe look for every level, so "biome" has no referent | DR14 | For pacing, biome = Bölüm. Acts are declared by the level doc or fixed by B.0's rule. | User |
| E9 | GDD:584: best time is the only replay reason (LBR:145-146 notes that the corpus disagrees) | DR20 | DR20 stays frozen. If adopted, a harder line pays only in time, with no pickups. | User |
| E10 | GDD:306-318, "bugün birinci kademe de yok" | DR04, DR08 and DR22 rely on tier 1 | Count the wells and catch ledges already built as tier 1, as the beat docs do (B1 beats:46-50), and ask for the GDD's tier table to be updated. Until then, "tier 1" in DR22 reads "costs a walk". | User (GDD) |
| E11 | B1 beats:75-76 rule 2 "…bir yürüyüş ya da bir segment kaybettirir" | DR22 (a troll's own cost is a walk or tier 1) | "A walk" stays. Whether a troll may cost a segment is the user's call. The three one-shot traps built today each cost a walk (B1 beats:33-36), so nothing built changes. | User |
| E12 | reference-teardowns.md:31-32 (the developer quote), :34-36 "difficulty rising with altitude", :38-40 "Hardcore… Golden wings from the upper regions"; playbook:120, :209; coop:155-156, :272-273 | §A (Chained Together evidence) | Corrections listed below the table. | Ask (a side issue) |
| E13 | Stale lines found in passing (listed below the table); not rhythm conflicts | — | List them and ask, per the working agreement. | Ask |
| E14 | GDD:219 "Hiçbir şey ölerek öğrenilmez"; GDD:256 the decoy "asla öldürmez"; B1 beats:73-74 rule 1; LBR:79-80, :187 (AP02) | The troll-game research (IWBTG, Kaizo: surprise deaths made cheap by dense saves) | No change to the repo; DR21–DR22 follow it. This doc has no key for a lethal surprise. A troll is a visible, tempting break of a taught rule, and its own cost is a walk or tier 1. Surprise deaths would need the user to reopen GDD:219. | Only if surprise trolls are wanted |
| E15 | GDD:187 "8. Final — renkli tüneller": the tunnel first appears in the finale. DA-18 (MIX-110) is open | DR05, DR18 (no new device in the finale) | Leave the GDD. Until DA-18 is decided, a new device in the finale is a Karar finding, not a Blocker. If the tunnel stays, DR17's low-threat opening of S13 doubles as its safe teach. | User (DA-18) |
| E16 | B1 beats:53-57 (partner windows: S7 ~355 ms, S9 and S11 ~210 ms); :115 (S8's second press, 0.18–0.66 s) | GDD:220-223 (talk-window rule); GDD:207-208 (the spoken channel takes 0.5–1 s); playbook:132-134 and LBR:34 (a window two machines agree on is ≥ 1 s) | The numbers were measured with the air jump, which MIX-95 removed, so they are stale. Re-measure online. Then either widen each to a counted window of ≥ 1 s, or record it as an exception the user approves. Until then the C scale does not rate them (`!`). | User |
| E17 | B3 beats:18 (no death, only falls), :30 (the pad under a gap prices the fall), :59 ("K2 en sert kademe"), :103 (a kademe takes ~2–3 min clean) | DR09 (≤ 60 s replay); T0–T3 | Towers use Tf and the Loss column (§C.2): storey or kademe = tooth, landing = refuge. DR09 is not applied to B3 until the user sets a Loss cap per band. K2's position is only reported (DR16 is open). | User |
| E18 | README:62 marks "at most one one-shot trap per level" **Open**; LBR:152-153 states it as advice; DA-45 (MIX-136) is open | DR23 | DR23 treats the cap as open and only places the traps. | User (DA-45) |

**E12 corrections:**
- The "resisting complexity" line is an indiegame.com writer's analysis, not a developer quote.
- "Difficulty rising with altitude" is not established either way; the evidence is mixed and confounded.
  - Against it: a two-post Steam thread calls Hell the hardest, and derived loss per minute is highest at the bottom. Casual quitters and a Temple achievement bug (patch 1.7.8) confound that figure.
  - For it: subzone length rises by act (CT-sr), and the Garden ends on two "brutal" challenges (CT-TheGamer).
- speedrun.com groups the in-game title cards into three act runs: Hell, City, Heaven. The Steam store copy says Hell through Purgatory toward Heaven.
- The modes are Beginner, Normal and Lava.
- The ten wings start at 0 m. Collecting all ten unlocks a glide toggle in the menu, for later runs only.
- reference-teardowns.md:77-79: the store names checkpoints as the difference between Carry The Glass's modes. It does not say nothing else changes.

**E13 stale lines:**
- LBR:74-75: the gate is said to be first met in the chase, but S0 has taught it since MIX-272. The "Bölüm 2" example there is the deleted horizontal level.
- GDD:164-170 and :179-188: the old 8-segment plan.
- grammar.md:201: EO05.
- bolum-02-beats.md: Kat 7 has been impassable since MIX-277, which is not noted there.
- design-audit.md:97: DA-16.

These agree with the DR rules and need no change:
- playbook:72-74 (chase);
- playbook:122-136 (the Kolay knobs, which DR10 now follows);
- `level-kit.md:295-296` (the costly last move, via DR03's exception);
- FR14 and FP20 (contrast and the success breath);
- GDD:205-213 (chase plus gate);
- GDD:219 and :256 (which DR22 now follows);
- coop:159-161 (betrayal between players).

---

## F. Repo edit map

**Process:**
- No Linear issue exists for this work. Per the few-issues rule, attach it as a checklist on MIX-110 (DA-18, the teaching arc).
- Cite rules by DR ID and restate them nowhere else.
- The only Turkish lines are in the GDD, which is written in Turkish. There are no player-facing strings in this change.

| # | File | Section | Change | Blocked on |
|---|---|---|---|---|
| 1 | `docs/difficulty-rhythm.md` (new) | Whole file | This draft | Adoption |
| 2 | `~/.claude/skills/level-beat-review/SKILL.md` | Frontmatter `description` | Add the triggers "zorluk sırası", "ritim", "rahatlama", "critique / yorumla this level", "is the order right" | — |
| | | `## Biome pacing` (:170) | Replace the bullet with "rule flat, load sawtooth: DR01, DR14" | E1 |
| | | `## Teaching arc` | Add one line: "RX09 orders the ideas; DR03–DR07 set the load; DR27 places sabotage" | — |
| | | `## Anti-patterns` | Rows citing DR IDs only: flat load (DR01); tier-2 after the peak (DR08); troll in the finale (DR18); a valley that lifts the swap (DR25) | — |
| | | New `## Critique procedure` | Three lines: run difficulty-rhythm.md §C with its inputs (LevelNotes, the scene, the beat docs); answer in Turkish; cite DR IDs. Do not copy the rules. | — |
| 3 | `docs/level-design-playbook.md` | `## Biome progression` (:209, :220-221); `## Anti-patterns` (:254) | Rewrite per E1, E2 and E12 | E1, E2 |
| | | After `## Beat construction` | A new `## Difficulty rhythm` section: a two-line pointer to the DR IDs | — |
| 4 | `docs/design-corpus/README.md` | `## Known conflicts` | Three rows: flat-inside-biome vs DR01; RX09 is orthogonal to DR; there is no de-escalation operator in EO, so use the DR04 palette. Row :62 stays Open. | — |
| 5 | `.claude/skills/mechanic-forge/references/recipes.md` | `## RX` | Append **RX27, Rhythm pass**: "Fill the intensity map (difficulty-rhythm.md §C), then fix the worst DR finding first." | — |
| 6 | `.claude/skills/mechanic-forge/SKILL.md` | The table at :20-30 | Add the row "Order these beats / is the pacing right → RX27, DR" | — |
| 7 | `docs/reference-teardowns.md`, `docs/coop-mechanics-playbook.md` | Chained Together (:31-42), Carry The Glass (:77-79) and the Sources section; coop :155-156 and :272-273 | Corrections per E12; one "difficulty order" row in the comparison table pointing to §A | Ask |
| 8 | `docs/gdd.md` | `### Öğretme sırası`, `### Tasarım testleri` | One Turkish line each, only after decisions E4, E7, E8, E10, E15 and E16. For example: "Vadi segmentinin tek yeni fikri bir sonraki cihazın güvenli öğretimi, bir fiil ya da bir manzara olabilir (DR05, DR14)." | User |
| 9 | `docs/design-audit.md` | A new dated section on top, rows from DA-66 | Record the Bölüm 1 findings (§G) once the user confirms them; link DA-18 and DA-45 | User |
| 10 | `docs/bolum-01-beats.md` | `## Segmentler`; `## Ölçülecekler` | Add "Perde" and "Ritim" columns (peak C, question, valley type). Add to the measurement list: clean time, the peak's commit time, attempts per pass and the online partner windows. | §G accepted |
| 11 | `docs/bolum-02-beats.md`, `docs/bolum-03-beats.md` | Their floor tables | The same columns plus Loss (s), when those levels are critiqued | Later; B3 after E17 |
| 12 | `CLAUDE.md` `## Skills` | The design-corpus line | Optional: add "difficulty order: docs/difficulty-rhythm.md (DR IDs)" | Optional |
| 13 | `~/.claude/skills/game-feel/references/feedback-stack.md` | FP22 row | Note that a tier-2 wipe may carry a short sting or line, and that encouragement lands better than mockery (Foddy18). GDD:256's mocking decoy stands. | User |

**Agents:** there is no `.claude/agents/`. The skills in rows 2, 5, 6 and 13 are what agents read, so those rows are the "agent" changes.

**Unchanged:** `grammar.md`, `generator.md`, `level-editor.md`.

---

## G. Demonstration: Bölüm 1, S0–S13

> **Provisional: built from the docs, never played.**
> - Every C is an estimate (E) from the §C.2 proxy, rated at 2 players (B1 is built for 2, GDD:157-158). The 4-player case is unrated.
> - No clean time exists anywhere (B1 beats:251).
> - Positions are given by x across −67..902 (969 m).
> - Acts come from B.0's rule: S0 is the tutorial; A1 = S1–S6 (family `device`); A2 = S7–S11 (`obstacle`); A3 = S12–S13 (set piece + finale).

| Seg | m (D) | Family | New (N) | Peak Q | Peak C (E, conf) | T | P | Win (D) | Troll (D) | Notes (D) |
|---|---|---|---|---|---|---|---|---|---|---|
| S0 | 69 | swap | Swap core + 2 gates (tutorial, exempt) | pw (untimed) | 2 (H) | T0 | — | untimed | — | No death; ~1 min estimated |
| S1 | 83 | device | Cauldron to a delivery plate (N1) | carry | 2 (H) | T0 | — | untimed | bait (shelf) | No hazard |
| S2 | 75 | device | Moving platform (N1) | sync | 3 (M) | T2 | cyc | ? | bet (twin shuttle; returns you) | Pits at x88–104 |
| S3 | 84 | device | Plate + held door (N1) | hold | 2 (L) | T? (door crush undefined, DA-19) | cyc (door shuts 0.7 s after release) | 0.7 s, sabotage only | bet (bait crate) | **3 m columns impassable** (B1 beats:58-60) |
| S4 | 78 | device | Crumbling floor **+** pushable (N1 ×2) | read | 4 (L) | T? (what lies under the tiles is not documented) | cyc (0.6 s crack) | ? | read trick on first contact (only two tiles truly solid) | Push-by-two broken (DA-21) |
| S5 | 83 | device | Launch pad (N1) | sync | 2 (L) | T2 (second pit on overshoot) | — | ? | bet (decoy CP at x334; real CP at x305) | 18 m landing strip (B1 beats:152-153); arc unmeasured; pad height 8 in the doc, `Ped_Yuksek.asset` has uncommitted changes |
| S6 | 86 | device | Seesaw (N1) | hold | 3 (L) | T2? | — | ? | bait (the high side ends at a wall) | **4 m column impassable** |
| S7 | 52.5 | obstacle | Bumper (N1) | pw | 4 (L) | T2 (goo) | cyc | ~355 ms `!` | bait (double bumper) | First beat is a tier-1 teach |
| S8 | 37.75 | obstacle | Propeller **+** bridge well (N1 ×2; the second user-requested) | pw | 4 (L) | T2 behind the slab; T1 at the front gap | cyc + hold (3 s up / 2.2 s down) | 0.48 s `!` (0.18–0.66 s) | — | **Exit impassable**; MIX-210 |
| S9 | 68.75 | obstacle | Hammer (N1) + S3's plates and door (N2) | pw | 4 (L) | T2 | cyc | ~210 ms `!` | — | First combination; the second hammer sweeps the well landing (visible; back-swing into the tier-1 well) |
| S10 | 67.5 | obstacle | Belt **+** rotating bar (N1 ×2), plus S4's crumbling floor (N2) | pw | 4 (L) | T2; the well gap is T1 | cyc | ? | — | |
| S11 | 71 | obstacle | Piston **+** swing (N1 ×2) | pw | 4 (L) | T2 | cyc | ~210 ms `!` | — | **Skip gone** (B1 beats:58-60) |
| S12 | 94 | set | Chase (N1, set piece) + re-deal (the gate, taught in S0: an N2 twist) | sync + read | 4 (L), maximum stakes | T2 | **clk** 5.5 m/s | ? | — | GDD conflict open |
| S13 | 65 | tunnel | Colour tunnel (N1) + goal | blind | 3 (L) | ? | — | ? | — | Tunnel's first contact is in the finale (E15) |

**Curve:** `S0▂ ‖ S1▂ S2▃ S3▂ S4▄ S5▂ S6▃ | S7▄! S8▄! S9▄! S10▄ S11▄! | S12▄ S13▃`

**Reading:**
- **A1 (S1–S6) is a gentle sawtooth with one spike at S4.** S4 brings two devices at an estimated C4, inside the first third. The act runs six segments, against a starting target of 3–5 (Tune).
- **A2 (S7–S11) is a plateau.** Every peak asks `pw`, and four of the five peaks need a sub-second partner window.
- **A3 (S12–S13) has no low-threat stretch** between the set piece and a finale that introduces the tunnel.

**Top findings**

1. **Blocker (repo): S3, S6, the S8 exit, the S11 skip.**
   - *What:* all four have been documented impassable since MIX-95 removed the air jump (B1 beats:58-60).
   - *Evidence:* D (documented impassable geometry).
   - *Proposal:* rebuild them to the rhythm below, not to their old layout. That is a separate issue, per the working agreement.
   - *Withdrawn if:* a group clears each one in Play Mode with the current movement.
   - *Decision:* ask (a side issue).

2. **Major: S4 → S12, DR13 and DR14 (DR01 at low confidence).**
   - *What:*
     - All five A2 peaks ask `pw`, the partner's Space over a goo gap. Before S8's bridge well, the level's own note said four of the five asked the same question (B1 beats:104-105).
     - No valley segment sits between A1's peak (S4) and A2's first peak (S7), or between A2 and the chase (S12).
     - Six segments in a row (S7–S12) are rated C4.
   - *Evidence:* D for the questions (B1 beats:38-42); E (L) for C.
   - *Why:* L4D never deals a Tank straight after a Tank (Booth09). White Forest Inn (Valve14). The breather falls back, but not all the way (Koster25).
   - *Proposal:*
     - Keep A2's peak at S9–S10, which lies at 63–78% of the level by x.
     - Rebuild S11, which needs rebuilding anyway, as A2's valley segment. The jump swap stays the floor (DR25), but the partner's call gets a counted window of ≥ 1 s, a wide margin, and a tier-1 lane underneath.
     - Between S4 and S7, S6 is the cheaper valley candidate, because its column has to be rebuilt anyway.
   - *Withdrawn if:* first-time outside groups keep S7's audible reactions per minute and attempts per pass through S9–S11, or measured C across S7–S11 varies by ≥ 2 levels.
   - *Decision:* user.

3. **Karar + Ölç: S7, S8, S9, S11 (E16).**
   - *What:* the documented partner windows are all under a second: S7 ~355 ms, S9 and S11 ~210 ms (B1 beats:53-57), and the second press of S8's re-climb 0.18–0.66 s (B1 beats:115). They were measured with the air jump. The talk-window rule (GDD:220-223) and the ≥ 1 s cross-machine decision (playbook:132-134) rule them out as peaks.
   - *Evidence:* D (stale).
   - *Proposal:* re-measure online with the 150 ms-each-way preset (playbook:135). Also measure the owner's dash rescue (~0.9–1 s), which is what keeps these beats fair today. Then widen each window to a counted ≥ 1 s, or record it as an approved exception.
   - *Withdrawn if:* the measured online windows are ≥ 1 s.
   - *Decision:* user.

4. **Major: S1–S7, DR23 and DR21 (the cap is open: README:62, DA-45).**
   - *What:*
     - Designer trolls sit in S1, S2, S3, S5, S6 and S7, plus S4's tile trick. There are none in S8–S13.
     - The three one-shot traps LBR:152 names (the twin shuttle in S2, the bait crate in S3, the decoy CP in S5) are all in the first half. One of them is in the first two segments after the tutorial, and no honest segment follows any of them.
     - All three cost a walk, and the decoy never kills (GDD:256), so each passes DR22.
   - *Evidence:* D (B1 beats:31-44).
   - *Why:* Kayin (room to breathe); EGM20 (obvious trolls first, the real one late).
   - *Proposal:* space the trolls so no two consecutive segments carry one, and keep the teaching baits (S1's shelf, S6's high side). How many one-shot traps stay is DA-45. DR23 would put the one that stays in the second half.
   - *Withdrawn if:* every troll in S1–S7 still draws an audible reaction from first-time groups, and S8–S13 does not lose reactions per minute against S1–S7.
   - *Decision:* user (DA-45).

5. **Major: S4, S10, S11, DR05, DR12 and DR21.**
   - *What:*
     - Each of these segments brings two new devices.
     - S4 also puts its trick (only two truly solid tiles) on first contact, and at an estimated C4 it sits inside the first third (S1–S5).
     - S8 also brings two devices, but its second (the bridge well, MIX-213) was requested by the user "level'a zorluk olarak" (B1 beats:104). That decision has been given.
   - *Evidence:* D for the devices; E for C.
   - *Why:* Linehan14, Valve14, Hodent, vanLankveld08.
   - *Proposal:*
     - Take DA-18 option (a) for S4, a split.
     - Split S10 and S11, or make their second device an ingredient met earlier.
     - Check what a wrong tile in S4 costs against GDD:219.
   - *Withdrawn if:* first-time groups clear S4 in ≤ 3 attempts and can name the tile rule after one failure.
   - *Decision:* user (DA-18, MIX-110).

6. **Karar: S12, DR17, DR21 and DR24.**
   - *What:* the gate's re-deal, a twist, is stacked on the set piece. This is the GDD's own open conflict (GDD:205-213; B1 beats:127-132). The gate has been taught in S0 since MIX-272, so this is not first contact.
   - *Evidence:* D.
   - *Proposal:* the GDD's own test. If a stranger group cannot clear S12 in three tries, slow the chase after the gate enough to leave a talk window, or move the gate.
   - *Withdrawn if:* a stranger group clears S12 within three tries.
   - *Decision:* user (GDD).

7. **Karar: S13, E15, DR17 and DR18.**
   - *What:* the finale introduces the colour tunnel (GDD:187 puts it there; DA-18 is open). S13 goes straight into a blind call right after the chase, and no win beat is documented before `LevelGoal`.
   - *Evidence:* D.
   - *Proposal:*
     - If the tunnel stays in the finale: open S13 with ≥ 30 s at C ≤ 2, which is the tunnel's safe teach and counts inside S13. Then the combination, then a 10–20 s win beat before `LevelGoal`. If that does not fit inside 90 s, split S13.
     - If the tunnel moves: teach it at an earlier valley (DA-18 option a).
   - *Withdrawn if:* first-time groups clear S13 in ≤ 3 attempts with no death they cannot attribute.
   - *Decision:* user (DA-18).

**Passes (D or E):**
- **DR15.** S1's peak is C2 (E, H) and its clip sentence exists (B1 beats:87).
- **DR05, first contact in S7–S11.** Each segment's first beat teaches at tier 1 (B1 beats:46-47).
- **DR08 at S12 → S13.** The wall parks at x834 and CP11 sits at x839 (B1 beats:139-142).
- **DR27.** Every segment lists a sabotage window (B1 beats:31-44).
- **S8's pedal bridge** routes a fall into a tier-1 rescue. It is the closest the level comes to RX09's missing recovery-chaos step (LBR:70-71).

**Report only (DR16):** the C4 peaks are spread across S4 and S7–S12 at low confidence, so the hardest beat's position cannot be named yet.

**Unknown until measured:**
- clean time per segment;
- the peak's commit time;
- attempts per pass, from first-time outside groups;
- online partner windows;
- audible reactions per minute;
- where each session stopped;
- 4-player behaviour (DR28).

Every rule that depends on time is open until these arrive: the DR03 lap, DR09, the DR14 valley length, DR17's 30 s, clip density and DR24's refuges.

---

## Critique log

**Applied in full:** 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26 and 27.
- For 25: finding 7 (S9's hammer) was dropped. The hammer is visible, and its back-swing lands in the tier-1 well.
- For 11: the recount gives 6 designer trolls in S1–S7 plus S4's tile trick, not "12 of 13". The three one-shot traps are the ones LBR:152 names.
- For 23: the new columns were added, and DR27 was appended for p2p windows. DR28 was appended for 2–4 players (item 19).

**14 was mostly wrong.** Most of the citations it flagged are in the verified findings and were kept:
- Totten 2011 (BK-14); Filatov15 (BK-13, whose note confirms the beat table is Filatov's own format); MCV15 (PL-01).
- C. Kerr 2015 (PL-30); Brown23 (PL-08, PL-35); Fares/GamingBolt 2021 (PL-22).
- Shacknews 2023 (BF-05, CO-14); U. Ali/GameRant (CT-05, CT-08); Hodent GDC16 (BK-05).
- Lomas CHI 2013 (PR-12); Smith FDG 2009 (PR-11); T. Sala 2013 (BK-02).
- PEAK Hotfix 1.42.a and Patch 1.1.a (CO-05); the PEAK wiki "Campfire" page (CO-03, opened).
- CTG-threads is keyed correctly: the 30–35 h / 95% attempt is the Immortal Buddy Steam thread (CTG-04, CTG-05). speedrun.com holds only the leaderboard times.

What was applied from 14:
- Kahneman93 now cites the full text (TH-04: 22 of 32, 69%).
- The campfire rule now cites the "Play It Your Way" announcement beside the wiki.
- MCV15 no longer sets a threshold (item 18).

**15 was partly wrong.** These claims are in the findings and were kept:
- L4D never deals a Tank straight after a Tank (PL-07).
- Portal 2 playtesters were confused in the lair (PL-08).
- Valve's co-op writing left room to talk (PL-09).
- Chained Together's "3,2,1 Go!" key (CO-19).
- Only Up's delisting, citing stress (TR-15, CO-27).
- The $4.99 price (indiegame26's title).
- Bread & Fred's cute look drawing a casual audience (CO-12).
- "Failure feels almost as good as success" (BF-08).
- Wolpaw's "about the easiest puzzle" (PL-10).
- Valve interviewing players after watching them (PL-35).
- Hayashida's "polite answers" (PL-35).

What was applied from 15:
- "Braid's worlds open low" was removed.
- The crab review is now one review.
- EGM's "hot garbage" list is credited to Defender1031's guide as EGM reports it, with pick-a-path choices and instant-death doors listed separately.
- The fire pit is now "the fire-pit escape at the end of Test Chamber 19", not "Portal's most climactic moment".