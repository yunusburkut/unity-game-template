# UI style bible: a named game's UI as numbers, then every screen gated against them

Claude-made UI looks generic ("AI slop") when nothing pins the look before the first screen: a default font, a new
corner radius per button, a gradient here, a glass panel there, text sizes picked per view. The UI style bible fixes
the numbers once per game in `Tools/UI/Style/`, and every screen, HUD, popup and icon is then measured against them.
It runs before the first screen of a game whose DESIGN.md Look names reference games, or when the user asks for a UI
"like game X". It is the UI twin of genre-defaults' `references/style-bible.md` (3D assets), with the same loop:
measure, write the numbers, gate, sheet, two scored reviews.

Neighbours, not repeats: layout and wiring are `ui-ugui`; scaling, safe area, orientation and touch sizes are
`platform-targets`; the words, the contrast and text-size floors (CL32, CL33) and the template tells (§F) are this
skill's `clarity-rules.md`. The bible may raise a floor, never lower one.

Not a copy: a named game gives palette, value contrast, type scale, shape language (radius, border), icon style and
density. Its logo, layouts, icons, fonts and signature screens are never rebuilt, and its screenshots stay reference
only: in `Tools/UI/Style/reference/`, never under `Assets/`, never shipped.

The script runs headless with Blender's own numpy and OpenImageIO (no system Python here) and imports genre-defaults'
`extract_style.py` for the colour maths. It sits in the `scripts` folder beside this file's `references` folder:
`S=<skill>/scripts`, with `<skill>` taken from the absolute path this file was read at (the player-clarity skill's
base directory).

| Call | Input | Output |
|---|---|---|
| `ui_style.py -- extract` | `ui_refs.json` (reference layouts) | `ui_metrics.json`, a swatch strip |
| `ui_style.py -- gate` | a screen's layout, `ui-style.json` | `UI GATE PASS`, or exit 1 with each failure's rule, place and fix |
| `ui_style.py -- sheet` | the layout, `ui-style.json`, `ui_refs.json` | review sheet PNG and its `.json` |

Every call is `blender --background --factory-startup --python-exit-code 1 --python "$S/ui_style.py" -- <call>
<args>`; the script's header lists the arguments. Without `--python-exit-code 1` a crash exits 0 and reads as a pass.
`<skill>/evals/test_ui_style_bible.py` is its fixture test (template `test-all.ps1`).

## Layouts

A layout is one screen as a json beside its image; `ui_refs.json` is a list of them:

```json
{"image": "menu_r1.png", "elements": [
  {"id": "card", "kind": "panel", "rect": [560, 160, 800, 760]},
  {"id": "title", "kind": "text", "rect": [616, 216, 560, 80], "px": 64, "bold": true},
  {"id": "play", "kind": "button", "rect": [616, 720, 320, 136], "hit": [600, 704, 352, 168]},
  {"id": "settings", "kind": "icon", "rect": [1208, 216, 96, 96]},
  {"id": "world", "kind": "art", "rect": [0, 0, 1920, 1080]}]}
```

