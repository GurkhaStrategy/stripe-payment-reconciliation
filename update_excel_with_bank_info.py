#!/usr/bin/env python3
"""
Update Excel file with Stripe account names, transfer IDs, bank info, and deposit dates
"""

import pandas as pd
import csv
import stripe
import os
from datetime import datetime
import pytz
import time

# Configuration
MAPPING_FILE = 'payment_account_mapping.csv'
EXCEL_FILE = 'All-Events-2025-11-13T04-41-45-385Z.xlsx'
OUTPUT_FILE = 'Deposit Breakdown - Updated.xlsx'
STRIPE_API_KEY = os.environ.get('STRIPE_SECRET_KEY', '')

# Timezone
EST = pytz.timezone('America/New_York')

def setup_stripe():
    """Initialize Stripe with API key"""
    if not STRIPE_API_KEY:
        print("WARNING: STRIPE_SECRET_KEY not set. Bank and transfer info will not be fetched.")
        return False
    stripe.api_key = STRIPE_API_KEY
    return True

def load_payment_mapping(filename):
    """Load payment ID to account info mapping from CSV"""
    payment_mapping = {}
    with open(filename, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            payment_mapping[row['payment_id']] = {
                'account_name': row['account_name'],
                'account_id': row['account_id']
            }
    return payment_mapping

def get_bank_and_transfer_info(payment_id, account_id):
    """Get transfer ID, bank account, and deposit date for a payment"""
    try:
        # Retrieve payment intent with expanded balance transaction
        if account_id and account_id != 'acct_1PsuX1Bq3IePH7QV':
            payment = stripe.PaymentIntent.retrieve(
                payment_id,
                stripe_account=account_id,
                expand=['latest_charge.balance_transaction']
            )
        else:
            payment = stripe.PaymentIntent.retrieve(
                payment_id,
                expand=['latest_charge.balance_transaction']
            )
        
        transfer_id = ''
        bank_account = ''
        deposit_date = ''
        
        # Get balance transaction info
        if hasattr(payment, 'latest_charge') and payment.latest_charge:
            charge = payment.latest_charge
            if hasattr(charge, 'balance_transaction') and charge.balance_transaction:
                bt = charge.balance_transaction
                
                # Get available date (when funds became available)
                if hasattr(bt, 'available_on') and bt.available_on:
                    deposit_date_obj = datetime.fromtimestamp(bt.available_on, EST)
                    deposit_date = deposit_date_obj.strftime('%Y-%m-%d')
                
                # Try to find payout information
                try:
                    if account_id and account_id != 'acct_1PsuX1Bq3IePH7QV':
                        payouts = stripe.Payout.list(limit=20, stripe_account=account_id)
                    else:
                        payouts = stripe.Payout.list(limit=20)
                    
                    # Look for a payout that includes this balance transaction
                    for payout in payouts.data:
                        if hasattr(payout, 'arrival_date') and hasattr(bt, 'available_on'):
                            # If payout arrival is within 3 days of available date
                            if abs(payout.arrival_date - bt.available_on) <= 86400 * 3:
                                transfer_id = payout.id
                                # Update deposit date with actual payout date
                                deposit_date_obj = datetime.fromtimestamp(payout.arrival_date, EST)
                                deposit_date = deposit_date_obj.strftime('%Y-%m-%d')
                                
                                # Get bank account from payout
                                if hasattr(payout, 'destination') and payout.destination:
                                    try:
                                        if account_id and account_id != 'acct_1PsuX1Bq3IePH7QV':
                                            bank = stripe.Account.retrieve_external_account(
                                                account_id,
                                                payout.destination
                                            )
                                        else:
                                            acct = stripe.Account.retrieve()
                                            bank = stripe.Account.retrieve_external_account(
                                                acct.id,
                                                payout.destination
                                            )
                                        
                                        if hasattr(bank, 'bank_name'):
                                            bank_name = bank.bank_name
                                            last4 = getattr(bank, 'last4', '****')
                                            bank_account = f"{bank_name} •••• {last4}"
                                    except:
                                        pass
                                break
                except:
                    pass
                
                # If no payout found, try to get default bank account
                if not bank_account:
                    try:
                        if account_id and account_id != 'acct_1PsuX1Bq3IePH7QV':
                            account = stripe.Account.retrieve(account_id)
                            external_accounts = account.external_accounts.list(limit=1)
                        else:
                            account = stripe.Account.retrieve()
                            external_accounts = account.external_accounts.list(limit=1)
                        
                        if external_accounts.data:
                            bank = external_accounts.data[0]
                            if hasattr(bank, 'bank_name'):
                                bank_name = bank.bank_name
                                last4 = getattr(bank, 'last4', '****')
                                bank_account = f"{bank_name} •••• {last4}"
                    except:
                        pass
        
        return transfer_id, bank_account, deposit_date
    except Exception as e:
        return '', '', ''

def main():
    print("="*70)
    print("UPDATING EXCEL FILE WITH BANK DEPOSIT INFORMATION")
    print("="*70 + "\n")
    
    # Setup Stripe
    stripe_enabled = setup_stripe()
    
    # Load payment mapping
    payment_mapping = load_payment_mapping(MAPPING_FILE)
    print(f"Loaded {len(payment_mapping)} payment mappings\n")
    
    # Read the Excel file
    df = pd.read_excel(EXCEL_FILE)
    print(f"Excel file has {len(df)} rows and {len(df.columns)} columns\n")
    
    # Find the payment ID column
    payment_id_column = None
    for col in df.columns:
        sample_values = df[col].astype(str).head(10)
        if any('pi_' in str(val) for val in sample_values):
            print(f"Found payment IDs in column: '{col}'")
            payment_id_column = col
            break
    
    if not payment_id_column:
        print("❌ Could not find a column with payment IDs")
        return
    
    # Create new columns
    df['Stripe Account Name'] = ''
    df['Transfer/Payout ID'] = ''
    df['Bank Account'] = ''
    df['Bank Deposit Date'] = ''
    
    # Process each row
    print(f"\nProcessing {len(df)} rows...\n")
    
    processed_count = 0
    for idx, row in df.iterrows():
        payment_id = str(row[payment_id_column]).strip()
        
        if pd.notna(row[payment_id_column]) and payment_id.startswith('pi_'):
            if payment_id in payment_mapping:
                # Get account name
                account_name = payment_mapping[payment_id]['account_name']
                account_id = payment_mapping[payment_id]['account_id']
                df.at[idx, 'Stripe Account Name'] = account_name
                
                # Get bank and transfer info if Stripe is enabled
                if stripe_enabled and account_name != 'NOT FOUND':
                    transfer_id, bank_account, deposit_date = get_bank_and_transfer_info(payment_id, account_id)
                    
                    if transfer_id:
                        df.at[idx, 'Transfer/Payout ID'] = transfer_id
                    if bank_account:
                        df.at[idx, 'Bank Account'] = bank_account
                    if deposit_date:
                        df.at[idx, 'Bank Deposit Date'] = deposit_date
                    
                    processed_count += 1
                    print(f"[{processed_count}/{len(payment_mapping)}] {payment_id} → {account_name} → {bank_account} (Deposited: {deposit_date})")
                    time.sleep(0.1)  # Rate limiting
                else:
                    print(f"[{idx+1}] {payment_id} → {account_name} (Stripe API not available)")
    
    # Save updated Excel file
    df.to_excel(OUTPUT_FILE, index=False)
    print(f"\n✓ Updated Excel file saved as: {OUTPUT_FILE}\n")
    
    # Summary
    print("="*70)
    print("SUMMARY")
    print("="*70)
    print(f"\nTotal rows processed: {len(df)}")
    print(f"Payment IDs mapped: {processed_count}")
    print(f"\nAccount Distribution:")
    print(df['Stripe Account Name'].value_counts())
    print(f"\nBank Accounts:")
    print(df['Bank Account'].value_counts())
    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    main()
