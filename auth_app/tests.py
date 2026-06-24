"""Tests for the auth API: registration, login, email check."""
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase


class RegistrationTests(APITestCase):
    """Covers the registration endpoint."""

    url = '/api/registration/'

    def setUp(self):
        """Provides a valid registration payload."""
        self.payload = {
            'fullname': 'Max Muster',
            'email': 'max@mail.de',
            'password': 'pass1234',
            'repeated_password': 'pass1234',
        }

    def test_registration_succeeds(self):
        """A valid payload creates a user and returns a token."""
        response = self.client.post(self.url, self.payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['email'], 'max@mail.de')

    def test_password_mismatch_returns_400(self):
        """Mismatched passwords are rejected."""
        self.payload['repeated_password'] = 'different'
        response = self.client.post(self.url, self.payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_duplicate_email_returns_400(self):
        """Registering an existing email is rejected."""
        User.objects.create_user(
            username='max@mail.de', email='max@mail.de', password='x'
        )
        response = self.client.post(self.url, self.payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoginTests(APITestCase):
    """Covers the login endpoint."""

    url = '/api/login/'

    def setUp(self):
        """Creates a user with a token to log in with."""
        self.user = User.objects.create_user(
            username='max@mail.de',
            email='max@mail.de',
            password='pass1234',
            first_name='Max Muster',
        )
        Token.objects.create(user=self.user)

    def test_login_succeeds(self):
        """Valid credentials return a token."""
        response = self.client.post(
            self.url,
            {'email': 'max@mail.de', 'password': 'pass1234'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

    def test_wrong_password_returns_400(self):
        """Invalid credentials are rejected."""
        response = self.client.post(
            self.url,
            {'email': 'max@mail.de', 'password': 'wrong'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class EmailCheckTests(APITestCase):
    """Covers the email-check endpoint."""

    url = '/api/email-check/'

    def setUp(self):
        """Creates and authenticates a user."""
        self.user = User.objects.create_user(
            username='max@mail.de',
            email='max@mail.de',
            password='pass1234',
            first_name='Max Muster',
        )
        token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

    def test_existing_email_returns_user(self):
        """A known email returns the matching user."""
        response = self.client.get(self.url, {'email': 'max@mail.de'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['fullname'], 'Max Muster')

    def test_missing_email_returns_400(self):
        """A missing email parameter is rejected."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unknown_email_returns_404(self):
        """An unknown email returns 404."""
        response = self.client.get(self.url, {'email': 'nobody@mail.de'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_requires_authentication(self):
        """Anonymous users get 401."""
        self.client.credentials()
        response = self.client.get(self.url, {'email': 'max@mail.de'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invalid_email_format_returns_400(self):
        """A malformed email value is rejected."""
        response = self.client.get(self.url, {'email': 'not-an-email'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
