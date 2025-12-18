# FindMyJournal - תכנית עבודה מקיפה
## Master Plan for Parallel Agent Execution

**תאריך:** December 17, 2024  
**מטרה:** תיקון באגים, הסרת מידע שקרי, ושיפור עיצוב לקהל אקדמי  
**תיאום:** כל הסוכנים עובדים במקביל ודוחפים ל-Git בסיום

---

## 🧠 PROJECT_MEMORY - חובה לכל הסוכנים!

**קובץ מרכזי לתיעוד:** `C:\Users\shait\Documents\-Find-My-Journal-\PROJECT_MEMORY.md`

### כללים לתיעוד:

1. **כל סוכן חייב לקרוא את PROJECT_MEMORY.md בתחילת העבודה**
2. **כל סוכן חייב לעדכן את PROJECT_MEMORY.md בסיום כל משימה**
3. **פורמט עדכון:**

```markdown
## [תאריך] - [שם הסוכן]

### משימות שבוצעו:
- [x] תיאור המשימה
- [x] תיאור המשימה

### קבצים ששונו:
- `path/to/file.tsx` - תיאור השינוי
- `path/to/file.py` - תיאור השינוי

### בעיות שנתקלתי בהן:
- בעיה X - פתרון Y

### הערות לסוכנים אחרים:
- הערה חשובה לתיאום

### סטטוס: ✅ הושלם / ⏳ בתהליך / ❌ נתקע
```

### מבנה PROJECT_MEMORY.md:

```markdown
# FindMyJournal - Project Memory
## Central Documentation for All Agents

### 🎯 Current Sprint: December 17, 2024
**Goal:** Fix bugs, remove false claims, academic design update

---

## 📊 Task Status Board

| Task ID | Description | Agent | Status | Updated |
|---------|-------------|-------|--------|---------|
| C1 | Fix Match Score | backend-agent | ⏳ | |
| C2 | Remove 20k researchers | frontend-agent | ⏳ | |
| ... | ... | ... | ... | ... |

---

## 📝 Agent Activity Log

[Agents add their updates here in reverse chronological order]

---

## 🔗 Dependencies & Conflicts

[Document any dependencies between tasks or conflicts found]

---

## 💡 Decisions Made

[Document important decisions and their rationale]
```

---

## 📋 סיכום הבעיות שזוהו

### 🔴 קריטי (Critical)
| # | בעיה | עמוד | סוכן אחראי |
|---|------|------|------------|
| C1 | Match Score מציג 2845% במקום 28% | Search Results | backend-agent |
| C2 | מידע שקרי: "20,000+ Researchers" | Landing, Login | frontend-agent |
| C3 | מידע שקרי: "150+ Countries" | Landing | frontend-agent |
| C4 | מידע שקרי: "98% Accuracy" | Landing | frontend-agent |
| C5 | מידע שקרי: "2M+ Papers Analyzed" | Landing | frontend-agent |
| C6 | אנימציית רקע נעה (מסיחה) | Login/Signup | frontend-agent |

### 🟠 בינוני (Medium)
| # | בעיה | עמוד | סוכן אחראי |
|---|------|------|------------|
| M1 | פיצ'רים לא קיימים מפורסמים (IF, Acceptance Rate, etc.) | Landing | frontend-agent |
| M2 | "Why It's a Good Fit" - טקסט גנרי מדי | Search Results | backend-agent |
| M3 | Discipline Detection - פספס Endocrinology | Search Results | backend-agent |
| M4 | H-Index label לא ברור | Search Results | frontend-agent |
| M5 | צבעים צרכניים מדי (Cyan בוהק) | All Pages | ui-ux-agent |

### 🟡 שיפורים (Enhancements)
| # | בעיה | עמוד | סוכן אחראי |
|---|------|------|------------|
| E1 | הוסף שדות לטופס הרשמה (Title, First/Last Name) | Signup | frontend-agent + backend-agent |
| E2 | פרסונליזציה - פנייה בשם | Search Results | frontend-agent |
| E3 | עיצוב אקדמי יותר - צבעים מאופקים | All Pages | ui-ux-agent |
| E4 | עדכן 50,000+ Journals למספר אמיתי מ-OpenAlex | Landing | backend-agent |

---

## 🤖 חלוקת עבודה לסוכנים

