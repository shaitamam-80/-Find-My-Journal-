# Tailwind CSS Quick Reference

## Spacing Scale

| Class | Value |
|-------|-------|
| `p-0` | 0 |
| `p-1` | 0.25rem (4px) |
| `p-2` | 0.5rem (8px) |
| `p-3` | 0.75rem (12px) |
| `p-4` | 1rem (16px) |
| `p-6` | 1.5rem (24px) |
| `p-8` | 2rem (32px) |
| `p-12` | 3rem (48px) |

Same scale for: `m-`, `gap-`, `space-x-`, `space-y-`

## Flexbox

```tsx
// Row with gap
"flex items-center gap-4"

// Column
"flex flex-col gap-2"

// Space between
"flex justify-between items-center"

// Center everything
"flex items-center justify-center"

// Wrap items
"flex flex-wrap gap-4"

// Grow/shrink
"flex-1"      // grow and shrink
"flex-none"   // don't grow or shrink
"flex-grow"   // only grow
"flex-shrink-0" // don't shrink
```

## Grid

```tsx
// Basic grid
"grid grid-cols-3 gap-4"

// Responsive grid
"grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"

// Auto-fit cards
"grid grid-cols-[repeat(auto-fit,minmax(300px,1fr))] gap-4"

// Span columns
"col-span-2"
"col-span-full"
```

## Typography

```tsx
// Sizes
"text-xs"    // 12px
"text-sm"    // 14px
"text-base"  // 16px
"text-lg"    // 18px
"text-xl"    // 20px
"text-2xl"   // 24px
"text-3xl"   // 30px

// Weight
"font-normal"   // 400
"font-medium"   // 500
"font-semibold" // 600
"font-bold"     // 700

// Colors
"text-gray-500"   // Muted
"text-gray-700"   // Body
"text-gray-900"   // Headings
"text-blue-600"   // Links
"text-red-600"    // Errors
"text-green-600"  // Success

// Truncate
"truncate"                    // Single line ellipsis
"line-clamp-2"               // 2 lines then ellipsis
"whitespace-nowrap"          // No wrap
"break-words"                // Break long words
```

## Colors

### Gray Scale
```tsx
"bg-gray-50"   // Almost white
"bg-gray-100"  // Light background
"bg-gray-200"  // Borders
"bg-gray-300"  // Disabled
"bg-gray-500"  // Muted text
"bg-gray-700"  // Body text
"bg-gray-900"  // Headings
```

### Primary (Blue)
```tsx
"bg-blue-50"   // Subtle background
"bg-blue-100"  // Hover background
"bg-blue-500"  // Primary
"bg-blue-600"  // Primary hover
"bg-blue-700"  // Primary active
```

### Status Colors
```tsx
// Success
"bg-green-50 text-green-700 border-green-200"

// Warning  
"bg-yellow-50 text-yellow-700 border-yellow-200"

// Error
"bg-red-50 text-red-700 border-red-200"

// Info
"bg-blue-50 text-blue-700 border-blue-200"
```

## Borders & Shadows

```tsx
// Borders
"border"              // 1px solid
"border-2"            // 2px solid
"border-gray-200"     // Light border
"border-gray-300"     // Default border
"rounded"             // 4px
"rounded-lg"          // 8px
"rounded-xl"          // 12px
"rounded-full"        // Pill/circle

// Shadows
"shadow-sm"           // Subtle
"shadow"              // Default
"shadow-md"           // Cards
"shadow-lg"           // Modals
"shadow-xl"           // Dropdowns
```

## Common Component Classes

### Button Primary
```tsx
"px-4 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
```

### Button Secondary
```tsx
"px-4 py-2 border border-gray-300 bg-white text-gray-700 font-medium rounded-lg hover:bg-gray-50 focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 transition-colors"
```

### Button Danger
```tsx
"px-4 py-2 bg-red-600 text-white font-medium rounded-lg hover:bg-red-700 focus:ring-2 focus:ring-red-500 focus:ring-offset-2 transition-colors"
```

### Input Field
```tsx
"w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
```

### Input with Error
```tsx
"w-full px-4 py-2 border border-red-500 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500"
```

