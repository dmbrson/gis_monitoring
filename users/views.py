from rest_framework import viewsets, permissions
from .models import User, Role
from .serializers import UserSerializer, RoleSerializer, UserRegistrationSerializer
from rest_framework_simplejwt.views import TokenObtainPairView


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [permissions.IsAdminUser]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserRegistrationSerializer
        return UserSerializer


class RoleViewSet(viewsets.ReadOnlyModelViewSet):
    # Роли обычно только читают
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [permissions.AllowAny]


# Получение токена
class MyTokenObtainPairView(TokenObtainPairView):
    pass