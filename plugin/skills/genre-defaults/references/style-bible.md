# Style bible: a named game's look as numbers, then every asset gated against them

Claude-made 3D art looks generic ("AI slop") when nothing pins the style before modelling: palette, value range,
budgets and shading are invented per asset. The style bible fixes them once per game in `Tools/Blender/Style/`, and
every Blender asset is then measured against it. It runs before the first Blender asset of a game whose DESIGN.md
Look names reference games, or when the user asks for assets "like game X". Shape matching from one reference image
stays `blender-image-to-3d`'s job; this adds the style layer around it. Export stays `unity-export`.

Not a copy: a named game guides palette, value range, proportions, detail density, shading and light. Its characters,
logos, layouts and distinctive designs are never rebuilt, and its screenshots stay reference only: never under
`Assets/`, never shipped, never used to train a model.

Scripts, run headless with Blender's own numpy and OpenImageIO. They sit in the `scripts` folder beside this file's
`references` folder: this file is `<skill>/references/style-bible.md`, so `S=<skill>/scripts`, with `<skill>` taken
from the absolute path this file was read at (the genre-defaults skill's base directory). No environment variable
holds it in a Bash call.

| Script | Input | Output |
|---|---|---|
| `$S/extract_style.py` | screenshots or `crops.json` | `style_metrics.json`, a swatch strip |
| `$S/style_gate.py` | the asset's saved `.blend`, `style.json` | PASS, or exit 1 with each failure's rule and number |
| `$S/contact_sheet.py` | the `.blend`, `style.json`, reference crops | review sheet PNG and its `.json` |

Every call is `blender --background --factory-startup --python-exit-code 1 [<asset>.blend] --python "$S/<script>" --
<args>`; each script's header lists its arguments. Without `--python-exit-code 1` a crash exits 0 and reads as a pass.
`<skill>/evals/test_style_bible.py` is their fixture test (template `test-all.ps1`).

## 1. Make the bible (once per game, about 1-2 h)

1. Ask the user for 1-3 games, what to take from each (colour, shapes, shading, detail level), the game's camera
   (top-down, isometric, third person, first person, side) and platform. A seen choice between readings goes on a
   decision page (`<skill>/../pipeline/references/decision-page.md`).
2. The user drops 10-20 of their own screenshots per game into `Tools/Blender/Style/reference/<Game>/`: several
   distances, little UI, a few evenly lit, at least 3 from the camera this game will use. The shots are another
   game's art: they stay on this machine (the game's `.gitignore` ignores `reference/`, and `anchors/`, whose sheets
   show crops of them: step 6); the bible keeps only numbers.
3. Look at each shot (Read) and write `Tools/Blender/Style/crops.json`, a list of rects in pixels from the top left
   of the shot itself (`"file"` is relative to `crops.json`'s folder; an entry without `"rect"` uses the whole shot).
   Read may show a large shot scaled down, so its preview's pixels are not the shot's: take each shot's size from
   step 4's `CROP` lines (`CROP 1 shot01.png: image 2560x1440, rect [0, 0, 2560, 1440]`; a first run on entries
   without `"rect"` prints them) and scale the rects to it:
   ```json
   [{"file": "reference/<Game>/shot01.png", "rect": [410, 300, 220, 160], "note": "flat-lit wall, mid distance"},
    {"file": "reference/<Game>/shot04.png", "rect": [880, 520, 140, 150], "kind": "object", "class": "prop"}]
   ```
   Two kinds of rect:
   - surface crops (the default): evenly lit surfaces of the kind of asset this game needs, for the numbers. Leave
     out UI, fog, bloom, motion blur and night scenes: the numbers measure the graded frame, not the albedo.
   - object crops, `"kind": "object", "class": "prop"`: 1-2 whole objects per asset class from each game, tight
     round the object, at the game camera. The sheet shows them beside every asset of that class, so silhouette and
     proportion have a reference (a crop larger than the sheet's tile is drawn smaller than the asset's scale:
     step 2.4); `extract_style` skips them, and a `crops.json` of object crops alone stops it (`<crops.json> holds
     only object crops: add surface crops (step 1.3), extract_style measures those`).
4. Run `extract_style.py -- --crops Tools/Blender/Style/crops.json --out Tools/Blender/Style/style_metrics.json
   --swatches Tools/Blender/Style/palette.png`. It measures every shot as if 1080 px tall, the scale `asset_px` is
   given at. `palette.png` holds the palette swatches, a white gap, then the accents; the run prints each cell's
   number, kind, hex and the albedo the toon shader lights to that hex (`SWATCH 3 palette #a0643c toon_albedo
   #9a6445`), so the decision page can name them. Each measured crop prints `CROP <n> <file>: image <W>x<H>, rect
   [x, y, w, h]` (the rect as measured); a rect that runs off its shot is cut to it with `STYLE WARNING: crop <n>
   rect ... runs off <file> (<W>x<H>): only [...] is measured; fix the rect in crops.json`: fix it and rerun. A shot
   is read as sRGB whatever profile it carries, so one with another profile prints `STYLE WARNING: <file> carries the
   colour profile <name> and is read as sRGB, so saturated colours read duller: convert the shot to sRGB first (an
   iPhone screenshot is Display P3)`: convert it and rerun. The run
   also writes `crops.png` beside the first measured shot, `Tools/Blender/Style/reference/<Game>/crops.png` (the shots'
   pixels, so git-ignored with them; `CROPS <path>: <n> measured crop(s), numbered as the CROP lines`), each crop a
   numbered thumbnail: Read it before writing `style.json`, and fix any crop that holds UI, sky, fog or another
   surface than its note says.
