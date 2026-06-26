from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('categories/', views.category_list_create_view, name='category_list_create'),
    path('accounts/', views.account_list_create_view, name='account_list_create'),
    path('transactions/add/', views.transaction_create_view, name='transaction_create'),
]
