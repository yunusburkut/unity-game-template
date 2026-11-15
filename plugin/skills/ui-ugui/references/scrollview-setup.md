# ScrollView Setup

ScrollRect requires a specific hierarchy to function correctly. Missing or misordered components cause jitter, duplication, or non-scrollable content.

<!-- HOUSE: the Viewport line in the hierarchy below (RectMask2D instead of Mask + Image) is a house edit. -->
**Required hierarchy:**
```
ScrollView (ScrollRect)
├── Viewport (RectTransform + RectMask2D)
│   └── Content (RectTransform + VerticalLayoutGroup + ContentSizeFitter)
│       └── [Children — static or added at runtime]
└── Scrollbar (optional)
```

**Setup rules:**
- **ScrollRect** component goes on the root ScrollView object
<!-- BEGIN HOUSE -->
- **Viewport** clips with `RectMask2D` (no stencil, no extra draw call, culls items fully outside it). Use `Mask` + `Image` only for a non-rectangular viewport (Mask requires a Graphic; turn off Show Mask Graphic if the image should not draw)
<!-- END HOUSE -->
- **Content** must have `ContentSizeFitter` with Vertical Fit set to "Preferred Size" so the scroll area grows with children
- ScrollRect references: assign Content to `Content`, Viewport to `Viewport`, and optionally assign a Scrollbar
- Content can contain static children (settings lists, about pages) or be populated dynamically at runtime

**Dynamic population (runtime items):**
<!-- BEGIN HOUSE -->
- **Reuse existing children** on panel re-open: rebind the first N items to the new data, activate them, deactivate the rest, and Instantiate only when more items are needed. This prevents duplication without Destroy/Instantiate churn (GC spikes and full layout rebuilds on cheap phones)
- Clearing and re-instantiating is acceptable only for short lists that are built once and rarely change
- New item prefabs are instantiated as children of the Content object (`Instantiate(prefab, content, false)`)
<!-- END HOUSE -->
- The ContentSizeFitter + VerticalLayoutGroup on Content will automatically size the scrollable area
<!-- BEGIN HOUSE -->
- Long lists (more rows than fit on about two screens) pool a fixed set of rows and recycle them as they scroll out of the Viewport instead of keeping one object per item; every row change in a LayoutGroup rebuilds the whole Content layout, so a long pooled list positions rows itself (fixed row height) rather than through the VerticalLayoutGroup
<!-- END HOUSE -->

**Common failures:**
<!-- BEGIN HOUSE -->
- Items duplicated on every open → existing children neither reused nor cleared before populating
- Content not scrollable → missing ContentSizeFitter on Content, or Viewport missing RectMask2D (or Mask), or ScrollRect's Content/Viewport fields unassigned
<!-- END HOUSE -->
- Jitter/flickering → ContentSizeFitter conflict with parent Layout Group (see "Avoiding layout conflicts" in the main skill)
