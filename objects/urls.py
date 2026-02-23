from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StatusViewSet, ObjectViewSet, CommentViewSet

router = DefaultRouter()
router.register(r'statuses', StatusViewSet, basename='status')
router.register(r'objects', ObjectViewSet, basename='object')
router.register(r'comments', CommentViewSet, basename='comment')

urlpatterns = [
    path('', include(router.urls)),
]