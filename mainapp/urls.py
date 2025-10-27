from django.urls import path
from . import views

urlpatterns = [
    path('app/', views.app, name='app'),
    path('mri/', views.mri_classification_view, name='mri_classification_view'),

    path('history/', views.history_view, name='history'),
    path('history/<int:pk>/', views.history_detail_view, name='history_detail'),
    path('history/<int:pk>/edit/', views.history_edit_view, name='history_edit'),
    path('history/<int:pk>/delete/', views.history_delete_view, name='history_delete'),
    path('history/export/', views.history_export_csv, name='history_export'),
    path('history/bulk-delete/', views.history_bulk_delete, name='history_bulk_delete'),
    path('history/<int:pk>/print/', views.history_print_view, name='history_print'),

    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('', views.dashboard_view, name='dashboard'),  # Make it the home page
]

