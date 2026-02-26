from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from ..models import Status, Object, History, Comment
from .serializers import StatusSerializer, ObjectSerializer,HistorySerializer, CommentSerializer
from ...users.permissions import IsAdmin, IsManagerOrAdmin


class IsCommentOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        user_role = getattr(request.user, 'role', None)
        role_name = getattr(user_role, 'name', '') if user_role else ''

        return obj.author == request.user or role_name == 'admin'


class StatusViewSet(viewsets.ModelViewSet):
    queryset = Status.objects.filter(is_active=True).order_by('order', 'name')
    serializer_class = StatusSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['order', 'name']
    ordering = ['order']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsAdmin()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action in ['list', 'retrieve']:
            queryset = queryset.filter(is_active=True)
        return queryset

class ObjectViewSet(viewsets.ModelViewSet):
    queryset = Object.objects.select_related('status', 'responsible').all()
    serializer_class = ObjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'responsible', 'region', 'start_date', 'end_date']
    search_fields = ['title', 'address', 'region', 'code', 'description']
    ordering_fields = ['start_date', 'end_date', 'created_at', 'title']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        user_role = getattr(user, 'role', None)
        role_name = getattr(user_role, 'name', '') if user_role else ''

        if role_name in ['admin', 'manager']:
            return self.queryset

        if role_name == 'master':
            return self.queryset.filter(responsible=user)

        return self.queryset.none()

    def get_permissions(self):
        if self.action in ['create', 'destroy']:
            return [permissions.IsAuthenticated(), IsAdmin()]
        elif self.action in ['update', 'partial_update']:
            return [permissions.IsAuthenticated(), IsManagerOrAdmin()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        return context


    @action(detail=True, methods=['patch'], permission_classes=[permissions.IsAuthenticated])
    def update_status(self, request, pk=None):
        obj = self.get_object()
        user = request.user
        user_role = getattr(user, 'role', None)
        role_name = getattr(user_role, 'name', '') if user_role else ''

        if role_name == 'master' and obj.responsible != user:
            return Response(
                {'error': 'Нет прав для изменения статуса этого объекта'},
                status=status.HTTP_403_FORBIDDEN
            )

        status_id = request.data.get('status_id')
        if not status_id:
            return Response({'error': 'Не указан статус'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            new_status = Status.objects.get(id=status_id, is_active=True)
        except Status.DoesNotExist:
            return Response({'error': 'Статус не найден или неактивен'}, status=status.HTTP_400_BAD_REQUEST)

        old_status_name = obj.status.name if obj.status else None

        obj.status = new_status
        obj.save(update_fields=['status', 'updated_at'])

        History.objects.create(
            object=obj,
            changed_by=user,
            field_name='status',
            old_value=old_status_name,
            new_value=new_status.name
        )

        return Response(ObjectSerializer(obj, context={'request': request}).data)

    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def history(self, request, pk=None):
        obj = self.get_object()
        history = obj.history.select_related('changed_by').all()
        serializer = HistorySerializer(history, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def comments(self, request, pk=None):
        obj = self.get_object()
        comments = obj.comments.select_related('author').all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.select_related('author', 'object').all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        user_role = getattr(user, 'role', None)
        role_name = getattr(user_role, 'name', '') if user_role else ''

        if role_name in ['admin', 'manager']:
            return self.queryset

        if role_name == 'master':
            return self.queryset.filter(object__responsible=user)

        return self.queryset.none()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsCommentOwnerOrAdmin()]
        return [permissions.IsAuthenticated()]