# Beat 'em up

Brawl with many enemies along a scrolling stage; the core verb is a combo that ends in a knockdown. Like Streets of
Rage or Castle Crashers.

**Camera (Unity):** an orthographic side view that follows the player along the stage, with a strip of depth to walk
up and down; a fixed-angle perspective camera that follows, for a 3D brawler.

## Defaults

- **stop-and-go**: The stage scrolls on; the camera stops at each fight until the group is beaten, then an arrow and
  the word Go point the way on. Why: the player always knows when to fight and when to move. Break it when: all
  fights are in one arena, a survival mode of endless waves.
- **food-in-crates**: Barrels and crates break, and some hold food that heals or a bag of points. Why: a hurt player
  has a reason to smash the scenery, and some hope. Break it when: health never comes back on purpose, a one-life
  score run.
- **enemy-bar**: The enemy you hit shows its name and health at the top of the screen. Why: the player sees how close
  the thug is to falling. Break it when: crowds are so big that one bar means nothing, a horde game.

Variety floor (hypothesis): 3 enemy kinds in the first slice, each attacks or moves differently.

## Feel

- **combo-knockdown**: Tapping attack strings a few hits, and the last one knocks the enemy off their feet and away.
  Why: a combo has a beginning and a big end. Break it when: every hit is one heavy blow.
- **grab-and-throw**: Walking into a dazed enemy grabs them, and a throw sends them into the crowd, knocking down
  whoever they hit. Why: one enemy becomes a weapon against the rest. Break it when: enemies are too big or too few
  to throw, a fight with one giant.
- **lane-align**: Attacks nudge you into line with the enemy you face, so standing a little above or below never
  makes a swing miss. Why: the depth strip is the genre's old trap, a miss that looked like a hit. Break it when: the
  stage is flat, one line of fighters with no depth.
- **crowd-breaker**: A special clears the enemies all around you at a small cost to your health. Why: being
  surrounded is never being stuck. Break it when: being surrounded is the danger to avoid, a careful fight.

## Variants

- **arcade**: quick and punchy, enemies drop fast, a score at the end of each stage.
- **heavy**: slower blows that land hard and send people flying.
- **juggle**: launch enemies and keep them in the air, a combo game with levels.

## Choices that shape the pitch

- **Players:** one (default) · two on one keyboard or on gamepads, couch co-op.
- **Stakes:** a few lives, a lost life restarting on the spot (default) · one life, an arcade score run · no lives,
  a retry from the last fight.
- **Growth:** the moves you start with (default) · levels and new moves between stages · weapons picked up from the
  ground, pipes and knives.
- **View:** 2D side view (default) · a 3D street at a set angle.
- **Feeling:** the player feels cathartic power by throwing one thug into a crowd and knocking them all down, because
  the throw is easy and the crowd falls in a chain.

## Platforms

- PC: WASD or arrows move, three keys attack, jump and special; a second player shares the keyboard or takes a
  gamepad. Touch: a left virtual stick and three buttons on the right *(guess)*.
- Phone: landscape.
- A stage is 5-10 min on both *(guess)*.

## Later

- Enemy groups whose roles work together: a shield, a thrower, a leader.
- More stages, each ending on a boss.
- A cast of heroes with different moves.
- A late move that adds a new tool.
- Weapons that break after a few hits.
- Bonus stages, a car to smash.
- Online co-op (the coop-multiplayer pack: FishNet + Unity Relay).

## In a mashup

The beat 'em up leads crowds, combos and the stage's stop and go. A character-action half leads style, dodges and
juggles. An RPG half leads levels and gear, and the brawling stays simple. A platformer half leads the jumps between
fights. A fighting half leads move lists, and the stage stays a street full of thugs.
