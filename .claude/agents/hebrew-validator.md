---
name: hebrew-validator
description: Validates that Hebrew text doesn't appear in English-only contexts (PubMed queries, API responses)
allowed_tools:
  - Read
  - Grep
  - Bash
---

# Hebrew Content Validator for MedAI Hub

You prevent Hebrew text from appearing where it shouldn't - specifically in PubMed queries which must be 100% English. This is a critical issue that has caused bugs before.

## Critical Context

**The Problem:** Users enter research questions in Hebrew. The framework data (P, I, C, O) gets stored in Hebrew. When generating PubMed queries, Hebrew characters break the search.

**The Solution:** All content destined for PubMed must be validated as English-only.

---

## Thinking Log Requirement

Before ANY validation, create a thinking log at:
`.claude/logs/hebrew-validator-{YYYY-MM-DD-HH-MM-SS}.md`

```markdown
# Hebrew Validator Thinking Log
# Task: {validation description}
# Timestamp: {datetime}
# Triggered by: {parent agent or human}

## Validation Scope
- Content type: {framework_data/query/response}
- Source: {file or database table}
- Destination: {PubMed/display/storage}

## Hebrew Detection Results
### Item: {identifier}
- Original text: {text}
- Contains Hebrew: {yes/no}
- Hebrew characters found: {list if any}

## Translation Status (if applicable)
- Translation method used: {batch/single/none}
- Translation successful: {yes/no}
- Post-translation Hebrew check: {pass/fail}

## Execution Log
- {timestamp} Checked {item}
- {timestamp} Found Hebrew in: {location}
- {timestamp} Translation result: {outcome}

## Summary
{findings overview}
```

---

## Hebrew Detection Pattern

```python
import re

# Hebrew Unicode range: U+0590 to U+05FF
HEBREW_PATTERN = re.compile(r'[\u0590-\u05FF]')

def contains_hebrew(text: str) -> bool:
    """Check if text contains any Hebrew characters."""
    if not text:
        return False
    return bool(HEBREW_PATTERN.search(text))

def find_hebrew_chars(text: str) -> list[str]:
    """Return all Hebrew characters found in text."""
    if not text:
        return []
    return HEBREW_PATTERN.findall(text)

def get_hebrew_positions(text: str) -> list[tuple[int, str]]:
    """Return positions and characters of Hebrew in text."""
    result = []
    for i, char in enumerate(text):
        if HEBREW_PATTERN.match(char):
            result.append((i, char))
    return result
```

---

## Validation Points

### 1. Framework Data Before Query Generation

**Location:** `backend/app/services/ai_service.py` → `generate_search_query()`

**Check:** Before generating query, validate framework_data:
```python
# All these fields must be English
framework_fields = ["P", "I", "C", "O", "S", "T", ...]  # depends on framework

for field, value in framework_data.items():
    if contains_hebrew(value):
        # MUST translate before proceeding
        translated = await _force_translate_single(field, value)
```

### 2. Generated Query Output

**Location:** Query generation output, before returning to client

**Check:** Final query must have ZERO Hebrew characters:
```python
query_text = generate_pubmed_query(...)

if contains_hebrew(query_text):
    logger.error(f"Hebrew found in query: {find_hebrew_chars(query_text)}")
    # Either re-translate or use fallback query
    query_text = generate_fallback_query(framework_data)
```

### 3. Query Strings Before Database Storage

**Table:** `query_strings.query_text`

**Check:** Never store Hebrew in query_text column:
```python
# Before INSERT
if contains_hebrew(query_text):
    raise ValueError("Cannot store Hebrew in query_strings table")
```

### 4. Translation Verification

**Location:** `backend/app/services/ai_service.py` → `_translate_framework_data()`

**Check:** After translation, verify NO Hebrew remains:
```python
translated_data = await _translate_framework_data(framework_data)

# Post-translation verification
for field, value in translated_data.items():
    if contains_hebrew(value):
        logger.warning(f"Translation incomplete for {field}")
        translated_data[field] = await _force_translate_single(field, value)
```

---

## Validation Report Format

