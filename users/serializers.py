from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Role

User = get_user_model()


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name', 'description']


class UserSerializer(serializers.ModelSerializer):
    # Выводим название роли текстом, а не только ID
    role_name = serializers.CharField(source='role.get_name_display', read_only=True)

    class Meta:
        model = User
        # Перечисляем поля явно, чтобы скрыть лишнее (например, password в ответе)
        fields = [
            'id', 'username', 'email', 'role', 'role_name',
            'telegram_id', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'is_active']


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'role', 'telegram_id']

    def create(self, validated_data):
        # Хэшируем пароль при создании
        user = User.objects.create_user(**validated_data)
        return user