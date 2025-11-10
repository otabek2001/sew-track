"""
Views for Tasks app.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Task
from .serializers import (
    TaskSerializer,
    TaskCreateSerializer,
    TaskListSerializer,
)
from core.permissions import IsStaffUser


class TaskViewSet(viewsets.ModelViewSet):
    """ViewSet for Task management."""
    
    queryset = Task.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        """Return appropriate serializer class."""
        if self.action == 'create':
            return TaskCreateSerializer
        elif self.action == 'list':
            return TaskListSerializer
        return TaskSerializer
    
    def get_permissions(self):
        """Set permissions based on action."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsStaffUser()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        """Filter queryset based on query parameters."""
        queryset = super().get_queryset()
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def categories(self, request):
        """Get list of task categories."""
        categories = [
            {'value': choice[0], 'label': choice[1]}
            for choice in Task.Category.choices
        ]
        return Response(categories)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get only active tasks."""
        tasks = self.get_queryset().filter(is_active=True)
        serializer = TaskListSerializer(tasks, many=True)
        return Response(serializer.data)
