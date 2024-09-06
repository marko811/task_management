from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


# Custom query set to handle soft-delete logic and non-deleted task filtering
class TaskQuerySet(models.QuerySet):
    # Filter out soft-deleted tasks
    def not_deleted(self):
        return self.filter(is_deleted=False)

    # Get soft-deleted tasks
    def deleted(self):
        return self.filter(is_deleted=True)


# Task model representing the tasks created in the system
class Task(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
    ]

    # Fields for task details
    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    owner = models.ForeignKey(
        User, related_name="owned_tasks", on_delete=models.CASCADE
    )  # Creator of the task
    assignee = models.ForeignKey(
        User,
        related_name="assigned_tasks",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    due_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)  # Soft-delete flag
    deleted_at = models.DateTimeField(
        null=True, blank=True
    )  # Timestamp for when the task was soft-deleted

    # Use custom query set for filtering
    objects = TaskQuerySet.as_manager()

    def __str__(self):
        return self.title

    # Override default delete method to perform soft delete
    def delete(self, *args, **kwargs):
        """
        Soft delete the task by setting is_deleted to True and marking the deletion time.
        """
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()

    class Meta:
        db_table = "tm_tasks"
        ordering = [
            "-created_at"
        ]  # Default ordering for task listings (most recent first)
