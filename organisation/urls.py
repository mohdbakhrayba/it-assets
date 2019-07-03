from django.urls import path, re_path
from organisation import views

urlpatterns = [
    path('user-account/export/', views.UserAccountExport.as_view(), name='user_account_export'),
]
