---
name: Siam Hydrocarbon Intelligence
colors:
  surface: '#faf8ff'
  surface-dim: '#d2d9f4'
  surface-bright: '#faf8ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f2f3ff'
  surface-container: '#eaedff'
  surface-container-high: '#e2e7ff'
  surface-container-highest: '#dae2fd'
  on-surface: '#131b2e'
  on-surface-variant: '#3e484f'
  inverse-surface: '#283044'
  inverse-on-surface: '#eef0ff'
  outline: '#6e787f'
  outline-variant: '#bdc8d0'
  surface-tint: '#006688'
  primary: '#006385'
  on-primary: '#ffffff'
  primary-container: '#007ea7'
  on-primary-container: '#fbfcff'
  inverse-primary: '#77d1ff'
  secondary: '#315ca9'
  on-secondary: '#ffffff'
  secondary-container: '#86adff'
  on-secondary-container: '#033e8a'
  tertiary: '#914800'
  on-tertiary: '#ffffff'
  tertiary-container: '#b65c00'
  on-tertiary-container: '#fffbff'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#c2e8ff'
  primary-fixed-dim: '#77d1ff'
  on-primary-fixed: '#001e2c'
  on-primary-fixed-variant: '#004d68'
  secondary-fixed: '#d8e2ff'
  secondary-fixed-dim: '#aec6ff'
  on-secondary-fixed: '#001a42'
  on-secondary-fixed-variant: '#0f4490'
  tertiary-fixed: '#ffdcc6'
  tertiary-fixed-dim: '#ffb784'
  on-tertiary-fixed: '#301400'
  on-tertiary-fixed-variant: '#713700'
  background: '#faf8ff'
  on-background: '#131b2e'
  surface-variant: '#dae2fd'
typography:
  headline-xl:
    fontFamily: Manrope
    fontSize: 40px
    fontWeight: '700'
    lineHeight: 48px
    letterSpacing: -0.02em
  headline-xl-mobile:
    fontFamily: Manrope
    fontSize: 30px
    fontWeight: '700'
    lineHeight: 38px
    letterSpacing: -0.015em
  headline-lg:
    fontFamily: Manrope
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.015em
  headline-lg-mobile:
    fontFamily: Manrope
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Manrope
    fontSize: 22px
    fontWeight: '600'
    lineHeight: 28px
    letterSpacing: -0.01em
  headline-sm:
    fontFamily: Manrope
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 24px
  body-lg:
    fontFamily: Hanken Grotesk
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-md:
    fontFamily: Hanken Grotesk
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  body-sm:
    fontFamily: Hanken Grotesk
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 16px
  metric-display:
    fontFamily: JetBrains Mono
    fontSize: 28px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.03em
  label-md:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.02em
  label-sm:
    fontFamily: JetBrains Mono
    fontSize: 10px
    fontWeight: '500'
    lineHeight: 14px
    letterSpacing: 0.04em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  gutter: 1.25rem
  gutter-mobile: 0.75rem
  margin: 2rem
  margin-mobile: 1rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 1rem
  space-lg: 1.5rem
  space-xl: 2.25rem
---

## Brand & Style

This design system delivers an executive-tier, mission-critical energy analytics platform tailored for Southeast Asia's petroleum infrastructure. The aesthetic balances optical precision, fluid lightness, and corporate rigor through an elevated Light Glassmorphism treatment. 

Rather than standard opaque data dashboards, surfaces evoke crystalline industrial instrumentation: translucent frosted surfaces, specular light edges, and faint refracted atmospheric glows that mimic natural daylight falling across high-tech command center consoles.

Key Tenets:
- **Luminosity & Clarity**: Backgrounds feel breathable and atmospheric. Information is layered via frosted vitreous plates that segment data streams without boxing them in.
- **Instrument Precision**: Metrics, barometric pressure readouts, refinery flow velocities, and fiscal telemetry look exact, sharp, and authoritative.
- **Controlled Vibrancy**: Dynamic marine cyans and deep gulf blues command primary workflows, balanced by warm refined amber/tangerine alerts that signal petroleum flow, thermal levels, and real-time yield spikes.
- **Executive Readability**: Deep maritime slate ensures absolute typographic contrast across all translucent layers, meeting stringent WCAG AAA legibility targets under any ambient lighting condition.

