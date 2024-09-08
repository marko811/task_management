from django.contrib.auth.models import User
from django.db import models
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics
from rest_framework.exceptions import PermissionDenied
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated

from .models import Task
from .notifications import send_task_notification
from .serializers import TaskSerializer

task_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "id": openapi.Schema(
            type=openapi.TYPE_INTEGER,
            description="ID of the task",
        ),
        "title": openapi.Schema(
            type=openapi.TYPE_STRING,
            description="Title of the task",
        ),
        "description": openapi.Schema(
            type=openapi.TYPE_STRING,
            description="Detailed description of the task",
        ),
        "status": openapi.Schema(
            type=openapi.TYPE_STRING,
            enum=["pending", "in_progress", "completed"],
            description="Status of the task",
        ),
        "owner": openapi.Schema(
            type=openapi.TYPE_STRING,
            description="Username of the owner",
        ),
        "assignee": openapi.Schema(
            type=openapi.TYPE_INTEGER,
            nullable=True,
            description="User ID of the assignee",
        ),
        "due_date": openapi.Schema(
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_DATETIME,
            description="Due date of the task",
        ),
        "created_at": openapi.Schema(
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_DATETIME,
            description="Created timestamp of the task",
        ),
        "updated_at": openapi.Schema(
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_DATETIME,
            description="Updated timestamp of the task",
        ),
    },
)


# List and create tasks
class TaskListCreateView(generics.ListCreateAPIView):
    """
    get:
    Returns a list of tasks that the user has access to.

    post:
    Creates a new task with the provided data.
    """

    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        OrderingFilter,
    ]  # Filtering and ordering capabilities
    filterset_fields = [
        "owner",
        "status",
        "assignee",
        "due_date",
    ]  # Allow filtering by these fields
    ordering_fields = [
        "due_date",
        "created_at",
        "updated_at",
    ]  # Allow ordering by these fields

    # Start --- API Documentation
    @swagger_auto_schema(
        operation_description="Retrieve a list of tasks. Filters can be applied to retrieve tasks by status, assignee, or owner.",
        manual_parameters=[
            openapi.Parameter(
                "owner",
                openapi.IN_QUERY,
                description="Filter by the owner user ID",
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                "assignee",
                openapi.IN_QUERY,
                description="Filter by the assigned user ID",
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                "status",
                openapi.IN_QUERY,
                description="Filter by task status",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "due_date",
                openapi.IN_QUERY,
                description="Filter by due date (YYYY-MM-DD)",
                type=openapi.TYPE_STRING,
            ),
        ],
        responses={
            200: openapi.Response(
                description="A list of tasks.",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=task_schema,
                ),
                examples={
                    "application/json": [
                        {
                            "id": 1,
                            "title": "Complete project documentation",
                            "description": "Finish writing the API documentation",
                            "status": "pending",
                            "owner": "johndoe",
                            "assignee": 2,
                            "due_date": "2024-09-15T15:30:00Z",
                            "created_at": "2024-09-01T12:00:00Z",
                            "updated_at": "2024-09-01T12:00:00Z",
                        },
                        {
                            "id": 2,
                            "title": "Write unit tests",
                            "description": "Write unit tests for the project",
                            "status": "in_progress",
                            "owner": "janedoe",
                            "assignee": 3,
                            "due_date": None,
                            "created_at": "2024-09-02T08:00:00Z",
                            "updated_at": "2024-09-02T08:00:00Z",
                        },
                    ]
                },
            ),
            401: "Unauthorized",
        },
        tags=["Tasks"],
    )
    def get(self, request, *args, **kwargs):
        """Retrieve tasks, optionally filtered by status, assignee, or owner."""
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Create a new task. The task must include a title and description.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["title", "description"],
            properties={
                "title": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Title of the task",
                ),
                "description": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Detailed description of the task",
                ),
                "status": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Status of the task",
                    enum=["pending", "in_progress", "completed"],
                ),
                "assignee": openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="User ID of the assignee",
                ),
                "due_date": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_DATETIME,
                    description="Due date of the task",
                ),
            },
            example={
                "title": "Complete project documentation",
                "description": "Finish writing the API documentation",
                "status": "pending",
                "assignee": 2,
                "due_date": "2024-09-06T14:30:00Z",
            },
        ),
        responses={
            201: openapi.Response(
                description="Task created successfully",
                schema=task_schema,
                examples={
                    "application/json": {
                        "id": 1,
                        "title": "Complete project documentation",
                        "description": "Finish writing the API documentation",
                        "status": "pending",
                        "owner": "johndoe",
                        "assignee": 2,
                        "due_date": "2024-09-06T14:30:00Z",
                        "created_at": "2024-09-01T12:00:00Z",
                        "updated_at": "2024-09-01T12:00:00Z",
                    }
                },
            ),
            400: "Bad Request",
            401: "Unauthorized",
        },
        tags=["Tasks"],
    )
    def post(self, request, *args, **kwargs):
        """Create a new task."""
        return super().post(request, *args, **kwargs)

    # End --- API Documentation

    # Get filtered tasks for staff or individual users
    def get_queryset(self):
        return Task.objects.not_deleted()

    def perform_create(self, serializer):
        user = self.request.user
        task = serializer.save(owner=user)
        if task.assignee:
            send_task_notification.delay(task.id, "assigned")