- Rects are image pixels from the top left, `[x, y, w, h]`; `image` is relative to the json's folder.
- `text`: the box round its ink (`TMP_Text.textBounds`; one line's box when `px` is left out). The script reads it 2 px larger and takes that rim as the background, so a
  busy picture behind the text counts. `px` is the font size at the reference (TMP `fontSize`); without it the
  script estimates it from the cap height, the top of the ink to the baseline (about 0.72 em, descenders left out,
  within about 10 % on a line with a capital or a tall letter).
- `button` and `panel` (a plate, a card, the background): drawn within 8 reference px of their edges; the script snaps
  them to the real edge, never more than half the way to a neighbouring button or panel, or to the edge of the panel round it. `hit` is a raycast area
  larger than the drawn button; two buttons' hit areas must not overlap, and `touch_gap_px` is measured between the
  drawn buttons.
- `icon`: its Image rect; its contrast is read against a 2 px ring outside it, so an icon on its own plate counts.
  `art`: the game view behind a HUD or an illustration; never measured.
- `safe_area`: `Screen.safeArea` in image pixels, only for a capture from a device or the Device Simulator; without
  it `ui-style.json` `safe_inset` applies, except to elements marked `"safe": true` (under a `SafeAreaFitter`,
  which moves them in on the phone).

Every number is read at the 1080 CanvasScaler reference (`platform-targets`): an image is scaled by 1080 / its short
side, so a capture taken at the reference aspect (16:9 or 9:16) matches the Canvas's own units.

## 1. Make the bible (once per game, about 1 h)

1. Ask the user for 1-3 games and what to take from each (colour, shape language, type scale, density); the
   orientation and platforms come from `CLAUDE.md` and DESIGN.md. A seen choice between readings goes on a decision
   page (`<skill>/../pipeline/references/decision-page.md`).
2. The user drops 5-10 of their own screenshots per game into `Tools/UI/Style/reference/<Game>/`: the main menu, a
   popup, the HUD in play, a list or shop; at the device's own resolution, the game's orientation where they can.
3. Look at each shot (Read) and write `Tools/UI/Style/ui_refs.json`: one layout per shot, 5-15 elements each (every
   button, one or two lines of each text size, the icons, the panels, `art` for the game view). Leave `px` out; the
   script estimates it from the cap height, so pick lines with a capital or a tall letter (b d f h k l t); a line of
   only x-height letters ("menu", "anı") reads about 30 % small.
4. Run `extract --layouts Tools/UI/Style/ui_refs.json --out Tools/UI/Style/ui_metrics.json --swatches
   Tools/UI/Style/palette.png`. It prints each swatch's number, kind and hex (`SWATCH 3 palette #fab833`) and pools the
   type scale, button sizes, radius, border, grid fit, icon fill, density and edge margins.
5. Write `ui-style.json` (below) and `UI_STYLE.md` from the metrics, the shots and the user's words:
   - `palette`: the swatches the user confirms by eye, renamed by use (Background, Panel, Text, TextMuted, Primary,
     Danger); `accents`: the metrics' accents the user keeps. `palette_de` 6; `off_palette_max_share` 0.03.
     `accent_max_share` about the references' share of accent in a screen (a gold Buy button on a dark shop: 0.05).
   - `contrast`: WCAG's 4.5 / 3 / 3 (CL32); raise it when the references read stronger, never lower.
   - `text_px`: 3-5 steps named by use (title, heading, body, label) from the metrics' `text_tiers`, rounded to
     whole px. `text_min_px` 18 (CL33), higher for a phone-first game whose references are larger.
   - `touch_min_px` 130 (48 dp at the 1080 reference, `platform-targets`) on touch; a mouse-only PC or WebGL game
     takes `ui-ugui`'s mouse target (64 with a 960x540 WebGL canvas, 32 when 1920x1080 is the smallest window);
     `touch_gap_px` 24 (about 8 dp) on touch, 8 for mouse only.
   - `grid_px`: 8 when the metrics' `on_grid` reads 0.7 or more for 8, else 4.
   - `radius_px` and `stroke_px`: per kind (`{"button": 24, "panel": 32}`) from the metrics, rounded to whole px;
     `null` leaves a kind unchecked.
   - `icon`: `fill` `solid` when the metrics' `icon_fill_share` is 0.4 or more, else `line` with `stroke_px` from
     `icon_line_px`. Icons come from the game's own art (player-clarity hard rules).
   - `density`: `max_elements` the references' `elements.max`; `min_empty_share` their `empty_share` less 0.1.
   - `safe_inset` `[top, right, bottom, left]`: a notched phone's insets at the reference, `[108, 0, 80, 0]` portrait
     and `[0, 108, 64, 108]` landscape, unless the game ships PC only (`[0, 0, 0, 0]`).
   - `font`: the typeface and weights; the gate cannot see a font, so UI_STYLE.md and the reviewers hold it, and it
     covers ç ğ ı İ ö ş ü (CL31).
   - `signature`: 1-3 motifs from the game's own world that carry the chrome: the shape or material of a carrier in
     DESIGN.md Look's `Carriers` (its characters, world, signature objects) turned into a frame cut, a plate's
     material, an icon motif or a divider; never from a reference game. `Carriers` missing or TODO: ask the user once
     and write it there first (player-clarity's opening rule); never invent the motif. The numbers alone make a screen
     tidy, not this game's: the reviewers' swap test (hide the title and the logo; could it be another game's, a UI
     kit's or Unity's default?) fails a screen that shows none.
   - `avoid`: every template tell in clarity-rules §F that a screen can show (among them the centred modal with a
     title, a body and an OK button, gradients and glass, glow on everything touchable, stock icons or emoji, bouncy
     easing, the engine's default font), then what the user names.

   The game's UI theme (the one place for font, sizes and colours, player-clarity "Building it") takes its values
   from `ui-style.json`; a change edits both the same day, or the gate measures a look the game does not draw.
   Show the swatches and two readings of one screen (the main menu) on a decision page, as inline SVG mock-ups drawn
   to the numbers: the two readings the user was unsure about in step 1 (two palettes, sharp or round, dense or airy;
   with none, the two closest reference games), both carrying the `signature`. The user approves one.
6. Build the golden screen: the main menu through section 2. After the user's yes, copy its last capture to
   `Tools/UI/Style/golden.png`. Keep three calibration anchors in `Tools/UI/Style/anchors/`, each with its score and
   one line why in `anchors/notes.md`: the golden sheet as `pass.png`; one rejected sheet (an early round's `_r1`) as
   `fail.png`; and the same screen in Unity's default UI skin (Unity's default sprites and font, no `signature`) as
   `fail_generic.png`, noted "Signature 4: swap test fails, no motif".

Review sheets are working files: add `/Tools/UI/**/review/` to the game's `.gitignore` when it is missing.

## 2. Every screen

1. Brief: the screen, its states (loading, empty and error for a screen that lists data; the HUD's per CL25), the
   platform, the reference shot it answers to.
2. Build it in uGUI (`ui-ugui`) with colours, sizes, radius and border from the theme, never typed again.
3. Capture: set the Game view to the reference resolution (1920x1080 or 1080x1920), then `gk-bridge play-capture`
   (`unity-editor-cli`). It shows what Play Mode shows at start: a screen behind a button needs a capture scene that
   opens it on Start, kept out of the build list. Copy the last shot (`Logs/agent/capture/shot-3.png`) to
   `Tools/UI/<Screen>/review/<Screen>_r<N>.png`, `<N>` the review round from 1. A PNG mock-up from elsewhere goes the
   same way.
4. Write `<Screen>_r<N>.layout.json` beside it. Rects: a `unity command script run` method (`unity-editor-cli`)
   calls `Canvas.ForceUpdateCanvases()`, then for each element takes `GetWorldCorners` into the root canvas's local
   space (`root.InverseTransformPoint`) and maps the root rect onto the image: x = (local x − root xMin) × image
   width / root width, y = (root yMax − local top) × the same factor. That holds for anchors, pivots, nesting and
   both canvas modes; reading rects off the capture is the fallback. Per kind:
   - text: the ink, not the RectTransform (a button's label is often stretched over the whole button): after
     `text.ForceMeshUpdate()`, the corners of `TMP_Text.textBounds` through `text.transform.TransformPoint`, then the
     same mapping. `px` is its `fontSize`. An empty text gets no entry (a text rect with no ink stops the script).
   - button: `rect` is the Button's `targetGraphic`; `hit` is a larger `raycastTarget` child Image, when it has one.
   - every element under a `GameKit.SafeAreaFitter` (`GetComponentInParent<SafeAreaFitter>() != null`) gets
     `"safe": true`.

   Every button, text, icon and panel gets an entry: what the layout leaves out, the gate never checks. Leave
   `safe_area` out: an Editor capture has no notch, so `safe_inset` stands in for the phone, checked only on the
   elements outside the fitter (inside it, the fitter moves them in on the phone).
5. `gate --style Tools/UI/Style/ui-style.json --layout <that json>`. Exit 1: fix the cause and capture again; never
   loosen `ui-style.json` to pass one screen.

   | Rule | Fix |
   |---|---|
   | `contrast` | the ink the message names, or a plate or outline behind the text (CL32) |
   | `text_px` | the type-scale step it names |
   | `touch` | a bigger button, or a larger transparent raycast Image as its hit area; space buttons `touch_gap_px` apart; overlapping hit areas meet halfway |
   | `grid` | sizes, spacing and padding (LayoutGroup) in multiples of `grid_px` |
   | `radius`, `stroke` | the theme's 9-sliced sprite for that kind |
   | `icon` | redraw it in the style's kind and line width |
   | `safe_area` | move it under the `SafeAreaFitter` child (`platform-targets`); never add a margin for the notch by hand |
   | `density` | cut or group (CL24), or move it to a second screen |
   | `palette`, `accent` | the theme role the message names; a new colour only with the user's yes |

6. `sheet --style ... --layout <that json> --refs Tools/UI/Style/ui_refs.json --golden Tools/UI/Style/golden.png
   --out Tools/UI/<Screen>/review/<Screen>_sheet_r<N>.png`. Row 1 at phone size (the short side 256 px: a 6.1-inch
   phone at its real size on a 100-dpi monitor, so look at it at 100 %): the screen, the gate drawn on it (red: a
   failing element, green: the rest, blue: the safe area), the references, the golden screen. Row 2 at the
   reference's real pixels: the smallest text, the smallest button and the lowest-contrast element, then each
   reference's smallest text. The `.json` names every tile and holds the gate result and the measured numbers beside
   the style's.
7. Review: two `gamekit:ui-reviewer` agents in parallel, each fresh, one with `lens: readability` and one with `lens:
   style`, each given the sheet, its `.json`, `UI_STYLE.md`, `ui-style.json`, `Tools/UI/Style/anchors/` and the
   brief, never the build code; the golden screen's own rounds have no anchors or golden yet, so the references and
   UI_STYLE.md set the scale. Each fix round repeats steps 3-6 as `_r<N+1>`, and from round 2 the reviewers also get
   the previous round's sheet (A/B). Done when both score at least 9/10 with no blocker; at most 3 rounds, then show
   the user the sheet and the open findings.
8. The user sees the final sheet: `SendUserFile` (`display: render`), so it opens beside the chat and reaches the
   phone; without that tool, give its path as a link. The last word on a phone is the Device Simulator or a device
   (`platform-targets`).

Every 5 approved screens: one `sheet` with the approved screens' layouts as `--refs` and one `lens: style` pass that
looks for drift (a radius, a text size or a colour that differs between screens).

## ui-style.json

```json
{
  "game": "__GAME__",
  "references": [{"game": "<name>", "take": "palette, round chunky buttons"}],
  "font": "<title font> Bold for titles and buttons, <body font> Regular for body",
  "palette": {"Background": [0.12, 0.15, 0.23], "Panel": [0.22, 0.27, 0.38], "Text": [0.96, 0.93, 0.86],
              "TextMuted": [0.72, 0.74, 0.80], "Primary": [0.98, 0.72, 0.20], "Ink": [0.10, 0.08, 0.06]},
  "accents": [[0.90, 0.22, 0.22]],
  "palette_de": 6,
  "off_palette_max_share": 0.03,
  "accent_max_share": 0.05,
  "contrast": {"text": 4.5, "large_text": 3.0, "ui": 3.0},
  "text_px": {"title": 64, "heading": 48, "body": 32, "label": 24},
  "text_min_px": 18,
  "touch_min_px": 130,
  "touch_gap_px": 24,
  "grid_px": 8,
  "radius_px": {"button": 24, "panel": 32},
  "stroke_px": {"button": 4, "panel": 0},
  "icon": {"fill": "solid", "stroke_px": null},
  "density": {"max_elements": 12, "min_empty_share": 0.5},
  "safe_inset": [0, 108, 64, 108],
  "signature": ["<motif from DESIGN.md Carriers>: where it goes (panel frames, the primary button, dividers)"],
  "avoid": ["gradients and glass", "glow on everything touchable", "stock icons or emoji", "bouncy easing",
            "a second corner radius"]
}
```

| Field | Meaning | Rule |
|---|---|---|
| `palette`, `accents`, `palette_de`, `off_palette_max_share`, `accent_max_share` | roles (sRGB 0-1); how far (CIELAB) a pixel may sit from one; how much of the UI (panels, buttons, icons, text ink; edges and `art` left out) may be off palette or accent | `palette`, `accent` |
| `contrast` | WCAG ratios: text, large text (24 px, or 19 px bold), icons that carry meaning | `contrast` |
| `text_px`, `text_min_px` | the type scale at the 1080 reference; the floor (CL33) | `text_px` |
| `touch_min_px`, `touch_gap_px` | a button's (or its `hit` area's) short side; the space between two buttons | `touch` |
| `grid_px` | sizes of buttons, icons and panels, and the gaps between neighbours, in multiples (1 px tolerance) | `grid` |
| `radius_px`, `stroke_px` | corner radius and border width per kind (a number: every kind; `null`: unchecked) | `radius`, `stroke` |
| `icon` | `solid` (ink covers 40 % or more of the rect) or `line`, and a line icon's width | `icon` |
| `density`, `safe_inset` | text, buttons and icons per screen and the empty share of the safe area; the safe area at the reference when a layout has none | `density`, `safe_area` |

`font`, `references`, `signature` and `avoid` are for the build and the reviewers; no script measures them (the sheet
prints `UI SHEET WARNING` when `signature` is empty). A threshold is tuned on
the golden screen, then frozen; a later change re-runs the gate on every approved screen.

## UI_STYLE.md

The words the numbers cannot hold, at most one screen: the 3-5 rules that make the look (shape language, where the
accent goes, how much air, how a button shows pressed and disabled), where each `signature` motif goes and where it
never does, the typeface and its weights, what each reference
game gives, the named mistakes, and the tie-breaker when two rules collide (for example "readability on the smallest
phone beats density").

## Limits

- The gate checks what the layout lists, so a missing element passes unseen. Rects come from the step 4 method
  (text from its ink bounds, the rest from RectTransforms) or by eye; the way up is a GameKit dump of those rects, TMP
  sizes and the fitter flag inside `play-capture`.
- A border thicker than 10 reference px reaches the band `stroke` reads the fill from, so the border is taken as the
  fill and measures 0: check such a style by eye on the sheet.
- A font is not identified from pixels, and a text size without `px` is an estimate; the reviewers hold the typeface.
- Contrast is measured on the flat capture: a glow, a drop shadow or an outline counts only where it reaches the text
  box's rim. Snap takes the outermost step within 8 px (less beside a neighbour) whose inner line is one colour along
  the edge, so a drop shadow counts as the button's edge while a busy game view behind a HUD button does not. A
  button whose own edge is a gradient or texture along its length finds no edge and keeps its drawn rect: give it an
  exact rect.
- A capture at another aspect than the reference scales by its short side, while a CanvasScaler at Match 0.5 does
  not; capture at the reference resolution, and judge other aspects in the Device Simulator.
