# Pet-raising

Raise and care for a creature that grows from how you treat it; the core verb is a care action and the pet's answer.

**Camera (Unity):** one static camera on a room or garden that fits the screen, orthographic for 2D (default); a
camera from above that follows the player around a garden.

*Thin sources:* there is no source for a pet that grows through stages shaped by its care, or for mood shown in its
face and body. Treat those lines as guesses and playtest them early.

## Defaults

- **few-needs**: A pet has a few needs (food, play, rest), each a bar that falls slowly, and one care action fills
  each. Why: the player always knows what the pet wants. Break it when: the creature has no needs, one to watch and
  pose.
- **sad-not-lost**: A neglected pet turns sad and grows slower, but never falls sick or leaves. Why: the player can
  step away and come back without guilt. Break it when: the user wants the old pocket-pet stakes, a pet that can be
  lost.

## Feel

- **pet-answers**: Petting, feeding or playing gets an instant answer (a hop, a purr, a burst of hearts), different
  for each action and each mood. Why: care feels returned, so the player gives more. Break it when: the aloof pet is
  the joke, a cat that ignores you.
- **alive-when-idle**: Left alone, the pet wanders, naps, plays with a toy and watches the pointer. Why: it seems
  alive, not a menu waiting for clicks. Break it when: a tiny pocket-pet screen of a few pixels is the look.

## Variants

- **doting**: one pet, lots of petting and play, a reaction to everything.
- **visitors**: put out food and toys, and creatures drop by while you are away.
- **garden**: plant the right things, and the creatures that like them move in.

## Choices that shape the pitch

- **The creature:** one pet raised from an egg (default) · visitors drawn by what you leave out, as in Neko Atsume ·
  a garden of creatures that move in, as in Viva Piñata.
- **Stakes:** a sad pet, never a lost one (default) · a pet that falls sick and needs a cure · a pet that runs off if
  neglected long enough.
- **Time:** only while the game is open (default) · on the real clock while away, capped (away time from a UTC timestamp
  saved at the `platform-targets` App lifecycle points: pause on a phone, focus loss on PC).
- **View:** one room (default) · a garden to walk.
- **Feeling:** the player feels affection by caring for the pet and seeing it answer, because every action gets a
  reaction and the pet grows from their care.

## Platforms

- PC: click to feed and play, drag over the pet to stroke it; the pet watches the mouse.
- Touch: the strongest fit: stroke with a finger drag, tap to feed, a light haptic on each answer. On a phone
  "watches the pointer" becomes "watches the last touch" *(guess)*. Portrait.
- Session: short, frequent visits on a phone (1-3 min); longer play sessions on PC *(guess)*.

## Later

- Breeding and passing looks on
- Many pets with their own wants that meet and squabble
- Creatures whose own legs find their way over any ground
- A shop of food, toys and outfits
- Mini-games to play with the pet
- Pets shown to friends or entered in contests (needs a server)
- Where the pet came from, told as a story

## In a mashup

Pet-raising leads care, needs and growth. A creature collector leads catching and battles, and care fills the time
between them. A farming half leads the day, and the creatures help with the work. An idle game leads the real clock
and time away. A racing or fighting half leads its contest, and care sets the pet's strengths.
