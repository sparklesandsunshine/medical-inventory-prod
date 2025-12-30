from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('history/', views.history, name='history'),
    path('add/', views.add_utilization, name='add_utilization'),
    path('update/<int:id>/', views.update_utilization, name='update_utilization'),
    path('delete/<int:id>/', views.delete_utilization, name='delete_utilization'),
    path('export_csv/', views.export_csv, name='export_csv'),
]