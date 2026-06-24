from rest_framework import permissions


class IsBoardMemberOrOwner(permissions.BasePermission):
    """Allows access to board owners and members."""

    def has_object_permission(self, request, view, obj):
        """True if the user owns or belongs to the board."""
        return (
                obj.owner_id == request.user.id
                or obj.members.filter(id=request.user.id).exists()
        )


class IsBoardOwner(permissions.BasePermission):
    """Allows access only to the board owner."""

    def has_object_permission(self, request, view, obj):
        """True if the user owns the board."""
        return obj.owner_id == request.user.id


class IsTaskBoardMemberOrOwner(permissions.BasePermission):
    """Allows access to members and the owner of the task's board."""

    def has_object_permission(self, request, view, obj):
        """True if the user owns or belongs to the task's board."""
        return (
                obj.board.owner_id == request.user.id
                or obj.board.members.filter(id=request.user.id).exists()
        )


class IsTaskCreatorOrBoardOwner(permissions.BasePermission):
    """Allows access to the task creator or the board owner."""

    def has_object_permission(self, request, view, obj):
        """True if the user created the task or owns its board."""
        return (
                obj.creator_id == request.user.id
                or obj.board.owner_id == request.user.id
        )
