# Racing

Drive a vehicle to finish first, or to wreck the others; the core verb is taking the corner.

**Camera (Unity):** a perspective chase camera behind the car with damped follow (default); a top-down camera that
follows for a top-down racer; or a cockpit view.

## Defaults

- **laps-and-place**: One closed track and a few laps, with lap and place on screen, then a finish screen with place
  and times. Why: a race needs a line to cross and a place to fight for. Break it when: the race is point to point,
  or a delivery against the clock.
- **rivals-close**: A few rival cars race clean lines and stay close, with a slight catch-up for whoever trails. Why:
  the race stays a race to the last lap. Break it when: a time trial, the same every run, no rivals, no catch-up.

## Feel

- **easy-drift**: Steering is quick but smoothed, and a held drift starts a slide that is easy to hold and to leave.
  Why: a corner is a choice, not a spin the player suffers. Break it when: the user wants a sim, where grip and
  weight are the challenge.
- **brake-to-turn**: A brake slows the car hard and a slower car turns tighter, so every bend can be taken by braking
  before it. Why: a bend the player cannot slow for is a wall. Break it when: no brake on purpose, a toy or an
  endless road whose bends all go at full speed.
- **turn-in**: At racing speed the car turns sharply enough for the tightest bend, and the track is laid out for the
  car's turning circle. Why: a corner is taken with skill, never missed because the car cannot make it. Break it
  when: a sim, where the line and the braking point are the challenge.
- **speed-shows**: The field of view widens and the wind rises with speed; a reduced-motion setting turns it down.
  Why: speed is felt without the car handling worse. Break it when: the view is fixed from above.
- **engine-pitch**: The engine's pitch climbs with speed and drops on a brake or a slide. Why: the ear tracks speed
  while the eyes watch the road. Break it when: the cars are silent on purpose.
- **quick-reset**: Off the track or stuck, one input puts the car back on the road facing the right way, and a jump
  lands straight. Why: a crash costs seconds, never the race. Break it when: wrecking is the game.

## Variants

- **arcade**: grippy until you drift, light cars, quick to recover.
- **grounded**: weight, body roll and braking that has to start early.
- **kart**: tiny turns, hops into drifts, bumps that cost little.

## Choices that shape the pitch

- **Stakes:** a race for place against rivals (default) · a time trial against your own best, the same every time ·
  wreck the others, with a crash replay.
- **Pickups:** none, pure driving (default) · pickups that help whoever trails · boost earned by sliding and near
  misses.
- **Progression:** one track (default) · a cup of tracks in a row · cars and parts unlocked by results.
- **View:** chase (default) · from above · the cockpit.
- **Feeling:** the player feels speed on the edge of control by holding a drift through a corner, because the slide
  is easy to start and leaving it at the right moment pays off.

## Platforms

- PC: WASD or arrows (gas, brake, steer), Shift or Space to drift, R to reset; a gamepad is the natural fit.
- Touch: left and right halves steer, gas is automatic with a brake/drift button, or tilt as an option *(guess)*.
  Landscape.
- Session: one race is 2-4 min, which fits both; a cup is a PC session *(guess)*.

## Later

- Cars that deform and handle worse when hit
- Force feedback and haptics
- Traffic
- Car upgrades and tuning
- A career of cups
- Split-screen races
- Ghost replays shared online (needs a server)
- Online races (needs a server)
- Switching between vehicles

## In a mashup

Racing leads handling; a time trial keeps its rules the same every run, while a race may help whoever trails. An RPG
leads progression. A sandbox leads what the world offers. A creature collector leads the collection and the party,
and racing leads the race itself.
