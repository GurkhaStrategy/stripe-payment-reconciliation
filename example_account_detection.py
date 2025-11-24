"""
Minimal Code Example: Finding Which Stripe Account Owns a Payment

This is the core logic for determining if a payment belongs to the platform 
account or a connected account.
"""

import stripe

# Set your Stripe API key
stripe.api_key = 'sk_live_...'

def find_payment_account(payment_id):
    """
    Determines which Stripe account owns a payment.
    
    Args:
        payment_id (str): Stripe PaymentIntent ID (e.g., "pi_3RuF3D...")
    
    Returns:
        dict: {
            'found': bool,
            'account_type': 'platform' | 'connected' | 'not_found',
            'account_id': str,
            'account_name': str,
            'payment': PaymentIntent object or None
        }
    """
    
    # STEP 1: Try platform account first (no stripe_account parameter)
    try:
        payment = stripe.PaymentIntent.retrieve(
            payment_id,
            expand=['latest_charge.balance_transaction']
        )
        
        return {
            'found': True,
            'account_type': 'platform',
            'account_id': 'platform',  # Your platform account ID
            'account_name': 'Platform Account',
            'payment': payment
        }
    except stripe.error.InvalidRequestError:
        # Payment not on platform, continue to connected accounts
        pass
    
    # STEP 2: Get all connected accounts
    try:
        connected_accounts = stripe.Account.list(limit=100)
    except Exception as e:
        print(f"Error listing accounts: {e}")
        return {
            'found': False,
            'account_type': 'error',
            'account_id': None,
            'account_name': 'Error listing accounts',
            'payment': None
        }
    
    # STEP 3: Try each connected account
    for account in connected_accounts.data:
        try:
            # THE KEY: Use stripe_account parameter to search specific account
            payment = stripe.PaymentIntent.retrieve(
                payment_id,
                stripe_account=account.id,  # THIS IS THE CRITICAL PARAMETER
                expand=['latest_charge.balance_transaction']
            )
            
            # Found it!
            account_name = "Unknown"
            if hasattr(account, 'business_profile') and account.business_profile:
                account_name = account.business_profile.name or account.email
            elif hasattr(account, 'email'):
                account_name = account.email
            
            return {
                'found': True,
                'account_type': 'connected',
                'account_id': account.id,
                'account_name': account_name,
                'payment': payment
            }
            
        except stripe.error.InvalidRequestError:
            # Payment not in this account, try next one
            continue
        except Exception as e:
            # Unexpected error, log and continue
            print(f"Error checking account {account.id}: {e}")
            continue
    
    # STEP 4: Not found in any account
    return {
        'found': False,
        'account_type': 'not_found',
        'account_id': None,
        'account_name': 'NOT FOUND',
        'payment': None
    }


# ============================================================================
# USAGE EXAMPLE
# ============================================================================

if __name__ == "__main__":
    # Example payment ID
    payment_id = "pi_3RuF3DBq3IePH7QV30RQ9lNJ"
    
    # Find which account owns this payment
    result = find_payment_account(payment_id)
    
    # Print results
    print(f"\nPayment ID: {payment_id}")
    print(f"Found: {result['found']}")
    print(f"Account Type: {result['account_type']}")
    print(f"Account ID: {result['account_id']}")
    print(f"Account Name: {result['account_name']}")
    
    if result['found']:
        payment = result['payment']
        print(f"Amount: ${payment.amount / 100:.2f} {payment.currency.upper()}")
        print(f"Status: {payment.status}")


# ============================================================================
# BATCH PROCESSING EXAMPLE
# ============================================================================

def process_multiple_payments(payment_ids):
    """
    Process multiple payment IDs and group by account
    
    Args:
        payment_ids (list): List of payment intent IDs
    
    Returns:
        dict: Results grouped by account type
    """
    results = {
        'platform': [],
        'connected': {},
        'not_found': []
    }
    
    for payment_id in payment_ids:
        print(f"Checking {payment_id}...", end=' ')
        
        result = find_payment_account(payment_id)
        
        if result['account_type'] == 'platform':
            results['platform'].append(result)
            print(f"✓ Platform - ${result['payment'].amount/100:.2f}")
            
        elif result['account_type'] == 'connected':
            account_name = result['account_name']
            if account_name not in results['connected']:
                results['connected'][account_name] = []
            results['connected'][account_name].append(result)
            print(f"✓ {account_name} - ${result['payment'].amount/100:.2f}")
            
        else:
            results['not_found'].append(payment_id)
            print("❌ Not found")
    
    return results


# Example usage:
if __name__ == "__main__":
    payment_list = [
        "pi_3RuF3DBq3IePH7QV30RQ9lNJ",
        "pi_3S0PqZPn6qRC6dvi1rJGQFsm",
        "pi_3Rsx51Bq3IePH7QV0iGy53tc"
    ]
    
    results = process_multiple_payments(payment_list)
    
    # Print summary
    print(f"\n{'='*50}")
    print("SUMMARY")
    print(f"{'='*50}")
    print(f"Platform payments: {len(results['platform'])}")
    print(f"Connected accounts: {len(results['connected'])}")
    print(f"Not found: {len(results['not_found'])}")


# ============================================================================
# KEY POINTS
# ============================================================================

"""
THE CRITICAL STRIPE API PARAMETER:

When calling stripe.PaymentIntent.retrieve():

1. NO stripe_account parameter:
   stripe.PaymentIntent.retrieve(payment_id)
   → Searches the PLATFORM account

2. WITH stripe_account parameter:
   stripe.PaymentIntent.retrieve(payment_id, stripe_account='acct_XXX')
   → Searches the CONNECTED account 'acct_XXX'

This is how we determine which account owns a payment:
- Try platform first
- If not found, try each connected account
- The account where retrieve() succeeds is the owner
"""
