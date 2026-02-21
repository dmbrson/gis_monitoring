from django.contrib.gis.db import models as gis_models
from django.db import models
from users.models import User


class Status(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Название статуса'
    )
    color = models.CharField(
        max_length=7,
        default='#007bff',
        verbose_name='Цвет маркера на карте (в формате #RRGGBB)'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Описание статуса'
    )
    order = models.IntegerField(
        default=0,
        verbose_name='Порядок сортировки'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активен'
    )

    class Meta:
        db_table = 'statuses'
        verbose_name = 'Статус'
        verbose_name_plural = 'Статусы'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class Object(gis_models.Model):
    code = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True,
        verbose_name='Код объекта'
    )

    title = models.CharField(
        max_length=200,
        verbose_name='Название объекта'
    )
    address = models.CharField(
        max_length=500,
        verbose_name='Адрес'
    )

    coordinates = gis_models.PointField(
        srid=4326,
        verbose_name='Координаты (долгота, широта)'
    )

    description = models.TextField(
        blank=True,
        verbose_name='Описание работ'
    )

    status = models.ForeignKey(
        Status,
        on_delete=models.PROTECT,
        related_name='objects',
        verbose_name='Статус'
    )
    responsible = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='assigned_objects',
        verbose_name='Ответственный'
    )

    start_date = models.DateField(
        verbose_name='Дата начала работ'
    )
    end_date = models.DateField(
        verbose_name='Дата завершения работ'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата последнего обновления'
    )

    class Meta:
        db_table = 'objects'
        verbose_name = 'Объект'
        verbose_name_plural = 'Объекты'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.code or f'OBJ-{self.id}'}: {self.title}"

    def save(self, *args, **kwargs):
        if not self.code and not self.pk:
            super().save(*args, **kwargs)
            self.code = f"OBJ-{self.id:04d}"
        super().save(*args, **kwargs)