from django.urls import path
from . import views

urlpatterns = [
    # Landing and auth
    path('', views.landing_page, name='landing'),
    path('login/', views.auth_login, name='login'),
    path('logout/', views.auth_logout, name='logout'),
    path('register/customer/', views.customer_register, name='customer_register'),
    path('register/owner/', views.owner_register, name='owner_register'),
    
    # Customer paths
    path('explore/', views.explore, name='explore'),
    path('gym/<int:gym_id>/', views.gym_detail, name='gym_detail'),
    path('gym/<int:gym_id>/book/<int:plan_id>/', views.checkout, name='checkout'),
    path('booking/success/<uuid:booking_id>/', views.booking_success, name='booking_success'),
    
    # Owner paths
    path('owner/dashboard/', views.owner_dashboard, name='owner_dashboard'),
    path('owner/gym/register/', views.gym_register, name='gym_register'),
    path('owner/gym/<int:gym_id>/plans/', views.gym_add_plans, name='gym_add_plans'),
    path('owner/gym/<int:gym_id>/plan/<int:plan_id>/edit/', views.gym_edit_plan, name='gym_edit_plan'),
    
    # API
    path('api/login/', views.api_login, name='api_login'),
    path('api/register/customer/', views.api_register_customer, name='api_register_customer'),
    path('api/register/owner/', views.api_register_owner, name='api_register_owner'),
    path('api/gyms/create/', views.api_create_gym, name='api_create_gym'),
    path('api/gyms/<int:gym_id>/plans/create/', views.api_create_plan, name='api_create_plan'),
    path('api/gyms/', views.GymListAPI.as_view(), name='api_gym_list'),
    path('api/gyms/<int:id>/', views.GymDetailAPI.as_view(), name='api_gym_detail'),
    path('api/gyms/<int:gym_id>/book/<int:plan_id>/', views.api_create_booking, name='api_create_booking'),
    path('api/owner/dashboard/', views.api_owner_dashboard, name='api_owner_dashboard'),
    path('api/update-location/', views.update_location, name='update_location'),
]
