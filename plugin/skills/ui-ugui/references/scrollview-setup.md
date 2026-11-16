# ScrollView Setup

ScrollRect requires a specific hierarchy to function correctly. Missing or misordered components cause jitter, duplication, or non-scrollable content.

**Required hierarchy:**
<!-- BEGIN HOUSE -->
```
ScrollView (ScrollRect)
├── Viewport (RectTransform + RectMask2D)
│   └── Content (RectTransform + VerticalLayoutGroup + ContentSizeFitter; a pooled long list: RectTransform only)
│       └── [Children — static or added at runtime]
└── Scrollbar (optional)
```
<!-- END HOUSE -->

**Setup rules:**
- **ScrollRect** component goes on the root ScrollView object
<!-- BEGIN HOUSE -->
- **Viewport** clips with `RectMask2D` (no stencil, no extra draw call, culls items fully outside it). Use `Mask` + `Image` only for a non-rectangular viewport (Mask requires a Graphic; turn off Show Mask Graphic if the image should not draw)
- **Content** of a short list (one object per item) must have `ContentSizeFitter` with Vertical Fit set to "Preferred Size" so the scroll area grows with children; a pooled long list sizes Content itself (see below)
<!-- END HOUSE -->
- ScrollRect references: assign Content to `Content`, Viewport to `Viewport`, and optionally assign a Scrollbar
- Content can contain static children (settings lists, about pages) or be populated dynamically at runtime

**Dynamic population (runtime items):**
<!-- BEGIN HOUSE -->
- **Reuse existing children** on panel re-open: rebind the first N items to the new data, activate them, deactivate the rest, and Instantiate only when more items are needed. This prevents duplication without Destroy/Instantiate churn (GC spikes and full layout rebuilds on cheap phones)
- Clearing and re-instantiating is acceptable only for short lists that are built once and rarely change
- New item prefabs are instantiated as children of the Content object (`Instantiate(prefab, content, false)`)
- In a short list, the ContentSizeFitter + VerticalLayoutGroup on Content will automatically size the scrollable area
- Long lists (more rows than fit on about two screens) pool a fixed set of rows and recycle them as they scroll out of the Viewport instead of keeping one object per item; every row change in a LayoutGroup rebuilds the whole Content layout, so a long pooled list positions rows itself (fixed row height) rather than through the VerticalLayoutGroup. Remove both the VerticalLayoutGroup and the ContentSizeFitter from its Content (with no layout element left, the fitter would size Content to about 0 and nothing scrolls), set `content.sizeDelta = new Vector2(content.sizeDelta.x, Mathf.Max(0, count * (rowHeight + spacing) - spacing) + paddingTop + paddingBottom)` (the `Max` keeps an empty list at its padding instead of a negative height) whenever the item count changes, and reposition and rebind the pooled rows in `ScrollRect.onValueChanged`
<!-- END HOUSE -->

**Common failures:**
<!-- BEGIN HOUSE -->
- Items duplicated on every open → existing children neither reused nor cleared before populating
- Content not scrollable → a short list is missing ContentSizeFitter on Content (a pooled list never sets `content.sizeDelta` from its item count), or Viewport missing RectMask2D (or Mask), or ScrollRect's Content/Viewport fields unassigned
<!-- END HOUSE -->
- Jitter/flickering → ContentSizeFitter conflict with parent Layout Group (see "Avoiding layout conflicts" in the main skill)
