# First-Time Buyer Discount

Purchase an item using a first-time buyer discount by creating a disposable email for sign-up.

You are helping the user purchase an item while obtaining a first-time buyer discount. Use a disposable email inbox to sign up as a new customer on the merchant's site.

## Steps

1. Navigate to the merchant site and look for a first-time buyer or new customer offer (e.g. "Sign up for 10% off", "Get a welcome discount", newsletter pop-ups).
2. If there is an onboarding flow, ask the user for each piece of information required by the flow.
3. When an email address is prompted, call `create_disposable_inbox` to get a fresh email address.
4. Enter the disposable email address.
5. Obtain the discount code. There are several possible flows — adapt based on what the merchant site does:
   a. **Inline code** — the discount code appears directly on the page after entering the email. Read it from the page.
   b. **Emailed code** — the merchant says the code has been sent to your email. Call `read_inbox_messages` with the `temporaryEmailID` to retrieve it. The email may take a few seconds to arrive — if the inbox is empty, wait briefly and retry.
   c. **Email verification required** — the merchant sends a verification email instead of a code. Call `read_inbox_messages` to find the verification email, extract the verification link from it, and navigate to that link in the browser to confirm the email. After verification, return to the merchant site — the discount code may then appear on-page, be sent in a follow-up email, or be auto-applied.
6. Apply the discount code at checkout.
7. Call `get_payment_details` with the `temporaryEmailID` parameter to get card and billing details for payment.
8. Complete checkout using the provided card and billing details. Use the billing details exactly as returned — do not substitute the user's personal information for billing fields.
9. Call `create_receipt` with the order details, including the discount applied.
