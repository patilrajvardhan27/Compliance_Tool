---
version: 1.0
name: BEST-Center-design-system
description: A content-first interface for BEST Center research tools. Gallery-style layout with quiet UI chrome, borrowed from Apple's product pages, dressed in the BEST Center (best-iucrc.org) identity — Work Sans and the forest-green palette. Light canvases alternate with deep "canopy" green tiles, one Action Green carries every interactive element, and motion is short, soft and always optional.

source:
  layout-principles: "Apple marketing / store surfaces (gallery tiles, pill CTAs, hairline cards, frosted bars)"
  brand: "https://best-iucrc.org — Blocksy theme palette + Work Sans"

colors:
  # Action
  primary: "#007A40"            # Action Green — BEST Green darkened for AA text contrast (5.4:1 on white)
  primary-focus: "#00964F"      # BEST Green (brand exact, palette-2) — focus rings, active indicators, brand rule
  primary-on-dark: "#3FC380"    # Bright leaf — links and accents on canopy tiles
  # Text
  ink: "#0C3D00"                # Forest (palette-1) — headlines
  body: "#161616"               # Charcoal — paragraphs and UI text on light surfaces
  body-on-dark: "#FFFFFF"
  body-muted: "#B9DEB8"         # Mint (palette-8) — secondary copy on dark tiles
  ink-muted-80: "#4A5246"       # Secondary copy on light surfaces
  ink-muted-48: "#767171"       # Warm gray (palette-6) — fine print, disabled, captions on white only
  # Lines
  divider-soft: "#EEF2EC"
  hairline: "#DDE3DA"
  hairline-strong: "#C5CEC1"
  # Surfaces
  canvas: "#FFFFFF"
  canvas-parchment: "#F4F7F2"   # Mist — the alternating light tile and tool page ground
  surface-pearl: "#FAFCF9"
  surface-tile-1: "#061B00"     # Canopy — the BEST hero overlay green, primary dark tile
  surface-tile-2: "#0A2304"
  surface-tile-3: "#041300"
  surface-black: "#161616"      # Charcoal — footer (BEST footer colour)
  surface-chip-translucent: "#D3DDD0"
  mint: "#B9DEB8"               # Selected-state wash, text selection on dark
  mint-wash: "#EAF4E9"          # Selected/highlight row on light
  on-primary: "#FFFFFF"
  on-dark: "#FFFFFF"
  # Status (only where a tool must warn)
  error: "#B42318"
  error-wash: "#FEF3F2"
  warning: "#96650C"            # Ochre (palette-5)
  warning-wash: "#FBF5EA"
  # Data visualization only — never for UI chrome
  data-1: "#00964F"             # BEST Green
  data-2: "#327674"             # Teal (palette-3)
  data-3: "#785A7B"             # Plum (palette-4)
  data-4: "#96650C"             # Ochre (palette-5)
  data-5: "#0C3D00"             # Forest (palette-1)
  data-6: "#767171"             # Warm gray (palette-6)

