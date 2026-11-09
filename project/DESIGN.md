# __GAME__: design plan

Working title. TODO: one paragraph on the game and the feeling it is after.

## Rules (as built)

TODO: the rules in bold-term bullets, written as they are in the code, not as planned. Update with every rule change.

## Platforms

| | PC | Mobile |
|---|---|---|
| Input | TODO (keyboard + mouse) | TODO (tap, swipe, drag) |
| Orientation / window | TODO | TODO |
| Session length | TODO | TODO |
| Frame target | vSync | 60 fps |

## Architecture

- Rules: `__GAME__.Core`, plain value types and static steps, tested in EditMode.
- Unity glue: `__GAME__.Game`, views listen to the simulation and never decide rules.
- Feel: presentation only; the simulation does not know it exists.

## Open questions

TODO

## Decisions

One line each: `YYYY-MM-DD: decision. Why. (PR #n)`
TODO

## Playtests

One entry each: `YYYY-MM-DD, build tag, who / device`: top 3 observations; what changed.
TODO
