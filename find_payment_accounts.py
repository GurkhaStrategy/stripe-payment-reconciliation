#!/usr/bin/env python3
"""
Check which Stripe account owns each payment
"""

import stripe
import os
import csv
from datetime import datetime
import pytz

# Configuration
STRIPE_API_KEY = os.environ.get('STRIPE_SECRET_KEY', '')
PAYMENT_IDS_FILE = 'payment_ids.txt'
OUTPUT_FILE = 'payment_account_mapping.csv'

# Timezone
EST = pytz.timezone('America/New_York')

def setup_stripe():
    """Initialize Stripe with API key"""
    if not STRIPE_API_KEY:
        print("ERROR: STRIPE_SECRET_KEY environment variable not set!")
        exit(1)
    stripe.api_key = STRIPE_API_KEY

def load_payment_ids(filename):
    """Load payment IDs from file"""
    payment_ids = []
    with open(filename, 'r') as f:
        for line in f:
            pid = line.strip()
            if pid and pid != 'N/A':
                payment_ids.append(pid)
    return payment_ids

def check_payment_on_connected_account(payment_id, connected_account_id):
    """Try to retrieve payment from a connected account"""
    try:
        payment = stripe.PaymentIntent.retrieve(
            payment_id,
            stripe_account=connected_account_id,
            expand=['latest_charge.balance_transaction']
        )
        return True, payment
    except:
        return False, None

def get_customer_name(customer_id, stripe_account=None):
    """Get customer name from Stripe"""
    if not customer_id:
        return ''
    try:
        if stripe_account:
            customer = stripe.Customer.retrieve(customer_id, stripe_account=stripe_account)
        else:
            customer = stripe.Customer.retrieve(customer_id)
        
        # Try to get name from customer object
        if hasattr(customer, 'name') and customer.name:
            return customer.name
        elif hasattr(customer, 'email') and customer.email:
            return customer.email
        return ''
    except:
        return ''

def get_payout_status(balance_transaction, stripe_account=None):
    """Check if the payment has been paid out to the bank"""
    if not balance_transaction:
        return 'Unknown', ''
    
    try:
        # Balance transaction should already be expanded
        bt = balance_transaction
        
        # Check status
        if hasattr(bt, 'status'):
            status = bt.status  # 'available' or 'pending'
            available_date = ''
            
            if hasattr(bt, 'available_on') and bt.available_on:
                available_date = datetime.fromtimestamp(bt.available_on, EST).strftime('%Y-%m-%d')
            
            if status == 'available':
                return f'Available ({available_date})', available_date
            else:
                return status.title(), available_date
        
        return 'Unknown', ''
    except Exception as e:
        return 'Unknown', ''

