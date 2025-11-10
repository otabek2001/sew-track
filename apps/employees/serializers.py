"""
Serializers for Employees app.
"""

from rest_framework import serializers
from .models import Employee
from apps.accounts.serializers import UserSerializer


class EmployeeSerializer(serializers.ModelSerializer):
    """Serializer for Employee model."""
    
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_role = serializers.CharField(source='user.get_role_display', read_only=True)
    
    class Meta:
        model = Employee
        fields = [
            'id', 'user', 'user_email', 'user_role', 'full_name', 'phone',
            'position', 'employment_type', 'hourly_rate', 'is_active',
            'hired_at', 'terminated_at', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class EmployeeDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer with user information."""
    
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Employee
        fields = [
            'id', 'user', 'full_name', 'phone', 'position', 'employment_type',
            'hourly_rate', 'is_active', 'hired_at', 'terminated_at', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class EmployeeCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating employees."""
    
    class Meta:
        model = Employee
        fields = [
            'user', 'full_name', 'phone', 'position', 'employment_type',
            'hourly_rate', 'hired_at', 'notes'
        ]
    
    def validate_user(self, value):
        """Check if user already has an employee record."""
        if Employee.objects.filter(user=value).exists():
            raise serializers.ValidationError(
                'This user already has an employee record.'
            )
        return value


class EmployeeStatisticsSerializer(serializers.Serializer):
    """Serializer for employee statistics."""
    
    total_work_records = serializers.IntegerField()
    total_earnings = serializers.DecimalField(max_digits=12, decimal_places=2)
    average_daily_earnings = serializers.DecimalField(max_digits=10, decimal_places=2)
    working_days = serializers.IntegerField()
    current_month_earnings = serializers.DecimalField(max_digits=12, decimal_places=2)

