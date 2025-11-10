"""
Serializers for Products app.
"""

from rest_framework import serializers
from .models import Product, ProductTask
from apps.tasks.serializers import TaskListSerializer


class ProductTaskSerializer(serializers.ModelSerializer):
    """Serializer for ProductTask model."""
    
    task_name = serializers.CharField(source='task.name_uz', read_only=True)
    task_code = serializers.CharField(source='task.code', read_only=True)
    
    class Meta:
        model = ProductTask
        fields = [
            'id', 'task', 'task_code', 'task_name', 'base_price',
            'premium_price', 'price_type', 'estimated_minutes',
            'metadata', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProductTaskCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating product tasks."""
    
    class Meta:
        model = ProductTask
        fields = [
            'task', 'base_price', 'premium_price',
            'price_type', 'estimated_minutes', 'metadata'
        ]
    
    def validate(self, attrs):
        """Validate prices."""
        if attrs.get('premium_price') and attrs['premium_price'] < attrs['base_price']:
            raise serializers.ValidationError({
                'premium_price': 'Premium price must be higher than base price.'
            })
        return attrs


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for Product model."""
    
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    tasks_count = serializers.IntegerField(
        source='product_tasks.count',
        read_only=True
    )
    
    class Meta:
        model = Product
        fields = [
            'id', 'article_code', 'name', 'category', 'category_display',
            'description', 'metadata', 'is_active', 'tasks_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProductDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer with product tasks."""
    
    product_tasks = ProductTaskSerializer(many=True, read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'article_code', 'name', 'category', 'category_display',
            'description', 'metadata', 'is_active', 'product_tasks',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProductCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating products."""
    
    class Meta:
        model = Product
        fields = [
            'article_code', 'name', 'category',
            'description', 'metadata', 'is_active'
        ]
    
    def validate_article_code(self, value):
        """Validate article code format."""
        if not value.startswith('ART-'):
            raise serializers.ValidationError(
                'Article code must start with "ART-"'
            )
        return value.upper()


class ProductListSerializer(serializers.ModelSerializer):
    """Minimal serializer for listing products."""
    
    class Meta:
        model = Product
        fields = ['id', 'article_code', 'name', 'category']

