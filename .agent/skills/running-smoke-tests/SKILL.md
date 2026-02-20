---
name: running-smoke-tests
description: Runs automated smoke tests after deployment to validate critical paths and UI readiness. Use after deployments, before releases, or when verifying environment health.
---

# Smoke Test Validation Agent

Automates post-deployment smoke testing to verify critical paths and environment readiness.

## When to use this skill

- Immediately after deployment (staging/production)
- Before release sign-off
- When environment health is questioned
- Daily/scheduled sanity checks
- After infrastructure changes

## Workflow

- [ ] Receive deployment notification or trigger
- [ ] Load smoke test scenarios for the environment
- [ ] Execute tests sequentially (login → navigation → key features)
- [ ] Capture screenshots at each checkpoint
- [ ] Validate UI elements are present and functional
- [ ] Generate readiness report with pass/fail status
- [ ] Notify team via Slack with results

## Instructions

### Step 1: Define Smoke Test Scenarios

Create scenario files in JSON/YAML format:

```json
{
  "name": "Post-Deployment Smoke",
  "environment": "staging",
  "base_url": "https://staging.example.com",
  "scenarios": [
    {
      "id": "login",
      "name": "User Login",
      "steps": [
        {"action": "navigate", "url": "/login"},
        {"action": "screenshot", "name": "login_page"},
        {"action": "fill", "selector": "#email", "value": "${TEST_USER}"},
        {"action": "fill", "selector": "#password", "value": "${TEST_PASS}"},
        {"action": "click", "selector": "#signin-btn"},
        {"action": "wait", "duration": 2000},
        {"action": "screenshot", "name": "dashboard"},
        {"action": "assert", "selector": ".dashboard-header", "expect": "visible"}
      ]
    },
    {
      "id": "dashboard",
      "name": "Dashboard Load",
      "steps": [
        {"action": "navigate", "url": "/dashboard"},
        {"action": "screenshot", "name": "dashboard_view"},
        {"action": "assert", "selector": ".stats-widget", "expect": "visible"},
        {"action": "assert", "selector": ".loading-spinner", "expect": "hidden"}
      ]
    }
  ]
}
```

### Step 2: Execute Smoke Tests

Run the smoke test runner:

```bash
python .agent/skills/running-smoke-tests/scripts/smoke_test_runner.py \
  --config smoke-tests-staging.json \
  --env staging \
  --output ./reports/
```

### Step 3: Capture Evidence

Screenshots captured at each checkpoint:
- `login_page.png` - Login form visible
- `dashboard.png` - After successful login
- `dashboard_view.png` - Full dashboard loaded
- `error_state.png` - If failures occur

Store in timestamped folder: `./reports/smoke-2026-02-20-143000/`

### Step 4: Validate Key Elements

| Checkpoint | Element | Validation |
|------------|---------|------------|
| Login Page | `#email`, `#password` | Visible, enabled |
| Login Page | `#signin-btn` | Clickable |
| Dashboard | `.dashboard-header` | Text contains "Dashboard" |
| Dashboard | `.stats-widget` | Visible, has data |
| Dashboard | `.user-menu` | Dropdown works |
| Navigation | Sidebar links | All clickable |

### Step 5: Generate Readiness Report

```
Smoke Test Report - staging.example.com
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Timestamp: 2026-02-20 14:30:00 UTC
Environment: staging
Duration: 45 seconds

Summary:
  Total Scenarios: 5
  Passed: 4 ✅
  Failed: 1 ❌
  Status: NOT READY

Scenario Results:
─────────────────
✅ User Login (8s)
   - Navigate to /login: PASS
   - Screenshot: login_page.png ✅
   - Fill credentials: PASS
   - Click sign in: PASS
   - Dashboard loaded: PASS
   - Screenshot: dashboard.png ✅

✅ Dashboard Load (3s)
   - Navigate: PASS
   - Stats widget visible: PASS
   - Screenshot: dashboard_view.png ✅

✅ Profile Navigation (4s)
   - Open user menu: PASS
   - Click profile: PASS
   - Profile page loaded: PASS

❌ Feature X Access (5s)
   - Navigate to /feature-x: PASS
   - Page loaded: PASS
   - Check data table: FAIL
   - Error: Timeout waiting for .data-table
   - Screenshot: error_feature_x.png ❌

✅ Logout Flow (3s)
   - Click logout: PASS
   - Redirect to login: PASS

Evidence:
─────────
📁 Report Directory: ./reports/smoke-2026-02-20-143000/
📷 Screenshots: 6 captured
📄 Full Logs: execution.log

Recommendation:
───────────────
🔴 DEPLOYMENT BLOCKED - Fix Feature X data loading issue
   before proceeding with release.
```

