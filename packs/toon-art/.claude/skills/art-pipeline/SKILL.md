---
name: art-pipeline
description: Making or changing __GAME__'s generated 3D art - a model, prop, kit piece, clip or material, a rebuild, judging the look. Blender script -> FBX + JSON manifest -> postprocessor -> builder prefab; the __GAME__/Toon shader and its outline.
---

# Art pipeline

This skill is the Unity side of generated art: the script's contract, the import, the builder and the shader.
Modelling inside Blender itself is the global Blender skills (start with `blender-director`; from a reference image,
`blender-image-to-3d`), and the export arguments are the `unity-export` skill.

Art is **generated, never hand-edited**. A Blender script is the source; the FBX, the materials and the prefabs are
outputs that a rebuild overwrites. Fix the script, rebuild, never patch an output.

## The chain

1. **Blender script** in `Tools/Blender/<thing>.py`, run headless:
   `blender --background --python-exit-code 1 --python Tools/Blender/<thing>.py -- <args>` (without the flag a
   Python error exits 0). It builds the mesh (and rig and clips), checks itself (polycount, naming, palette rules: fail the run on a broken rule rather than export it), and exports
   `Assets/__GAME__/Game/Art/Models/<Thing>.fbx` at Unity scale. Check renders go to `Tools/Blender/checks/`
   (gitignored).
2. **Manifest**: when Unity needs more than the mesh (pivots, walk heights, collider boxes, which piece is which
   variant), the script also writes `<Thing>.json` next to the FBX: public fields named like `JsonUtility` reads them,
   no dictionaries, no nulls, every number already in Unity space. Nothing on the Unity side converts from Blender.
3. **AssetPostprocessor** (`Editor/Art/<Thing>ModelPostprocessor.cs`) pins the import for that folder: scale,
   no rig or Generic rig, clip flags, material naming. Raise `GetVersion()` when it changes so the models reimport.
   `OutlineNormalsPostprocessor` is one already: it bakes smoothed normals into every mesh under
   `Game/Art/Models/` for the outline.
4. **Builder** (`Editor/Art/<Thing>Builder.cs`, a `__GAME__/Art/Rebuild <Thing>` menu item) reads the manifest and
   makes the materials and prefabs **in place** (same path, same GUID, so scenes keep their references). It is
   rerunnable: it strips what it made last time first.

Examples live only in the template, never in a game: `C:\GitHub\unity-game-template\packs\toon-art\examples\`.

- **Start from** `toon_prop.py` + `PropBuilder.cs.txt`: the whole chain for one prop, generic and runnable. The script
  builds, checks (triangle budget, palette roles, pivot, identity transform) and exports with the `unity-export`
  preset into `Game/Art/Models/`, and writes the manifest; the C# file pins the import and rebuilds the materials and
  prefab in place.
- `kit_common.py` (Mixtrol): a large real kit module for a modular level kit (pieces, hosts, colliders, walk heights,
  a palette atlas). Read it for those patterns only: it imports Mixtrol's `kit_palette.py` (not included, so it does
  not run here), its paths are Mixtrol's (`Art/LevelKit`, `Game/Art/LevelKit`, outside the folder that gets outline
  normals), and its ticket numbers are Mixtrol's. Its export call does follow the preset.
- `LevelKitModelPostprocessor.cs.txt` (Mixtrol): a postprocessor with texture rules (a point-filtered palette atlas).
- `city_assets.py` (Pixel Volley): the modelling helpers of a toy-town set. Pre-contract: its export
  (`FBX_SCALE_UNITS`, `bake_space_transform=True`, a manual half turn) and its output folder are not the template's;
  never copy them, copy the export from `toon_prop.py`.

## Axes and scale

Export with the `unity-export` skill's settings. An imported mesh keeps Blender X and negates Z: measure a direction on
the vertices before rotating one in code. One metre is one metre; never fix scale on the Unity side.

## The look: `__GAME__/Toon`

Every lit material is `__GAME__/Toon` (`Game/Art/Shaders/Toon.shader`), never URP/Lit: two bands of light and shade
with a saturated tinted shade, shadows cut to the same edge, a glossy spot and rim driven by Smoothness, contact shading
near `_GroundY`, and an ink outline tinted from the surface colour. Same property names as URP/Lit, so a builder swaps
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
  same two bands (Forward and Forward+), light layers, fog, and ambient from light probes. It does not sample baked
  lightmaps or shadowmask: light toon objects in real time and give them baked light through probes.
- Keep the URP renderer's **Depth Priming Mode on Disabled** (the default). Depth priming draws the opaque list with
  ZTest Equal, and the outline hull, which is not in the depth prepass, disappears.
- After changing `Toon.shader`, run `__GAME__/Art/Check Toon Shader` (ProjectSetup runs it too): it compiles every
  pass for the main keyword sets and logs `[toon-art] Toon shader OK` or each error. A shader error otherwise shows
  only as a pink object in Play Mode.
- Tune the look on a reference scene from the game camera, on both quality tiers, before changing every material.

## Rules

- Never edit an FBX, a generated material, a generated prefab or a controller by hand; change the script or the builder.
- A colour or palette rule lives in the Blender script's check, so a rebuild that breaks it fails.
- Keep `.blend` files out of `Assets/`; a `.blend` there makes Unity import it through a Blender install.
