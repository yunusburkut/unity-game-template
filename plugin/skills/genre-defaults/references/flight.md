# Flight

Fly a plane, glider or ship through the air or space (Star Fox, Pilotwings, Elite). Core verb: steer and
trade height for speed.

**Camera (Unity):** a perspective chase camera behind the craft; a first-person cockpit camera; an
orthographic side view that follows a glider.

Start with simple arcade handling of your own (forward speed, bank, pitch). A real flight model with
lift and stalls comes later, if ever.

## Defaults

- **course-and-goal**: A short course with a goal from the first second: rings to fly through, a pad to
  land on, or a far landmark always in view. Goal and time on screen, then a results screen. Why: an
  open sky gets a purpose at once. Break it when: free flight to explore is the point.
- **soft-ground**: Grazing the ground or a wall bounces and slows the craft, never an instant wreck. A
  real crash puts you back in the air a moment later near the spot. Why: a mistake costs seconds, not
  the flight. Break it when: the landing is the challenge and a crash ends the run.

## Feel

- **self-leveling**: The craft always moves forward, banks into turns and levels out when you let go, so
  it never tumbles. An option inverts up and down. Why: the player flies well from the first second.
  Break it when: the user wants a sim with full rolls, stalls and spins.
- **dive-for-speed**: Diving builds speed and climbing spends it; height is a store the player trades.
  Why: flight gets a rhythm of dive and climb. Break it when: speed is fixed (a rail shooter).
- **speed-in-the-air**: The view pulls back and widens (field of view up) and the wind rises with speed;
  clouds and ground streak past. A reduced-motion option turns it down. Why: speed is felt without
  worse handling. Break it when: calm is the point (a balloon or glider ride).
- **height-reads**: The craft casts a shadow on the ground, the horizon stays in view, and near the
  ground the camera tips to show what comes. Why: the player always knows which way is up and how far
  the ground is. Break it when: deep space, where a speed marker and far stars do the job.

## Variants

- **ace**: fast, a quick roll to dodge, a stream of targets to shoot.
- **glider**: no engine, rising air and long dives keep you up, a quiet sky.
- **drift**: the space ship keeps drifting; thrusters turn and slow it, and arriving is a skill.

## Choices that shape the pitch

- **What you fly:** a plane over land and sea (default) · a glider riding rising air · a ship in space
  that drifts until you slow it.
- **Stakes:** rings against the clock (default) · a dogfight with rival craft on simple patterns ·
  reach a far landmark and land there.
- **View:** behind the craft, chase (default) · the cockpit · a side view of a glider.
- **Feeling:** the player feels free by trading a long dive for the climb over a ridge, because speed
  and height are theirs to spend.

## Platforms

- Keyboard+mouse: W/S pitch, A/D bank, Shift/Ctrl throttle; or mouse steers toward the pointer
  *(guess)*. A gamepad stick fits best.
- Touch (Pointer): drag anywhere as a virtual stick, or tilt with the accelerometer as an option
  *(guess)*. Landscape on phones.
- Session: one course (1-3 min) per phone sitting; longer free flights on PC *(guess)*.

## Later

- A real flight model with lift, stalls and spins.
- Orbits and gravity around planets.
- Enemy aces that fly and fight on their own.
- Landing on a runway with a flare and a score.
- Switching from glider to parachute to wingsuit in the air.
- Trading between stations, with cargo at risk.
- Joysticks, throttles and rumble.
- Ships lost for good in a shared space (needs a server).

## In a mashup

Flight leads handling, the camera and how speed is shown. A shooter half leads weapons and enemy
patterns, and flight keeps the craft readable. A racing half leads the course, the rivals and the laps.
A trading half leads prices between ports or stations, and flight is the trip. An exploration half
leads landmarks and what is found.
