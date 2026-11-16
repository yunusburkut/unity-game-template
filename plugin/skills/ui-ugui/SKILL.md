---
name: ui-ugui
description: Building or changing a uGUI menu, screen, popup or HUD layout ("menü", "ekran", "popup", "buton", "arayüz") - Canvas, RectTransform, layout groups, ScrollRect lists. Safe area, scaling and input are platform-targets; the words are player-clarity.
---

Understand existing Unity uGUI, make targeted edits, and generate new Canvas-based hierarchies.

<!-- BEGIN HOUSE -->
**House rules win.** This is a vendored copy of Unity's skill; where it disagrees with the game's CLAUDE.md,
`unity-architecture` or `unity-code-review`, the house rules apply:
- Inspector-wired references are guaranteed: no null checks and no "verify referenced objects exist" for them. Only
  untrusted input is guarded.
- Scripts go in the game's `<Game>.Game` asmdef (`Assets/<Game>/Game`), not next to prefabs.
- A direct reference, or a UnityEvent wired in the Inspector, over a C# event, unless two or more real listeners exist.
- Every house edit in this copy, here and in `references/`, sits between `BEGIN HOUSE` / `END HOUSE` comments; an
  upstream refresh keeps them (`unity-editor-cli`).
<!-- END HOUSE -->

When working with ScrollRect/ScrollView, read the reference file:
- [references/scrollview-setup.md](references/scrollview-setup.md) — Required hierarchy, setup rules, and common failures

## Scope

Determine what the user is asking for:

| Request Type | Action |
|--------------|--------|
| Question about UI | **Understand** — analyze hierarchy, explain structure |
| Change specific element | **Edit** — targeted modification only |
| Create new UI | **Generate** — create new hierarchy |
| Fix/improve existing UI | **Edit** — modify existing, don't rebuild |

**Generate only what is requested:**

| Request | Output |
|---------|--------|
| UI layout | Prefab or scene hierarchy only |
| "with code" / "with logic" / "functional" | Hierarchy + scripts |

**These do NOT imply scripts:**
- "proper buttons" → well-configured Button components
- "working UI" → valid hierarchy that renders
- "menu screen" → visual layout only

## Critical Rules

**Namespace disambiguation:**
- Always use fully qualified type names when creating or referencing UI components
- `UnityEngine.UI.Image`, not `Image`
- `UnityEngine.UI.Button`, not `Button`
- Other namespaces in the project can cause ambiguous type errors

**Verify before modifying:**
- Always check what exists before making changes
- Confirm parent objects exist before adding children
- Verify components are present before modifying properties
- Never assume hierarchy state — query it first

**Incremental fixes over rebuilds:**
- When fixing issues, make targeted corrections
- Never destroy and recreate entire hierarchies to fix problems — destroyed objects cause null reference cascades
- Prefer identifying the specific broken property and fixing only that over rewriting large sections
- **When a fix fails, revert the change** before trying an alternative approach

**One change at a time:**
- Make a single change, then verify the result
- Do not batch multiple unrelated modifications
- Be careful not to inadvertently modify or remove adjacent elements when editing a specific one
- If something fails, understand why before trying alternatives
- Avoid "shotgun debugging" with multiple simultaneous changes

**Color and visibility:**
<!-- BEGIN HOUSE -->
- **Ensure text is readable by default:** When choosing colors, ensure text contrasts with its background (at least 4.5:1, `player-clarity` CL32) — but respect intentional low-contrast uses (disabled states, placeholder text, decorative elements)
<!-- END HOUSE -->
- **Check visibility for new elements:** After creating UI elements, verify they have non-zero size and are within parent bounds. Elements intentionally created hidden (for later toggling, animation, etc.) are fine

**Specification adherence:**
- **Honor user specifications exactly:** When the user provides pixel dimensions, hex colors, positions, spacing, or other exact values, apply them precisely — do not approximate or substitute
- **Minimize unrelated changes:** When editing, avoid changing properties the user didn't ask about unless a related adjustment is necessary for the fix to work

## Conventions

**Follow project patterns first.** Search existing files before applying defaults.

<!-- BEGIN HOUSE -->
| Type | Convention | Good | Bad |
|------|------------|------|-----|
| GameObject names | PascalCase | `SubmitButton` | `submit-button` |
| Prefab paths | Feature folders inside the game folder | `Assets/<Game>/UI/Inventory/` | `Assets/Prefabs/UI/`, `Assets/UI/` |
<!-- END HOUSE -->

