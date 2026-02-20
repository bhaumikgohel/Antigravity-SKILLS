---
name: generating-test-data
description: Automatically generates valid, invalid, and boundary test data based on field names and validation rules. Use when the user provides field specifications and needs a comprehensive data set for testing forms, APIs, or database constraints.
---

# Generating Test Data

## When to use this skill
- When a user provides a field name (e.g., "Password", "Email", "Age") and a set of validation rules.
- When asked to generate "Valid", "Invalid", or "Boundary" test data sets.
- When preparing data for automated tests or manual regression testing.

## Workflow

1.  **Rule Analysis**:
    -   Parse the provided rules for each field (min/max length, character types, patterns).
    -   Identify the "Boundary" values (e.g., if max is 10, boundary values are 9, 10, and 11).
2.  **Data Set Construction**:
    -   **Valid Data**: Generate 3-5 strings/values that satisfy ALL rules.
    -   **Invalid Data**: Generate values that violate exactly one rule at a time to isolate validation logic.
    -   **Boundary Data**: Specifically target minimum and maximum limits.
3.  **Reporting**:
    -   Present the data in a clear table format categorized by data type.

## Instructions

### 1. Parsing Validation Rules
Identify tokens like "Min", "Max", "Uppercase", "Special Character", "Numeric Only", "Regex".
Example Input:
- Field: `Username`
- Rules: `Min 5, Max 12, Alpha-numeric only`

### 2. Generating Values
- **Valid**: `User123`, `Admin88`, `TestPlayer`
- **Invalid**: `Abc` (Too short), `LongUsername1234` (Too long), `User@123` (Invalid character)
- **Boundary**: `abcde` (5 chars), `abcdefghijkl` (12 chars), `abcd` (4 chars - Invalid boundary)

## Output Format

### Field: [Field Name]
| Category | Value | Rule Tested / Reason |
| :--- | :--- | :--- |
| **Valid** | `SafePass1!` | Meets all criteria |
| **Invalid** | `safepass1!` | Missing uppercase |
| **Invalid** | `Safe1!` | Too short (5 chars) |
| **Boundary** | `Abcdefg1!` | Minimum length (8 chars) |
| **Boundary** | `VeryLongPass123!@#` | Realistic long value |

## Resources
- [Example Rules and Data Sets](examples/data_generation_example.md)
- [Python Faker Script (External)](scripts/generate_random_data.py)
