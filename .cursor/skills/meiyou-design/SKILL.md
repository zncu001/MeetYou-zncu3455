---
name: meiyou-design-skill
description: Use when designing or implementing meiyou 美柚 App/H5 UI, mobile product screens, business operation pages, membership/ecommerce pages, component libraries, or Figma-to-code work that must follow 美柚设计语言 rather than generic pink mobile UI.
---

# meiyou Design skill

Use this skill whenever the task involves 美柚 product UI, H5, mobile components, business operation cards, or AI-generated interface drafts for meiyou.

Always apply the guide before generating UI. If the project has a newer local `DESIGN.md`, component library, Figma file, or design token file, prefer the project artifact and treat this skill as the baseline.

Bundled references in this skill folder:

- `design-system.md` — full design specification (color roles, business color mapping, typography scale, layout grid, component rules, scene recipes, acceptance checklist). Read when you need a rule beyond the speed-dial below.
- `ui-kit.html` — a self-contained 美柚 H5 control library demo with real HTML/CSS for every component (buttons, tabs, lists, forms, modals, calendar, period cycle card, community card, membership, cashback, floating actions, etc.) plus light and dark theme tokens. This is the source of truth for actual markup, class names, and CSS variables. Do NOT read the whole file (~350KB). Use grep/search:
  - Look up tokens at the top of the file (`:root { --brand: ... }` and `body.theme-dark { ... }`).
  - Find a component by its `data-component="..."` attribute (e.g. `business-period-cycle-card`, `form-input-code`, `编辑悬浮按钮`) or by its section heading (e.g. `L1-控件-按钮`, `L1-控件-表单`).
  - Copy the markup + matching CSS class block, then adapt — keep class names and tokens consistent with this kit.

## Workflow

Before designing or coding:

1. Identify page type: product feature, health data, community/content, tool recording, ecommerce/membership, operation campaign, modal/sheet, or component library.
2. Identify business context: 经期, 备孕, 怀孕, 育儿, 医疗健康, 会员, or platform-generic.
3. Choose density: tools and transaction flows are compact; reports and operation pages can breathe; do not turn every request into a landing page.
4. Define tokens first: colors, typography, spacing, radius, shadow, states.
5. Build a real screen: navigation, return/close, content hierarchy, primary action, loading/empty/error/disabled states.
6. Add atmosphere last: business colors, illustration, operation font, gradient, and motion only when they clarify hierarchy.
7. Verify 360/375/390/430px mobile widths before finalizing UI code.

## Non-Negotiables

- 美柚 is not generic pink UI. It is female-friendly, warm, clear, rounded, orderly, full, light, and business-aware.
- Brand red is for platform-level primary actions, selected states, focus, key guidance, and core data emphasis.
- Do not use brand red for every icon, state, or business mood.
- Semantic colors must keep their meaning: green for healthy/success, orange for warning, red for danger/risk, fog blue for links and professional/medical entries.
- Business moods are distinct: 经期 uses red/soft red, 备孕 and medical use blue/fog blue, 怀孕 and ovulation use purple, 育儿 uses warm yellow, 会员 uses purple-gold.
- Every page needs a recognizable return, close, or cancel path.
- Positive actions go in the convenient/right/bottom position; negative or cancel actions are weaker and placed away from the primary path.
- Use an 8dp grid, 4dp for small elements/baseline, and keep outside space greater than or equal to inside space.
- Use rounded, continuous-curvature icons and consistent visual weight.
- Do not add heavy shadows, random radii, decorative blur blobs, unrelated tech backgrounds, or large brand-color backgrounds to product screens.

## Core Tokens

Use official project tokens when present. Otherwise use these fallback values:

```css
:root {
  --my-brand-red: #ff4d88;
  --my-brand-soft: rgba(255, 77, 136, 0.08);
  --my-bg: #f2f2f5;
  --my-surface: #ffffff;
  --my-text-primary: #323232;
  --my-text-secondary: #666666;
  --my-text-tertiary: #999999;
  --my-line: rgba(0, 0, 0, 0.08);
  --my-success: #00cc99;
  --my-warning: #ff9500;
  --my-danger: #ff4d4d;
  --my-link: #4f7cae;
  --my-radius-xs: 4px;
  --my-radius-sm: 8px;
  --my-radius-md: 12px;
  --my-space-1: 4px;
  --my-space-2: 8px;
  --my-space-3: 12px;
  --my-space-4: 16px;
  --my-space-6: 24px;
  --my-shadow-1: 0 2px 10px rgba(50, 50, 50, 0.08);
  --my-shadow-2: 0 8px 24px rgba(0, 0, 0, 0.14);
}
```

Typography:

- Use PingFang SC / platform system font.
- Letter spacing stays `0` for Chinese UI.
- Main sizes: 28 page title, 21 module title, 17 nav/body, 15 list, 13/14 support text, 11/12 labels.
- Use weights 400 and 500 by default; 600 only for key data.
- Use `font-variant-numeric: tabular-nums` for aligned numbers.

## Component Defaults

- Primary button: brand red background, white text, 40/44 height, 8px or pill radius, one primary action per region.
- Secondary button: brand-soft background or outline, brand-red text.
- Tertiary/system button: gray/transparent background with neutral text.
- Danger action: danger red, never visually equal to the primary safe action.
- Navigation: left return/close, centered or contextual title, right action if needed.
- Tab bar: icon plus text, selected brand red, badges supported.
- Cards: white surface, 8/12 radius, 12/16 padding, light or no shadow.
- Lists: single row 44/56, double row 64/72, aligned icon/text/meta/arrow.
- Inputs: 8 radius, 12 horizontal padding, clear placeholder, error text, disabled state, count when needed.
- Modals: one theme, one primary action, cancel/close path mandatory.
- Toast: short, 1.5-2s, never blocks the main CTA.
- Empty/error/loading: include action or recovery path.

## Business Recipes

- 经期: white/light-gray base, brand red for selected dates, today state, key data, and primary CTA. Avoid full-screen saturated red.
- 备孕/medical: blue or fog blue for professional trust and detail links. Keep explanations structured as result, reason, suggestion, next step.
- 怀孕: purple mood for pregnancy stage and ovulation-related states. Week number, baby size, and checkup reminders must be first-class.
- 育儿: warm yellow mood, but health and vaccine states still use semantic colors.
- 会员/ecommerce: purple-gold gradient for member identity and benefit blocks only. Price, benefit, countdown, and CTA must remain highly readable.
- Operation/H5: stronger visuals are allowed, but the screen still needs readable theme, benefit, participation path, and primary CTA. Gradients only for cards taller than a double-line list.

## Final Check

Before final response or screenshot handoff, verify:

- The output is a usable interface, not a decorative brand poster.
- Color roles are not mixed.
- Text fits on 360px width.
- Touch targets are at least 44x44.
- Return/close/cancel exists.
- Loading, empty, error, disabled, focus/pressed states exist where relevant.
- The result reads as Meiyou: rounded, orderly, full, light, female-friendly, and business-specific.
