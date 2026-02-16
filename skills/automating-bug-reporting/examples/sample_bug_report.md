# Sample Bug Report: Payment Gateway Timeout

## Bug Title
[Payment] Checkout fails with 504 Gateway Timeout on "Submit Order" button click

## Environment
- **Platform**: Web
- **Browser**: Chrome 121.0.6167.140
- **Environment**: Staging (US-East-1)
- **User Role**: Premium Customer

## Steps to Reproduce
1. Navigate to `/checkout` page with items in the cart.
2. Fill in valid shipping and billing address.
3. Click on the "Submit Order" button.
4. Wait for 30 seconds.

## Expected Result
Order is successfully placed and the "Order Confirmation" page is displayed.

## Actual Result
The page hangs for 30 seconds and then displays a "504 Gateway Timeout" error.

## Root Cause Analysis (RCA)
Based on `backend-service.log`, the `PaymentProcessingService` attempts to connect to the 3rd party gateway but receives no response within the configured 25-second timeout.
- **Log Entry**: `ERROR [PaymentProcessingService] - External Gateway Timeout - Request ID: req_98765`

## Priority & Severity
- **Priority**: High (Prevents revenue generation)
- **Severity**: S1 (Major functionality broken)

---
**JIRA Ticket Status**: Created (DEF-402)
