---
name: automating-bug-reporting
description: Processes failed test executions, screenshots, and logs to generate comprehensive bug reports and automatically create JIRA tickets. Includes root cause analysis and environment details.
---

# Automating Bug Reporting

## When to use this skill
- When a user provides a "Failed test execution" report, "Screenshot", or "Logs".
- When a bug report needs to be generated with "Steps to Reproduce", "Expected/Actual Results", and "Root Cause".
- When automatic JIRA ticket creation with "Priority" and "Severity" is required.

## Workflow

1.  **Artifact Analysis**:
    -   **Logs**: Parse logs to identify the stack trace, error message, and timestamp.
    -   **Screenshot**: Analyze the screenshot to identify visual discrepancies or UI state at failure.
    -   **Execution Report**: Identify the specific test case that failed and the environment it ran in.
2.  **Report Generation**:
    -   Synthesize findings into a structured bug report.
    -   Determine **Root Cause** by correlating log errors with test steps.
    -   Assess **Priority** and **Severity** based on error type (e.g., Crash = Blocker/P0, Typos = Low/P3).
3.  **JIRA Automation**:
    -   Format the synthesized data for JIRA API.
    -   Execute the creation script or provide the JSON payload for manual entry if API is disconnected.

## Instructions

### 1. Data Identification
-   **Tracebacks**: Look for keywords like `AssertionError`, `NullPointerException`, `TimeoutError`.
-   **Log Correlation**: Match the failure timestamp in logs with the test step execution.

### 2. Bug Report Template
```markdown
# [Bug Title]
- **Environment**: [OS, Browser, Version, Environment (Stage/Prod)]
- **Steps to Reproduce**:
  1. ...
  2. ...
- **Expected Result**: ...
- **Actual Result**: ...
- **Root Cause Analysis (RCA)**: [The technical reason why it failed]
- **Priority**: [Critical|High|Medium|Low]
- **Severity**: [S1|S2|S3|S4]
```

### 3. Automatic JIRA Creation
Use the provided script in `scripts/jira_ticket_helper.py` (if configured) or generate the command:
```bash
# Example for a hypothetical JIRA CLI or API call
python scripts/jira_ticket_helper.py --title "[Title]" --description "[Body]" --priority "High"
```

## Checklist
- [ ] Parse Error Logs / Stack Trace
- [ ] Review Screenshot content
- [ ] Determine Environment (e.g., local vs CI/CD)
- [ ] Draft Bug Report
- [ ] Validate Priority/Severity
- [ ] Create JIRA Ticket

## Resources
- [JIRA Integration Script](scripts/jira_ticket_helper.py)
- [Example Bug Report](examples/sample_bug_report.md)
