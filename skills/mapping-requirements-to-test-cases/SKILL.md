---
name: mapping-requirements-to-test-cases
description: Analyzes requirement documents and existing test cases (Excel/JIRA) to identify coverage gaps, duplicates, and missing scenarios. Generates a gap analysis report mapping requirements to test coverage status.
---

# Mapping Requirements to Test Cases

## When to use this skill
- When the user provides a "Requirement document" and "Existing test cases" (Excel or JIRA Ticket ID).
- When asked to identify "Missing test cases", "Duplicate test cases", and "Incomplete coverage".
- When a requirement-to-test-case mapping/gap analysis report is needed.

## Workflow

1.  **Requirement Extraction**:
    -   Read the requirement document (PDF, Text, Word, or Markdown).
    -   Parse and identify unique Requirements (e.g., REQ-001, FR-01, or bullet points).
    -   Store Requirement IDs and Descriptions in a list.
2.  **Test Case Extraction**:
    -   **Excel/CSV**: Use `pandas` to load the file. Identify columns for "Test Case ID", "Test Description", and "Requirement Mapping/Requirement ID".
    -   **JIRA**: If a JIRA Ticket ID is provided, use available JIRA tools (or ask user for details) to fetch the "Test Issues" linked to the requirement.
3.  **Cross-Mapping & Gap Analysis**:
    -   **Covered**: A requirement is covered if it appears in the "Requirement Mapping" column of at least one test case.
    -   **Missing**: A requirement is missing if no test case maps to it.
    -   **Duplicates**: Flag requirements that have multiple test cases covering the exact same validation logic.
    -   **Incomplete**: Flag requirements that have a test case but lack specific edge cases (e.g., negative testing).
4.  **Reporting**:
    -   Generate the summary report in the table format requested.

## Instructions

### 1. Parsing Requirements
If the document is unstructured, use regex or keyword search for tokens like `REQ-`, `MUST`, `SHOULD`.
Example:
- `FR-login`: User must be able to login with valid credentials.

### 2. Reading Excel Test Cases
```python
import pandas as pd
# Load and peek at headers
df = pd.read_excel('path/to/test_cases.xlsx')
print(df.columns)
# Identify the mapping column (e.g., 'Requirement ID', 'Linked Req')
mapping_col = 'Requirement ID' 
```

### 3. Gap Analysis Logic
- **Missing**: `set(requirements) - set(mapped_requirements)`
- **Duplicate**: Count occurrences of `(Requirement ID, Test Case Logic)` pairs.
- **Coverage Summary**: Calculate `%` of requirements covered.

## Output Format
| Requirement | Covered | Missing Test Case |
| :--- | :--- | :--- |
| Login with valid data | Yes | No |
| Reset password | No | Yes |

### Additional Findings
- **Duplicate Test Cases**:
  - `TC-01` and `TC-05` both cover "User login" with identical steps.
- **Incomplete Coverage**:
  - `REQ-002` (Logout) only has a "Happy Path" test case; missing "Session Timeout" scenario.

## Resources
- [Example Report](examples/sample_report.md)
