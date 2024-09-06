from django.contrib.auth.models import User
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import (
    TokenBlacklistView,
    TokenObtainPairView,
    TokenRefreshView,
)

from .serializers import RegisterSerializer


# RegisterView
class RegisterView(generics.CreateAPIView):
    """
    Registers a new user with a username, email, and password.
    """

    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    # Start --- API Documentation
    @swagger_auto_schema(
        security=[],
        operation_id="user_register",
        operation_description="Register a new user.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["username", "email", "password"],
            properties={
                "username": openapi.Schema(
                    type=openapi.TYPE_STRING, description="User's username (User ID)"
                ),
                "email": openapi.Schema(
                    type=openapi.TYPE_STRING, description="User's email address "
                ),
                "password": openapi.Schema(
                    type=openapi.TYPE_STRING, description="User's password"
                ),
            },
            example={
                "username": "johndoe",
                "email": "johndoe@mail.com",
                "password": "yourpassword",
            },
        ),
        responses={
            201: openapi.Response(
                description="New user successfully registered.",
                examples={
                    "application/json": {
                        "username": "johndoe",
                        "email": "johndoe@mail.com",
                    },
                },
            ),
            400: "Bad Request",
        },
        tags=["Authentication"],
    )
    def post(self, request, *args, **kwargs):
        """Register a new user."""
        return super().post(request, *args, **kwargs)

    # End --- API Documentation


# LoginView - Subclass the TokenObtainPairView and add custom documentation
class LoginView(TokenObtainPairView):
    """
    User login and get access and refresh tokens.
    """

    @swagger_auto_schema(
        security=[],
        operation_id="user_login",
        operation_description="Obtain a JWT access and refresh token by providing a valid username and password.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["username", "password"],
            properties={
                "username": openapi.Schema(
                    type=openapi.TYPE_STRING, description="User's username"
                ),
                "password": openapi.Schema(
                    type=openapi.TYPE_STRING, description="User's password"
                ),
            },
            example={"username": "johndoe", "password": "yourpassword"},
        ),
        responses={
            200: openapi.Response(
                description="A user successfully logged in.",
                examples={
                    "application/json": {
                        "access": "eyJ0eXAiOiJKV1QiLCJhb...",
                        "refresh": "eyKV1QiLCJhbdsUzI1NiJ9...",
                    },
                },
            ),
            400: "Bad Request",
            401: "Unauthorized",
        },
        tags=["Authentication"],
    )
    def post(self, request, *args, **kwargs):
        """
        API endpoint to obtain JWT tokens (access and refresh).
        """
        return super().post(request, *args, **kwargs)


# TokenRefreshView - Subclass the TokenRefreshView and add custom documentation
class UserTokenRefreshView(TokenRefreshView):
    """
    Refresh JWT access token using the refresh token.
    """

    @swagger_auto_schema(
        security=[],
        operation_id="user_token_refresh",
        operation_description="Refresh a JWT access token using a valid refresh token.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["refresh"],
            properties={
                "refresh": openapi.Schema(
                    type=openapi.TYPE_STRING, description="JWT refresh token"
                ),
            },
            example={"refresh": "eyKV1QiLCJhbdsUzI1NiJ9..."},
        ),
        responses={
            200: openapi.Response(
                description="Returned a new access token.",
                examples={
                    "application/json": {
                        "access": "eyJ0eXAiOiJKV1QiLCJhb...",
                    },
                },
            ),
            400: "Bad Request",
            401: "Unauthorize",
        },
        tags=["Authentication"],  # Tag to group endpoints related to authentication
    )
    def post(self, request, *args, **kwargs):
        """Handle the refresh token and return a new access token."""
        return super().post(request, *args, **kwargs)


# LogoutView - Subclass the TokenBlacklistView and add custom documentation
class LogoutView(TokenBlacklistView):
    """
    Logs out the user by invalidating their tokens
    """

    @swagger_auto_schema(
        security=[],
        operation_id="user_logout",
        operation_description="Logout the user. This will invalidate the JWT tokens",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["refresh"],
            properties={
                "refresh": openapi.Schema(
                    type=openapi.TYPE_STRING, description="JWT refresh token"
                ),
            },
            example={"refresh": "eyKV1QiLCJhbdsUzI1NiJ9..."},
        ),
        responses={
            200: "Logged out successfully",
            400: "Bad Request",
            401: "Unauthorize",
        },
        tags=["Authentication"],
    )
    def post(self, request, *args, **kwargs):
        """
        Logout the user.
        Blacklist the provided refresh token.
        """
        super().post(request, *args, **kwargs)
        return Response("Logged out successfully", status=status.HTTP_200_OK)
