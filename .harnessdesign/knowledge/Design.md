# Prism Design System — Desktop & Web 2.5

> **Figma Source File**: [Prism Desktop — Web 2.5](https://www.figma.com/design/OWKBE2BJBBanezKhapWx2Y/Prism-Desktop---Web-2.5?m=dev)
> **Sticker Sheet**: [node-id=87965-45200](https://www.figma.com/design/OWKBE2BJBBanezKhapWx2Y/Prism-Desktop---Web-2.5?m=dev&node-id=87965-45200)
> **File Key**: `OWKBE2BJBBanezKhapWx2Y`
> **Library Key**: `lk-6ee1714a4c349337e72ad8b4da7dec8c657b1ac90c7009476d4ed3162a9551ab487734fd41432129d713b0ef68fb096ee4a0e5d6f005c23514a81274fd0946b6`
> **Variables Sheet**: [Prism Visual Assets Library 2.5](https://www.figma.com/design/h6w6QEFNEw9GhxC4ZGKOQ3/Prism-Visual-Assets-Library-2.5?m=dev&node-id=70183-10010) — File Key: `h6w6QEFNEw9GhxC4ZGKOQ3`
> **Token Source**: ADS: Design Tokens

This document is the complete specification for the Prism Design System, intended for AI code generation tools (Cursor / Claude Code, etc.) to reference directly when building UI prototypes. All values are extracted from actual components in the Figma Sticker Sheet.

---

## 1. Design Principles

| Principle | Description |
|-----------|-------------|
| Consistency | All components follow a unified visual language: same spacing, border-radius, and interaction states |
| Semantic Tokens | Colors, fonts, etc. are all referenced via semantic CSS variables, never hardcoded hex values |
| State Completeness | Every interactive component must cover 5 states: Default / Hover / Pressed / Focused / Disabled |
| Accessibility | Follows WCAG 2.1 AA, ensuring sufficient color contrast and keyboard navigation support |
| Five-Theme Adaptation | The system supports 5 themes: Light, Dark, Bloom (blue-toned dark), Agave (teal-toned dark), Rose (pink-toned dark), with tokens adapting automatically |

---

## 2. Design Tokens

### 2.1 Color System — Semantic Tokens

Use CSS variables for color references. **Never** hardcode hex values in code (fallback values are only for when tokens are unavailable).

> The table below uses the **Light mode** as an example to illustrate usage. For the complete five-theme (Light/Dark/Bloom/Agave/Rose) color value comparison, see **§ 2.1b Multi-Theme Color Variable Complete Reference**.

#### Background

| Token | CSS Variable | Fallback | Usage |
|-------|-------------|----------|-------|
| bg-default | `var(--background/bg-default)` | `white` | Page/container default background |
| bg-darker-neutral | `var(--background/bg-darker-neutral)` | `#f1f4f6` | Darker neutral background (header areas, secondary panels) |

#### Fill

| Token | CSS Variable | Fallback | Usage |
|-------|-------------|----------|-------|
| fill-global-primary | `var(--fill/fill-global-primary)` | `#0d6bde` | Primary button, primary icon button, Slider selected range |
| fill-primary | `var(--fill/fill-primary)` | `#0d6bde` | Tab selected indicator, Slider value track |
| fill-default | `var(--fill/fill-default)` | `white` | Default background, Dialog background |
| fill-elevated-strongest | `var(--fill/fill-elevated-strongest)` | `white` | Top-level floating panel (Notification background) |
| fill-elevated-strong | `var(--fill/fill-elevated-strong)` | `rgba(255,255,255,0.8)` | Semi-transparent floating layer (Segmented control selected item) |
| fill-subtle-neutral | `var(--fill/fill-subtle-neutral)` | `#f1f4f6` | Secondary button background, Token label background |
| fill-subtler-neutral | `var(--fill/fill-subtler-neutral)` | `#f7f9fa` | Lighter neutral background |
| fill-subtler-primary | `var(--fill/fill-subtler-primary)` | `#f2f8ff` | Banner info background (alias: `fill-subtler-informative`) |
| fill-contrary-subtler-transparent | `var(--fill/fill-contrary-subtler-transparent)` | `rgba(0,0,0,0.04)` | Segmented control track, Slider track |

#### Text

| Token | CSS Variable | Fallback | Usage |
|-------|-------------|----------|-------|
| text-stronger-neutral | `var(--text/text-stronger-neutral)` | `#222325` | Headings, emphasized text, labels, active tab |
| text-neutral | `var(--text/text-neutral)` | `#686f79` | Body text, secondary text, placeholder, inactive tab |
| text-primary | `var(--text/text-primary)` | `#0d6bde` | Brand color text, links, Ghost button text |
| text-strong-primary | `var(--text/text-strong-primary)` | `#2057b1` | Emphasized brand color text (Tag label text) |
| text-default | `var(--color/text/default)` | — | Default text color |
| text-subtle | `var(--color/text/subtle)` | — | Supporting information |
| text-brand | `var(--color/text/brand)` | — | Brand color text |
| text-danger | `var(--color/text/danger)` | — | Error message |
| text-success | `var(--color/text/success)` | — | Success message |
| inverse-global-default | `var(--inverse/inverse-global-default)` | `white` | Inverse text (white text inside Primary button) |

#### Icon

| Token | CSS Variable | Usage |
|-------|-------------|-------|
| icon-default | `var(--color/icon/default)` | Default icon color |
| icon-subtle | `var(--color/icon/subtle)` | Secondary icon |
| icon-brand | `var(--color/icon/brand)` | Brand color icon |
| icon-danger | `var(--color/icon/danger)` | Error state icon |
| icon-warning | `var(--color/icon/warning)` | Warning state icon |
| icon-inverse | `var(--color/icon/inverse)` | Inverse scenario icon (light icon on dark background) |

#### Border

| Token | CSS Variable | Fallback | Usage |
|-------|-------------|----------|-------|
| border-subtle-neutral | `var(--border/border-subtle-neutral)` | `#dfe3e8` | Dividers, Notification border, table row border |
| border-strong-neutral | `var(--border/border-strong-neutral)` | `#555b62` | Strong border (table header bottom line, prominent separation) |
| border-subtle-primary | `var(--border/border-subtle-primary)` | `#a8ccf8` | Banner border (alias: `border-subtle-informative`) |
| border-bold | `var(--color/border/bold)` | — | Bold border |
| border-brand | `var(--color/border/brand)` | — | Brand color border, selected state |
| input-border | `var(--component/input/input-border)` | `#c1c6ce` | Input field border |

#### Link

| Token | CSS Variable | Usage |
|-------|-------------|-------|
| link-default | `var(--color/link/default)` | Link text color |

#### Underlay / Shadow

| Token | CSS Variable | Fallback | Usage |
|-------|-------------|----------|-------|
| dropshadow | `var(--underlay/dropshadow)` | `rgba(0,0,0,0.08)` | Base color for all drop shadows |

### 2.1b Multi-Theme Color Variable Complete Reference

> Source: [Prism Visual Assets Library 2.5 — Variables Sheet](https://www.figma.com/design/h6w6QEFNEw9GhxC4ZGKOQ3/Prism-Visual-Assets-Library-2.5?m=dev&node-id=70183-10010)

Prism 2.5 supports 5 themes. **Light** and **Dark** are standard light/dark modes; **Bloom** (blue-toned), **Agave** (teal-toned), and **Rose** (pink-toned) are branded dark themes where background and accent colors shift with the brand palette, while semantic colors (error/warning/success) remain consistent across themes.

**Global Tokens (`*-global-*`)**: Values are the same in Light/Dark (not inverted); in Bloom/Agave/Rose they follow the brand color.

#### Background

| Token | Light | Dark | Bloom | Agave | Rose |
|-------|-------|------|-------|-------|------|
| bg-default | `#FFFFFF` | `#131619` | `#1D3770` | `#18413F` | `#571E2C` |
| bg-neutral | `#FCFDFD` | `#1D1E20` | `#081E59` | `#0A3534` | `#430F1E` |
| bg-darker-neutral | `#F1F4F6` | `#040506` | `#143584` | `#11565A` | `#84192F` |

#### Border — Core Tokens

| Token | Light | Dark | Bloom | Agave | Rose |
|-------|-------|------|-------|-------|------|
| border-subtle-neutral | `#DFE3E8` | `#313235` | `#395286` | `#4F6D6B` | `#86525C` |
| border-neutral | `#939BA4` | `#686F79` | `#92A2C2` | `#6A7F7E` | `#996770` |
| border-strong-neutral | `#555B62` | `#C1C6CE` | `#D3DBEC` | `#D2DBDB` | `#E9D3D6` |
| border-subtle-primary | `#A8CCF8` | `#213C77` | `#3865C9` | `#187B79` | `#BC3A55` |
| border-primary | `#4B96F1` | `#0D6BDE` | `#8CB2FF` | `#3A9C99` | `#E3526D` |
| border-strong-primary | `#2057B1` | `#7AB1F4` | `#E2ECFD` | `#C2E9E6` | `#FFD8DB` |

#### Border — Semantic Tokens (Consistent Across Brand Themes)

| Token | Light | Dark | Bloom/Agave/Rose |
|-------|-------|------|-----------------|
| border-subtle-error | `#F6AAB8` | `#771D23` | `#771D23` |
| border-error | `#FF6682` | `#DA1639` | `#DA1639` |
| border-strong-error | `#AF1E30` | `#F17E93` | `#F17E93` |
| border-subtle-warning | `#E1BD93` | `#5D350E` | `#5D350E` |
| border-warning | `#C28030` | `#B36200` | `#B36200` |
| border-strong-warning | `#884B0A` | `#D19F61` | `#D19F61` |
| border-subtle-success | `#9ECEAD` | `#174823` | `#174823` |
| border-success | `#48AD67` | `#247F40` | `#247F40` |
| border-strong-success | `#196830` | `#74B688` | `#74B688` |
| border-subtle-informative | `#A8CCF8` | `#213C77` | `#A8CCF8` |
| border-informative | `#4B96F1` | `#0D6BDE` | `#0D6BDE` |
| border-strong-informative | `#2057B1` | `#7AB1F4` | `#7AB1F4` |

#### Border — Supplementary Colors

| Token | Light | Dark | Bloom/Agave/Rose |
|-------|-------|------|-----------------|
| border-subtle-complementary | `#FFAB81` | `#6B2C0F` | `#6B2C0F` |
| border-complementary | `#FF5F0F` | `#CF4B0A` | `#CF4B0A` |
| border-strong-complementary | `#9D3B0F` | `#FF8548` | `#FF8548` |
| border-subtle-supplementary1 | `#EBDDF6` | `#38214C` | `#EBDDF6` |
| border-supplementary1 | `#AD75DA` | `#864EB5` | `#864EB5` |
| border-strong-supplementary1 | `#73439A` | `#BB8CE0` | `#BB8CE0` |
| border-subtle-supplementary2 | `#61F6F2` | `#003130` | `#003130` |
| border-supplementary2 | `#009E9A` | `#007573` | `#007573` |
| border-strong-supplementary2 | `#006462` | `#00B2AE` | `#00B2AE` |

#### Fill — Core Tokens

| Token | Light | Dark | Bloom | Agave | Rose |
|-------|-------|------|-------|-------|------|
| fill-default | `#FFFFFF` | `#222325` | `#1D3770` | `#18413F` | `#571E2C` |
| fill-subtler-neutral | `#F7F9FA` | `#2A2B2D` | `#395286` | `#335654` | `#703843` |
| fill-subtle-neutral | `#F1F4F6` | `#313235` | `#5B719E` | `#4F6D6B` | `#86525C` |
| fill-neutral | `#686F79` | `#939BA4` | `#BCC4D5` | `#94A6A5` | `#C0979D` |
| fill-global-neutral | `#555B62` | `#555B62` | `#BCC4D5` | `#94A6A5` | `#C0979D` |
| fill-subtler-primary | `#F2F8FF` | `#1A2A52` | `#2049AA` | `#1F615F` | `#973648` |
| fill-primary | `#0D6BDE` | `#4B96F1` | `#C4D8FF` | `#62ADAB` | `#EF798A` |
| fill-global-primary | `#0D6BDE` | `#0D6BDE` | `#3865C9` | `#187B79` | `#BC3A55` |

#### Fill — Semantic Tokens (Consistent Across Brand Themes)

| Token | Light | Dark | Bloom/Agave/Rose |
|-------|-------|------|-----------------|
| fill-subtler-error | `#FFF2F5` | `#54171A` | `#54171A` |
| fill-error | `#DA1639` | `#FF6682` | `#FF6682` |
| fill-global-error | `#DA1639` | `#DA1639` | `#DA1639` |
| fill-subtler-warning | `#FFF9F2` | `#492B0D` | `#492B0D` |
| fill-warning | `#B36200` | `#C28030` | `#C28030` |
| fill-global-warning | `#B36200` | `#B36200` | `#B36200` |
| fill-subtler-success | `#F2FFF6` | `#123019` | `#123019` |
| fill-success | `#247F40` | `#48AD67` | `#48AD67` |
| fill-global-success | `#247F40` | `#247F40` | `#247F40` |
| fill-subtler-informative | `#F2F8FF` | `#1A2A52` | `#2049AA` / `#1F615F` / `#973648` |

#### Text

| Token | Light | Dark | Bloom | Agave | Rose |
|-------|-------|------|-------|-------|------|
| text-neutral | `#686F79` | `#939BA4` | `#D3DBEC` | `#D2DBDB` | `#E9D3D6` |
| text-strong-neutral | `#555B62` | `#DFE3E8` | `#E6EAF0` | `#E7EAEA` | `#F2E8E8` |
| text-stronger-neutral | `#222325` | `#F7F9FA` | `#F5F7FA` | `#FCFDFC` | `#FDFCFC` |
| text-primary | `#0D6BDE` | `#4B96F1` | `#C4D8FF` | `#62ADAB` | `#EF798A` |
| text-global-primary | `#0D6BDE` | `#0D6BDE` | `#C4D8FF` | `#62ADAB` | `#EF798A` |
| text-alternative-primary | `#0B5CFF` | `#75AFF5` | `#8AB3FA` | `#72EDF3` | `#FEA1C5` |
| text-strong-primary | `#2057B1` | `#A8CCF8` | `#E2ECFD` | `#C2E9E6` | `#FFD8DB` |
| text-stronger-primary | `#1A2A52` | `#F2F8FF` | `#FAFCFF` | `#EFFDFC` | `#FFF2F3` |

#### Text — Semantic Tokens (Consistent Across Brand Themes)

| Token | Light | Dark | Bloom/Agave/Rose |
|-------|-------|------|-----------------|
| text-error | `#DA1639` | `#FF6682` | `#FF6682` |
| text-global-error | `#DA1639` | `#DA1639` | `#DA1639` |
| text-alternative-error | `#DB1439` | `#F48A9E` | `#F48A9E` |
| text-strong-error | `#AF1E30` | `#F6AAB8` | `#F6AAB8` |
| text-stronger-error | `#54171A` | `#FFF2F5` | `#FFF2F5` |
| text-warning | `#B36200` | `#C28030` | `#C28030` |
| text-strong-warning | `#884B0A` | `#E1BD93` | `#E1BD93` |
| text-stronger-warning | `#492B0D` | `#FFF9F2` | `#FFF9F2` |
| text-global-strong-warning | `#884B0A` | `#884B0A` | `#884B0A` |
| text-success | `#247F40` | `#48AD67` | `#48AD67` |

#### Icon

| Token | Light | Dark | Bloom/Agave/Rose |
|-------|-------|------|-----------------|
| icon-neutral | `#8E9194` (gray) | `#8E9194` (gray) | = text-neutral |
| icon-strong-neutral | = text-strong-neutral | = text-strong-neutral | = text-strong-neutral |
| icon-stronger-neutral | = text-stronger-neutral | = text-stronger-neutral | = text-stronger-neutral |
| icon-primary | `#3B90F7` (blue) | `#3B90F7` (blue) | `#C4D8FF` / `#62ADAB` / `#EF798A` |
| icon-error | `#FF2638` (red) | `#FF2638` | `#FF2638` |
| icon-warning | `#FFD700` (yellow) | `#FFD700` | `#FFD700` |
| icon-success | `#09A639` (green) | `#09A639` | `#09A639` |
| icon-informative | `#3B90F7` (blue) | `#3B90F7` | `#3B90F7` |
| icon-complementary | `#FF5500` (orange) | `#FF5500` | `#FF5500` |
| icon-supplementary1 | `#AD75DA` | `#864EB5` | `#864EB5` |
| icon-supplementary2 | `#009E9A` | `#007573` | `#007573` |

#### Inverse

| Token | Light | Dark | Bloom | Agave | Rose |
|-------|-------|------|-------|-------|------|
| inverse-default | `#FFFFFF` | `#131619` | `#010D3C` | `#081716` | `#0A0102` |

#### Underlay / Shadow

| Token | Light | Dark | Bloom/Agave/Rose |
|-------|-------|------|-----------------|
| underlay-dark | `#00000033` | `#00000085` | `#00000085` |
| underlay-default | `#FFFFFFCC` | `#000000CC` | `#000000CC` |
| dropShadow | `#00000014` | `#0000007A` | `#0000007A` |
| dropShadow-global | `#00000014` | `#00000014` | `#00000014` |

#### Component Tokens — Badge

| Token | Light | Dark | Bloom/Agave/Rose |
|-------|-------|------|-----------------|
| badge-background-alert | `#DA1639` | `#DA1639` | `#DA1639` (rose: `#FFFFFF`) |
| badge-text-alert | `#FFFFFF` | `#FFFFFF` | `#FFFFFF` (rose: `#000000`) |
| badge-background-default | `#0D6BDE` | `#4B96F1` | `#F2F8FF` |
| badge-text-default | `#FFFFFF` | `#FFFFFF` | `#000000` |
| badge-background-global-default | `#0D6BDE` | `#0D6BDE` | `#F2F8FF` |

#### Component Tokens — Global Nav

| Token | Light | Dark | Bloom/Agave/Rose |
|-------|-------|------|-----------------|
| global-nav-background-classic | `#DFE3E8` | `#555B62` | `#555B62` |

### 2.2 Typography System

**Font Family**: SF Pro (referenced via `var(--font/font-family)`)

| Style Name | Font Size | Weight | Line Height | Letter Spacing Variable | Usage |
|------------|-----------|--------|-------------|------------------------|-------|
| **title-2-emphasis** | 20px | Bold (700) | 24px | `var(--font/font-letterSpacing-20)` → `-0.45px` | Dialog title |
| **body-1-emphasis** | 14px | Semibold (590) | 18px | `var(--font/font-letterSpacing-14)` → `-0.15px` | Accordion label, Notification title |
| **body-1** | 14px | Regular (400) | 18px | `var(--font/font-letterSpacing-14)` → `-0.15px` | Default body text, button text, input label |
| **body-1 (medium)** | 14px | Medium (500) | 18px | `var(--font/font-letterSpacing-14)` → `-0.15px` | Primary button text, Tab text |
| **paragraph-1** | 14px | Regular (400) | 20px | `var(--font/font-letterSpacing-14)` → `-0.15px` | Long-form text (Notification body, Dialog body) |

**Font Weight Quick Reference**:

| Variable | Value | Usage |
|----------|-------|-------|
| `var(--font/font-weight-regular)` | 400 | Body text, Secondary/Ghost buttons |
| `var(--font/font-weight-medium)` | 500 | Primary button, Tab label |
| `var(--font/font-weight-semibold)` | 590 | Accordion label, Notification title |
| `var(--font/font-weight-bold)` | 700 | Dialog title |

**Letter Spacing Quick Reference**:

| Variable | Value | Applicable Font Size |
|----------|-------|---------------------|
| `var(--font/font-letterSpacing-14)` | `-0.15px` | 14px |
| `var(--font/font-letterSpacing-16)` | `-0.31px` | 16px (used in Tabs) |
| `var(--font/font-letterSpacing-20)` | `-0.45px` | 20px |

### 2.3 Spacing System

Based on a **4px base grid**, the following are commonly used spacings extracted from components:

| Value | Usage |
|-------|-------|
| `2px` | Segmented control gap, inline icon button padding |
| `4px` | Button icon-text gap, form label-input gap, content gap |
| `6px` | Button vertical padding, Tab vertical padding, Input vertical padding |
| `8px` | Accordion gap/padding, standard component gap, Segmented control horizontal padding |
| `12px` | Input horizontal padding, Notification content gap, Banner column gap |
| `14px` | Primary/Secondary button horizontal padding |
| `16px` | Tab bar gap, Banner padding, Dialog inner gap, Footer button gap |
| `24px` | Dialog header bottom padding |
| `32px` | Dialog outer padding |

### 2.4 Border Radius

| Value | CSS | Usage |
|-------|-----|-------|
| `999px` | `rounded-[999px]` | Pill/circle: Icon button, Segmented control track & item, Linear progress bar |
| `99px` | `rounded-[99px]` | Rounded inline elements: Avatar, Inline icon button, Slider track |
| `9999px` | `rounded-[9999px]` | Full circle: Slider tick marks |
| `32px` | `rounded-[32px]` | Dialog |
| `16px` | `rounded-[16px]` | Notification |
| `12px` | `rounded-[12px]` | Basic button, Text input, Select input |
| `4px` | `rounded-[4px]` | Small containers |

### 2.5 Shadow

| Token Name | CSS | Usage |
|------------|-----|-------|
| dropShadow-md | `0px 6px 12px var(--underlay/dropshadow), 0px 12px 24px var(--underlay/dropshadow)` | Notification, Dialog |
| dropShadow-sm | `0px 2px 4px var(--underlay/dropshadow), 0px 4px 8px var(--underlay/dropshadow)` | Segmented control selected item |

### 2.6 Blur

| Token | Value | Usage |
|-------|-------|-------|
| `var(--number/blur/blur-sm)` | `15px` | Segmented control backdrop-blur |

### 2.7 Grid System (Column Styles)

> Source: [Column Styles](https://www.figma.com/design/OWKBE2BJBBanezKhapWx2Y/Prism-Desktop---Web-2.5?m=dev&node-id=194458-32745) — **Desktop and Web** platform

The Prism grid system is based on a flexible column layout; all dimension units are `px`. Columns are equal-width and fluid, Gutter is the spacing between columns, and Margin is the spacing on both sides of the content area.

| Grid Style Name | Columns | Gutter | Margin | Recommended Scenario |
|----------------|---------|--------|--------|---------------------|
| **1 Column** | 1 | 16px | 16px | Full-width content: Hero, single-column forms, large media |
| **2 Columns** | 2 | 16px | 32px | Side-by-side comparison, main-side two-column layout |
| **3 Columns** | 3 | 24px | 32px | Card grids, multi-column settings panels |
| **4 Columns** | 4 | 24px | 32px | Dashboard card grids, image galleries |
| **6 Columns** | 6 | 24px | 32px | Complex dashboards, data-intensive views |
| **12 Columns** | 12 | 24px | 32px | Full-featured grid, fine-grained layout control |

**Pattern Summary**:
- Gutter: 1–2 columns use `16px`, 3+ columns use `24px`
- Margin: 1 column uses `16px`, 2+ columns use `32px`
- Column width = `(container width - 2 × Margin - (N-1) × Gutter) / N`

**CSS Grid Implementation Reference**:

```css
/* Generic grid container */
.prism-grid {
  display: grid;
  /* Choose one of the following based on Grid Style */
}

.prism-grid--1col  { grid-template-columns: 1fr;              gap: 16px; padding: 0 16px; }
.prism-grid--2col  { grid-template-columns: repeat(2, 1fr);   gap: 16px; padding: 0 32px; }
.prism-grid--3col  { grid-template-columns: repeat(3, 1fr);   gap: 24px; padding: 0 32px; }
.prism-grid--4col  { grid-template-columns: repeat(4, 1fr);   gap: 24px; padding: 0 32px; }
.prism-grid--6col  { grid-template-columns: repeat(6, 1fr);   gap: 24px; padding: 0 32px; }
.prism-grid--12col { grid-template-columns: repeat(12, 1fr);  gap: 24px; padding: 0 32px; }
```

### 2.8 Sizing Specifications

| Element | Size |
|---------|------|
| Chevron icon | 14 × 14px |
| Icon (inside button) | 16 × 16px |
| Info button | 18 × 18px |
| Icon (Banner/Notification) | 20 × 20px |
| Inline icon button icon | 14 × 14px + 2px padding |
| Icon button (standard) | 32 × 32px (circular) |
| Slider thumb | 24 × 24px (outer) / 16 × 16px (inner) / 10 × 10px (dot) |
| Slider track | Height 4px |
| Slider tick mark | 2 × 2px |
| Avatar | 32 × 32px (default) |

---

## 3. Component Library

The Sticker Sheet includes two complete sets of components for Light mode and Dark mode. The following list covers all components.

### 3.1 Buttons

| Component | Description | Size |
|-----------|-------------|------|
| **Basic button** | Main button, supports Primary / Secondary / Tertiary variants | min-h: 32px |
| **Icon button** | Icon-only circular button | 32 × 32px |
| **Split button** | Button with dropdown separator | h: 32px |
| **Toggle button** | Toggle-style button (on/off), supports icon or text | 32 × 32px / 66 × 32px |
| **Home action button** | Home quick action button (icon + text stacked vertically) | 100 × 84px |
| **Grabber button** | Drag handle button | 18 × 18px |
| **Info button** | Info tooltip trigger button | 18 × 18px |
| **Inline icon button** | Inline close/action button | 14px icon + 2px padding |

**Basic Button Detailed Specifications**:

| Variant | Background | Text Color | Weight | Padding | Border Radius |
|---------|------------|------------|--------|---------|---------------|
| **Primary** | `var(--fill/fill-global-primary)` #0d6bde | `var(--inverse/inverse-global-default)` white | Medium (500) | px: 14px, py: 6px | 12px |
| **Secondary** | `var(--fill/fill-subtle-neutral)` #f1f4f6 | `var(--text/text-primary)` #0d6bde | Regular (400) | px: 14px, py: 6px | 12px |
| **Tertiary (Ghost)** | transparent | `var(--text/text-primary)` #0d6bde | Regular (400) | px: 8px, py: 6px | 12px |

**Icon Button Detailed Specifications**:

| Variant | Background | Border Radius | Size | Icon Size |
|---------|------------|---------------|------|-----------|
| **Primary (Filled)** | `var(--fill/fill-global-primary)` | 999px | 32 × 32px | 16 × 16px |
| **Ghost** | transparent | 999px | 32 × 32px | 16 × 16px |

### 3.2 Form Controls

| Component | Description | Height |
|-----------|-------------|--------|
| **Text input** | Single-line text input with Label + input area | Total height 54px (label 18px + gap 4px + input 32px) |
| **Text area input** | Multi-line text input | Total height 82px |
| **Select input** | Dropdown selection input | Total height 54px / 78px (with helper text) |
| **Ghost select input** | Lightweight borderless dropdown | 32px |
| **Combo input** | Combined input | 32px |
| **Password input** | Password input | Total height 54px |
| **Number input** | Number input | Total height 54px |
| **Search input** | Search input | 32px |
| **Date picker input** | Date picker input | Total height 54px |
| **Checkbox group** | Checkbox group | Variable height per item |
| **Radio group** | Radio button group | Variable height per item |
| **Toggle** (Switch) | Toggle switch control | 16px height |

**Text Input Detailed Specifications**:

```
┌─────────────────────────────────┐
│ Label                            │ ← body-1, text-stronger-neutral
│ (gap: 4px)                       │
├─────────────────────────────────┤
│ [12px] Placeholder       [12px] │ ← min-h: 32px, py: 6px
│         body-1, text-neutral     │
│   border: 1px input-border       │    rounded: 12px
└─────────────────────────────────┘
```

### 3.3 Data Display

| Component | Description | Size |
|-----------|-------------|------|
| **Accordion** | Collapsible accordion panel | min-h: 40px (per row) |
| **Avatar** | User avatar (circular) | 32 × 32px (default) |
| **Avatar group** | Avatar group (stacked display) | — |
| **Divider** | Divider line (horizontal/vertical) | 1px |
| **List item** | List item (with leading/content/trailing slots) | 32px |
| **Inline tag** | Inline tag | — |
| **Text Badge** | Text badge | ~16px height |
| **Notifier** | Notification dot/number | 8px / 16px |
| **Code snippet** | Code snippet display | — |
| **Image gallery** | Image gallery | — |
| **Carousel single** | Single image carousel | 320 × 212px |
| **Carousel multiple** | Multi-image carousel | 864 × 212px |

### 3.4 Navigation

| Component | Description | Size |
|-----------|-------------|------|
| **Tab bar** | Tab switching (underline indicator) | min-h: 32px / 40px |
| **Breadcrumbs** | Breadcrumb navigation | h: 18px |
| **Segmented control** | Segmented control (pill-shaped) | h: 32px, control min-h: 28px |
| **Chip bar** | Chip bar / filter strip | h: 32px |
| **Pagination** | Pagination control | h: 32px |
| **Anchor** | Anchor navigation | — |
| **Step progress indicator** | Step progress indicator (horizontal/vertical) | h: 42px / w: 65px |
| **Link** | Link text | h: 18px |

**Tab Bar Detailed Specifications**:

```
┌──────────┬──────────┬──────────┬──────────┐
│  Label ● │  Label   │  Label   │  Label   │ ← min-h: 32px
│  ═══════ │          │          │          │ ← Selected: 1px fill-primary bottom line
├──────────┴──────────┴──────────┴──────────┤ ← Divider: 1px border-subtle-neutral
```

- Container: `flex`, `gap: 16px`
- Tab: `px: 2px`, `py: 6px`, `min-h: 32px`
- Selected text: `text-stronger-neutral`, `font-weight: medium`
- Unselected text: `text-neutral`, `font-weight: medium`
- Selected indicator: `1px`, `fill-primary`, `rounded: 999px`, at Tab bottom

**Segmented Control Detailed Specifications**:

```
┌─────────────────────────────────────────────┐
│ ┌──Selected──┐  Label    Label    Label      │ ← h: 32px
│ │   Label    │                               │
│ └────────────┘                               │
└─────────────────────────────────────────────┘
```

- Track: `bg: fill-contrary-subtler-transparent`, `rounded: 999px`, `p: 2px`, `gap: 2px`, `backdrop-blur: 15px`
- Selected item: `bg: fill-elevated-strong`, `rounded: 999px`, `shadow: dropShadow-sm`, `min-h: 28px`, `px: 8px`, `py: 4px`, `backdrop-blur: 15px`
- Text: `body-1`, `text-stronger-neutral`

### 3.5 Feedback

| Component | Description | Size |
|-----------|-------------|------|
| **Banner** | Banner notification (with icon, text, action, close) | h: 68px |
| **Notification** | Floating notification card (with title, body, close) | h: 74px |
| **Dialog** | Modal dialog (with Header/Body/Footer) | w: 448px |
| **Dialog overlay** | Dialog overlay mask | Full screen |
| **Info popover** | Info tooltip popover (4 directions) | w: 310-344px, h: 68px |
| **Tooltip** | Tooltip | — |
| **Loading indicator** | Loading indicator (with background overlay) | — |

**Banner Detailed Specifications**:

```
┌─────────────────────────────────────────────────────┐
│ [16px padding]                                       │
│  ℹ [12px] Body text...                     Action  × │
│           text-stronger-neutral, body-1    text-primary│
│ [16px padding]                                       │
├─────────────────────────────────────────────────────┤ ← border-bottom: border-subtle-primary
```

- Background: `fill-subtler-primary` (#f2f8ff) + 30% opacity `fill-default` overlay
- Bottom border: `border-subtle-primary` (#a8ccf8)
- Padding: `16px`
- Icon: `20 × 20px`
- Gap: horizontal `12px` (icon-content), content gap `8px`
- Action: Ghost button style, `text-primary`
- Close: `24px` circular icon button

**Notification Detailed Specifications**:

```
┌─────────────────────────────────────────┐
│ [16px]                                   │
│  ℹ [12px] Title (body-1-emphasis)     ×  │
│           Body (paragraph-1)             │
│ [16px]                                   │
└─────────────────────────────────────────┘
```

- Background: `fill-elevated-strongest` (white)
- Border: `0.5px`, `border-subtle-neutral`
- Border radius: `16px`
- Shadow: `dropShadow-md`
- Padding: `16px`
- Icon: `20 × 20px`
- Content gap: `12px`
- Title: `body-1-emphasis` (14/18, Semibold)
- Body: `paragraph-1` (14/20, Regular)
- Close: inline icon button (14px icon + 2px padding, `rounded: 99px`)

**Dialog Detailed Specifications**:

```
┌──────────────────────────────────────────┐
│ [32px pt, 32px px]                        │
│  Title (title-2-emphasis)            [×]  │ ← Header
│ [24px pb]                                 │
├──────────────────────────────────────────┤
│ [32px px]                                 │
│  Body (paragraph-1)                       │ ← Body
│  [Slot area]                              │
├──────────────────────────────────────────┤
│ [32px padding]                            │
│                    [Secondary] [Primary]  │ ← Footer, gap: 16px
└──────────────────────────────────────────┘
```

- Background: `fill-default` (white)
- Border radius: `32px`
- Shadow: `dropShadow-md`
- Title: `title-2-emphasis` (20/24, Bold, `text-stronger-neutral`)
- Body: `paragraph-1` (14/20, Regular, `text-stronger-neutral`)
- Close button: Ghost icon button `32 × 32px`
- Footer button gap: `16px`

### 3.6 Input Enhancement

| Component | Description | Size |
|-----------|-------------|------|
| **Menu** | Dropdown menu panel | w: 98-184px |
| **Menu item** | Menu item | h: 32px |
| **Dropdown menu** | Dropdown menu combo (trigger + Menu) | — |
| **Dropdown - Date picker** | Date picker dropdown | 280 × 336px |
| **Dropdown - Date & time picker** | Date and time picker | 416 × 400px |
| **Dropdown - Date range picker** | Date range picker | 552 × 336px |
| **Dropdown - Month picker** | Month picker | 280 × 248px |
| **Dropdown - Quarter picker** | Quarter picker | 280 × 104px |
| **Dropdown - Year picker** | Year picker | 280 × 248px |
| **Time picker** | Time picker | 176 × 242px |
| **Emoji picker** | Emoji picker (with search, categories, skin tone selection) | 334 × 380px |
| **Color picker** | Color picker (multiple modes) | 236-252px wide |
| **Slider** | Slider (single value) | h: 24px |
| **Slider range** | Range slider | h: 24px |
| **Dial pad** | Dial pad | 216 × 440-456px |

**Menu Item Detailed Specifications**:
- Height: `32px`
- Padding: `8px` horizontal
- Content: `body-1` (14/18, Regular)
- Supports: Leading slot (icon) + Content slot (label) + Trailing slot

**Slider Detailed Specifications**:
- Track: `h: 4px`, `bg: fill-contrary-subtler-transparent`, `rounded: 99px`
- Value bar: `h: 4px`, `bg: fill-global-primary`, `rounded: 99px`
- Thumb: `24 × 24px` outer frame, `16 × 16px` inner circle
- Tick marks: `2 × 2px`, `rounded: 9999px`

### 3.7 Content

| Component | Description |
|-----------|-------------|
| **Scroll view** | Content container with scrollbar |
| **File uploader** | File upload area (drag-and-drop + list) |
| **Drag and drop** | Drag-and-drop sortable list |
| **Linear** (Progress bar) | Linear progress bar |

### 3.8 Other

| Component | Description |
|-----------|-------------|
| **Pointer** | Mouse cursor style (for demos) |
| **Closed hand** | Dragging mouse cursor style |

---

## 4. Accordion Component Detailed Specifications

> Provided as a reference example to demonstrate the complete specification pattern for Prism components.

### Properties

| Property | Type | Values | Default |
|----------|------|--------|---------|
| variant | enum | `Leading chevron` / `Trailing chevron` | Leading chevron |
| state | enum | `Default` / `Hover` / `Pressed` / `Focused` / `Disabled` | Default |
| expand | enum | `True` / `False` | False |
| label | string | Custom text | "Label" |
| infoButton | boolean | Show/hide info button | false |
| secondaryText | boolean | Show/hide secondary text | false |
| divider | boolean | Show/hide bottom divider | true |

### Layout Specifications

```
┌─────────────────────────────────────┐
│ [8px] ▶ [8px] Label [4px] ⓘ  Detail│ ← min-h: 40px
│         14px   14px/SB     14px/R   │
├─────────────────────────────────────┤ ← divider (1px)
```

- Container: `flex`, `items-center`, `gap-8px`, `padding-8px`, `min-height-40px`
- Chevron: `14 × 14px`
- Label: `body-1-emphasis` (SF Pro Semibold, 14px, line-height 18px), `color: var(--text/text-stronger-neutral)`
- Info button: `18 × 18px`, gap from label `4px`
- Secondary text: `body-1` (SF Pro Regular, 14px), `color: var(--text/text-neutral)`, `text-align: right`
- Divider: `1px`, `absolute bottom-0`, `color: var(--border/border-subtle-neutral)`

### Interaction Behavior

- **Collapse (Default)**: All items collapsed, only label is shown
- **Expand**: Content area expands on click, content area padding-left `30px`
- **Overflow**: Long text wraps automatically (text-wrap), min-height expands with content

---

## 5. Interaction State Specifications

All interactive components must implement the following 5 states:

| State | Visual Change |
|-------|--------------|
| **Default** | Default appearance |
| **Hover** | Subtle background change (usually darkened or with added opacity layer) |
| **Pressed** | Further darkened, slight scale or inner shadow |
| **Focused** | Brand color focus ring (`var(--color/border/brand)`), for keyboard navigation |
| **Disabled** | Reduced opacity (usually 0.4–0.5), interaction disabled |

---

## 6. Using This Specification in AI Coding

### 6.1 Retrieving Component Details

When implementing a Prism component, retrieve precise specifications via Figma MCP:

```
// Get complete design context for a component (includes code and screenshot)
get_design_context(fileKey="OWKBE2BJBBanezKhapWx2Y", nodeId="<component nodeId>")

// Search for a specific component
search_design_system(query="<component name>", fileKey="OWKBE2BJBBanezKhapWx2Y",
  includeLibraryKeys=["lk-6ee1714a4c349337e72ad8b4da7dec8c657b1ac90c7009476d4ed3162a9551ab487734fd41432129d713b0ef68fb096ee4a0e5d6f005c23514a81274fd0946b6"])

// Get design variable definitions
get_variable_defs(fileKey="OWKBE2BJBBanezKhapWx2Y", nodeId="<nodeId>")
```

### 6.2 Code Generation Rules

1. **Always use semantic CSS variables** — Colors, font weights, letter spacing must all be referenced via `var(--token-name)`
2. **Follow the spacing grid** — All spacing must be multiples of 4px (2px is only used in rare cases like Segmented control)
3. **Complete component states** — Every interactive component must implement 5 states
4. **Unified typography** — Use SF Pro font family, referenced via `var(--font/font-family)`
5. **Don't reinvent components** — If Prism already has the corresponding component, use the Prism component instead of building your own
6. **Dividers** — Use the Divider component, color `var(--border/border-subtle-neutral)`; table header bottom line uses `var(--border/border-strong-neutral)`
7. **Border radius hierarchy** — Strictly follow component hierarchy: Dialog(32px) > Notification(16px) > Button/Input(12px) > Small elements(99/999px)
8. **Shadow specification** — Floating panels use `dropShadow-md` uniformly, Segmented control selected item uses `dropShadow-sm`
9. **Grid specification** — Layouts must use Prism Column Styles grid parameters; 1–2 columns Gutter 16px, 3+ columns Gutter 24px; 1 column Margin 16px, 2+ columns Margin 32px

### 6.3 CSS Variable Naming Conventions

```css
/* Background */
--background/bg-default           /* Page/container default background (white) */
--background/bg-darker-neutral    /* Darker neutral background (#f1f4f6) */

/* Fill */
--fill/fill-global-primary        /* Primary brand color fill (#0d6bde) */
--fill/fill-primary               /* Primary fill */
--fill/fill-default               /* Default background (white) */
--fill/fill-elevated-strongest    /* Strongest floating layer (white) */
--fill/fill-elevated-strong       /* Semi-transparent floating layer */
--fill/fill-subtle-neutral        /* Subtle neutral fill (#f1f4f6) */
--fill/fill-subtler-neutral       /* Subtler neutral fill */
--fill/fill-subtler-primary       /* Subtler primary fill (#f2f8ff), alias: fill-subtler-informative */
--fill/fill-contrary-subtler-transparent  /* Semi-transparent inverse */

/* Text Color */
--text/text-stronger-neutral      /* Heading/emphasis (#222325) */
--text/text-neutral               /* Body/secondary (#686f79) */
--text/text-primary               /* Brand/link (#0d6bde) */
--text/text-strong-primary        /* Emphasized brand text (#2057b1) */
--inverse/inverse-global-default  /* Inverse (white) */
--color/text/default              /* Default */
--color/text/subtle               /* Supporting */
--color/text/danger               /* Error */
--color/text/success              /* Success */

/* Icon Color */
--color/icon/default              /* Default icon */
--color/icon/subtle               /* Secondary icon */
--color/icon/brand                /* Brand icon */
--color/icon/danger               /* Error icon */
--color/icon/warning              /* Warning icon */
--color/icon/inverse              /* Inverse icon */

/* Border Color */
--border/border-subtle-neutral    /* Subtle border/divider (#dfe3e8) */
--border/border-strong-neutral    /* Strong border/table header bottom line (#555b62) */
--border/border-subtle-primary    /* Subtle primary border (#a8ccf8), alias: border-subtle-informative */
--component/input/input-border    /* Input field border (#c1c6ce) */
--color/border/bold               /* Bold border */
--color/border/brand              /* Brand border/selected */

/* Shadow */
--underlay/dropshadow             /* Shadow base color rgba(0,0,0,0.08) */

/* Font */
--font/font-family                /* SF Pro font family */
--font/font-weight-regular        /* 400 */
--font/font-weight-medium         /* 500 */
--font/font-weight-semibold       /* 590 */
--font/font-weight-bold           /* 700 */
--font/font-letterSpacing-14      /* -0.15px */
--font/font-letterSpacing-16      /* -0.31px */
--font/font-letterSpacing-20      /* -0.45px */

/* Blur */
--number/blur/blur-sm             /* 15px */
```

### 6.4 React Component Template

Follow this pattern when generating components:

```tsx
type ComponentProps = {
  className?: string;
  variant?: "primary" | "secondary" | "tertiary";
  state?: "default" | "hover" | "pressed" | "focused" | "disabled";
};

function Component({
  className,
  variant = "primary",
  state = "default",
  ...props
}: ComponentProps) {
  return (
    <div
      className={cn(
        // Base styles
        "flex items-center justify-center overflow-clip",
        "min-h-[32px] rounded-[12px]",
        // Typography
        "font-[family-name:var(--font/font-family)]",
        "text-[14px] leading-[18px]",
        "tracking-[var(--font/font-letterSpacing-14)]",
        // Variant
        variant === "primary" && [
          "bg-[var(--fill/fill-global-primary)]",
          "text-[color:var(--inverse/inverse-global-default)]",
          "font-[var(--font/font-weight-medium)]",
          "px-[14px] py-[6px]",
        ],
        variant === "secondary" && [
          "bg-[var(--fill/fill-subtle-neutral)]",
          "text-[color:var(--text/text-primary)]",
          "font-[var(--font/font-weight-regular)]",
          "px-[14px] py-[6px]",
        ],
        variant === "tertiary" && [
          "text-[color:var(--text/text-primary)]",
          "font-[var(--font/font-weight-regular)]",
          "px-[8px] py-[6px]",
        ],
        // State
        state === "disabled" && "opacity-50 pointer-events-none",
        className
      )}
      {...props}
    />
  );
}
```

---

## 7. Sticker Sheet Common Node ID Quick Reference

The following IDs can be used with `get_design_context` to quickly retrieve component details:

| Component | Light Mode Node ID | Dark Mode Node ID |
|-----------|-------------------|-------------------|
| **Column styles** | `194458:32745` | — |
| Basic button (Primary) | `194458:33613` | `194458:41679` |
| Basic button (Secondary) | `194458:33614` | `194458:41680` |
| Icon button | `194458:33582` | `194458:41648` |
| Text input | `194458:33653` | `194458:41719` |
| Select input | `194458:33655` | `194458:41721` |
| Tab bar (32px) | `194458:33611` | `194458:41677` |
| Segmented control | `194458:33591` | `194458:41657` |
| Banner | `194458:33670` | `194458:41736` |
| Notification | `194458:33604` | `194458:41670` |
| Dialog | `194458:33741` | `194458:41807` |
| Accordion | `194458:33747` | `194458:41813` |
| Avatar | `194458:33698` | `194458:41764` |
| Slider | `194458:33636` | `194458:41702` |
| Link | `194458:33576` | `194458:41642` |
| Checkbox group | `194458:33693` | `194458:41759` |
| Radio group | `194458:33692` | `194458:41758` |

---

## 8. Deprecated Components

The following components are marked as Deprecated — **do not use**:

- Toggle button group → Use standalone Toggle button instead
- Info popover button → Use Info button + Popover combination instead
- Base: checkbox (legacy) → Use new Checkbox component
- List item - Parts (legacy) → Use new Table cell instead
- List item slot element (legacy)
- Base: Swap instance

---

## 9. Quick Reference

### Figma MCP Parameter Quick Reference

| Parameter | Value |
|-----------|-------|
| fileKey | `OWKBE2BJBBanezKhapWx2Y` |
| Sticker Sheet nodeId | `87965:45200` |
| Prism 2.5 libraryKey | `lk-6ee1714a4c349337e72ad8b4da7dec8c657b1ac90c7009476d4ed3162a9551ab487734fd41432129d713b0ef68fb096ee4a0e5d6f005c23514a81274fd0946b6` |
| ADS Tokens libraryKey | `lk-83c7074d942e1b21eecc5ed91729a6823ce710b8c8cea69b158b58c3366c7b0404c64c2ea9e95f96b8637a218261339f2ab23b2fe9ecdffdb6c6ed8325038646` |

### Core Values Quick Reference

| Property | Value |
|----------|-------|
| Base font size | 14px |
| Title font size | 20px |
| Base line height | 18px (body) / 20px (paragraph) / 24px (title) |
| Letter spacing 14px | -0.15px |
| Letter spacing 16px | -0.31px |
| Letter spacing 20px | -0.45px |
| Font family | SF Pro |
| Body font weight | Regular (400) |
| Button font weight | Medium (500) |
| Emphasis font weight | Semibold (590) |
| Title font weight | Bold (700) |
| Base spacing unit | 4px |
| Button padding | 14px / 8px (Ghost) |
| Input padding | 12px horizontal |
| Component min height | 32px |
| Dialog padding | 32px |
| Divider height | 1px |
| Brand primary color | #0d6bde |
| Emphasized brand text color | #2057b1 |
| Strong text color | #222325 |
| Secondary text color | #686f79 |
| Border color (subtle) | #dfe3e8 |
| Border color (strong) | #555b62 |
| Input border color | #c1c6ce |
| Secondary button background | #f1f4f6 |
| Darker neutral background | #f1f4f6 |
| Banner background | #f2f8ff |
| Shadow base color | rgba(0,0,0,0.08) |
| Grid Gutter (1–2 columns) | 16px |
| Grid Gutter (3+ columns) | 24px |
| Grid Margin (1 column) | 16px |
| Grid Margin (2+ columns) | 32px |

---

---

## 10. Zoom Admin Portal — Page Layout & Interaction Specifications

> **Figma Source File**: [Design.md — Best practices](https://www.figma.com/design/eQBlSC1E4pbHJA5FCElUHv/Design.md?node-id=1-130291)
> **File Key**: `eQBlSC1E4pbHJA5FCElUHv`
> **Section**: `Best practices` (node-id: `1:130291`)

This chapter serves as the complete layout, navigation, and page pattern reference for the Zoom Admin Portal. **All design prototypes generated for the Admin Portal must follow this specification** to ensure visual and interaction consistency with the actual Zoom product.

### 10.1 Overall Page Structure

The Admin Portal standard viewport is **1920 × 1080px**, using a classic three-column structure with a fixed top bar + sidebar navigation + main content area.

```
┌─────────────────────────────────────────────────────────────────┐
│  Standalone Product Navigation (Top Bar)          h: 64px       │
├────────┬────────┬───────────────────────────────────────────────┤
│  1st   │  2nd   │                                               │
│  Nav   │  Nav   │         Main Content Area                     │
│        │        │                                               │
│ 280px  │ 220px  │         (1920 - sidebar)px                    │
│  or    │        │                                               │
│ 56px   │        │                                               │
│(collapsed)│     │                                               │
├────────┴────────┴───────────────────────────────────────────────┤
```

**Top Navigation Bar (Top Bar)**:
- Width: Full width `1920px`
- Height: `64px`
- Content: Zoom Logo + "Admin" label | Main nav links (Products, Solutions, Pricing) | "Try new experience" Toggle | "Upgrade to pro" Primary Button | Grid icon | User Avatar
- Background: `white`, with `1px` `border-subtle-neutral` bottom divider

### 10.2 Navigation System — Three-Level Hierarchy

The Admin Portal uses three-level navigation: 1st (main categories) → 2nd (sub-categories) → 3rd (specific feature pages, i.e., anchors/tabs in the content area). The sidebar has two states: **expanded mode** and **collapsed mode**.

#### Mode A: Expanded Sidebar (1st + 2nd Displayed Simultaneously)

Applicable scenario: When the user is browsing or switching between first/second-level navigation categories.

```
┌──────────────────────┬─────────────────────┬─────────────────────────┐
│   1st Level Nav      │   2nd Level Nav     │                         │
│   w: 280px           │   w: 220px          │    Content Area         │
│                      │                     │    starts at x=500      │
│   ● Setup guide      │   Category header   │                         │
│   ● Dashboard        │   ● Item 1          │                         │
│   ● Account mgmt     │   ● Item 2          │                         │
│   ● Users/Groups     │   ● Item 3 ●(sel)   │                         │
│   ● Settings   →     │   ● Item 4          │                         │
│   ● Security         │   ● ...             │                         │
│   ● Content mgmt     │                     │                         │
│   ● Configure   →    │                     │                         │
│   ● Reports          │                     │                         │
│   ● Plans & billing  │                     │                         │
│   ● Customer mgmt    │                     │                         │
│   ● Subaccount mgmt  │                     │                         │
└──────────────────────┴─────────────────────┴─────────────────────────┘
 Total sidebar: 500px
```

| Property | 1st Level Nav | 2nd Level Nav |
|----------|--------------|---------------|
| Width | `280px` | `220px` |
| Start Y | `64px` (directly below Top Bar) | `64px` |
| Background | `bg-default` (white) | `bg-default` (white) |
| Separator | Right side `1px` `border-subtle-neutral` vertical line | Right side `1px` `border-subtle-neutral` vertical line |
| Item height | `32px` | `32px` |
| Item padding | Horizontal `16px`, vertically centered | Horizontal `16px`, vertically centered |
| Icon size | `16 × 16px` | `16 × 16px` |
| Icon-text gap | `8px` | `8px` |
| Font | `body-1` (14px, Regular) | `body-1` (14px, Regular) |
| Default text color | `text-stronger-neutral` (#222325) | `text-stronger-neutral` (#222325) |
| Selected text color | `text-primary` (#0d6bde) | `text-primary` (#0d6bde) |
| Selected background | `fill-subtler-primary` (#f2f8ff) + border-radius `8px` | `fill-subtler-primary` (#f2f8ff) + border-radius `8px` |
| Hover background | `fill-subtler-neutral` (#f7f9fa) | `fill-subtler-neutral` (#f7f9fa) |
| Submenu indicator | Right side `→` arrow icon | — |
| Category title | — | Displayed at top, `text-neutral` (#686f79), `body-1` |

#### Mode B: Collapsed Sidebar (icon-only 1st + 2nd)

Applicable scenario: When the user has selected a secondary category and entered a specific feature page to view content. The 1st Level collapses to an icon-only bar, giving more space to the content area.

```
┌──────┬─────────────────────┬──────────────────────────────────────┐
│ 1st  │   2nd Level Nav     │                                      │
│ 56px │   w: 220px          │    Content Area                      │
│      │                     │    starts at x=276                   │
│  ◉   │   ← Category title  │                                      │
│  ◉   │   ● Item 1          │                                      │
│  ◉   │   ● Item 2          │                                      │
│  ◉●  │   ● Item 3 ●(sel)   │                                      │
│  ◉   │   ● Item 4          │                                      │
│  ◉   │   ● ...             │                                      │
│  ◉   │                     │                                      │
└──────┴─────────────────────┴──────────────────────────────────────┘
 Total sidebar: 276px
```

| Property | Collapsed 1st Level | 2nd Level Nav |
|----------|--------------------|---------------|
| Width | `56px` | `220px` |
| Icon | `32 × 32px` area, icon `16 × 16px` centered | Same as Mode A |
| Default icon color | `icon-neutral` (gray) | — |
| Selected icon color | `icon-primary` (blue) | — |
| Hover background | Border-radius `8px`, `fill-subtler-neutral` | — |
| 2nd title bar | — | Top: `← back arrow` + category name, `text-stronger-neutral` |

**Total Sidebar Width Quick Reference**:
| State | Total Width | Content Area Start X |
|-------|------------|---------------------|
| Expanded (1st 280 + 2nd 220) | `500px` | `500px` |
| Collapsed (1st 56 + 2nd 220) | `276px` | `276px` |

### 10.3 Main Content Area General Specifications

| Property | Value | Description |
|----------|-------|-------------|
| Left margin (from sidebar) | `32px` | Content area distance from left sidebar edge |
| Right margin | `32px` | Content area distance from right viewport edge |
| Top margin | `32px` | Content area distance from Top Bar bottom (i.e., from y=64) |
| Content area max width | `1580px` (collapsed sidebar) / `1356px` (expanded sidebar) | Adapts automatically to sidebar state |
| Background | `bg-default` (white) | Same background as sidebar, no color difference |

### 10.4 Page Pattern A: Settings Page (Settings/Toggle List)

Settings-type pages are the most common page pattern in the Admin Portal, used for toggle configurations of various product features.

```
┌─ Sidebar ─┬─────────────────────────────────────────────────────┐
│            │  [32px margin-top]                                   │
│            │  Page Title (22-24px, Bold)                          │
│            │  [16px gap]                                         │
│            │  ┌─ Search Input ─────────────┐  (360×32px)        │
│            │  └────────────────────────────┘                     │
│            │  [16px gap]                                         │
│            │  ┌─ Anchor ─┐  ┌─ Settings Content ─────────────┐  │
│            │  │ ● General │  │  Section Title "General"       │  │
│            │  │   AI Comp │  │  [8px gap]                     │  │
│            │  │           │  │  ┌─ Setting Card ──────────┐   │  │
│            │  │  200px    │  │  │ Label            Toggle │   │  │
│            │  │           │  │  │ Description (optional)  │   │  │
│            │  │           │  │  └────────────────────────┘   │  │
│            │  │           │  │  [24px gap between items]      │  │
│            │  │           │  │  ┌─ Setting Card ──────────┐   │  │
│            │  │           │  │  │ Label            Toggle │   │  │
│            │  │           │  │  └────────────────────────┘   │  │
│            │  └───────────┘  └────────────────────────────────┘  │
│            │   ← 24px gap →                                      │
└────────────┴─────────────────────────────────────────────────────┘
```

#### Page Title Area

| Property | Value |
|----------|-------|
| Title font | `title-1` approx 22-24px, Bold (700) |
| Title color | `text-stronger-neutral` (#222325) |
| Title height | `28px` |
| Title top distance | `32px` (from Top Bar bottom) |

#### Search Input

| Property | Value |
|----------|-------|
| Size | `360px × 32px` |
| Position | Below title, gap `16px` |
| Style | Standard Search input component |
| Placeholder | "Search settings" |

#### Anchor Navigation (Left-side Anchor)

| Property | Value |
|----------|-------|
| Width | `200px` |
| Item height | `30px` |
| Font | `body-1` (14px, Regular) |
| Default text color | `text-neutral` (#686f79) |
| Selected text color | `text-primary` (#0d6bde) |
| Selected indicator | Left side `2px` wide `fill-primary` (#0d6bde) vertical bar |
| Gap from content area | `24px` |

#### Settings Content Area

| Property | Value |
|----------|-------|
| Width | `1356px` (remaining space after Anchor width 200px + gap 24px) |
| Section Title | `title-2` approx 20-24px, Bold, `text-stronger-neutral` |
| Section-to-content gap | `40px` (Title 32px + 8px gap) |
| Content area inner padding | Left `24px`, top `24px` |

#### Setting Item

| Type | Structure | Height |
|------|-----------|--------|
| Simple toggle | Label + Toggle | `20px` |
| Toggle with description | Label + Description + Toggle | `60-78px` |
| With sub-options | Label + Toggle + Radio group (indented) | Variable |

```
┌───────────────────────────────────────────────────────────────┐
│ [24px pl]                                                      │
│  Setting label text (14px, Regular, text-stronger-neutral)     │
│  Description text (14px, Regular, text-neutral, max-w: 524px) │
│                                              Toggle (36×20px) │
│ [24px gap to next item]                      ← right-aligned x=1272  │
└───────────────────────────────────────────────────────────────┘
```

| Property | Value |
|----------|-------|
| Item container width | `1308px` (1356 - 24×2 padding) |
| Label font | `body-1` (14px, Regular), `text-stronger-neutral` |
| Label height | `20px` (line-height) |
| Description font | `body-1` (14px, Regular), `text-neutral` (#686f79) |
| Description max width | `524px` |
| Description-Label gap | `4px` (wrapped in a 24px height gap container) |
| Toggle position | Right side of container, x offset `1272px` |
| Toggle size | `36 × 20px` |
| Item-to-item vertical gap | `24px` (between simple items) / `24px` (between compound items) |
| Radio Group indent | Same `24px` left padding as setting item |

### 10.5 Page Pattern B: Data Table Page (Data List / Bulk Management)

Data Table pages are used to display list data, such as user management, bulk operation history, etc.

```
┌─ Sidebar ─┬─────────────────────────────────────────────────────┐
│            │  ┌─ Page Header ──────────────────────────────────┐ │
│            │  │  [32px pt, 32px pl]                             │ │
│            │  │  Page Title (22-24px, Bold)                     │ │
│            │  │  Description (14px, text-neutral)               │ │
│            │  │                                    h: 104px     │ │
│            │  └────────────────────────────────────────────────┘ │
│            │  ┌─ Tab Bar ──────────────────────────────────────┐ │
│            │  │  [32px pl]  History | Templates    h: 62px     │ │
│            │  └────────────────────────────────────────────────┘ │
│            │  ┌─ Action Bar ───────────────────────────────────┐ │
│            │  │  [Search 360×32]              [Action Button]  │ │
│            │  │  [32px pl]                    [32px pr] h:64px │ │
│            │  └────────────────────────────────────────────────┘ │
│            │  ┌─ Data Table ───────────────────────────────────┐ │
│            │  │  [32px pl]                                     │ │
│            │  │  Col Header | Col Header | ... |   h: 36px     │ │
│            │  │  ─────────────────────────────────             │ │
│            │  │  Cell       | Cell       | ... |   h: 52px     │ │
│            │  │  Cell       | Cell       | ... |   h: 52px     │ │
│            │  └────────────────────────────────────────────────┘ │
└────────────┴─────────────────────────────────────────────────────┘
```

#### Page Header

| Property | Value |
|----------|-------|
| Container height | `104px` |
| Container width | Content area full width (1920 - sidebar) |
| Padding | `32px` top, `32px` left |
| Title font | `title-1` approx 22-24px, Bold (700) |
| Title color | `text-stronger-neutral` |
| Title height | `32px` |
| Description font | `body-1` (14px, Regular) |
| Description color | `text-neutral` (#686f79) |
| Description height | `20px` |
| Title-description gap | `4px` |

#### Tab Bar

| Property | Value |
|----------|-------|
| Container height | `62px` |
| Tab inner padding | `9px` top, `32px` left |
| Tab component | Standard Prism Tab bar, height `44px` |
| Tab width | Content area width - left/right padding (`1580px`) |
| Bottom border | `1px` `border-subtle-neutral` |

#### Action Bar

| Property | Value |
|----------|-------|
| Container height | `64px` |
| Padding | `16px` top/bottom, `32px` left/right |
| Search input | Left-aligned, `360 × 32px` |
| Action button | Right-aligned, Primary button style |

#### Data Table

| Property | Value |
|----------|-------|
| Table padding | `32px` left/right, `16px` top |
| Table width | `1580px` (content area width - 64px left/right padding) |
| Column Header height | `36px` |
| Column Header text | `body-1` (14px, Medium 500), `text-neutral` |
| Column Header bottom line | `1px` `border-strong-neutral` |
| Table Cell height | `52px` |
| Table Cell text | `body-1` (14px, Regular), `text-stronger-neutral` |
| Table Row bottom line | `1px` `border-subtle-neutral` |
| Status label | Inline colored dot + text, e.g., "● Imported" (green) |
| Action link | `text-primary` (#0d6bde), e.g., "View" |
| More actions | Row-end `...` ellipsis icon button |

### 10.6 Admin Portal Key Dimensions Quick Reference

| Property | Value |
|----------|-------|
| Viewport width | `1920px` |
| Viewport height | `1080px` |
| Top Bar height | `64px` |
| 1st Nav expanded width | `280px` |
| 1st Nav collapsed width | `56px` |
| 2nd Nav width | `220px` |
| Total sidebar width (expanded) | `500px` |
| Total sidebar width (collapsed) | `276px` |
| Content area left margin | `32px` |
| Content area right margin | `32px` |
| Content area top margin | `32px` |
| Content area max width (collapsed) | `1580px` |
| Content area max width (expanded) | `1356px` |
| Standard Search input | `360 × 32px` |
| Tab bar container height | `62px` |
| Action bar height | `64px` |
| Page header height | `104px` |
| Table header row height | `36px` |
| Table cell row height | `52px` |
| Setting item gap | `24px` |
| Setting Toggle size | `36 × 20px` |
| Anchor navigation width | `200px` |
| Anchor-content gap | `24px` |

### 10.7 Admin Portal Navigation Item List

Below is the actual navigation structure in the Admin Portal. Prototypes must use these real category names and hierarchy relationships.

#### 1st Level (Admin Center) — Expanded Mode

| Icon | Name | Type | Has 2nd Nav |
|------|------|------|-------------|
| 📋 | Setup guide | Direct link | ✗ |
| 📊 | Dashboard | Direct link | ✗ |
| 🏢 | Account management | Expandable | ✓ |
| 👥 | Users, Groups & Roles | Expandable | ✓ |
| ⚙️ | Settings | Expandable | ✓ |
| 🔒 | Security and Privacy | Expandable | ✓ |
| 📁 | Content management | Expandable | ✓ |
| 🔧 | Configure products | Expandable → | ✓ |
| 📈 | Reports | Expandable | ✓ |
| 💳 | Plans and billing | Expandable | ✓ |
| 🏪 | Customer management | Expandable | ✓ |
| 🏗️ | Subaccount management | Expandable | ✓ |

#### 2nd Level — Settings & Policies

AI Companion, General, Meetings, Webinars, Recording, Mail and calendar, Audio conferencing, Zoom Phone, Zoom apps, Whiteboard, Notes, Docs, Paper, Sheet, Present, Tasks, Hub, Team Chat, Workspace, Revenue Accelerator

#### 2nd Level — Product Configuration

AI Studio, Contact Center, Devices, Frontline, Mail and calendar, Numbers, Phone system, Rooms, Team Chat, Workspace, Workforce, Scheduler, Zoom Mesh, Zoom Node, Huddle, Hybrid

### 10.8 Code Generation Rules — Admin Portal Specific

When generating design prototypes for the Admin Portal, in addition to following the general rules in §6.2, the following rules must also be observed:

1. **Must include the complete page shell** — Every prototype must include the full structure of Top Bar + sidebar + main content area; do not output isolated content area fragments
2. **Sidebar state selection** — Settings/Configure detail pages use the **collapsed sidebar** (56+220=276px); navigation browsing pages use the **expanded sidebar** (280+220=500px)
3. **Content area width adaptation** — Content area width = `viewport width - sidebar width - left margin(32px) - right margin(32px)`, must not be hardcoded
4. **Settings pages must include Anchor navigation** — When there are more than one section, the left-side Anchor nav must be displayed, width `200px`, gap from content `24px`
5. **Toggle right-aligned** — The Toggle in setting items must always be right-aligned, never left-aligned or centered
6. **Description text width constraint** — Setting item description text max width `524px` to prevent long lines from affecting readability
7. **Data Table pages follow layered structure** — Header → Tab → Action bar → Table, each layer uses an independent container, horizontal padding uniformly `32px`
8. **Table header and body visual distinction** — Column header uses Medium font weight + `border-strong-neutral` bottom line; Cell uses Regular font weight + `border-subtle-neutral` bottom line
9. **Real navigation names** — Sidebar navigation items must use the real names listed in §10.7, no fabricated names
10. **Page title** — Every feature page must have a clear title, positioned at the top-left of the content area, using Bold large font

### 10.9 React Page Skeleton Template — Admin Portal

```tsx
type AdminPageProps = {
  sidebarMode: "expanded" | "collapsed";
  activePrimaryNav: string;
  activeSecondaryNav: string;
  children: React.ReactNode;
};

function AdminPortalLayout({
  sidebarMode = "collapsed",
  activePrimaryNav,
  activeSecondaryNav,
  children,
}: AdminPageProps) {
  const sidebarWidth = sidebarMode === "expanded" ? 500 : 276;

  return (
    <div className="w-[1920px] h-[1080px] bg-[var(--background/bg-default)] overflow-hidden">
      {/* Top Bar */}
      <header className="h-[64px] w-full flex items-center justify-between px-[16px] border-b border-[var(--border/border-subtle-neutral)]">
        {/* Logo + Nav + Actions */}
      </header>

      <div className="flex h-[calc(100%-64px)]">
        {/* 1st Level Nav */}
        {sidebarMode === "expanded" ? (
          <nav className="w-[280px] h-full border-r border-[var(--border/border-subtle-neutral)] py-[8px]">
            {/* Admin Center menu items */}
          </nav>
        ) : (
          <nav className="w-[56px] h-full border-r border-[var(--border/border-subtle-neutral)] py-[8px] flex flex-col items-center">
            {/* Icon-only items */}
          </nav>
        )}

        {/* 2nd Level Nav */}
        <nav className="w-[220px] h-full border-r border-[var(--border/border-subtle-neutral)] py-[8px]">
          {/* Category title + submenu items */}
        </nav>

        {/* Main Content */}
        <main className="flex-1 overflow-y-auto">
          <div className="px-[32px] pt-[32px]">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
```

**Settings Page Content Template**:

```tsx
function SettingsPageContent({
  pageTitle,
  anchors,
  activeAnchor,
  settings,
}: SettingsContentProps) {
  return (
    <>
      <h1 className="text-[22px] font-[var(--font/font-weight-bold)] text-[color:var(--text/text-stronger-neutral)] leading-[28px]">
        {pageTitle}
      </h1>
      <div className="mt-[16px]">
        <SearchInput placeholder="Search settings" className="w-[360px]" />
      </div>
      <div className="flex mt-[16px] gap-[24px]">
        {/* Anchor Navigation */}
        <div className="w-[200px] flex-shrink-0">
          {anchors.map((anchor) => (
            <AnchorItem
              key={anchor.id}
              label={anchor.label}
              isActive={anchor.id === activeAnchor}
            />
          ))}
        </div>
        {/* Settings Content */}
        <div className="flex-1">
          <h2 className="text-[20px] font-[var(--font/font-weight-bold)] text-[color:var(--text/text-stronger-neutral)] leading-[24px]">
            {activeAnchor}
          </h2>
          <div className="mt-[40px] bg-[var(--fill/fill-default)] rounded-[0px] p-[24px]">
            {settings.map((setting) => (
              <SettingItem key={setting.id} {...setting} />
            ))}
          </div>
        </div>
      </div>
    </>
  );
}
```

**Data Table Page Content Template**:

```tsx
function DataTablePageContent({
  pageTitle,
  description,
  tabs,
  activeTab,
  columns,
  rows,
  actionLabel,
}: DataTableContentProps) {
  return (
    <>
      {/* Page Header */}
      <div className="py-[32px] px-[32px]">
        <h1 className="text-[22px] font-[var(--font/font-weight-bold)] text-[color:var(--text/text-stronger-neutral)] leading-[32px]">
          {pageTitle}
        </h1>
        {description && (
          <p className="mt-[4px] text-[14px] text-[color:var(--text/text-neutral)] leading-[20px]">
            {description}
          </p>
        )}
      </div>

      {/* Tab Bar */}
      <div className="h-[62px] px-[32px] pt-[9px] border-b border-[var(--border/border-subtle-neutral)]">
        <TabBar tabs={tabs} activeTab={activeTab} />
      </div>

      {/* Action Bar */}
      <div className="h-[64px] px-[32px] py-[16px] flex items-center justify-between">
        <SearchInput className="w-[360px]" />
        <PrimaryButton>{actionLabel}</PrimaryButton>
      </div>

      {/* Data Table */}
      <div className="px-[32px]">
        <table className="w-full">
          <thead>
            <tr className="h-[36px] border-b-[2px] border-[var(--border/border-strong-neutral)]">
              {columns.map((col) => (
                <th key={col.key} className="text-left text-[14px] font-[var(--font/font-weight-medium)] text-[color:var(--text/text-neutral)]">
                  {col.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.id} className="h-[52px] border-b border-[var(--border/border-subtle-neutral)]">
                {columns.map((col) => (
                  <td key={col.key} className="text-[14px] text-[color:var(--text/text-stronger-neutral)]">
                    {row[col.key]}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}
```

### 10.10 Figma MCP Parameter Quick Reference — Admin Portal

| Parameter | Value |
|-----------|-------|
| fileKey | `eQBlSC1E4pbHJA5FCElUHv` |
| Best practices section | `1:130291` |
| Settings - Second menu | `2:19794` |
| Settings - Zoom Phone | `2:48621` |
| Configure product - Second menu | `2:19024` |
| Configure product - Bulk management | `2:46779` |
| Navigation section | `1:39473` |

---

*Last updated: 2025-03-25 — Based on actual component styles extracted from the Figma Sticker Sheet (node-id: 87965-45200) in Light/Dark mode, Column Styles (node-id: 194458-32745) grid system specification supplement, and Design.md (fileKey: eQBlSC1E4pbHJA5FCElUHv, node-id: 1-130291) Admin Portal Best Practices page layout specification supplement*
