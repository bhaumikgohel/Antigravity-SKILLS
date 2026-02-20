---
name: regression-impact-analysis
description: Analyzes code changes (via GitHub diffs or JIRA tickets) and maps them to existing test cases to identify the minimum necessary regression set. Prevents redundant testing by highlighting only impacted modules and test cases.
---

# Regression Test Case Impact Analysis

## When to use this skill
- When a developer submits a PR or code change and you need to know which manual test cases to run.
- When you provide a "JIRA ticket" or "Git Diff" and an "Existing test case" Excel/CSV file.
- When there is a need to optimize testing time by pruning unnecessary test runs.

## Workflow

1.  **Change Detection**:
    -   **Git Diff**: Parse the `git diff` to identify modified files, function names, and UI components.
    -   **JIRA Ticket**: Extract "Module", "Description", and "Fixed in" fields to understand the functional change.
2.  **Impact Mapping**:
    -   Correlate the changed files/modules with the "Module" or "Feature" column in the test case Excel.
    -   Search for keywords from the code change in the "Test Description" or "Step" columns of the test cases.
3.  **Selection & Analysis**:
    -   Identify "Direct Impact" (cases covering the exact module changed).
    -   Identify "Indirect Impact" (cases covering downstream dependencies or shared utilities).
4.  **Reporting**:
    -   Generate a "Module Changed vs. Impacted Test Cases" table.
    -   Provide a list of "High Priority" regression cases.

## Instructions

### 1. Analyzing Code Changes
Look for modified paths:
- If `src/auth/*` changed -> Map to `Login`, `Register`, `MFA` test cases.
- If `components/shared/Button.js` changed -> Map to ALL UI test cases using buttons.

### 2. Matching with Test Cases
```python
import pandas as pd
# Load test cases
df = pd.read_excel('test_cases.xlsx')
# Search for keyword 'Login' in 'Component' or 'Module' column
impacted = df[df['Module'].str.contains('Login', case=False)]
```

### 3. Output Format
| Module Changed | Impacted Test Cases | Impact Type |
| :--- | :--- | :--- |
| Authentication | TC001 (Valid Login), TC002 (Lockout) | Direct |
| Payment Gateway | TC015 (Stripe Checkout), TC018 (Refund) | Indirect (Dependency) |

## Checklist
- [ ] Identify modified files/functions from Diff/JIRA.
- [ ] Scan Test Case Excel for matching Modules/Features.
- [ ] Group by "Direct" vs "Indirect" impact.
- [ ] Generate the optimized regression list.

## Resources
- [Sample Impact Report](examples/impact_report_sample.md)
- [Diff Parser Helper](scripts/diff_to_keywords.py)
