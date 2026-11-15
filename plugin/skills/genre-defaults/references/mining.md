# Mining

Dig down, collect ore, sell it and upgrade to dig deeper; the core verb is dig.

**Camera (Unity):** orthographic side view that follows the digger down (Cinemachine Position Composer); a
top-down follow camera for digging from above. A Tilemap holds the ground.

Thin research: one sourced entry (tool tiers that gate materials). Fuel, the bag and the trip back up rest on
survival and push-your-luck entries from other genres.

## Defaults

- **dig-sell-upgrade**: Dig down, fill the bag, ride back up to sell, then buy a better drill, a bigger bag or
  a bigger tank; the shop shows what each upgrade does, and each costs more than the last. Why: the whole loop
  is clear from the first trip. Break it when: there is no way back up, one long dive to the bottom.
- **fuel-runs-down**: Fuel runs down as you dig and shows on screen beside how full the bag is; running dry
  hauls you to the surface with part of the haul lost. Why: each trip is a choice of how deep to go before
  turning back. Break it when: a calm dig with no limit.
- **deeper-richer**: Each layer down looks different and holds better ore and harder rock, and a rock the drill
  cannot break yet says what it needs. Why: the locked rock gives the next upgrade a purpose. Break it when:
  a short arcade dig with one kind of rock, where the route is the game.

## Feel

- **dig-crunch**: Each block cracks in steps under the drill, with its own sound and a spray of flakes: dirt
  goes fast, stone takes a moment, and each drill upgrade cuts visibly faster. Why: the hundredth block still
  feels good to break. Break it when: digging is one tap per block, a puzzle of where to dig.
- **ore-glints**: Ore glints in the rock a little before you reach it, and picked-up ore flies into the bag
  with its own chime. Why: the player steers toward the next find, and every find is a small win. Break it when:
  finding ore is the mystery, and a scanner upgrade shows it.
- **sell-rush**: Back at the surface, the bag empties one ore at a time with the money counting up. Why: the
  trip's payoff lands in one rush. Break it when: ore sells the moment it is dug.

## Variants

- **steady**: Plenty of fuel, dig and sell at your own pace, every tunnel stays as you left it.
- **greedy**: Fuel goes fast, the best ore lies deep, and every trip is a gamble on how far to go.

## Choices that shape the pitch

- **The trip:** dig down and ride back up to sell (default) · dig between waves, then race up to defend the
  base on the surface · one long dive to the bottom, no way back.
- **Stakes:** running dry costs part of the haul (default) · falls and lava hurt the hull, and a wreck ends
  the run · no limit, dig at your own pace.
- **The ground:** generated from a seed each game (default) · one hand-made mine with secrets.
- **View:** a side view (default) · from above.
- **Feeling:** the player feels greedy tension by digging one block deeper for a rare ore with the tank nearly
  dry, because the way up is long and the haul is safe only once it is sold.

## Platforms

- PC: arrows or WASD steer the drill into the block ahead; the mouse runs the shop.
- Touch: a virtual stick, or hold a Pointer press on the side of the digger to dig that way *(guess)*. Portrait
  shows more depth on a dig-down mine *(guess)*.
- Session: one trip is 1-3 minutes, which fits a phone; save the mine and the haul on `OnApplicationPause`.

## Later

- Monster waves to defend between digs
- New tools that open new materials and regions
- Explosives, cave-ins and falling rock
- Drills that mine on their own while you dig
- Starting over deeper with a bonus, a prestige reset
- Hidden rooms, relics and a story underground

## In a mashup

Mining leads the dig, the trip and the haul, and the economy prices the upgrades. A tower-defense half leads
the waves, and mining pays for the defences. A survival half leads needs and the base. A platformer half leads
movement and jumps in the tunnels. A roguelite half leads the run and what carries over after a wreck.