5. Write the bible's fields (below) and `STYLE.md` from the metrics, the screenshots and the user's words. They go
   into the two readings of the decision page at the end of this step, `style_a.json` and `style_b.json`; the
   approved one is copied to `style.json`.
   - `palette`: the swatches the user confirms by eye, renamed by material (Wood, Stone, Foliage), each
     `{"srgb": [...], "smoothness": 0-1}` (a role written as a bare list stops the gate, the sheet and the starter,
     naming that form): the swatch's `srgb`, and a smoothness on Toon.shader's scale read off the
     references: 0 matte (wood, stone, cloth: no glossy spot, no rim), about 0.3 paint, 0.5-0.6 metal; the build
     reads both. `accents`: the metrics' accents the user keeps.
     For `toon` the screenshots show lit and shade bands, not albedo: write the swatch's `toon_albedo_srgb` (the
     list; `toon_albedo` is its hex for the page, and the gate, the sheet and the starter stop on a hex or 0-255
     value: `write 3 numbers 0-1`; the gate and the sheet hold `light.color`, `light.shadow_srgb` and `outline.srgb`
     to the same), for the accents too, and drop a swatch that is another one's shade
     band (same hue, darker), or the palette holds one material twice. `toon_albedo` is the linear swatch divided by
     the lit band's light, the metrics' `toon_lit` (per channel): `light.color` x `intensity` + `ambient` x
     `ambient_strength`, about (1.09, 0.995, 0.762) with the template's Main scene (Unity's default sun, colour
     (1, 0.957, 0.839) x intensity 1; SH ambient 0.5 x 0.18). So write `light` into each reading first and rerun
     step 4 once per reading with `--style` on it (`--style Tools/Blender/Style/style_a.json --out
     Tools/Blender/Style/style_metrics_a.json`, then `_b`), and take that reading's albedos from its own run:
     `toon_lit` then names the game's light, a tinted or dimmed sun or another ambient moves every albedo with it,
     and the approved reading keeps its light in `style.json`. An albedo cannot pass 1, so a pooled swatch brighter
     in a channel than the lit band reaches (under the default warm sun, sRGB blue over about 0.89) is unreachable
     under this light: the run prints `STYLE WARNING: swatch <n> <hex> needs an albedo over 1 in <r/g/b>: the lit band
     under this light draws <hex>` and lists it in the metrics' `albedo_clipped` (`swatch`, `hex`, `channels`,
     `drawn_srgb`, `drawn_hex`). Change the reading's `light.color` or `ambient` and rerun, or accept the drawn colour
     (the swatch's `toon_albedo_srgb` draws it). Read the scene's light once from the game's main scene
     in the open Editor, one `unity command script run --file <absolute .cs path>` (`unity-editor-cli`) on a static
     method that logs the sun (`RenderSettings.sun`, else the first directional `Light`): its `color` (sRGB as 3
     numbers 0-1, as `Color` logs it: the Inspector's 0-255 values over 255; a hex or 0-255 value stops the gate, the
     sheet and `extract_style --style`), `intensity` and `transform.eulerAngles`, and the ambient,
     `RenderSettings.ambientProbe.Evaluate(new[] { Vector3.up }, c)` into a one-entry `Color[] c`: the mean of
     `c[0]`'s r, g and b (linear) is the level `SampleSH` gives an upward face. Write them into `light`: `color`,
     `intensity`, `pitch` = Euler x, `yaw` = 180 - Euler y (the conversion below; mod 360), `ambient`. A template
     game's Main scene holds Unity's default sun, Euler (50, -30, 0): pitch 50, yaw 210, which a field left out takes.
   - `value_range`: pooled `L_p2` - 3 to `L_p98` + 3; `palette_de` 6 for toon and flat, 10 for lit and painted.
     Pooled means all crops' pixels together (each crop sampled to at most 200,000), so a large crop weighs more:
     keep the crops of one game about the same size. A palette or accent colour may sit outside it: the gate checks
     the range, and the pure black (L* under 3) and pure white (over 97) rule, only for colours that are within
     `palette_de` of no role, so a near-black ink role passes.
   - `look`: pooled `detail_energy`, `dark_edge_share`, `chroma_mean` and `accent_share`, copied as they are.
   - `accent_max_share`: how much of one asset's surface may be accent colour, read off the object crops (a red trim
     on a crate: about 0.1-0.2). The gate measures the surface within `palette_de` of an accent, so `look`'s
     `accent_share` (screenshot pixels of chroma over 60) does not set it.
   - `camera.asset_px` and `asset_m`: the pixels `asset_m` metres span across a 1080p frame at the game camera, the
     scale every script draws and measures at. From the camera: ortho `540 x asset_m / orthographicSize`, perspective
     `540 x asset_m / (distance x tan(fov / 2))`, `distance` to where the props stand. Off a shot scaled to 1080 px
     tall: a typical prop's width in pixels, with `asset_m` its width in metres (width, not height: a pitched camera
     foreshortens height). `triangles` from them: prop about 3-6 x `asset_px` (64 px: 200-400, 128 px: 400-800),
     hero 3x prop, kit 0 to 0.75x the prop's top (floor 0: a level instances flat tiles and wall panels by the
     hundred). A low-poly or faceted look draws with fewer: count the faces of a reference object crop at game size
     and set the band round that count, or put the two bands on the decision page. The band's top is a ceiling, not
     a target: `band_top_share` in the gate's `STYLE FACTS` line (the asset's triangles over the top) shows a build
     parked at it. The floor is for an asset of `asset_m`: the gate and the starter hold a smaller one to
     `ceil(floor x min(1, size / asset_m))`, `size` its largest bounding-box side in metres (band 400-800, `asset_m`
     1: a 0.5 m prop needs 200); the top stays.
   - `detail_floor_m`: 2 pixels at game size, 2 x `asset_m` / `asset_px` (128 px, 1 m: 0.016). The gate takes a
     loose part's widths along its face normals, so a 12 mm cube reads 12 mm however it is turned: under the floor
     on its longest side, or thinner across (a rod), fails `detail`.
   - `flat_waste_max_share`: 0.1. It counts only triangles whose removal leaves the asset looking the same (shape,
     shading, outline, UV map), so the look never pays for it.
   - `curve_waste_max_share`: 0.1 per class the game draws at about `asset_px` (`{"prop": 0.1, "kit": 0.1}`); a
     class it shows larger (a close-up hero) gets no entry. It counts triangles on curves (smooth ones, and hard
     facets under 1 px across, which blur into a curve) cut so fine that two neighbouring segments merged into one
     stay within 0.25 px of the curve at game size (each segment's own chord error under about 0.06 px), and loops
     along a smooth side's straight way (a tube's height loops) that change neither shading, outline nor UV map.
     Loops that stay (under hard caps they hold the outline) count with their over-fine segment, every piece of
     it, so they cannot thin the share, which is taken over all the asset's triangles. An asset drawn without the ink
     line (`outline` false, or its root's `outline` False) has no outline to hold: there those loops count on their
     own. Each face is judged at each curved edge by its own width, so a Bevel's strips count the same shaded smooth
     or flat, the outer strip beside the wide flat it ends in too; a hard facet a pixel or wider is a look and holds
     its two faces out of the count.
   - `hidden_max_share` 0.05: triangles inside another closed part of the asset (a buried cap: corners and centre
     all inside) only cost. A face lying flat on another closed part is inside it too (a body's top under a flush
     lid, and the lid's bottom): two closed shells that share whole edges in one mesh stay two parts.
     `materials_max` per class (`{"prop": 3, "kit": 2}`): each material is a submesh, drawn twice under
     Toon.shader when outlined (ForwardLit and the Outline pass; once without the line), and parts kept
     separate multiply the draws (the gate's `submeshes` fact: each part's materials, summed). Fewer roles on
     mobile: merge roles that read the same at game size; past that the palette atlas (`texel_density` `"atlas"`,
     `kit_common.py`'s pattern) is the way up.
     With `"atlas"` every material maps the atlas: the gate fails a flat colour (`material`: `<M> is a flat colour,
     but texel_density is atlas: map it to the palette atlas`). An atlas the build script paints in memory is packed
     (`image.pack()`) or saved to a file before the `.blend` is saved: Blender stores neither its pixels nor a path
     otherwise, so the gate fails it (`texture`) and the sheet warns that it draws blank.
   - `shading`: the game's material model (`toon` for the toon-art pack's `__GAME__/Toon`). `outline` and the toon
     fields of `light` (the table below): the values the game draws with, which start as Toon.shader's defaults
     (left out, a field takes the default). A different look changes both the same day: the shader's
     defaults or the builder's material values in Unity, and these fields, or the sheet shows a look the game does
     not draw.
   - `camera` and `light` angles: the game's Main Camera and sun. Yaw 0, pitch 0 looks from Blender's front (-Y);
     with toon-art's axes (Blender (x, y, z) is Unity (-x, z, -y)) a Unity rotation Euler (x, r, 0) is `pitch` x,
     `yaw` 180 - r (the default sun's (50, -30, 0) is pitch 50, yaw 210). `projection` and `fov` from the camera.
     A top-down camera (pitch 90) keeps its yaw: Unity Euler (90, 0, 0) is yaw 180 and the sheet draws Unity +Z up
     (yaw 0 is Blender's Top view). The game row draws the asset as built, unturned: its front is Blender -Y (Unity
     +Z, the prefab's forward). Where the level shows the asset turned (a chest facing the player), add that turn to
     `camera.yaw`, or the game row shows a side the player does not see.
   - `texture_off_palette_max` 0.15 and `texel_density` (`"atlas"` for a palette atlas, else the px per metre the
     brief's platform affords) only when the game textures its assets; `hard_edges_max_share` `null` until the golden
     asset shows a number worth holding; `bevel_m` about 2 pixels at game size, like `detail_floor_m`.

   Show the swatches and 2 test assets (a crate and a rock) built two ways on a decision page: the two readings the
   user was unsure about in step 1 (two palettes, toon or flat, chunky or slim proportions; with none, the two closest
   reference games), each a short build script on the starter (`toon_prop.py` in toon-art). Write the readings as
   `Tools/Blender/Style/style_a.json` and `style_b.json` and run the starter once per reading,
   `-- <project> --style Tools/Blender/Style/style_a.json` (then `style_b.json`; its paths may be relative to the
   working folder): it saves
   `Tools/Blender/checks/<Asset>_style_a.blend` (and `_style_b`) and exports nothing, `--export` or not (a missing
   `--style` file stops it with `CheckError: --style <path> is no file`). A reading's build may stop on its band
   (`<n> triangles, budget <top>`, or `under the <class> band's <low>`): the `.blend` is saved before that check, so it
   still goes to the sheet, and both bands go on the page for the user to pick. Then
   run `contact_sheet.py` on each with `--style` set to the same reading. The user approves one; it becomes
   `style.json`.
6. Build the golden asset: one typical prop of the most common class, through section 2. After the user's yes, copy
   its last sheet's `<Asset>_sheet_r<N>_game.png` (the game-view look tile) to `Tools/Blender/Style/golden.png`; it
   stands beside every later sheet. Keep three calibration anchors in `Tools/Blender/Style/anchors/`, each with its
   score and one line why in `anchors/notes.md`: the golden sheet as `pass.png`; a colour fail as `fail.png` (an early
   round's `_r1`, or the asset with one renamed material at plain grey 0.5: a material still named `Material` at
   Blender's default grey draws magenta in the sheet, and a mesh with no material draws plain grey); and a shape fail as
   `fail_generic.png` (the sheet of the unchanged starter, or of the
   golden rebuilt on default proportions without the Motif), noted "Originality 4: swap test fails, no Motif". An
   anchor is a whole sheet, and its last row holds the reference crops: `anchors/` stays on this machine like the
   shots (git-ignored), while `golden.png`, the asset's own tile, is committed.

## 2. Every asset

1. Brief, saved as `Tools/Blender/<Asset>/brief.md` (every review round passes it to the reviewers): class (a
   `triangles` key), budget, the reference crop or concept, and where this asset carries STYLE.md's `Motif` and how
   many pixels it spans at `asset_px` (2 x 2 or more, or it is lost). A specific reference image of the object runs
   `blender-image-to-3d`'s phases; anything else is a build script in `Tools/Blender/`.
2. The build script takes its colours from the bible, never typed again. In the toon-art pipeline the starter
   `toon_prop.py` does it (`use_style_bible`: the palette, the accents as roles `Accent1..N` (a colour that is not
   3 numbers 0-1 stops it, as in the gate), the class's triangle band checked at both ends (the floor scaled by the
   asset's size, section 1's rule), the outline, `style_class`, `bevel_m`, and the saved
   `Tools/Blender/checks/<Asset>.blend`;
   `main()` builds round parts at 0.5 px of chord error on the widest silhouette ring (the ink line hides less
   there), rounded up to even, and drops two segments at a time, down to 8, only while the triangles are over the
   band's top; still over at 8 it stops with `<n> triangles, budget <top>: run style_gate.py on <blend> with --style
   <style> ...`, and the gate (step 3) names what to cut, or that the design has more parts than the band affords.
   Its barrel, one closed surface turned from a profile (a bowed side, alternating stave colours, two hoops stepped
   2 px out, one flat cap for the bottom; with a bible the chime bevel, the top head's recess and a side ring within
   2 px of a hoop are shed when under 2 px at game size, so the round keeps its segments), shows the wiring only:
   `build()` is rewritten from the brief for every asset, never shipped as it is, and with a bible `--export`
   refuses it while `NAME` is still `SM_Barrel` (`--export refused: this is still the starter barrel`). A rewritten
   build names its `ROLES` from `style.json`'s palette; a role not in it stops the run with `ROLES values must be
   style.json palette roles`); elsewhere:
   `PALETTE = {r: (tuple(v["srgb"]), v["smoothness"]) for r, v in json.load(open(STYLE))["palette"].items()}`, and
   a material's Base Color takes `srgb_to_linear(srgb)` (Blender colours are linear, and the gate's `palette`
   message names the slip when the raw sRGB numbers are typed in). A game's build script never imports from `$S`:
   the plugin's cache folder moves with every plugin update. Copy the helpers it needs into the game's
   `Tools/Blender/style_common.py` (`srgb_to_linear` from `extract_style.py`; `flat_waste` below) and import them
   from there.
   The build tags the Motif's faces with a boolean face attribute named `motif` (after `bm.to_mesh(mesh)`:
   `a = mesh.attributes.new("motif", 'BOOLEAN', 'FACE')`, then `a.data.foreach_set('value', flags)`): FBX ignores
   it, and the sheet measures the Motif at game size from it. The starter tags none (it is generic on purpose, so its
   sheet warns). Base Color is that colour or an Image Texture linked straight to it, read through UV0 as it is: FBX
   follows no Reroute or muted node to the image (the gate fails `material`), and Unity's material ignores a Mapping
   node, or a UV Map node naming another layer, on the image's Vector input (the gate fails `texture`: bake the
   mapping into the UVs). The Principled BSDF links straight to the Material Output: behind a Mix Shader or another
   node FBX exports the viewport colour and no texture (`material`: `the Principled BSDF reaches the output through
   <node> ...: link it straight to the Material Output`). A material still named `Material` or
   `Material.001` at Blender's default grey fails as
   untouched; with a colour set it fails too (`carries Blender's default name: name it M_<Role>`) and its colour is
   still judged; a renamed one at that grey is judged as the light grey it is. The gate and the sheet read the
   evaluated object's material slots, the ones FBX ships: a Boolean's transferred material or a Set Material node's
   counts. The asset's root object gets the custom property `style_class` (`obj["style_class"] = "prop"`, on the
   object, not its mesh). The starter joins its parts into one mesh; a build that keeps several parts parents them
   under that root, and the gate sums their triangles (an Empty that only groups props is not an asset; an unparented
   part is an asset of its own). A piece the game draws without the ink line (toon_prop's `OUTLINE = False`, kit and
   level pieces) sets `obj["outline"] = False` on its root, so the sheet leaves the line off too. A cutout links the
   texture's Alpha to the Principled Alpha; any other texture alpha (the toon-art atlas's smoothness) is not
   transparency. Under `shading` `toon` the gate fails a cutout (`material`: `a cutout under Toon.shader draws as
   a solid card (Toon.shader has no alpha clip): model the shape, or give this piece a non-toon shading`), and the
   sheet draws it solid with a `SHEET WARNING`; under the other shadings the sheet clips it at alpha 0.5. A closed
   part wound inside out fails `mesh` (`faces wound inside out, recalc normals`), and so do single flipped faces on
   any part, closed or open (`<n> edge(s) join faces wound opposite ways`): the shader's ForwardLit pass
   culls back faces, and so do the sheet's look and silhouette columns, so the game would draw the part's far
   inside. The remedy for both is `bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])` in the build script. A face
   left between two welded parts (a Mirror or Array merge, `remove_doubles` on a lid and its body) fails `mesh` too
   (`<n> inner wall face(s) ...: delete them`): nobody sees it, and with it the part has no inside for the `hidden`
   rule. So does a checked part hidden in the viewport (`<part> is hidden in the viewport`): the export by selection
   skips it, so show it or delete it. The script saves the `.blend` and exports the FBX only after the
   user's yes in step 6 (the starter:
   rerun with `-- <project> --export`). Parts under the root are meshes: a Curve, Text or Surface part is dropped by
   the FBX export, so the gate fails it (`mesh`): convert it to a mesh in the build script, or, when it is only a
   helper a modifier reads, hide it from render (`hide_render`).
3. `style_gate.py` on that `.blend`. Exit 1: fix the cause and rebuild; never loosen `style.json` to pass one asset.
   Every run, pass or fail, prints one line per asset: `STYLE FACTS <asset>: <n> triangles, band <class> <lo>-<hi>
   (band_top_share <x>), curve_waste_share <x>, flat_waste_share <x>, hidden_share <x>, largest parts: <part> <n>,
   ...; submeshes <n>` (the 3 largest loose parts; each part's materials, summed; a textured asset adds `;
   texture_off_palette <x>`, its worst part's; `--report <file>` writes every fact as json): the numbers a rebuild
   steers by.
   After 3 rebuilds that fail the same rule (two rules pulling apart, such as `triangles` under the band and
   `curve`), stop and put the conflict and the numbers on a decision page for the user.
   Without `--objects` the gate and the sheet take what the FBX export takes: the view layer's render-visible meshes
   and the hidden parts under a root with `style_class`, minus Boolean cutters, `COL_` and `_LOD1+`. An `--objects`
   list that names only some parts of an asset prints a `STYLE NOTE` with the parts it left out. An instancer under
   no checked asset (an Empty instancing a collection beside the props) prints `STYLE NOTE <name> instances <n>
   object(s) the gate does not count`: make them real, or leave it out of the export.
   A `triangles` failure under the band on a part with no `style_class` (`if this is a part, parent the asset's parts
   under one root with "style_class"`): parent the parts first. The floor it names is the asset's own (`under the
   prop band 200-800 (the band's 400 scaled by the asset's 0.50 m against asset_m 1.0)`), while the `band` fact
   stays the style's. Otherwise the asset is plainer than the style; add
   the detail the references show at `asset_px` (bevels, rims, planks, a trim), never cuts on flat faces (the
   `waste` rule) or extra segments (the `curve` rule). Over the band: remove detail the game size cannot show,
   starting with the `curve`, `waste`, `detail` or `hidden` failures the message names. With none of them it names
   a share over 0.1 that failed no limit (a class with no curve limit, a `null` `flat_waste_max_share`):
   `curve_waste_share 0.47 failed no limit for hero, but cut there first (fewer segments round curves) where the
   game size shows no difference`. With no such share either it says so plainly, `no curve, waste, detail or hidden
   failure names anything to cut, so the design has more parts than the
   band affords (largest: ...)`: drop parts in the build script, or take the band to the decision page. An
   `instances` failure: realize the instances in the build script before saving (a Realize Instances node, or
   `bpy.ops.object.duplicates_make_real()`). A `hidden` failure: leave the buried
   faces out (step the detail out of one closed surface, as the starter's hoops, or make it an open band round the
   body; under a flush lid, the body's top and the lid's bottom). A `materials` failure: each material is a submesh,
   drawn twice under Toon.shader when outlined (the message says whether this asset is); merge roles that read
   the same at game size, or, with `texel_density` `"atlas"`, use the palette atlas. With several parts it also
   names their submeshes (`<n> submeshes in <k> parts`): join them into one mesh.
   A `waste` failure: drop the cuts on flat faces in the build script (no subdivide or loop cut where nothing bends).
   Where a shared helper has to cut, copy `style_gate.py`'s `flat_waste` into `Tools/Blender/style_common.py` with
   what it calls (`flat_faces`, `corner_normals`, `same_uv_map`, `affine`, `FLAT_DEG`, `TEXTURE_SIDE`; it needs
   `numpy as np`, `bmesh` and `math`). After `bm.to_mesh(mesh)`, call `flat_waste(mesh, bm)` (it reads the corner
   normals off the mesh, which must hold the bmesh's faces; the face normals it updates itself, so faces just made
   with `bm.faces.new` need no `normal_update` first) and write the bmesh back with `bm.to_mesh(mesh)` again:
   it dissolves and triangulates only what the gate counted. A bare Limited
   Dissolve (`dissolve_limit`) is not that: it also drops the edge midpoints the outline needs, warps a 9-slice UV and
   leaves n-gons for Unity to triangulate. Never Decimate to meet a budget: the look comes first, and Decimate removes
   shape.
   A `curve` failure: give each round part `ceil(pi / acos(1 - 0.5 / r_px))` segments around, rounded up to even,
   `r_px` = the widest silhouette ring's radius x `asset_px` / `asset_m` (16 px radius: 14, 32 px: 18, 64 px: 26),
   and half that along a sphere's height: 0.5 px of own chord error. The gate fails only a curve cut so fine that
   two neighbouring segments merged into one stay within 0.25 px of the curve (each segment's own chord error under
   about 0.06 px). A hard facet under 1 px across counts as a curve too (a flat-shaded Bevel's segments at 2 px):
   fewer segments, or one (a 2 px Bevel passes at 3 segments and fails at 4, shaded smooth or flat). The message
   splits the count: the part that cuts a smooth side along its straight way
   goes by dropping those loops. Loops that stay (a tube's height loops under hard caps) count with their
   over-fine segment, so adding loops never passes a round cut too fine.
4. `contact_sheet.py -- --style ... --out Tools/Blender/<Asset>/review/<Asset>_sheet_r<N>.png --crops
   Tools/Blender/Style/crops.json --class <class> --golden Tools/Blender/Style/golden.png` (`--refs <files>` adds
   whole images), `<N>` the review round from 1, so every round's sheet, `.json` and `_game.png` stay for the A/B
   and the anchors. The golden asset's own sheets go without a golden (the script notes it and goes on). Read the
   sheet: rows front, right, back, top, game camera, references (the class's object crops); columns silhouette,
   clay, look (silhouette and look cull back faces as the game does; clay does not). An object crop larger than
   the tile at the asset's zoom is drawn at a smaller whole zoom, or fitted, with `SHEET NOTE: object crop <file>
   ... reads smaller beside the asset than in the game`: tighten its rect in `crops.json` to the object alone, or
   tell the reviewers that crop is not at the asset's scale. Its `.json` holds the game view's L* range,
   `inside_value_range` (0.9 or more; for toon: of the pixels nearer a lit band than a shade band, since the shade
   band sits below the references' range by design; their share
   is `lit_share`, and under a third prints `SHEET NOTE: <n>% of the game view is in the lit band ...: the camera
   (yaw <y>) looks at the side the sun (yaw <y>) leaves in shade`: set `camera.yaw` and `light.yaw` from the game),
   `palette_coverage` (0.85 or more for toon and flat from `asset_px` 64 up: the share of the asset's pixels, the ink
   ring and one pixel inside it left out, within `palette_de` of a drawn colour, its bands, ink and the blends
   between them; under 64 px the edge pixels weigh more, so compare it with the golden's) and the `look` numbers
   beside the references'. A `chroma_mean` more than 10 from the references' prints `SHEET NOTE: game view
   chroma_mean <a>, the references <b> ...: a lead for the colour lens to look at, not a fix on its own`: one asset
   in one role differs from whole frames, so the lens looks at the sheet and decides. `silhouette_fill` holds per
   view the asset's pixels over its
   bounding box's; front and right both at 0.93 or more print `SHEET NOTE: front and side silhouettes fill ... a
   primitive's outline` (say in the brief what in the silhouette is not a box or can, or why it wants one). `motif`
   is false, with a `SHEET WARNING`, when `STYLE.md` beside `--style` is missing or has no line starting `Motif:`;
   write it before the review. `motif_px` is the game view's pixels (an area, at the sheet's render scale) of the
   faces tagged `motif` (step 2), hidden where the asset's own faces cover them; `null` with `SHEET WARNING: no face
   carries the boolean face attribute "motif"`, and under 4 (2 x 2) it prints `SHEET WARNING: the motif covers <n>
   px of the game view (under 2 x 2)`: tag the faces, or make the Motif larger or bolder. At 0 px the tagged faces
   are hidden or face away from the game camera, and the warning names its yaw: put the Motif on a side this camera
   sees, or set `camera.yaw` to the angle the level shows the asset from. `motif_px` shows only that
   tagged faces are visible, not that they are the Motif. So with a tagged face the game row gets a fourth tile, the
   motif mask (the tagged pixels black on the asset in light grey; `layout.game_row_extra` in the `.json` names it),
   which shows where the tag sits, and `motif_share` (`motif_px` over the asset's game-view pixels) over 0.5 prints
   `SHEET WARNING: the motif tag covers most of the asset (<n>% of its game-view pixels): tag only the motif's
   faces`. A reference file missing on this machine (a new clone: the shots stay local, step 1.2) prints a `SHEET
   NOTE` and leaves its tile out; copy `Tools/Blender/Style/reference/` and `anchors/` over.
5. Review: two `gamekit:art-reviewer` agents in parallel, each fresh, one with `lens: shape` and one with `lens:
   colour`, each given the sheet, its `.json`, `STYLE.md`, `style.json`, `Tools/Blender/Style/golden.png`,
   `Tools/Blender/Style/anchors/` and the brief (`Tools/Blender/<Asset>/brief.md`), never the build script. From
   round 2 the previous round's sheet too (A/B). Each fix round reruns steps 2-4 (build, gate, sheet as
   `_r<N+1>`): a gate failure is fixed before the
   reviewers see the round. Copy the build script beside each round's sheet (`review/<Asset>_r<N>.py`): when both
   lenses answer `A/B: worse`, revert the build script to the previous round's copy and try another fix. Done when
   both score at least 8/10 with no blocker; at most 3 rounds, then show the user the sheet and the open findings.
6. The user sees the final sheet before export. Show a sheet with `SendUserFile` (`display: render`), so it opens
   beside the chat and reaches the phone; without that tool, give its path as a link. After the user's yes, rerun the
   build with its export on (`toon_prop.py ... -- <project> --export`: the FBX and its manifest go to
   `Assets/<Game>/Game/Art/Models/`, `<Game>` the one folder under `Assets` that holds `Game/Art`; with none or
   several, every run stops before it writes anything and names `--game <Name>`), then `unity-export`, and the
   final judgement is an in-engine capture at the game camera (`gk-bridge play-capture`) beside a reference crop and
   the sheet's game tile. Compare three things: the L* range, the shade band's hue, the outline's width. Measure the
   L* range the same way on both images: a crops file each (`capture_crops.json` on the whole capture, `tile_crops.json`
   on the sheet's `_game.png`) with one rect on the same surfaces of the asset, tight inside it (no ground, no ink
   line, at least 8 px a side), then `extract_style.py -- --crops <file> --out <file>_metrics.json` on each; their
   pooled `L_p2` and `L_p98` within 3 is the same. A
   difference from the sheet is drift between `style.json` and the game: set `light`, `outline` and Toon.shader's
   values equal the same day (section 1, step 5), then rerun the sheet; a difference from the reference crop alone
   goes back to step 2 of this section.
7. A helper that repeats across assets (a trim, a plank, an edge-wear recipe) moves into the game's shared build
   module, `Tools/Blender/style_common.py`, so the next asset reuses it instead of re-inventing it.

Every 5-10 approved assets: append them into one `.blend` in a row and run `contact_sheet.py` on it; its game row is
the kit lineup. Two art-reviewer passes, `lens: shape` and `lens: colour`, look for drift (a bevel or a detail
density, a colour or a value that differs). First rebuild each approved asset (its build script without `--export`),
so its `checks/<Asset>.blend` is the current build; a `blender-image-to-3d` asset is listed by its master `.blend`
under `Tools/Blender/<Asset>/`. Append with this script, run headless (`blender --background --factory-startup
--python-exit-code 1 --python Tools/Blender/lineup.py`), then run the sheet on `Tools/Blender/checks/lineup.blend`
with `--style Tools/Blender/Style/style.json --out Tools/Blender/checks/lineup_sheet.png --crops
Tools/Blender/Style/crops.json --golden Tools/Blender/Style/golden.png`. The row runs along the game camera's right
axis, so the game row shows the assets side by side; the front, right and back rows look along or across it, where
assets hide each other: in a lineup they are not meant to be read. The look pass draws cast shadows as the game
does, so in the row an asset's shadow can fall on its neighbour: a shade patch shaped like the neighbour is that
shadow, not colour drift (widen the gap, `0.5 * asset_m` in the script, when it covers what is compared). A lineup's
sheet usually passes 2000 px a side, and an image that large is shrunk when it is read: the run prints `SHEET NOTE:
the sheet is <w>x<h> px ... judge pixel detail on <stem>_game.png`. Give the reviewers that file too
(`lineup_sheet_game.png`, the game row's look tile alone at 1 x): they judge pixel detail (a bevel, the line's
width) on it, not on the sheet.
```python
import json, math, os, bpy
from mathutils import Vector
bpy.ops.wm.read_factory_settings(use_empty=True)
paths = ["Tools/Blender/checks/SM_Crate.blend", "Tools/Blender/Lantern/Lantern.blend"]  # the approved assets
cam = json.load(open("Tools/Blender/Style/style.json"))["camera"]
asset_m = cam.get("asset_m", 1.0)
yaw = math.radians(cam.get("yaw", 135.0))  # left out: the sheet's fallback camera
right = Vector((math.cos(yaw), math.sin(yaw), 0.0))  # the game camera's right axis
at = 0.0
for path in paths:
    # an absolute path: after read_factory_settings a relative one resolves against the drive root
    with bpy.data.libraries.load(os.path.abspath(path)) as (src, dst):
        dst.objects = src.objects
    for o in dst.objects:
        bpy.context.scene.collection.objects.link(o)
    bpy.context.view_layer.update()
    ts = [(o.matrix_world @ Vector(c)).dot(right) for o in dst.objects if o.type == 'MESH' for c in o.bound_box]
    for o in dst.objects:
        if o.parent is None:
            o.location += right * (at - min(ts))  # the roots; parts follow their parent
    # each asset its bounding box's width along the row apart (the box's diagonal at a three-quarter yaw), plus a gap
    at += max(ts) - min(ts) + 0.5 * asset_m
bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath("Tools/Blender/checks/lineup.blend"))
```
Keep a lineup the sheet draws at 1x: from a three-quarter yaw a row holds at most `floor(1024 / (2 x asset_px))`
assets as wide as they are tall (4 at 128 px, 8 at 64 px; slimmer ones more); when it prints `SHEET WARNING ... drawn
at <1 x`, split the row, or the bevels it is meant to compare fall under a pixel (the reference crops stay at game
scale there, so they read larger than the assets by the factor the warning names). The golden tile keeps the zoom of
the sheet it came from, whatever the tile size (`layout.golden_zoom`; the lineup's is `layout.zoom`): `SHEET NOTE:
the golden tile is drawn at <g> x, the asset at <k> x` means compare its colours and line, and judge size and
proportion against the object crops. `layout.reference_zoom` lists each reference tile's zoom in the row's order (an
object crop's; `null` for a surface crop or a `--refs` image, which are fitted; the golden's last): a crop at the
asset's zoom compares by eye, another by its number.

## style.json

```json
{
  "game": "__GAME__",
  "references": [{"game": "<name>", "take": "palette, chunky proportions"}],
  "shading": "toon",
  "outline": {"px": 1.5, "srgb": [0.36, 0.30, 0.46]},
  "camera": {"projection": "ortho", "pitch": 35, "yaw": 135, "fov": 40, "asset_px": 128, "asset_m": 1.0},
  "light": {"pitch": 50, "yaw": 210, "band": 0.05, "shadow_srgb": [0.62, 0.62, 0.86], "shade_saturation": 1.3,
            "ambient": 0.5, "color": [1.0, 0.957, 0.839], "intensity": 1.0},
  "palette": {"Wood": {"srgb": [0.74, 0.49, 0.28], "smoothness": 0.0},
              "WoodDark": {"srgb": [0.52, 0.32, 0.19], "smoothness": 0.0},
              "Metal": {"srgb": [0.59, 0.63, 0.71], "smoothness": 0.55}},
  "accents": [[0.95, 0.15, 0.10]],
  "palette_de": 6,
  "value_range": [18, 92],
  "accent_max_share": 0.12,
  "look": {"detail_energy": 2.4, "dark_edge_share": 0.031, "chroma_mean": 28.5, "accent_share": 0.006},
  "triangles": {"hero": [1200, 2400], "prop": [400, 800], "kit": [0, 600]},
  "detail_floor_m": 0.016,
  "bevel_m": 0.016,
  "hard_edges_max_share": null,
  "flat_waste_max_share": 0.1,
  "curve_waste_max_share": {"prop": 0.1, "kit": 0.1},
  "hidden_max_share": 0.05,
  "materials_max": {"prop": 3, "kit": 2},
  "avoid": ["thin parts that vanish at asset_px", "a second outline width"]
}
```

The light is the template Main scene's: Unity's default sun, Euler (50, -30, 0) converted (step 1.5). The camera
looks from that sun's lit side (yaw 135; the sheet draws a `camera` with no `pitch` or `yaw` from pitch 30, yaw 135):
from yaw 45 the game view is mostly shade band and the sheet prints its `lit_share` note (step 2.4). The example
game draws flat colours, so it has no `texture_off_palette_max` or `texel_density`.

| Field | Meaning | Checked by |
|---|---|---|
| `shading`, `outline` | `toon`, `flat`, `lit` or `painted`: the Unity shading model the look pass copies; the ink line (left out or `true` = Toon.shader's 1.5 px at 1080p, tint `srgb`, under every shading; `false` = none, which a game without the line writes); the sheet draws these numbers, so they stay equal to the shader's (step 1.5) | contact_sheet, style_gate (a cutout under `toon`; `outline` in the `materials` message and the `curve` rule's height loops), toon_prop (`outline`) |
| `camera` | the game camera (`pitch` and `yaw` left out: 30 and 135, a three-quarter view from the default sun's lit side; at pitch 90 the view still turns by `yaw`); `projection` `"ortho"` or `"persp"` (`"orthographic"` and `"perspective"` also read; any other value stops the sheet); `asset_px` = the pixels `asset_m` metres (default 1) span across a 1080p frame at the game camera, measured on a typical prop's width (ortho: `540 x asset_m / orthographicSize`) | contact_sheet, style_gate (`curve`, the `triangles` floor) |
| `light` | sun direction; toon only: `band` = the N.L of the shadow edge, `shadow_srgb`, `shade_saturation` = the shade band (Toon.shader `_RampOffset`, `_ShadeColor`, `_ShadeSaturation`), `ambient` = the scene's SH level, `color` (sRGB, 3 numbers 0-1 like `shadow_srgb` and the outline's `srgb`: a hex or 0-255 stops the gate and the sheet) and `intensity` = the main light's (both bands scale with them; left out: Unity's default sun, (1, 0.957, 0.839) x 1 at `pitch` 50, `yaw` 210), `contact_shade` 0.3, `ground_y` -0.06 and `contact_height` 0.25 = the darkening toward the floor (Toon.shader `_ContactShade`, `_GroundY`, `_ContactHeight`; the `.blend`'s z = 0 is the game's floor), `softness` 0.035, `ambient_strength` 0.18, `spot` 0.85, `rim` 0.5, `rim_edge` 0.62 (`_RampSoftness`, `_AmbientStrength`, `_SpecularStrength`, `_RimStrength`, `_RimEdge`; a field left out takes that default); equal to the shader's and the scene's values (the sun and `ambient` read once from the scene, step 1.5; extract_style's `--style` divides `toon_albedo` by this light). The glossy spot and the rim take the smoothness the game gets: an `M_<Role>` material's palette role smoothness, else 1 - a set Principled Roughness, else 1 - the viewport roughness. The sheet renders under its own world and this sun only; lights in the `.blend` are left out (a `SHEET NOTE` names them) | contact_sheet |
| `palette`, `accents`, `palette_de`, `accent_max_share` | the roles (sRGB 0-1), how far (CIELAB distance) a colour may sit from one, and how much of an asset's surface may be accent (by colour: any face or texel within `palette_de` of an accent counts, whatever its role) | style_gate, contact_sheet |
| `texture_off_palette_max` | share of a texture's area (read through UV0, the map the game samples) whose colour sits off every role (left out = report only: the `texture_off_palette` fact in the `STYLE FACTS` line) | style_gate |
| `value_range`, `look` | L* 0-100 the asset's off-role colours stay in (a palette or accent colour is exempt); the references' pooled look numbers, shown beside the asset's (`detail_energy` comes from surface crops and reads higher on any whole asset; the asset's numbers are measured one pixel inside its silhouette, which drops most of a 1.5 px ink ring, so `dark_edge_share`, pixels under L* 15 on a strong edge, reads near 0 on an asset whose only line is its outline) | style_gate, contact_sheet |
| `triangles`, `detail_floor_m`, `texel_density`, `hard_edges_max_share` | budgets per class (per asset root; the floor scales down for an asset smaller than `asset_m`, `ceil(floor x min(1, size / asset_m))`; the top is a ceiling, `band_top_share` in the `STYLE FACTS` line the share of it used; over it with no `curve`, `waste`, `detail` or `hidden` failure the message names a waste or hidden share over 0.1 that failed no limit, else says the design has more parts than the band affords); smallest loose part, by its widths along its face normals (the longest under the floor, or a rod thinner across); px per metre or `"atlas"` (then a flat-colour material fails); share of unbevelled hard edges (`null` = report only) | style_gate |
| `flat_waste_max_share` | share of an asset's triangles that only split flat, flat-normal faces of one material and one affine UV map, away from the edges that shape the outline: removing them leaves the render the same (`null` = report only) | style_gate |
| `curve_waste_max_share` | per class (a number: every class): share of an asset's triangles that refine curves (smooth, or hard facets under 1 px across) cut so fine that two neighbouring segments merged into one stay within 0.25 px of the curve at `asset_px` (each segment's own chord error under about 0.06 px: fewer segments look the same at game size), or cut a smooth side along its straight way with shading, outline and UV map unchanged (no outline to hold on an asset drawn without the line); loops that stay count with their over-fine segment; the share is over all the asset's triangles (a class without an entry = report only) | style_gate |
| `hidden_max_share`, `materials_max` | share of an asset's triangles whose corners and centre all lie inside another closed part of it (a cap buried in the body, or a face lying flat on the other part: a body's top under a flush lid; closed shells joined flush along whole edges stay separate parts; an open part, such as a label plane, buries nothing; the accent share weighs each triangle's seen area by its corners, edge midpoints and centre outside); materials per asset, per class or one number (each one a submesh, drawn twice under Toon.shader when outlined, ForwardLit and Outline; the `submeshes` fact sums them per part, so separate parts multiply the draws: fewer roles on mobile, merge roles that read the same at game size; the palette atlas, `kit_common.py`'s pattern, is the way up); `null` or left out = report only | style_gate |

`bevel_m` and `avoid` are for the build and the reviewers; no script measures them. A threshold (`palette_de`,
`value_range`) is tuned on the golden asset, then frozen; a later change re-runs the gate on every approved asset.

## STYLE.md

The words the numbers cannot hold, at most one screen: the 3-5 rules that make the look (proportion, edge
treatment, how much detail and where, how shadows are coloured), what each reference game gives, the named mistakes,
and the tie-breaker when two rules collide (for example "readability at asset_px beats detail").

One line starts `Motif:`: this game's own signature detail, which no reference game has and every asset carries
in its class's form (a notched corner, a rope wrap, a two-tone rim; the user picks it from 2-3 options on the decision
page of step 1.5). It is what keeps the kit from reading as any game's: the art-reviewer's Originality line looks for
it at game size, beside the swap test (the asset placed in another game of the genre reads the same: 5 at most).
A missing line, or a Motif the game row does not show, is a blocker there; the sheet's `motif` warning catches the
first. `motif_px` (the faces each build tags `motif`, step 2.2) shows only that tagged faces are visible: whether
they are the Motif is read off the game row's motif mask tile, which the reviewer compares with this line. A tag on
a whole role or band is no tag, and the blocker stands as for no Motif; the sheet itself warns only past a
`motif_share` of 0.5.

## Limits

- Organic characters and creatures are the weak spot of scripted bpy. An AI image-to-3D mesh (TRELLIS.2, Hunyuan3D)
  is a separate setup the user decides on, and its output passes the same gates after retopology.
- Brush-stroke hand painting is not reachable headless; `painted` reaches stylised baked colour. A paid cloud
  retexture service is only used after the user's yes.
- Blender's look pass is a stand-in for the Unity shader: it draws the bands, spot, rim and contact shade, but SH
  ambient as one level, not sampled by the normal, and no post-processing; the in-engine capture decides.
- The `look` numbers compare a whole reference frame with one asset, so they guide the reviewers and gate nothing.
- `curve` reads each curved edge's turn and its two faces' widths and counts half the triangles of faces whose
  curved edges are all past the bound, so it errs low: it catches about 2.8x the segments the build formula gives
  (a merged pair within 0.25 px: a 64x32 ball, a 64-sided cylinder at prop size), not a few too many. Height loops
  count on their own only where the baked outline normal stays affine, so a tube under hard caps keeps them (its
  rims tilt the outline) unless the asset is drawn without the line; there they count only with a segment that is
  itself over-fine. It reads asset_px as the size on screen, so a part the game zooms in on needs its own class.
- `triangles` scales the floor by the asset's largest bounding-box side against `asset_m`, so a long thin asset (a
  1 m pole) is held to the whole floor. That side is read along the world axes: keep the root unrotated, or a 1 m
  pole turned 45 degrees reads 0.71 m.
- `detail` reads a loose part's overall widths: a bent wire or a ring reads as wide as its bend, so the rule passes
  it however thin the wire; the sheet's game tile judges it.
- The opposite-winding rule reads an edge's two faces, so faces behind an Edge Split modifier (their edges no longer
  shared) are not compared, and neither are faces that only meet at 3 or more per edge. The inner-wall rule reads
  faces whose every edge joins 3 or more faces: a wall that keeps one free edge is not caught.
- A cutout is one only when the base-colour texture's own Alpha feeds the Principled Alpha: alpha from another
  texture or node is not caught by the gate's toon rule, nor clipped in the sheet. The inside-out rule reads closed
  parts only (an open plane facing away shows as a hole in the sheet's look column), and the sheet's clay column
  neither culls back faces nor clips a cutout.
- `hidden` errs low in two cases: a flush pair behind an Edge Split modifier reads as open parts (hidden 0), and a
  flush triangle under about 1.5 cm high still counts as seen.
