from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from leaflet.forms.widgets import LeafletWidget
from .models import Status, Object, History, Comment


@admin.register(Object)
class ObjectAdmin(admin.ModelAdmin):
    list_display = ['code', 'title', 'region', 'status_colored', 'responsible_link', 'start_date', 'end_date',
                    'created_at']
    list_filter = ['status', 'region', 'responsible', 'start_date', 'end_date', 'created_at']
    search_fields = ['code', 'title', 'address', 'region', 'description']
    readonly_fields = ['code', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']

    fieldsets = (
        ('Основная информация', {'fields': ('code', 'title', 'address', 'region', 'description')}),
        ('Статус и ответственные', {'fields': ('status', 'responsible')}),
        ('Период работ', {'fields': ('start_date', 'end_date')}),
        ('Геоданные', {
            'fields': ('coordinates',),
            'classes': ('collapse',),
            'description': 'Кликните на карту или введите адрес для автозаполнения'
        }),
        ('Служебная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def status_colored(self, obj):
        return format_html('<span style="color: {};">● {}</span>', obj.status.color, obj.status.name)

    status_colored.short_description = 'Статус'

    def responsible_link(self, obj):
        if obj.responsible:
            url = reverse('admin:users_user_change', args=[obj.responsible.id])
            return format_html('<a href="{}">{}</a>', url, obj.responsible.username)
        return '-'

    responsible_link.short_description = 'Ответственный'


# Остальные админки...
@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ['name', 'colored_indicator', 'order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']
    ordering = ['order', 'name']

    def colored_indicator(self, obj):
        return format_html('<span style="color: {};">●●●</span>', obj.color)

    colored_indicator.short_description = 'Цвет'


@admin.register(History)
class HistoryAdmin(admin.ModelAdmin):
    list_display = ['object_link', 'field_name', 'changed_by', 'changed_at']
    list_filter = ['field_name', 'changed_at']
    readonly_fields = ['object', 'field_name', 'old_value', 'new_value', 'changed_by', 'changed_at']
    ordering = ['-changed_at']

    def has_add_permission(self, request):
        return False

    def object_link(self, obj):
        url = reverse('admin:objects_object_change', args=[obj.object.id])
        return format_html('<a href="{}">{}</a>', url, obj.object.title)

    object_link.short_description = 'Объект'

    def changed_by(self, obj):
        return obj.changed_by.username if obj.changed_by else 'Система'

    changed_by.short_description = 'Изменил'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['object', 'author', 'created_at', 'text_preview']
    list_filter = ['created_at', 'author']
    search_fields = ['text', 'object__title']
    readonly_fields = ['author', 'created_at']

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.author = request.user
        super().save_model(request, obj, form, change)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not request.user.is_superuser:
            form.base_fields['author'].disabled = True
        return form

    def text_preview(self, obj):
        return (obj.text[:100] + '…') if len(obj.text) > 100 else obj.text

    text_preview.short_description = "Текст"