## Colors

The color architecture is built around an airy, clean-room atmospheric base accented by marine energy teals and hydrocarbon amber thermal indicators.

### Surface & Atmosphere
- **Canvas Base**: `#F0F5FA` layered with subtle directional mesh gradients shifting softly between `#E8F2FA` and `#F8FAFC`.
- **Vitreous Plate Primary (Cards & Modals)**: `rgba(255, 255, 255, 0.72)` with active specular perimeter highlighting.
- **Vitreous Plate Elevated (Dropdowns & Floating Overlays)**: `rgba(255, 255, 255, 0.86)`.
- **Subsurface Inset (Wells & Form Tracks)**: `rgba(235, 243, 250, 0.55)`.

### Chromatic Roles
- **Primary Energy Marine (`#0096C7`)**: Active navigation states, primary telemetry gauges, fluid volume vectors, and direct call-to-action surfaces.
- **Deep Maritime Anchor (`#023E8A`)**: Deep flow paths, historical analytics overlays, structural charts, and critical interactive nodes.
- **Thermal Amber (`#F77F00`) & Kinetic Tangerine (`#E85D04`)**: Pipeline throughput warnings, crude fraction indicators, thermal telemetry, and operational yield thresholds.
- **Executive Typography Hierarchy**:
  - **High-Empathy Heading & Primary Value**: `#0F172A` (Slate Navy 900)
  - **Standard Data Readouts & Body**: `#1E293B` (Slate Navy 800)
  - **Metric Units, Secondary Headers, & Inactive Labels**: `#475569` (Slate Navy 600)
  - **Subtle Tick Marks & Vitreous Grid Dividers**: `rgba(15, 23, 42, 0.08)`

## Typography

Typographic structure balances geometric authority with technical precision:

- **Primary Display & Headings (`Manrope`)**: Provides an authoritative, rounded architectural presence for dashboard suite titles, refinery section headers, and macro summary banners.
- **Narrative & Contextual Text (`Hanken Grotesk`)**: Clean, low-distortion neo-grotesque optimized for parsing dense technical logs, chemical compositions, and production reports.
- **Telemetry, Metrics, & Timestamps (`JetBrains Mono`)**: Strict tabular alignment for throughput barrels per day (BPD), pipeline pressures (PSI), temperature gauges, coordinates, and real-time streaming tickers.

## Layout & Spacing

The layout is engineered as a responsive 12-column analytical canvas using an 8pt architectural rhythm.

### Grid & Breakpoints
- **Desktop Grid (1440px and up)**: 12-column layout with 2rem (`32px`) margins and 1.25rem (`20px`) gutters. Provides maximum spatial stability for complex multi-chart telemetry walls.
- **Tablet Grid (768px – 1439px)**: 8-column layout with 1.5rem (`24px`) margins and 1rem (`16px`) gutters. Side rails collapse into frosted floating action docks.
- **Mobile Handheld (Below 768px)**: 4-column layout with 1rem (`16px`) margins and 0.75rem (`12px`) gutters. Dual-axis widgets stack vertically into dedicated glanceable analytical cards.

### Spatial Discipline
- Never overcrowd frosted panels; allow minimum `space-lg` separation between disparate analytical modules so blurred background elements maintain subtle depth without creating visual static.
- Card interiors consistently employ `space-md` (`16px`) to `space-lg` (`24px`) padding to isolate numeric readouts from perimeter glass refraction borders.

## Elevation & Depth

Visual hierarchy is attained through optical refraction, light dispersion, and specular boundary gradients rather than heavy drop shadows.

### Glassmorphism & Refractive Surface Hierarchy
1. **Atmospheric Canvas (Level 0)**: Non-blurry, soft luminescent substrate with directional daylight gradients.
2. **Standard Instrument Panel (Level 1)**: 
   - Fill: `rgba(255, 255, 255, 0.72)`
   - Filter: `backdrop-filter: blur(14px) saturate(160%)`
   - Perimeter: `border: 1px solid rgba(255, 255, 255, 0.85)` with a faint directional highlight (top and left edges hit by light).
   - Shadow: `0 8px 32px -4px rgba(2, 62, 138, 0.05), 0 2px 8px -1px rgba(0, 150, 199, 0.04)`
