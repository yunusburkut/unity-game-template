# Style bible: a named game's look as numbers, then every asset gated against them

Claude-made 3D art looks generic ("AI slop") when nothing pins the style before modelling: palette, value range,
budgets and shading are invented per asset. The style bible fixes them once per game in `Tools/Blender/Style/`, and
every Blender asset is then measured against it. It runs before the first Blender asset of a game whose DESIGN.md
Look names reference games, or when the user asks for assets "like game X". Shape matching from one reference image
stays `blender-image-to-3d`'s job; this adds the style layer around it. Export stays `unity-export`.

Not a copy: a named game guides palette, value range, proportions, detail density, shading and light. Its characters,
logos, layouts and distinctive designs are never rebuilt, and its screenshots stay reference only: never under
`Assets/`, never shipped, never used to train a model.

Scripts, run headless with Blender's own numpy and OpenImageIO (`S=${CLAUDE_PLUGIN_ROOT}/skills/genre-defaults/scripts`):

| Script | Input | Output |
|---|---|---|
| `${CLAUDE_PLUGIN_ROOT}/skills/genre-defaults/scripts/extract_style.py` | screenshots or `crops.json` | `style_metrics.json`, a swatch strip |
| `${CLAUDE_PLUGIN_ROOT}/skills/genre-defaults/scripts/style_gate.py` | the asset's saved `.blend`, `style.json` | PASS, or exit 1 with each failure's rule and number |
| `${CLAUDE_PLUGIN_ROOT}/skills/genre-defaults/scripts/contact_sheet.py` | the `.blend`, `style.json`, reference crops | review sheet PNG and its `.json` |

Every call is `blender --background --factory-startup --python-exit-code 1 [<asset>.blend] --python "$S/<script>" --
<args>`; each script's header lists its arguments. Without `--python-exit-code 1` a crash exits 0 and reads as a pass.
`${CLAUDE_PLUGIN_ROOT}/skills/genre-defaults/evals/test_style_bible.py` is their fixture test (template `test-all.ps1`).

## 1. Make the bible (once per game, about 1-2 h)

1. Ask the user for 1-3 games, what to take from each (colour, shapes, shading, detail level), the game's camera
   (top-down, isometric, third person, first person, side) and platform. A seen choice between readings goes on a
   decision page (`${CLAUDE_PLUGIN_ROOT}/skills/pipeline/references/decision-page.md`).
2. The user drops 10-20 of their own screenshots per game into `Tools/Blender/Style/reference/<Game>/`: several
   distances, little UI, a few evenly lit, at least 3 from the camera this game will use.
3. Look at each shot (Read) and write `Tools/Blender/Style/crops.json`, two kinds of rect:
   - surface crops (the default): evenly lit surfaces of the kind of asset this game needs, for the numbers. Leave
     out UI, fog, bloom, motion blur and night scenes: the numbers measure the graded frame, not the albedo.
   - object crops, `"kind": "object", "class": "prop"`: 1-2 whole objects per asset class from each game, tight
     round the object, at the game camera. The sheet shows them beside every asset of that class, so silhouette and
     proportion have a reference; `extract_style` skips them.
4. Run `extract_style.py -- --crops Tools/Blender/Style/crops.json --out Tools/Blender/Style/style_metrics.json
   --swatches Tools/Blender/Style/palette.png`. It measures every shot as if 1080 px tall, the scale `asset_px` is
   given at.
