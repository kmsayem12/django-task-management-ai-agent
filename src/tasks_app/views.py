import json
from django.http import JsonResponse
from rest_framework import viewsets, status
from django.contrib.auth.models import User
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, AllowAny

from .models import Task
from .serializers import TaskSerializer, UserSerializer


# Create your views here.
class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all().order_by('-created_at')
    serializer_class = TaskSerializer
    # Requires authentication for all actions
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        print("Create request data:", request.data)
        return super().create(request, *args, **kwargs)

    # Override the create method to set the created_by field
    def perform_create(self, serializer):
        print("Creating task for user:", self.request.user)
        print("Data:", serializer.validated_data)
        serializer.save(created_by=self.request.user)

    # Optional: Custom action to mark a task as done
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        task = get_object_or_404(Task, pk=pk)
        task.status = 'completed'
        task.save()
        return Response({'status': 'task completed'}, status=status.HTTP_200_OK)

    # Optional: Custom action to assign a task by username
    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None, username=None):
        task = get_object_or_404(Task, pk=pk)
        username = request.data.get('username')
        if not username:
            return Response({'error': 'Username is required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(username=username)
            task.assigned_to = user
            task.save()
            serializer = self.get_serializer(task)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('username')
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    lookup_field = 'username'  # Allows fetching users by username