typography:
  hero-display:   { fontFamily: "Work Sans", fontSize: 56px, fontWeight: 600, lineHeight: 1.07, letterSpacing: -0.9px }
  display-lg:     { fontFamily: "Work Sans", fontSize: 40px, fontWeight: 600, lineHeight: 1.1,  letterSpacing: -0.5px }
  display-md:     { fontFamily: "Work Sans", fontSize: 32px, fontWeight: 600, lineHeight: 1.2,  letterSpacing: -0.4px }
  lead:           { fontFamily: "Work Sans", fontSize: 24px, fontWeight: 400, lineHeight: 1.3,  letterSpacing: -0.1px }
  lead-airy:      { fontFamily: "Work Sans", fontSize: 21px, fontWeight: 300, lineHeight: 1.5,  letterSpacing: 0 }
  tagline:        { fontFamily: "Work Sans", fontSize: 21px, fontWeight: 600, lineHeight: 1.19, letterSpacing: -0.2px }
  body-strong:    { fontFamily: "Work Sans", fontSize: 17px, fontWeight: 600, lineHeight: 1.3,  letterSpacing: -0.17px }
  body:           { fontFamily: "Work Sans", fontSize: 17px, fontWeight: 400, lineHeight: 1.47, letterSpacing: -0.17px }
  body-ui:        { fontFamily: "Work Sans", fontSize: 15px, fontWeight: 400, lineHeight: 1.45, letterSpacing: -0.1px }
  caption:        { fontFamily: "Work Sans", fontSize: 14px, fontWeight: 400, lineHeight: 1.43, letterSpacing: -0.1px }
  caption-strong: { fontFamily: "Work Sans", fontSize: 14px, fontWeight: 600, lineHeight: 1.29, letterSpacing: -0.1px }
  button-large:   { fontFamily: "Work Sans", fontSize: 18px, fontWeight: 400, lineHeight: 1.0,  letterSpacing: 0 }
  button:         { fontFamily: "Work Sans", fontSize: 15px, fontWeight: 500, lineHeight: 1.0,  letterSpacing: 0 }
  fine-print:     { fontFamily: "Work Sans", fontSize: 12px, fontWeight: 400, lineHeight: 1.33, letterSpacing: 0 }
  nav-link:       { fontFamily: "Work Sans", fontSize: 13px, fontWeight: 400, lineHeight: 1.0,  letterSpacing: 0 }
  numeric:        { fontFamily: "Work Sans", fontFeature: "tnum", note: "all data values use tabular figures" }

rounded:
  none: 0px
  xs: 5px
  sm: 8px
  md: 11px
  lg: 18px
  pill: 9999px
  full: 9999px

spacing:
  xxs: 4px
  xs: 8px
  sm: 12px
  md: 17px
  lg: 24px
  xl: 32px
  xxl: 48px
  section: 80px

elevation:
  flat: "none"
  hairline: "1px solid {colors.hairline}"
  frosted: "background: rgb(255 255 255 / 0.72); backdrop-filter: saturate(180%) blur(20px)"
  render-shadow: "rgba(0, 0, 0, 0.22) 3px 5px 30px 0"   # the only shadow — renders, diagrams, and floating layers

motion:
  ease-standard: "cubic-bezier(0.28, 0.11, 0.32, 1)"
  ease-emphasized: "cubic-bezier(0.16, 1, 0.3, 1)"
  duration-press: 120ms
  duration-fast: 200ms
  duration-base: 360ms
  duration-reveal: 800ms
  reveal-distance: 24px
  stagger-step: 70ms
  press-scale: 0.95

