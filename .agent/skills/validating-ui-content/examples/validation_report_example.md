# UI Content Validation - Example Reports

## Example 1: E-commerce Checkout Page

### Input
- **URL**: `https://shop.example.com/checkout`
- **Context**: QA testing new checkout flow

### Extracted Content
```
Title: "Checkout - Payment"
Heading: "Complete your order"
Buttons: ["Pay $99.99", "Apply coupon", "go back"]
Labels: ["card number", "Expiration Date", "CVV Code"]
Error: "There is errors in your form"
Success: "You will recieve a confirmation email"
Price display: "Total: 99.99$"
```

### Validation Report

```
UI Content Validation Report
==================================================
Source: https://shop.example.com/checkout

Summary: 6 issues found
  🔴 Critical: 1
  🟡 Major: 3
  🟢 Minor: 2

CRITICAL ISSUES:
----------------------------------------
🔴 [FORMAT] Incorrect currency format
   Location: body text
   Current:  "99.99$"
   Suggest:  "$99.99"

MAJOR ISSUES:
----------------------------------------
🟡 [SPELLING] Common misspelling detected
   Location: body text
   Current:  "recieve"
   Suggest:  "receive"

🟡 [GRAMMAR] Subject-verb agreement
   Location: body text
   Current:  "...there is..."
   Suggest:  "there are"

🟡 [CASING] Button should use Title Case
   Location: button
   Current:  "go back"
   Suggest:  "Go Back"

MINOR ISSUES:
----------------------------------------
🟢 [CASING] Label should use sentence case
   Location: label
   Current:  "card number"
   Suggest:  "Card number"

🟢 [CASING] Label should use sentence case
   Location: label
   Current:  "Expiration Date"
   Suggest:  "Expiration date"
```

---

## Example 2: Login Page

### Input
- **URL**: `https://app.example.com/login`

### Extracted Content
```
Heading: "Login to your account"
Button: "Sign In"
Link: "Don't have an account? Sign up"
Error: "Invalid email or password"
Label: "E-mail Address"
```

### Validation Report

```
UI Content Validation Report
==================================================
Source: https://app.example.com/login

Summary: 2 issues found
  🔴 Critical: 0
  🟡 Major: 2
  🟢 Minor: 0

MAJOR ISSUES:
----------------------------------------
🟡 [TERMINOLOGY] Non-preferred term found
   Location: body text
   Current:  "e-mail"
   Suggest:  "email"

🟡 [TERMINOLOGY] Inconsistent terminology
   Location: body text
   Current:  "Login" (heading) vs "Sign In" (button)
   Suggest:  Use "Sign In" consistently
```

---

## Example 3: Clean Dashboard (No Issues)

### Input
- **URL**: `https://app.example.com/dashboard`

### Validation Report

```
UI Content Validation Report
==================================================
Source: https://app.example.com/dashboard

✅ No issues found! Content looks good.
```

---

## Example 4: Form with Multiple Errors

### Input
- **Screenshot**: `signup_form.png`

### Extracted Content (via OCR)
```
"Create an Account"
"First Name*"
"Last Name*"
"Phone Number (optional)"
"By clicking Submit, you agree to our terms"
[Submit]
"Sucess! Your account has been created."
"Click here to continoue"
```

### Validation Report

```
UI Content Validation Report
==================================================
Source: signup_form.png

Summary: 4 issues found
  🔴 Critical: 0
  🟡 Major: 4
  🟢 Minor: 0

MAJOR ISSUES:
----------------------------------------
🟡 [SPELLING] Common misspelling detected
   Location: body text
   Current:  "Sucess"
   Suggest:  "Success"

🟡 [SPELLING] Common misspelling detected
   Location: body text
   Current:  "continoue"
   Suggest:  "continue"

🟡 [CASING] Label should use sentence case
   Location: label
   Current:  "First Name*"
   Suggest:  "First name*"

🟡 [CASING] Label should use sentence case
   Location: label
   Current:  "Last Name*"
   Suggest:  "Last name*"
```

---

## Integration Example: CI/CD Pipeline

```yaml
# .github/workflows/ui-validation.yml
name: UI Content Validation

on:
  deployment:
    environments: [staging]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install playwright
          playwright install chromium
      
      - name: Validate UI Content
        run: |
          python .agent/skills/validating-ui-content/scripts/ui_validator.py \
            --url ${{ vars.STAGING_URL }} \
            --glossary .agent/skills/validating-ui-content/examples/glossary_template.json \
            --output validation-report.json
      
      - name: Check for critical issues
        run: |
          critical_count=$(jq '[.issues[] | select(.severity == "critical")] | length' validation-report.json)
          if [ "$critical_count" -gt 0 ]; then
            echo "❌ Found $critical_count critical content issues"
            exit 1
          fi
          echo "✅ No critical issues found"
```

---

## JIRA Bug Creation Integration

```python
import json
import requests

def create_jira_bugs(report_path, jira_config):
    with open(report_path) as f:
        report = json.load(f)
    
    for issue in report['issues']:
        if issue['severity'] == 'critical':
            payload = {
                'fields': {
                    'project': {'key': jira_config['project']},
                    'summary': f"Content Error: {issue['message']}",
                    'description': f"""
                        *Issue Type*: {issue['category']}
                        *Location*: {issue['location']}
                        *Current Text*: {issue['current_text']}
                        *Suggested Fix*: {issue['suggested_text']}
                        
                        h3. Acceptance Criteria
                        - Fix the content error
                        - Verify on staging
                    """,
                    'issuetype': {'name': 'Bug'},
                    'priority': {'name': 'High'}
                }
            }
            
            requests.post(
                f"{jira_config['base_url']}/rest/api/2/issue",
                json=payload,
                headers={'Authorization': f"Bearer {jira_config['token']}"}
            )
```
