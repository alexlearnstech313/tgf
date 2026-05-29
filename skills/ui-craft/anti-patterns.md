# Anti-Patterns + Canonical Patterns — UI-CRAFT

Full anti-pattern + canonical pattern pairs with code examples and high-craft reference site studies. Referenced from `SKILL.md` §6 Anti-Pattern Summaries.

Eight anti-pattern pairs covering the most common AI-slop failure modes. CP examples reference high-craft sites — **Stripe**, **Vercel**, **Linear**, **Monogram**, **Kraken** — per `DEC-2026-05-17-004` Clause 6: comparative pattern references, not authoritative citations. The reference sites are studied for what they do right; the patterns are extracted as principles. Per `DEC-2026-05-17-003` Clause 1: every anti-pattern is paired with a canonical pattern.

---

## AP-1: Default Tailwind/Bootstrap shapes everywhere

**Pattern:**

```tsx
// Throughout the product — buttons accumulating default classes
<button className="rounded-md bg-blue-500 px-4 py-2 text-white hover:bg-blue-600">
  Save
</button>

<button className="rounded-md bg-blue-500 px-4 py-2 text-white hover:bg-blue-600">
  Submit
</button>

<button className="rounded-md bg-blue-500 px-4 py-2 text-white hover:bg-blue-600">
  Continue
</button>

// In another file, slight inconsistency creeps in
<button className="rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700">
  Get Started
</button>
```

```css
/* tailwind.config.js — no theme customization */
module.exports = {
  content: [...],
  theme: {
    extend: {},  // empty — using all defaults
  },
}
```

