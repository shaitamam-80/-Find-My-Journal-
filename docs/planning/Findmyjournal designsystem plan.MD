# FindMyJournal - Design System Upgrade Plan
## Sprint: Design System Overhaul (Based on MedAI Hub Principles)

**תאריך:** December 17, 2024  
**מטרה:** שדרוג מערכת העיצוב לסטנדרט אקדמי-רפואי מקצועי  
**בסיס:** עקרונות עיצוב MedAI Hub

---

## 🛠️ Available Slash Commands

השתמש בפקודות הבאות במהלך העבודה:

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `/frontend-design` | עיצוב כללי | תכנון מבנה ופריסה |
| `/frontend-excellence:frontend` | Best practices | לפני כתיבת קוד |
| `/frontend-excellence:react` | React patterns | קומפוננטות חדשות |
| `/frontend-excellence:state` | State management | ניהול מצב |
| `/frontend-excellence:ui` | UI components | עיצוב רכיבים |

---

## 📋 Phase 1: Foundation (CSS Variables & Colors)

### 1.1 Create Design Tokens File

**Command:** `/frontend-design` → "Create CSS variables system with HSL colors"

**File:** `frontend/src/styles/design-tokens.css`

```css
@layer base {
  :root {
    /* ===== Brand Colors - Academic/Medical ===== */
    --primary: 222.2 47.4% 11.2%;           /* #0F172A - Slate 900 */
    --primary-foreground: 210 40% 98%;       /* White */
    
    /* Secondary & Muted */
    --secondary: 210 40% 96.1%;              /* Light gray */
    --secondary-foreground: 222.2 47.4% 11.2%;
    --muted: 210 40% 96.1%;
    --muted-foreground: 215.4 16.3% 46.9%;   /* Gray text */
    
    /* Accent */
    --accent: 210 40% 96.1%;
    --accent-foreground: 222.2 47.4% 11.2%;
    
    /* ===== Semantic Status Colors (Journal Categories) ===== */
    --status-top-tier: 142.1 76.2% 36.3%;    /* Green - Top journals */
    --status-niche: 221.2 83.2% 53.3%;       /* Blue - Niche specialists */
    --status-methodology: 270 60% 50%;        /* Purple - Methodology focused */
    --status-broad: 47.9 95.8% 53.1%;        /* Amber - Broad scope */
    
    /* Match Score Colors */
    --match-high: 142.1 76.2% 36.3%;         /* Green 85%+ */
    --match-medium: 47.9 95.8% 53.1%;        /* Amber 50-84% */
    --match-low: 215.4 16.3% 46.9%;          /* Gray <50% */
    
    /* ===== UI Colors ===== */
    --background: 0 0% 100%;                  /* White */
    --foreground: 222.2 84% 4.9%;            /* Near black */
    --card: 0 0% 100%;
    --card-foreground: 222.2 84% 4.9%;
    
    /* Borders & Inputs */
    --border: 214.3 31.8% 91.4%;
    --input: 214.3 31.8% 91.4%;
    --ring: 222.2 84% 4.9%;
    
    /* Radius */
    --radius: 0.5rem;
    
    /* ===== Feedback Colors ===== */
    --success: 142.1 76.2% 36.3%;            /* Green */
    --warning: 47.9 95.8% 53.1%;             /* Amber */
    --error: 346.8 77.2% 49.8%;              /* Red */
    --info: 221.2 83.2% 53.3%;               /* Blue */
  }

  /* ===== Dark Mode ===== */
  .dark {
    --background: 222.2 84% 4.9%;            /* Dark blue-black */
    --foreground: 210 40% 98%;               /* Off-white */
    
    --primary: 210 40% 98%;
    --primary-foreground: 222.2 47.4% 11.2%;
    
    --secondary: 217.2 32.6% 17.5%;
    --secondary-foreground: 210 40% 98%;
    
    --muted: 217.2 32.6% 17.5%;
    --muted-foreground: 215 20.2% 65.1%;
    
    --card: 222.2 84% 4.9%;
    --card-foreground: 210 40% 98%;
    
    --border: 217.2 32.6% 17.5%;
    --input: 217.2 32.6% 17.5%;
  }
}
```

