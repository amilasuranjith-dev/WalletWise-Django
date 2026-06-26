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
        account = txn.finance_account
        
        # 1. Reverse the old transaction from the balance
        if txn.type == 'income':
            account.balance -= txn.amount
        elif txn.type == 'expense':
            account.balance += txn.amount

        # 2. Update the transaction fields with whatever was passed in kwargs
        for field, value in kwargs.items():
            if hasattr(txn, field) and value is not None:
                setattr(txn, field, value)

        # Re-validate the new state
        if txn.amount <= 0:
            raise ValidationError("Transaction amount must be greater than zero.")
        if txn.type == 'expense' and account.balance < txn.amount:
            raise ValidationError("Insufficient funds to update to this amount.")

        # 3. Apply the new math back to the wallet
        if txn.type == 'income':
            account.balance += txn.amount
        elif txn.type == 'expense':
            account.balance -= txn.amount
            
        account.save()
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