**Violates:** Rule 5.1 (build a design system, don't accumulate defaults). See `rules.md#rule-51-build-a-design-system-dont-accumulate-defaults`.

**Why it fails:** Every button is a fresh class accumulation; no shared abstraction means small inconsistencies (rounded-md vs rounded-lg, blue-500 vs blue-600) creep in without anyone noticing. The bigger problem: `bg-blue-500` IS the modal Tailwind tutorial color. Anyone familiar with Tailwind sees the product and recognizes "Tailwind defaults, no design system" — the AI-slop signal. The product looks like template, not product.

**Source for failure mode:** AI default-class reproduction. Tailwind tutorial code is over-represented in training data; `rounded-md bg-blue-500 px-4 py-2 text-white` is the modal "Tailwind button" pattern AI emits without project-specific context.

### CP-1: Design tokens + reusable Button component

**Pattern:**

```css
/* tailwind.config.js — design system encoded */
module.exports = {
  theme: {
    extend: {
      colors: {
        // Brand-specific palette; semantic naming
        primary: {
          50: '#f5f3ff',
          500: '#7c3aed',  // brand purple, not blue-500
          600: '#6d28d9',
          700: '#5b21b6',
        },
        neutral: { /* 50-900 brand-tuned grays */ },
        success: { /* ... */ },
        danger: { /* ... */ },
      },
      borderRadius: {
        button: '8px',  // brand-decided radius, used for all buttons
        card: '12px',
      },
      fontFamily: {
        sans: ['Geist', 'Inter', 'system-ui', 'sans-serif'],
        mono: ['Geist Mono', 'JetBrains Mono', 'monospace'],
      },
    },
  },
}
```

```tsx
// src/components/ui/Button.tsx — single source of truth
import { cva } from 'class-variance-authority';

const buttonStyles = cva(
  'rounded-button px-4 py-2 font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 focus-visible:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed',
  {
    variants: {
      variant: {
        primary: 'bg-primary-500 text-white hover:bg-primary-600 active:bg-primary-700',
        secondary: 'bg-neutral-100 text-neutral-900 hover:bg-neutral-200 active:bg-neutral-300',
        danger: 'bg-danger-500 text-white hover:bg-danger-600',
        ghost: 'bg-transparent text-primary-600 hover:bg-primary-50',
      },
      size: {
        sm: 'px-3 py-1.5 text-sm',
        md: 'px-4 py-2 text-base',
        lg: 'px-6 py-3 text-lg',
      },
    },
    defaultVariants: { variant: 'primary', size: 'md' },
  }
);

export const Button = ({ variant, size, className, ...props }) => (
  <button className={buttonStyles({ variant, size, className })} {...props} />
);

// Usage everywhere — consistent
<Button>Save</Button>
<Button>Submit</Button>
<Button variant="secondary">Cancel</Button>
<Button variant="danger">Delete</Button>
```

**Pairs with:** Anti-pattern AP-1

**Why it works:** Design tokens encode the system at the source (Tailwind theme). Brand color is `primary-500` (purple, not the modal blue), border radius is one decided value, typography uses a brand-chosen typeface. Single Button component is the source of truth — variant + size are explicit; consistency is automatic. Focus ring (Rule 5.6) is designed in once and applied everywhere. AI prompted for "a button" produces `<Button>` against the system, not default Tailwind classes.

**High-craft reference:** Vercel's buttons. Black background, subtle hover state, Geist typeface, no rounded-2xl defaults. The buttons across vercel.com all share the same proportions, the same hover feedback, the same focus treatment — visible signal of a design system. Stripe similarly: their button system is so consistent across pages that a Stripe-style button is instantly recognizable independent of context.

---

## AP-2: Color sprawl

**Pattern:**

```tsx
// Across one product, in different components
<div className="bg-blue-500 text-white">Header banner</div>
<button className="bg-blue-600 text-white">Primary CTA</button>
<a className="text-blue-500 hover:text-blue-700">Link</a>
<div className="border-blue-400 ring-blue-300">Focused input</div>
<svg className="text-blue-500 fill-blue-600 stroke-blue-700">Icon</svg>
<span className="bg-sky-500 text-white">Status badge</span>
<div className="bg-indigo-500 text-white">Notification</div>
<button className="bg-cyan-500 text-white">Secondary CTA</button>

// Each individual choice was fine. The accumulation across the
// product = 8 distinct blue-family values doing similar jobs.
```

**Violates:** Rule 5.2 (restrained color palette). See `rules.md#rule-52-restrained-color-palette`.

**Why it fails:** Each `bg-blue-*` was a sensible local choice; the cumulative palette is sprawl. Users perceive the product as "looks generic and unpolished" without articulating why. The technical signal: more than 5-7 distinct color values in a single product surface usually means palette accumulated rather than designed. The visual signal: nothing looks intentional.

**Source for failure mode:** AI color-picker pattern. Each component is generated with a contextually-appropriate color; AI doesn't check whether the color belongs to a coherent system.

### CP-2: Restrained palette via design tokens

**Pattern:**

```css
/* Tailwind theme — restrained palette */
module.exports = {
  theme: {
    extend: {
      colors: {
        // Single brand color with a tight scale
        primary: {
          50: '#eef2ff',
          100: '#e0e7ff',
          500: '#6366f1',  // Indigo-500 — the one brand color
          600: '#4f46e5',
          700: '#4338ca',
          900: '#312e81',
        },
        // Neutral grays — separate from brand
        neutral: { 50: '#fafafa', 100: '#f5f5f5', 200: '#e5e5e5', /* ... */ 900: '#171717' },
        // Semantic colors — used for their semantic meaning only
        success: { 50: '#f0fdf4', 500: '#22c55e', 700: '#15803d' },
        warning: { 50: '#fffbeb', 500: '#f59e0b', 700: '#b45309' },
        danger:  { 50: '#fef2f2', 500: '#ef4444', 700: '#b91c1c' },
      },
    },
  },
}
```

```tsx
// Usage — discipline maintained
<div className="bg-primary-500 text-white">Header banner</div>
<button className="bg-primary-500 text-white hover:bg-primary-600">Primary CTA</button>
<a className="text-primary-600 hover:text-primary-700">Link</a>
<div className="border-primary-300 ring-primary-500/30">Focused input</div>
<svg className="text-primary-500">Icon</svg>
<span className="bg-success-500 text-white">Success badge</span>
<span className="bg-warning-500 text-white">Warning badge</span>
<button className="bg-neutral-100 text-neutral-900 hover:bg-neutral-200">Secondary CTA</button>

// Across the product: one brand color in 6 shades + neutral grays
// + semantic colors for semantic uses only. ~12-15 named tokens
// total, used with discipline.
```

**Pairs with:** Anti-pattern AP-2

**Why it works:** One brand color (indigo) plus a tight neutral scale plus semantic colors used for their semantic meaning. No "what blue should I use here?" decision moments — the token system answers it. The product reads as designed because the same color choices appear consistently across surfaces.

**High-craft reference:** Linear (linear.app). Indigo as the brand color, neutrals dominant, semantic colors used sparingly and consistently. Their UI feels coherent because the palette is disciplined — you can identify a Linear screenshot by color alone. Stripe similarly: their purple-blue is consistent; semantic colors appear when they're semantically needed; the marketing surfaces and product UI share the palette.

---

## AP-3: Typography monotone

**Pattern:**

```tsx
// Across the product
<h1 className="text-3xl font-bold">Page Title</h1>
<h2 className="text-2xl font-bold">Section Heading</h2>
<h3 className="text-xl font-bold">Subsection</h3>
<p className="text-base">Body content goes here.</p>
<p className="text-sm text-gray-500">Caption text</p>

// In another file
<h1 className="text-2xl font-semibold">Page Title</h1>
<h2 className="text-xl font-semibold">Section Heading</h2>
<p className="text-base">Body content</p>

// In a third file
<div className="text-lg font-bold">Header</div>
<div className="text-base">Content</div>
<div className="text-sm text-gray-400">Meta</div>
```

```css
/* tailwind.config.js — no custom font scale */
/* font-family stays at system default sans-serif */
```

**Violates:** Rule 5.3 (typography hierarchy is structural, not decorative). See `rules.md#rule-53-typography-hierarchy-is-structural-not-decorative`.

**Why it fails:** Three things wrong: (1) no consistent type scale across the product — h1 is sometimes text-3xl, sometimes text-2xl, sometimes text-lg; (2) hierarchy compressed into the same narrow size range (text-sm through text-3xl, ~14px-30px) means h1 and body are too close to feel like distinct levels; (3) no typeface choice — system default sans-serif everywhere makes the product look like a wireframe.

**Source for failure mode:** AI generates per-component without product-wide hierarchy. Per-file the choices look reasonable; across the product they don't cohere.

### CP-3: Documented type scale + intentional typeface

**Pattern:**

```css
/* tailwind.config.js */
module.exports = {
  theme: {
    extend: {
      fontFamily: {
        sans: ['Geist', 'Inter var', 'system-ui', 'sans-serif'],
        mono: ['Geist Mono', 'JetBrains Mono', 'monospace'],
      },
      fontSize: {
        // Custom scale with clear purposes
        'display': ['4.5rem', { lineHeight: '1.05', letterSpacing: '-0.04em', fontWeight: '700' }],  // 72px — hero only
        'h1':      ['3rem',   { lineHeight: '1.1',  letterSpacing: '-0.03em', fontWeight: '700' }],  // 48px
        'h2':      ['2rem',   { lineHeight: '1.2',  letterSpacing: '-0.02em', fontWeight: '600' }],  // 32px
        'h3':      ['1.5rem', { lineHeight: '1.3',  letterSpacing: '-0.01em', fontWeight: '600' }],  // 24px
        'body-lg': ['1.125rem', { lineHeight: '1.6', fontWeight: '400' }],                          // 18px
        'body':    ['1rem',   { lineHeight: '1.6',  fontWeight: '400' }],                          // 16px
        'caption': ['0.875rem', { lineHeight: '1.5', fontWeight: '500' }],                          // 14px
        'small':   ['0.75rem',  { lineHeight: '1.4', fontWeight: '500' }],                          // 12px
      },
    },
  },
}
```

```tsx
// Usage — consistent hierarchy
<h1 className="text-display">Brand-level hero text</h1>      {/* one per landing */}
<h1 className="text-h1">Page Title</h1>
<h2 className="text-h2">Section Heading</h2>
<h3 className="text-h3">Subsection</h3>
<p className="text-body">Standard body content.</p>
<p className="text-body-lg">Lead paragraph or editorial content.</p>
<span className="text-caption text-neutral-500">Meta information</span>
<span className="text-small text-neutral-500">Legal / smallest UI text</span>
```

**Pairs with:** Anti-pattern AP-3

**Why it works:** Documented scale with clear purposes (display, h1, h2, h3, body, caption, small) means hierarchy is structural — text-display reads as "the one big thing," text-body reads as "content." Weight contrast is built into the scale tokens (display/h1 = 700, h2/h3 = 600, body = 400). A custom typeface (Geist) signals intentional brand choice over wireframe-defaults. The scale spans 72px → 12px — a 6x range that gives real hierarchy room.

**High-craft reference:** Vercel (vercel.com). Geist typeface used with mastery — display text at very large sizes for hero moments; tight letter-spacing on headings; deliberate weight contrast between display (often regular weight at large sizes, editorial feel) and body. The vertical rhythm and weight contrast make every page feel like the same product even when content varies. Stripe's typography similarly: Inter / their custom variants used with intentional hierarchy; headings have negative letter-spacing for editorial polish.

---

## AP-4: Default spacing accumulation

**Pattern:**

```tsx
// Across components
<div className="p-4">
  <div className="mb-4">
    <h2 className="mb-4">Heading</h2>
    <p className="mb-4">Content</p>
  </div>
  <div className="p-4 mb-4">
    <h3 className="mb-4">Subheading</h3>
    <p>More content</p>
  </div>
  <div className="flex gap-4 mt-4">
    <button className="p-4">Button</button>
    <button className="p-4">Button</button>
  </div>
</div>

// p-4 (16px) and m-4 (16px) everywhere; no rhythm; cramped
// where content needs breathing room, uniform where hierarchy
// would help.
```

**Violates:** Rule 5.4 (spacing rhythm via consistent scale). See `rules.md#rule-54-spacing-rhythm-via-consistent-scale`.

**Why it fails:** `p-4 m-4 gap-4` is the Tailwind tutorial default. Applied everywhere, it produces visually-uniform spacing — every gap is 16px, no rhythm signals hierarchy or grouping. Cramped where content needs to breathe (paragraphs touching subsequent headings); over-spaced where elements should be tightly grouped (icon + label inside a button).

**Source for failure mode:** AI generates spacing values from the most-common training-data choice. `p-4` is the modal Tailwind padding; it accumulates without project rhythm consideration.

### CP-4: Spacing scale with rhythm intent

**Pattern:**

```tsx
// Same content, designed spacing rhythm
<div className="px-6 py-12">                              {/* page padding: comfortable horizontal margin + generous vertical */}
  <div className="mb-16">                                  {/* large gap before major section break */}
    <h2 className="mb-3 text-h2">Heading</h2>              {/* tight gap heading→content (related) */}
    <p className="text-body text-neutral-700">Content describing the section.</p>
  </div>

  <div className="mb-16 p-8 rounded-card bg-neutral-50">  {/* card with comfortable interior padding */}
    <h3 className="mb-2 text-h3">Subheading</h3>           {/* even tighter h3→content (more closely related) */}
    <p className="text-body">More content with breathing room.</p>
  </div>

  <div className="flex gap-3 mt-12">                       {/* small gap between related buttons; large gap from preceding content */}
    <Button>Primary action</Button>
    <Button variant="secondary">Secondary</Button>
  </div>
</div>
```

```css
/* Spacing scale used — 4px base, multiples consistent with brand rhythm:
   gap-1 (4px)   — very tight (icon + label)
   gap-2 (8px)   — tight (button text + icon)
   gap-3 (12px)  — small (related buttons in a group)
   gap-4 (16px)  — base (heading + immediate content)
   gap-6 (24px)  — medium (between related content blocks)
   gap-8 (32px)  — comfortable (card padding, between sections)
   gap-12 (48px) — generous (between major sections)
   gap-16 (64px) — large (major section breaks)
   gap-24 (96px) — editorial (landing-page section breaks) */
```

**Pairs with:** Anti-pattern AP-4

**Why it works:** Spacing reflects content relationships — tight where things belong together (heading + its immediate paragraph: 8-12px), generous where things are distinct (between major sections: 64px). Vertical rhythm is intentional. Page-level padding is comfortable. Card interior is generous. Button-group spacing is tight (related items). The layout breathes; hierarchy is visible from spacing alone.

**High-craft reference:** Stripe's landing pages. Their vertical rhythm is striking — small gaps within related content groups; very large gaps between major sections; editorial whitespace around hero text. The site doesn't feel sparse; it feels like every gap is intentional. Linear's product UI similarly: tight where keyboard-shortcut speed matters; comfortable where content needs reading.

---

## AP-5: Indiscriminate motion

**Pattern:**

```tsx
// Landing page where every element has motion
<section className="animate-fade-in-up">
  <h1 className="animate-fade-in-down">Hero text</h1>
  <p className="animate-fade-in delay-100">Subtitle</p>
  <Button className="animate-pulse hover:scale-110 transition-transform">CTA</Button>
</section>

<section className="bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 animate-gradient">
  <div className="animate-fade-in-left">
    <h2 className="animate-bounce">Feature</h2>
    <Card className="hover:rotate-3 hover:scale-105 transition-all">
      Hover-rotate card
    </Card>
  </div>
</section>

<footer className="animate-fade-in-up delay-300">
  Footer content
</footer>
```

```css
/* Plus animated gradient backgrounds in static contexts,
   parallax scrolling on every section, marquee text scrolling
   across the top, particle effects behind hero text */
```

**Violates:** Rule 5.5 (motion is communication, not decoration). See `rules.md#rule-55-motion-is-communication-not-decoration`.

**Why it fails:** Every element animates → nothing communicates anything in particular. The fade-ins on scroll add noise without signaling structure. Animated gradients in static contexts add motion sickness risk without aiding usability. Hover-rotate cards feel busy. Users with vestibular disorders or motion sensitivity experience nausea. Performance suffers from concurrent animations. The overall signal: "we wanted to look animated," not "we used motion to communicate."

**Source for failure mode:** AI training rewards visually-impressive output. Asked for "a nice landing page," AI defaults to "everything animated" because animated landing pages are over-represented in tutorial content and showcase galleries.

### CP-5: Motion serves feedback, structure, or status

**Pattern:**

```tsx
// Same landing page, restrained motion
<section className="px-6 py-24">
  <h1 className="text-display text-neutral-900">Hero text</h1>  {/* No entrance animation — text just is */}
  <p className="text-body-lg mt-6 text-neutral-600">Subtitle</p>
  <Button className="mt-12">CTA</Button>                          {/* Button has its own hover/active feedback per Rule 5.6 */}
</section>

<section className="px-6 py-24 bg-neutral-50">  {/* Static gradient or solid color; no animation */}
  <h2 className="text-h2">Feature</h2>
  <Card className="hover:bg-neutral-100 transition-colors duration-200">
    {/* Hover provides feedback that card is interactive; subtle color shift, not rotate/scale */}
    Card content
  </Card>
</section>

{/* One signature motion element: a product visualization that animates
    to show how the product works. The motion is a demonstration, not
    decoration. */}
<section className="px-6 py-24">
  <ProductDemo /> {/* Custom animation that communicates the product's value */}
</section>

<footer className="px-6 py-12 bg-neutral-100">Footer</footer>
```

```tsx
// Motion respects prefers-reduced-motion
// In the component:
@media (prefers-reduced-motion: reduce) {
  // Animations are disabled or significantly reduced
}
```

**Pairs with:** Anti-pattern AP-5

**Why it works:** Static content is static. Motion appears where it communicates: button hover provides feedback that the element is interactive (subtle color shift); the one product-demo animation communicates how the product works (motion as demonstration). No fade-in-on-scroll; no animated gradients in static contexts; no hover-rotate. `prefers-reduced-motion` respected per WCAG 2.2 SC 2.3.3. The page feels confident — most of it is still; the one element that moves carries the message.

**High-craft reference:** Stripe's product visualizations (the animated demonstrations of payment flows, dashboards, fraud detection) — purposeful motion that demonstrates the product. The rest of stripe.com is mostly static. Monogram (monogram.io) similarly: experimental motion is the agency's signature, but it's applied to specific moments (case study reveals, transitions between sections) — not to every element. Vercel: motion serves transitions and feedback; the landing page is mostly still.

---

## AP-6: Forgotten states

**Pattern:**

```tsx
// Button — only default state designed
<button className="rounded-md bg-blue-500 px-4 py-2 text-white outline-none">
  Save
</button>

// Form input — only default state
<input type="text" className="border border-gray-300 px-3 py-2 outline-none" />

// Data list — only the populated state designed
<ul>
  {items.map(item => <li key={item.id}>{item.name}</li>)}
</ul>
// What happens when items is empty? Blank screen.
// What happens while items is loading? Layout shift when items arrive.
// What happens if the fetch fails? No error shown.
```

**Violates:** Rule 5.6 (designed states across the board). See `rules.md#rule-56-designed-states-across-the-board`. **Also violates WCAG 2.2 SC 2.4.7 (Focus Visible)** — `outline-none` without a designed replacement focus indicator is an accessibility regression at AA level.

**Why it fails:** Multiple state failures compound:

- **Button:** `outline-none` removes the browser-default focus ring (accessibility regression); no hover state designed (no feedback on interaction); no disabled state (the button stays enabled visually even when functionally disabled); no loading state (users wonder if their click registered).
- **Input:** Same `outline-none` issue; no error state, no success state, no disabled state.
- **List:** Empty-state is a blank screen (users wonder if it's broken); loading shows nothing then suddenly shows results (layout shift); error shows nothing (no recovery path).

These are the most common AI-slop tells: AI generates the default state confidently and forgets everything else.

**Source for failure mode:** AI state neglect. Prompts usually specify the default ("a button," "a form," "a list") and AI delivers the default. State design needs explicit prompting or systematic application.

### CP-6: All states designed; focus rings respected

**Pattern:**

```tsx
// Button — all states designed
<button
  className="
    rounded-button bg-primary-500 px-4 py-2 font-medium text-white
    transition-colors
    hover:bg-primary-600
    active:bg-primary-700
    focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 focus-visible:ring-offset-2
    disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-primary-500
  "
  disabled={isLoading}
  aria-busy={isLoading}
>
  {isLoading ? (
    <>
      <Spinner className="mr-2 h-4 w-4" />
      Saving...
    </>
  ) : (
    'Save'
  )}
</button>

// Form input — designed states
<div>
  <label htmlFor="email" className="block text-caption font-medium text-neutral-700">
    Email
  </label>
  <input
    id="email"
    type="email"
    className={cn(
      'mt-1 block w-full rounded-md border px-3 py-2 transition-colors',
      'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500',
      'disabled:bg-neutral-100 disabled:text-neutral-500',
      error ? 'border-danger-500 ring-1 ring-danger-500' : 'border-neutral-300'
    )}
    aria-invalid={!!error}
    aria-describedby={error ? 'email-error' : undefined}
  />
  {error && (
    <p id="email-error" className="mt-1 text-caption text-danger-600 flex items-center gap-1">
      <ExclamationIcon className="h-4 w-4" />  {/* Icon + color + text — not color-only per WCAG SC 1.4.1 */}
      {error}
    </p>
  )}
</div>

// Data list — empty, loading, error states
<div>
  {isLoading && <SkeletonList />}
  {!isLoading && error && (
    <ErrorState>
      <p>We couldn't load the list. <button onClick={retry}>Try again</button></p>
    </ErrorState>
  )}
  {!isLoading && !error && items.length === 0 && (
    <EmptyState>
      <Illustration />
      <h3 className="text-h3">No items yet</h3>
      <p className="text-body text-neutral-600">
        Get started by creating your first item.
      </p>
      <Button onClick={createNew}>Create item</Button>
    </EmptyState>
  )}
  {!isLoading && !error && items.length > 0 && (
    <ul>
      {items.map(item => <li key={item.id}>{item.name}</li>)}
    </ul>
  )}
</div>
```

**Pairs with:** Anti-pattern AP-6

**Why it works:** Every state designed. Button has hover/active/disabled/focus-visible/loading; loading state shows a spinner inside the button so users see the click registered. Input has error state with icon + color + text per WCAG 2.2 SC 1.4.1 (Use of Color). List has explicit loading (skeleton), error (recovery action), empty (onboarding moment with CTA), and populated (the data itself) states. Focus rings designed in brand color (`ring-primary-500`) with offset; visible per WCAG 2.2 SC 2.4.7.

**High-craft reference:** Linear (linear.app). Every interactive element has all states designed — focus rings are indigo and consistent across the product; loading states use skeleton placeholders that match the eventual content shape; empty states have actionable copy and visual interest. The discipline shows: every interaction feels handled. Stripe's dashboard similarly — empty states for "no transactions yet," loading skeletons for slow queries, error states with recovery paths.

---

## AP-7: Stock-aesthetic accumulation

**Pattern:**

```tsx
// Landing page with accumulated stock aesthetic
<section>
  <h1>Build better products faster</h1>
  <p>The all-in-one platform for modern teams.</p>

  {/* Generic 3D illustration: floating geometric shapes,
      isometric figure looking at a chart, gradient blobs in background */}
  <img src="/3d-hero-illustration.svg" />

  {/* Gradient blob backgrounds */}
  <div className="absolute inset-0 bg-gradient-to-br from-purple-400 via-pink-400 to-orange-400 opacity-20 blur-3xl" />
</section>

<section>
  <h2>Trusted by teams worldwide</h2>
  {/* Generic placeholder logos */}
  <div className="grid grid-cols-6 gap-8">
    <CompanyLogo>Company A</CompanyLogo>
    <CompanyLogo>Company B</CompanyLogo>
    {/* etc — generic logo placeholders */}
  </div>
</section>

<section>
  <h2>Loved by users</h2>
  {/* Testimonials with AI-generated avatars and lorem-ipsum-feeling copy */}
  <Testimonial
    avatar="/avatar-1.jpg"  {/* AI-generated avatar — recognizable */}
    name="Sarah K."
    quote="This platform has transformed how our team works. I can't imagine going back."
  />
</section>
```

**Violates:** Rule 5.1 (build a design system) AND Rule 5.7 (restraint earns trust). See `rules.md` for both.

**Why it fails:** Every visual signal is generic: the 3D illustration could be on any landing page, the gradient blobs are the recognizable "AI-generated SaaS landing page" backdrop, the testimonial avatar is an AI-generated face that doesn't quite look real, the testimonial copy is too generic to be from a real person. None of it is wrong individually; the accumulation reads as "templated product, not real product." Users see this and unconsciously discount whatever the actual product is.

**Source for failure mode:** AI training rewards "looks like a landing page" — and landing-page training data is heavily populated by templates. Asked for "a landing page," AI assembles the most-common landing-page elements without commitment to a distinctive aesthetic.

### CP-7: Real content, intentional illustration, distinct aesthetic

**Pattern:**

```tsx
<section className="px-6 py-24 max-w-content mx-auto">
  <h1 className="text-display text-neutral-900">
    {/* Concrete, specific copy — not generic SaaS pitch */}
    Process payments in 8 lines of code.
  </h1>
  <p className="text-body-lg mt-6 text-neutral-600 max-w-prose">
    Stripe handles billions in transactions for millions of businesses.
  </p>

  {/* Product visualization — actual UI of the product, not generic illustration */}
  <ProductScreenshot
    src="/screenshots/dashboard-real.png"
    alt="Stripe dashboard showing real transaction data"
    className="mt-12 rounded-card shadow-xl"
  />
</section>

<section className="px-6 py-24 bg-neutral-50">
  <p className="text-caption uppercase tracking-wider text-neutral-500">
    Trusted by
  </p>
  {/* Real logos of real customers, not placeholder text */}
  <div className="mt-8 grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-12 items-center">
    <RealCustomerLogo name="OpenAI" />
    <RealCustomerLogo name="Shopify" />
    <RealCustomerLogo name="Anthropic" />
    {/* etc — real customer logos */}
  </div>
</section>

<section className="px-6 py-24">
  {/* Testimonials with real people (with permission), real product impact */}
  <blockquote className="text-h3 font-medium text-neutral-900 max-w-prose">
    "We integrated Stripe in two days. The dashboard showed us our first
    transaction within an hour of launch."
  </blockquote>
  <footer className="mt-6 flex items-center gap-3">
    <img
      src="/real-customer-photo.jpg"
      alt="Real customer name"
      className="h-12 w-12 rounded-full"
    />
    <div>
      <p className="text-body font-medium">Real Person Name</p>
      <p className="text-caption text-neutral-600">CEO, Real Company</p>
    </div>
  </footer>
</section>
```

**Pairs with:** Anti-pattern AP-7

**Why it works:** Real content (real product UI, real customers, real testimonials) signals a real product. Specific copy ("process payments in 8 lines of code") signals a specific value proposition rather than generic SaaS pitch. Restraint in visuals — product screenshot does the heavy lifting; no gradient blobs, no AI-generated avatars, no stock illustrations. The page reads as confident because it doesn't hide behind generic aesthetics.

**High-craft reference:** Stripe (stripe.com). The landing page features the actual product UI prominently — real dashboards, real payment flows visualized. The illustration is purposeful product demonstration, not decorative. Customer logos are real, recognizable companies. Vercel similarly: their landing features actual Next.js deployments and dashboards, not generic 3D illustrations. Linear: the marketing site is essentially "here's what the product looks like" — the product IS the visualization.

---

## AP-8: Maximalist accumulation

**Pattern:**

```tsx
// Landing page where every section tries to communicate everything
<section className="bg-gradient-to-br from-purple-500 to-pink-500 text-white py-24">
  <Badge className="animate-pulse bg-yellow-400">🔥 New!</Badge>
  <h1 className="text-7xl font-black bg-clip-text text-transparent bg-gradient-to-r from-yellow-300 to-red-400 animate-shimmer">
    The Revolutionary Platform That Changes Everything
  </h1>
  <p className="text-2xl">Built with AI ✨ for the modern team 🚀 powered by blockchain 🔗</p>

  <div className="flex gap-4 mt-8">
    <Button className="bg-yellow-400 text-black hover:scale-110 animate-bounce">
      Start Free Trial ⭐
    </Button>
    <Button className="bg-pink-300 text-white hover:scale-110">
      Watch Demo 🎥
    </Button>
    <Button className="bg-blue-400 text-white hover:scale-110">
      Read Docs 📖
    </Button>
    <Button className="bg-green-400 text-white hover:scale-110">
      Book Call 📞
    </Button>
  </div>

  <div className="mt-12 grid grid-cols-4 gap-4">
    <Stat number="1M+" label="Users" />
    <Stat number="50+" label="Countries" />
    <Stat number="99.9%" label="Uptime" />
    <Stat number="24/7" label="Support" />
  </div>

  <p className="text-yellow-300 animate-pulse">⚡ Limited Time: 50% Off!</p>
</section>
```

**Violates:** Rule 5.7 (restraint earns trust) AND DESIGN Rule 5.3 (simplest wins). See `rules.md#rule-57-restraint-earns-trust`.

**Why it fails:** Every element competes for attention; nothing wins. Gradients in the background AND text. Four CTAs of equal visual weight (no hierarchy of action — what does the user do?). Emoji-decorated copy reads as performative excitement. Pulsing animations on multiple elements. "Limited time" + "50% off" + "🔥" + animated gradients accumulate into the visual signal of "we want you to believe this is exciting." Users perceive this as anxious, not confident. Trust erodes — products that feel desperate read as low-quality.

**Source for failure mode:** AI optimizes for "thorough" and "impressive" — both bias toward accumulation. Restraint is harder to generate from training data because restraint isn't visually impressive in screenshots.

### CP-8: Restraint — one thing prominent, supporting context

**Pattern:**

```tsx
<section className="px-6 py-32 max-w-content mx-auto">
  <h1 className="text-display text-neutral-900 max-w-prose">
    Process payments in 8 lines of code.
  </h1>
  <p className="text-body-lg mt-6 text-neutral-600 max-w-prose">
    Stripe handles billions in transactions for millions of businesses.
  </p>

  {/* ONE primary action; secondary action visually subordinate */}
  <div className="mt-10 flex items-center gap-6">
    <Button size="lg">Start now</Button>
    <a href="/docs" className="text-body font-medium text-primary-600 hover:text-primary-700">
      View documentation →
    </a>
  </div>

  {/* Supporting stats — small, neutral, in service of credibility */}
  <p className="text-caption text-neutral-500 mt-16">
    Trusted by businesses processing over $1T per year.
  </p>
</section>
```

**Pairs with:** Anti-pattern AP-8

**Why it works:** One headline. One subtitle. One primary action. One secondary action (visually subordinate, not equally-weighted). One supporting credibility line. Most of the page is whitespace and neutral content. The single primary action gets all the user's attention because nothing else competes. The page reads as confident — the product doesn't need to shout because it's secure in what it offers.

**High-craft reference:** Vercel (vercel.com). Their landing page is almost shockingly restrained — black background, white text, one accent color, generous whitespace, one primary CTA per section. The restraint signals confidence: "we don't need to convince you with effects; the product speaks for itself." Stripe similarly: even their elaborate product visualizations are surrounded by significant whitespace; nothing competes with the focal element. Linear: marketing site is mostly neutral; one accent color; product UI visualizations carry the message.

---

## Pairing discipline

Per `DEC-2026-05-17-003` Clause 1: every anti-pattern is paired with a canonical pattern. The framework's value depends on showing the user both what to reject and what to write instead.

High-craft reference sites (Stripe, Vercel, Linear, Monogram, Kraken) appear in CP examples per `DEC-2026-05-17-004` Clause 6 as **comparative pattern references**, not authoritative citations. They illustrate craft patterns by example; the underlying principles are codified in this skill's rules with authoritative grounding from Apple HIG, Material Design 3, Nielsen heuristics, and WCAG 2.2.

When a new UI-CRAFT anti-pattern is observed during use but no clear canonical pattern is obvious, log to `WAIVER-LOG.md` for revisit rather than shipping a one-sided entry. As high-craft reference sites evolve over time, examples may need refresh — captured in the `refresh-recommended` frontmatter field.
