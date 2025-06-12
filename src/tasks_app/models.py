from django.db import models
# Using Django's built-in User model
from django.contrib.auth.models import User
from tasks_app import STATUS_CHOICES, PRIORITY_CHOICES
# Create your models here.


class Task(models.Model):

    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='todo')
    priority = models.CharField(
        max_length=20, choices=PRIORITY_CHOICES, default='medium')
    due_date = models.DateField(null=True, blank=True)
    assigned_to = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks_assigned')
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True, related_name='tasks_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['due_date', 'priority']

    def __str__(self):
        return self.title
