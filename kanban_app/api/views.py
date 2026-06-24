"""API views for boards, tasks, and task comments."""
from django.db.models import Count, Prefetch, Q
from django.shortcuts import get_object_or_404
from rest_framework import generics, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from kanban_app.models import Board, Comment, Task

from .permissions import (
    IsBoardMemberOrOwner,
    IsBoardOwner,
    IsTaskBoardMemberOrOwner,
    IsTaskCreatorOrBoardOwner,
)
from .serializers import (
    BoardDetailSerializer,
    BoardSummarySerializer,
    BoardUpdateSerializer,
    CommentSerializer,
    TaskCreateSerializer,
    TaskListSerializer,
    TaskUpdateSerializer,
)


class BoardViewSet(viewsets.ModelViewSet):
    """CRUD endpoints for boards the user owns or belongs to."""

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Boards with counters; only list is scoped to the user."""
        queryset = self._boards_with_counters()
        if self.action == 'list':
            queryset = queryset.filter(
                Q(owner=self.request.user) | Q(members=self.request.user)
            ).distinct()
        return queryset

    def _boards_with_counters(self):
        """Returns boards annotated with member and task counters."""
        return Board.objects.annotate(
            member_count=Count('members', distinct=True),
            ticket_count=Count('tasks', distinct=True),
            tasks_to_do_count=Count(
                'tasks', filter=Q(tasks__status='to-do'), distinct=True,
            ),
            tasks_high_prio_count=Count(
                'tasks', filter=Q(tasks__priority='high'), distinct=True,
            ),
        ).prefetch_related('members', self._task_prefetch())

    @staticmethod
    def _task_prefetch():
        """Prefetch board tasks annotated with their comment count."""
        return Prefetch(
            'tasks',
            queryset=Task.objects.annotate(
                comments_count=Count('comments', distinct=True)
            ),
        )

    def get_serializer_class(self):
        """Picks the serializer matching the current action."""
        if self.action == 'retrieve':
            return BoardDetailSerializer
        if self.action in ['partial_update', 'update']:
            return BoardUpdateSerializer
        return BoardSummarySerializer

    def get_permissions(self):
        """Owner may delete; members may read and update."""
        if self.action == 'destroy':
            return [IsAuthenticated(), IsBoardOwner()]
        if self.action in ['retrieve', 'partial_update', 'update']:
            return [IsAuthenticated(), IsBoardMemberOrOwner()]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        """Creates a board and returns it with its annotated counters."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        created_board = self.perform_create(serializer)
        board = self.get_queryset().get(pk=created_board.pk)
        output = self.get_serializer(board)
        return Response(output.data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        """Saves the board with the request user as owner and member."""
        members = serializer.validated_data.pop('members', [])
        board = serializer.save(owner=self.request.user)
        board.members.set({self.request.user, *members})
        return board

    def perform_update(self, serializer):
        """Saves the board and replaces its members when provided."""
        members = serializer.validated_data.pop('members', None)
        board = serializer.save()
        if members is not None:
            board.members.set(members)


class TaskViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """Create, update, delete tasks plus the user's task lists."""

    serializer_class = TaskCreateSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_queryset(self):
        """Returns all tasks with related board and user objects."""
        return Task.objects.select_related(
            'board',
            'board__owner',
            'creator',
            'assignee',
            'reviewer',
        ).prefetch_related('board__members')

    def get_serializer_class(self):
        """Uses the update serializer for partial updates."""
        if self.action == 'partial_update':
            return TaskUpdateSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        """Members may update; creator or board owner may delete."""
        if self.action == 'partial_update':
            return [IsAuthenticated(), IsTaskBoardMemberOrOwner()]
        if self.action == 'destroy':
            return [IsAuthenticated(), IsTaskCreatorOrBoardOwner()]
        return super().get_permissions()

    def get_visible_tasks(self):
        """Returns tasks on boards visible to the current user."""
        return self.get_queryset().filter(
            Q(board__owner=self.request.user)
            | Q(board__members=self.request.user)
        ).distinct().annotate(comments_count=Count('comments', distinct=True))

    def create(self, request, *args, **kwargs):
        """Creates a task and returns it with its comment count."""
        self._ensure_board_exists(request.data.get('board'))
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        created_task = self.perform_create(serializer)
        task = self.get_visible_tasks().get(pk=created_task.pk)
        output = self.get_serializer(task)
        return Response(output.data, status=status.HTTP_201_CREATED)

    @staticmethod
    def _ensure_board_exists(board_id):
        """Raises 404 if a board id is given but does not exist."""
        if board_id in (None, ''):
            return
        try:
            exists = Board.objects.filter(pk=board_id).exists()
        except (ValueError, TypeError):
            return
        if not exists:
            raise NotFound('Board not found.')

    def perform_create(self, serializer):
        """Stores the authenticated user as the task creator."""
        return serializer.save(creator=self.request.user)

    @action(detail=False, methods=['get'], url_path='assigned-to-me')
    def assigned_to_me(self, request):
        """Lists tasks assigned to the authenticated user."""
        tasks = self.get_visible_tasks().filter(assignee=request.user)
        serializer = TaskListSerializer(tasks, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='reviewing')
    def reviewing(self, request):
        """Lists tasks where the authenticated user is reviewer."""
        tasks = self.get_visible_tasks().filter(reviewer=request.user)
        serializer = TaskListSerializer(tasks, many=True)
        return Response(serializer.data)


class TaskCommentListCreateView(generics.ListCreateAPIView):
    """Lists and creates comments for a single task."""

    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Returns comments for a task after checking board access."""
        task = self.get_task()
        self.check_task_permission(task)
        return task.comments.select_related('author')

    def perform_create(self, serializer):
        """Stores the authenticated user as comment author."""
        task = self.get_task()
        self.check_task_permission(task)
        serializer.save(task=task, author=self.request.user)

    def get_task(self):
        """Fetches the task from the URL or raises 404."""
        return get_object_or_404(
            Task.objects.select_related(
                'board', 'board__owner'
            ).prefetch_related('board__members'),
            id=self.kwargs['task_id'],
        )

    def check_task_permission(self, task):
        """Raises 403 if the user is not a member of the task board."""
        if not self.is_board_member(task.board, self.request.user):
            raise PermissionDenied(
                'You must be a board member to access comments.'
            )

    def is_board_member(self, board, user):
        """Returns True if the user owns or belongs to the board."""
        return (
                board.owner_id == user.id
                or board.members.filter(id=user.id).exists()
        )


class TaskCommentDetailView(generics.DestroyAPIView):
    """Deletes a single comment of a task."""

    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    lookup_url_kwarg = 'comment_id'

    def get_queryset(self):
        """Returns the comments belonging to the URL's task."""
        return Comment.objects.select_related(
            'task', 'task__board', 'author'
        ).filter(task_id=self.kwargs['task_id'])

    def perform_destroy(self, instance):
        """Deletes the comment only if the user is its author."""
        if instance.author_id != self.request.user.id:
            raise PermissionDenied(
                'Only the comment author can delete this comment.'
            )
        instance.delete()
