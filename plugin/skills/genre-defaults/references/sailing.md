# Sailing

Sail a ship with the wind, explore the sea and fight other ships (Sea of Thieves, Sid Meier's Pirates!).
Core verb: set the sail to the wind and steer.

**Camera (Unity):** a perspective chase camera behind and above the ship; a top-down camera that follows
the ship for a sea seen from above.

Start with simple rules of your own: one wind, a sail setting, turn rate and speed. No wave or
buoyancy simulation in the first slice.

Research gap: the CCGS sources covered water, waves, flooding and the wind in a chase, and had nothing on
broadside cannons, sails as the throttle, or a goal for the voyage.

## Defaults

- **sink-to-port**: Hits make leaks that slowly fill the ship and can be patched; a sunk ship washes up
  at the last port with its cargo lost, not the game. Why: a lost fight costs a haul, never the voyage.
  Break it when: one ship and one life (a hard run).

## Feel

- **read-the-wind**: One wind blows, shown by a flag, an arrow and the sails filling; across it is
  fastest, straight into it the ship slows to a crawl. Why: the sea has a rule the player can read and
  use. Break it when: a motor boat, where the wind is only weather.
- **ship-on-swell**: The ship rolls and pitches on the swell, spray rises at the bow with speed, a wake
  trails behind. Why: speed and weight are felt without a number. Break it when: a flat sea seen from
  above, where the wake alone shows speed.

## Variants

- **voyage**: a wide sea, islands to find, rare fights, the wind the only clock.
- **battle**: slow ships, broadsides at close range, a duel won by position and the wind.
- **nimble**: a small fast boat, quick turns through the wind, races round buoys.

## Choices that shape the pitch

- **What you do:** sail between islands to find treasure (default) · fight ships with broadsides ·
  trade cargo between ports · race round buoys.
- **Stakes:** a sunk ship washes up at port, cargo lost (default) · one ship, sinking ends it · no
  fighting, a calm voyage.
- **Crew:** you sail alone (default) · two players on one screen, one steers and one fires.
- **View:** behind the ship, chase (default) · from above.
- **Feeling:** the player feels seamanship by catching the wind to close on a fleeing ship and turning
  to fire, because the wind's rule was theirs to learn.

## Platforms

- Keyboard+mouse: A/D steer, W/S raise and lower sail, mouse aims and clicks to fire a broadside.
- Touch (Pointer): a steering wheel or drag on the left, a sail slider and fire buttons per side on the
  right *(guess)*. Landscape on phones.
- Session: one voyage between two ports (5-10 min) on a phone; longer on PC *(guess)*. Save at each port.

## Later

- Real waves and buoyancy; ships that flood and list.
- Waves that hide ships and spoil aim.
- Rival ships that sail, chase and flee on their own.
- Trade between ports with changing prices.
- Storms and a wind that changes.
- Boarding fights on deck.
- A crew of players sharing jobs in a storm (needs a server).

## In a mashup

Sailing leads the ship, the wind and the sea. A trading half leads prices and cargo, and sailing is the
trip between ports. An action-adventure half leads the islands on foot. A fishing half leads the catch,
and sailing reaches the spots. A naval strategy half leads fleets and turns, and sailing gives each
ship its handling.
