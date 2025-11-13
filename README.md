# Stripe Payment Reconciliation Tool

Automatically reconcile Stripe payments with bank deposits by analyzing payment IDs and updating Excel spreadsheets with detailed payment information.

## Overview

This tool helps you:
- ✅ Identify which Stripe account (platform or connected) received each payment
- ✅ Track bank deposit dates and destination accounts
- ✅ Extract customer names and event metadata
- ✅ Update Excel files automatically with payment reconciliation data

## Features

- **Multi-Account Support**: Analyzes payments across platform and connected Stripe accounts
- **Bank Deposit Tracking**: Shows which bank account received funds and when
- **Excel Integration**: Automatically updates your spreadsheets with new columns
- **Timezone Handling**: Converts all timestamps to EST/EDT
- **Comprehensive Data**: Customer names, event names, payout status, transfer IDs

## Prerequisites

- Python 3.9 or higher
- Stripe API key (live mode)
- Excel file with payment IDs

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/gurkhaStrategy/stripe-payment-reconciliation.git
cd stripe-payment-reconciliation
```

### 2. Set Up Python Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Stripe API Key

```bash
# Set your Stripe secret key
export STRIPE_SECRET_KEY='sk_live_...'
```

### 4. Prepare Your Excel File

Place your Excel file in the project directory. The file should contain a column with Stripe payment IDs (starting with `pi_`).

## Usage

### Option 1: Analyze Payment IDs from Text File

1. **Create a payment IDs file**:
   ```bash
   # Create payment_ids.txt with one payment ID per line
   echo "pi_3RuF3DBq3IePH7QV30RQ9lNJ" > payment_ids.txt
   echo "pi_3Rsx51Bq3IePH7QV0iGy53tc" >> payment_ids.txt
   ```

2. **Run the analysis**:
   ```bash
   python find_payment_accounts.py
   ```

3. **Output**: Creates `payment_account_mapping.csv` with all payment details

### Option 2: Update Existing Excel File

1. **Place your Excel file** in the project directory

2. **Edit the script** to point to your Excel file:
   ```python
   # In update_excel_with_bank_info.py, update line 13:
   EXCEL_FILE = 'your-excel-file-name.xlsx'
   ```

3. **Run the Excel updater**:
   ```bash
   source venv/bin/activate
   export STRIPE_SECRET_KEY='sk_live_...'
   python update_excel_with_bank_info.py
   ```

4. **Output**: Creates `[Original Name] - Updated.xlsx` with new columns:
   - `Stripe Account Name`
   - `Transfer/Payout ID`
   - `Bank Account`
   - `Bank Deposit Date`

## File Structure

```
stripe-payment-reconciliation/
├── README.md                           # This file
├── requirements.txt                    # Python dependencies
├── .gitignore                         # Git ignore rules
├── find_payment_accounts.py           # Main analysis script
├── update_excel_with_bank_info.py     # Excel updater script
├── payment_ids.txt                    # Input: Payment IDs (one per line)
├── payment_account_mapping.csv        # Output: Analysis results
└── [YourFile] - Updated.xlsx          # Output: Updated Excel file
```

## How to Use With a New Excel File

### Step-by-Step Guide

1. **Place your Excel file in the project directory**
   ```bash
   cp /path/to/your/Events-Export.xlsx .
   ```

2. **Update the script configuration**
   
   Open `update_excel_with_bank_info.py` and modify line 13:
   ```python
   EXCEL_FILE = 'Events-Export.xlsx'  # Change to your filename
   ```

3. **Set your Stripe API key**
   ```bash
   export STRIPE_SECRET_KEY='sk_live_...'
   ```

4. **Run the script**
   ```bash
   source venv/bin/activate
   python update_excel_with_bank_info.py
   ```

5. **Check the output**
   
   Look for: `Events-Export - Updated.xlsx`

### What Gets Added to Your Excel

| Column Name | Description | Example |
|------------|-------------|---------|
| **Stripe Account Name** | Which Stripe account received the funds | "LITFirst, LLC (Platform)" |
| **Transfer/Payout ID** | Stripe payout identifier | "po_1234567890abcdef" |
| **Bank Account** | Bank that received the deposit | "CAPITAL ONE, NA •••• 9035" |
| **Bank Deposit Date** | Date funds were deposited | "2025-08-27" |

### Script Detection Logic

The script **automatically detects** your payment ID column by:
- Scanning all columns in your Excel file
- Looking for values that start with `pi_`
- Using the first matching column

**No manual configuration needed for column selection!**

## Configuration

### Environment Variables

```bash
# Required: Your Stripe secret key
export STRIPE_SECRET_KEY='sk_live_...'
```

### Script Configuration

**In `find_payment_accounts.py`**:
```python
PAYMENT_IDS_FILE = 'payment_ids.txt'
OUTPUT_FILE = 'payment_account_mapping.csv'
```

**In `update_excel_with_bank_info.py`**:
```python
EXCEL_FILE = 'your-file.xlsx'  # Change this to your Excel filename
OUTPUT_FILE = 'Deposit Breakdown - Updated.xlsx'
```

## Troubleshooting

### "STRIPE_SECRET_KEY environment variable not set"

```bash
export STRIPE_SECRET_KEY='sk_live_...'
```

### "Could not find a column with payment IDs"

1. Ensure payment IDs start with `pi_`
2. Check that IDs are in a proper column
3. Verify the Excel file isn't corrupted

### "Module not found" errors

```bash
pip install -r requirements.txt
```

### "Permission denied" when saving Excel

Close the Excel file if it's open in another program.

## Security Best Practices

⚠️ **Important**:

1. **Never commit API keys** to Git
2. Use environment variables for sensitive data
3. Add sensitive files to `.gitignore`
4. Rotate API keys regularly

## License

MIT License

---

**Built for financial reconciliation and transparency** 🎯
