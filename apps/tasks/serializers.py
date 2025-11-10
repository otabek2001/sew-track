"""
Serializers for Tasks app.
"""

from rest_framework import serializers
from .models import Task


class TaskSerializer(serializers.ModelSerializer):
    """Serializer for Task model."""
    
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    
    class Meta:
        model = Task
        fields = [
            'id', 'code', 'name_uz', 'name_ru', 'description',
            'category', 'category_display', 'sequence_order', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TaskCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating tasks."""
    
    class Meta:
        model = Task
        fields = [
            'code', 'name_uz', 'name_ru', 'description',
            'category', 'sequence_order', 'is_active'
        ]
    
    def validate_code(self, value):
        """Validate task code format."""
        if not value.startswith('TASK-'):
            raise serializers.ValidationError(
                'Task code must start with "TASK-"'
            )
        return value.upper()


class TaskListSerializer(serializers.ModelSerializer):
    """Minimal serializer for listing tasks."""
    
    class Meta:
        model = Task
        fields = ['id', 'code', 'name_uz', 'name_ru', 'category']