### 1. ORCHESTRATOR (`orchestrator.md`)
```
תפקיד: תיאום כללי ומעקב התקדמות

⚠️ PROJECT_MEMORY:
- קרא PROJECT_MEMORY.md לפני הפעלת סוכנים
- וודא שכל סוכן מעדכן את הקובץ
- עקוב אחר Status Board

משימות:
1. קרא PROJECT_MEMORY.md
2. הפעל את כל הסוכנים במקביל
3. עקוב אחר סטטוס כל משימה ב-PROJECT_MEMORY.md
4. פתור קונפליקטים אם יש
5. וודא שכולם סיימו לפני Git push
6. בצע merge של כל השינויים

פקודת הפעלה:
/orchestrator start-parallel-work --plan="MasterPlan-Dec17"
```

### 2. FRONTEND-AGENT (`frontend-agent.md`)
```
תפקיד: תיקוני Frontend ו-UI

⚠️ PROJECT_MEMORY - חובה!
- קרא PROJECT_MEMORY.md לפני תחילת עבודה
- עדכן Status Board כשמתחיל משימה (⏳ → 🔄)
- עדכן Activity Log בסיום כל משימה
- תעד קבצים ששינית

משימות:
├── C2: הסר "20,000+ Researchers" מ-Landing + Login
├── C3: הסר "150+ Countries" מ-Landing
├── C4: הסר "98% Accuracy" מ-Landing
├── C5: הסר "2M+ Papers Analyzed" מ-Landing
├── C6: בטל אנימציית רקע נעה ב-Login/Signup
├── M1: הסר פיצ'רים לא קיימים מ-Landing:
│   ├── Impact Factor
│   ├── Acceptance rates
│   ├── Estimated Publication Times
│   └── Reference Manager Export (Zotero, Mendeley, EndNote)
├── M4: שנה label מ-"H-Index" ל-"Journal H-Index"
└── E2: הוסף פרסונליזציה עם שם משתמש (אם זמין)

קבצים לעריכה:
- frontend/src/pages/Landing.tsx
- frontend/src/pages/Login.tsx
- frontend/src/pages/Signup.tsx
- frontend/src/components/search/AIAnalysisHeader.tsx
- frontend/src/components/search/AccordionJournalCard.tsx

בדיקה:
npm run build && npm run lint

📝 בסיום - עדכן PROJECT_MEMORY.md!
```

### 3. BACKEND-AGENT (`backend-agent.md`)
```
תפקיד: תיקוני Backend ו-API

⚠️ PROJECT_MEMORY - חובה!
- קרא PROJECT_MEMORY.md לפני תחילת עבודה
- עדכן Status Board כשמתחיל משימה
- עדכן Activity Log בסיום כל משימה
- תעד קבצים ששינית והחלטות שקיבלת

משימות:
├── C1: תקן חישוב Match Score (relevance_score conversion)
│   ├── Debug: console.log raw relevance_score
│   ├── Fix: וודא תוצאה 0-100, לא יותר
│   └── Cap: Math.min(score, 100)
├── M2: שפר match_reason להיות יותר ספציפי
├── M3: שפר Discipline Detection (הוסף Endocrinology)
├── E1: הוסף שדות למודל User:
│   ├── title (Dr./Prof./Mr./Ms.)
│   ├── first_name
│   └── last_name
└── E4: שלוף מספר כתבי עת אמיתי מ-OpenAlex

קבצים לעריכה:
- backend/app/services/search_service.py
- backend/app/models/user.py
- backend/app/schemas/user.py
- backend/app/api/routes/search.py

בדיקה:
pytest && python -m mypy .

📝 בסיום - עדכן PROJECT_MEMORY.md!
```

