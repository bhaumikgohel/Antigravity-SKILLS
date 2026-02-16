# Sample Regression Impact Analysis

## Change Overview
- **Source**: GitHub PR #405
- **Files Modified**: 
  - `src/services/auth_service.py` (Modified `validate_password` logic)
  - `src/ui/login_screen.tsx` (Updated button CSS)
  - `config/settings.json` (Changed session timeout value)

## Impact Analysis Table

| Module Changed | Impacted Test Cases | Reason for Inclusion |
| :--- | :--- | :--- |
| **Login / Auth** | TC001, TC002, TC005, TC012 | High risk: Logic change in password validation. |
| **Session Management**| TC020, TC021 | Direct impact: Timeout settings modified in config. |
| **Global UI** | TC050, TC088 | Regression: Shared button CSS updated. |

## Suggested Regression Set
- **Critical Path**: TC001, TC002, TC020 (Run these first)
- **Sanity**: TC050 (Quick check for UI alignment)

## Non-Impacted Modules (Can skip)
- Dashboard Analytics
- Data Export
- User Profile Editing
