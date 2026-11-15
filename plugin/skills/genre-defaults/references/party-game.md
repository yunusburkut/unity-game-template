# Party game

Short rounds several people play on one screen, for laughs (Mario Party, WarioWare, Gang Beasts). Core
verb: join, play a round, laugh at the result.

**Camera (Unity):** a fixed camera on one arena that fits the screen; for a wider stage, a camera that
frames the group and zooms to keep every player in view.

Online level: one screen. Local players join through the Input System PlayerInputManager; bots fill
empty seats. Friends on other machines need the coop-multiplayer pack or a server.

## Defaults

- **press-to-join**: On the title screen each player joins by pressing a button on their device; bots
  fill the empty seats. Why: the game starts in seconds with whoever is in the room, and one person can
  still play. Break it when: the game is made for exactly two people with no seats to fill.
- **short-rounds**: Each round opens with its goal in a word or two, big in the middle, and ends on a
  scoreboard; the first to a few round wins takes the match. Why: a loss is over fast and everyone is
  back in at once. Break it when: one long free-for-all with no score.
- **trailing-help**: Whoever is last gets a small boost or a better pickup in the next round. Why: no one
  falls so far behind that they stop trying. Break it when: the user wants a pure contest.

## Feel

- **slapstick-bodies**: Bodies are a little floppy: shoves, bumps and falls knock players about, and
  getting up is quick. Why: a mistake is funny to watch, and no one sits out for long. Break it when: a
  quiz or a reaction test with no bodies on screen.
- **own-colour**: Every player has a bright colour and a marker over their head, kept through a pile-up
  and on the scoreboard. Why: in the chaos everyone finds themselves at a glance. Break it when: all
  players steer one shared thing.
- **winner-moment**: The round winner gets a beat: a short freeze, a cheer in their colour, their points
  ticking up. Why: the whole room sees who won and reacts together. Break it when: rounds flow straight
  into each other (a non-stop brawl).

## Variants

- **slapstick**: wobbly bodies, shoves and falls that get a laugh.
- **quickfire**: tiny games of a few seconds each, one after another, getting faster.
- **cutthroat**: points can be stolen from the leader, and a late round is worth more.

## Choices that shape the pitch

- **Format:** one arena, a new short round each time (default) · a string of microgames, faster and
  faster · a board you move around, with a minigame after each turn.
- **Sides:** each for themselves (default) · two teams · everyone against one player.
- **Who plays:** friends on one device, bots in empty seats (default) · one person against bots only.
- **View:** one arena (default) · a wider stage that zooms to fit everyone · a 3D arena from one angle.
- **Feeling:** the player feels shared laughter by knocking a friend off the edge a moment before
  falling off too, because bodies react the same way every time and the next round is seconds away.

## Platforms

- PC: gamepads first, one per player; a shared keyboard holds two players at most (WASD and arrows).
  Test with one gamepad plus the keyboard as the minimum.
- Touch (Pointer): one phone is one player against bots, or two players on the halves of a tablet in
  landscape *(guess)*. Landscape.
- Session: a match of 5-10 min; on a phone a single round of 1-2 min *(guess)*.

## Later

- Full ragdoll bodies driven by motors.
- Bots that learn each minigame and play like people.
- A board with dozens of minigames.
- Hats and costumes to unlock.
- An arena editor to build and play in together.
- Friends on other machines, lobbies and matchmaking (needs a server; the coop-multiplayer pack covers
  host/client with friends).
- Voice chat in the game (needs a server).

## In a mashup

The party game leads joining, the rounds, the scoreboard and the bots. A platformer leads movement
inside each round. Racing leads handling, and the party game leads the help for whoever trails and the
score across races. Sports leads the field and its scoring. Fighting leads the moves when the party
brawls. A co-op half leads the shared goal when everyone plays against the game, and the party game
keeps the rounds short and the mistakes funny.
