from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Role


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'is_active', 'needs_password_change',
                    'created_at']
    list_filter = ['is_active', 'needs_password_change', 'role', 'is_staff']
    readonly_fields = ['created_at', 'updated_at', 'last_login', 'date_joined']

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Персональная информация', {
            'fields': ('first_name', 'last_name', 'email', 'telegram_id')
        }),
        ('Права доступа', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Роль', {'fields': ('role', 'needs_password_change')}),
        ('Даты', {'fields': ('last_login', 'date_joined', 'created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username',
                'email',
                'password1',
                'password2',
                'first_name',
                'last_name',
                'role',
                'telegram_id',
                'is_active'
            ),
        }),
    )