# Retrieve, update, and delete tasks
class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    get:
    Retrieves the details of a specific task.

    put:
    Updates the details of a specific task.

    delete:
    Soft deletes a specific task.
    """

    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    # Start --- API Documentation
    @swagger_auto_schema(
        operation_description="Retrieve a specific task by its ID.",
        responses={
            200: openapi.Response(
                description="Details of the task.",
                schema=task_schema,
                examples={
                    "application/json": {
                        "id": 1,
                        "title": "Complete project documentation",
                        "description": "Finish writing the API documentation",
                        "status": "pending",
                        "owner": "johndoe",
                        "assignee": 2,
                        "due_date": "2024-09-06T14:30:00Z",
                        "created_at": "2024-09-01T12:00:00Z",
                        "updated_at": "2024-09-01T12:00:00Z",
                    }
                },
            ),
            401: "Unauthorized",
            403: "Forbidden",
            404: "Not Found",
        },
        tags=["Tasks"],
    )
    def get(self, request, *args, **kwargs):
        """Retrieve task by ID."""
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Update a task. The user can only update tasks they created. Admins can update any task.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["title", "description"],
            properties={
                "title": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Title of the task",
                ),
                "description": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Detailed description of the task",
                ),
                "status": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Status of the task",
                    enum=["pending", "in_progress", "completed"],
                ),
                "assignee": openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="User ID of the assignee",
                ),
                "due_date": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_DATETIME,
                    description="Due date of the task",
                ),
            },
            example={
                "title": "Update API documentation",
                "description": "Make necessary changes to the API documentation",
                "status": "in_progress",
                "assignee": 3,
                "due_date": "2024-09-20T10:00:00Z",
            },
        ),
        responses={
            200: openapi.Response(
                description="Task updated successfully",
                schema=task_schema,
                examples={
                    "application/json": {
                        "id": 1,
                        "title": "Update API documentation",
                        "description": "Make necessary changes to the API documentation",
                        "status": "in_progress",
                        "owner": "johndoe",
                        "assignee": 3,
                        "due_date": "2024-09-20T10:00:00Z",
                        "created_at": "2024-09-01T12:00:00Z",
                        "updated_at": "2024-09-05T16:00:00Z",
                    }
                },
            ),
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden",
            404: "Not Found",
        },
        tags=["Tasks"],
    )
    def put(self, request, *args, **kwargs):
        """Update a task."""
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Partially update a task. The user can only update tasks they created. Admins can update any task.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "title": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Title of the task",
                ),
                "description": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Detailed description of the task",
                ),
                "status": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Status of the task",
                    enum=["pending", "in_progress", "completed"],
                ),
                "assignee": openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="User ID of the assignee",
                ),
                "due_date": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_DATETIME,
                    description="Due date of the task",
                ),
            },
            example={"status": "completed"},
        ),
        responses={
            200: openapi.Response(
                description="Task updated successfully",
                schema=task_schema,
                examples={
                    "application/json": {
                        "id": 1,
                        "title": "Complete project documentation",
                        "description": "Finish writing the API documentation",
                        "status": "completed",
                        "creator": "johndoe",
                        "assignee": 2,
                        "due_date": "2024-09-15T15:30:00Z",
                        "created_at": "2024-09-01T12:00:00Z",
                        "updated_at": "2024-09-05T16:00:00Z",
                    }
                },
            ),
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden",
            404: "Not Found",
        },
        tags=["Tasks"],
    )
    def patch(self, request, *args, **kwargs):
        """Partially update a task."""
        return super().patch(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Delete a task (soft delete). Only the owner or an admin can delete a task.",
        request_body=None,
        responses={
            204: "Task deleted successfully",
            401: "Unauthorized",
            403: "Forbidden",
            404: "Not Found",
        },
        tags=["Tasks"],
    )
    def delete(self, request, *args, **kwargs):
        """Soft delete a task."""
        return super().delete(request, *args, **kwargs)

    # End --- API Documentation

    def get_queryset(self):
        return Task.objects.not_deleted()

    def perform_update(self, serializer):
        user = self.request.user
        task = self.get_object()
        if task.owner != user and not user.is_staff:
            raise PermissionDenied("You do not have permission to edit this task.")

        old_assignee = task.assignee
        task = serializer.save()
        send_task_notification.delay(task.id, "updated")

        # If assignee is changed, send an email notification to the assignee
        if task.assignee and old_assignee.id != task.assignee.id:
            send_task_notification.delay(task.id, "assigned")

    def perform_destroy(self, instance):
        user = self.request.user
        if instance.owner != user and not user.is_staff:
            raise PermissionDenied("You do not have permission to delete this task.")
        instance.delete()
