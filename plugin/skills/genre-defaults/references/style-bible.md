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
   game's art: they stay on this machine (the game's `.gitignore` ignores `reference/`); the bible keeps only numbers.
3. Look at each shot (Read) and write `Tools/Blender/Style/crops.json`, a list of rects in pixels from the top left
   (`"file"` is relative to `crops.json`'s folder; an entry without `"rect"` uses the whole shot):
   ```json
   [{"file": "reference/<Game>/shot01.png", "rect": [410, 300, 220, 160], "note": "flat-lit wall, mid distance"},
    {"file": "reference/<Game>/shot04.png", "rect": [880, 520, 140, 150], "kind": "object", "class": "prop"}]
   ```
   Two kinds of rect:
   - surface crops (the default): evenly lit surfaces of the kind of asset this game needs, for the numbers. Leave
     out UI, fog, bloom, motion blur and night scenes: the numbers measure the graded frame, not the albedo.
   - object crops, `"kind": "object", "class": "prop"`: 1-2 whole objects per asset class from each game, tight
     round the object, at the game camera. The sheet shows them beside every asset of that class, so silhouette and
     proportion have a reference; `extract_style` skips them.
4. Run `extract_style.py -- --crops Tools/Blender/Style/crops.json --out Tools/Blender/Style/style_metrics.json
   --swatches Tools/Blender/Style/palette.png`. It measures every shot as if 1080 px tall, the scale `asset_px` is
   given at. `palette.png` holds the palette swatches, a white gap, then the accents; the run prints each cell's
   number, kind, hex and the albedo the toon shader lights to that hex (`SWATCH 3 palette #a0643c toon_albedo
   #9a6039`), so the decision page can name them.
5. Write `style.json` (below) and `STYLE.md` from the metrics, the screenshots and the user's words:
   - `palette`: the swatches the user confirms by eye, renamed by material (Wood, Stone, Foliage), each
     `{"srgb": [...], "smoothness": 0-1}`: the swatch's `srgb`, and a smoothness read off the references (matte wood
     0.1-0.2, painted metal 0.4-0.6); the build reads both. `accents`: the metrics' accents the user keeps.
     For `toon` the screenshots show lit and shade bands, not albedo: write the swatch's `toon_albedo_srgb` (the
     list; `toon_albedo` is its hex for the page), for the accents too, and drop a swatch that is another one's shade
     band (same hue, darker), or the palette holds one material twice. `toon_albedo` is the linear swatch divided by
     the lit band's light, the metrics' `toon_lit`: `light.color` x `intensity` + `ambient` x `ambient_strength`,
     1.09 with Unity's defaults (a white sun of 1, SH ambient 0.5 x 0.18). So write `light` into `style.json` first
     and rerun step 4 with `--style Tools/Blender/Style/style.json`: `toon_lit` then names the game's light, and a
     tinted or dimmed sun or another ambient moves every albedo with it. Read the scene's `ambient` once from the
     game's main scene in the open Editor, `unity command script run --file <absolute .cs path>` (`unity-editor-cli`)
     on a static method that logs `RenderSettings.ambientProbe.Evaluate(new[] { Vector3.up }, c)` into a one-entry
     `Color[] c`: the mean of `c[0]`'s r, g and b (linear) is the level `SampleSH` gives an upward face.
   - `value_range`: pooled `L_p2` - 3 to `L_p98` + 3; `palette_de` 6 for toon and flat, 10 for lit and painted.
     Pooled means all crops' pixels together (each crop sampled to at most 200,000), so a large crop weighs more:
     keep the crops of one game about the same size. A palette or accent colour may sit outside it: the gate checks
     the range only for colours that are within `palette_de` of no role.
   - `look`: pooled `detail_energy`, `dark_edge_share`, `chroma_mean` and `accent_share`, copied as they are.
   - `accent_max_share`: how much of one asset's surface may be accent colour, read off the object crops (a red trim
     on a crate: about 0.1-0.2). The gate measures the surface within `palette_de` of an accent, so `look`'s
     `accent_share` (screenshot pixels of chroma over 60) does not set it.
   - `camera.asset_px` and `asset_m`: a typical prop's height in pixels in a 1080p shot at the game camera, and that
     prop's height in metres; the sheet draws every asset at that scale. `triangles` from them: prop about 3-6 x
     `asset_px` (64 px: 200-400, 128 px: 400-800), hero 3x prop, kit 0.75x prop. A low-poly or faceted look draws
     with fewer: count the faces of a reference object crop at game size and set the band round that count, or put
     the two bands on the decision page.
   - `detail_floor_m`: 2 pixels at game size, 2 x `asset_m` / `asset_px` (128 px, 1 m: 0.016).
   - `flat_waste_max_share`: 0.1. It counts only triangles whose removal leaves the asset looking the same (shape,
     shading, outline, UV map), so the look never pays for it.
   - `curve_waste_max_share`: 0.1 per class the game draws at about `asset_px` (`{"prop": 0.1, "kit": 0.1}`); a
     class it shows larger (a close-up hero) gets no entry. It counts triangles on smooth curves cut finer than
     0.25 px of chord error at game size, and loops along a smooth side's straight way (a tube's height loops) that
     change neither shading, outline nor UV map.
   - `hidden_max_share` 0.05: triangles inside another closed part of the asset (a buried cap) only cost.
     `materials_max` per class (`{"prop": 3, "kit": 2}`): each material is a submesh drawn twice under
     `__GAME__/Toon` (its lit pass and its outline pass). Fewer roles on mobile: merge roles that read the same at
     game size; past that the palette atlas (`texel_density` `"atlas"`, `kit_common.py`'s pattern) is the way up.
   - `shading`: the game's material model (`toon` for the toon-art pack's `__GAME__/Toon`). `outline` and the toon
     fields of `light` (the table below): the values the game draws with, which start as Toon.shader's defaults
     (left out, a field takes the default). A different look changes both the same day: the shader's
     defaults or the builder's material values in Unity, and these fields, or the sheet shows a look the game does
     not draw.
   - `camera` and `light` angles: the game's Main Camera and sun. Yaw 0, pitch 0 looks from Blender's front (-Y);
     with toon-art's axes (Blender (x, y, z) is Unity (-x, z, -y)) a Unity rotation Euler (x, r, 0) is `pitch` x,
     `yaw` 180 - r. `projection` and `fov` from the same camera.
   - `texture_off_palette_max` 0.15 and `texel_density` (`"atlas"` for a palette atlas, else the px per metre the
     brief's platform affords) only when the game textures its assets; `hard_edges_max_share` `null` until the golden
     asset shows a number worth holding; `bevel_m` about 2 pixels at game size, like `detail_floor_m`.

   Show the swatches and 2 test assets (a crate and a rock) built two ways on a decision page: the two readings the
   user was unsure about in step 1 (two palettes, toon or flat, chunky or slim proportions; with none, the two closest
   reference games), each a short build script on the starter (`toon_prop.py` in toon-art). Write the readings as
   `Tools/Blender/Style/style_a.json` and `style_b.json` and run the starter once per reading,
   `-- <project> --style Tools/Blender/Style/style_a.json` (then `style_b.json`): it saves
   `Tools/Blender/checks/<Asset>_style_a.blend` (and `_style_b`) and exports nothing, `--export` or not (a missing
   `--style` file stops it with `CheckError: --style <path> is no file`). Then
   run `contact_sheet.py` on each with `--style` set to the same reading. The user approves one; it becomes
   `style.json`.
6. Build the golden asset: one typical prop of the most common class, through section 2. After the user's yes, copy
   its last sheet's `<Asset>_sheet_r<N>_game.png` (the game-view look tile) to `Tools/Blender/Style/golden.png`; it
   stands beside every later sheet. Keep three calibration anchors in `Tools/Blender/Style/anchors/`, each with its
   score and one line why in `anchors/notes.md`: the golden sheet as `pass.png`; a colour fail as `fail.png` (an early
   round's `_r1`, or the asset with one plain grey 0.5 Principled material: a mesh left on Blender's default material
   draws magenta in the sheet); and a shape fail as `fail_generic.png` (the sheet of the unchanged starter, or of the
   golden rebuilt on default proportions without the Motif), noted "Originality 4: swap test fails, no Motif".

## 2. Every asset

1. Brief: class (a `triangles` key), budget, the reference crop or concept, and where this asset carries STYLE.md's
   `Motif` and how many pixels it spans at `asset_px` (2 or more, or it is lost). A specific reference image of the
   object runs `blender-image-to-3d`'s phases; anything else is a build script in `Tools/Blender/`.
2. The build script takes its colours from the bible, never typed again. In the toon-art pipeline the starter
   `toon_prop.py` does it (`use_style_bible`: the palette, the accents as roles `Accent1..N`, the class's triangle
   band checked at both ends, the outline, `style_class`, `bevel_m`, and the saved `Tools/Blender/checks/<Asset>.blend`;
   `main()` builds at the curve rule's segment count and drops two segments at a time, down to 8, until the triangles
   fit the band's top. Its barrel, one closed surface turned from a profile (a bowed side, two hoops stepped 2 px out,
   heads recessed under a bevelled chime), shows the wiring only: `build()` is rewritten from the brief for every
   asset, never shipped as it is);
   elsewhere:
   `PALETTE = {r: (tuple(v["srgb"]), v["smoothness"]) for r, v in json.load(open(STYLE))["palette"].items()}`, and
   a material's Base Color takes `srgb_to_linear(srgb)` (from `extract_style.py`; Blender colours are linear, and the
   gate's `palette` message names the slip when the raw sRGB numbers are typed in). Base Color is that colour or an
   Image Texture linked straight to it, read through UV0 as it is: FBX follows no Reroute or muted node to the image
   (the gate fails `material`), and Unity's material ignores a Mapping node, or a UV Map node naming another layer, on
   the image's Vector input (the gate fails `texture`: bake the mapping into the UVs). A material still named
   `Material` or `Material.001` at Blender's default grey fails as untouched; a renamed one at that grey is judged as
   the light grey it is. The asset's root object gets the
   custom property `style_class` (`obj["style_class"] = "prop"`, on the object, not its mesh). The starter joins its
   parts into one mesh; a build that keeps several parts parents them under that root, and the gate sums their
   triangles (an Empty that only groups props is not an asset). A piece the game draws without the ink line (toon_prop's `OUTLINE = False`,
   kit and level pieces) sets `obj["outline"] = False` on its root, so the sheet leaves the line off too. A cutout
   links the texture's Alpha to the Principled Alpha; any other texture alpha (the toon-art atlas's smoothness) is
   not transparency. The script saves the `.blend` and exports the FBX only after the user's yes in step 6 (the
   starter: rerun with `-- <project> --export`). Parts under the root are meshes: a Curve, Text or Surface part is
   dropped by the FBX export, so the gate fails it (`mesh`); convert it in the build script.
