# Colony sim

Colonists' needs and moods drive a small settlement's stories; the core verb is give orders.

**Camera (Unity):** top-down orthographic camera with pan and zoom (zoom changes the orthographic size); one
fixed camera for a small base that fits the screen. A first slice is a few colonists, one small base and a day
or two, with needs and moods kept few and readable, never a deep simulation.

## Defaults

- **named-colonists**: A few colonists, each with a name, a face and one or two traits that change how they
  act. Why: events happen to people the player knows, and that is where the stories come from. Break it when:
  the workers are a faceless swarm, an ant farm.
- **orders-not-steering**: You mark jobs (dig here, build that, carry this), and colonists take them by priority;
  the clock can be paused or sped up while you plan. Why: the player plans and the colony works, the heart of
  the genre. Break it when: one colonist is a hero you steer by hand, a survival game.
- **setbacks-not-endings**: A bad turn changes the game rather than ending it: the injured rest in bed, a burnt
  room is rebuilt, a lost fight costs supplies, and the run ends only when no one is left. Why: the colony's
  trouble is the story, not a reload. Break it when: one life that ends the run is asked for.

## Feel

- **mood-with-reasons**: Each colonist's mood shows on them and lists its reasons, a good meal, a cold night,
  a friend hurt, each small and named. Why: the player reads how the colony feels and can act on it. Break it
  when: the workers are robots with no moods, a logistics colony.
- **watch-them-live**: Colonists walk to work, eat at the table, chat on breaks and sleep in their beds where
  you can watch, and selecting one shows what they are doing and why. Why: the colony runs on its own, and the
  cause of a problem is one tap away. Break it when: the colony is run from reports.
- **stories-happen**: Small events start on their own, a quarrel between two who dislike each other, a breakdown
  at low mood, a stranger at the gate, and a log line names each one. Why: the colony writes its own stories,
  the reason the genre is played. Break it when: a calm build with no events.

## Variants

- **gentle**: Kind colonists, rare events, the slow build of a home.
- **harsh**: Raids, hunger and cold, a colony on the edge.
- **chaotic**: Many events and odd traits, and the fun is in what goes wrong.

## Choices that shape the pitch

- **The setting:** a crash-landed crew on a strange world (default) · dwarves digging into a mountain · a base
  under the sea or in space, where air is the need.
- **The pressure:** a raid warned ahead, with time to prepare (default) · winter coming and food running short
  · none, a gentle build.
- **Stakes:** setbacks first, and the run ends when no one is left (default) · a goal to reach, a ship to build
  and leave on · none.
- **The map:** a small generated patch (default) · a hand-made one.
- **View:** flat from above with pan and zoom (default) · a small base that fits the screen.
- **Feeling:** the player feels responsible for a few lives by planning around their moods and needs, because
  each colonist is named and the reasons for their mood are shown.

## Platforms

- PC: mouse drag or WASD pans, the wheel zooms, drag a box to mark jobs, Space pauses, 1-3 set speed.
- Touch: one-finger drag pans, pinch zooms (`EnhancedTouch`, with the wheel as the PC fallback), a mode button
  turns drag into marking jobs; landscape.
- Session: PC sessions run for hours; phone play is short check-ins, so pause on `OnApplicationPause` and save
  *(guess)*.

## Later

- Relationships, rivalries and gossip that spread
- Deep needs: temperature, air, sickness, wounds by body part
- A world map with several colonies
- Colonists who come back changed by what happened
- A storyteller that paces the events
- Research and new buildings
- Trade with visitors and other settlements

## In a mashup

The colony sim leads needs, moods and jobs. A city builder leads zones and roads when the colony grows into a
town. Survival-crafting leads one hero's hunger when the player steers a single colonist. A tactics half leads
the fight when a raid arrives. Management leads the money when the colony trades.