## Workflow

1. **Verify state** — Check what exists in the scene/hierarchy before any action.
2. **Analyze** — Determine exactly what's needed. No extras.
3. **Search** — Find existing prefabs, canvases, assets. Don't assume paths.
4. **Follow project patterns** — Match folder structure and naming.
5. **Create or edit** — Build structure with proper anchoring, or make targeted edits.
6. **Confirm result** — Verify the change worked before moving on.

## Canvas Setup

Every UI needs a Canvas:

```
Canvas (Screen Space - Overlay or Camera)
├── CanvasScaler (Scale With Screen Size recommended)
├── GraphicRaycaster
└── [UI Content]
```

**CanvasScaler settings:**
- Default to UI Scale Mode "Scale With Screen Size" unless the project has a specific reason for "Constant Pixel Size" (e.g., pixel-art, fixed-resolution targets)
<!-- BEGIN HOUSE -->
- Reference Resolution: in the game's main orientation from CLAUDE.md (1080x1920 portrait, 1920x1080 landscape); match an existing Canvas in the project first. Orientation still TODO and no Canvas yet: 1920x1080 (the default landscape window, `platform-targets`), and tell the user the orientation is open, since locking portrait later means 1080x1920
- Screen Space - Camera: assign the camera that renders the UI (`Canvas.worldCamera`); the reference resolution still comes from the Canvas Scaler, not the camera
- Match Width Or Height: 0.5 (balanced)
- Interactive content goes under a full-stretch child with `SafeAreaFitter` (GameKit); backgrounds stay outside it, full-bleed. Letterboxing, orientation and touch sizes: `platform-targets`
<!-- END HOUSE -->
- If an existing Canvas uses "Constant Pixel Size", flag it and ask the user before changing
- Prefer anchors and Layout Groups over absolute pixel positions for layout

## Layout Components

**Layout Groups control child sizing:**
- When a parent has a Layout Group, it manages child RectTransforms
- Children's anchors and sizeDelta may be overridden by the parent
- Understand whether the parent or child controls size before setting values

**Vertical/Horizontal Layout Groups:**
- Control Child Size: determines if parent sets child dimensions
- Child Force Expand: determines if children stretch to fill space
- If Control Child Size is off, children must have explicit sizes

**Avoiding layout conflicts:**
- Do not manually set child anchors/size when parent controls them
- Do not add Layout Group to an element that should have fixed size
- Nested Layout Groups require careful configuration of each level
- When layout is wrong, check parent settings before modifying child
<!-- BEGIN HOUSE -->
- ContentSizeFitter and a Layout Group on the **same** object is the normal pattern: Control Child Size sizes the children, the fitter sizes the object itself from the group's preferred size
- ContentSizeFitter on a child of a Layout Group = the parent drives that child, so the fitter is overridden (wasted) and Unity warns about it
- To size such a child to its content, remove its fitter and enable Control Child Size on the parent for that axis; the child's preferred size comes from its own Layout Group, a `LayoutElement` or its TMP text
<!-- END HOUSE -->
- Common pattern: ScrollView Content should have ContentSizeFitter + VerticalLayoutGroup where VLG controls children but ContentSizeFitter sizes the Content itself

**Grid Layout Group:**
- For inventory grids, card layouts
- Cell Size must be set explicitly — children are sized to match
- Constraint controls row/column limits

**Content Size Fitter:**
- Horizontal/Vertical Fit: Preferred Size
- Use on containers that should size to their content
- Requires a layout element or text component to provide preferred size

## RectTransform Anchoring

**Elements must have non-zero size to be visible:**
- Set explicit width/height via sizeDelta, or
- Use stretch anchors with proper offsets, or
- Let a parent Layout Group control size (with Control Child Size enabled)

**Anchor configuration order:**
1. Set anchor preset first (corner, edge, or stretch)
2. Then set position/offset values
3. Verify the resulting size is non-zero

**Common patterns:**
- **Stretch anchors** — for responsive elements that fill available space
- **Corner anchors** — for fixed-position, fixed-size elements
- **Edge anchors** — for elements that stretch in one direction only

