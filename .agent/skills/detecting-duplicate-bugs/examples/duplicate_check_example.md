# Duplicate Bug Detection - Example Workflow

## Scenario

QA Engineer Sarah is about to log a new bug:

**New Bug Report:**
```
Summary: Login button unresponsive on iPhone Safari
Description: When accessing the login page on iPhone Safari (iOS 16+), 
clicking the login button does nothing. No error message shown.
Component: Authentication
Steps:
1. Open Safari on iPhone
2. Navigate to login page
3. Enter valid credentials
4. Click login button
Expected: User logs in successfully
Actual: Nothing happens
```

## Agent Workflow

### Step 1: Search Existing Bugs

Construct JQL query:
```jql
project IN (PROJ, QA, BUG) AND (
  summary ~ "login button" OR
  summary ~ "iPhone Safari" OR
  summary ~ "unresponsive" OR
  text ~ "Safari login"
) AND status != Closed ORDER BY updated DESC
```

### Step 2: Candidate Results

```json
[
  {
    "key": "BUG-245",
    "summary": "Login failure on iOS browsers",
    "description": "Users cannot log in using Safari on iOS devices...",
    "component": "Authentication",
    "status": "Open"
  },
  {
    "key": "BUG-189",
    "summary": "Button click not registering on mobile",
    "description": "Some buttons don't respond to touch events...",
    "component": "UI",
    "status": "In Progress"
  }
]
```

### Step 3: Similarity Analysis

| Bug | Summary Sim | Desc Sim | Component | Overall | Verdict |
|-----|-------------|----------|-----------|---------|---------|
| BUG-245 | 0.82 | 0.91 | Match | **92%** | 🔴 HIGH |
| BUG-189 | 0.45 | 0.38 | Different | **42%** | ✅ Low |

### Step 4: Agent Response

```
Duplicate Check Results:
==================================================

🔴 HIGH PROBABILITY DUPLICATES:
   • BUG-245: "Login failure on iOS browsers" (92% match)
     URL: https://jira.company.com/browse/BUG-245

📋 Recommendation:
   → Review BUG-245 before creating new bug.
   → Consider adding your iOS 16 specific details as a comment to BUG-245.
```

## Alternative: Unique Bug

If the new bug was genuinely unique:

```
Duplicate Check Results:
==================================================
✅ No duplicate found - Safe to create new bug ticket.

📋 Recommendation:
   → No duplicates found. Proceed with ticket creation.
```

## Script Usage Example

```bash
# Create new bug JSON
cat > new_bug.json << 'EOF'
{
  "summary": "Login button unresponsive on iPhone Safari",
  "description": "When accessing the login page on iPhone Safari...",
  "component": "Authentication",
  "steps_to_reproduce": "1. Open Safari..."
}
EOF

# Run similarity check
python .agent/skills/detecting-duplicate-bugs/scripts/similarity_checker.py \
  --new-bug new_bug.json \
  --candidates existing_bugs.json \
  --threshold 0.70
```

## Integration with JIRA API

```python
import requests

# Search for candidates
def search_jira(jql_query, base_url, auth_token):
    url = f"{base_url}/rest/api/2/search"
    headers = {"Authorization": f"Bearer {auth_token}"}
    params = {"jql": jql_query, "fields": "summary,description,component"}
    response = requests.get(url, headers=headers, params=params)
    return response.json()["issues"]

# Check before creating
def check_duplicate_before_create(new_bug_summary):
    keywords = extract_keywords(new_bug_summary)
    jql = build_jql_query(keywords)
    candidates = search_jira(jql, JIRA_BASE_URL, JIRA_TOKEN)
    
    if candidates:
        matches = find_duplicates(new_bug, candidates)
        if matches and matches[0]['similarity'] > 0.85:
            return f"Duplicate found: {matches[0]['key']}"
    
    return "No duplicate found"
```
