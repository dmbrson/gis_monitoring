from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import LoginView, LogoutView, UserView, ChangePasswordView, ProfileUpdateView

urlpatterns = [
    # Auth
    path('api/auth/login/', LoginView.as_view(), name='login'),
    path('api/auth/logout/', LogoutView.as_view(), name='logout'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # User
    path('api/auth/user/', UserView.as_view(), name='user'),
    path('api/auth/user/update/', ProfileUpdateView.as_view(), name='profile_update'),
    path('api/auth/change-password/', ChangePasswordView.as_view(), name='change_password'),
]