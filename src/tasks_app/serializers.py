from rest_framework import serializers
from django.contrib.auth.models import User

from .models import Task


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class TaskSerializer(serializers.ModelSerializer):

    # Define computed read-only fields
    assigned_to_username = serializers.SerializerMethodField()
    created_by_username = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'status', 'priority', 'due_date',
            # assigned_to for write, assigned_to_username for read
            'assigned_to', 'assigned_to_username',
            # created_by for write, created_by_username for read
            'created_by', 'created_by_username',
            'created_at', 'updated_at'
        ]

        read_only_fields = ['created_at', 'updated_at',
                            'assigned_to_username', 'created_by_username']

    def get_assigned_to_username(self, obj):
        return obj.assigned_to.username if obj.assigned_to else None

    def get_created_by_username(self, obj):
        return obj.created_by.username if obj.created_by else None

    def validate_title(self, value):
        if not value.strip():
            raise serializers.ValidationError("Title cannot be empty.")
        return value

    def validate_description(self, value):
        if not value.strip():
            raise serializers.ValidationError("Description cannot be empty.")
        return value