### 1.2 Update Tailwind Config

**Command:** `/frontend-excellence:ui` → "Configure Tailwind with HSL CSS variables"

**File:** `frontend/tailwind.config.js`

```javascript
/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        // Base colors from CSS variables
        border: 'hsl(var(--border))',
        input: 'hsl(var(--input))',
        ring: 'hsl(var(--ring))',
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        
        primary: {
          DEFAULT: 'hsl(var(--primary))',
          foreground: 'hsl(var(--primary-foreground))',
        },
        secondary: {
          DEFAULT: 'hsl(var(--secondary))',
          foreground: 'hsl(var(--secondary-foreground))',
        },
        muted: {
          DEFAULT: 'hsl(var(--muted))',
          foreground: 'hsl(var(--muted-foreground))',
        },
        accent: {
          DEFAULT: 'hsl(var(--accent))',
          foreground: 'hsl(var(--accent-foreground))',
        },
        card: {
          DEFAULT: 'hsl(var(--card))',
          foreground: 'hsl(var(--card-foreground))',
        },
        
        // Journal Category Status Colors
        status: {
          'top-tier': 'hsl(var(--status-top-tier))',
          'niche': 'hsl(var(--status-niche))',
          'methodology': 'hsl(var(--status-methodology))',
          'broad': 'hsl(var(--status-broad))',
        },
        
        // Match Score Colors
        match: {
          high: 'hsl(var(--match-high))',
          medium: 'hsl(var(--match-medium))',
          low: 'hsl(var(--match-low))',
        },
        
        // Feedback Colors
        success: 'hsl(var(--success))',
        warning: 'hsl(var(--warning))',
        error: 'hsl(var(--error))',
        info: 'hsl(var(--info))',
      },
      
      borderRadius: {
        lg: 'var(--radius)',
        md: 'calc(var(--radius) - 2px)',
        sm: 'calc(var(--radius) - 4px)',
      },
      
      fontFamily: {
        sans: ['var(--font-sans)', 'var(--font-hebrew)', 'ui-sans-serif', 'system-ui'],
        mono: ['var(--font-mono)', 'ui-monospace', 'SFMono-Regular'],
      },
    },
  },
  plugins: [],
}
```

---

## 📋 Phase 2: Typography & Fonts

### 2.1 Add Professional Fonts

**Command:** `/frontend-excellence:frontend` → "Add Google Fonts for academic interface"

**File:** `frontend/index.html`

```html
<head>
  <!-- Preconnect for performance -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  
  <!-- Fonts: Inter (English), Assistant (Hebrew), JetBrains Mono (Code) -->
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Assistant:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
</head>
```

**File:** `frontend/src/index.css` (add to top)

```css
@import './styles/design-tokens.css';

:root {
  --font-sans: 'Inter', sans-serif;
  --font-hebrew: 'Assistant', sans-serif;
  --font-mono: 'JetBrains Mono', monospace;
}

body {
  font-family: var(--font-sans), var(--font-hebrew), ui-sans-serif, system-ui;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* Monospace for queries and code */
.font-mono, code, pre, .query-display {
  font-family: var(--font-mono), ui-monospace, monospace;
}
```

---

## 📋 Phase 3: RTL Support (Logical Properties)

### 3.1 Global RTL Fixes

**Command:** `/frontend-excellence:ui` → "Convert physical margins to logical properties for RTL"

**Search & Replace across all components:**

