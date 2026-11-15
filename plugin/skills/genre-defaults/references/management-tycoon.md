# Management / tycoon

Run a business or a place, balancing money, staff and customers; the core verb is fixing the next bottleneck.

**Camera (Unity):** an angled perspective camera with pan and zoom, clamped to the site (default); one static camera
for a single room that fits the screen; or a top-down view.

## Defaults

- **money-in-out**: Income and costs are both on screen, each with where it comes from. Why: the player can tell why
  the money went down. Break it when: money is hidden on purpose, a cozy shop with no money worries.
- **goals-near-far**: A goal for now, one for the day and one for the run are always on screen. Why: there is always
  a next thing, and a natural place to stop. Break it when: a sandbox with no goals the user asked for.
- **day-summary**: Each day ends with a summary of what was earned and spent, and the game saves there. Why: the day
  closes cleanly, and the next one starts with a plan. Break it when: time runs without days, a factory that never
  stops.

## Feel

- **placement-feedback**: Building snaps to a grid with a ghost preview and its price; placing lands with a snap and
  a sound, and it works at once. Why: every placement answers straight away, so a mistake is cheap. Break it when:
  nothing is placed, or the layout is fixed and the game is the prices.
- **money-ticks**: Money counts up as customers pay, each payment rising from the spot where it was made. Why: the
  player sees the layout earning, coin by coin. Break it when: money moves only between days, a spreadsheet game.
- **watch-them-work**: Customers and staff walk the floor in view, and queues and idle spots show. Why: the player
  finds a problem by watching it. Break it when: the business runs from menus, a trading desk or a stock market.
- **near-done-ding**: A goal close to done shows how close it is, and finishing it rings with a small celebration.
  Why: the next goal pulls the player on. Break it when: there are no goals.

## Variants

- **busy**: a crowd that keeps coming, quick fixes, a rush at peak hours.
- **calm**: a slow trickle, time to arrange things just right, nothing urgent.

## Choices that shape the pitch

- **What you run:** one place you lay out, a shop, park or hospital (default) · a production chain whose ratios are
  the puzzle · a town of services and roads.
- **Stakes:** money runs out and the run ends, winnable at full pace (default) · a score after a few days, no way to
  fail · a sandbox with no money worries.
- **Progression:** new buildings unlocked by goals (default) · expand to a new site and start again stronger
  (prestige) · set scenarios with a target each.
- **View:** angled pan and zoom (default) · one room · from above.
- **Feeling:** the player feels ongoing planning by fixing one bottleneck and spotting the next, because each
  expansion puts pressure somewhere new and the floor shows where.

## Platforms

- PC: click to place, right-click or Escape to cancel, drag or edge to pan, scroll wheel to zoom.
- Touch: tap to place with a confirm, drag to pan, pinch to zoom; no hover, so info shows on tap *(guess)*. One room
  fits portrait; a site needs landscape *(guess)*.
- Session: one in-game day per phone sitting, with the day-summary save as the stop; PC plays many days.

## Later

- Staff with their own needs and moods, inspectable one by one
- Research trees
- Several currencies
- Marketing and rival businesses
- Loans
- Several sites
- A scenario editor
- Long-run balance of money made and spent

## In a mashup

Management leads resource flow and the diagnostics that show it. A life sim leads the daily rhythm and relationships,
and saves stay safe to stop after a day. A roguelite leads how a run ends and what carries over. Cozy building leads
placement tolerance and decoration. An action half, a platformer between shop days, leads its own levels.
