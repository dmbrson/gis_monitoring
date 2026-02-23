from rest_framework import viewsets, permissions, filters, status
from django_filters.rest_framework import DjangoFilterBackend
from .models import Status, Object, History, Comment
from .serializers import StatusSerializer, ObjectSerializer,HistorySerializer, CommentSerializer
from users.permissions import IsAdmin, IsManagerOrAdmin


class IsCommentOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        user_role = getattr(request.user, 'role', None)
        role_name = getattr(user_role, 'name', '') if user_role else ''

        return obj.author == request.user or role_name == 'admin'


class StatusViewSet(viewsets.ModelViewSet):
    queryset = Status.objects.all()
    serializer_class = StatusSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['order', 'name']
    ordering = ['order']


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