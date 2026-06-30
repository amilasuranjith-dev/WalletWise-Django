from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .forms import CategoryForm, FinanceAccountForm
from .services import CategoryService, FinanceAccountService, TransactionService

@login_required
def dashboard_view(request):
    user = request.user
    
    # Get Accounts
    accounts = FinanceAccountService.get_user_accounts(user)
    accounts_count = accounts.count()
    current_balance = accounts.aggregate(total=Sum('balance'))['total'] or 0.00
    
    # Get Transactions
    recent_transactions = TransactionService.get_recent_transactions(user, limit=5)
    
    # Calculate Income/Expenses
    transactions = TransactionService.get_user_transactions(user)
    total_income = transactions.filter(type='income').aggregate(total=Sum('amount'))['total'] or 0.00
    total_expenses = transactions.filter(type='expense').aggregate(total=Sum('amount'))['total'] or 0.00
    
    # DUMMY DATA FOR CHARTS AS REQUESTED
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    income_data = [120000, 150000, 140000, 180000, 160000, 245000]
    expense_data = [50000, 60000, 55000, 70000, 65000, 98500]
    
    context = {
        'total_income': f"{total_income:,.2f}",
        'total_expenses': f"{total_expenses:,.2f}",
        'current_balance': f"{current_balance:,.2f}",
        'accounts_count': accounts_count,
        'recent_transactions': recent_transactions,
        'accounts': accounts[:5],
        'months_json': months,
        'income_json': income_data,
        'expense_json': expense_data,
    }
    return render(request, 'finance/dashboard.html', context)

@login_required
def category_list_create_view(request):
    categories = CategoryService.get_available_categories(request.user)
    
    categories_with_forms = []
    for category in categories:
        if category.user == request.user:
            edit_form = CategoryForm(instance=category)
            categories_with_forms.append({'category': category, 'form': edit_form, 'is_custom': True})
        else:
            categories_with_forms.append({'category': category, 'form': None, 'is_custom': False})

    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            CategoryService.create_category(
                user=request.user,
                name=form.cleaned_data['name'],
                type=form.cleaned_data['type'],
                icon=form.cleaned_data['icon']
            )
            messages.success(request, 'Category created successfully!')
            return redirect('category_list_create')
    else:
        form = CategoryForm()
        
    return render(request, 'finance/category_list.html', {
        'categories_with_forms': categories_with_forms, 
        'form': form
    })

@login_required
def category_update_view(request, category_id):
    if request.method == 'POST':
        existing_category = CategoryService.get_category(category_id, request.user)
        form = CategoryForm(request.POST, instance=existing_category)
        if form.is_valid():
            try:
                CategoryService.update_category(
                    category_id, request.user,
                    name=form.cleaned_data['name'],
                    type=form.cleaned_data['type'],
                    icon=form.cleaned_data['icon']
                )
                messages.success(request, 'Category updated successfully!')
            except ValidationError as error:
                messages.error(request, str(error.message) if hasattr(error, 'message') else str(error))
        else:
            messages.error(request, "Invalid data submitted.")
    return redirect('category_list_create')

@login_required
def category_delete_view(request, category_id):
    if request.method == 'POST':
        try:
            CategoryService.delete_category(category_id, request.user)
            messages.success(request, 'Category deleted successfully!')
        except ValidationError as error:
            messages.error(request, str(error.message) if hasattr(error, 'message') else str(error))
    return redirect('category_list_create')
    
@login_required
def account_list_create_view(request):
    accounts = FinanceAccountService.get_user_accounts(request.user)
    if request.method == 'POST':
        form = FinanceAccountForm(request.POST)
        if form.is_valid():
            FinanceAccountService.create_account(
                user=request.user,
                name=form.cleaned_data['name'],
                initial_balance=form.cleaned_data['balance']
            )
            return redirect('account_list_create')
    else:
        form = FinanceAccountForm()
    return render(request, 'finance/account_list.html', {'accounts': accounts, 'form': form})

from django.contrib import messages
from django.core.exceptions import ValidationError
from .forms import TransactionForm

@login_required
def transaction_create_view(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST, user=request.user)
        if form.is_valid():
            try:
                TransactionService.create_transaction(
                    finance_account=form.cleaned_data['finance_account'],
                    category=form.cleaned_data['category'],
                    type=form.cleaned_data['type'],
                    amount=form.cleaned_data['amount'],
                    date=form.cleaned_data['transaction_date'],
                    description=form.cleaned_data['description']
                )
                messages.success(request, 'Transaction added successfully!')
                return redirect('dashboard')
            except ValidationError as e:
                messages.error(request, str(e.message) if hasattr(e, 'message') else str(e))
    else:
        form = TransactionForm(user=request.user)
        
    return render(request, 'finance/transaction_form.html', {'form': form})

@login_required
def transaction_list_view(request):
    user_transactions = TransactionService.get_user_transactions(request.user)
    
    transactions_with_forms = []
    for transaction in user_transactions:
        edit_form = TransactionForm(instance=transaction, user=request.user)
        transactions_with_forms.append({'transaction': transaction, 'form': edit_form})
        
    context = {
        'transactions_with_forms': transactions_with_forms
    }
    return render(request, 'finance/transaction_list.html', context)

@login_required
def transaction_update_view(request, transaction_id):
    if request.method == 'POST':
        existing_transaction = TransactionService.get_transaction(transaction_id, request.user)
        form = TransactionForm(request.POST, instance=existing_transaction, user=request.user)
        if form.is_valid():
            try:
                TransactionService.update_transaction(
                    transaction_id, request.user,
                    amount=form.cleaned_data['amount'],
                    description=form.cleaned_data['description'],
                    type=form.cleaned_data['type'],
                    finance_account=form.cleaned_data['finance_account'],
                    category=form.cleaned_data['category'],
                    transaction_date=form.cleaned_data['transaction_date']
                )
                messages.success(request, 'Transaction updated successfully!')
            except ValidationError as error:
                messages.error(request, str(error.message) if hasattr(error, 'message') else str(error))
        else:
            messages.error(request, "Invalid data submitted.")
    return redirect('transaction_list')

@login_required
def transaction_delete_view(request, transaction_id):
    if request.method == 'POST':
        try:
            TransactionService.delete_transaction(transaction_id, request.user)
            messages.success(request, 'Transaction deleted successfully!')
        except ValidationError as error:
            messages.error(request, str(error.message) if hasattr(error, 'message') else str(error))
    return redirect('transaction_list')