3. `style_gate.py` on that `.blend`. Exit 1: fix the cause and rebuild; never loosen `style.json` to pass one asset.
   After 3 rebuilds that fail the same rule (two rules pulling apart, such as `triangles` under the band and
   `curve`), stop and put the conflict and the numbers on a decision page for the user.
   Without `--objects` the gate and the sheet take what the FBX export takes: the view layer's render-visible meshes
   and the hidden parts under a root with `style_class`, minus Boolean cutters, `COL_` and `_LOD1+`. An `--objects`
   list that names only some parts of an asset prints a `STYLE NOTE` with the parts it left out.
   A `triangles` failure under the band: the asset is plainer than the style; add the detail the references show at
   `asset_px` (bevels, rims, planks, a trim), never cuts on flat faces (the `waste` rule) or extra segments (the
   `curve` rule). Over the band: remove detail the game size cannot show, starting with what `detail` and `curve`
   name. An `instances` failure: realize the instances in the build script before saving. A `hidden` failure: leave
   the buried faces out (step the detail out of one closed surface, as the starter's hoops, or make it an open band
   round the body). A `materials` failure: each material is a submesh drawn twice under `__GAME__/Toon` with its
   outline; merge roles that read the same at game size, or, with `texel_density` `"atlas"`, use the palette atlas.
   A `waste` failure: drop the cuts on flat faces in the build script (no subdivide or loop cut where nothing bends).
   Where a shared helper has to cut, call `style_gate.flat_waste` on the bmesh (import it from `$S`, or copy it into
   the game's build module with what it calls: `flat_faces`, `corner_normals`, `same_uv_map`, `affine`, `FLAT_DEG`,
   `TEXTURE_SIDE`) and write the bmesh back: it dissolves and triangulates only what the gate counted. A bare Limited
   Dissolve (`dissolve_limit`) is not that: it also drops the edge midpoints the outline needs, warps a 9-slice UV and
   leaves n-gons for Unity to triangulate. Never Decimate to meet a budget: the look comes first, and Decimate removes
   shape.
   A `curve` failure: give each round part `ceil(pi / acos(1 - 0.25 / r_px))` segments around, `r_px` = radius x
   `asset_px` / `asset_m` (16 px radius: 18, 32 px: 26, 64 px: 36), and half that along a sphere's height. The
   message splits the count: the part that cuts a smooth side along its straight way goes by dropping those loops.
