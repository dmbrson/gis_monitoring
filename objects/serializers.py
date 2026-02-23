from rest_framework import serializers
from django.contrib.gis.geos import Point
from users.models import User
from .models import Status, Object, History, Comment
from users.serializers import UserSerializer


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

    class Meta:
        model = Object
        fields = [
            'id', 'code', 'title', 'address', 'region', 'coordinates',
            'coordinates_input', 'description', 'status', 'status_id',
            'responsible', 'responsible_id', 'start_date', 'end_date',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'code', 'created_at', 'updated_at']

    def get_coordinates(self, obj):
        if obj.coordinates:
            return [obj.coordinates.x, obj.coordinates.y]
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

    class Meta:
        model = History
        fields = [
            'id', 'object', 'field_name', 'old_value', 'new_value',
            'changed_by', 'changed_at'
        ]


class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'object', 'author', 'text', 'created_at']
        read_only_fields = ['id', 'created_at', 'author']

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['author'] = request.user
        else:
            raise serializers.ValidationError("Не удалось определить автора")
        return super().create(validated_data)