| Find | Replace | Meaning |
|------|---------|---------|
| `ml-` | `ms-` | Margin Start |
| `mr-` | `me-` | Margin End |
| `pl-` | `ps-` | Padding Start |
| `pr-` | `pe-` | Padding End |
| `text-left` | `text-start` | Text align start |
| `text-right` | `text-end` | Text align end |
| `left-` | `start-` | Position start |
| `right-` | `end-` | Position end |
| `rounded-l-` | `rounded-s-` | Border radius start |
| `rounded-r-` | `rounded-e-` | Border radius end |

**Note:** Keep `ml-auto` and `mr-auto` for centering (they work the same)

---

## 📋 Phase 4: Component Updates

### 4.1 Create Status Badge Component

**Command:** `/frontend-excellence:react` → "Create reusable StatusBadge component"

**File:** `frontend/src/components/ui/StatusBadge.tsx`

```tsx
import { cn } from '@/lib/utils';

type CategoryType = 'top-tier' | 'niche' | 'methodology' | 'broad';

interface StatusBadgeProps {
  category: CategoryType;
  className?: string;
}

const categoryStyles: Record<CategoryType, string> = {
  'top-tier': 'bg-emerald-100 text-emerald-800 border-emerald-200',
  'niche': 'bg-blue-100 text-blue-800 border-blue-200',
  'methodology': 'bg-purple-100 text-purple-800 border-purple-200',
  'broad': 'bg-amber-100 text-amber-800 border-amber-200',
};

const categoryLabels: Record<CategoryType, string> = {
  'top-tier': 'Top-Tier',
  'niche': 'Niche Specialist',
  'methodology': 'Methodology',
  'broad': 'Broad Scope',
};

export function StatusBadge({ category, className }: StatusBadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border',
        categoryStyles[category],
        className
      )}
    >
      {categoryLabels[category]}
    </span>
  );
}
```

### 4.2 Create Match Score Badge Component

**Command:** `/frontend-excellence:react` → "Create MatchScoreBadge with semantic colors"

**File:** `frontend/src/components/ui/MatchScoreBadge.tsx`

```tsx
import { cn } from '@/lib/utils';

interface MatchScoreBadgeProps {
  score: number;
  className?: string;
}

function getScoreLevel(score: number): 'high' | 'medium' | 'low' {
  if (score >= 85) return 'high';
  if (score >= 50) return 'medium';
  return 'low';
}

const scoreStyles = {
  high: 'bg-emerald-600 text-white',
  medium: 'bg-amber-500 text-white',
  low: 'bg-slate-400 text-white',
};

export function MatchScoreBadge({ score, className }: MatchScoreBadgeProps) {
  const level = getScoreLevel(score);
  
  return (
    <div
      className={cn(
        'flex flex-col items-center justify-center rounded-lg px-3 py-2 min-w-[60px]',
        scoreStyles[level],
        className
      )}
    >
      <span className="text-lg font-bold">{score}%</span>
      <span className="text-xs opacity-90">Match</span>
    </div>
  );
}
```

### 4.3 Update Category Section Colors

**Command:** `/frontend-excellence:ui` → "Update CategorySection with new design tokens"

**File:** `frontend/src/components/search/CategorySection.tsx`

```tsx
// Update the category config to use new semantic colors
const categoryConfig = {
  topTier: {
    title: 'Top-Tier Journals',
    subtitle: 'Highest impact, most competitive',
    icon: Star,
    bgClass: 'bg-emerald-50',
    borderClass: 'border-emerald-200',
    iconBgClass: 'bg-emerald-100',
    iconTextClass: 'text-emerald-600',
    badgeClass: 'bg-emerald-100 text-emerald-800',
  },
  niche: {
    title: 'Niche Specialists',
    subtitle: 'Field-specific, targeted audience',
    icon: Target,
    bgClass: 'bg-blue-50',
    borderClass: 'border-blue-200',
    iconBgClass: 'bg-blue-100',
    iconTextClass: 'text-blue-600',
    badgeClass: 'bg-blue-100 text-blue-800',
  },
  methodology: {
    title: 'Methodology-Focused',
    subtitle: 'Methods and techniques emphasis',
    icon: FlaskConical,
    bgClass: 'bg-purple-50',
    borderClass: 'border-purple-200',
    iconBgClass: 'bg-purple-100',
    iconTextClass: 'text-purple-600',
    badgeClass: 'bg-purple-100 text-purple-800',
  },
  broad: {
    title: 'Broad Scope',
    subtitle: 'Interdisciplinary, wide reach',
    icon: Globe,
    bgClass: 'bg-amber-50',
    borderClass: 'border-amber-200',
    iconBgClass: 'bg-amber-100',
    iconTextClass: 'text-amber-600',
    badgeClass: 'bg-amber-100 text-amber-800',
  },
};
```

