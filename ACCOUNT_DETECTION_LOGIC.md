# Core Logic: Determining Which Stripe Account Owns a Payment

## Overview
This explains the algorithm for checking whether a payment (transaction) belongs to the platform account or a connected account in Stripe.

---

## The Key Logic

### Step 1: Try Platform Account First
```python
# Attempt to retrieve the payment from the platform account (default)
try:
    payment = stripe.PaymentIntent.retrieve(
        payment_id,
        expand=['latest_charge.balance_transaction']
    )
    # SUCCESS: Payment belongs to platform account
    account_name = 'Platform Account'
    
except stripe.error.InvalidRequestError:
    # FAILURE: Payment not found on platform account
    # Continue to Step 2
    pass
```

**How it works:**
- Call `stripe.PaymentIntent.retrieve()` WITHOUT `stripe_account` parameter
- This queries the platform/parent account by default
- If successful → payment belongs to platform
- If it throws an error → payment is not on platform, try connected accounts

---

### Step 2: Try Each Connected Account
```python
# Get all connected accounts
connected_accounts = stripe.Account.list(limit=100)

# Try each connected account
for account in connected_accounts:
    try:
        payment = stripe.PaymentIntent.retrieve(
            payment_id,
            stripe_account=account.id,  # THIS IS THE KEY PARAMETER
            expand=['latest_charge.balance_transaction']
        )
        # SUCCESS: Payment belongs to this connected account
        account_name = account.business_profile.name
        break
        
    except stripe.error.InvalidRequestError:
        # FAILURE: Payment not in this connected account
        # Try next account
        continue
```

**How it works:**
- Loop through all connected accounts
- For each account, try to retrieve the payment using `stripe_account=account.id`
- The `stripe_account` parameter tells Stripe to look in that specific connected account
- If successful → payment belongs to that connected account
- If all accounts fail → payment not found anywhere

---

## Complete Algorithm Flow

```
START
  ↓
Input: payment_id (e.g., "pi_3RuF3DBq3IePH7QV30RQ9lNJ")
  ↓
┌─────────────────────────────────────────┐
│ Step 1: Try Platform Account            │
│                                         │
│ stripe.PaymentIntent.retrieve(          │
│     payment_id                          │
│ )                                       │
└─────────────────────────────────────────┘
  ↓
  ├─ SUCCESS? → Payment is on PLATFORM ACCOUNT
  │              - Return platform account info
  │              - DONE
  │
  └─ FAILED? → Continue to Step 2
       ↓
┌─────────────────────────────────────────┐
│ Step 2: Get All Connected Accounts      │
│                                         │
│ accounts = stripe.Account.list()        │
└─────────────────────────────────────────┘
       ↓
┌─────────────────────────────────────────┐
│ Step 3: Loop Through Connected Accounts │
│                                         │
│ FOR EACH connected_account:             │
│   Try:                                  │
│     stripe.PaymentIntent.retrieve(      │
│         payment_id,                     │
│         stripe_account=connected_account│
│     )                                   │
└─────────────────────────────────────────┘
       ↓
       ├─ FOUND? → Payment is on CONNECTED ACCOUNT
       │           - Return connected account info
       │           - DONE
       │
       └─ NOT FOUND IN ANY? → Payment doesn't exist
                              - Return "NOT FOUND"
                              - DONE
```

---

## The Critical Stripe API Parameter

### `stripe_account` Parameter

This is the KEY to checking connected accounts:

```python
# Check platform account (default)
stripe.PaymentIntent.retrieve(payment_id)

# Check specific connected account
stripe.PaymentIntent.retrieve(
    payment_id,
    stripe_account='acct_1234567890'  # Connected account ID
)
```

**What it does:**
- When `stripe_account` is **NOT provided** → Stripe searches platform account
- When `stripe_account='acct_XXX'` is provided → Stripe searches that specific connected account
- Each Stripe account (platform or connected) has its own isolated payment data
- A payment can only exist in ONE account

