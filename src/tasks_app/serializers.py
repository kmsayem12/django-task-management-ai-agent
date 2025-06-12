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
            'assigned_to', 'assigned_to_username', # assigned_to for write, assigned_to_username for read
            'created_by', 'created_by_username', # created_by for write, created_by_username for read
            'created_at', 'updated_at'
        ]

        read_only_fields = ['created_by','created_at', 'updated_at', 'assigned_to_username', 'created_by_username']

    def get_assigned_to_username(self, obj):
        return obj.assigned_to.username if obj.assigned_to else None

    def get_created_by_username(self, obj):
        return obj.created_by.username if obj.created_by else None

    def created(self, validated_data):
        # Set created_by to the current user (from request context)
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        # Allow updating assigned_to by username if provided
        assigned_to_username = validated_data.pop('assigned_to_username', None)
        if assigned_to_username:
            try:
                assigned_to_user = User.objects.get(username=assigned_to_username)
                validated_data['assigned_to'] = assigned_to_user
            except User.DoesNotExist:
                raise serializers.ValidationError({"assigned_to_username": "User does not exist"})
        return super().update(instance, validated_data)