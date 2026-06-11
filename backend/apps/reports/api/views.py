from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from django.http import FileResponse, HttpResponse
from django.template.loader import render_to_string
from django.db.models import Count, Case, When, Value, CharField, Q
from datetime import datetime, date
from io import BytesIO
from ...objects.models import Object
from .serializers import ReportRequestSerializer


class ReportGenerateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ReportRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        report_type = serializer.validated_data['report_type']
        filters = serializer.validated_data.get('filters', {})
        format = serializer.validated_data['format']

        queryset = self._get_filtered_queryset(request.user, filters)

        if report_type == 'objects_period':
            data = self._prepare_objects_data(queryset)
        elif report_type == 'by_responsible':
            data = self._prepare_responsible_data(queryset)
        elif report_type == 'problematic':
            data = self._prepare_problematic_data(queryset)
        else:
            return Response(
                {'error': 'Неизвестный тип отчёта'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if format == 'pdf':
            return self._generate_pdf(report_type, data)
        elif format == 'xlsx':
            return self._generate_xlsx(report_type, data)

    def _get_filtered_queryset(self, user, filters):
        queryset = Object.objects.select_related(
            'status', 'responsible', 'responsible__role'
        ).all()

        user_role = getattr(user, 'role', None)
        role_name = getattr(user_role, 'name', '') if user_role else ''

        if role_name == 'master':
            queryset = queryset.filter(responsible=user)
        elif role_name not in ['admin', 'manager']:
            queryset = queryset.none()

        if filters.get('start_date'):
            queryset = queryset.filter(start_date__gte=filters['start_date'])
        if filters.get('end_date'):
            queryset = queryset.filter(end_date__lte=filters['end_date'])
        if filters.get('status'):
            queryset = queryset.filter(status_id=filters['status'])
        if filters.get('responsible'):
            queryset = queryset.filter(responsible_id=filters['responsible'])
        if filters.get('region'):
            queryset = queryset.filter(region__icontains=filters['region'])

        return queryset

    def _prepare_objects_data(self, queryset):
        return [
            {
                'code': obj.code or '',
                'title': obj.title,
                'address': obj.address,
                'region': obj.region or '',
                'status': obj.status.name if obj.status else '',
                'responsible': f"{obj.responsible.last_name or ''} {obj.responsible.first_name or ''}".strip() if obj.responsible else '',
                'start_date': obj.start_date.strftime('%d.%m.%Y') if obj.start_date else '',
                'end_date': obj.end_date.strftime('%d.%m.%Y') if obj.end_date else '',
                'description': obj.description or '',
            }
            for obj in queryset
        ]

    def _prepare_responsible_data(self, queryset):
        stats = queryset.values(
            'responsible__id',
            'responsible__last_name',
            'responsible__first_name',
            'responsible__role__name'
        ).annotate(
            total_count=Count('id'),
            completed_count=Count(
                Case(
                    When(status__name='Завершён', then=1),
                    output_field=CharField()
                )
            ),
            in_progress_count=Count(
                Case(
                    When(status__name='В работе', then=1),
                    output_field=CharField()
                )
            ),
            overdue_count=Count(
                Case(
                    When(
                        end_date__lt=date.today(),
                        status__name__in=['В работе', 'Планируется'],
                        then=1
                    ),
                    output_field=CharField()
                )
            )
        )
        return list(stats)

    def _prepare_problematic_data(self, queryset):
        today = date.today()
        problematic = queryset.filter(
            Q(end_date__lt=today) & ~Q(status__name='Завершён')
        )
        return self._prepare_objects_data(problematic)

    def _generate_pdf(self, report_type, data):
        return Response(
            {'message': 'PDF '},
            status=status.HTTP_200_OK
        )

    def _generate_xlsx(self, report_type, data):
        return Response(
            {'message': 'Excel '},
            status=status.HTTP_200_OK
        )