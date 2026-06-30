from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('categories/', views.category_list_create_view, name='category_list_create'),
    path('categories/<int:category_id>/edit/', views.category_update_view, name='category_update'),
    path('categories/<int:category_id>/delete/', views.category_delete_view, name='category_delete'),
    path('accounts/', views.account_list_create_view, name='account_list_create'),
    path('transactions/', views.transaction_list_view, name='transaction_list'),
    path('transactions/add/', views.transaction_create_view, name='transaction_create'),
    path('transactions/<int:transaction_id>/edit/', views.transaction_update_view, name='transaction_update'),
    path('transactions/<int:transaction_id>/delete/', views.transaction_delete_view, name='transaction_delete'),
]
