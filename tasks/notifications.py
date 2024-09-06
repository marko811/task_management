from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from .models import Task


@shared_task
def send_task_notification(task_id, action):
    task = Task.objects.get(id=task_id)
    subject = f"Task {action}: {task.title}"
    message = f'Task "{task.title}" has been {action}.'
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [task.assignee.email],
        fail_silently=False,
    )


@shared_task
def send_due_date_reminder():
    now = timezone.now()
    tasks = Task.objects.filter(
        due_date__lte=now + timezone.timedelta(days=1), status="pending"
    )
    for task in tasks:
        subject = f'Reminder: Task "{task.title}" is due soon'
        message = f'This is a reminder that the task "{task.title}" is due on {task.due_date}.'
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [task.assignee.email],
            fail_silently=False,
        )
