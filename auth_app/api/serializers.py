"""Serializers for registration, login, and user lookups."""
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.authtoken.models import Token


class UserResponseSerializer(serializers.ModelSerializer):
    """Serializes a user as id, email, and full name."""

    fullname = serializers.SerializerMethodField()

    class Meta:
        """Maps the public user fields."""

        model = User
        fields = ['id', 'email', 'fullname']

    def get_fullname(self, obj):
        """Returns the user's full name or username as fallback."""
        return obj.get_full_name() or obj.username


class RegistrationSerializer(serializers.Serializer):
    """Validates registration data and creates a user with a token."""

    fullname = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=4)
    repeated_password = serializers.CharField(write_only=True, min_length=4)

    def validate_email(self, value):
        """Rejects duplicate emails and normalises to lower case."""
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('A user with this email exists.')
        return value.lower()

    def validate(self, attrs):
        """Ensures both password fields match."""
        if attrs['password'] != attrs['repeated_password']:
            raise serializers.ValidationError(
                {'repeated_password': 'Passwords do not match.'}
            )
        return attrs

    def create(self, validated_data):
        """Creates the user and its authentication token."""
        user = User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['fullname'],
        )
        Token.objects.create(user=user)
        return user


class LoginSerializer(serializers.Serializer):
    """Validates credentials and exposes the authenticated user."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        """Authenticates the user from email and password."""
        user = authenticate(
            username=attrs['email'].lower(),
            password=attrs['password'],
        )
        if user is None:
            raise serializers.ValidationError('Invalid credentials.')
        attrs['user'] = user
        return attrs
