from rest_framework import serializers

from users.models import User
from .models import Status, Object
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
            'id', 'code', 'title', 'address', 'coordinates',
            'coordinates_input', 'description', 'status', 'status_id',
            'responsible', 'responsible_id', 'start_date', 'end_date',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'code', 'created_at', 'updated_at']

    def get_coordinates(self, obj):
        if obj.coordinates:
            return [obj.coordinates.x, obj.coordinates.y]
        return None
