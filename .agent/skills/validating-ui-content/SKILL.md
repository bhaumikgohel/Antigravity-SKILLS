---
name: validating-ui-content
description: Validates UI text content for spelling, grammar, formatting, and consistency issues. Use when testing web pages, reviewing UI copy, checking for content errors, or validating labels and messages.
---

# Smart UI Content Validation Agent

Automates detection of spelling, grammar, formatting, and terminology issues in UI content.

## When to use this skill

- QA is testing a web page or UI screen
- User asks to "check this page for errors"
- Before UI release/content freeze
- Reviewing labels, buttons, error messages
- Validating currency, dates, or numeric formats

## Workflow

- [ ] Capture or receive target webpage/UI URL
- [ ] Crawl and extract visible text content
- [ ] Categorize content (labels, buttons, errors, descriptions)
- [ ] Validate spelling and grammar
- [ ] Check formatting consistency (currency, dates, casing)
- [ ] Identify terminology inconsistencies
- [ ] Generate report with findings and fixes

## Instructions

### Step 1: Capture UI Content

Methods to extract text:
- **Web page**: Use headless browser (Playwright/Puppeteer)
- **Screenshot + OCR**: For non-web UIs
- **DOM extraction**: JavaScript `document.body.innerText`

Elements to capture:
- Headings (H1-H6)
- Labels and form placeholders
- Button text
- Error/success messages
- Tooltips and help text
- Modal/dialog content

### Step 2: Content Categorization

Group extracted text by type:

| Category | Examples | Validation Focus |
|----------|----------|------------------|
| Navigation | Menu items, breadcrumbs | Consistency, capitalization |
| Actions | Buttons, links | Verb consistency, clarity |
| Forms | Labels, placeholders, hints | Completeness, grammar |
| Feedback | Errors, warnings, success | Tone, helpfulness, grammar |
| Data | Prices, dates, numbers | Format consistency |

### Step 3: Validation Checks

#### Spelling & Grammar
- Check against dictionary
- Grammar rules (subject-verb agreement, tense)
- Common confusions (its/it's, there/their)

#### Format Validation

| Type | Pattern | Example |
|------|---------|---------|
| Currency | `$X.XX` or `USD X.XX` | `$99.99` ✓ `99.99$` ✗ |
| Date | Consistent format | `MM/DD/YYYY` or `DD MMM YYYY` |
| Time | 12h vs 24h consistency | `2:30 PM` vs `14:30` |
| Phone | `(XXX) XXX-XXXX` | Standard format per region |
| Percentage | `X%` with consistent decimals | `10%` vs `10.0%` |

#### Terminology Consistency
Create glossary of approved terms:
- "Sign In" vs "Login" vs "Log In"
- "Email" vs "E-mail"
- "OK" vs "Okay" vs "O.K."
- Product name capitalization

#### Casing Rules
- **Title Case**: Page titles, section headers
- **Sentence case**: Descriptions, body text
- **UPPERCASE**: Acronyms only (avoid shouting)

### Step 4: Issue Severity

| Severity | Criteria | Action |
|----------|----------|--------|
| 🔴 Critical | Wrong prices, misleading errors, broken grammar | Block release |
| 🟡 Major | Spelling errors, inconsistent terms | Fix before release |
| 🟢 Minor | Casing inconsistencies, punctuation | Fix in next sprint |

### Step 5: Report Format

```
UI Content Validation Report
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Page: https://app.example.com/checkout
Timestamp: 2026-02-20 14:30:00

Summary:
  Total text elements: 45
  Issues found: 7
  Critical: 1 | Major: 3 | Minor: 3

Critical Issues (Fix Immediately):
─────────────────────────────────
🔴 [Price Mismatch] Button "Pay $99.99" vs displayed "$100.00"
   Location: Checkout button
   Suggested: "Pay $100.00"

Major Issues:
─────────────
🟡 [Spelling] "Recieve" should be "Receive"
   Location: Success message
   Current: "You will recieve an email"
   Suggested: "You will receive an email"

🟡 [Terminology] Inconsistent: "Sign In" vs "Login"
   Location: Header uses "Login", button uses "Sign In"
   Suggested: Use "Sign In" everywhere

🟡 [Grammar] "There is errors" → "There are errors"
   Location: Error summary

Minor Issues:
─────────────
🟢 [Casing] "submit" should be "Submit"
   Location: Form button

Glossary Violations:
────────────────────
Found "e-mail" (use "email")
Found "log in" (use "Sign In")
```

## Scripts

Run content extraction and validation:

```bash
# Extract and validate
python .agent/skills/validating-ui-content/scripts/ui_validator.py \
  --url https://app.example.com/page \
  --glossary glossary.json \
  --rules rules.json \
  --output report.json

# Validate against screenshot (OCR)
python .agent/skills/validating-ui-content/scripts/ui_validator.py \
  --screenshot page.png \
  --glossary glossary.json
```

## Configuration

### glossary.json
```json
{
  "preferred_terms": {
    "sign in": ["login", "log in", "signin"],
    "email": ["e-mail", "e mail"],
    "OK": ["okay", "o.k.", "Ok"]
  },
  "format_rules": {
    "currency": "$#,##0.00",
    "date": "MMM DD, YYYY",
    "time": "12h"
  },
  "casing": {
    "buttons": "title",
    "labels": "sentence",
    "headings": "title"
  }
}
```

### Environment Variables
```
SPELLCHECK_LANGUAGE=en-US
CURRENCY_DEFAULT=USD
DATE_FORMAT=MM/DD/YYYY
VALIDATION_STRICTNESS=normal  # strict | normal | relaxed
```

## Example Usage

```
User: "Check the checkout page for content errors"

→ Navigate to /checkout
→ Extract all visible text
→ Validate: spelling, grammar, currency formats
→ Find: "Recieve" typo, "$99.99" vs "$100.00" mismatch
→ Report with line numbers and suggested fixes
```

## Resources

- [scripts/ui_validator.py](scripts/ui_validator.py) - Main validation engine
- [examples/validation_report_example.md](examples/validation_report_example.md) - Sample outputs
- [examples/glossary_template.json](examples/glossary_template.json) - Terminology guide

## Integration Tips

**With CI/CD:**
```yaml
# GitHub Actions example
- name: UI Content Validation
  run: python scripts/ui_validator.py --url ${{ env.STAGING_URL }}
  continue-on-error: false
```

**With JIRA:**
Create bugs automatically for critical issues:
```python
if issue['severity'] == 'critical':
    jira.create_issue(summary=f"Content error: {issue['description']}")
```
