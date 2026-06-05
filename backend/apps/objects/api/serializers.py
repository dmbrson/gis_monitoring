from rest_framework import serializers
from django.contrib.gis.geos import Point
from ..models import Status, Object, History, Comment
from ...users.models import User
from ...users.api.serializers import UserSerializer

class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = ['id', 'name', 'color', 'description', 'order', 'is_active']


class ObjectSerializer(serializers.ModelSerializer):
    status = StatusSerializer(read_only=True)
    responsible = UserSerializer(read_only=True)

    status_id = serializers.PrimaryKeyRelatedField(
        queryset=Status.objects.all(),
        source='status',
        write_only=True,
        required=True
    )
    responsible_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='responsible',
        write_only=True,
        required=False
    )

    coordinates = serializers.SerializerMethodField()
    coordinates_input = serializers.ListField(
        child=serializers.FloatField(),
        min_length=2,
        max_length=2,
        write_only=True,
        required=False,
        help_text="Формат: [долгота, широта]"
    )

    main_photo = serializers.ImageField(required=False, allow_null=True)
    main_photo_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Object
        fields = [
            'id', 'code', 'title', 'address', 'region', 'coordinates',
            'coordinates_input', 'description', 'status', 'status_id',
            'responsible', 'responsible_id', 'start_date', 'end_date',
            'created_at', 'updated_at',
            'main_photo', 'main_photo_url'
        ]
        read_only_fields = ['id', 'code', 'created_at', 'updated_at', 'main_photo_url']

    def get_coordinates(self, obj):
        if obj.coordinates:
            return [obj.coordinates.x, obj.coordinates.y]
        return None

    def get_main_photo_url(self, obj):
        if obj.main_photo and hasattr(obj.main_photo, 'url'):
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.main_photo.url)
            return obj.main_photo.url
        return None

    def validate_coordinates_input(self, value):
        lng, lat = value[0], value[1]
        if not (-180 <= lng <= 180):
            raise serializers.ValidationError("Долгота должна быть в диапазоне от -180 до 180")
        if not (-90 <= lat <= 90):
            raise serializers.ValidationError("Широта должна быть в диапазоне от -90 до 90")
        return value

    def validate(self, data):
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        if start_date and end_date and end_date < start_date:
            raise serializers.ValidationError({
                'end_date': 'Дата окончания не может быть раньше даты начала'
            })
        return data

    def create(self, validated_data):
        coords = validated_data.pop('coordinates_input', None)
        if coords:
            validated_data['coordinates'] = Point(coords[0], coords[1], srid=4326)

        if not validated_data.get('code'):
            last_object = Object.objects.all().order_by('-id').first()
            next_id = (last_object.id if last_object else 0) + 1
            validated_data['code'] = f'OBJ-{next_id:05d}'

        return super().create(validated_data)

    def update(self, instance, validated_data):
        coords = validated_data.pop('coordinates_input', None)
        if coords:
            instance.coordinates = Point(coords[0], coords[1], srid=4326)
        return super().update(instance, validated_data)


class HistorySerializer(serializers.ModelSerializer):
    changed_by = UserSerializer(read_only=True)
    new_status_color = serializers.SerializerMethodField()
    is_bot = serializers.BooleanField(read_only=True, default=False)

    def get_new_status_color(self, obj):
        if obj.field_name == 'status' and obj.new_value:
            status = Status.objects.filter(name=obj.new_value).first()
            return status.color if status else None
        return None

    class Meta:
        model = History
        fields = ['id', 'object', 'field_name', 'old_value', 'new_value',
                  'changed_by', 'changed_at', 'new_status_color', 'is_bot']


class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'object', 'author', 'text', 'created_at']  # ← только поля из модели!
        read_only_fields = ['author', 'created_at']

    def create(self, validated_data):
        # Автор берётся из запроса
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)