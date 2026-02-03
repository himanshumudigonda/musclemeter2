from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.auth_login, name='login'),
    path('register/', views.auth_register, name='register'),
    path('logout/', views.auth_logout, name='logout'),
    
    # Admin Paths
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('members/', views.admin_member_list, name='admin_member_list'),
    path('payments/add/', views.payment_add, name='payment_add'),
    
    # Member Paths
    path('profile/', views.member_profile, name='member_profile'),
]
