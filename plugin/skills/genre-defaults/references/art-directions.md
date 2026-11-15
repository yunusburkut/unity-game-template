# Art directions by genre

DESIGN.md Look is the decision; this file only gives options for it. The user's words and pictures win, written in
their own words on the Look lines. A look they name is built as named, even when it is hard to draw.

- **No default look.** The user said nothing about the look: pick a direction from the genre's row below, near the
  hook and the user's words, and mark the Look *guessed*. Choose for this game, not by habit.
- **Never an emoji or a font glyph as art** (figure, tile, icon or HUD), unless the user asks for emoji by name.
- **Every enemy kind has its own silhouette** at play size: a different outline, not a recolour or a resize. The player
  reads apart from all of them.
- **Not a copy.** A named game guides camera, proportions, palette mood and light. Its characters, logos and art are
  not copied; write what to avoid on the Look References line.
- **Colour:** risky colour pairs and "never colour alone" belong to `player-clarity`; the Look names the pairs only.

## Who executes a Look

The user's Blender style skills (for example `pixel-art-style`, `lowpoly-style`, `psx-horror-style`,
`hand-painted-style`, `cartoon-style`, `vector-style`, `hd-2d-style`, when installed) and the `toon-art` pack execute a
Look that names their style. They never pick the look.

## Failures to check, in Unity terms

- Pixel art imported with Bilinear filter or compression: set Filter Mode Point, Compression None, one Pixels Per Unit
  for every sprite, and a Pixel Perfect Camera.
- A camera that moves in sub-pixel steps in a pixel-art game: snap it to the pixel grid.
- Two pixel sizes on one screen (a sprite scaled by a non-whole number).
- Outlines run over noisy meshes: an outline needs clean silhouettes and smoothed normals (the `toon-art` pack bakes
  them).
- A preset palette used as is, with no roles (player, threat, ground, accent).

## Directions that recur among each genre's best games

The model's reading of about six well-received games per genre, mostly recent, not checked game by game. Options to
combine, never a menu shown to the user. A genre not listed: take the nearest row and the user's words.

| Genre | Directions that recur, with an example |
|---|---|
| Platformer | lit hi-bit pixel (*Animal Well*); rubber-hose cartoon (*Pizza Tower*); clean-line low poly (*Neon White*); authentic NES retro (*Shovel Knight*) |
| Action roguelite | heavy-ink mythic painterly (*Hades II*); comic vector 2.5D (*Rogue Legacy 2*); modern 16-bit pixel (*Dead Cells*); chiaroscuro (*Warm Snow*) |
| Survivors-like | gothic pixel (*Vampire Survivors*); high-legibility vector (*Brotato*); 2-bit monochrome chiaroscuro (*20 Minutes Till Dawn*) |
| Roguelike deckbuilder | tactile CRT dither (*Balatro*); creepy tabletop (*Inscryption*); picture-book papercraft (*Wildfrost*); dense GBA pixel (*Cobalt Core*) |
| Farming and cozy | 90s anime pixel (*Fields of Mistria*); vibrant tropical low poly (*Coral Island*); soft pastel gouache 3D (*Slime Rancher 2*) |
| Fishing | gothic low-poly fog (*DREDGE*); pixel sprites in a 3D sea (*Dave the Diver*); lo-fi PS1 (*WEBFISHING*) |
| Horror | PS1 dithered software rendering (*Signalis*, *Crow Country*); grimy lo-fi VHS (*Lethal Company*, *Buckshot Roulette*); claustrophobic minimal (*Iron Lung*) |
| Puzzle | orthographic minimal (*Patrick's Parabox*); ligne claire comic (*Chants of Sennaar*); hand-drawn wobbly grid (*Baba Is You*) |
| Metroidvania | hand-drawn graphic novel (*Nine Sols*); baroque pixel (*Blasphemous 2*); luminous hand-painted 2D (*Hollow Knight*) |
| Tower defence | clean low-poly diorama (*Thronefall*); saturated 2.5D cartoon (*Kingdom Rush*, *Bloons TD 6*); tactile isometric board (*Isle of Arrows*) |
| City builder | grounded historical realism (*Manor Lords*); dieselpunk woodcraft (*Timberborn*, *Frostpunk*); painterly micro-dioramas (*Tiny Glade*) |
| Colony sim | clean minimal pawns (*RimWorld*); hand-drawn cutaway (*Oxygen Not Included*); low-poly medieval timber (*Going Medieval*) |
| Shooter | high-contrast PS1 or Quake (*ULTRAKILL*, *Dusk*); chunky 2.5D sprites (*Boltgun*); volumetric kinetic (*Helldivers 2*) |
| Racing | isometric stylised low poly (*art of rally*); saturated 90s arcade (*Horizon Chase 2*); cockpit realism (*Pacific Drive*) |
| Party and social | physics ragdoll cute (*Party Animals*); flat vector caricature (*Among Us*); chaotic kitchen papercraft (*Overcooked! 2*) |
| Narrative | graphite and woodcut (*Slay the Princess*, *Pentiment*); manga over 3D dioramas (*Citizen Sleeper*); 2.5D volumetric pixel (*Until Then*) |
| Idle | desktop companion (*Rusty's Retirement*); high-contrast vector stage (*The Gnorp Apologue*); escalating collage (*Cookie Clicker*) |
| Auto-battler | tactile inventory grid (*Backpack Battles*); clean vector animals (*Super Auto Pets*); industrial mech diorama (*Mechabellum*) |
| Tactics | illuminated HD-2D (*Triangle Strategy*, *Songs of Conquest*); cel-shaded comic (*Tactical Breach Wizards*); grid pixel minimal (*Into the Breach*) |
| Soulslike | monumental dark fantasy (*Elden Ring*); belle-époque gothic (*Lies of P*); saturated cartoon (*Another Crab's Treasure*) |
| Factory | pristine geometric void (*Shapez 2*); grimy 2D dieselpunk (*Factorio*); first-person industrial (*Satisfactory*) |
| Survival craft | low-poly meshes with volumetric light (*Valheim*); voxel masonry (*Enshrouded*) |
| Action RPG | living oil painting (*No Rest for the Wicked*); gothic chiaroscuro (*Diablo IV*); anime watercolour cel (*Granblue Fantasy: Relink*) |
| Dungeon crawler | torch-lit masonry (*Dark and Darker*); 90s low poly (*Lunacid*); monochrome woodcut (*Cryptmaster*) |
| Hidden object and adventure | pen-and-ink doodle canvas (*Hidden Folks*); satirical caricature (*The Case of the Golden Idol*); cozy pastel flat-lay (*A Little to the Left*) |
| Monster taming | high-detail 2.5D sprites on 3D fields (*Pokémon Black and White 2*); the user's named game first |