**Positioning from natural language descriptions:**
When the user describes a position (e.g., "top right", "bottom bar", "left side"):
1. Determine if it's a **corner** (fixed point), an **edge** (stretch along one axis), or **fill** (stretch both axes)
2. Set anchor min and anchor max — for corners these are the same point; for edges/fill they span a range
3. **Set pivot to match the anchor point** — pivot must align with where the element is anchored, not left at the default (0.5, 0.5). A "top right" element needs pivot at the top-right corner; a "top bar" needs pivot at the top edge center
4. Set position/offset values **after** anchors and pivot are configured

**Visibility checklist:**
- Width and height are both greater than zero
- Element is within parent bounds
- Element is not obscured by siblings (check hierarchy order)
- Image component has a sprite or color with alpha > 0

## Common Components

| Component | Use Case |
|-----------|----------|
| `Image` | Backgrounds, icons |
| `RawImage` | Render textures, videos |
| `Text (TMP)` | All text (use TextMeshPro) |
| `Button` | Clickable elements |
| `Toggle` | Checkboxes, radio buttons |
| `Slider` | Value ranges |
| `ScrollRect` | Scrollable content |
| `InputField (TMP)` | Text input |

## Best Practices

- Use TextMeshPro for all text (not legacy Text)
- WorldSpace UI that have text should also use Text Mesh Pro, be sure to review the project and import the TMP essentials if they are not present in the project
<!-- BEGIN HOUSE -->
- Import the TMP Essentials only through the non-interactive `ImportResources` call below; it opens no TMP Importer or Import Unity Package window, so there is nothing to close (an interactive import opened by the user still needs both closed before the Editor accepts commands)
<!-- END HOUSE -->
- Organize hierarchy logically (Header, Content, Footer)
- Use Layout Groups instead of manual positioning where possible
- Set Raycast Target = false on non-interactive images
- Use sprite atlases for performance
<!-- BEGIN HOUSE -->
- Split canvases by change rate: a changing element dirties and rebuilds its whole Canvas, so the HUD (timers, score) sits on its own Canvas or a nested sub-Canvas, apart from static frames and labels
- Hide or fade a group with a `CanvasGroup` (alpha, interactable, blocksRaycasts), not per-element alpha and not SetActive every frame. A screen hidden for a long time: disable its Canvas component (layout kept, no drawing)
- Set `Canvas.sortingOrder` explicitly per layer (HUD, Menus, Popups) instead of relying on hierarchy order
- Long lists and grids in a ScrollRect pool their items, never Instantiate/Destroy per scroll
- UI never owns or changes game state: it reads the controller's state and calls the controller (direct reference or Inspector-wired UnityEvent); the rules live in Core
- UI CPU stays within about 1–2 ms of the frame on the target phone; read the Profiler's UI module before restructuring
<!-- END HOUSE -->

**Never use** `EditorApplication.ExecuteMenuItem("Window/TextMeshPro/Import TMP Essential Resources")`, unless the user asks for an interactive TMP Essentials installation. It opens a modal dialog that blocks whatever invoked it until a human dismisses it.

<!-- BEGIN HOUSE -->
**Do not use** `AssetDatabase.ImportPackage()` for TMP resources, instead `TMPro.TMP_PackageResourceImporter.ImportResources(importEssentials: true, importExamples: false, interactive: false)` is the canonical non-interactive API (Editor only; run it once through `script run` when `Assets/TextMesh Pro` is missing, then let the import finish before creating TMP text).
<!-- END HOUSE -->

## Interaction Readiness

Before completing any UI that contains interactive elements, verify:

<!-- BEGIN HOUSE -->
1. **EventSystem** must exist in the scene (exactly one), with `InputSystemUIInputModule`, not `StandaloneInputModule` (the old Input Manager is off)
<!-- END HOUSE -->
2. **GraphicRaycaster** must be on the Canvas
3. **Raycast Target = true** on interactive elements (and false on non-interactive ones to avoid blocking)
4. **Button.onClick should be wired** (via inspector or script) — only when scripts or logic were requested

If the first three are missing, interactive elements will exist visually but fail silently.

<!-- BEGIN HOUSE -->
## Screens

A screen that loads or lists data defines its loading, empty and error states before it is built; every screen defines
what Back does. Empty = one image from the game's art, one line, one action.

**Navigation:**
- Esc, the Android back button and the close button do the same thing (`platform-targets`). With one menu, Back
  closes it; a screen stack (Push, Pop) waits for nested screens. At the root, Back asks to quit on PC and Android;
  iOS and WebGL have no quit.