5. Write `style.json` (below) and `STYLE.md` from the metrics, the screenshots and the user's words:
   - `palette`: the swatches the user confirms by eye, renamed by material (Wood, Stone, Foliage); `accents`: the
     metrics' accents the user keeps.
   - `value_range`: pooled `L_p2` - 3 to `L_p98` + 3; `palette_de` 6 for toon and flat, 10 for lit and painted.
   - `look`: pooled `detail_energy`, `dark_edge_share`, `chroma_mean` and `accent_share`, copied as they are.
   - `accent_max_share`: how much of one asset's surface may be accent colour, read off the object crops (a red trim
     on a crate: about 0.1-0.2). The gate measures the surface within `palette_de` of an accent, so `look`'s
     `accent_share` (screenshot pixels of chroma over 60) does not set it.
   - `camera.asset_px` and `asset_m`: a typical prop's height in pixels in a 1080p shot at the game camera, and that
     prop's height in metres; the sheet draws every asset at that scale. `triangles` from them: prop about 3-6 x
     `asset_px` (64 px: 200-400, 128 px: 400-800), hero 3x prop, kit 0.75x prop.
   - `detail_floor_m`: 2 pixels at game size, 2 x `asset_m` / `asset_px`.

   Show the swatches and 2 test assets (a crate and a rock) built two ways on a decision page; the user approves.
6. Build the golden asset: one typical prop of the most common class, through section 2. After the user's yes, copy
   its sheet's `<Asset>_sheet_game.png` (the game-view look tile) to `Tools/Blender/Style/golden.png`; it stands
   beside every later sheet. Keep two calibration anchors in `Tools/Blender/Style/anchors/`: the golden sheet as
   `pass.png` and one rejected sheet (an early round, or the asset with Blender's default material) as `fail.png`,
   each with its score and one line why in `anchors/notes.md`.

## 2. Every asset

1. Brief: class (a `triangles` key), budget, the reference crop or concept. A specific reference image of the object
   runs `blender-image-to-3d`'s phases; anything else is a build script in `Tools/Blender/`.
2. The build script takes its colours from the bible, never typed again. In the toon-art pipeline:
   `PALETTE = {r: (tuple(v["srgb"]), v["smoothness"]) for r, v in json.load(open(STYLE))["palette"].items()}`. The
   asset's root object gets the custom property `style_class` (`obj["style_class"] = "prop"`, on the object, not
   its mesh); a multi-part asset parents its parts under that root, and the gate sums their triangles (an Empty that
   only groups props is not an asset). A piece the game draws without the ink line (toon_prop's `"outline": False`,
   kit and level pieces) sets `obj["outline"] = False` on its root, so the sheet leaves the line off too. A cutout
   links the texture's Alpha to the Principled Alpha; any other texture alpha (the toon-art atlas's smoothness) is
   not transparency. The script saves the `.blend` it exported.
3. `style_gate.py` on that `.blend`. Exit 1: fix the cause and rebuild; never loosen `style.json` to pass one asset.
   An `--objects` list that names only some parts of an asset prints a `STYLE NOTE` with the parts it left out.
