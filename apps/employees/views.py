"""
Views for Employees app.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Sum
from datetime import datetime, date

from .models import Employee
from .serializers import (
    EmployeeSerializer,
    EmployeeDetailSerializer,
    EmployeeCreateSerializer,
    EmployeeStatisticsSerializer,
)
from core.permissions import IsStaffUser


class EmployeeViewSet(viewsets.ModelViewSet):
    """ViewSet for Employee management."""
    
    queryset = Employee.objects.select_related('user').all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        """Return appropriate serializer class."""
        if self.action == 'create':
            return EmployeeCreateSerializer
        elif self.action == 'retrieve':
            return EmployeeDetailSerializer
        return EmployeeSerializer
    
    def get_permissions(self):
        """Set permissions based on action."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsStaffUser()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        """Filter queryset based on user role."""
        queryset = super().get_queryset()
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # Filter by position
        position = self.request.query_params.get('position')
        if position:
            queryset = queryset.filter(position=position)
        
        return queryset
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """Get current user's employee profile."""
        try:
            employee = request.user.employee
            serializer = EmployeeDetailSerializer(employee)
            return Response(serializer.data)
        except Employee.DoesNotExist:
            return Response(
                {'detail': 'Employee profile not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'], permission_classes=[IsStaffUser])
    def activate(self, request, pk=None):
        """Activate employee."""
        employee = self.get_object()
        employee.activate()
        
        return Response(
            {'message': f'Employee {employee.full_name} activated.'},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'], permission_classes=[IsStaffUser])
    def deactivate(self, request, pk=None):
        """Deactivate employee."""
        employee = self.get_object()
        termination_date = request.data.get('termination_date')
        
        if termination_date:
            try:
                termination_date = datetime.strptime(termination_date, '%Y-%m-%d').date()
            except ValueError:
                return Response(
                    {'error': 'Invalid date format. Use YYYY-MM-DD.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        employee.deactivate(termination_date)
        
        return Response(
            {'message': f'Employee {employee.full_name} deactivated.'},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def statistics(self, request, pk=None):
        """Get employee statistics."""
        employee = self.get_object()
        
        # This is a placeholder - will be implemented when work_records app is ready
        statistics = {
            'total_work_records': 0,
            'total_earnings': 0,
            'average_daily_earnings': 0,
            'working_days': 0,
            'current_month_earnings': 0,
        }
        
        serializer = EmployeeStatisticsSerializer(statistics)
        return Response(serializer.data)
