# Rules — UI-CRAFT

Full rule statements with citations, plain-language impact, and extended discussion. Referenced from `SKILL.md` §5 Rule Summaries. Loaded on demand when deep rule application is needed.

Seven rules covering UI/UX craft for AI-assisted development — anti-AI-slop discipline. Anchored in Apple Human Interface Guidelines, Material Design 3, Nielsen's 10 Usability Heuristics, and WCAG 2.2 (cross-reference from DESIGN). Anti-AI-slop discipline is TGF synthesis acknowledged honestly per `DEC-2026-05-17-004` — observable 2024-2026 phenomenon not yet codified in standards.

Citation discipline: APPLE-HIG and MATERIAL-3 cited at foundation level (their main docs are SPA-rendered and not fetchable via WebFetch — the source authority is real and publicly published; verbatim sub-quote isn't available via current tooling). Similar to paywalled-source pattern under `DEC-2026-05-17-004` Clause 5 — cite by reference, not by fabricated sub-quote.

---

## Rule 5.1: Build a Design System, Don't Accumulate Defaults

**Statement:** Color palette, typography scale, spacing scale, and component shapes are decided early as a coherent system and used consistently across the product. The system is encoded in design tokens (Tailwind theme config, CSS variables, design-system primitives) — not as ad-hoc class accumulation across components. Default framework classes accumulating across components signal "AI generated this with defaults," not "this was designed."

**Citation:** `APPLE-HIG Foundations (Color, Typography, Layout)` + `MATERIAL-3 Foundations (color system, type scale, shape, elevation)` + `TGF-SYNTHESIS on anti-AI-slop discipline`. Apple HIG and Material 3 each document foundational design-system structure at the principle level — APPLE-HIG's "Foundations" section and MATERIAL-3's "Foundations" articulate the discipline of building from a system rather than from defaults.

**Plain-language impact:** Without an intentional design system, UI accumulates the visual signal of "this was thrown together." Buttons use `rounded-md` in some files and `rounded-lg` in others; some use `bg-blue-500`, others `bg-blue-600`. Each individual choice looks fine in isolation; the accumulation across the product looks random. Users don't articulate the failure as "inconsistent design tokens" — they perceive it as "this product feels unpolished." With an intentional system, even a small one, the product feels designed because it IS designed.

**Extended discussion:** A design system at minimum is:

- **A color palette.** Primary brand color + 1-2 accents + neutral grays (typically 5-9 steps from white to black) + semantic states (success/warning/error/info). Encoded as design tokens.
- **A type scale.** 4-6 sizes with clear purposes (display, h1, h2, body, caption). Encoded with rem/px values and intended uses.
- **A spacing scale.** 4px or 8px base with multiples (e.g., 4/8/12/16/24/32/48/64). Used consistently for margin/padding/gap throughout.
- **Component shapes.** Border radius decided once (e.g., 4px buttons, 8px cards, 16px modals — or a single radius value used consistently). Border weights decided once. Shadow scale (no shadow → small → medium → large) decided once.

A design system does NOT require a comprehensive design system like Material Design — for early-stage products, a minimum-viable design system (10-15 design tokens total) is sufficient. The discipline is having a system, not having a comprehensive one.

For AI-assisted development specifically: AI defaults to the modal Tailwind/Bootstrap pattern because those patterns are over-represented in training data. The defense is making design tokens override the defaults at the source. If `text-primary-500` is what AI uses (because the design system established it), the output is on-system; if AI defaults to `text-blue-500`, the output is off-system. Define the tokens, AI inherits them.

**Related anti-patterns:** AP-1 (default Tailwind everywhere), AP-7 (stock-aesthetic accumulation) (see `anti-patterns.md`)

---

## Rule 5.2: Restrained Color Palette

**Statement:** Color palette stays disciplined: approximately 3-5 colors total — primary brand color + 1-2 accents + neutral grays (5-9 steps) + semantic states (success/warning/error/info). When more colors are needed (data visualization, illustrative graphics, brand expression in marketing surfaces), they are added consciously and named in the design tokens, not picked ad-hoc from a color picker.

**Citation:** `MATERIAL-3 Color System` (the structured color-role approach — primary, secondary, tertiary, surface, error — operationalizes restrained-palette thinking) + `TGF-SYNTHESIS on anti-AI-slop`.

**Plain-language impact:** "14 different blues" across a single product screen is the immediately-recognizable signal of palette accumulated through ad-hoc choices. Each `bg-blue-500`, `text-blue-600`, `border-blue-400`, `hover:bg-blue-700` was a sensible local choice but collectively reads as random. Users perceive this as the product looking generic and unpolished. A restrained palette (one blue used consistently across roles, with the variations being intentional shades from a defined scale) reads as designed.

**Extended discussion:** Restrained doesn't mean monochromatic. Stripe's site uses purple, blue, and accent colors deliberately. Vercel uses black + white + a single accent. Linear uses indigo + neutrals. The pattern across high-craft sites: a SMALL palette used with discipline, not a LARGE palette used randomly.

Common color-discipline mistakes:

- **Picking colors ad-hoc instead of from the palette.** Symptom: `text-blue-500` in one file, `text-blue-600` in another, with no system reason for the variation.
- **Adding "just one more" color.** Each addition feels small; the accumulation defeats the system.
- **Using semantic colors decoratively.** Red is for errors, green is for success. Using red for "important call-to-action" muddles the semantic system.
- **Inconsistent saturation.** A muted gray scale paired with saturated brand colors works; mixing muted and saturated freely doesn't.

For data visualization specifically, palettes expand legitimately — but the data-viz palette is its own system (e.g., a categorical-color scheme with 8-12 colors designed to be distinguishable, paired with accessibility-conscious choices) rather than a free-for-all.

For AI-assisted development: AI tends to use whatever color seems contextually appropriate per call, without checking whether the chosen color belongs to a coherent palette. The cumulative effect is color sprawl that compounds across components. Defense: design tokens that constrain choices ("only use colors from `theme.colors`") combined with code review checking for off-palette additions.

**Related anti-patterns:** AP-2 (color sprawl) (see `anti-patterns.md`)

---

## Rule 5.3: Typography Hierarchy Is Structural, Not Decorative

**Statement:** Typography hierarchy is established as a type scale with 4-6 sizes with clear purposes (display, h1, h2, body, caption, small) and intentional weight contrast. Hierarchy is communicated through size + weight + color combination — not through any one of these in isolation. Custom or carefully-chosen typefaces over the system default where the brand earns it; system defaults are fine when the brand is utilitarian.

**Citation:** `APPLE-HIG Typography` (Apple documents text styles like Title 1, Title 2, Headline, Body, Caption with explicit hierarchical purposes — operationalizes structural typography) + `MATERIAL-3 Typography (type scale: display, headline, title, body, label)` + `TGF-SYNTHESIS`.

**Plain-language impact:** Without typographic hierarchy, every text element competes equally for attention — nothing is important because everything is the same. Users have to read every line to find what matters. With clear hierarchy (display size for the one truly-important thing, body size for content, caption for metadata, weights differentiating headers from body), scanning works — users find what they need in seconds because the hierarchy guides their eyes.

**Extended discussion:** A type scale at minimum:

- **Display (60-80px).** For one-of-the-page hero text. Rare; used for impact.
- **H1 (32-48px).** Page-level heading. One per page (or per major section).
- **H2 (24-32px).** Section heading. Multiple per page.
- **H3 (20-24px).** Sub-section heading. Used as needed.
- **Body (16-18px).** Default reading size.
- **Small/Caption (12-14px).** Metadata, labels, tertiary information.

Weight contrast: typically body uses regular (400), headers use semibold/bold (600-700), display can use lighter weights (300-400) at large sizes for editorial feel. The contrast between body and headers is the hierarchy signal.

Common typography failures:

- **Mid-range sizes that blur hierarchy.** Using `text-lg` (18px) for both "slightly larger body" and "smaller heading" muddles the structural role.
- **Weight monotone.** Everything `font-medium` or everything `font-bold` removes the contrast that makes hierarchy work.
- **Custom typeface without commitment.** Using a custom typeface for headers but system font for body looks accidental; commit to one typeface family or use system fonts consistently.
- **Italics for emphasis instead of weight.** Italics work for *titles of works* or specific semantic emphasis; using them for general emphasis is weak typography.

For AI-assisted development: AI defaults to a small set of sizes (`text-base`, `text-lg`, `text-xl`, `text-2xl`) without considering hierarchy across the product. Defense: document the type scale in the project's style guide / theme config; review components against the documented scale.

**Related anti-patterns:** AP-3 (typography monotone) (see `anti-patterns.md`)

---

## Rule 5.4: Spacing Rhythm via Consistent Scale

**Statement:** Spacing (margin, padding, gap) follows a consistent scale — typically 4px or 8px base with multiples: 4/8/12/16/24/32/48/64. Vertical rhythm is intentional: related elements use smaller spacing; section breaks use larger spacing. Default-margin everything (`p-4 m-4 gap-4` accumulating across components) signals absence of rhythm consideration.

**Citation:** `MATERIAL-3 Foundations (8dp grid)` — Material Design documents the 8dp base grid as the foundational spacing rhythm; `APPLE-HIG Layout` (Apple documents spacing in terms of safe areas and layout margins with consistent system-derived values) + `TGF-SYNTHESIS`.

**Plain-language impact:** Without spacing rhythm, layouts feel cramped or uniformly-spaced — both signals of "no intent." Cramped layouts (`p-2` everywhere) make content hard to read; uniformly-spaced layouts (`p-4` everywhere) provide no hierarchy. With rhythm, related elements feel grouped; unrelated elements feel separated; section breaks feel intentional.

**Extended discussion:** A spacing scale at minimum:

- **Micro (4-8px).** Spacing within tight groups (icon + label, button text + chevron).
- **Small (12-16px).** Spacing within related content (list items, form field + label).
- **Medium (24-32px).** Spacing between content groups (form sections, card content + actions).
- **Large (48-64px).** Spacing between major sections (page sections, hero + content).
- **Extra Large (96-128px).** Spacing for editorial-feeling whitespace (landing pages, marketing surfaces).

Vertical rhythm cuts across the scale: spacing-before of an h2 is larger than spacing-before of a paragraph; spacing-between paragraphs is consistent across the document; spacing-around a section is larger than spacing-within.

For Tailwind specifically: the default scale (`p-1, p-2, p-3, p-4, p-6, p-8, p-12, p-16, p-24`) maps reasonably to a 4px base with multiples. Use a subset consistently rather than all values randomly.

Common spacing failures:

- **All values are p-4.** Default applied everywhere; no rhythm.
- **Random scale choices.** `p-4` and `p-5` and `p-7` next to each other — these aren't multiples of any clean base.
- **Cramped layouts.** Everything `p-2 m-2`; nothing has room to breathe.
- **Same vertical and horizontal spacing.** Often horizontal spacing should be tighter than vertical spacing for readability.

For AI-assisted development: AI defaults to `p-4 m-4 gap-4` because those are common values in training data. Defense: design tokens / a documented spacing scale that constrains choices; review components against rhythm intent.

**Related anti-patterns:** AP-4 (default spacing accumulation) (see `anti-patterns.md`)

---

## Rule 5.5: Motion Is Communication, Not Decoration

**Statement:** Motion serves a purpose: **feedback** (the button knows you clicked it, the form knows you submitted it), **structure** (the modal arrives from somewhere logical, the page transition reveals the new context), or **status** (the spinner indicates work in progress, the progress bar shows advancement). Indiscriminate motion — every element fades-in on scroll, hover-translate on everything, animated gradients in static contexts — is noise that adds nothing and may actively harm users (especially those with vestibular disorders or motion sensitivity).

**Citation:** `APPLE-HIG Motion` (Apple's motion guidance emphasizes meaning and reduced-motion accessibility) + `NIELSEN-10 Heuristic #1 (Visibility of System Status)` — motion communicates system status; the heuristic operationalizes when motion earns its place; `WCAG 2.2 SC 2.3.3 (Animation from Interactions, Level AAA)` — gives users mechanisms to disable non-essential motion.

**Plain-language impact:** Indiscriminate motion makes products feel busy, scattered, and amateur. Users sensitive to motion experience nausea or vestibular discomfort from gratuitous animations. Performance suffers when too many elements animate simultaneously. Purposeful motion, by contrast, communicates: users see what's happening, what changed, what's loading. Restraint in motion (most of the page is still; the one element that animates carries the message) communicates more than total-page motion.

**Extended discussion:** Three categories of motion that earn their place:

- **Feedback.** Button states (subtle press animation), form validation (red shake on invalid), drag-and-drop (cursor follow + drop-zone highlight).
- **Structure.** Modal open/close (origin point + scale), page transitions (slide or fade with directional logic), menu reveal (slide from origin).
- **Status.** Loading spinner, progress bar advancement, skeleton screens during data fetch, optimistic UI feedback before server confirms.

Three categories of motion that usually don't:

- **Decorative entrance animations.** "Every element fades-in on scroll" adds noise; nothing communicated.
- **Animated gradients in static contexts.** Marketing landing pages may earn one signature animated element; product UI rarely needs animated gradients.
- **Hover-translate everywhere.** Cards that lift on hover is sometimes useful as feedback; applying it to every element loses the signal.

WCAG 2.2 SC 2.3.3 (Animation from Interactions) requires users to be able to disable non-essential animation. CSS `prefers-reduced-motion` is the technical mechanism; designing motion to respect this preference is accessibility-craft (also Rule 5.6 in DESIGN — accessibility is designed in).

For AI-assisted development: AI may add motion ("nice animations") without considering purpose. Asked for a landing page, AI adds fade-in-on-scroll to every section, animated-gradient backgrounds, hover effects on every card. Defense: explicit motion principle (motion communicates feedback, structure, or status) + review surfacing motion that doesn't fit any of those three categories.

**Related anti-patterns:** AP-5 (indiscriminate motion) (see `anti-patterns.md`)

---

## Rule 5.6: Designed States Across the Board

**Statement:** Every interactive element has all states considered and designed: **default**, **hover** (or `:focus-visible` on touch devices), **focus** (keyboard navigation visibility — designed ring, not browser default), **active** (during click/tap), **disabled** (visually distinct, accessibility-aware), **loading** (where async work happens), **error** (graceful, informative), **empty** (where collections might be empty — designed intent, not blank screen). Focus rings are designed as part of the brand, not the browser-default blue outline. Empty states have intent: they tell the user what to do, not just "no data."

**Citation:** `NIELSEN-10 Heuristic #1 (Visibility of System Status)` — states communicate system status; the heuristic operationalizes designed states as a usability requirement. `WCAG 2.2 SC 2.4.7 (Focus Visible)` — focus indicator must be visible (Level AA requirement). `APPLE-HIG Foundations` and `MATERIAL-3 States` — both document state design at the foundation level + `TGF-SYNTHESIS`.

**Plain-language impact:** Forgotten states are one of the most common signals of AI-generated UI. The default state is designed; everything else is browser/library default. Users see flash-of-default-focus-ring on tab navigation; disabled buttons look the same as enabled ones; loading states are missing (users wonder if their click registered); empty states are blank screens that signal "broken." Designing all states is the difference between a UI that handles every interaction gracefully and one that feels brittle.

**Extended discussion:** State-by-state discipline:

- **Default.** The starting state. Designed first.
- **Hover.** Subtle visual change (slight color shift, slight shadow change). On touch devices, `:hover` doesn't apply meaningfully; use `:focus-visible` patterns.
- **Focus.** Designed focus ring. **`outline-none` without replacement is a WCAG 2.2 SC 2.4.7 violation** — focus must be visible. The replacement is a designed ring (e.g., 2px solid in brand color with 2px offset).
- **Active.** During click/tap. Brief visual feedback (slight scale, slight darken).
- **Disabled.** Visually distinct (reduced opacity, removed shadow, color change). `aria-disabled` for assistive tech. NOT just lower opacity that fails contrast.
- **Loading.** Spinner, skeleton, progress indicator, or optimistic UI. Users need to see that their action registered.
- **Error.** Inline error messages with constructive guidance. Color (red) PLUS icon PLUS text — per `WCAG 2.2 SC 1.4.1` no color-only differentiation.
- **Empty.** "No items yet" with action prompt: "Add your first X." Empty states are onboarding moments.

For data-display components specifically (lists, tables, dashboards), empty/loading/error states are first-class — they appear before users have any data. AI tends to design "list with three sample items" first and forget the empty/loading/error states.

For AI-assisted development: prompts usually specify the default state ("a button that does X") and AI implements only that. Defense: state-design checklist applied at component creation time — every interactive element gets all 8 states designed before review.

**Related anti-patterns:** AP-6 (forgotten states) (see `anti-patterns.md`)

---

## Rule 5.7: Restraint Earns Trust

**Statement:** Saying NO to elements, colors, motions, and patterns that don't earn their place. Maximalism (everything animated, every color used, every effect applied, every section emphasized) signals lack of editing. Restraint signals intent. Cross-references DESIGN Rule 5.3 (simplest wins) applied at the visual layer.

**Citation:** `TGF-SYNTHESIS — grounded in observable high-craft pattern across Stripe, Vercel, Linear, Monogram, Kraken` and cross-reference to DESIGN Rule 5.3. No single authoritative source codifies "restraint as craft" at the rule level — but it's observable across every high-craft site as the unifying pattern: they ship LESS than they could; what ships is considered.

**Plain-language impact:** Maximalism reads as either inexperienced or insecure — "we couldn't decide what to emphasize, so we emphasized everything." Restraint reads as confident — "we chose what matters and edited out the rest." Users experience restraint as polish; they can't always articulate it, but they perceive it. The product feels considered.

**Extended discussion:** What restraint looks like in practice:

- **One animated hero element on a landing page, not five.** The single animation reads as deliberate signature; multiple animations compete and dilute.
- **One bold call-to-action per screen, not three competing ones.** Hierarchy of action is part of design discipline.
- **Whitespace that lets things breathe.** Generous spacing isn't waste; it's editing-out.
- **Color used sparingly for emphasis.** A landing page that's mostly neutral with one or two accent uses of brand color reads as confident; a landing page where every section is heavily colored reads as anxious.
- **Typography that serves content.** Not every word needs to be bigger; not every heading needs to be unique.

Stripe's site is restrained: most content is neutral; brand color appears at intentional accent points; motion is sparing and deliberate. Vercel similar: black/white dominant; accent colors at specific moments; motion serves transitions, not decoration. Linear: indigo + neutrals; almost no motion outside functional moments. The shared pattern across these high-craft sites: editing-down, not adding-on.

The opposite — maximalism — comes from a place of "we want users to see we put effort in." But effort signaled through accumulation reads as anxious. Effort signaled through restraint reads as confident. The user perceives the difference.

For AI-assisted development: AI optimizes for "thorough" — including every reasonable element, applying every available pattern. The default trend is toward maximalism. Defense: explicit restraint as a design principle; reviewing each addition for "does this earn its place?"; treating editing-down as part of the design pass, not as an afterthought.

**Related anti-patterns:** AP-7 (stock-aesthetic accumulation), AP-8 (maximalist accumulation) (see `anti-patterns.md`)

---
