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
        queryset=Status.objects.filter(is_active=True),
        source='status',
        write_only=True,
        required=True
    )
    responsible_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(is_active=True),
        source='responsible',
        write_only=True,
        required=True
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

    def create(self, validated_data):
        coords = validated_data.pop('coordinates_input', None)
        if coords:
            validated_data['coordinates'] = Point(coords[0], coords[1], srid=4326)
        else:
            validated_data['coordinates'] = Point(131.885, 43.115, srid=4326)

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
    author_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='author',
        write_only=True,
        required=False
    )

    class Meta:
        model = Comment
        fields = [
            'id', 'object', 'author', 'author_id', 'text', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        if 'author' not in validated_data and self.context['request'].user:
            validated_data['author'] = self.context['request'].user
        return super().create(validated_data)