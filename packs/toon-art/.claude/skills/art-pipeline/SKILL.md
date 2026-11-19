---
name: art-pipeline
description: Use when adding or changing a model, prop, kit piece, clip or material, after a rebuild, or before judging the look or outline. __GAME__'s generated art - Blender script, FBX + JSON manifest, postprocessor, builder prefab, __GAME__/Toon.
---

# Art pipeline

This skill is the Unity side of generated art: the script's contract, the import, the builder and the shader.
Modelling inside Blender itself is the global Blender skills (start with `blender-director`; from a reference image,
`blender-image-to-3d`), and the export arguments are the `unity-export` skill.

Art is **generated, never hand-edited**. A Blender script is the source; the FBX, the materials and the prefabs are
outputs that a rebuild overwrites. Fix the script, rebuild, never patch an output.

## The chain

1. **Blender script** in `Tools/Blender/<thing>.py`, run headless:
   `blender --background --factory-startup --python-exit-code 1 --python Tools/Blender/<thing>.py -- <args>` (without
   `--python-exit-code 1` a Python error exits 0; `--factory-startup` keeps user add-ons and prefs out of the build).
   It builds the mesh (and rig and clips), checks itself (polycount, naming, palette rules: fail the run on a broken rule rather than export it), and exports
   `Assets/__GAME__/Game/Art/Models/<Thing>.fbx` at Unity scale. Check renders go to `Tools/Blender/checks/`
   (gitignored).
2. **Manifest**: when Unity needs more than the mesh (pivots, walk heights, collider boxes, which piece is which
   variant), the script also writes `<Thing>.json` next to the FBX: public fields named like `JsonUtility` reads them,
   no dictionaries, no nulls, every number already in Unity space. Nothing on the Unity side converts from Blender.
3. **AssetPostprocessor** (`Editor/Art/<Thing>ModelPostprocessor.cs`) pins the import for its own files: scale,
   no rig or Generic rig, clip flags, material naming. Each one owns a disjoint set of paths, never a shared prefix:
   the prop pin takes only the FBX files directly in `Game/Art/Models/`, and an asset in a subfolder
   (`Models/<Asset>/`) gets its own postprocessor, which keeps a rig as Generic or Humanoid and imports its clips (two
   pins on one path fight, and the order decides). Raise `GetVersion()` when it changes so the models reimport.
   `OutlineNormalsPostprocessor` is one already: it bakes smoothed normals into every mesh under
   `Game/Art/Models/` for the outline.
4. **Builder** (`Editor/Art/<Thing>Builder.cs`, a `__GAME__/Art/Rebuild <Thing>` menu item) reads the manifest and
   makes the materials and prefabs **in place** (same path, same GUID, so scenes keep their references). It is
   rerunnable: it strips what it made last time first.