components:
  button-primary:        { backgroundColor: "{colors.primary}", textColor: "{colors.on-primary}", typography: "{typography.button}", rounded: "{rounded.pill}", padding: 11px 22px }
  button-secondary-pill: { backgroundColor: transparent, textColor: "{colors.primary}", border: "1px solid {colors.primary}", typography: "{typography.button}", rounded: "{rounded.pill}", padding: 11px 22px }
  button-dark-utility:   { backgroundColor: "{colors.body}", textColor: "{colors.on-dark}", typography: "{typography.caption}", rounded: "{rounded.sm}", padding: 8px 15px }
  button-pearl-capsule:  { backgroundColor: "{colors.surface-pearl}", textColor: "{colors.ink-muted-80}", border: "1px solid {colors.hairline}", typography: "{typography.caption}", rounded: "{rounded.md}", padding: 8px 14px }
  option-chip:           { backgroundColor: "{colors.canvas}", textColor: "{colors.body}", border: "1px solid {colors.hairline}", typography: "{typography.caption}", rounded: "{rounded.md}", padding: 8px 14px }
  option-chip-selected:  { backgroundColor: "{colors.mint-wash}", textColor: "{colors.ink}", border: "2px solid {colors.primary-focus}" }
  segmented-control:     { backgroundColor: "{colors.divider-soft}", rounded: "{rounded.pill}", padding: 3px, thumb: "{colors.canvas}" }
  text-input:            { backgroundColor: "{colors.canvas}", textColor: "{colors.body}", border: "1px solid {colors.hairline-strong}", typography: "{typography.body-ui}", rounded: "{rounded.sm}", padding: 8px 12px, height: 40px, focus: "2px {colors.primary-focus} ring" }
  search-input:          { backgroundColor: "{colors.canvas}", border: "1px solid {colors.hairline}", rounded: "{rounded.pill}", padding: 12px 20px, height: 44px }
  global-nav:            { backgroundColor: "{elevation.frosted}", textColor: "{colors.body}", typography: "{typography.nav-link}", height: 52px, borderBottom: "2px solid {colors.primary-focus}" }
  tile-light:            { backgroundColor: "{colors.canvas}", textColor: "{colors.ink}", rounded: "{rounded.none}", padding: 80px }
  tile-parchment:        { backgroundColor: "{colors.canvas-parchment}", textColor: "{colors.ink}", rounded: "{rounded.none}", padding: 80px }
  tile-dark:             { backgroundColor: "{colors.surface-tile-1}", textColor: "{colors.on-dark}", rounded: "{rounded.none}", padding: 80px }
  utility-card:          { backgroundColor: "{colors.canvas}", border: "1px solid {colors.hairline}", rounded: "{rounded.lg}", padding: 24px }
  result-highlight-card: { backgroundColor: "{colors.surface-tile-1}", textColor: "{colors.on-dark}", rounded: "{rounded.lg}", padding: 24px }
  stat-tile:             { backgroundColor: "{colors.canvas}", border: "1px solid {colors.hairline}", rounded: "{rounded.lg}", value: "{typography.display-md} tnum", label: "{typography.caption} {colors.ink-muted-80}" }
  floating-sticky-bar:   { backgroundColor: "{elevation.frosted}", height: 64px, padding: 12px 32px, borderTop: "1px solid {colors.hairline}" }
  footer:                { backgroundColor: "{colors.surface-black}", textColor: "{colors.body-muted}", borderTop: "4px solid {colors.primary-focus}", typography: "{typography.fine-print}", padding: 48px }
---

## Overview

BEST Center tools are research instruments, so the design treats the **data as the product**. The layout grammar comes from Apple's product pages — full-bleed tiles, quiet chrome, one interactive colour, generous air — while every colour and the typeface come from the BEST Center website (best-iucrc.org): **Work Sans**, forest headlines, BEST Green, mint, and the deep canopy green of its hero overlay.

The page should read like a gallery: the wall disappears and the number, chart or wall section takes over. No decorative gradients, no drop shadows on cards or buttons, no borders thicker than a hairline except the single green brand rule under the nav and over the footer.

**Key characteristics**
- Content first; UI recedes.
- Alternating full-bleed tiles on landing pages: white → mist → canopy green. The colour change is the divider.
- One accent: **Action Green `#007A40`** carries every link, button and selected state. BEST Green `#00964F` is the focus ring and brand rule.
- Two button grammars: green pill CTAs (`rounded.pill`) and compact utility rects (`rounded.sm`).
- Work Sans at 600 for headlines with slight negative tracking; body at 17px on marketing pages, 15px inside dense tool panels.
- Tabular figures for every number.
- Exactly one shadow, reserved for renders, diagrams and floating layers.
- Motion is soft, short and purposeful, and switches off under `prefers-reduced-motion`.

## Colors

### Brand & accent
- **Action Green** `{colors.primary}` `#007A40` — every interactive element: links, pill buttons, selected chips, active tabs. Derived from BEST Green, darkened so white text and green-on-white text both pass WCAG AA.
- **BEST Green** `{colors.primary-focus}` `#00964F` — the exact brand green. Focus rings, the 2px rule under the global nav, the 4px rule above the footer, progress fills and active indicators.
- **Leaf** `{colors.primary-on-dark}` `#3FC380` — links and accents on canopy tiles, where Action Green disappears.

