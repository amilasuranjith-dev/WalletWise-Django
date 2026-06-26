import os
import django
from datetime import date, timedelta

# Set up django environment so we can use models and services outside of manage.py
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wallet_wise.settings')
django.setup()

from django.contrib.auth import get_user_model
from finance.services import CategoryService, FinanceAccountService, TransactionService
from finance.models import Category, FinanceAccount, Transaction

User = get_user_model()
user = User.objects.first()

if not user:
    print("No user found in the database. Creating a default superuser 'admin' with password 'admin'...")
    user = User.objects.create_superuser('admin', 'admin@example.com', 'admin')

print(f"Seeding data for user: {user.username}")

# Clear existing finance data to prevent duplicates if run multiple times
Transaction.objects.filter(finance_account__user=user).delete()
FinanceAccount.objects.filter(user=user).delete()
Category.objects.filter(user=user).delete()

# Create Categories
print("Creating Categories...")
cat_salary = CategoryService.create_category(user=user, name="Salary", type="income", icon="💼")
cat_freelance = CategoryService.create_category(user=user, name="Freelance", type="income", icon="💻")
cat_food = CategoryService.create_category(user=user, name="Food", type="expense", icon="🍔")
cat_transport = CategoryService.create_category(user=user, name="Transport", type="expense", icon="🚕")
cat_utilities = CategoryService.create_category(user=user, name="Utilities", type="expense", icon="💡")

# Create Accounts (with some base balance)
print("Creating Accounts...")
acc_cash = FinanceAccountService.create_account(user=user, name="Cash Wallet", initial_balance=15000.00)
acc_sampath = FinanceAccountService.create_account(user=user, name="Sampath Bank", initial_balance=15000.00)
acc_combank = FinanceAccountService.create_account(user=user, name="Commercial Bank", initial_balance=5000.00)

today = date.today()

# Create Transactions (The Service Layer automatically adds/subtracts these amounts from the accounts)
print("Creating Transactions...")
TransactionService.create_transaction(
    finance_account=acc_sampath, category=cat_salary, type="income", amount=120000.00,
    date=today - timedelta(days=2), description="May Salary"
)

TransactionService.create_transaction(
    finance_account=acc_cash, category=cat_food, type="expense", amount=2450.00,
    date=today - timedelta(days=1), description="Grocery Shopping"
)

TransactionService.create_transaction(
    finance_account=acc_cash, category=cat_transport, type="expense", amount=850.00,
    date=today, description="Uber Ride"
)

TransactionService.create_transaction(
    finance_account=acc_combank, category=cat_freelance, type="income", amount=32800.00,
    date=today - timedelta(days=5), description="Web Design Project"
)

TransactionService.create_transaction(
    finance_account=acc_sampath, category=cat_utilities, type="expense", amount=15000.00,
    date=today - timedelta(days=3), description="Electricity Bill"
)

print("\n✅ Sample data successfully generated! You can now refresh your dashboard.")
