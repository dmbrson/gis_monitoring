from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager


class Role(models.Model):
    ADMIN = 'admin'
    MANAGER = 'manager'
    MASTER = 'master'

    ROLE_CHOICES = [
        (ADMIN, 'Администратор'),
        (MANAGER, 'Менеджер'),
        (MASTER, 'Мастер'),
    ]

    name = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        unique=True,
        verbose_name='Название роли'
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Описание роли'
    )

    class Meta:
        db_table = 'roles'
        verbose_name = 'Роль'
        verbose_name_plural = 'Роли'
        ordering = ['name']

    def __str__(self):
        return self.get_name_display()


class CustomUserManager(BaseUserManager):
    def create_user(self, username, email=None, password=None, **extra_fields):
        if not username:
            raise ValueError('Username должен быть указан')

        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        # Пытаемся получить роль 'admin' из БД
        try:
            role = Role.objects.get(name=Role.ADMIN)
            extra_fields.setdefault('role', role)
        except Role.DoesNotExist:
            role, _ = Role.objects.get_or_create(
                name=Role.ADMIN,
                defaults={'description': 'Полный доступ к системе'}
            )
            extra_fields.setdefault('role', role)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser должен иметь is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser должен иметь is_superuser=True')

        return self.create_user(username, email, password, **extra_fields)

class User(AbstractUser):
    role = models.ForeignKey(
        Role,
        on_delete=models.PROTECT,
        related_name='users',
        verbose_name='Роль',
        db_column='role_id',
        null=True,
        blank=True
    )

    telegram_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='ID в Telegram',
        db_column='telegram_id'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания',
        db_column='created_at'
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления',
        db_column='updated_at'
    )

    needs_password_change = models.BooleanField(
        default=True,
        verbose_name='Требуется смена пароля'
    )

    class Meta:
        db_table = 'users'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['username']

    def __str__(self):
        return f"{self.username} ({self.role.get_name_display() if self.role else 'Без роли'})"