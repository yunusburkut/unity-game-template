# __GAME__: design plan

Working title. TODO: one paragraph on the game and the feeling it is after, ending with the hook: "like <a known
game>, and also <the unique thing>". If the "and also" sparks no curiosity, rework it.

## Pillars

3-5 at most; more means none of them is non-negotiable. Each one is falsifiable ("combat rewards patience over
aggression", never "fun gameplay") and decides a real choice. A pillar that never conflicts with anything is too vague.
Pillars bind the art, audio and UI too. When two pillars clash, the higher one wins.

1. TODO: pillar. Test: between __ and __, this pillar picks __.

Not this game (1-3 anti-pillars: something worth adding that the game refuses, and the pillar it would hurt):

- TODO: not __, because it hurts pillar __.

Scope-cut order when time runs out: first a feature that serves no pillar; then one that serves a pillar at a high
cost for its impact; then simplify the rest to the smallest version that still serves its pillar. A pillar itself is
never cut. A cut relaxes what must exist, never what must work.

Kill condition: TODO: stop or pivot if <a playtest result> after <N> playtests.

## Look

Written from the user's words and pictures; a line inferred without them is marked *guessed*. A line that narrows no
choice is cut.

- Mood: TODO (a few words; menu, play, danger, win and lose must differ at a glance).
- Camera and scale: TODO (view, reference resolution; pixel art: its Pixels Per Unit).
- Palette: TODO (5-7 colours, each with a role: player, threat, reward, ground, accent; shadows cooler, lights warmer
  unless the user says otherwise). Every HUD and state colour and the risky pairs it uses (red/green, red/brown,
  blue/purple, green/yellow): TODO, each with its backup cue: shape, icon or text (player-clarity CL09, CL37).
- Readability: the player and hazards hold the extreme values, the background a narrower range; detail stays out of
  the play area. TODO: exceptions.
- Voice: TODO (player-clarity §E defaults unless stated: person, word budget, words never used).
- Carriers: TODO (the characters, world objects and narrator that carry instructions; player-clarity CL05).
- References: TODO (3-5 games: what to take, what to avoid; take the direction, never their characters or art).
- Made with: TODO (the pack or the Blender style sheet that executes this Look, for example the `toon-art` pack or
  `lowpoly-style`; style sheets are not in the skill listing: `blender-director` reads them from
  `~/.claude/spares/blender-skills/<name>/SKILL.md`, so route art through it).

## Rules (as built)

TODO: the rules in bold-term bullets, written as they are in the code, not as planned. Update with every rule change.

A numeric rule is written as: the expression with named variables; a table `Symbol | Type | Range | Source (Config
field, calculated, constant) | Meaning`; the output range (min and max over the input ranges, and which inputs give
each; flag any reachable value the game cannot use, such as negative damage or a divide by zero); one worked example
with the real values from the Config asset. An edge case is written `If <condition>: <exact outcome>`; one with no
outcome goes to Open questions.

## Levels

Written and read by `level-beat-review`; fill it once the first level exists.

- Units: beat = TODO, segment = TODO, act = TODO, world = TODO (what each is in this game).
- Escalation operators: TODO (each config knob that raises difficulty without a new mechanic).
- One line per level: `Level <n>: <moment sentence> | clean time <s> | peak C <value>`.
TODO

## Platforms

| | PC | Mobile | WebGL (itch.io playtests) |
|---|---|---|---|
| Input | TODO (keyboard + mouse) | TODO (tap, swipe, drag) | TODO (mouse; touch too if phone browsers are in scope) |
| Orientation / window | TODO | TODO | TODO (canvas size, fullscreen button) |
| Session length | TODO | TODO | TODO (a short playtest) |
| Monetisation | TODO (premium / free with ads / free with IAP) | TODO (premium / free with ads / free with IAP) | none (free playtest builds) |
| Frame target | vSync | 60 fps | browser refresh (requestAnimationFrame) |
| Languages | TODO (Turkish / English) | TODO (Turkish / English) | TODO (as PC) |

## Architecture

- Rules: `__GAME__.Core`, plain value types and static steps, testable in EditMode (tests only after the user's OK).
- Unity glue: `__GAME__.Game`, views listen to the simulation and never decide rules.
- Feel: presentation only; the simulation does not know it exists.

## Open questions

TODO

## Decisions

One line each: `YYYY-MM-DD: decision. Why. Rejected: <alternative> (<reason>).` Add the Rejected part only when a real
alternative was weighed. A reversal edits its line (new date and text, the old text kept as `was: ...`) instead of
adding a second line that contradicts it. A prototype verdict is one line in the format `gamekit:prototype` gives.
TODO

## Playtests

One entry each, two lines:
`YYYY-MM-DD, build tag, who / device / input, first time or returning, minutes played: question tested.`
`First 5 min: goal and controls understood (yes / partly / no), mood in the player's words; top 3 observations; what
changed.`

The first playable passes when: a person played with no help from the developer; the game showed what to do within 2
minutes; no bug stopped the fun; the player (never the AI) said the core mechanic felt good; one full start, challenge
and resolution loop worked.
TODO
