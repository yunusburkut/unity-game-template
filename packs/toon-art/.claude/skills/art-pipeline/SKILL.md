---
name: art-pipeline
description: Making and rebuilding __GAME__'s generated 3D art — Blender build scripts in Tools/Blender that export FBX plus a JSON manifest, the AssetPostprocessor that pins their import, the Editor builder that turns them into materials and prefabs, the __GAME__/Toon shader and its outline. Use when adding or changing a model, prop, kit piece, clip or material, after rebuilding art, or before judging or changing the look. Modelling inside Blender itself is the global blender-skills (start with blender-director).
---

# Art pipeline

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

`examples/` in the template's `packs/toon-art` holds a real script (`city_assets.py`, Pixel Volley), a manifest-writing
kit module (`kit_common.py`, Mixtrol) and a postprocessor (`LevelKitModelPostprocessor.cs.txt`) to copy the shape from.

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
- Tune the look on a reference scene from the game camera, on both quality tiers, before changing every material.

## Rules

- Never edit an FBX, a generated material, a generated prefab or a controller by hand; change the script or the builder.
- A colour or palette rule lives in the Blender script's check, so a rebuild that breaks it fails.
- Keep `.blend` files out of `Assets/`; a `.blend` there makes Unity import it through a Blender install.
