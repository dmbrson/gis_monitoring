from rest_framework import serializers
from datetime import date


class ReportFilterSerializer(serializers.Serializer):
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    status = serializers.IntegerField(required=False)
    responsible = serializers.IntegerField(required=False)
    region = serializers.CharField(max_length=200, required=False)


class ReportRequestSerializer(serializers.Serializer):
    report_type = serializers.ChoiceField(
        choices=[
            ('objects_period', 'Объекты за период'),
            ('by_responsible', 'По сотрудникам'),
            ('problematic', 'Проблемные объекты'),
        ]
    )
    filters = ReportFilterSerializer(required=False, default={})
    format = serializers.ChoiceField(
        choices=[
            ('pdf', 'PDF'),
            ('xlsx', 'Excel'),
        ],
        default='pdf'
    )