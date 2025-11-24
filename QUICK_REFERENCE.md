# Quick Reference: Account Detection Logic

## The One Key Thing

### The `stripe_account` Parameter

```python
# Check PLATFORM account
stripe.PaymentIntent.retrieve(payment_id)

# Check CONNECTED account  
stripe.PaymentIntent.retrieve(payment_id, stripe_account='acct_XXX')
```

That's it! This one parameter controls which account you're searching.

---

## The Algorithm (3 Steps)

### 1. Try Platform
```python
try:
    payment = stripe.PaymentIntent.retrieve(payment_id)
    return "PLATFORM ACCOUNT"
except:
    # Continue to step 2
```

### 2. Get Connected Accounts
```python
accounts = stripe.Account.list(limit=100)
```

### 3. Try Each Connected Account
```python
for account in accounts:
    try:
        payment = stripe.PaymentIntent.retrieve(
            payment_id, 
            stripe_account=account.id  # ← THE KEY
        )
        return f"CONNECTED ACCOUNT: {account.id}"
    except:
        continue  # Try next account
```

---

## Complete Working Function

```python
def find_payment_account(payment_id):
    # Try platform
    try:
        payment = stripe.PaymentIntent.retrieve(payment_id)
        return {'type': 'platform', 'payment': payment}
    except:
        pass
    
    # Try connected accounts
    accounts = stripe.Account.list(limit=100)
    for account in accounts.data:
        try:
            payment = stripe.PaymentIntent.retrieve(
                payment_id,
                stripe_account=account.id
            )
            return {
                'type': 'connected',
                'account': account.id,
                'name': account.business_profile.name,
                'payment': payment
            }
        except:
            continue
    
    return {'type': 'not_found'}
```

---

## Why It Works

- Each Stripe account has **isolated data**
- A payment exists in **exactly ONE account**
- `stripe_account` parameter = which account to search
- Error = payment not in that account (expected)
- Success = found the owner account

---

## Files to Share

1. **`ACCOUNT_DETECTION_LOGIC.md`** - Detailed explanation with diagrams
2. **`example_account_detection.py`** - Copy-paste ready code
3. **`find_payment_accounts.py`** - Full production implementation

All files in: https://github.com/GurkhaStrategy/stripe-payment-reconciliation
