"""URL routes for the kanban_app API (boards, tasks, comments)."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    BoardViewSet,
    TaskCommentDetailView,
    TaskCommentListCreateView,
    TaskViewSet,
)

router = DefaultRouter()
router.register('boards', BoardViewSet, basename='board')
router.register('tasks', TaskViewSet, basename='task')

urlpatterns = [
    path(
        'tasks/<int:task_id>/comments/',
        TaskCommentListCreateView.as_view(),
        name='task-comments',
    ),
    path(
        'tasks/<int:task_id>/comments/<int:comment_id>/',
        TaskCommentDetailView.as_view(),
        name='task-comment-detail',
    ),
    path('', include(router.urls)),
]