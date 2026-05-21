---
# ─── Anthropic-native runtime fields (Claude Code honors these) ───
name: ui-craft
description: |
  UI/UX craft discipline for AI-assisted development — anti-AI-slop. Use when
  building UI or reviewing visual design: design systems (color/typography/
  spacing scales), considered motion, designed states across the board,
  restraint over maximalism. Pairs with DESIGN (decision discipline) as
  design's craft companion. Defends against the recognizable "AI-generated UI"
  aesthetic: Tailwind defaults everywhere, color sprawl, monotone typography,
  indiscriminate motion, forgotten states.
paths:
  - "**/*.tsx"
  - "**/*.jsx"
  - "**/*.vue"
  - "**/*.svelte"
  - "**/*.css"
  - "**/*.scss"
  - "**/tailwind.config.*"
  - "**/theme.*"

# ─── TGF-extension metadata (Phase 11 meta-skills read these; Claude Code ignores) ───
applies-when:
  paths-include:
    - "**/*.{tsx,jsx,vue,svelte,css,scss}"
    - "**/tailwind.config.*"
    - "**/theme.*"
  operations-include:
    - UI component creation or modification
    - color, typography, or spacing system definition
    - design token configuration
    - motion or animation implementation
    - state styling (hover, focus, active, disabled, loading, error, empty)
    - styling system selection or migration
  data-flows-include:
    - visual content rendering to user
disqualifying-when:
  - pure logic changes with no visual surface
  - documentation-only changes
  - backend-only modifications
  - debugging an established issue (use DEBUGGING)
sources:
  - Apple Human Interface Guidelines (developer.apple.com/design/human-interface-guidelines) — cited by reference (SPA-rendered; not directly fetchable via WebFetch but publicly published authoritative source)
  - Material Design 3 (m3.material.io) — cited by reference (same caveat)
  - Jakob Nielsen — 10 Usability Heuristics for User Interface Design (1994, refreshed; Nielsen Norman Group, nngroup.com/articles/ten-usability-heuristics/)
  - WCAG 2.2 (W3C Recommendation, 2023-10-05; updated 2024-12-12; verified 2026-05-20 in Phase 5 commit 3/7 DESIGN) — cross-reference for accessibility-as-craft
  - MITRE ATLAS v5.4.0 — AI design/output failure modes (verified Phase 2, 2026-05-17)
last-generated: 2026-05-20
refresh-recommended: 2027-05-20
self-evolution:
  anti-patterns-observed: []
  triggers-refined: []
  ai-failures-documented: []
---

# UI-CRAFT

> **Skill body ≤300 lines** (per `DEC-2026-05-19-007`). Principles, rule summaries, and navigation live here. Full content in reference files loaded on demand:
> - `rules.md` — full rules with citations
> - `anti-patterns.md` — full anti-pattern + canonical pattern pairs with concrete examples and high-craft reference site studies

<!-- SECTION: overview -->
## §1 Overview

UI-CRAFT governs the *craft* of executing UI/UX design — the visual and interaction discipline that separates polished intentional interfaces from recognizable "AI slop." It is an **activity skill** in TGF (loads on context per `CLAUDE.md` §9), not always-on. It activates when work touches the visible surface: components, styling systems, design tokens, motion, state design.

UI-CRAFT pairs with DESIGN (Phase 5 commit 3/8). DESIGN governs *decision discipline* about design (which approach, against which constraints, why). UI-CRAFT governs *craft discipline* in executing the design (which color value, which spacing, which motion timing, which states). The two are complementary: a project can have good decision discipline and poor craft (AI-slop UI built against sound architectural choices), or good craft and poor decision discipline (beautifully-rendered solution to the wrong problem). TGF wants both.

The skill exists to defend against an observable 2024-2026 phenomenon: AI-assisted UI development produces a recognizable aesthetic. Tailwind defaults (`rounded-2xl bg-blue-500 text-white`), color sprawl (14 different blues), monotone typography, default spacing, indiscriminate motion, forgotten states. The cost is not aesthetic taste — it's that AI-slop UI signals "this product was thrown together" and erodes user trust. The discipline is to ship interfaces that feel *intentional* — built as a designed system, not as default-class accumulation.

Authoritative grounding: Apple Human Interface Guidelines, Material Design 3, Nielsen's 10 Usability Heuristics, WCAG 2.2 (cross-reference from DESIGN). Comparative pattern references in `anti-patterns.md` study high-craft sites (Stripe, Vercel, Linear, Monogram, Kraken) for what they do right — per `DEC-2026-05-17-004` Clause 6, these inform examples without being authoritative citations.
<!-- /SECTION: overview -->