4. `contact_sheet.py -- --style ... --out Tools/Blender/<Asset>/review/<Asset>_sheet.png --crops
   Tools/Blender/Style/crops.json --class <class> --golden Tools/Blender/Style/golden.png` (`--refs <files>` adds
   whole images). Read the sheet: rows front, right, back, top, game camera, references (the class's object crops);
   columns silhouette, clay, look. Its `.json` holds the game view's L* range, `inside_value_range`,
   `palette_coverage` (0.85 or more for toon and flat) and the `look` numbers beside the references'.
5. Review: two `gamekit:art-reviewer` agents in parallel, each fresh, one with `lens: shape` and one with `lens:
   colour`, each given the sheet, its `.json`, `STYLE.md`, `style.json`, `Tools/Blender/Style/anchors/` and the
   brief, never the build script. Previous sheet too from round 2 (A/B). Done when both score at least 8/10 with no
   blocker; at most 3 rounds, then show the user the sheet and the open findings.
6. The user sees the final sheet before export. Then `unity-export`, and the final judgement is an in-engine capture
   at the game camera (`gk-bridge play-capture`) beside a reference crop.
7. A helper that repeats across assets (a trim, a plank, an edge-wear recipe) moves into the game's shared build
   module, so the next asset reuses it instead of re-inventing it.

Every 5-10 approved assets: append them into one `.blend` in a row and run `contact_sheet.py` on it; its game row is
the kit lineup. One art-reviewer pass looks for drift (a colour, a bevel or a detail density that differs).

## style.json

```json
{
  "game": "__GAME__",
  "references": [{"game": "<name>", "take": "palette, chunky proportions"}],
  "shading": "toon",
  "outline": {"px": 1.5, "srgb": [0.36, 0.30, 0.46]},
  "camera": {"projection": "ortho", "pitch": 35, "yaw": 45, "fov": 40, "asset_px": 128, "asset_m": 1.0},
  "light": {"pitch": 50, "yaw": -30, "band": 0.05, "shadow_srgb": [0.62, 0.62, 0.86], "shade_saturation": 1.3,
            "ambient": 0.5},
  "palette": {"Wood": {"srgb": [0.78, 0.52, 0.30], "smoothness": 0.15}},
  "accents": [[0.95, 0.15, 0.10]],
  "palette_de": 6,
  "value_range": [18, 92],
  "accent_max_share": 0.12,
  "look": {"detail_energy": 2.4, "dark_edge_share": 0.031, "chroma_mean": 28.5, "accent_share": 0.006},
  "texture_off_palette_max": 0.15,
  "texel_density": "atlas",
  "triangles": {"hero": [1200, 2400], "prop": [400, 800], "kit": [300, 600]},
  "detail_floor_m": 0.03,
  "bevel_m": 0.02,
  "hard_edges_max_share": null,
  "avoid": ["thin parts that vanish at asset_px", "a second outline width"]
}
```

| Field | Meaning | Checked by |
|---|---|---|
| `shading`, `outline` | `toon`, `flat`, `lit` or `painted`: the Unity shading model the look pass copies; the ink line (`true` = Toon.shader's 1.5 px at 1080p, tint `srgb`; `false` = none) | contact_sheet |
| `camera` | the game camera; `asset_px` = a typical prop's height in pixels in a 1080p frame, `asset_m` = its height in metres (default 1) | contact_sheet |
| `light` | sun direction; toon only: `band` = the N.L of the shadow edge, `shadow_srgb`, `shade_saturation` = the shade band (Toon.shader `_RampOffset`, `_ShadeColor`, `_ShadeSaturation`), `ambient` = the scene's SH level | contact_sheet |
| `palette`, `accents`, `palette_de`, `accent_max_share` | the roles (sRGB 0-1), how far (CIELAB distance) a colour may sit from one, and how much of an asset's surface may be accent | style_gate, contact_sheet |
| `value_range`, `look` | L* 0-100 the asset's colours stay in; the references' pooled look numbers, shown beside the asset's | style_gate, contact_sheet |
| `triangles`, `detail_floor_m`, `texel_density`, `hard_edges_max_share` | budgets per class (per asset root); smallest loose part; px per metre or `"atlas"`; share of unbevelled hard edges (`null` = report only) | style_gate |

`bevel_m` and `avoid` are for the build and the reviewers; no script measures them. A threshold (`palette_de`,
`value_range`) is tuned on the golden asset, then frozen; a later change re-runs the gate on every approved asset.

## STYLE.md

The words the numbers cannot hold, at most one screen: the 3-5 rules that make the look (proportion, edge
treatment, how much detail and where, how shadows are coloured), what each reference game gives, the named mistakes,
and the tie-breaker when two rules collide (for example "readability at asset_px beats detail").

## Limits

- Organic characters and creatures are the weak spot of scripted bpy. An AI image-to-3D mesh (TRELLIS.2, Hunyuan3D)
  is a separate setup the user decides on, and its output passes the same gates after retopology.
- Brush-stroke hand painting is not reachable headless; `painted` reaches stylised baked colour. A paid cloud
  retexture service is only used after the user's yes.
- Blender's look pass is a stand-in for the Unity shader (no gloss spot, rim or contact shade); the in-engine capture
  decides.
- The `look` numbers compare a whole reference frame with one asset, so they guide the reviewers and gate nothing.