### Step 6: Slack Notification

Send notification with summary and links:

```json
{
  "channel": "#qa-smoke-tests",
  "username": "SmokeTestBot",
  "icon_emoji": ":warning:",
  "attachments": [
    {
      "color": "danger",
      "title": "❌ Smoke Tests Failed - Staging",
      "fields": [
        {"title": "Environment", "value": "staging", "short": true},
        {"title": "Passed", "value": "4/5", "short": true},
        {"title": "Failed Scenario", "value": "Feature X Access", "short": false},
        {"title": "Report", "value": "<https://ci.example.com/reports/smoke-2026-02-20-143000/|View Full Report>", "short": false}
      ]
    }
  ]
}
```

## Scripts

Run smoke tests:

```bash
# Run with config file
python .agent/skills/running-smoke-tests/scripts/smoke_test_runner.py \
  --config smoke-tests.json \
  --env staging

# Run specific scenario
python .agent/skills/running-smoke-tests/scripts/smoke_test_runner.py \
  --config smoke-tests.json \
  --scenario login \
  --headless

# Run with Slack notification
python .agent/skills/running-smoke-tests/scripts/smoke_test_runner.py \
  --config smoke-tests.json \
  --slack-webhook $SLACK_WEBHOOK_URL \
  --channel "#deployments"
```

## Configuration

### Environment Variables
```bash
# Required
BASE_URL=https://staging.example.com
TEST_USER=smoke.test@example.com
TEST_PASS=smoke_test_password

# Optional
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/xxx
SLACK_CHANNEL=#qa-smoke-tests
SCREENSHOT_ON_PASS=true
SCREENSHOT_ON_FAIL=true
TIMEOUT_DEFAULT=10000
RETRY_ATTEMPTS=2
```

### Smoke Test Config Structure
```json
{
  "name": "Production Smoke Tests",
  "base_url": "${BASE_URL}",
  "timeouts": {
    "navigation": 10000,
    "element": 5000,
    "assertion": 3000
  },
  "retry": {
    "attempts": 2,
    "delay": 1000
  },
  "notifications": {
    "slack": {
      "webhook": "${SLACK_WEBHOOK_URL}",
      "channel": "${SLACK_CHANNEL}",
      "on_success": true,
      "on_failure": true
    }
  },
  "scenarios": []
}
```

## CI/CD Integration

### GitHub Actions
```yaml
name: Post-Deploy Smoke Tests

on:
  deployment_status:
    environments: [staging, production]

jobs:
  smoke-test:
    if: github.event.deployment_status.state == 'success'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install Playwright
        run: |
          pip install playwright
          playwright install chromium
      
      - name: Run Smoke Tests
        run: |
          python .agent/skills/running-smoke-tests/scripts/smoke_test_runner.py \
            --config .agent/skills/running-smoke-tests/examples/smoke-tests-${{ github.event.deployment.environment }}.json \
            --slack-webhook ${{ secrets.SLACK_WEBHOOK_URL }}
```

## Common Smoke Test Scenarios

| Scenario | Purpose | Critical Elements |
|----------|---------|-------------------|
| Login | Auth working | Form, submit, redirect |
| Dashboard | Core view loads | Widgets, data, navigation |
| Profile | User data accessible | Form, save, validation |
| Search | Core feature works | Input, results, filters |
| Logout | Session ends | Redirect, cookie cleared |

## Resources

- [scripts/smoke_test_runner.py](scripts/smoke_test_runner.py) - Test execution engine
- [examples/smoke-tests-staging.json](examples/smoke-tests-staging.json) - Sample config
- [examples/smoke-report-example.md](examples/smoke-report-example.md) - Sample outputs

## Best Practices

1. **Keep it fast** - Smoke tests should complete in < 2 minutes
2. **Focus on critical paths** - Don't test everything, test what matters
3. **Stable selectors** - Use data-testid attributes, not CSS classes
4. **Idempotent** - Tests should be safe to run multiple times
5. **Clear evidence** - Screenshots for every checkpoint
