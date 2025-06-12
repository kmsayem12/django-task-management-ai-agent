from typing import Optional, List, Dict, Any
from langchain_core.runnables import RunnableConfig
from django.contrib.auth import get_user_model
from langchain_core.runnables import RunnableConfig

from tasks_app.models import Task
from tasks_app.serializers import TaskSerializer
from tasks_app import STATUS_CHOICES, PRIORITY_CHOICES


class TaskToolsError(Exception):
    """Custom exception for task tools operations."""
    pass


class ToolsValidator:
    """Centralized validation and utilities for task operations."""

    DEFAULT_PRIORITY = 'medium'
    DEFAULT_STATUS = 'todo'
    DEFAULT_LIMIT = 5
    MAX_LIMIT = 20

    @staticmethod
    def get_user_from_config(config: RunnableConfig) -> int:
        """Extract and validate user ID from config."""
        if not config:
            raise TaskToolsError("Configuration is required")

        metadata = config.get('configurable') or config.get('metadata')
        if not metadata:
            raise TaskToolsError("Configuration metadata is required")

        created_by = metadata.get('created_by')
        if not created_by:
            raise TaskToolsError("created_by is required in configuration")

        return created_by

    @classmethod
    def validate_limit(cls, limit: int) -> int:
        """Validate and normalize limit parameter."""
        if limit < 1:
            return cls.DEFAULT_LIMIT
        return min(limit, cls.MAX_LIMIT)

    @classmethod
    def validate_priority(cls, priority: Optional[str]) -> str:
        print("Incoming priority type:", type(priority), "value:", priority)

        if priority is None:
            return cls.DEFAULT_PRIORITY

        # Handle tuple input
        if isinstance(priority, tuple):
            priority = priority[0]

        priority_lower = priority.lower()
        valid_priorities = [choice[0].lower() for choice in PRIORITY_CHOICES]

        if priority_lower not in valid_priorities:
            raise TaskToolsError(
                f"Invalid priority '{priority}'. Valid options: {', '.join([c[0] for c in PRIORITY_CHOICES])}"
            )

        return priority_lower

    @classmethod
    def validate_status(cls, status: Optional[str]) -> str:
        """Validate and normalize status parameter."""
        if status is None:
            return cls.DEFAULT_STATUS

        # Handle tuple input
        if isinstance(status, tuple):
            status = status[0]

        status_lower = status.lower()
        valid_statuses = [choice[0].lower() for choice in STATUS_CHOICES]

        if status_lower not in valid_statuses:
            raise TaskToolsError(
                f"Invalid status '{status}'. Valid options: {', '.join([c[0] for c in PRIORITY_CHOICES])}"
            )

        return status_lower

    @staticmethod
    def get_user_by_id(user_id: int):
        """Get user by ID with proper error handling."""
        User = get_user_model()
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise TaskToolsError(f"User with ID {user_id} does not exist")

    @staticmethod
    def get_task_by_id_or_title(task_id: Optional[int] = None, title: Optional[str] = None) -> Task:
        """Get a single task by ID or title with proper error handling."""
        if not task_id and not title:
            raise TaskToolsError("Either task_id or title must be provided")

        try:
            if task_id is not None:
                return Task.objects.get(id=task_id)
            else:
                return Task.objects.get(title=title)
        except Task.DoesNotExist:
            identifier = f"ID {task_id}" if task_id else f"title '{title}'"
            raise TaskToolsError(f"Task with {identifier} does not exist")
        except Task.MultipleObjectsReturned:
            raise TaskToolsError(
                f"Multiple tasks found with title '{title}'. Use task_id instead.")

    @staticmethod
    def validate_search_query(query: str) -> str:
        """Validate and normalize search query."""
        if not query or not query.strip():
            raise TaskToolsError("Search query cannot be empty")
        return query.strip()

    @staticmethod
    def serialize_task(task: Task) -> Dict[str, Any]:
        """Serialize a single task."""
        serializer = TaskSerializer(task)
        return serializer.data

    @staticmethod
    def serialize_tasks(tasks) -> List[Dict[str, Any]]:
        """Serialize multiple tasks."""
        serializer = TaskSerializer(tasks, many=True)
        return serializer.data