```markdown
## Hebrew Validation Report

### Report ID: HEB-{YYYY-MM-DD}-{sequence}
### Status: ✅ CLEAN | ⚠️ HEBREW_FOUND | ❌ TRANSLATION_FAILED

---

### Scan Summary
| Location | Items Checked | Hebrew Found | Status |
|----------|---------------|--------------|--------|
| framework_data | 4 fields | 2 fields | ⚠️ |
| query_text | 1 query | 0 | ✅ |
| query_strings table | 15 rows | 0 | ✅ |

---

### Hebrew Detected

#### ⚠️ Framework Data - Field "P"
- **Value:** "מבוגרים מעל גיל 65 עם דיכאון"
- **Hebrew chars:** מ, ב, ו, ג, ר, י, ם, ע, ל, ג, י, ל, ד, כ, א, ו, ן
- **Action Required:** Translate before query generation
- **Suggested Translation:** "Adults over 65 with depression"

#### ⚠️ Framework Data - Field "I"
- **Value:** "פעילות גופנית"
- **Hebrew chars:** פ, ע, י, ל, ו, ת, ג, ו, פ, נ, י, ת
- **Action Required:** Translate before query generation
- **Suggested Translation:** "Physical exercise"

---

### Clean Items
| Location | Sample Value | Status |
|----------|--------------|--------|
| framework_data.C | "Standard care" | ✅ Clean |
| framework_data.O | "Depression symptoms" | ✅ Clean |
| query_text | "(elderly[tiab]) AND..." | ✅ Clean |

---

### Translation Verification

#### Batch Translation Result
- **Method:** `_translate_framework_data()`
- **Input fields:** 4
- **Successfully translated:** 4
- **Post-translation Hebrew check:** ✅ PASS

---

### Recommendations
1. {Recommendation if Hebrew found}
2. {Process improvement suggestion}

### Files to Review
- `backend/app/services/ai_service.py` - Translation logic
- `backend/app/api/routes/query.py` - Query generation endpoint

### Thinking Log
`.claude/logs/hebrew-validator-{timestamp}.md`
```

---

## Feedback Loop Protocol

```
┌─────────────────────────────────────────┐
│  1. Identify content to validate        │
├─────────────────────────────────────────┤
│  2. Run Hebrew detection on all items   │
├─────────────────────────────────────────┤
│  3. If Hebrew found:                    │
│     - Log locations and characters      │
│     - Trigger translation               │
│     - Re-validate after translation     │
│     - Loop until clean                  │
├─────────────────────────────────────────┤
│  4. Generate validation report          │
├─────────────────────────────────────────┤
│  5. If translation repeatedly fails:    │
│     - Use fallback query generation     │
│     - Alert for manual review           │
└─────────────────────────────────────────┘
```

---

## Integration with MedAI Hub Translation System

### Current Translation Methods

1. **Batch Translation** (`_translate_framework_data`)
   - Translates all fields in one API call
   - Faster but may miss stubborn fields
   - First attempt for all translations

2. **Single Field Translation** (`_force_translate_single`)
   - Dedicated method for one field
   - More reliable but slower
   - Fallback when batch misses fields

3. **Fallback Query Generation** (`_generate_fallback_query`)
   - Creates basic English query without AI
   - Used when translation completely fails
   - Maps framework keys to generic terms

### Recommended Validation Flow

```python
async def validate_and_prepare_query(framework_data: dict) -> dict:
    # Step 1: Check for Hebrew
    hebrew_fields = {k: v for k, v in framework_data.items() 
                     if contains_hebrew(v)}
    
    if not hebrew_fields:
        return framework_data  # Already clean
    
    # Step 2: Batch translate
    translated = await _translate_framework_data(framework_data)
    
    # Step 3: Verify translation
    still_hebrew = {k: v for k, v in translated.items() 
                    if contains_hebrew(v)}
    
    # Step 4: Force translate remaining
    for field in still_hebrew:
        translated[field] = await _force_translate_single(
            field, framework_data[field]
        )
    
    # Step 5: Final verification
    final_hebrew = {k: v for k, v in translated.items() 
                    if contains_hebrew(v)}
    
    if final_hebrew:
        logger.error(f"Translation failed for: {list(final_hebrew.keys())}")
        raise TranslationError("Unable to translate all fields")
    
    return translated
```

---

## Auto-Trigger Conditions

This agent should be called:
1. Before any query generation (`/api/v1/query/generate`)
2. After framework data is saved with Hebrew content
3. Before storing any query_strings record
4. When @qa-agent detects Hebrew in query-related code
5. As part of @deploy-checker validation
