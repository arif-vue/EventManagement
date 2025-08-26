from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('activate/<uuid:activation_token>/', views.activate, name='activate'),
    path('debug-activation/', views.test_activation_url, name='debug-activation'),  # Debug URL
]