---

## Code Implementation

### Function: Check Connected Account
```python
def check_payment_on_connected_account(payment_id, connected_account_id):
    """
    Try to retrieve a payment from a specific connected account
    
    Args:
        payment_id: Stripe payment intent ID (e.g., "pi_...")
        connected_account_id: Stripe account ID (e.g., "acct_...")
    
    Returns:
        (True, payment_object) if found
        (False, None) if not found
    """
    try:
        payment = stripe.PaymentIntent.retrieve(
            payment_id,
            stripe_account=connected_account_id,
            expand=['latest_charge.balance_transaction']
        )
        return True, payment
    except:
        return False, None
```

### Main Logic
```python
def find_payment_account(payment_id):
    """
    Determine which account owns a payment
    
    Returns: (account_type, account_id, account_name)
    """
    
    # Step 1: Try platform account
    try:
        payment = stripe.PaymentIntent.retrieve(payment_id)
        return ('platform', 'acct_platform', 'Platform Account')
    except:
        pass
    
    # Step 2: Get all connected accounts
    connected_accounts = stripe.Account.list(limit=100)
    
    # Step 3: Try each connected account
    for account in connected_accounts.data:
        success, payment = check_payment_on_connected_account(
            payment_id, 
            account.id
        )
        
        if success:
            account_name = account.business_profile.name
            return ('connected', account.id, account_name)
    
    # Not found in any account
    return ('not_found', None, 'NOT FOUND')
```

---

## Why This Works

### Stripe Account Isolation
- Each Stripe account (platform and connected) has its own isolated data
- A payment created on Account A cannot be seen by Account B
- When you call `PaymentIntent.retrieve()` with `stripe_account` parameter:
  - Stripe switches context to that account
  - Searches only in that account's data
  - Returns the payment if it exists there

### The Search Process
1. **Platform First**: Most payments are usually on the platform, so check there first for efficiency
2. **Connected Second**: If not on platform, systematically check each connected account
3. **Guaranteed Result**: Since a payment must exist in exactly one account, this process will find it

### Error Handling
- `stripe.error.InvalidRequestError` means payment doesn't exist in that account
- This is **expected behavior** when searching multiple accounts
- We catch the error and continue to the next account

---

## Example Walkthrough

### Scenario: Check payment `pi_ABC123`

**Attempt 1: Platform Account**
```python
stripe.PaymentIntent.retrieve('pi_ABC123')
# Result: Error - not found
# Conclusion: Not on platform
```

**Attempt 2: Connected Account "acct_111"**
```python
stripe.PaymentIntent.retrieve('pi_ABC123', stripe_account='acct_111')
# Result: Error - not found
# Conclusion: Not in acct_111, try next
```

**Attempt 3: Connected Account "acct_222"**
```python
stripe.PaymentIntent.retrieve('pi_ABC123', stripe_account='acct_222')
# Result: SUCCESS! Payment object returned
# Conclusion: Payment belongs to acct_222
```

**Final Result:**
- Account Type: Connected Account
- Account ID: acct_222
- Account Name: "3E Entertainment LLC"
- Amount: $50.00

---

## Key Takeaways

1. **The `stripe_account` parameter** is what allows you to check different accounts
2. **Platform account** is checked by NOT providing `stripe_account`
3. **Connected accounts** are checked by providing `stripe_account=account_id`
4. **A payment exists in exactly one account** - once found, stop searching
5. **Errors are expected** when a payment isn't in an account - this is how we know to keep looking

---

## File Location

**Full implementation**: `find_payment_accounts.py`
- Lines 25-33: `check_payment_on_connected_account()` function
- Lines 102-165: Main search logic

**Repository**: https://github.com/GurkhaStrategy/stripe-payment-reconciliation

---

**This logic is the core of how we determine payment destinations in multi-account Stripe setups.**
