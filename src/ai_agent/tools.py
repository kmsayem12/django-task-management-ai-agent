import json
from django.db.models import Q
from langchain_core.tools import tool
from django.contrib.auth import get_user_model
from langchain_core.runnables import RunnableConfig

from tasks_app.models import Task
from tasks_app.serializers import TaskSerializer


@tool
def get_tasks(config: RunnableConfig, limit: int = 5):
    """
    list of latest 5 tasks for the created_by user
    arguments: 
    limit number of results and default is 5 max limit is 20
    """
    metadata = config.get('configurable') or config.get('metadata')
    created_by = metadata.get('created_by')

    if limit >= 20:
        limit = 20

    if not created_by:
        raise Exception("created_by is required")

    try:
        tasks = Task.objects.filter(
            created_by=created_by).order_by('-created_at')[:limit]
    except Exception as e:
        raise Exception(f"Error get task list: {e}")
    return tasks


@tool
def create_task(title: str, description: str, priority: str, status: str, config: RunnableConfig, assigned_to: int = None, due_date: str = None):
    """
    Creates new task based on arguments
    Arguments are:
    title and description and assigned_to and due_date and priority and status are get from the messages
    assigned_to and priority and status is not required
    """
    metadata = config.get('configurable') or config.get('metadata')
    created_by = metadata.get('created_by')
    User = get_user_model()

    if not created_by:
        raise Exception("created_by is required")

    if not priority:
        priority = 'medium'

    if not status:
        status = 'todo'

    if assigned_to is not None:
        assigned_to_user = User.objects.get(id=assigned_to)
    else:
        assigned_to_user = None
    try:
        created_by = User.objects.get(id=created_by)

        task = Task(title=title, description=description,
                    priority=priority,
                    status=status,
                    due_date=due_date, assigned_to=assigned_to_user, created_by=created_by)
        task.save()
    except Exception as e:
        raise Exception(f"Error creating task: {e}")

    return task


@tool
def update_task(task_id: int = None, title: str = None, description: str = None, due_date: str = None, assigned_to: str = None, priority: str = None, status: str = None, config: RunnableConfig = None):
    """
    Update the task by task_id or title based on arguments
    Arguments are:
    title and description and assigned_to and due_date and priority and status are get from the messages
    all arguments is optional
    """
    print('update_task', task_id, title, description,
          due_date, assigned_to, priority, status, config)
    if task_id is not None:
        task = Task.objects.get(id=task_id)
    else:
        task = Task.objects.get(title=title)

    if not task:
        raise Exception("Task does not found")

    if title is not None:
        task.title = title
    if description is not None:
        task.description = description
    if due_date is not None:
        task.due_date = due_date
    if assigned_to is not None:
        task.assigned_to = assigned_to
    if priority is not None:
        task.priority = priority
    if status is not None:
        task.status = status

    try:
        task.title = task.title
        task.description = task.description
        task.due_date = task.due_date
        task.assigned_to = task.assigned_to
        task.priority = task.priority
        task.status = task.status
        task.save()
    except Exception as e:
        raise Exception(f"Error updating task: {e}")
    except Task.MultipleObjectsReturned:
        raise Exception("Multiple tasks found with the same title!")
    return task


@tool
def delete_task(task_id: int = None, title: str = None, config: RunnableConfig = None):
    """
    Deletes the task by task_id or title based on arguments
    Arguments are:
    task_id and title are get from the messages
    """
    if task_id is not None:
        task = Task.objects.get(id=task_id)
    else:
        task = Task.objects.get(title=title)

    try:
        task.delete()
    except Task.DoesNotExist:
        raise Exception("Task does not exist")
    except Task.MultipleObjectsReturned:
        raise Exception("Multiple tasks found with the same title!")
    return task


@tool
def get_task(task_id: int = None, title: str = None, config: RunnableConfig = None):
    """
    get single task by task_id or title based on arguments
    Arguments are:
    task_id and title are get from the messages
    """

    try:
        if task_id is not None:
            task = Task.objects.get(id=task_id)
        else:
            task = Task.objects.get(title=title)

    except Task.DoesNotExist:
        raise Exception("Task does not exist")
    except Task.MultipleObjectsReturned:
        raise Exception("Multiple tasks found with the same title!")
    return task


def search_tasks(query: str,  config: RunnableConfig, limit: int = 5):
    """
    search the latest 5 tasks for the created_by user
    arguments: 
    query string are looked up in title and description
    limit number of results and default is 5 max limit is 20
    """
    metadata = config.get('configurable') or config.get('metadata')
    created_by = metadata.get('created_by')

    if limit >= 20:
        limit = 20

    if not created_by:
        raise Exception("created_by is required")

    tasks = Task.objects.filter(
        created_by=created_by
    ).filter(Q(title__icontains=query) | Q(
        description__icontains=query)).order_by('-created_at')[:limit]
    # return tasks
    serialized = TaskSerializer(tasks, many=True)
    return json.dumps(serialized.data)


task_tools = [
    get_tasks,
    create_task,
    update_task,
    delete_task,
    get_task,
    search_tasks
]

# __all__ = [
#     'task_tools',
#     'get_tasks',
#     'create_task',
#     'update_task',
#     'delete_task',
#     'get_task',
#     'search_tasks'
# ]
