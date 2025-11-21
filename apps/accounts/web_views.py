"""
Web views for authentication (non-API).
"""

from django.contrib.auth import views as auth_views
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth import logout
from django.http import HttpResponseRedirect


class CustomLoginView(auth_views.LoginView):
    """
    Custom login view with role-based redirect.
    """
    template_name = 'registration/login.html'
    
    def get_success_url(self):
        """
        Redirect user based on their role after successful login.
        """
        user = self.request.user
        
        # Super Admin/Owner → Admin Panel (Custom)
        if user.role in [user.Role.SUPER_ADMIN, user.Role.TENANT_ADMIN]:
            return reverse('admin_panel:dashboard')
        
        # Django Staff → Django Admin
        if user.is_staff and not user.role:
            return reverse('admin:index')
        
        # Master → Master panel
        if user.role == user.Role.MASTER:
            return reverse('master:dashboard')
        
        # Check if user has employee profile with master/supervisor position
        if hasattr(user, 'employee'):
            from apps.employees.models import Employee
            if user.employee.position in [Employee.Position.MASTER, Employee.Position.SUPERVISOR]:
                return reverse('master:dashboard')
        
        # Default: Worker dashboard
        return reverse('dashboard:dashboard')


class CustomLogoutView(auth_views.LogoutView):
    """
    Custom logout view that supports both GET and POST methods.
    """
    http_method_names = ['get', 'post']
    next_page = 'login'  # Default redirect after logout
    
    def get(self, request, *args, **kwargs):
        """Handle GET requests for logout - redirect to login page after logout."""
        logout(request)
        # Get the next page URL, defaulting to login
        next_page = self.get_success_url()
        return HttpResponseRedirect(next_page)
    
    def post(self, request, *args, **kwargs):
        """Handle POST requests for logout - use default behavior."""
        return super().post(request, *args, **kwargs)

