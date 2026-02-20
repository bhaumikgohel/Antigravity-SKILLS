# Example Gap Analysis Report

## Summary
- **Total Requirements**: 10
- **Total Test Cases**: 12
- **Coverage**: 80%
- **Missing Requirements**: 2

## Mapping Table
| Requirement | Covered | Missing Test Case |
| :--- | :--- | :--- |
| REQ-01: Valid Login | Yes | No |
| REQ-02: Invalid Password Error | Yes | No |
| REQ-03: Account Lockout logic | No | Yes |
| REQ-04: Dashboard Loading | Yes | No |
| REQ-05: Side Navigation | Yes | No |
| REQ-06: Profile Update | Yes | No |
| REQ-07: Logout Session Kill | No | Yes |
| REQ-08: Data Export to CSV | Yes | No |
| REQ-09: Filter by Date | Yes | No |
| REQ-10: Sort by Name | Yes | No |

## Detailed Analysis

### 1. Missing Test Cases
- **REQ-03 (Account Lockout)**: No test cases found. Recommended: Create 3 test cases (3 failed attempts, 5 failed attempts, Lockout duration).
- **REQ-07 (Logout Session)**: No test cases found. Recommended: Verify token invalidation on server side.

### 2. Duplicate Test Cases
- **TC-10** and **TC-15** both verify "REQ-06: Profile Update" using the same "First Name" field update logic. Suggest merging or differentiating.

### 3. Incomplete Coverage
- **REQ-08 (Data Export)**: Currently only covered by `TC-20` (Happy Path). Missing: Empty state export, File permission errors, and Special character handling.