- Selection on open (this skill owns it, with or without a gamepad, since PC can be driven keyboard-only): opening a
  screen selects its one primary button (`EventSystem.current.SetSelectedGameObject`) when the last input was
  keyboard or gamepad, so the keyboard works at once; after touch or mouse input leave nothing selected (a touch build
  would show a stuck Selected tint). So leave the `EventSystem`'s First Selected empty, since it selects
  unconditionally. Track the last input in one place: `InputSystem.onActionChange`, on
  `InputActionChange.ActionPerformed`, sets `lastWasPointer = ((InputAction)obj).activeControl?.device is Pointer`
  (`Pointer` covers mouse, touch and pen; keyboard and gamepad are not). When a navigate or submit input arrives while
  nothing is selected, select the screen's primary button (the re-selection after a switch back from the pointer).
  Gamepad bindings and glyphs: `platform-targets`.
- Closing a sub-screen or a modal returns the selection to the button that opened it.
- A modal blocks input behind it with a full-screen raycast blocker image. The only modal confirms a destructive
  action: focus on Cancel, never used as a hint (`player-clarity` §F).

**Behaviour:**
- Buttons act on release (`Button.onClick` already does), never on press.
- A confirm button names its action ("Delete save", "Quit"), never "OK" or "Yes".
- No loading indicator for a load under 2 s; above that, show one. Never a blank black screen.
- Error text never blames the player and never says "invalid": it says what to do.
- Labels leave room for 40 % longer text (`player-clarity` CL28).
- Mouse targets at least 32 screen px at the smallest supported window, so 32 / (that window's CanvasScaler scale)
  reference px: 64 px at the 1080 reference when a 960x540 WebGL canvas is supported, 32 px when 1920x1080 is the
  smallest; touch targets per `platform-targets`. A swipe never starts in a system gesture edge.
<!-- END HOUSE -->

## Understanding

When the user asks questions about existing UI:

**Read the hierarchy first.** Don't assume — always inspect the scene or prefab before answering.

**Analyze structure:**
- Identify the Canvas and its render mode
- Map the parent-child relationships
- Identify which Layout Groups control which children
- Check RectTransform anchor configurations

**Answer questions about:**
- "What does this button do?" → Explain component, hierarchy position, event wiring
- "How is this laid out?" → Describe Layout Groups, anchoring, hierarchy
- "Why is this invisible?" → Check size, anchors, parent bounds, component state
- "What controls this element's size?" → Trace Layout Group settings or anchors

## Editing

For targeted changes to existing UI:

**Read before editing.** Always inspect the current state first.

**Edit workflow:**
1. Verify the target object exists
2. Identify the specific property or component to change
3. Make the minimal change required
4. Verify the result before proceeding

**Never destroy to fix:**
- Destroying objects cascades to null references elsewhere
- Fix properties in place rather than recreating
- If an element must be removed, update all references first

## C# (Only When Requested)

- Use fully qualified UI types to avoid namespace conflicts
<!-- BEGIN HOUSE -->
- Use `[SerializeField] private` fields for Inspector references; they are guaranteed, so no null checks for them (house rules above)
- Cache components the script finds itself in Awake(), never look them up per frame
- Button callbacks: `onClick` wired in the Inspector, or one `AddListener` in Awake that calls the controller directly; a C# event only when two or more real listeners exist
- Scripts go in `Assets/<Game>/Game` (`<Game>.Game` asmdef), not next to prefabs
<!-- END HOUSE -->

**Component references:**
<!-- BEGIN HOUSE -->
- When wiring references in the Editor, confirm the target component is present on the object you assign
- A reference resolved at runtime from untrusted data (a lookup by id, a loaded save) is guarded; Inspector refs are not
<!-- END HOUSE -->

## Error Recovery

When something goes wrong:

**Stop and diagnose:**
- Identify the exact error or symptom
- Determine the root cause before attempting fixes
- Do not make speculative changes

**Fix incrementally:**
- Address one issue at a time
- Verify each fix before moving to the next
- Keep track of what was changed

**Avoid destructive patterns:**
- "Start fresh" strategies destroy working elements along with broken ones
- Rebuilding entire hierarchies creates more problems than it solves
- Prefer surgical fixes to wholesale replacements

**When stuck:**
- Re-verify the current state of the hierarchy
- Check if previous changes were actually applied
- Consider if the approach itself is wrong rather than the implementation