3. **Elevated Tactical Overlays & Flight Modals (Level 2)**:
   - Fill: `rgba(255, 255, 255, 0.88)`
   - Filter: `backdrop-filter: blur(20px) saturate(180%)`
   - Perimeter: `border: 1px solid rgba(255, 255, 255, 0.95)`
   - Shadow: `0 20px 48px -8px rgba(2, 62, 138, 0.10), 0 0 16px 2px rgba(0, 150, 199, 0.08)`
4. **Recessed Data Cavities (Wells, Code Tracks, Tables)**:
   - Fill: `rgba(240, 245, 250, 0.50)`
   - Perimeter: `border: 1px solid rgba(15, 23, 42, 0.05)`
   - Shadow: `inset 0 2px 4px rgba(15, 23, 42, 0.03)`

## Shapes

The geometric form factor relies on balanced curvature (`0.5rem` / `8px` baseline) reflecting precision milled glass tiles.

- **Primary Cards & Telemetry Pods**: `rounded-lg` (`1rem` / `16px`). Smooth ergonomic corners that accentuate inner specular rim lighting.
- **Dropdowns, Popovers, & Tooltips**: `rounded-md` (`0.5rem` / `8px`).
- **Control Pills, Metric Badges, & Status Pins**: `rounded-full` (`9999px`) for quick glanceable status nodes (e.g., active pipeline flow markers).
- **Interactive Buttons & Input Wells**: `rounded-md` (`0.5rem` / `8px`) matching structural precision without appearing overly bubbly.

## Components

### Vitreous Analytics Cards
- Standard data containers feature `rgba(255, 255, 255, 0.72)` background fills with `backdrop-filter: blur(14px)`.
- Borders use a linear gradient: `rgba(255, 255, 255, 0.9)` at the top-left descending to `rgba(255, 255, 255, 0.4)` at the bottom-right to emulate overhead daylight reflection.
- Cards host an upper meta bar containing Manrope category titles (`12px`, uppercase, tracking `0.05em`) paired with mono status pills.

### Buttons & Interactive Controls
- **Primary Action**: Solid cyan base (`#0096C7`) with white text, accompanied by an ambient cyan glow hover state (`box-shadow: 0 4px 14px rgba(0, 150, 199, 0.35)`).
- **Glass / Secondary Action**: Translucent plate (`rgba(255, 255, 255, 0.65)`), crisp specular border (`rgba(255, 255, 255, 0.9)`), deep navy text (`#0F172A`). Hover triggers `rgba(255, 255, 255, 0.95)` and an azure rim glow.
- **Thermal Alert CTA**: Saturated amber (`#F77F00`) with high-contrast white text, reserved for valve release overrides, hazard logging, or threshold acknowledgments.

### Data Inputs & Search
- Translucent hollow fields (`rgba(255, 255, 255, 0.5)`) that shift to `rgba(255, 255, 255, 0.95)` with a solid `#0096C7` perimeter glow on focus.
- Placeholder text in `#475569`. Input text rendered in `#0F172A`.

### Status Badges & Chips
- **Nominal Flow / Stable**: Glass pill with `rgba(0, 150, 199, 0.12)` fill, `#023E8A` text, and a glowing cyan pulsing indicator.
- **Alert / Overpressure**: Glass pill with `rgba(247, 127, 0, 0.15)` fill, `#E85D04` text, and an amber indicator.
- **Offline / Standby**: Glass pill with `rgba(15, 23, 42, 0.08)` fill, `#475569` text.

### Telemetry Charts & Visualization Nodes
- Line graphs use high-luminance strokes (`#0096C7`, `#023E8A`, `#F77F00`) with translucent area-fills fading to `0%` opacity at the chart baseline.
- Crosshairs render as crisp 1px dashed lines in `#0096C7` with glassmorphic tooltip chips showing real-time timestamps (`JetBrains Mono`) and values floating directly over data coordinates.