### Card
```tsx
"bg-white rounded-xl shadow-md border border-gray-200 p-6"
```

### Card Hoverable
```tsx
"bg-white rounded-xl shadow-md border border-gray-200 p-6 hover:shadow-lg transition-shadow cursor-pointer"
```

### Badge
```tsx
// Default
"inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800"

// Success
"inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800"

// Warning
"inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800"
```

### Avatar
```tsx
// Small
"w-8 h-8 rounded-full bg-gray-200"

// Medium
"w-10 h-10 rounded-full bg-gray-200"

// Large
"w-12 h-12 rounded-full bg-gray-200"
```

## Responsive Breakpoints

| Prefix | Min Width |
|--------|-----------|
| `sm:` | 640px |
| `md:` | 768px |
| `lg:` | 1024px |
| `xl:` | 1280px |
| `2xl:` | 1536px |

### Mobile-First Pattern
```tsx
// Default (mobile) → sm → md → lg
"w-full sm:w-1/2 lg:w-1/3"
"text-sm md:text-base lg:text-lg"
"p-4 md:p-6 lg:p-8"
"grid-cols-1 md:grid-cols-2 lg:grid-cols-3"
```

### Hide/Show Responsive
```tsx
"hidden md:block"      // Hide on mobile, show on md+
"block md:hidden"      // Show on mobile, hide on md+
"hidden lg:flex"       // Hide until lg, then flex
```

## Animations

```tsx
// Transitions
"transition-all"         // All properties
"transition-colors"      // Background, border, text color
"transition-opacity"     // Opacity only
"transition-transform"   // Scale, rotate, translate

// Duration
"duration-150"  // Fast
"duration-300"  // Default
"duration-500"  // Slow

// Hover effects
"hover:scale-105"
"hover:opacity-80"
"hover:-translate-y-1"

// Loading spinner
"animate-spin"
"animate-pulse"
"animate-bounce"
```

## Layout Patterns

### Page Container
```tsx
"max-w-7xl mx-auto px-4 sm:px-6 lg:px-8"
```

### Content Container (Narrow)
```tsx
"max-w-2xl mx-auto"
```

### Full Height Page
```tsx
"min-h-screen flex flex-col"
```

### Sticky Header
```tsx
"sticky top-0 z-50 bg-white border-b"
```

### Fixed Footer
```tsx
"fixed bottom-0 left-0 right-0 bg-white border-t"
```

### Overlay
```tsx
"fixed inset-0 bg-black/50 z-50"
```

### Centered Modal
```tsx
"fixed inset-0 flex items-center justify-center z-50"
```


## RTL Support (Hebrew/Arabic)

### Logical Properties Mapping

| Physical (LTR only) | Logical (RTL-safe) |
|---------------------|-------------------|
| `ml-4` | `ms-4` (margin-start) |
| `mr-4` | `me-4` (margin-end) |
| `pl-4` | `ps-4` (padding-start) |
| `pr-4` | `pe-4` (padding-end) |
| `left-0` | `start-0` |
| `right-0` | `end-0` |
| `text-left` | `text-start` |
| `text-right` | `text-end` |
| `border-l` | `border-s` |
| `border-r` | `border-e` |
| `rounded-l` | `rounded-s` |
| `rounded-r` | `rounded-e` |

### RTL-Safe Component

```tsx
// ❌ Bad - breaks in RTL
<div className="flex items-center ml-4 pl-6 text-left border-l-2">
  <span className="mr-2">Icon</span>
  Text
</div>

// ✅ Good - works in both LTR and RTL
<div className="flex items-center ms-4 ps-6 text-start border-s-2">
  <span className="me-2">Icon</span>
  Text
</div>
```

### RTL Config

```tsx
// App.tsx or layout
<html dir="rtl" lang="he">

// Or dynamically
<div dir={isRTL ? 'rtl' : 'ltr'}>
```

### Common RTL Patterns

```tsx
// Flex direction auto-reverses - no change needed!
"flex items-center gap-4"  // ✅ Works in RTL

// Icons that should flip
<ChevronLeft className="rtl:rotate-180" />

// Conditional spacing
"ms-auto"  // Push to end (right in LTR, left in RTL)
```
