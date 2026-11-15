# Real-time strategy

Gather, build a base and command an army in real time; the core verb is select and order. Like StarCraft, Age of
Empires or Command & Conquer.

**Camera (Unity):** an angled perspective camera with pan (keys, screen edge) and zoom, clamped to the map; a
top-down orthographic camera for a flat 2D map.

## Defaults

- **enemy-waves**: The enemy base sends waves on a timer, the first one early, each one bigger, with a warning before
  each, and destroying its base wins. Why: pressure comes on a rhythm the player can prepare for. Break it when: two
  sides race to build, which needs a rival AI that builds like a player (Later). [shelley-1], [browder-1]
- **unit-counters**: A few kinds of unit, each told apart by its shape, beat each other in a loop, and each counter
  wins clearly. Why: an army is a choice, and a fight is won by the right mix. Break it when: one kind of unit, where
  numbers win. [shelley-2], [browder-1]
- **orders-obeyed**: A unit does what it was told and never overrides an order on its own, and workers walking to and
  from a resource pass through each other instead of jamming. Why: the player commands, and the economy runs
  without babysitting. Break it when: unruly troops are the point. [tiberian-sun-1], [wyatt-1]

## Feel

- **order-answers**: Every order answers at once: a marker where you clicked, a ring under the selected units and a
  short reply, a voice or a chirp. Why: the player knows the order was heard, even in a crowd. Break it when: orders
  are given only while paused, a slow command game.
- **under-attack**: A fight off screen sounds an alert and pings the minimap where it is, and one input jumps the view
  there. Why: the player never loses a base they could not see. Break it when: the whole map fits the screen.
- **skill-in-the-fight**: A few units handled well beat a bigger crowd left alone: a fast unit can hit and step back,
  and a hurt one pulled out of the fight lives. Why: the player wins by how they use an army, not only by what they
  built. Break it when: armies fight on their own once sent, a game of planning only. [browder-2]

## Variants

- **buildup**: a calm start, a growing economy, one big army for a final push.
- **hold**: no base to destroy, a base to keep through bigger waves until the timer ends.
- **squad**: no base, a handful of units with their own skills, a map to cross.

## Choices that shape the pitch

- **Economy:** workers gather and the base trains (default) · income from points held on the map · none, a set army.
- **The enemy:** a base that sends bigger waves on a timer (default) · survive until a timer runs out · a scripted
  rival that builds along a set plan.
- **Army size:** a small army the player can follow (default) · a handful of named units with skills · crowds of tiny
  units.
- **View:** angled pan and zoom (default) · flat from above.
- **Feeling:** the player feels in command by breaking a wave with an army built for it, because the wave was seen
  coming and the units did exactly as told.

## Platforms

- PC: left-drag box-selects, right-click orders, WASD or the screen edge pans, the wheel zooms, number keys hold
  groups.
- Touch: tap selects, a drag on empty ground box-selects, a tap on ground or an enemy orders, two fingers pan and pinch
  zooms; a select-all button replaces groups *(guess)*. The verb loses the most on a phone, so keep armies small.
- Phone: landscape. A match is 10-20 min on PC; on a phone, a 5-10 min mission *(guess)*.

## Later

- An enemy that scouts, adapts and builds like a player.
- Units that path as a group and hold formation.
- Sides with their own units and timing.
- Fog of war and scouting.
- Upgrades researched at buildings.
- Hero units with skills.
- A campaign of missions with a story.
- Battle sound that changes with distance and place.
- Online matches and ranking (needs a server).

## In a mashup

The RTS leads the economy loop, the orders and the camera. Tower defense leads a base held by placed defences, and
the RTS leads the army that goes out. A city builder leads the base's layout and services. A tactics half leads slow,
careful moves, and the game pauses for orders. A MOBA leads one hero in the middle of the army.
