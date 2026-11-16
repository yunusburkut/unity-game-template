# Categorical palettes that stay apart, colour-blind included

The numbers behind CL09 for a set of colours that names categories (teams, players, pieces, liquids, gem types). A
colour that only decorates needs none of this. The recommended set and the benchmark row you need are inlined below.
The full worked example (benchmarks of Okabe-Ito, Tol, IBM, Tableau and Kelly, ordering, symbols) is optional
background that exists only on the template machine, not in game repos:
`C:\GitHub\unity-game-template\packs\reference-docs\research_notes\Sort bulmaca oyunu renk teorisi\palette_distinguishability.md`.

No standard sets a categorical threshold: the just-noticeable difference is about 0.02 ΔEOK (about 1 ΔE00), far too
small for at-a-glance matching. The targets below come from the worst pair of palettes experts accept as CVD-safe
(Okabe-Ito's worst simulated pair is 0.076 ΔEOK) `[inferred]`.

## Targets

| Check | Target |
|---|---|
| Every pair, normal vision | at least 0.10-0.12 ΔEOK (ΔE00 about 15 or more) |
| Every pair, under each simulated CVD (protan, deutan, tritan) | at least 0.075-0.08 ΔEOK (ΔE00 about 8-10) |
| Hard failure | any pair under about 0.04 ΔEOK in simulation collapses in play |
| Lightness spread | OKLab L across about 0.45-0.97, about 0.5 between the darkest and the lightest |
| Count | about 7-9 colours at most for colour-only identification; past that, lightness tiers plus a shape or pattern per colour |

- Under red-green CVD only lightness and the blue-yellow axis are left, so two colours with the same L must differ on
  blue-yellow (Okabe-Ito vermillion and bluish-green share L 0.62 and survive because the green leans blue).
- A dark background costs the bottom of the L axis: against an L 0.25 background, colours under L 0.45 drop below
  about 2:1 contrast and turn into weak categories. A colour that also means "hidden" or "empty" keeps its own L band.
- Passing the numbers does not lift CL09: every category still carries a shape, icon, name or pattern, and the
  colour-blind mode adds a symbol per colour rather than a whole-screen filter.
- Small, brief marks read worse than the numbers say (small-field tritan confusion): give a category colour enough
  area, or a second cue.

## Starting points

- **Up to 7 colours:** Okabe-Ito, #E69F00 #56B4E9 #009E73 #F0E442 #0072B2 #D55E00 #CC79A7 (plus #000000). Worst
  pair: normal 0.156, protan 0.096, deutan 0.076, tritan 0.085 ΔEOK.
- **Up to 12 colours:** the recommended set, in the order to introduce them (early levels take the first ones, which
  are the most distinct): Red #EA464A, Blue #1770FA, Yellow #F1D01B, Cyan #3DCDCF, White (cream) #F6F3E9, Pink
  #C75CAA, Brown #7E462D, Orange #F98A21, Purple #7B4EAE, Green #61BD69, Lime #BEF686, Gray (warm) #9D968E. Worst
  pair: normal 0.108 (Yellow/Lime), protan 0.088 (Orange/Green), deutan 0.076 (Yellow/Lime), tritan 0.076
  (Green/Cyan). Tuned against a dark background of oklch(0.25 0.04 270); Brown (L 0.456) and Purple (L 0.519) are
  the weakest against it. A different background means scoring again, and past about 9 colours the shape or pattern
  per colour is required, not optional.

## Method

The score of a palette is the minimum pairwise ΔEOK over four conditions: normal, protanopia, deuteranopia and
tritanopia. ΔEOK is the Euclidean distance in OKLab.

1. sRGB to linear sRGB (the standard transfer: `c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055)^2.4`).
2. For a CVD condition, multiply the linear colour by the Machado, Oliveira and Fernandes 2009 matrix at severity 1.0
   and clamp to [0, 1]. Rows:
   - Protan: (0.152286, 1.052583, -0.204868), (0.114503, 0.786281, 0.099216), (-0.003882, -0.048116, 1.051998)
   - Deutan: (0.367322, 0.860646, -0.227968), (0.280085, 0.672501, 0.047413), (-0.011820, 0.042940, 0.968881)
   - Tritan: (1.255528, -0.076749, -0.178779), (-0.078411, 0.930809, 0.147602), (0.004733, 0.691367, 0.303900)
3. Linear sRGB to OKLab with Ottosson's matrices:
   - `l = 0.4122214708 r + 0.5363313299 g + 0.0514459929 b`
   - `m = 0.2119034982 r + 0.6806995451 g + 0.1073969566 b`
   - `s = 0.0883024619 r + 0.2817188376 g + 0.6299787005 b`
   - take the cube root of l, m and s, then
   - `L = 0.2104542553 l + 0.7936177850 m - 0.0040720468 s`
   - `a = 1.9779984951 l - 2.4285922050 m + 0.4505937099 s`
   - `b = 0.0259040371 l + 0.7827717662 m - 0.8086757660 s`
4. Check the implementation first: #FF0000 must give oklch(0.628 0.258 29.23), and the CVD path must give Okabe-Ito
   bluish green #009E73 against reddish purple #CC79A7 under deutan as 0.0761 ΔEOK (the Okabe-Ito deutan worst
   pair; protan #0072B2/#CC79A7 gives 0.0955). A matrix applied by columns or to gamma-encoded values misses these.

Machado 2009 models tritanopia poorly (it suits anomalous trichromacy best), so a tritan pass is approximate: also
look at the palette through a simulator (Colour Oracle on PC, a CVD simulator on the phone) at full severity.
Run it as a small Editor script in the game, which reads the palette asset directly; write the worst pair per
condition on the `DESIGN.md` Look > Palette line next to each colour's backup (CL37).
