"""Serializer for boards, tasks, and comments."""
from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

from kanban_app.models import Board, Comment, Task


class UserDataSerializer(serializers.ModelSerializer):
    """Serializes a user as id, email, and full name."""

    fullname = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'fullname']

    def get_fullname(self, obj):
        """Returns the user's full name or username as fallback."""
        return obj.get_full_name() or obj.username


class CommentSerializer(serializers.ModelSerializer):
    """Serializes a comment with its author's full name."""

    author = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'created_at', 'author', 'content']
        read_only_fields = ['id', 'created_at', 'author']

    def get_author(self, obj):
        """Returns the author's full name or username as fallback."""
        return obj.author.get_full_name() or obj.author.username


class BoardSummarySerializer(serializers.ModelSerializer):
    """Serializes a board with its aggregated counters."""

    member_count = serializers.IntegerField(read_only=True)
    ticket_count = serializers.IntegerField(read_only=True)
    tasks_to_do_count = serializers.IntegerField(read_only=True)
    tasks_high_prio_count = serializers.IntegerField(read_only=True)
    owner_id = serializers.IntegerField(source='owner.id', read_only=True)
    members = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        many=True,
        write_only=True,
        required=False,
    )

    class Meta:
        model = Board
        fields = [
            'id',
            'title',
            'members',
            'member_count',
            'ticket_count',
            'tasks_to_do_count',
            'tasks_high_prio_count',
            'owner_id',
        ]


class TaskNestedSerializer(serializers.ModelSerializer):
    """Serializes a task as nested inside a board's detail view."""

    assignee = UserDataSerializer(read_only=True)
    reviewer = UserDataSerializer(read_only=True)
    comments_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Task
        fields = [
            'id',
            'title',
            'description',
            'status',
            'priority',
            'assignee',
            'reviewer',
            'due_date',
            'comments_count',
        ]


class TaskListSerializer(serializers.ModelSerializer):
    """Serializes a task for the list-style task endpoints."""

    assignee = UserDataSerializer(read_only=True)
    reviewer = UserDataSerializer(read_only=True)
    comments_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Task
        fields = [
            'id',
            'board',
            'title',
            'description',
            'status',
            'priority',
            'assignee',
            'reviewer',
            'due_date',
            'comments_count',
        ]


class TaskCreateSerializer(serializers.ModelSerializer):
    """Validates and creates a task within a board."""

    assignee = UserDataSerializer(read_only=True)
    reviewer = UserDataSerializer(read_only=True)
    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='assignee',
        write_only=True,
        required=False,
        allow_null=True,
    )
    reviewer_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='reviewer',
        write_only=True,
        required=False,
        allow_null=True,
    )
    comments_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Task
        fields = [
            'id',
            'board',
            'title',
            'description',
            'status',
            'priority',
            'assignee',
            'reviewer',
            'assignee_id',
            'reviewer_id',
            'due_date',
            'comments_count',
        ]

    def validate(self, attrs):
        """Checks board access and member-only task assignments."""
        board = attrs.get('board')
        request = self.context['request']
        if not self._is_board_member(board, request.user):
            raise PermissionDenied(
                'You must be a board member to create tasks.'
            )
        self._validate_board_user(board, attrs.get('assignee'), 'assignee_id')
        self._validate_board_user(board, attrs.get('reviewer'), 'reviewer_id')
        return attrs

    def _is_board_member(self, board, user):
        """Checks whether a user can work on a board."""
        return (
            board.owner_id == user.id
            or board.members.filter(id=user.id).exists()
        )

    def _validate_board_user(self, board, user, field_name):
        """Checks that assigned users belong to the task board."""
        if user is not None and not self._is_board_member(board, user):
            raise serializers.ValidationError(
                {field_name: 'User must be a board member.'}
            )


class TaskUpdateSerializer(serializers.ModelSerializer):
    """Validates and updates an existing task (board id is fixed)."""

    assignee = UserDataSerializer(read_only=True)
    reviewer = UserDataSerializer(read_only=True)
    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='assignee',
        write_only=True,
        required=False,
        allow_null=True,
    )
    reviewer_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='reviewer',
        write_only=True,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Task
        fields = [
            'id',
            'title',
            'description',
            'status',
            'priority',
            'assignee',
            'reviewer',
            'assignee_id',
            'reviewer_id',
            'due_date',
        ]

    def validate(self, attrs):
        """Checks that reassigned users still belong to the task board."""
        if self.instance is None:
            raise serializers.ValidationError(
                'Task update requires an existing task instance.'
            )
        board = self.instance.board
        self._validate_board_user(board, attrs.get('assignee'), 'assignee_id')
        self._validate_board_user(board, attrs.get('reviewer'), 'reviewer_id')
        return attrs

    def _is_board_member(self, board, user):
        """Checks whether a user can work on a board."""
        return (
            board.owner_id == user.id
            or board.members.filter(id=user.id).exists()
        )

    def _validate_board_user(self, board, user, field_name):
        """Checks that assigned users belong to the task board."""
        if user is not None and not self._is_board_member(board, user):
            raise serializers.ValidationError(
                {field_name: 'User must be a board member.'}
            )


class BoardDetailSerializer(serializers.ModelSerializer):
    """Serializes a board with its members and nested tasks."""

    owner_id = serializers.IntegerField(source='owner.id', read_only=True)
    members = UserDataSerializer(read_only=True, many=True)
    tasks = TaskNestedSerializer(read_only=True, many=True)

    class Meta:
        model = Board
        fields = ['id', 'title', 'owner_id', 'members', 'tasks']


class BoardUpdateSerializer(serializers.ModelSerializer):
    """Updates a board's title and full member list."""

    members = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        many=True,
        required=False,
        write_only=True,
    )
    owner_data = UserDataSerializer(source='owner', read_only=True)
    members_data = UserDataSerializer(
        source='members', many=True, read_only=True
    )

    class Meta:
        model = Board
        fields = ['id', 'title', 'members', 'owner_data', 'members_data']
