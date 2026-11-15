# Factory automation

Build machines and belts that make things on their own, then scale them up (Factorio, shapez, Mini Metro); the core
verb is place and connect.

**Camera (Unity):** an orthographic top-down camera with pan and zoom; a fixed orthographic camera when the whole map
fits the screen; a perspective angled camera with pan and zoom for a 3D look.

First slice: a small grid, a few machines and belts on one fixed simulation tick, one or two products. Not a simulated
world.

## Defaults

- **goal-to-deliver**: One product to deliver, with the count delivered and the target on screen; meeting it opens the
  next goal and a new machine. Why: the factory has a reason to exist, and each goal brings something new to build.
  Break it when: a sandbox with no goals, asked for by the user.
- **ratios-to-balance**: Machines work at different speeds, so one kind feeds a few of the next, and each machine's
  rate shows under the pointer. Why: the layout becomes a puzzle of balance, not rows copied over. Break it when: a
  transport game where the routes are the puzzle, not the machines.

## Feel

- **hand-then-machine**: The first ore is mined by hand with a click, and the first drill placed takes the job over and
  keeps going while you build. Why: the player feels work turn automatic, the genre's first pleasure. Break it when: a
  puzzle of belts and shapes from the start.
- **drag-and-snap**: Belts lay by dragging a line, machines snap to the grid with a ghost that shows their input and
  output sides, and picking one up refunds it in full. Why: building is quick and a change of mind costs nothing.
  Break it when: rebuilding has a price on purpose.
- **see-the-flow**: Every item rides the belt in view; a machine short of input or blocked on output shows a sign, and
  a backed-up belt bunches up. Why: the player finds the bottleneck by looking. Break it when: the factory is run from
  menus and reports.
- **fix-drains**: A fixed bottleneck shows at once: the jam drains, the idle machine starts and the output rate climbs.
  Why: the fix is a pleasure to watch, not a number to read. Break it when: a level judged only by its final product.

## Variants

- **sprawl**: more ore patches, more products, a factory that spreads across the map.
- **tidy**: a small set board, each level one product with the fewest machines.
- **rush**: stations appear over time, lines carry passengers, one overflowing station ends the run.

## Choices that shape the pitch

- **What you build:** belts and machines making goods (default) · lines between stations carrying passengers · trains
  on tracks between towns.
- **Stakes:** goals met at your own pace, no way to fail (default) · a run that ends when one station overflows, with a
  warning first · money from each delivery and a cost to build.
- **View:** flat top-down (default) · the whole map at once · an angled perspective view.
- **Feeling:** the player feels in charge of something bigger than themself by watching a line they built run on its
  own, because every item can be followed and every jam traced.

## Platforms

- PC: click to place, drag to lay belts, R to rotate, right click to pick up, wheel to zoom. Touch: tap to place, drag
  to lay, a rotate button, two-finger pan and pinch zoom; dragging needs a build mode so it does not fight the pan
  *(guess)*.
- Phone: landscape for a sprawling map; portrait only for a small set board (tidy) *(guess)*.
- PC sessions run long (30 min+); phone sessions need one goal per few minutes. Save the whole grid on pause.

## Later

- Power, fluids and a second network to feed.
- Research that unlocks machines.
- Long chains that keep early materials in use.
- Copying a built line as a blueprint.
- Trains, drones and robots that carry goods.
- Creatures that attack the factory.
- Regional prices and hauling between towns.
- Workers and vehicles with their own routes.

## In a mashup

The factory leads production, belts and the signs that show a jam. A survival half leads needs and threats, and the
factory takes over the chores. A tower-defense half leads the waves, and the factory feeds the towers. A management
half leads prices and customers. A puzzle half leads set levels with a best answer.