---

## 📋 Phase 5: Dark Mode Support

### 5.1 Add Dark Mode Toggle

**Command:** `/frontend-excellence:state` → "Add dark mode state management"

**File:** `frontend/src/hooks/useDarkMode.ts`

```tsx
import { useState, useEffect } from 'react';

export function useDarkMode() {
  const [isDark, setIsDark] = useState(() => {
    if (typeof window === 'undefined') return false;
    return localStorage.getItem('theme') === 'dark' ||
      (!localStorage.getItem('theme') && 
       window.matchMedia('(prefers-color-scheme: dark)').matches);
  });

  useEffect(() => {
    const root = document.documentElement;
    if (isDark) {
      root.classList.add('dark');
      localStorage.setItem('theme', 'dark');
    } else {
      root.classList.remove('dark');
      localStorage.setItem('theme', 'light');
    }
  }, [isDark]);

  return { isDark, toggle: () => setIsDark(!isDark) };
}
```

### 5.2 Dark Mode Toggle Button

**File:** `frontend/src/components/ui/ThemeToggle.tsx`

```tsx
import { Moon, Sun } from 'lucide-react';
import { useDarkMode } from '@/hooks/useDarkMode';

export function ThemeToggle() {
  const { isDark, toggle } = useDarkMode();
  
  return (
    <button
      onClick={toggle}
      className="p-2 rounded-lg bg-secondary hover:bg-secondary/80 transition-colors"
      aria-label={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
    >
      {isDark ? (
        <Sun className="h-5 w-5 text-foreground" />
      ) : (
        <Moon className="h-5 w-5 text-foreground" />
      )}
    </button>
  );
}
```

---

## 📋 Phase 6: Page Updates

### 6.1 Update Landing Page

**Command:** `/frontend-design` → "Redesign Landing page with academic color palette"

**Changes:**
- Replace cyan gradients with slate/navy gradients
- Update CTA buttons to primary color
- Add subtle dark mode support
- Professional typography

### 6.2 Update Login/Signup Pages

**Command:** `/frontend-design` → "Redesign auth pages with academic colors"

**Changes:**
- Solid slate-900 background (no animation)
- Clean white card
- Professional form styling

### 6.3 Update Search Results Page

**Command:** `/frontend-excellence:ui` → "Update search results with semantic status colors"

**Changes:**
- Use StatusBadge for categories
- Use MatchScoreBadge for scores
- Apply new card styling

---

## 🤖 Agent Assignments

### FRONTEND-AGENT
```
Tasks:
├── Phase 1: Create design-tokens.css
├── Phase 2: Add fonts to index.html and index.css
├── Phase 3: Convert all ml/mr to ms/me (RTL)
├── Phase 4: Create StatusBadge, MatchScoreBadge components
├── Phase 5: Add ThemeToggle component
└── Phase 6: Update Landing, Login, Signup pages

Commands to use:
- /frontend-design for layout decisions
- /frontend-excellence:react for component patterns
- /frontend-excellence:ui for styling best practices

Files to modify:
- frontend/src/styles/design-tokens.css (NEW)
- frontend/tailwind.config.js
- frontend/index.html
- frontend/src/index.css
- frontend/src/components/ui/StatusBadge.tsx (NEW)
- frontend/src/components/ui/MatchScoreBadge.tsx (NEW)
- frontend/src/components/ui/ThemeToggle.tsx (NEW)
- frontend/src/hooks/useDarkMode.ts (NEW)
- frontend/src/pages/Landing.tsx
- frontend/src/pages/Login.tsx
- frontend/src/pages/Signup.tsx
- frontend/src/components/search/*.tsx
```

