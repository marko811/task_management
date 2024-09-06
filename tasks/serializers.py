from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from rest_framework import serializers

from .models import Task


# Serializer for user registration
class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "password"]

    # Custom validation to ensure email uniqueness
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise ValidationError("This email is already in use.")
        return value

    # Custom user creation method
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
        )
        return user


# Serializer for task creation, update, and listing
class TaskSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.username")
    assignee = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), required=False, allow_null=True
    )
    due_date = serializers.DateTimeField(required=False, allow_null=True)

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "status",
            "owner",
            "assignee",
            "due_date",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["owner", "created_at", "updated_at"]


class UserSerializer(serializers.ModelSerializer):
    owned_tasks = TaskSerializer(many=True, read_only=True)
    assigned_tasks = TaskSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "owned_tasks", "assigned_tasks"]
