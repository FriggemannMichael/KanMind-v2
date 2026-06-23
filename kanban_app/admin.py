"""Admin registrations for board, task, and comment models."""
from django.contrib import admin

from .models import Board, Comment, Task

admin.site.register(Board)
admin.site.register(Comment)
admin.site.register(Task)