### 4. UI-UX-AGENT (`ui-ux-agent.md`)
```
תפקיד: שיפור עיצוב לקהל אקדמי

⚠️ PROJECT_MEMORY - חובה!
- קרא PROJECT_MEMORY.md - יש שם פלטת צבעים מוגדרת!
- עדכן Status Board כשמתחיל משימה
- תעד את ה-Design Tokens שיצרת

משימות:
├── M5: עדכן צבעים לפלטה אקדמית:
│   ├── Primary: Navy (#1e3a5f) במקום Cyan
│   ├── Secondary: Slate Blue (#4a6fa5)
│   ├── Accent: Teal (#0d9488) מאופק
│   └── Background: Warm Gray (#f8f9fa)
├── E3: הסר גרדיאנטים בוהקים
├── עדכן Match Score badge לצבע נייבי/אפור
└── צור Design Tokens file לעקביות

קבצים לעריכה/ליצירה:
- frontend/src/styles/design-tokens.css (חדש)
- frontend/tailwind.config.js
- frontend/src/index.css

Color Palette (Academic) - מוגדר ב-PROJECT_MEMORY.md:
--color-primary: #1e3a5f;      /* Navy */
--color-secondary: #4a6fa5;    /* Slate Blue */
--color-accent: #0d9488;       /* Teal */
--color-success: #059669;      /* Emerald */
--color-warning: #d97706;      /* Amber */
--color-background: #f8fafc;   /* Slate 50 */
--color-surface: #ffffff;
--color-text: #1e293b;         /* Slate 800 */
--color-text-muted: #64748b;   /* Slate 500 */

📝 בסיום - עדכן PROJECT_MEMORY.md!
```

### 5. QA-AGENT (`qa-agent.md`)
```
תפקיד: בדיקות ווידוא איכות

⚠️ PROJECT_MEMORY - חובה!
- קרא PROJECT_MEMORY.md לראות מה שונה
- בדוק שכל המשימות מסומנות ✅ לפני שמתחיל
- עדכן Testing Checklist ב-PROJECT_MEMORY.md

משימות:
├── הרץ Playwright E2E tests
├── וודא Match Score מציג 0-100%
├── וודא אין מידע שקרי בדפים
├── וודא אנימציות בוטלו
├── צלם screenshots לפני/אחרי
└── דווח על בעיות שנותרו ב-PROJECT_MEMORY.md

פקודות:
cd frontend
npx playwright test tests/e2e/search-results.spec.ts
npx playwright test tests/e2e/ui-audit.spec.ts

📝 בסיום - עדכן Testing Checklist ב-PROJECT_MEMORY.md!
```

### 6. DOCS-AGENT (`docs-agent.md`)
```
תפקיד: עדכון תיעוד

⚠️ PROJECT_MEMORY - חובה!
- קרא PROJECT_MEMORY.md לראות את כל השינויים
- השתמש ב-Activity Log כמקור ל-CHANGELOG
- תעד את פלטת הצבעים החדשה מ-PROJECT_MEMORY.md

משימות:
├── עדכן README עם שינויים
├── תעד את פלטת הצבעים החדשה (מ-PROJECT_MEMORY.md)
├── תעד את שדות User החדשים
├── צור CHANGELOG entry מבוסס על Activity Log
├── עדכן API docs אם רלוונטי
└── ⭐ עדכן CLAUDE.md עם מידע עדכני על המערכת (ראה פירוט למטה)

קבצים:
- README.md
- CHANGELOG.md
- docs/design-system.md (חדש)
- docs/api-reference.md
- CLAUDE.md ⭐ (קובץ מידע מרכזי על הפרויקט)

📝 בסיום - עדכן PROJECT_MEMORY.md!
```

### 6.1 CLAUDE.md - מבנה מומלץ לעדכון
```markdown
# FindMyJournal - Project Overview

## 🎯 What is FindMyJournal?
[תיאור קצר של המערכת ומה היא עושה]

## 🏗️ Architecture
### Frontend
- Framework: React + TypeScript + Vite
- Styling: Tailwind CSS
- Key components: [רשימה]

### Backend  
- Framework: FastAPI + Python
- Database: [סוג]
- External APIs: OpenAlex

## 📊 Current Features (Actually Implemented)
- [x] Feature 1
- [x] Feature 2
- [ ] Feature 3 (planned)

## 🎨 Design System
- Color Palette: Navy/Slate (Academic)
- Typography: [פונטים]
- Components: [רשימה]

## 📁 Project Structure
[מבנה תיקיות]

## 🔧 Development
### Setup
[הוראות התקנה]

### Running
[פקודות הרצה]

### Testing
[פקודות בדיקה]

## 📈 Data Sources
- OpenAlex: Journal metadata, H-Index, topics
- [מקורות עתידיים]

## 🚀 Deployment
[מידע על deployment]

## 📝 Recent Changes
[שינויים אחרונים - מעודכן אוטומטית]

## 👥 For AI Agents
[הנחיות ספציפיות לסוכני AI שעובדים על הפרויקט]
```