### UI-UX-AGENT
```
Tasks:
├── Review color palette implementation
├── Verify dark mode contrast ratios
├── Test RTL layout
└── Approve final design

Commands to use:
- /frontend-excellence:ui for component review
```

### QA-AGENT
```
Tasks:
├── Test dark mode toggle
├── Test RTL layout in Hebrew
├── Verify all colors match design tokens
├── Screenshot all pages (light + dark)
└── Accessibility audit (contrast ratios)
```

---

## 📊 Color Palette Summary

### Light Mode
| Purpose | CSS Variable | HSL | Hex | Preview |
|---------|-------------|-----|-----|---------|
| Primary | `--primary` | 222.2 47.4% 11.2% | #0F172A | 🟦 Slate 900 |
| Background | `--background` | 0 0% 100% | #FFFFFF | ⬜ White |
| Top-Tier | `--status-top-tier` | 142.1 76.2% 36.3% | #16A34A | 🟩 Green |
| Niche | `--status-niche` | 221.2 83.2% 53.3% | #3B82F6 | 🟦 Blue |
| Methodology | `--status-methodology` | 270 60% 50% | #8B5CF6 | 🟪 Purple |
| Broad | `--status-broad` | 47.9 95.8% 53.1% | #EAB308 | 🟨 Amber |

### Dark Mode
| Purpose | CSS Variable | Hex | Preview |
|---------|-------------|-----|---------|
| Background | `--background` | #0F172A | 🌑 Dark slate |
| Foreground | `--foreground` | #F8FAFC | ⬜ Off-white |

---

## ✅ Definition of Done

- [ ] design-tokens.css created with all CSS variables
- [ ] tailwind.config.js updated with new color mappings
- [ ] Fonts loaded (Inter, Assistant, JetBrains Mono)
- [ ] All ml/mr converted to ms/me for RTL
- [ ] StatusBadge component created
- [ ] MatchScoreBadge component created
- [ ] Dark mode hook and toggle created
- [ ] Landing page updated with new colors
- [ ] Login/Signup pages updated (no animations)
- [ ] Search results using new components
- [ ] Dark mode tested
- [ ] RTL layout tested
- [ ] All tests passing
- [ ] Screenshots captured (light + dark)
- [ ] PROJECT_MEMORY.md updated
- [ ] CLAUDE.md updated with design system info
- [ ] Git pushed

---

## 🚀 Execution Command

```bash
cd C:\Users\shait\Documents\-Find-My-Journal-

claude "
Execute Design System Upgrade Plan from .claude/DesignSystem-Plan.md

IMPORTANT: 
1. Read PROJECT_MEMORY.md first
2. Use slash commands during work:
   - /frontend-design for layout decisions
   - /frontend-excellence:react for component patterns
   - /frontend-excellence:ui for styling
   - /frontend-excellence:state for dark mode state

PHASE ORDER:
1. Create design-tokens.css with CSS variables
2. Update tailwind.config.js
3. Add fonts to index.html
4. Convert ml/mr to ms/me across all components
5. Create StatusBadge, MatchScoreBadge, ThemeToggle components
6. Update Landing, Login, Signup pages
7. Test dark mode and RTL
8. Run all tests
9. Update PROJECT_MEMORY.md and CLAUDE.md
10. Git commit and push

Use /frontend-excellence:ui before creating any new component.
Document all changes in PROJECT_MEMORY.md.
"
```

---

**Last Updated:** December 17, 2024S