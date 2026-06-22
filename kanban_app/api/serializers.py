"""Serializer for boards, tasks, and comments."""
from django.contrib.auth.models import User
from rest_framework import serializers

from kanban_app.models import Board, Task, Comment


class UserDataSerializer(serializers.ModelSerializer):
    """Serializes a user as id, email, and full name."""

    fullname = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'fullname']

    def get_fullname(self, obj):
        """Returns the user's full name or username as fallback"""
        return obj.get_full_name() or obj.username


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for comments with author's full name."""

    author = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'created_at', 'author', 'content']
        read_only_fields = ['id', 'created_at', 'author']

    def get_author(self, obj):
        """Returns the author's full name or username as fallback"""
        return obj.author.get_full_name() or obj.author.username


class BoardSummarySerializer(serializers.ModelSerializer):
    """Serializer for board with its aggregated counters."""

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
