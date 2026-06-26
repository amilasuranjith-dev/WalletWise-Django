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
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            CategoryService.create_category(
                user=request.user,
                name=form.cleaned_data['name'],
                type=form.cleaned_data['type'],
                icon=form.cleaned_data['icon']
            )
            return redirect('category_list_create')
    else:
        form = CategoryForm()
    return render(request, 'finance/category_list.html', {'categories': categories, 'form': form})

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