Examples live only in the template, never in a game: `C:\GitHub\unity-game-template\packs\toon-art\examples\`.

- **Start from** `toon_prop.py` + `PropBuilder.cs.txt`: the whole chain for one prop, generic and runnable. The script
  builds, checks (triangle budget, palette roles, pivot, identity transform) and exports with the `unity-export`
  preset into `Game/Art/Models/`, and writes the manifest; the C# file pins the import and rebuilds the materials and
  prefab in place. With a style bible (`Tools/Blender/Style/style.json`,
  `${CLAUDE_PLUGIN_ROOT}/skills/genre-defaults/references/style-bible.md`) it takes the palette and the triangle band
  from there, tags the root's `style_class` and saves `Tools/Blender/checks/<Thing>.blend`; run that bible's
  `style_gate.py` and `contact_sheet.py` on it before the user sees the asset.
- `kit_common.py` (Mixtrol): a large real kit module for a modular level kit (pieces, hosts, colliders, walk heights,
  a palette atlas). Read it for those patterns only: it imports Mixtrol's `kit_palette.py` (not included, so it does
  not run here), its paths are Mixtrol's (`Art/LevelKit`, `Game/Art/LevelKit`, outside the folder that gets outline
  normals), and its ticket numbers are Mixtrol's. Its axis mapping is Mixtrol's too: a `Euler(90, 0, 0)` child and
  Blender (x, y, z) to Unity (x, z, y), so never lift its `to_unity()` or host maths; pair the template's
  `Euler(90, 180, 0)` builder child with `toon_prop.py`'s `to_unity()` (below). Its export call does follow the preset.
- `LevelKitModelPostprocessor.cs.txt` (Mixtrol): a postprocessor with texture rules (a point-filtered palette atlas).
- `city_assets.py` (Pixel Volley): the modelling helpers of a toy-town set. Pre-contract: its export
  (`FBX_SCALE_UNITS`, `bake_space_transform=True`, a manual half turn) and its output folder are not the template's;
  never copy them, copy the export from `toon_prop.py`.

## Axes and scale

Export with the `unity-export` skill's settings. An imported mesh keeps Blender X and negates Z: measure a direction on
the vertices before rotating one in code. One metre is one metre; never fix scale on the Unity side.

Author the front toward Blender -Y (the Front view). The builder's `Mesh` child is turned `Euler(90, 180, 0)`, so the
front faces the prefab's `transform.forward` (+Z) and a Blender point (x, y, z) lands at Unity (-x, z, -y); the
script's `to_unity()` writes the manifest in that space. A character or vehicle moving along `transform.forward` then
looks where it goes.

## From `blender-image-to-3d`

An asset made from a reference image keeps that skill's layout, moved into the game:

- The master `.blend`, the numbered `build/NN_<phase>.py` scripts and the review renders go under
  `Tools/Blender/<Asset>/` (out of `Assets/`; its `review/` renders stay out of git: the game's `.gitignore` already ignores
  `/Tools/Blender/**/review/` and `checks/`). The build scripts are the source.
- `export_delivery.py --format FBX --engine unity` writes with `--out Assets/__GAME__/Game/Art/Models/<Asset>/`, so the
  FBX, its base-colour PNGs and `asset-manifest.json` land where `OutlineNormalsPostprocessor` bakes outline normals.
  Bake `--maps basecolor` only (below).
- An `<Asset>Builder.cs` reads `asset-manifest.json` (that skill's schema, not `PropBuilder`'s `<Thing>.json`) and, in
  place: makes the `__GAME__/Toon` materials through `ToonShader.Apply`, sets the `LODGroup` Unity makes from the
  `_LOD0..N` objects to the brief's screen heights, turns every `COL_<Name>` mesh into a convex `MeshCollider` with its
  renderer removed, and saves the prefab. `PropBuilder.cs.txt` has none of the LOD or `COL_` steps; the `unity-export`
  skill's LODs and collision section is the contract they follow.
- Done means the `unity-export` import check: Unity's triangle count per LOD, height and `min_y` match the manifest.

## The look: `__GAME__/Toon`

Every lit material is `__GAME__/Toon` (`Game/Art/Shaders/Toon.shader`), never URP/Lit: two bands of light and shade
with a saturated tinted shade (both bands scale with the main light, so a dim sun dims the shade too), shadows cut to
the same edge, a glossy spot and rim driven by Smoothness, contact shading near `_GroundY`, and an ink outline tinted from the surface colour. Same property names as URP/Lit, so a builder swaps
the shader and keeps the colours.

- Make or retarget a material only through `ToonShader.Apply(material, outline)`. The outline is a second pass; a
  material without it has the pass switched off so it costs no extra draw. On phones keep outlines for what the player
  must read (characters, carried things), not the whole level.
- Outline width is in 1080p pixels, so it reads the same on a phone and a monitor.
- A mesh outside `Game/Art/Models/` gets no smoothed normals; its outline may split at hard edges.
- Bake or paint only the base map for a toon asset (`bake_maps.py --maps basecolor`, or a palette atlas); Smoothness
  is a material value. No normal, AO or mask map: the shader samples none, and `OutlineNormalsPostprocessor`
  overwrites the tangents under `Game/Art/Models/`. The `unity-export` skill has the per-shader texture table.
- Lighting it takes: the main light with its shadows (fading out at the shadow distance), point and spot lights in the
  same two bands (Forward and Forward+), light layers, fog, ambient from light probes or Adaptive Probe Volumes, SSAO
  (both bands and the ambient), DBuffer decals on the surface colour, and motion vectors for TAA, STP and motion blur
  (the outline hull has none of its own). It does not sample baked
  lightmaps or shadowmask: light toon objects in real time and give them baked light through probes.
- Keep the URP renderer's **Depth Priming Mode on Disabled** (the default). Depth priming draws the opaque list with
  ZTest Equal, and the outline hull, which is not in the depth prepass, disappears.
- After changing `Toon.shader`, run `__GAME__/Art/Check Toon Shader` (ProjectSetup runs it too): it compiles every
  pass for the main keyword sets (the Mobile tier's among them), and ForwardLit and Outline also for GLES3, Vulkan and
  Metal (Mobile tier and Forward+ variants) where those build modules are installed, then logs `[toon-art] Toon shader OK (device APIs: ...)` or each
  error. A shader error otherwise shows only as a pink object in Play Mode or on a device.
- Contact shading is world-space: one ground height per material (`_GroundY`, default just under y = 0). It suits a
  level whose floor is one plane at y = 0; with raised platforms or several floor heights set `_ContactShade` to 0 (or
  `_GroundY` per material), or everything below the plane reads about 30% darker, like a lighting bug.
- Tune the look on a reference scene from the game camera, on both quality tiers, before changing every material, and
  check a dark case too (the sun dimmed to about 0.2, or off with only point lights): the shade side must stay darker
  than the lit side.

## Rules

- Never edit an FBX, a generated material, a generated prefab or a controller by hand; change the script or the builder.
- A colour or palette rule lives in the Blender script's check, so a rebuild that breaks it fails.
- Keep `.blend` files out of `Assets/`; a `.blend` there makes Unity import it through a Blender install.
