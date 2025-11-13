# GitHub Repository Setup Guide

## Quick Setup (Recommended)

If you have GitHub CLI installed:

```bash
./setup_github_repo.sh
```

This will automatically create the repository in the gurkhaStrategy organization.

---

## Manual Setup

### Option 1: Using GitHub CLI

1. **Install GitHub CLI** (if not already installed):
   ```bash
   brew install gh  # macOS
   ```

2. **Authenticate**:
   ```bash
   gh auth login
   ```

3. **Create repository**:
   ```bash
   gh repo create gurkhaStrategy/stripe-payment-reconciliation \
       --public \
       --description "Automatically reconcile Stripe payments with bank deposits and update Excel spreadsheets" \
       --source=. \
       --remote=origin \
       --push
   ```

### Option 2: Using GitHub Web Interface

1. **Go to GitHub**:
   - Navigate to: https://github.com/organizations/gurkhaStrategy/repositories/new

2. **Configure repository**:
   - Repository name: `stripe-payment-reconciliation`
   - Description: `Automatically reconcile Stripe payments with bank deposits and update Excel spreadsheets`
   - Visibility: Public (or Private if preferred)
   - **DO NOT** initialize with README (we already have one)
   - Click "Create repository"

3. **Push your local repository**:
   ```bash
   git remote add origin https://github.com/gurkhaStrategy/stripe-payment-reconciliation.git
   git branch -M main
   git push -u origin main
   ```

---

## What's Included in the Repository

### Files Being Committed:
- ✅ `README.md` - Comprehensive documentation
- ✅ `requirements.txt` - Python dependencies
- ✅ `.gitignore` - Excludes sensitive data and outputs
- ✅ `find_payment_accounts.py` - Payment analysis script
- ✅ `update_excel_with_bank_info.py` - Excel updater script

### Files Being Ignored (in .gitignore):
- ❌ `venv/` - Virtual environment
- ❌ API keys and credentials
- ❌ Excel output files
- ❌ CSV output files
- ❌ Personal data files

---

## After Creating the Repository

### 1. Verify the Push

Visit: https://github.com/gurkhaStrategy/stripe-payment-reconciliation

You should see:
- README.md displayed on the homepage
- 5 files committed
- All documentation visible

### 2. Add Topics (Optional but Recommended)

On GitHub, click "⚙️ Settings" or the gear icon next to "About", then add topics:
- `stripe`
- `payment-reconciliation`
- `excel-automation`
- `python`
- `financial-tools`

### 3. Configure Repository Settings (Optional)

Consider these settings:
- ✅ Enable Issues (for bug reports and feature requests)
- ✅ Enable Discussions (for Q&A with team)
- ✅ Add a LICENSE file (MIT recommended)
- ✅ Set branch protection rules (for production use)

### 4. Share with Your Team

Send them:
```
Repository URL: https://github.com/gurkhaStrategy/stripe-payment-reconciliation

Quick start:
1. git clone https://github.com/gurkhaStrategy/stripe-payment-reconciliation.git
2. cd stripe-payment-reconciliation
3. python3 -m venv venv
4. source venv/bin/activate
5. pip install -r requirements.txt
6. export STRIPE_SECRET_KEY='your_key_here'
7. python update_excel_with_bank_info.py
```

---

## Using the Repository with New Excel Files

### For Your Team Members:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/gurkhaStrategy/stripe-payment-reconciliation.git
   cd stripe-payment-reconciliation
   ```

2. **Set up Python environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Add their Excel file**:
   ```bash
   # Copy their Excel file into the project directory
   cp ~/Downloads/Events-Export.xlsx .
   ```

4. **Update the script**:
   ```python
   # Edit update_excel_with_bank_info.py, line 13:
   EXCEL_FILE = 'Events-Export.xlsx'
   ```

5. **Set Stripe API key**:
   ```bash
   export STRIPE_SECRET_KEY='sk_live_...'
   ```

6. **Run the script**:
   ```bash
   python update_excel_with_bank_info.py
   ```

7. **Get the updated file**:
   - File will be saved as: `Events-Export - Updated.xlsx`
   - Contains 4 new columns with bank deposit information

---

## Future Updates

### To Update the Repository with Changes:

```bash
# Make your changes to the scripts
# Then commit and push:

git add .
git commit -m "Description of changes"
git push origin main
```

### For Team Members to Get Updates:

```bash
cd stripe-payment-reconciliation
git pull origin main
```

---

## Troubleshooting

### "Permission denied" when creating repository

Make sure you have admin access to the gurkhaStrategy organization.

### "Repository already exists"

The repository may already exist. Check:
https://github.com/gurkhaStrategy/stripe-payment-reconciliation

### "gh: command not found"

Install GitHub CLI:
```bash
brew install gh  # macOS
```

Then authenticate:
```bash
gh auth login
```

---

## Security Reminder

⚠️ **IMPORTANT**: 
- Never commit Stripe API keys to the repository
- The `.gitignore` file protects against this
- Always use environment variables for API keys
- Don't commit actual Excel files with customer data

---

## Support

For questions about:
- **The tool**: See README.md in the repository
- **GitHub setup**: See this guide
- **Stripe API**: https://stripe.com/docs/api

---

**Ready to push to GitHub!** 🚀
