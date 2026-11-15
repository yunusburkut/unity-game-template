# Soulslike

Hard, deliberate fights; death drops what you carry near a rest point you return to (Dark Souls, Elden Ring, Monster
Hunter). The core verb is read the attack, then answer it.

**Camera (Unity):** a perspective third-person orbit behind the hero, with a lock-on that frames the hero and the
target together; for a 2D soulslike, an orthographic side view that follows the player.

## Defaults

- **drop-on-death**: Death sends the player back to the last bonfire and leaves their souls where they fell; reach them
  to take them back, but die first and they are gone. Why: every death has a cost and a way to win it back. Break it
  when: failure should cost nothing, a boss rush where only the retry matters.
- **bonfire-rest**: Resting at the bonfire heals, refills flasks, saves and spends souls on levels, and ordinary
  enemies come back; the boss waits a short run away. Why: the bonfire is a safe home, and the way back to the boss is
  short enough to try again. Break it when: there are no ordinary enemies, a boss rush with a rest between bosses.

Variety floor (hypothesis): 3 enemy kinds in the first slice, the boss included, each attacking differently.
[miyazaki-1] (loose: enemy variety, not the number)

## Feel

- **stamina-commit**: Attacks, rolls and blocks spend a stamina bar that refills when you pause, and an attack once
  started plays out. Why: every swing is a choice, and greed is punished. Break it when: a fast, free hero, a game of
  long combos.
- **roll-through**: A roll is invulnerable for a moment from its start (numbers in game-feel), so the right move is to
  roll into a blow, not away from it. Why: the player masters timing, not distance. Break it when: blocking and
  deflecting are the defence, a duel where a roll is weak.
- **punish-window**: Enemies, bosses most of all, stop to recover after each string of attacks, the window to hit
  back, and a few hold a wind-up to catch a panicked roll. Why: a fight is a conversation the player learns to read.
  Break it when: enemies are a crowd to cut through, a hack and slash.
- **heal-commits**: Drinking a flask takes a moment that cannot be cancelled, and an enemy can hit through it. Why:
  healing is a choice made in a gap, never a panic button. Break it when: a gentle game for players new to hard fights,
  with instant heals.
- **lock-on**: One input locks on: the camera frames hero and target, and the hero circles and rolls around it. Why:
  the player watches the enemy, never the camera. Break it when: many weak enemies come at once and a lock would hide
  the rest.

## Variants

- **heavy**: slow, weighty blows, a shield held up, hits that stagger.
- **duelist**: a block at the moment of a hit builds up and breaks the enemy's guard.
- **hunter**: one great beast that limps when hurt, loses parts and runs off to rest.

## Choices that shape the pitch

- **Fights:** a short area of enemies, then a boss (default) · a boss rush with a rest between · one great monster to
  hunt.
- **Stakes:** souls dropped, won back once (default) · nothing lost, straight back to the boss · everything lost on
  death, a hard mode.
- **Growth:** levels bought with souls at the bonfire (default) · a weapon made stronger at the bonfire · none, skill
  alone.
- **View:** third-person orbit (default) · 2D side view.
- **Feeling:** the player feels hard-won mastery by beating a boss that killed them again and again, because each death
  taught one more attack and the way back was short.

## Platforms

- PC: WASD and mouse look, left click attack, right click block, Space roll, middle click or Q lock-on; a gamepad is
  the expected way to play, so support it from the start *(guess)*. Touch: a left-thumb stick and right-thumb buttons
  for attack, roll and heal; lock-on becomes a tap on the enemy *(guess)*.
- Phone: landscape only. Exact roll timing on touch is hard; the 2D side-view form suits phones better *(guess)*.
- A boss attempt is 1-5 min; a PC session runs an area and its boss. Save at every bonfire rest.

## Later

- A second phase that changes the boss's moves.
- A connected world of shortcuts back to the bonfires.
- Weapons, armour and builds with weight.
- Giant bosses framed from below.
- Monsters that fight each other in a hunt.
- A story told through items and places.
- Help from other players, or invasions (needs a server).

## In a mashup

The soulslike leads fights, stamina, death and the bonfire. A metroidvania half leads the map and its gates, and the
soulslike leads the benches and dropped souls. An RPG half leads builds and gear. A roguelite half leads the run, and a
death ends it instead of dropping souls. A character-action half leads combos, and stamina keeps them short.
