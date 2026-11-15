# Stealth

Get past or take out guards unseen by reading their routines (Thief, Hitman, Dishonored). Core verb:
watch a routine, then move through its gap.

**Camera (Unity):** a top-down camera that follows the player (orthographic for 2D); a perspective
third-person orbit behind the player in 3D; a first-person camera for a thief's-eye view.

Start with guards on fixed routines and simple sight and hearing rules; team search comes later.

## Defaults

- **guard-routines**: Guards walk set routes and stop at set spots, the same on every try. Why: a
  routine can be watched, learned and slipped past. Break it when: the threat should feel unpredictable
  (a horror hunter that follows noise).
- **steal-and-escape**: One thing to steal or reach and an exit to leave by; once you have it, the music
  changes and the way out is shown. Why: the job has a clear end, and the escape is a tense beat of its
  own. Break it when: there is nothing to take, only a sneak through.
- **caught-retry**: Being caught puts you back at the room start at once, guards back on their routes.
  Why: a mistake costs seconds, so the player tries a new line. Break it when: being caught opens a new
  situation (a cell to escape).

## Feel

- **see-their-sight**: Each guard's sight is drawn on the floor as a cone, and every noise you make
  shows as a ring. Why: the player judges what the character could judge, with no guessing. Break it
  when: not knowing is the fear (horror with no cones).
- **suspicion-builds**: A guard who glimpses you does not raise the alarm at once: a mark over the head
  fills, faster up close and in light, and drains if you slip out of sight. Why: a glimpse is a warning
  the player can escape. Break it when: one look is the end (a strict ghost challenge).
- **search-last-seen**: A guard who loses you walks to the last seen spot, looks around, then goes back
  to the route. Why: the player can trick a guard, and hiding really works. Break it when: the watchers
  are cameras and lasers that never move.
- **shadow-and-noise**: Shadows hide you, light shows you; walking is quiet, running is loud, and the
  floor changes how loud. Why: every step is a choice between speed and silence. Break it when: the
  hiding is social (a crowd or a disguise).

## Variants

- **ghost**: avoid everyone, no knockouts, a puzzle of timing and routes.
- **predator**: take guards down one by one from shadows and ledges, hide the bodies.
- **social**: blend into a crowd or wear a disguise; only a few guards see through it.

## Choices that shape the pitch

- **Approach:** slip past unseen (default) · knock guards out from behind and hide them · walk in
  disguised past guards who may see through it.
- **Preparation:** straight in (default) · scout first, then plant tools and open routes · plan a crew's
  moves and run them together.
- **Caught:** back to the room start (default) · a chase you can end by hiding · captured, with a cell
  to escape.
- **View:** from above (default) · from behind, orbit · first person.
- **Feeling:** the player feels like a master thief by slipping past a guard whose route they watched,
  because the routine was learnable and the sight was drawn.

## Platforms

- Keyboard+mouse: WASD move, Shift to run, Ctrl or C to crouch, mouse aims a top-down look or turns the
  camera in 3D.
- Touch (Pointer): tap to move or a virtual stick; walk speed set by how far the stick is pushed, so
  quiet and loud are one gesture *(guess)*. Top-down plays in portrait or landscape; 3D is landscape.
- Session: one room or job of 3-8 min on a phone; a whole level on PC *(guess)*.

## Later

- Guards that call each other, search as a team and adapt to your favourite trick.
- Daily schedules tied to work, meals and sleep.
- Fire, falling loads and animals as ways past a guard; factions that react to each other.
- A companion who never gives you away.
- Sound that bends around walls and through doors.
- Several routes for every job, by talk, tools or force.

## In a mashup

Stealth leads guards, sight, noise and the alarm. An action half leads the fight once you are seen, and
stealth still decides when the alarm spreads and how it ends. A parkour or platformer half leads
movement and gives rooftop routes. A puzzle half leads hand-made rooms with one way through. A horror
half leads a hunter who cannot be fought, heard before seen.
