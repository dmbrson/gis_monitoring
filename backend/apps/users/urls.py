from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .api.views import LoginView, LogoutView, UserView, ChangePasswordView, ProfileUpdateView

urlpatterns = [
    # Auth
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # User
    path('user/', UserView.as_view(), name='user'),
    path('user/update/', ProfileUpdateView.as_view(), name='profile_update'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
]