---
name: frontend-design
description: >-
  Comprehensive guide and design system rules for building high-quality, modern,
  responsive, and aesthetically stunning web components and dashboards.
---

# Frontend UI/UX Design System & Guidelines

This skill provides best practices, UI component guidelines, design tokens, and aesthetic principles for building modern web applications.

---

## 🎨 1. Aesthetic Principles & Design Tokens

### Color Palette (Dark Theme / Glassmorphism)
- **Background Layer**: Slate 950 (`#020617`) with subtle radial glow gradients.
- **Card Containers**: Slate 900 with backdrop blur (`backdrop-blur-xl`), `border-slate-800/80` or `border-indigo-500/30`.
- **Primary Accent**: Electric Indigo / Royal Violet (`from-indigo-600 to-purple-600`).
- **Success / Revenue**: Emerald / Mint (`emerald-400`, `emerald-500/10`).
- **Warning / Pending**: Warm Amber / Gold (`amber-400`, `amber-500/20`).
- **Typography**: Inter / Outfit font family with high legibility, strict contrast ratios, and clear hierarchy.

---

## 🧩 2. Component Design Standards

### Cards & Container Glassmorphism
- Use rounded corners (`rounded-2xl` or `rounded-3xl`).
- Subtle drop shadows (`shadow-xl` or `shadow-2xl`).
- Hover states with light border highlights (`hover:border-slate-700` or `hover:scale-[1.01]`).

### Buttons & Interactive Controls
- Primary: Gradient backgrounds (`bg-gradient-to-r from-indigo-600 to-purple-600`) with glow effects (`shadow-lg shadow-indigo-600/30`).
- Secondary: Dark slate pills (`bg-slate-800 hover:bg-slate-700`) with crisp borders (`border border-slate-700/60`).
- Micro-interactions: Smooth scale transitions (`transition-all active:scale-[0.98]`).

---

## 📊 3. Dashboard Data Visualizations

- **Recharts Integration**: Use semi-transparent gradients (`AreaChart`, `BarChart`) with rounded bar caps (`radius={[8, 8, 0, 0]}`).
- **Custom Tooltips**: Styled with dark slate background, rounded corners, clean font spacing, and zero browser defaults.
- **KPI Metrics Cards**: Bold 3XL stat numbers with clear directional badges (`+5.2% ArrowUpRight`) and icon indicators.

---

## ♿ 4. Accessibility & Responsiveness

- Ensure mobile-first flexbox/grid layout (`grid-cols-1 md:grid-cols-2 lg:grid-cols-4`).
- Maintain WCAG AAA/AA color contrast ratios for text on dark backgrounds.
- Add descriptive aria-labels and semantic HTML structure across all components.
