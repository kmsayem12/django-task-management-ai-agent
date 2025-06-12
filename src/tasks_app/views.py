import json
import logging
from uuid import uuid4
from django.http import JsonResponse
from rest_framework import viewsets, status
from django.contrib.auth.models import User
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from .models import Task
from ai_agent import get_agent
from ai_agent.chat_service import ChatService
from .serializers import TaskSerializer, UserSerializer
# Configure logging
logger = logging.getLogger(__name__)

# Create your views here.


class TaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling Task CRUD operations with additional custom actions.
    """
    queryset = Task.objects.all().order_by('-created_at')
    serializer_class = TaskSerializer
    # Requires authentication for all actions
    permission_classes = [IsAuthenticated]

    # Override the create method to set the created_by field
    def perform_create(self, serializer):
        """Set the created_by field when creating a task."""
        logger.info(f"Saving task for user: {self.request.user.username}")
        serializer.save(created_by=self.request.user)

    # Optional: Custom action to mark a task as done
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark a task as completed."""
        try:
            task = get_object_or_404(Task, pk=pk)
            task.status = 'completed'
            task.save()

            logger.info(f"Task {pk} completed by user {request.user.username}")
            return Response({'status': 'task completed'}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error completing task {pk}: {str(e)}")
            return Response(
                {'error': 'Failed to complete task'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    # Optional: Custom action to assign a task by username
    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None, username=None):
        """Assign a task to a user by username."""
        try:
            task = get_object_or_404(Task, pk=pk)
            username = request.data.get('username')
            if not username:
                return Response({'error': 'Username is required'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                user = User.objects.get(username=username)
                task.assigned_to = user
                task.save()
                serializer = self.get_serializer(task)
                logger.info(
                    f"Task {pk} assigned to {username} by {request.user.username}")
                return Response(serializer.data, status=status.HTTP_200_OK)

            except User.DoesNotExist:
                logger.warning(
                    f"Attempted to assign task {pk} to non-existent user: {username}")
                return Response(
                    {'error': f'User "{username}" does not exist'},
                    status=status.HTTP_404_NOT_FOUND
                )

        except Exception as e:
            logger.error(f"Error assigning task {pk}: {str(e)}")
            return Response(
                {'error': 'Failed to assign task'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling User operations.
    """
    queryset = User.objects.all().order_by('username')
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    lookup_field = 'username'  # Allows fetching users by username


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def chat_with_agent(request):
    """
    API endpoint to initiate a chat with the LangGraph AI agent.

    Expected JSON payload:
    {
        "message": "Your message here"
    }

    Returns:
    {
        "data": [
            {
                "content": "...",
                "name": "...",
                "status": "...",
                "tool_call_id": "..."
            }
        ]
    }
    """
    try:
        # Parse request data
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            logger.warning(
                f"Invalid JSON received from user {request.user.username}")
            return JsonResponse(
                {"error": "Invalid JSON format"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user_input = data.get('message', '').strip()

        if not user_input:
            return JsonResponse(
                {"error": "Message is required and cannot be empty"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Initialize and use chat service
        try:
            chat_service = ChatService()
            result = chat_service.process_chat(user_input, request.user.id)
            # is result is list then return first element
            if isinstance(result["data"], list):
                result = result["data"][0]
            return JsonResponse(result, status=status.HTTP_200_OK)

        except ValueError as e:
            logger.error(
                f"Validation error for user {request.user.username}: {str(e)}")
            return JsonResponse(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(
                f"Unexpected error in chat processing for user {request.user.username}: {str(e)}")
            return JsonResponse(
                {"error": "An unexpected error occurred while processing your request"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    except Exception as e:
        logger.error(f"Critical error in chat_with_agent: {str(e)}")
        return JsonResponse(
            {"error": "A critical error occurred"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
