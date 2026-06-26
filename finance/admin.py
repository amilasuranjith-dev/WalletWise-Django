from django.contrib import admin
from .models import Category, FinanceAccount, Transaction

admin.site.register(Category)
admin.site.register(FinanceAccount)
admin.site.register(Transaction)
