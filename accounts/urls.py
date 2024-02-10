from django.urls import path
from . import views

# app_name = 'accounts'

urlpatterns = [
    path('register/', views.UserRegistration.as_view(), name='register'),
    path('login/', views.UserLogin.as_view(), name='login'),
    path('profile/', views.UserBankAccountUpdate.as_view(), name='profile'),
    path('logout/', views.UserLogout.as_view(), name='logout'),
    # path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
]
