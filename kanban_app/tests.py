"""Tests for the kanban API: boards, tasks, and comments."""
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from kanban_app.models import Board, Comment, Task


def make_user(name, email):
    """Creates a user and returns it with its auth token key."""
    user = User.objects.create_user(
        username=email, email=email, password='pass1234', first_name=name
    )
    return user, Token.objects.create(user=user).key


class KanbanBaseTest(APITestCase):
    """Shared users and helpers for the kanban API tests."""

    def setUp(self):
        """Creates an owner, a board member, and an outsider."""
        self.owner, self.owner_token = make_user('Owner', 'owner@mail.de')
        self.member, self.member_token = make_user('Member', 'member@mail.de')
        self.outsider, self.outsider_token = make_user('Out', 'out@mail.de')

    def auth(self, token):
        """Authenticates the test client with the given token."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')

    def make_board(self, owner, members=()):
        """Creates a board with an owner and optional members."""
        board = Board.objects.create(title='Board', owner=owner)
        board.members.set(members)
        return board


class BoardTests(KanbanBaseTest):
    """Covers the board endpoints."""

    url = '/api/boards/'

    def test_list_returns_only_accessible_boards(self):
        """A user sees only boards they own or belong to."""
        self.make_board(self.owner, members=[self.member])
        self.make_board(self.outsider)
        self.auth(self.member_token)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_sets_owner_as_member(self):
        """Creating a board adds the owner to its members."""
        self.auth(self.owner_token)
        response = self.client.post(
            self.url, {'title': 'New', 'members': []}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['member_count'], 1)
        self.assertEqual(response.data['owner_id'], self.owner.id)

    def test_requires_authentication(self):
        """Anonymous users cannot list boards."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_detail_allows_member(self):
        """A board member can read the board detail."""
        board = self.make_board(self.owner, members=[self.member])
        self.auth(self.member_token)
        response = self.client.get(f'{self.url}{board.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_detail_forbids_outsider(self):
        """A non-member gets 403 on board detail."""
        board = self.make_board(self.owner)
        self.auth(self.outsider_token)
        response = self.client.get(f'{self.url}{board.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_detail_missing_returns_404(self):
        """An unknown board id returns 404."""
        self.auth(self.owner_token)
        response = self.client.get(f'{self.url}999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_updates_title_and_members(self):
        """The owner can update title and member list."""
        board = self.make_board(self.owner)
        self.auth(self.owner_token)
        response = self.client.patch(
            f'{self.url}{board.id}/',
            {'title': 'Renamed', 'members': [self.member.id]},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Renamed')
        self.assertEqual(len(response.data['members_data']), 1)

    def test_delete_allows_owner(self):
        """The owner can delete the board."""
        board = self.make_board(self.owner, members=[self.member])
        self.auth(self.owner_token)
        response = self.client.delete(f'{self.url}{board.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_forbids_non_owner(self):
        """A member who is not the owner cannot delete the board."""
        board = self.make_board(self.owner, members=[self.member])
        self.auth(self.member_token)
        response = self.client.delete(f'{self.url}{board.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TaskTests(KanbanBaseTest):
    """Covers the task endpoints."""

    url = '/api/tasks/'

    def setUp(self):
        """Adds a shared board with the member for task tests."""
        super().setUp()
        self.board = self.make_board(self.owner, members=[self.member])

    def payload(self, **overrides):
        """Builds a valid task creation payload."""
        data = {
            'board': self.board.id,
            'title': 'Task',
            'description': 'desc',
            'status': 'to-do',
            'priority': 'high',
        }
        data.update(overrides)
        return data

    def make_task(self, creator, assignee=None, reviewer=None):
        """Creates a task on the shared board."""
        return Task.objects.create(
            board=self.board, title='T', status='to-do', priority='low',
            creator=creator, assignee=assignee, reviewer=reviewer,
        )

    def test_member_can_create_task(self):
        """A board member creates a task."""
        self.auth(self.member_token)
        response = self.client.post(self.url, self.payload(), format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_outsider_cannot_create_task(self):
        """A non-member is forbidden from creating tasks."""
        self.auth(self.outsider_token)
        response = self.client.post(self.url, self.payload(), format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_assignee_must_be_board_member(self):
        """Assigning a non-member is rejected."""
        self.auth(self.owner_token)
        data = self.payload(assignee_id=self.outsider.id)
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_on_missing_board_returns_404(self):
        """A non-existent board id returns 404."""
        self.auth(self.owner_token)
        response = self.client.post(
            self.url, self.payload(board=999), format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_member_can_patch_task(self):
        """A board member can update a task's status."""
        task = self.make_task(self.owner)
        self.auth(self.member_token)
        response = self.client.patch(
            f'{self.url}{task.id}/', {'status': 'done'}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'done')

    def test_creator_can_delete_task(self):
        """The task creator can delete it."""
        task = self.make_task(self.member)
        self.auth(self.member_token)
        response = self.client.delete(f'{self.url}{task.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_other_member_cannot_delete_task(self):
        """A member who is neither creator nor owner cannot delete."""
        extra, extra_token = make_user('Extra', 'extra@mail.de')
        self.board.members.add(extra)
        task = self.make_task(self.member)
        self.auth(extra_token)
        response = self.client.delete(f'{self.url}{task.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_assigned_to_me_lists_user_tasks(self):
        """assigned-to-me returns tasks assigned to the user."""
        self.make_task(self.owner, assignee=self.member)
        self.auth(self.member_token)
        response = self.client.get(f'{self.url}assigned-to-me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_reviewing_lists_user_tasks(self):
        """reviewing returns tasks the user reviews."""
        self.make_task(self.owner, reviewer=self.member)
        self.auth(self.member_token)
        response = self.client.get(f'{self.url}reviewing/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_patch_assignee_must_be_board_member(self):
        """Reassigning a task to a non-member is rejected."""
        task = self.make_task(self.owner)
        self.auth(self.member_token)
        response = self.client.patch(
            f'{self.url}{task.id}/',
            {'assignee_id': self.outsider.id},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_with_malformed_board_id_returns_400(self):
        """A non-numeric board id is rejected."""
        self.auth(self.owner_token)
        response = self.client.post(
            self.url, self.payload(board='abc'), format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_without_board_returns_400(self):
        """A missing board id is rejected."""
        self.auth(self.owner_token)
        data = self.payload()
        data.pop('board')
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class CommentTests(KanbanBaseTest):
    """Covers the task comment endpoints."""

    def setUp(self):
        """Adds a board, a task, and a comment URL for comment tests."""
        super().setUp()
        self.board = self.make_board(self.owner, members=[self.member])
        self.task = Task.objects.create(
            board=self.board, title='T', status='to-do',
            priority='low', creator=self.owner,
        )
        self.list_url = f'/api/tasks/{self.task.id}/comments/'

    def make_comment(self, author):
        """Creates a comment on the shared task."""
        return Comment.objects.create(
            task=self.task, author=author, content='hi'
        )

    def test_member_can_list_comments(self):
        """A board member can list a task's comments."""
        self.make_comment(self.owner)
        self.auth(self.member_token)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_outsider_cannot_list_comments(self):
        """A non-member gets 403 on a task's comments."""
        self.auth(self.outsider_token)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_member_can_create_comment(self):
        """A board member creates a comment as its author."""
        self.auth(self.member_token)
        response = self.client.post(
            self.list_url, {'content': 'Hello'}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['author'], 'Member')

    def test_comments_on_missing_task_return_404(self):
        """Commenting on an unknown task returns 404."""
        self.auth(self.member_token)
        response = self.client.get('/api/tasks/999/comments/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_author_can_delete_comment(self):
        """The comment author can delete it."""
        comment = self.make_comment(self.member)
        self.auth(self.member_token)
        url = f'{self.list_url}{comment.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_non_author_cannot_delete_comment(self):
        """A user who is not the author cannot delete the comment."""
        comment = self.make_comment(self.owner)
        self.auth(self.member_token)
        url = f'{self.list_url}{comment.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