def main():
    print("\n" + "="*70)
    print("FINDING WHICH ACCOUNT OWNS EACH PAYMENT")
    print("="*70 + "\n")
    
    setup_stripe()
    payment_ids = load_payment_ids(PAYMENT_IDS_FILE)
    
    # Get list of connected accounts
    print("Fetching connected accounts...")
    accounts = stripe.Account.list(limit=100)
    connected_accounts = []
    
    for account in accounts.data:
        account_name = "Unknown"
        if hasattr(account, 'business_profile') and account.business_profile:
            account_name = getattr(account.business_profile, 'name', getattr(account, 'email', 'N/A'))
        elif hasattr(account, 'email'):
            account_name = account.email
        
        connected_accounts.append({
            'id': account.id,
            'name': account_name
        })
    
    print(f"Found {len(connected_accounts)} connected accounts\n")
    
    # Check which account owns each payment
    results = []
    
    for idx, payment_id in enumerate(payment_ids, 1):
        print(f"[{idx}/{len(payment_ids)}] Checking {payment_id}...", end=' ')
        
        result = {
            'payment_id': payment_id,
            'account_id': '',
            'account_name': '',
            'customer_name': '',
            'event_name': '',
            'amount': 0,
            'currency': '',
            'status': '',
            'transaction_date_est': '',
            'payout_status': '',
            'payout_date': ''
        }
        
        # First, try platform account
        try:
            payment = stripe.PaymentIntent.retrieve(payment_id, expand=['latest_charge.balance_transaction'])
            result['account_id'] = 'acct_1PsuX1Bq3IePH7QV'  # Platform account
            result['account_name'] = 'LITFirst, LLC (Platform)'
            result['amount'] = payment.amount / 100
            result['currency'] = payment.currency.upper()
            result['status'] = payment.status
            
            # Get transaction date in EST
            if hasattr(payment, 'created'):
                created_utc = datetime.fromtimestamp(payment.created, pytz.UTC)
                created_est = created_utc.astimezone(EST)
                result['transaction_date_est'] = created_est.strftime('%Y-%m-%d %H:%M:%S %Z')
            
            # Get customer name
            if hasattr(payment, 'customer') and payment.customer:
                result['customer_name'] = get_customer_name(payment.customer)
            
            # Get event name from metadata
            if hasattr(payment, 'metadata') and payment.metadata:
                result['event_name'] = payment.metadata.get('event', payment.metadata.get('event_name', payment.metadata.get('Event Name', '')))
            
            # Get payout status
            if hasattr(payment, 'latest_charge') and payment.latest_charge:
                charge = payment.latest_charge
                if hasattr(charge, 'balance_transaction') and charge.balance_transaction:
                    payout_status, payout_date = get_payout_status(charge.balance_transaction)
                    result['payout_status'] = payout_status
                    result['payout_date'] = payout_date
            
            print(f"✓ Platform Account - ${payment.amount/100:.2f} {payment.currency.upper()}")
            results.append(result)
            continue
        except:
            pass
        
        # Try each connected account
        found = False
        for account in connected_accounts:
            success, payment = check_payment_on_connected_account(payment_id, account['id'])
            if success:
                result['account_id'] = account['id']
                result['account_name'] = account['name']
                result['amount'] = payment.amount / 100
                result['currency'] = payment.currency.upper()
                result['status'] = payment.status
                
                # Get transaction date in EST
                if hasattr(payment, 'created'):
                    created_utc = datetime.fromtimestamp(payment.created, pytz.UTC)
                    created_est = created_utc.astimezone(EST)
                    result['transaction_date_est'] = created_est.strftime('%Y-%m-%d %H:%M:%S %Z')
                
                # Get customer name
                if hasattr(payment, 'customer') and payment.customer:
                    result['customer_name'] = get_customer_name(payment.customer, stripe_account=account['id'])
                
                # Get event name from metadata
                if hasattr(payment, 'metadata') and payment.metadata:
                    result['event_name'] = payment.metadata.get('event', payment.metadata.get('event_name', payment.metadata.get('Event Name', '')))
                
                # Get payout status
                if hasattr(payment, 'latest_charge') and payment.latest_charge:
                    charge = payment.latest_charge
                    if hasattr(charge, 'balance_transaction') and charge.balance_transaction:
                        payout_status, payout_date = get_payout_status(charge.balance_transaction, stripe_account=account['id'])
                        result['payout_status'] = payout_status
                        result['payout_date'] = payout_date
                
                print(f"✓ Connected: {account['name']} - ${payment.amount/100:.2f}")
                found = True
                break
        
        if not found:
            result['account_name'] = 'NOT FOUND'
            print("❌ Not found in any account")
        
        results.append(result)
    
    # Save results to CSV
    with open(OUTPUT_FILE, 'w', newline='') as csvfile:
        fieldnames = ['payment_id', 'account_id', 'account_name', 'customer_name', 'event_name', 
                      'amount', 'currency', 'status', 'transaction_date_est', 'payout_status', 'payout_date']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    print(f"\n✓ Results saved to {OUTPUT_FILE}")
    
    # Print summary
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}\n")
    
    account_totals = {}
    for result in results:
        if result['account_name'] not in account_totals:
            account_totals[result['account_name']] = 0
        account_totals[result['account_name']] += result['amount']
    
    for account_name, total in sorted(account_totals.items(), key=lambda x: x[1], reverse=True):
        print(f"{account_name}: ${total:,.2f}")
    
    print(f"\n{'='*70}\n")

if __name__ == "__main__":
    main()
