# Claude Code + Blender Character Reference Guide

**Scope:** this is one character's brief (Mixtrol's small antenna character), kept as a worked example of what a
brief for `blender-image-to-3d` holds. The process lives in that skill (gated phases, renders matched to the
reference camera, validation); the export lives in `unity-export`, the one Blender-to-Unity contract. Where this
brief and those skills differ, the skills win.

## Goal
Recreate the supplied character in Blender as quickly and reliably as possible for Unity use.

The reference board should be treated as the visual source of truth. Do not redesign the character.

## Modeling Priority
1. Silhouette
2. Body proportions
3. Eye size and placement
4. Arm/hand proportions
5. Feet
6. Antenna
7. Facial details
8. Topology polish

## Reference Board Usage
Use orthographic views:
- Front
- Right side
- Back
- Left side
- 3/4 view only for visual validation

All views should:
- Use the same character scale
- Use the same vertical center
- Keep the feet on the same ground line
- Use a neutral T-pose
- Use a neutral closed-mouth expression
- Use plain white materials for the body so gameplay color can be assigned in Unity

## Blender Setup
- Units: Metric
- Character height: 1.0 m excluding antenna
- Apply Scale = 1,1,1 before rigging/export
- Keep origin at ground center between the feet
- Use symmetry wherever possible
- Use Mirror Modifier during modeling
- Use Subdivision Surface only where needed
- Avoid unnecessary sculpt density
- Final mesh target: ~5k–12k triangles
- Prefer clean quad topology around deforming areas
- Keep eyes, pupils, brows, and antenna as separate objects when it improves control

## Fast Modeling Order

### 1. Body
Start with a low-resolution UV sphere.
Match front and side silhouettes first.
Do not add detail until both views match.

### 2. Arms
Model one arm and mirror it.
Keep arms simple, rounded, and slightly tapered.

### 3. Hands
Use simple rounded cartoon fingers.
Do not model realistic human anatomy.

### 4. Legs and Feet
Keep legs extremely short.
Feet should be rounded, simple, and stable on the ground plane.

### 5. Eyes
Use separate geometry.
Match eye size/spacing before adding pupils.

### 6. Face
Keep mouth closed in the base model.
Create facial expressions later using shape keys if needed.

### 7. Antenna
Keep antenna separate and centered.
Use minimal geometry.

## Materials
Base character/body material:
- Pure white or neutral near-white
- No baked color
- No texture dependency

Gameplay color should be assigned in Unity through material/property changes.

Recommended Blender preview:
- Base Color: #FFFFFF
- Metallic: 0
- Roughness: 0.35–0.5

Eyes/pupils/brows may remain separate materials.

## Rig
Use a Generic rig, not Humanoid.

Suggested hierarchy:
- Root
  - Body
    - Arm_L
      - Forearm_L
        - Hand_L
    - Arm_R
      - Forearm_R
        - Hand_R
    - Leg_L
      - Foot_L
    - Leg_R
      - Foot_R
    - Antenna
    - Eye_L
    - Eye_R

Keep bone count low.

## Animation
Required:
- Idle
- Run_Loop
- Jump

Use 30 FPS.
Bake secondary motion into animations.
Avoid runtime physics for antenna/limb follow-through unless specifically required.

## Unity Export
Export with the `unity-export` preset, rigged variant (`bpy.ops.export_scene.fbx` with `axis_forward='-Z'`,
`axis_up='Y'`, `apply_scale_options='FBX_SCALE_ALL'`, `add_leaf_bones=False`, `use_armature_deform_only=True`,
`bake_anim=True`, `bake_anim_use_all_actions=True`; the importer side uses `bakeAxisConversion`). Blender's FBX
defaults add leaf bones and leave a -90 X root in Unity. The FBX must carry:
- Mesh
- Armature
- Skin weights
- Blend shapes
- Actions/animations

Unity:
- Rig Type: Generic
- Run_Loop: Loop Time ON
- Idle: Loop Time ON
- Jump: Loop Time OFF

## Claude Code Execution Rules
Do not build everything in one pass. The order below is this character's path through the gated phases of
`blender-image-to-3d`; run those phases, with their evidence renders, and use this list for what each one covers here.

Use this order:
1. Analyze reference
2. Create body blockout
3. Render front/side comparison
4. Correct proportions
5. Add limbs
6. Add face
7. Add antenna
8. Finalize topology
9. Rig
10. Animate
11. Export FBX

At each major modeling milestone:
- Render from orthographic front and side cameras
- Compare against the reference
- Fix the three largest silhouette/proportion errors
- Only then continue

Do not spend time on topology polish while major proportion errors remain.

## Definition of Done
- Front silhouette closely matches
- Side silhouette closely matches
- Feet align with ground line
- Eyes match size and spacing
- Arm and hand proportions match
- Antenna placement matches
- Body is white and recolorable in Unity
- Neutral T-pose is clean
- Rig deforms without visible collapsing
- Run and jump export correctly to Unity
