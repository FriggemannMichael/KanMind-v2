"""Authentication API views: registration, login, email check."""
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import validate_email
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    LoginSerializer,
    RegistrationSerializer,
    UserResponseSerializer,
)


def auth_payload(user):
    """Builds the token-and-user response payload for a user."""
    return {
        'token': user.auth_token.key,
        'fullname': user.get_full_name() or user.username,
        'email': user.email,
        'user_id': user.id,
    }


class RegistrationView(generics.CreateAPIView):
    """Registers a new user and returns a token."""

    serializer_class = RegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        """Creates the user and returns the auth payload (201)."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(auth_payload(user), status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """Authenticates a user and returns a token."""

    permission_classes = [AllowAny]

    def post(self, request):
        """Validates credentials and returns the auth payload."""
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(auth_payload(serializer.validated_data['user']))


class EmailCheckView(generics.RetrieveAPIView):
    """Looks up a user by email passed as a query parameter."""

    serializer_class = UserResponseSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """Validates the email param and returns the matching user."""
        email = self.request.query_params.get('email')
        if not email:
            raise ValidationError(
                {'email': 'This query parameter is required.'}
            )
        try:
            validate_email(email)
        except DjangoValidationError as exc:
            raise ValidationError(
                {'email': 'Enter a valid email address.'}
            ) from exc
        return generics.get_object_or_404(User, email__iexact=email)
