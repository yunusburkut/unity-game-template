# Turn-based JRPG

Party battles fought in turns chosen from a menu; the core verb is pick a command.

**Camera (Unity):** a top-down follow camera for the world; one fixed camera on a side-on battle screen; a fixed
perspective camera for a 3D battle stage. A first slice is a short dungeon of a few battles and a boss.

Thin research: the sources cover direct battle commands, party rules and gear that teaches skills, not set party
roles, enemy weaknesses or turn order beyond showing an enemy's next move.

## Defaults

- **retry-battle**: A lost battle offers to retry it at once, from its first turn, with the party as it came
  in. Why: a loss teaches without wiping progress. Break it when: a real game over is asked for.

Variety floor (hypothesis): 3 enemy kinds in the first slice.

## Feel

- **quick-commands**: Attack, skill, item and guard sit on fixed inputs, the cursor remembers each hero's last
  choice, and an action starts the moment it is picked. Why: the hundredth battle is as quick as the first. Break
  it when: battles are rare and slow on purpose, each one a set piece.
- **turn-order**: A strip shows who acts next, heroes and enemies, and a big enemy attack is announced a turn
  before it lands. Why: the player plans ahead, and guards or heals before the hit. Break it when: a plain
  fight where planning ahead is not the point.
- **damage-pop**: Damage numbers pop from the target on their own arcs, a weakness or a critical hit lands bigger
  and louder, and a health bar drains with a trailing ghost. Why: every hit is read at a glance. Break it when:
  health is hidden on purpose, a story battle.
- **victory-tally**: A won battle ends on a short fanfare, experience and gold count up, and a level-up rings
  with what grew. Why: each fight ends on a reward the player sees. Break it when: battles flow into each other
  with no break, a boss rush.

## Variants

- **classic**: Each hero picks in turn, a calm menu, battles won by the right matchup.
- **timed**: A press as a hit lands does more, and one as the enemy's hit lands blocks it.
- **rules**: The party acts on its own from rules you set, and you step in to override.

## Choices that shape the pitch

- **Battles:** turns picked from a menu in a fixed order (default) · a gauge that fills for each fighter,
  and the enemy does not wait · timed presses on each hit.
- **The world:** a short dungeon of a few rooms to a boss (default) · a small town and a route · battles only,
  one after another.
- **Encounters:** enemies seen on the map and touched to fight (default) · random battles on a route · set
  battles only.
- **Growth:** levels from experience (default) · gear that teaches skills · jobs swapped between battles.
- **View:** a top-down world and a side-on battle (default) · a 3D battle stage.
- **Feeling:** the player feels like a careful leader by guarding the turn before a big hit and winning, because
  the turn order and the warning showed it coming.

## Platforms

- PC: arrows or WASD plus Enter/Esc drive the menu; the mouse clicks the same buttons.
- Touch: every command is a uGUI button the Pointer taps, so one path serves both; tap-to-move on the map. Portrait
  fits a menu battle *(guess)*.
- Session: a phone gets short sessions and can kill the app: save on `OnApplicationPause`; inside a battle
  keep the state from when it began, so a killed app resumes the battle from its first turn.

## Later

- A story told in scenes and dialogue
- Towns, shops and side quests
- Gear that teaches skills
- Party rules set ahead of battles
- Jobs and skill boards
- A card game or another mini-game in a town
- Summons and special moves that charge over a battle
- Rest spots that heal the party and bring enemies back

## In a mashup

The JRPG leads the battle: the menu, the turn order and the party. An adventure half leads the world and the
route between battles. A creature collector leads the collection, and the party is caught. A deckbuilder leads the
commands, and skills become cards. An action half leads timed presses on each hit, and the menu still leads the turn.
