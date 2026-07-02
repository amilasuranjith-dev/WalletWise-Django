# finance/services.py
from django.db import transaction
from django.core.exceptions import ValidationError
from .models import FinanceAccount, Category, Transaction

class FinanceAccountService:
    @staticmethod
    def create_account(user, name, initial_balance=0.00):
        try:
            return FinanceAccount.objects.create(user=user, name=name, balance=initial_balance)
        except Exception as e:
            raise ValidationError(f"Error creating account: {str(e)}")

    @staticmethod
    def get_user_accounts(user):
        return FinanceAccount.objects.filter(user=user)

    @staticmethod
    def get_account(account_id, user):
        try:
            return FinanceAccount.objects.get(id=account_id, user=user)
        except FinanceAccount.DoesNotExist:
            raise ValidationError("Account does not exist or you do not have permission.")

    @staticmethod
    def update_account(account_id, user, name=None, balance=None):
        account = FinanceAccountService.get_account(account_id, user)
        if name is not None:
            account.name = name
        if balance is not None:
            account.balance = balance
        account.save()
        return account

    @staticmethod
    def delete_account(account_id, user):
        account = FinanceAccountService.get_account(account_id, user)
        account.delete()
        return True


class CategoryService:
    @staticmethod
    def create_category(user, name, type, icon=None):
        try:
            return Category.objects.create(user=user, name=name, type=type, icon=icon)
        except Exception as e:
            raise ValidationError(f"Error creating category: {str(e)}")

    @staticmethod
    def get_available_categories(user):
        # Returns both system defaults (user__isnull=True) and the user's custom categories
        return Category.objects.filter(user=user) | Category.objects.filter(user__isnull=True)

    @staticmethod
    def get_category(category_id, user):
        try:
            #allow fetching system categories (user=None) as well as user's own
            category = Category.objects.get(id=category_id)
            if category.user is not None and category.user != user:
                raise ValidationError("You do not have permission to access this category.")
            return category
        except Category.DoesNotExist:
            raise ValidationError("Category does not exist.")

    @staticmethod
    def update_category(category_id, user, name=None, type=None, icon=None):
        try:
            # user can ONLY update their own categories
            category = Category.objects.get(id=category_id, user=user) 
        except Category.DoesNotExist:
            raise ValidationError("Cannot update system categories or non-existent categories.")
        
        if name is not None:
            category.name = name
        if type is not None:
            category.type = type
        if icon is not None:
            category.icon = icon
        category.save()
        return category

    @staticmethod
    def delete_category(category_id, user):
        try:
            category = Category.objects.get(id=category_id, user=user)
            category.delete()
            return True
        except Category.DoesNotExist:
            raise ValidationError("Cannot delete system categories or non-existent categories.")
        except Exception as e:
            raise ValidationError("Cannot delete this category because it is being used in existing transactions.")


class TransactionService:
    @staticmethod
    @transaction.atomic 
    def create_transaction(finance_account, category, type, amount, date, description=None):
        if amount <= 0:
            raise ValidationError("Transaction amount must be greater than zero.")
        if type not in ['income', 'expense']:
            raise ValidationError("Transaction type must be 'income' or 'expense'.")
            
        # Ensure category type matches transaction type
        if category.type != 'both' and category.type != type:
            raise ValidationError(f"Category '{category.name}' is an {category.type} category. You cannot use it for an {type} transaction.")
            
        if type == 'expense' and finance_account.balance < amount:
            raise ValidationError("Insufficient funds in this account.")

        new_transaction = Transaction.objects.create(
            finance_account=finance_account,
            category=category,
            type=type,
            amount=amount,
            description=description,
            transaction_date=date
        )

        if type == 'income':
            finance_account.balance += amount
        elif type == 'expense':
            finance_account.balance -= amount
            
        finance_account.save()
        return new_transaction

    @staticmethod
    def get_transaction(transaction_id, user):
        try:
            return Transaction.objects.get(id=transaction_id, finance_account__user=user)
        except Transaction.DoesNotExist:
            raise ValidationError("Transaction not found or you do not have permission.")

    @staticmethod
    def get_user_transactions(user):
        return Transaction.objects.filter(finance_account__user=user).order_by('-transaction_date', '-created_at')

    @staticmethod
    def get_recent_transactions(user, limit=5):
        return TransactionService.get_user_transactions(user)[:limit]

    @staticmethod
    @transaction.atomic
    def update_transaction(transaction_id, user, **kwargs):
        """
        Updating a transaction is complex because we have to REVERSE the old math,
        apply the new data, and then apply the NEW math to the wallet balance!
        """
        txn = TransactionService.get_transaction(transaction_id, user)
        old_account = txn.finance_account
        
        # 1. Reverse the old transaction from the balance
        if txn.type == 'income':
            old_account.balance -= txn.amount
        elif txn.type == 'expense':
            old_account.balance += txn.amount

        # 2. Update the transaction fields with whatever was passed in kwargs
        for field, value in kwargs.items():
            if hasattr(txn, field) and value is not None:
                setattr(txn, field, value)

        new_account = txn.finance_account

        # Re-validate the new state
        if txn.amount <= 0:
            raise ValidationError("Transaction amount must be greater than zero.")
        if txn.type == 'expense' and new_account.balance < txn.amount:
            raise ValidationError("Insufficient funds to update to this amount.")

        # 3. Apply the new math back to the wallet
        if txn.type == 'income':
            new_account.balance += txn.amount
        elif txn.type == 'expense':
            new_account.balance -= txn.amount
            
        old_account.save()
        if old_account.id != new_account.id:
            new_account.save()
            
        txn.save()
        return txn

    @staticmethod
    @transaction.atomic
    def delete_transaction(transaction_id, user):
        txn = TransactionService.get_transaction(transaction_id, user)
        account = txn.finance_account
        
        # Reverse the math! If we delete an expense, we get the money back.
        if txn.type == 'income':
            account.balance -= txn.amount
        elif txn.type == 'expense':
            account.balance += txn.amount
            
        account.save()
        txn.delete()
        return True

class AnalyticsService:
    @staticmethod
    def get_monthly_income_expense(user, months_count=6):
        from django.utils import timezone
        import datetime
        from django.db.models.functions import TruncMonth
        from django.db.models import Sum

        today = timezone.now().date()
        
        # Exact start date calculation: 1st day of the target month
        month = today.month - (months_count - 1)
        year = today.year
        while month <= 0:
            month += 12
            year -= 1
        start_date = datetime.date(year, month, 1)
        
        # Group by month and type, sum amount
        data = Transaction.objects.filter(
            finance_account__user=user,
            transaction_date__gte=start_date
        ).annotate(
            month=TruncMonth('transaction_date')
        ).values('month', 'type').annotate(
            total=Sum('amount')
        ).order_by('month')
        
        return data

    @staticmethod
    def get_top_spending_categories(user, limit=5):
        from django.db.models import Sum
        data = Transaction.objects.filter(
            finance_account__user=user,
            type='expense'
        ).values('category__name').annotate(
            total=Sum('amount')
        ).order_by('-total')[:limit]
        return data
