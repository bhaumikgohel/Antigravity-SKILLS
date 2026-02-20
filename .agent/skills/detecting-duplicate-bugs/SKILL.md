---
name: detecting-duplicate-bugs
description: Detects duplicate JIRA bugs before creation by comparing new bug summaries against existing issues. Use when QA is logging bugs, mentions potential duplicates, or before creating new JIRA tickets.
---

# Duplicate Bug Detection Agent

Prevents JIRA clutter by identifying duplicate or similar bugs before ticket creation.

## When to use this skill

- QA is writing a new bug report
- User mentions "similar issue" or "might be duplicate"
- Before creating a new JIRA bug ticket
- Reviewing backlog for potential duplicates

## Workflow

- [ ] Collect the new bug summary and description from QA
- [ ] Search existing JIRA bugs using relevant keywords
- [ ] Fetch full details of candidate duplicate bugs
- [ ] Compare similarity using text comparison logic
- [ ] Return recommendation with confidence score

## Instructions

### Step 1: Extract Bug Information

Gather from user input:
- **Summary**: Brief title of the bug
- **Description**: Detailed explanation of the issue
- **Component** (optional): Affected module/feature
- **Labels** (optional): Existing tags

### Step 2: Search Existing Bugs

Construct JQL query to find potential duplicates:

```jql
project = * AND (
  summary ~ "keyword1 keyword2" OR
  description ~ "keyword1 keyword2" OR
  text ~ "error message"
) AND status != Closed ORDER BY updated DESC
```

Search strategies:
- Extract 3-5 key terms from the new bug summary
- Include error messages or codes
- Search within same component if known
- Limit to last 6 months (adjustable)

### Step 3: Compare Similarity

For each candidate bug, compare:

| Field | Weight | Method |
|-------|--------|--------|
| Summary | 40% | Cosine similarity or keyword overlap |
| Description | 40% | Semantic similarity, error pattern match |
| Component | 10% | Exact match bonus |
| Steps to Reproduce | 10% | Sequence similarity |

Similarity scoring:
- **> 85%**: High probability duplicate
- **70-85%**: Possible duplicate (flag for review)
- **< 70%**: Likely unique

### Step 4: Return Recommendation

Response format:

```
Duplicate Check Results:
━━━━━━━━━━━━━━━━━━━━━━━
🔍 Analyzed: [X] existing bugs

✅ HIGH MATCH (>85%):
   • BUG-245: "[Summary]" (92% similar)
     → URL: https://jira.company.com/browse/BUG-245

⚠️  POSSIBLE MATCH (70-85%):
   • BUG-189: "[Summary]" (78% similar)
     → URL: https://jira.company.com/browse/BUG-189

✨ Recommendation: [Create New / Review BUG-245 / Add Comment to BUG-189]
```

## JIRA Integration

### API Endpoints needed:
```bash
# Search issues
GET /rest/api/2/search?jql={query}&fields=summary,description,status,key

# Get issue details
GET /rest/api/2/issue/{issueKey}
```

### Authentication:
- Use API token stored in env: `JIRA_API_TOKEN`
- Base URL from env: `JIRA_BASE_URL` (e.g., https://company.atlassian.net)

## Scripts

Use the helper script for similarity calculation:

```bash
python .agent/skills/detecting-duplicate-bugs/scripts/similarity_checker.py \
  --new-bug "bug_summary.txt" \
  --candidates "candidate_bugs.json" \
  --threshold 0.7
```

## Example Usage

```
User: "Login button not working on mobile safari"

→ Search JQL: project = * AND (summary ~ "login button" OR summary ~ "mobile safari")
→ Compare with top 20 results
→ Output: "Similar bug found: BUG-178 (85% match) - Login failure on iOS browsers"
```

## Resources

- [scripts/similarity_checker.py](scripts/similarity_checker.py) - Text similarity engine
- [examples/duplicate_check_example.md](examples/duplicate_check_example.md) - Sample workflow

## Configuration

Set in environment or `.env` file:
```
JIRA_BASE_URL=https://yourcompany.atlassian.net
JIRA_API_TOKEN=your_api_token_here
JIRA_PROJECT_KEYS=PROJ,QA,BUG
SIMILARITY_THRESHOLD=0.75
```