### Surfaces
- **White** `{colors.canvas}` — the dominant canvas; all cards.
- **Mist** `{colors.canvas-parchment}` `#F4F7F2` — the alternating light tile, and the ground behind tool panels so white cards read without shadows.
- **Pearl** `{colors.surface-pearl}` — ghost button fill.
- **Canopy** `{colors.surface-tile-1}` `#061B00` — the dark tile, taken from the BEST hero overlay. Also the "best result" highlight card inside tools. Tile-2 and Tile-3 are micro-steps for stacked dark tiles.
- **Charcoal** `{colors.surface-black}` `#161616` — the footer, matching the BEST footer.

### Text
- **Forest** `{colors.ink}` `#0C3D00` — headlines on light surfaces (BEST's heading colour).
- **Charcoal** `{colors.body}` `#161616` — paragraphs and UI text.
- **Muted** `{colors.ink-muted-80}` `#4A5246` — secondary copy, labels, units.
- **Warm gray** `{colors.ink-muted-48}` `#767171` — fine print and disabled text, on white only.
- **Mint** `{colors.body-muted}` `#B9DEB8` — secondary copy on canopy/charcoal.

### Data palette
Teal, plum and ochre from the BEST palette exist **only** inside charts, legends and diagrams (`data-1 … data-6`). They never colour buttons, links or chrome.

### No gradients
Atmosphere comes from photography and real diagrams, never CSS gradients.

## Typography

Work Sans replaces SF Pro for every role (loaded with `next/font/google` or Google Fonts). Weights used: 300 / 400 / 500 (buttons only) / 600 / 700.

| Token | Size | Weight | Line height | Tracking | Use |
|---|---|---|---|---|---|
| hero-display | 56px | 600 | 1.07 | -0.9px | Landing hero headline |
| display-lg | 40px | 600 | 1.10 | -0.5px | Tile headlines |
| display-md | 32px | 600 | 1.20 | -0.4px | Section heads, big result numbers |
| lead | 24px | 400 | 1.30 | -0.1px | Tile subcopy |
| lead-airy | 21px | 300 | 1.50 | 0 | Long-form intro paragraphs |
| tagline | 21px | 600 | 1.19 | -0.2px | Card titles, nav product name |
| body | 17px | 400 | 1.47 | -0.17px | Marketing and document paragraphs |
| body-ui | 15px | 400 | 1.45 | -0.1px | Text inside tool panels and forms |
| caption | 14px | 400 | 1.43 | -0.1px | Labels, hints, button text |
| caption-strong | 14px | 600 | 1.29 | -0.1px | Panel titles, column headings |
| fine-print | 12px | 400 | 1.33 | 0 | Units, legal, footers |

**Principles**
- Negative tracking at display sizes only; never below 14px.
- Sentence case everywhere. No wide-tracked uppercase labels.
- Headlines at 600, not 700.
- Every number uses `font-variant-numeric: tabular-nums`.
- Body line-height never tighter than 1.45.

## Layout

- **Base unit** 8px; tokens `4 / 8 / 12 / 17 / 24 / 32 / 48 / 80`.
- **Landing tiles**: 80px vertical padding (48px on phones), edge-to-edge, 0 gap.
- **Content width**: 980px for reading pages, 1280–1400px for tool layouts.
- **Tool layout**: mist page ground, a sticky control column of white cards, results on the right.
- **Gutters**: 16–24px between cards.
- Whitespace is the pedestal: at least 48px above any tile headline.

## Elevation & depth

| Level | Treatment | Use |
|---|---|---|
| Flat | none | Tiles, nav, footer, body |
| Hairline | 1px `{colors.hairline}` | Cards, inputs, tables |
| Frosted | white 72% + `saturate(180%) blur(20px)` | Sticky nav, sticky action bars |
| Render shadow | `rgba(0,0,0,0.22) 3px 5px 30px` | Product renders, diagrams on a surface, popovers/chat panels that float over content |

Cards never get shadows. Hierarchy comes from surface colour (mist → white → canopy) and the frosted blur.

## Shapes

| Token | Value | Use |
|---|---|---|
| none | 0 | Full-bleed tiles |
| sm | 8px | Inputs, utility buttons, inline images |
| md | 11px | Option chips, pearl buttons |
| lg | 18px | Cards, result panels, tables in cards |
| pill | 9999px | Primary/secondary CTAs, segmented controls, search, tags |

## Components

- **Global nav** — 52px, frosted white, product name in tagline weight on the left, quiet 13px links, one green pill CTA on the right, a 2px BEST Green rule at the bottom (the BEST header signature). Sticky.
- **Primary button** — Action Green pill, white 15px/500 text, 11×22px padding, `scale(0.95)` on press, 2px BEST Green focus ring with 2px offset.
- **Secondary button** — transparent pill, 1px Action Green border, green text.
- **Utility button** — charcoal 8px rect, 14px white text. For tool actions like Export.
- **Option chip** — white, hairline, 11px radius. Selected: mint-wash fill + 2px BEST Green border.
- **Segmented control / tabs** — mist pill track with a white sliding thumb; active label in forest.
- **Text input** — white, 1px hairline-strong, 8px radius, 40px tall, green focus ring. Errors use `{colors.error}` border + message below.
- **Utility card** — white, 1px hairline, 18px radius, 24px padding. The building block of every tool panel.
- **Result highlight card** — canopy tile with white text and mint secondary copy, 18px radius; used for the single best/primary result.
- **Stat tile** — white card, big tabular number in display-md forest, caption label above, unit in fine-print.
- **Tables** — hairline rows, caption-strong muted headers, tabular numbers right-aligned, no zebra stripes (use mint-wash for the highlighted row only).
- **Footer** — charcoal with 4px BEST Green top rule, mint and white fine-print links.

## Motion

Motion explains change; it is never decoration. Every animation is disabled under `prefers-reduced-motion: reduce`, and content is fully visible without JavaScript.

| Pattern | Spec | Use |
|---|---|---|
| Reveal on scroll | opacity 0→1, translateY 24px→0, 800ms `ease-emphasized` | Landing tiles, section heads, cards entering the viewport (`[data-reveal]`) |
| Stagger | children delayed by 70ms each | Card grids, step lists, result rows on first paint (`.stagger`) |
| Page enter | opacity + 12px rise, 600ms | Main content on route load (`.animate-enter`) |
| Press | `scale(0.95)` 120ms | Every button and chip |
| Hover lift | colour shift only, 200ms | Links, chips, rows — no hover shadows |
| Tab / segment thumb | transform 360ms `ease-standard` | Segmented controls |
| Result refresh | opacity 0→1 + 6px rise, 360ms | New numbers after a calculation (`.animate-settle`) |
| Bars & meters | width/height from 0, 800ms `ease-emphasized` | Score bars, chart fills |

## Do's and don'ts

**Do**
- Use Action Green for every interactive element and nothing else.
- Alternate white / mist / canopy tiles on landing pages.
- Put tool controls in white hairline cards on a mist ground.
- Use tabular figures for all data.
- Keep the 2px green rule under the nav and the 4px green rule over the footer — they are the BEST signature.
- Respect reduced motion.

**Don't**
- Don't add a second accent colour; teal/plum/ochre are chart-only.
- Don't put shadows on cards, buttons or text.
- Don't use gradients.
- Don't use uppercase wide-tracked labels.
- Don't round full-bleed tiles.
- Don't animate layout for its own sake — no bouncing, no parallax, no looping motion.

## Responsive behaviour

| Breakpoint | Change |
|---|---|
| ≤ 640px | Single column; hero 34px; tiles 48px padding; nav collapses to name + CTA |
| 641–1023px | Two-column grids; tool controls stack above results |
| ≥ 1024px | Sticky control column + results |
| ≥ 1440px | Content locks at max width |

Touch targets are at least 44×44px on phones. Inputs are 16px on phones to stop iOS zoom.

## Iteration guide

1. Reference tokens, never raw hex, in components.
2. New variants live next to their base component.
3. When in doubt about emphasis, change the surface (mist → white → canopy) before adding chrome.
4. One shadow. One accent. One typeface.
