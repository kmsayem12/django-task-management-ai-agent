import json
from typing import Optional, List, Dict, Any
from django.db.models import Q
from django.core.exceptions import ValidationError
from langchain_core.tools import tool
from django.contrib.auth import get_user_model
from langchain_core.runnables import RunnableConfig

from tasks_app.models import Task
from tasks_app.serializers import TaskSerializer
from tasks_app import STATUS_CHOICES, PRIORITY_CHOICES
from ai_agent.tools_validator import ToolsValidator, TaskToolsError


@tool
def get_tasks(config: RunnableConfig, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Get a list of latest tasks for the authenticated user.

    Args:
        config: Configuration containing user information
        limit: Number of results (default: 5, max: 20)

    Returns:
        List of task dictionaries
    """
    try:
        # Initialize validator instance
        validator = ToolsValidator()
        created_by = validator.get_user_from_config(config)
        validated_limit = validator.validate_limit(limit)

        tasks = Task.objects.filter(
            created_by=created_by
        ).order_by('-created_at')[:validated_limit]

        return validator.serialize_tasks(tasks)

    except Exception as e:
        if isinstance(e, TaskToolsError):
            raise
        raise TaskToolsError(f"Error retrieving tasks: {str(e)}")


@tool
def create_task(
    title: str,
    description: str,
    config: RunnableConfig,
    priority: Optional[str] = None,
    status: Optional[str] = None,
    assigned_to: Optional[str] = None,
    due_date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a new task.

    Args:
        title: Task title (required)
        description: Task description (required)
        config: Configuration containing user information
        priority: Task priority (optional, default: 'medium')
        status: Task status (optional, default: 'todo')
        assigned_to: username to assign task to (optional)
        due_date: Due date in string format (optional)

    Returns:
        Created task dictionary
    """
    try:
        # Initialize validator instance
        validator = ToolsValidator()

        # 1. Extract user and validate fields
        created_by_id = validator.get_user_from_config(config)
        created_by_user = validator.get_user_by_id(created_by_id)

        validated_priority = validator.validate_priority(priority)
        validated_status = validator.validate_status(status)

        assigned_to_user = None
        if assigned_to is not None:
            assigned_to_user = validator.get_user_by_username(assigned_to)

         # 2. Build input data for the serializer
        task_data = {
            "title": title,
            "description": description,
            "priority": validated_priority,
            "status": validated_status,
            "due_date": due_date,
            "assigned_to": assigned_to_user.id if assigned_to_user else None,
            "created_by": created_by_user.id
        }
        # 3. Use DRF serializer for validation + creation
        serializer = TaskSerializer(data=task_data)
        if serializer.is_valid():
            task = serializer.save()
            return serializer.data
        else:
            raise TaskToolsError(f"Validation error: {serializer.errors}")

    except Exception as e:
        raise Exception(f"Error creating task: {e}")

    return task


@tool
def update_task(
    config: RunnableConfig,
    task_id: Optional[int] = None,
    title: Optional[str] = None,
    description: Optional[str] = None,
    due_date: Optional[str] = None,
    assigned_to: Optional[str] = None,
    priority: Optional[str] = None,
    status: Optional[str] = None
) -> Dict[str, Any]:
    """
    Update an existing task by ID or title.

    Args:
        config: Configuration containing user information
        task_id: Task ID to update (optional if title provided)
        title: Task title to find and update (optional if task_id provided)
        description: New description (optional)
        due_date: New due date (optional)
        assigned_to: New assigned username (optional)
        priority: New priority (optional)
        status: New status (optional)

    Returns:
        Updated task dictionary
    """
    try:
        # Initialize validator instance
        validator = ToolsValidator()
        created_by = validator.get_user_from_config(config)
        task = validator.get_task_by_id_or_title(task_id, title, created_by)

        validated_priority = validator.validate_priority(priority)
        validated_status = validator.validate_status(status)

        assigned_to_user = None
        if assigned_to is not None:
            assigned_to_user = validator.get_user_by_username(assigned_to)

        update_data = {
            "title": title if title else task.title,
            "description": description if description else task.description,
            "priority": validated_priority if priority else task.priority,
            "status": validated_status if status else task.status,
            "due_date": due_date if due_date else task.due_date,
            "assigned_to": assigned_to_user.id if assigned_to_user else (task.assigned_to.id if task.assigned_to else None),
        }
        # Use DRF serializer for validation + update
        serializer = TaskSerializer(task, data=update_data, partial=True)
        if serializer.is_valid():
            updated_task = serializer.save()
            return serializer.data
        else:
            raise TaskToolsError(f"Validation error: {serializer.errors}")

    except ValidationError as e:
        raise TaskToolsError(f"Validation error: {str(e)}")
    except Exception as e:
        if isinstance(e, TaskToolsError):
            raise
        raise TaskToolsError(f"Error updating task: {str(e)}")


@tool
def delete_task(
    config: RunnableConfig,
    task_id: Optional[int] = None,
    title: Optional[str] = None
) -> Dict[str, str]:
    """
    Delete a task by ID or title.

    Args:
        config: Configuration containing user information
        task_id: Task ID to delete (optional if title provided)
        title: Task title to find and delete (optional if task_id provided)

    Returns:
        Success message dictionary
    """
    try:
        # Initialize validator instance
        validator = ToolsValidator()
        created_by = validator.get_user_from_config(config)
        task = validator.get_task_by_id_or_title(task_id, title, created_by)
        task_identifier = f"'{task.title}' (ID: {task.id})"
        task.delete()

        return {"message": f"Task {task_identifier} deleted successfully"}

    except Exception as e:
        if isinstance(e, TaskToolsError):
            raise
        raise TaskToolsError(f"Error deleting task: {str(e)}")


@tool
def get_task(
    config: RunnableConfig,
    task_id: Optional[int] = None,
    title: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get a single task by ID or title.

    Args:
        config: Configuration containing user information
        task_id: Task ID to retrieve (optional if title provided)
        title: Task title to find (optional if task_id provided)

    Returns:
        Task dictionary
    """
    try:
        # Initialize validator instance
        validator = ToolsValidator()
        created_by = validator.get_user_from_config(config)
        task = validator.get_task_by_id_or_title(task_id, title, created_by)
        return validator.serialize_task(task)

    except Exception as e:
        if isinstance(e, TaskToolsError):
            raise
        raise TaskToolsError(f"Error retrieving task: {str(e)}")


@tool
def search_tasks(
    query: str,
    config: RunnableConfig,
    limit: int = 5
) -> List[Dict[str, Any]]:
    """
    Search tasks by query string in title and description.

    Args:
        query: Search query string
        config: Configuration containing user information
        limit: Number of results (default: 5, max: 20)

    Returns:
        List of matching task dictionaries
    """
    try:
        # Initialize validator instance
        validator = ToolsValidator()
        created_by = validator.get_user_from_config(config)
        validated_limit = validator.validate_limit(limit)
        validated_query = validator.validate_search_query(query)

        tasks = Task.objects.filter(
            created_by=created_by
        ).filter(
            Q(title__icontains=validated_query) | Q(
                description__icontains=validated_query)
        ).order_by('-created_at')[:validated_limit]

        return validator.serialize_tasks(tasks)

    except Exception as e:
        if isinstance(e, TaskToolsError):
            raise
        raise TaskToolsError(f"Error searching tasks: {str(e)}")


# Export all tools
task_tools = [
    get_tasks,
    create_task,
    update_task,
    delete_task,
    get_task,
    search_tasks
]

__all__ = [
    'task_tools',
    'get_tasks',
    'create_task',
    'update_task',
    'delete_task',
    'get_task',
    'search_tasks',
]
