# Test Data Generation Examples

## Example 1: Password Field
**Rules**:
- Min 8 characters, Max 16 characters
- At least 1 Uppercase, 1 Lowercase, 1 Number, 1 Special Char

### Generated Data Set
| Category | Value | Rationale |
| :--- | :--- | :--- |
| **Valid** | `Bhaumik@2024` | 12 chars, fits all rules. |
| **Valid** | `A1b2C3d4!` | Mixed sequence. |
| **Invalid** | `bhaumik@2024` | Fails: No uppercase. |
| **Invalid** | `BHAUMIK@2024` | Fails: No lowercase. |
| **Invalid** | `Bhaumik@` | Fails: No numbers. |
| **Invalid** | `Bhaumik2024` | Fails: No special character. |
| **Boundary (Min)** | `Aa1!Bb2@` | Exactly 8 characters (Valid). |
| **Boundary (Min-1)** | `Aa1!Bb2` | 7 characters (Invalid). |
| **Boundary (Max)** | `Aa1!Bb2@Cc3#Dd4$`| Exactly 16 characters (Valid). |
| **Boundary (Max+1)** | `Aa1!Bb2@Cc3#Dd4$E`| 17 characters (Invalid). |

## Example 2: Age Field (Numeric)
**Rules**:
- Numeric only
- Range: 18 to 65

### Generated Data Set
| Category | Value | Rationale |
| :--- | :--- | :--- |
| **Valid** | `25` | Within range. |
| **Valid** | `40` | Mid-range. |
| **Invalid** | `17` | Below minimum. |
| **Invalid** | `66` | Above maximum. |
| **Invalid** | `abc` | Non-numeric data. |
| **Boundary (Low)** | `18` | Minimum valid age. |
| **Boundary (High)**| `65` | Maximum valid age. |