<!-- SECTION: sources -->
## §2 Authoritative Sources

| Source ID | Reference | Version | Date Verified |
|-----------|-----------|---------|---------------|
| APPLE-HIG | [Apple Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines) — Foundations (Color, Typography, Layout, Motion, Materials, Accessibility) | Current (continually updated by Apple) | reference (SPA-rendered, unfetchable via WebFetch; publicly published) |
| MATERIAL-3 | [Material Design 3](https://m3.material.io) — Foundations (color system, type scale, motion, shape, elevation) and Styles | Current (Material Design 3 with M3 Expressive updates 2024-2025) | reference (SPA-rendered, unfetchable via WebFetch; publicly published) |
| NIELSEN-10 | [Jakob Nielsen — 10 Usability Heuristics for User Interface Design](https://www.nngroup.com/articles/ten-usability-heuristics/) (Nielsen Norman Group) | Original 1994; refreshed 2020 | reference (stable methodology) |
| WCAG | W3C Web Content Accessibility Guidelines 2.2 (cross-reference from DESIGN; verified 2026-05-20) | 2.2 (2023-10-05; updated 2024-12-12) | 2026-05-20 (Phase 5 commit 3/7) |
| MITRE-ATLAS | [MITRE ATLAS](https://atlas.mitre.org) — AI output failure modes | v5.4.0 | 2026-05-17 (Phase 2) |

Citation granularity per Phase 4 Checkpoint 1 Decision A: APPLE-HIG and MATERIAL-3 cited at foundation level (e.g., "APPLE-HIG Typography" / "MATERIAL-3 Color System") since their main pages are SPA-rendered and not fetchable via WebFetch — the source authority is real and publicly published; the URL stability is high; but sub-rule verbatim quoting isn't possible via the available tools. This is similar to the paywalled-source pattern under DEC-2026-05-17-004 Clause 5 — cite by reference, not by fabricated sub-quote. NIELSEN-10 cited at heuristic level (1 through 10). WCAG 2.2 cited at success-criterion level where applicable (e.g., `WCAG 2.2 SC 2.4.7 Focus Visible`). Anti-AI-slop discipline is TGF synthesis acknowledged honestly per `DEC-2026-05-17-004` — 2024-2026 observable phenomenon not yet codified in any single authoritative source.
<!-- /SECTION: sources -->

<!-- SECTION: discovery -->
## §3 Discovery Commands

Copy-pasteable commands to detect AI-slop signals and design-system absence in a codebase.

```bash
# Detect color sprawl — count distinct color values in styles
grep -rhoE "#[0-9a-fA-F]{3,8}|rgb\([^)]+\)|hsl\([^)]+\)" --include="*.css" --include="*.scss" --include="*.tsx" --include="*.jsx" 2>/dev/null | sort -u | head -30
# More than ~15-20 distinct colors usually indicates accumulation rather than system

# Detect Tailwind default-class accumulation (slop signals)
grep -rnE "rounded-(md|lg|xl|2xl|3xl)\s+bg-(blue|gray|red|green|yellow|purple)-(400|500|600)" --include="*.tsx" --include="*.jsx" 2>/dev/null | head -10

# Look for design token system (positive signal)
test -f tailwind.config.* && grep -E "theme:.*extend|colors:" tailwind.config.* 2>/dev/null | head -5
find . -name "tokens.*" -o -name "design-tokens*" -o -name "theme.*" 2>/dev/null | head

# Detect monotone typography — count distinct font sizes
grep -rhoE "text-(xs|sm|base|lg|xl|2xl|3xl|4xl|5xl|6xl|7xl|8xl|9xl)" --include="*.tsx" --include="*.jsx" 2>/dev/null | sort -u
# Fewer than 4 distinct sizes = monotone; more than 8 = noisy. The right answer is usually 4-6 with clear purposes.

# Detect missing focus styles (forgotten-state signal)
grep -rn "focus:" --include="*.tsx" --include="*.jsx" 2>/dev/null | wc -l
grep -rn "outline-none" --include="*.tsx" --include="*.jsx" 2>/dev/null | wc -l
# If outline-none usage exceeds focus: ring usage, focus rings have been removed without replacement (AP-6 territory)
```
<!-- /SECTION: discovery -->

<!-- SECTION: principles -->
## §4 Universal Principles

Seven principles that ground every numbered rule.

- **A design system is a decision, not a default.** Color palette, typography scale, spacing scale, component shapes — all decided early as a coherent system and used consistently across the product. Default Tailwind/Bootstrap shapes and the modal Material/Apple-style components signal "AI generated this." An intentional system (even a small one) is the difference between AI-slop and crafted UI.

- **Restraint is craft.** Saying NO to elements, colors, motions, and patterns that don't earn their place is the discipline that distinguishes Stripe and Vercel from generic SaaS templates. Maximalism (everything animated, every color used, every effect applied) signals lack of editing. Restraint signals intent.

- **Hierarchy is structural.** Typography hierarchy (4-6 sizes/weights with clear purposes), color hierarchy (one accent color does the heavy lifting; others support), motion hierarchy (primary actions get the strongest motion; secondary actions are subtler) — all communicate importance and guide attention. Flat hierarchy (everything same size, everything same weight) makes nothing important.

- **States are first-class.** Every interactive element has default, hover, focus, active, disabled, loading, error, empty states. Focus rings are designed (not the browser-default blue outline). Empty states have intent — they tell the user what to do, not just "no data." Loading states give feedback. Error states recover gracefully.

- **Motion communicates.** Motion is feedback (the button knows you clicked it), structure (the modal arrives from somewhere logical), or status (the spinner indicates work in progress). Indiscriminate motion — every element fades-in on scroll, animated gradients everywhere — is noise that adds nothing.

- **Whitespace is content.** Generous spacing between elements is not absence — it is content that says "these things are separate" or "this thing matters more." Cramped layouts with default-margin everything signal "I didn't think about this." Disciplined whitespace signals craft.

- **Consistency over cleverness.** Once a pattern is established for one element (a button shape, a card layout, a transition), use it consistently elsewhere. Cleverness applied inconsistently across components reads as random, not intentional. Consistency reads as designed.
<!-- /SECTION: principles -->

<!-- SECTION: rules -->
## §5 Rule Summaries

Seven rules. Each summary: title + 1-line statement + source identifier.

<!-- RULE: 5.1 -->
- **Rule 5.1: Build a Design System, Don't Accumulate Defaults** — Color palette, typography scale, spacing scale, and component shapes are decided early as a coherent system and used consistently. Default framework classes accumulating across components signal "AI generated this." `APPLE-HIG Foundations + MATERIAL-3 Foundations + TGF-SYNTHESIS` → [`rules.md#rule-51-build-a-design-system-dont-accumulate-defaults`](rules.md)
<!-- /RULE: 5.1 -->
<!-- RULE: 5.2 -->
- **Rule 5.2: Restrained Color Palette** — Approximately 3-5 colors total: primary brand color + 1-2 accents + neutral grays + semantic states (success/warning/error). 14 different blues across one screen signals palette accumulated through ad-hoc choices rather than a system. `MATERIAL-3 Color System + TGF-SYNTHESIS` → [`rules.md#rule-52-restrained-color-palette`](rules.md)
<!-- /RULE: 5.2 -->
<!-- RULE: 5.3 -->
- **Rule 5.3: Typography Hierarchy Is Structural, Not Decorative** — Establish 4-6 type sizes/weights with clear purposes (display, h1, h2, body, caption). Hierarchy via combination of size, weight, and color — not all three independently. Custom or carefully-chosen typefaces over system defaults where the brand earns it. `APPLE-HIG Typography + TGF-SYNTHESIS` → [`rules.md#rule-53-typography-hierarchy-is-structural`](rules.md)
<!-- /RULE: 5.3 -->
<!-- RULE: 5.4 -->
- **Rule 5.4: Spacing Rhythm via Consistent Scale** — Spacing follows a consistent scale (typically 4px or 8px base with multiples: 4/8/12/16/24/32/48/64). Vertical rhythm is intentional. Default-margin everything (`p-4 m-4 gap-4` accumulating across components) signals absence of rhythm consideration. `MATERIAL-3 Foundations (8dp grid) + TGF-SYNTHESIS` → [`rules.md#rule-54-spacing-rhythm-via-consistent-scale`](rules.md)
<!-- /RULE: 5.4 -->
<!-- RULE: 5.5 -->
- **Rule 5.5: Motion Is Communication, Not Decoration** — Motion serves a purpose: feedback (button click), structure (modal arrives logically), or status (spinner indicates work). Indiscriminate motion (every element fades-in on scroll, animated gradients in places adding no value) is noise. `APPLE-HIG Motion + NIELSEN-10 Heuristic #1 (Visibility of System Status)` → [`rules.md#rule-55-motion-is-communication-not-decoration`](rules.md)
<!-- /RULE: 5.5 -->
<!-- RULE: 5.6 -->
- **Rule 5.6: Designed States Across the Board** — Every interactive element has all states considered: default, hover, focus, active, disabled, loading, error, empty. Focus rings are designed (visible, brand-consistent), not the browser-default outline. Empty states have intent. Loading and error states give feedback. `NIELSEN-10 Heuristic #1 (Visibility of System Status) + WCAG 2.2 SC 2.4.7 (Focus Visible) + TGF-SYNTHESIS` → [`rules.md#rule-56-designed-states-across-the-board`](rules.md)
<!-- /RULE: 5.6 -->
<!-- RULE: 5.7 -->
- **Rule 5.7: Restraint Earns Trust** — Saying NO to elements, colors, motions, and patterns that don't earn their place. Maximalism (everything animated, every color used, every effect applied) signals lack of editing. Restraint signals intent. Cross-references DESIGN Rule 5.3 (simplest wins) applied at the visual layer. `TGF-SYNTHESIS — grounded in observable high-craft pattern across Stripe / Vercel / Linear / Monogram / Kraken` → [`rules.md#rule-57-restraint-earns-trust`](rules.md)
<!-- /RULE: 5.7 -->

See `rules.md` for full rule text, citations, plain-language impact, and extended discussion.
<!-- /SECTION: rules -->

<!-- SECTION: anti-patterns -->
## §6 Anti-Pattern Summaries

Eight anti-pattern pairs covering the most common AI-slop failure modes. CP examples reference high-craft sites (Stripe, Vercel, Linear, Monogram, Kraken) per `DEC-2026-05-17-004` Clause 6 — comparative pattern references, not authoritative citations.

<!-- ANTI-PATTERN: AP-1 -->
- **AP-1: Default Tailwind/Bootstrap shapes everywhere** — `rounded-md bg-blue-500 text-white px-4 py-2` accumulating across components; the AI-generated-this-with-default-classes signal. Violates Rule 5.1. → [`anti-patterns.md#ap-1-default-tailwind-bootstrap-everywhere`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-1 -->
<!-- ANTI-PATTERN: AP-2 -->
- **AP-2: Color sprawl** — 14 different blues, 8 grays, 6 reds across a single product; no color system; palette accumulated through ad-hoc choices. Violates Rule 5.2. → [`anti-patterns.md#ap-2-color-sprawl`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-2 -->
<!-- ANTI-PATTERN: AP-3 -->
- **AP-3: Typography monotone** — Everything 16px body / 24px h2 / 32px h1 with no purposeful additional hierarchy; no contrast in weight or scale; default font stack. Violates Rule 5.3. → [`anti-patterns.md#ap-3-typography-monotone`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-3 -->
<!-- ANTI-PATTERN: AP-4 -->
- **AP-4: Default spacing accumulation** — All margins/paddings are `p-4 m-4 gap-4` (Tailwind defaults) without rhythm consideration; no vertical-rhythm intent; cramped + uniform throughout. Violates Rule 5.4. → [`anti-patterns.md#ap-4-default-spacing-accumulation`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-4 -->
<!-- ANTI-PATTERN: AP-5 -->
- **AP-5: Indiscriminate motion** — Every element fades-in on scroll; hover-translate on everything; animated gradients in static contexts; motion applied without communicative purpose. Violates Rule 5.5. → [`anti-patterns.md#ap-5-indiscriminate-motion`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-5 -->
<!-- ANTI-PATTERN: AP-6 -->
- **AP-6: Forgotten states** — Only default state designed. Hover/focus/active/disabled/loading/error/empty look like browser/library defaults. `outline-none` applied without replacement focus indicator (also a WCAG 2.2 violation per SC 2.4.7). Violates Rule 5.6. → [`anti-patterns.md#ap-6-forgotten-states`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-6 -->
<!-- ANTI-PATTERN: AP-7 -->
- **AP-7: Stock-aesthetic accumulation** — Generic 3D illustrations + gradient blobs + lorem-ipsum content + AI-generated avatars + stock-photography style. The visual signal of "templated product." Violates Rules 5.1 and 5.7. → [`anti-patterns.md#ap-7-stock-aesthetic-accumulation`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-7 -->
<!-- ANTI-PATTERN: AP-8 -->
- **AP-8: Maximalist accumulation** — Every screen tries to communicate everything: every feature highlighted equally, every section animated, every color used, every effect layered. No hierarchy of importance; no editing-down to what matters most. Violates Rule 5.7 and DESIGN Rule 5.3 (simplest wins). → [`anti-patterns.md#ap-8-maximalist-accumulation`](anti-patterns.md)
<!-- /ANTI-PATTERN: AP-8 -->

Per `DEC-2026-05-17-003` Clause 1: every anti-pattern is paired with a canonical pattern in `anti-patterns.md`.
<!-- /SECTION: anti-patterns -->

<!-- SECTION: ai-concerns -->
## §7 AI-Specific Concerns

UI-CRAFT failure modes specific to AI-assisted development.

- **Default-class reproduction.** AI training data over-represents Tailwind/Bootstrap default-class usage because those classes are the modal solution in code samples. Asked for "a button," AI produces `<button class="rounded-md bg-blue-500 text-white px-4 py-2">` — recognizable as AI-default. The pattern compounds across components and the product accumulates the AI-slop aesthetic. Defense: Rule 5.1 (design system) operationalized via design tokens / theme config that override defaults at the source.

- **Color picker pattern.** AI tends to use whatever color seems contextually appropriate — `bg-blue-500` for one button, `bg-blue-600` for another, `bg-sky-500` for a third — without checking whether they belong to a coherent palette. Color sprawl accumulates invisibly. Defense: Rule 5.2 + design tokens that constrain color choices to the system.

- **Monotone defaults.** Asked to "make the heading bigger," AI bumps from `text-base` to `text-2xl` without considering hierarchy across the product. Typography accumulates with no system-wide intent. Defense: Rule 5.3 + a documented type scale.

- **State neglect.** AI focuses on what was prompted — usually the default state. Hover/focus/active/disabled/loading/error/empty get afterthought treatment if mentioned at all. Defense: Rule 5.6 + state-design checklist applied at component creation time.

- **Motion as decoration.** AI may add motion ("nice animations") without considering whether the motion communicates anything. Asked for a landing page, AI adds fade-in-on-scroll to every section, animated-gradient backgrounds, hover-translate on every card. Defense: Rule 5.5 — motion must serve feedback, structure, or status.

- **"Looks impressive" bias.** AI training rewards visually-impressive output. The signal "this looks impressive" can outrank "this is appropriate for the user." Maximalism is the failure mode this creates. Defense: Rule 5.7 (restraint) + DESIGN Rule 5.3 (simplest wins).

Relevant external taxonomies: MITRE ATLAS framework on AI design output; OWASP LLM Top 10:2025 `LLM09:2025` (Misinformation — including AI confidently producing UI patterns that don't fit project constraints).
<!-- /SECTION: ai-concerns -->

<!-- SECTION: workflow -->
## §8 Workflow Integration

How UI-CRAFT participates in the six-stage workflow (per `docs/WORKFLOW.md`).

- **Stage 1 (Research):** Run §3 discovery commands when work touches the visible surface. Surface existing design-system artifacts (design tokens, theme config, component library) before adding new components.
- **Stage 2 (Scope):** If a design system doesn't yet exist for the project, scoping new UI work includes "establish minimum design system" as a sub-deliverable (Rule 5.1).
- **Stage 3 (Plan with Governance):** Rules 5.1–5.7 contribute when the change touches color, typography, spacing, motion, states, or component shape.
- **Stage 4 (Implement):** Apply rules during component creation. Use design tokens; reference the type scale; respect the spacing rhythm; design all states.
- **Stage 5 Phase 1 (Code Review):** UI-CRAFT references during code review when the diff touches visible components. Flag default-class accumulation, color sprawl, monotone typography, state neglect.
- **Stage 5 Phase 4 (Holistic Review):** Holistic Reviewer references UI-CRAFT principles when checking visual integrity of the change — does it match the design system; does it respect existing patterns.
- **Stage 6 (Commit):** Design system extensions captured in DECISIONS.md per CONTINUITY Rule 5.2 (e.g., "added a new accent color for warning states; rationale: ...").
<!-- /SECTION: workflow -->

<!-- SECTION: subagent-context -->
## §9 Subagent Context

**Preloaded by:** None directly. UI-CRAFT activates at the orchestrator level during Stage 3/Stage 4 when visible-surface work is in scope. The `code-reviewer` subagent (Phase 4) references UI-CRAFT principles when reviewing visible-component diffs but does not preload the full skill.

**Critical rules for orchestrator use (when not preloaded):**

- Rule 5.1 (Build a Design System, Don't Accumulate Defaults)
- Rule 5.6 (Designed States Across the Board)
- Rule 5.7 (Restraint Earns Trust)

**Top AI-specific concerns:**

- Default-class reproduction (Tailwind/Bootstrap modal classes accumulating)
- Color picker pattern (color sprawl without system)
- State neglect (only default state designed; focus/error/empty/loading forgotten)

Reference files (`rules.md`, `anti-patterns.md`) load on demand within the orchestrator if a specific UI-craft scenario warrants deep rule application. The high-craft reference site studies in `anti-patterns.md` provide concrete pattern examples.
<!-- /SECTION: subagent-context -->
