# City-builder

Grow a city from empty land, balancing housing, jobs and services; the core verb is zoning and connecting land.

**Camera (Unity):** an angled perspective camera with pan and zoom, clamped to the map (default); a flat top-down
orthographic map; or one static camera for a small island that fits the screen.

## Defaults

- **zone-demand**: A demand meter shows which zone the city wants next (homes, shops or work) and shifts as you
  build. Why: the player knows what to build without reading reports. Break it when: there are no zones, a free town
  painter.
- **tax-and-upkeep**: Taxes come in from homes and shops, roads and services cost upkeep, both on screen; running out
  of money ends the run. Why: growth pays for itself, and the player sees why the money went down. Break it when: a
  calm builder with no money.
- **grow-to-unlock**: The population is on screen with the next milestone and the building it unlocks. Why: there is
  always a next thing to grow toward. Break it when: a sandbox city with everything open.
- **small-first-slice**: One small district, a few zone kinds, one service and simple traffic. Why: a whole simulated
  city is not a first slice. Break it when: never for the first slice.

## Feel

- **paint-and-snap**: Roads are drawn and zones painted by dragging; both snap to a grid with a ghost and the total
  price before release, and land with a sound. Why: a district takes seconds, and the cost is known before it is
  spent. Break it when: buildings are placed one by one, a free-form town toy.
- **grows-by-itself**: Homes and shops rise on zoned land beside a road, a few at a time, each with a short build
  animation. Why: the plan comes alive while the player watches. Break it when: every building is placed by hand.
- **coverage-shows**: A service shows its reach before it is placed, and homes inside it look happier at once. Why:
  the player sees what a service gives before paying. Break it when: the town has no services.
- **jams-show-and-clear**: Cars move on the roads, a jammed road shows in colour and an icon, and after a fix the
  queue visibly drains. Why: problems are seen, not hunted in menus. Break it when: a calm picture town, no traffic.

## Variants

- **planner**: a tight budget, demand to balance, a new jam to fix every few minutes.
- **painter**: no money, pieces that fit together on their own, nothing to fail.
- **pressure**: a hard winter is warned ahead, and the town must be ready in time.

## Choices that shape the pitch

- **What you build:** a city of zones and roads (default) · a small town placed piece by piece that fits itself
  together · a settlement racing a coming winter.
- **Stakes:** money runs out and the run ends (default) · a population target by a deadline · none, a calm builder.
- **Progression:** new buildings at population milestones (default) · a new district once one is full · set
  scenarios with a target each.
- **View:** angled pan and zoom (default) · flat from above · a small island that fits the screen.
- **Feeling:** the player feels order from chaos by fixing a jammed road and watching the traffic clear, because the
  problem shows on the map and the fix shows at once.

## Platforms

- PC: drag with the mouse to draw and paint, right or middle drag to pan, scroll wheel to zoom.
- Touch: one finger draws and paints, two fingers pan and pinch to zoom, so drawing needs a clear mode switch
  *(guess)*. Landscape.
- Session: a few milestones on a phone, long planning sessions on PC; autosave often *(guess)*.

## Later

- Citizens with a home, a job and a route you can follow
- Full traffic, with lanes and routes chosen car by car
- Water, power and waste networks
- Disasters
- Several districts and a region map
- Land, rivers and resources placed for reasons
- Long-run balance of money made and spent
- Policies and tax rates by zone

## In a mashup

The city-builder leads zones, roads and what the city needs. Management leads one business's floor inside the city.
Survival leads the threat and the winter. Tower defense leads the waves, and the city pays for the towers. A colony
sim leads named people with needs when the pitch wants a few lives, not a crowd.