4. `contact_sheet.py -- --style ... --out Tools/Blender/<Asset>/review/<Asset>_sheet_r<N>.png --crops
   Tools/Blender/Style/crops.json --class <class> --golden Tools/Blender/Style/golden.png` (`--refs <files>` adds
   whole images), `<N>` the review round from 1, so every round's sheet, `.json` and `_game.png` stay for the A/B
   and the anchors. The golden asset's own sheets go without a golden (the script notes it and goes on). Read the
   sheet: rows front, right, back, top, game camera, references (the class's object crops); columns silhouette,
   clay, look. Its `.json` holds the game view's L* range, `inside_value_range` (0.9 or more; for toon: of the pixels
   nearer a lit band than a shade band, since the shade band sits below the references' range by design),
   `palette_coverage` (0.85 or more for toon and flat from `asset_px` 64 up: the share of the asset's pixels, the ink
   ring and one pixel inside it left out, within `palette_de` of a drawn colour, its bands, ink and the blends
   between them; under 64 px the edge pixels weigh more, so compare it with the golden's) and the `look` numbers
   beside the references'. A `chroma_mean` more than 10 from the references' prints a `SHEET WARNING`: the colour
   lens makes it a fix unless STYLE.md says why. `silhouette_fill` holds per view the asset's pixels over its
   bounding box's; front and right both at 0.95 or more print `SHEET NOTE: front and side silhouettes fill ... a
   primitive's outline` (say in the brief what in the silhouette is not a box or can, or why it wants one). `motif`
   is false, with a `SHEET WARNING`, when `STYLE.md` beside `--style` is missing or has no line starting `Motif:`;
   write it before the review. A reference file missing on this machine (a new clone: the shots
   stay local, step 1.2) prints a `SHEET NOTE` and leaves its tile out; copy `Tools/Blender/Style/reference/` over.
5. Review: two `gamekit:art-reviewer` agents in parallel, each fresh, one with `lens: shape` and one with `lens:
   colour`, each given the sheet, its `.json`, `STYLE.md`, `style.json`, `Tools/Blender/Style/anchors/` and the
   brief, never the build script. From round 2 the previous round's sheet too (A/B). Each fix round reruns steps
   2-4 (build, gate, sheet as `_r<N+1>`): a gate failure is fixed before the reviewers see the round. Done when both
   score at least 8/10 with no blocker; at most 3 rounds, then show the user the sheet and the open findings.
6. The user sees the final sheet before export. Show a sheet with `SendUserFile` (`display: render`), so it opens
   beside the chat and reaches the phone; without that tool, give its path as a link. After the user's yes, rerun the
   build with its export on (`toon_prop.py ... -- <project> --export`), then `unity-export`, and the
   final judgement is an in-engine capture at the game camera (`gk-bridge play-capture`) beside a reference crop and
   the sheet's game tile. Compare three things: the L* range, the shade band's hue, the outline's width. Measure the
   L* range the same way on both images: a crops file each (`capture_crops.json` on the whole capture, `tile_crops.json`
   on the sheet's `_game.png`) with one rect on the same surfaces of the asset, tight inside it (no ground, no ink
   line), then `extract_style.py -- --crops <file> --out <file>_metrics.json` on each; their pooled `L_p2` and
   `L_p98` within 3 is the same. A
   difference from the sheet is drift between `style.json` and the game: set `light`, `outline` and Toon.shader's
   values equal the same day (section 1, step 5), then rerun the sheet; a difference from the reference crop alone
   goes back to step 2 of this section.
7. A helper that repeats across assets (a trim, a plank, an edge-wear recipe) moves into the game's shared build
   module, so the next asset reuses it instead of re-inventing it.

Every 5-10 approved assets: append them into one `.blend` in a row and run `contact_sheet.py` on it; its game row is
the kit lineup. Two art-reviewer passes, `lens: shape` and `lens: colour`, look for drift (a bevel or a detail
density, a colour or a value that differs). Append
with this script, run headless (`blender --background --factory-startup --python-exit-code 1 --python
Tools/Blender/lineup.py`), then run the sheet on `Tools/Blender/checks/lineup.blend`:
```python
import json, os, bpy
from mathutils import Vector
bpy.ops.wm.read_factory_settings(use_empty=True)
paths = ["Tools/Blender/checks/SM_Crate.blend", "Tools/Blender/checks/SM_Barrel.blend"]  # the approved assets
asset_m = json.load(open("Tools/Blender/Style/style.json"))["camera"].get("asset_m", 1.0)
x = 0.0
for path in paths:
    # an absolute path: after read_factory_settings a relative one resolves against the drive root
    with bpy.data.libraries.load(os.path.abspath(path)) as (src, dst):
        dst.objects = src.objects
    for o in dst.objects:
        bpy.context.scene.collection.objects.link(o)
    bpy.context.view_layer.update()
    xs = [(o.matrix_world @ Vector(c)).x for o in dst.objects if o.type == 'MESH' for c in o.bound_box]
    for o in dst.objects:
        if o.parent is None:
            o.location.x += x - min(xs)  # the roots; parts follow their parent
    x += max(xs) - min(xs) + 0.5 * asset_m  # each asset its own width apart, plus a gap
bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath("Tools/Blender/checks/lineup.blend"))
```
Keep a lineup the sheet draws at 1x: a row holds at most `floor(1024 / (1.6 x asset_px))` assets (5 at 128 px, 10
at 64 px); when it prints `SHEET WARNING ... drawn at <1 x`, split the row, or the bevels it is meant to compare fall
under a pixel.

## style.json

```json
{
  "game": "__GAME__",
  "references": [{"game": "<name>", "take": "palette, chunky proportions"}],
  "shading": "toon",
  "outline": {"px": 1.5, "srgb": [0.36, 0.30, 0.46]},
  "camera": {"projection": "ortho", "pitch": 35, "yaw": 45, "fov": 40, "asset_px": 128, "asset_m": 1.0},
  "light": {"pitch": 50, "yaw": -30, "band": 0.05, "shadow_srgb": [0.62, 0.62, 0.86], "shade_saturation": 1.3,
            "ambient": 0.5, "color": [1.0, 1.0, 1.0], "intensity": 1.0},
  "palette": {"Wood": {"srgb": [0.74, 0.49, 0.28], "smoothness": 0.15},
              "WoodDark": {"srgb": [0.52, 0.32, 0.19], "smoothness": 0.10},
              "Metal": {"srgb": [0.59, 0.63, 0.71], "smoothness": 0.55}},
  "accents": [[0.95, 0.15, 0.10]],
  "palette_de": 6,
  "value_range": [18, 92],
  "accent_max_share": 0.12,
  "look": {"detail_energy": 2.4, "dark_edge_share": 0.031, "chroma_mean": 28.5, "accent_share": 0.006},
  "texture_off_palette_max": 0.15,
  "texel_density": "atlas",
  "triangles": {"hero": [1200, 2400], "prop": [400, 800], "kit": [300, 600]},
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

| Field | Meaning | Checked by |
|---|---|---|
| `shading`, `outline` | `toon`, `flat`, `lit` or `painted`: the Unity shading model the look pass copies; the ink line (`true` = Toon.shader's 1.5 px at 1080p, tint `srgb`; `false` = none); the sheet draws these numbers, so they stay equal to the shader's (step 1.5) | contact_sheet, toon_prop (`outline`) |
| `camera` | the game camera; `projection` `"ortho"` or `"persp"` (`"orthographic"` and `"perspective"` also read; any other value stops the sheet); `asset_px` = a typical prop's height in pixels in a 1080p frame, `asset_m` = its height in metres (default 1) | contact_sheet, style_gate (`curve`) |
| `light` | sun direction; toon only: `band` = the N.L of the shadow edge, `shadow_srgb`, `shade_saturation` = the shade band (Toon.shader `_RampOffset`, `_ShadeColor`, `_ShadeSaturation`), `ambient` = the scene's SH level, `color` (sRGB) and `intensity` = the main light's (both bands scale with them), `contact_shade` 0.3, `ground_y` -0.06 and `contact_height` 0.25 = the darkening toward the floor (Toon.shader `_ContactShade`, `_GroundY`, `_ContactHeight`; the `.blend`'s z = 0 is the game's floor), `softness` 0.035, `ambient_strength` 0.18, `spot` 0.85, `rim` 0.5, `rim_edge` 0.62 (`_RampSoftness`, `_AmbientStrength`, `_SpecularStrength`, `_RimStrength`, `_RimEdge`; a field left out takes that default); equal to the shader's and the scene's values (`ambient` read once from the scene, step 1.5; extract_style's `--style` divides `toon_albedo` by this light). The glossy spot and the rim take the smoothness the game gets: an `M_<Role>` material's palette role smoothness, else 1 - a set Principled Roughness, else 1 - the viewport roughness. The sheet renders under its own world and this sun only; lights in the `.blend` are left out (a `SHEET NOTE` names them) | contact_sheet |
| `palette`, `accents`, `palette_de`, `accent_max_share` | the roles (sRGB 0-1), how far (CIELAB distance) a colour may sit from one, and how much of an asset's surface may be accent (by colour: any face or texel within `palette_de` of an accent counts, whatever its role) | style_gate, contact_sheet |
| `texture_off_palette_max` | share of a texture's area (read through UV0, the map the game samples) whose colour sits off every role | style_gate |
| `value_range`, `look` | L* 0-100 the asset's off-role colours stay in (a palette or accent colour is exempt); the references' pooled look numbers, shown beside the asset's (`detail_energy` and `dark_edge_share` come from surface crops and read higher on any whole asset) | style_gate, contact_sheet |
| `triangles`, `detail_floor_m`, `texel_density`, `hard_edges_max_share` | budgets per class (per asset root); smallest loose part; px per metre or `"atlas"`; share of unbevelled hard edges (`null` = report only) | style_gate |
| `flat_waste_max_share` | share of an asset's triangles that only split flat, flat-normal faces of one material and one affine UV map, away from the edges that shape the outline: removing them leaves the render the same (`null` = report only) | style_gate |
| `curve_waste_max_share` | per class (a number: every class): share of an asset's triangles that refine smooth curves past 0.25 px of chord error at `asset_px` (fewer segments look the same at game size), or cut a smooth side along its straight way with shading, outline and UV map unchanged (a class without an entry = report only) | style_gate |
| `hidden_max_share`, `materials_max` | share of an asset's triangles whose centre lies inside another closed part of it (a cap buried in the body; an open part, such as a label plane, buries nothing); materials per asset, per class or one number (each one a submesh drawn twice under `__GAME__/Toon`, lit and outline: fewer roles on mobile, merge roles that read the same at game size; the palette atlas, `kit_common.py`'s pattern, is the way up); `null` or left out = report only | style_gate |

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
first.

## Limits

- Organic characters and creatures are the weak spot of scripted bpy. An AI image-to-3D mesh (TRELLIS.2, Hunyuan3D)
  is a separate setup the user decides on, and its output passes the same gates after retopology.
- Brush-stroke hand painting is not reachable headless; `painted` reaches stylised baked colour. A paid cloud
  retexture service is only used after the user's yes.
- Blender's look pass is a stand-in for the Unity shader: it draws the bands, spot, rim and contact shade, but SH
  ambient as one level, not sampled by the normal, and no post-processing; the in-engine capture decides.
- The `look` numbers compare a whole reference frame with one asset, so they guide the reviewers and gate nothing.
- `curve` estimates each smooth edge's radius from its two faces and counts half the triangles of faces whose
  curved edges are all past the bound, so it errs low: it catches twice the segments a curve needs (a 64x32 ball,
  a 64-sided cylinder at prop size), not a few too many. Height loops count only where the baked outline normal
  stays affine, so a tube under hard caps keeps them (its rims tilt the outline). It reads asset_px as the size on
  screen, so a part the game zooms in on needs its own class.
