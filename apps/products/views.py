"""
Views for Products app.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Product, ProductTask
from .serializers import (
    ProductSerializer,
    ProductDetailSerializer,
    ProductCreateSerializer,
    ProductListSerializer,
    ProductTaskSerializer,
    ProductTaskCreateSerializer,
)
from core.permissions import IsStaffUser


class ProductViewSet(viewsets.ModelViewSet):
    """ViewSet for Product management."""
    
    queryset = Product.objects.prefetch_related('product_tasks__task').all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        """Return appropriate serializer class."""
        if self.action == 'create':
            return ProductCreateSerializer
        elif self.action == 'retrieve':
            return ProductDetailSerializer
        elif self.action == 'list':
            return ProductListSerializer
        return ProductSerializer
    
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
    
    @action(detail=True, methods=['get'])
    def tasks(self, request, pk=None):
        """Get all tasks for a product."""
        product = self.get_object()
        product_tasks = product.product_tasks.select_related('task').all()
        serializer = ProductTaskSerializer(product_tasks, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsStaffUser])
    def add_task(self, request, pk=None):
        """Add a task to product."""
        product = self.get_object()
        serializer = ProductTaskCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Check if task already exists for this product
        if ProductTask.objects.filter(
            product=product,
            task=serializer.validated_data['task']
        ).exists():
            return Response(
                {'error': 'This task is already assigned to this product.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        product_task = serializer.save(product=product)
        response_serializer = ProductTaskSerializer(product_task)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['delete'], permission_classes=[IsStaffUser],
            url_path='remove_task/(?P<task_id>[^/.]+)')
    def remove_task(self, request, pk=None, task_id=None):
        """Remove a task from product."""
        product = self.get_object()
        
        try:
            product_task = ProductTask.objects.get(product=product, task_id=task_id)
            product_task.delete()
            return Response(
                {'message': 'Task removed from product.'},
                status=status.HTTP_200_OK
            )
        except ProductTask.DoesNotExist:
            return Response(
                {'error': 'Task not found for this product.'},
                status=status.HTTP_404_NOT_FOUND
            )


class ProductTaskViewSet(viewsets.ModelViewSet):
    """ViewSet for ProductTask management."""
    
    queryset = ProductTask.objects.select_related('product', 'task').all()
    serializer_class = ProductTaskSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        """Set permissions based on action."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsStaffUser()]
        return [IsAuthenticated()]