### 7. DEVOPS-AGENT (`devops-agent.md`)
```
תפקיד: Git ו-Deployment

⚠️ PROJECT_MEMORY - חובה!
- קרא PROJECT_MEMORY.md לפני push
- וודא שכל המשימות ב-Status Board מסומנות ✅
- וודא ש-Testing Checklist הושלם
- השתמש ב-Activity Log ליצירת commit message מפורט

משימות (בסיום העבודה):
├── בדוק שכל Tasks ב-PROJECT_MEMORY.md = ✅
├── git add .
├── git commit -m "[message from Activity Log]"
├── git push origin main
└── וודא build עובר ב-CI

Commit Message Format:
fix: resolve critical issues and improve academic UX

- Fix Match Score calculation (was showing 2845% instead of 28%)
- Remove false statistics (20k researchers, 150 countries, etc.)
- Remove non-existent features from landing page
- Disable distracting background animations on auth pages
- Update color palette to academic-friendly navy/slate
- Add Journal H-Index label clarification
- Add user profile fields (title, first_name, last_name)

📝 בסיום - עדכן PROJECT_MEMORY.md עם Git hash ותאריך push!
```

---

## 🔄 תרשים זרימה - עבודה מקבילית

```
                    ┌─────────────────┐
                    │   ORCHESTRATOR  │
                    │   Start Work    │
                    └────────┬────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
         ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ FRONTEND-AGENT  │ │ BACKEND-AGENT   │ │  UI-UX-AGENT    │
│                 │ │                 │ │                 │
│ - Remove stats  │ │ - Fix Match %   │ │ - Color palette │
│ - Remove anim   │ │ - Fix Discipline│ │ - Design tokens │
│ - Remove features│ │ - Add User fields│ │ - Remove gradients│
└────────┬────────┘ └────────┬────────┘ └────────┬────────┘
         │                   │                   │
         └───────────────────┼───────────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │    QA-AGENT     │
                    │  Run All Tests  │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │   DOCS-AGENT    │
                    │ Update Docs     │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  DEVOPS-AGENT   │
                    │  Git Push       │
                    └─────────────────┘
```

---

## 📝 פקודת הפעלה ראשית

```bash
# הפעל את ה-Orchestrator עם התכנית
claude --agent orchestrator \
  --task "Execute MasterPlan-Dec17" \
  --parallel-agents "frontend-agent,backend-agent,ui-ux-agent" \
  --sequential-agents "qa-agent,docs-agent,devops-agent" \
  --auto-git-push true
```

---

## ✅ Definition of Done

- [ ] כל באגים קריטיים (C1-C6) תוקנו
- [ ] כל המידע השקרי הוסר
- [ ] פיצ'רים לא קיימים הוסרו מ-Landing
- [ ] אנימציות מסיחות בוטלו
- [ ] צבעים עודכנו לפלטה אקדמית
- [ ] כל הבדיקות עוברות
- [ ] תיעוד עודכן
- [ ] CLAUDE.md עודכן עם מידע עדכני על המערכת ⭐
- [ ] PROJECT_MEMORY.md מעודכן עם כל הפעילות
- [ ] שינויים נדחפו ל-Git
- [ ] Build עובר ב-CI

---

## 🚨 הערות חשובות

1. **אל תוסיף מידע שקרי** - עדיף להסיר מאשר להמציא
2. **בדוק לפני Push** - npm run build && npm run lint
3. **תאם בין סוכנים** - אם יש קונפליקט, דווח ל-Orchestrator
4. **צלם screenshots** - לפני ואחרי כל שינוי משמעותי

---

## 📊 מעקב התקדמות

| סוכן | סטטוס | הערות |
|------|-------|-------|
| frontend-agent | ⏳ Pending | |
| backend-agent | ⏳ Pending | |
| ui-ux-agent | ⏳ Pending | |
| qa-agent | ⏳ Waiting | מחכה לשאר |
| docs-agent | ⏳ Waiting | מחכה ל-QA |
| devops-agent | ⏳ Waiting | מחכה לכולם |

---

**עדכון אחרון:** December 17, 2024