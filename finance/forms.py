from django import forms
from .models import Category, FinanceAccount, Transaction

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'type', 'icon']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 bg-white border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500', 'placeholder': 'e.g. Groceries'}),
            'type': forms.Select(attrs={'class': 'w-full px-4 py-2 bg-white border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500'}),
            'icon': forms.TextInput(attrs={'class': 'w-full px-4 py-2 bg-white border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500', 'placeholder': 'e.g. 🍔 (Optional)'}),
        }

class FinanceAccountForm(forms.ModelForm):
    class Meta:
        model = FinanceAccount
        fields = ['name', 'balance']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 bg-white border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500', 'placeholder': 'e.g. Cash Wallet'}),
            'balance': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 bg-white border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500', 'step': '0.01'}),
        }

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['finance_account', 'category', 'type', 'amount', 'transaction_date', 'description']
        widgets = {
            'finance_account': forms.Select(attrs={'class': 'w-full px-4 py-3 bg-white border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-500 transition-all'}),
            'category': forms.Select(attrs={'class': 'w-full px-4 py-3 bg-white border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-500 transition-all'}),
            'type': forms.Select(attrs={'class': 'w-full px-4 py-3 bg-white border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-500 transition-all'}),
            'amount': forms.NumberInput(attrs={'class': 'w-full px-4 py-3 bg-white border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-500 transition-all', 'step': '0.01'}),
            'transaction_date': forms.DateInput(attrs={'class': 'w-full px-4 py-3 bg-white border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-500 transition-all', 'type': 'date'}),
            'description': forms.TextInput(attrs={'class': 'w-full px-4 py-3 bg-white border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-500 transition-all', 'placeholder': 'e.g. Morning Coffee'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(TransactionForm, self).__init__(*args, **kwargs)
        
        from datetime import date
        self.fields['transaction_date'].initial = date.today()
        
        if user:
            self.fields['finance_account'].queryset = FinanceAccount.objects.filter(user=user)
            self.fields['category'].queryset = Category.objects.filter(user=user) | Category.objects.filter(user__isnull=True)
