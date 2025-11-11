"""
Tenant Middleware - Auto-detect and set current tenant.

This middleware automatically detects the current tenant based on:
1. Employee's tenant (for workers/masters)
2. Session tenant selection (for owners with multiple tenants)
3. First available tenant (for tenant admins)
"""

from apps.tenants.models import Tenant


class TenantMiddleware:
    """
    Middleware to set current tenant on request.
    
    Sets request.tenant and request.tenant_id for all views.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Initialize tenant attributes
        request.tenant = None
        request.tenant_id = None
        
        # Skip for unauthenticated users
        if not request.user.is_authenticated:
            return self.get_response(request)
        
        user = request.user
        
        # Strategy 1: Get tenant from employee profile (most common case)
        if hasattr(user, 'employee') and user.employee:
            request.tenant = user.employee.tenant
            request.tenant_id = user.employee.tenant_id
        
        # Strategy 2: Get tenant from session (for owners switching between tenants)
        elif 'selected_tenant_id' in request.session:
            try:
                tenant_id = request.session['selected_tenant_id']
                tenant = Tenant.objects.get(id=tenant_id, is_active=True)
                
                # Verify user has access to this tenant
                if user.owned_tenants.filter(id=tenant_id).exists() or \
                   user.tenant_memberships.filter(tenant_id=tenant_id, is_active=True).exists():
                    request.tenant = tenant
                    request.tenant_id = tenant.id
            except Tenant.DoesNotExist:
                # Invalid tenant in session, clear it
                del request.session['selected_tenant_id']
        
        # Strategy 3: Auto-select first available tenant for owners
        if not request.tenant:
            # Owner's first tenant
            if user.owned_tenants.exists():
                tenant = user.owned_tenants.filter(is_active=True).first()
                if tenant:
                    request.tenant = tenant
                    request.tenant_id = tenant.id
                    # Save to session for future requests
                    request.session['selected_tenant_id'] = str(tenant.id)
            
            # Or first membership tenant
            elif user.tenant_memberships.filter(is_active=True).exists():
                membership = user.tenant_memberships.filter(is_active=True).first()
                if membership:
                    request.tenant = membership.tenant
                    request.tenant_id = membership.tenant_id
                    request.session['selected_tenant_id'] = str(membership.tenant_id)
        
        # Log tenant selection for debugging
        if request.tenant:
            print(f"🏭 [TENANT] User: {user.username}, Tenant: {request.tenant.name}")
        else:
            print(f"⚠️ [TENANT] User: {user.username}, No tenant found!")
        
        response = self.get_response(request)
        return response


def get_current_tenant(request):
    """
    Helper function to get current tenant from request.
    
    Usage in views:
        tenant = get_current_tenant(request)
    """
    return getattr(request, 'tenant', None)


def get_current_tenant_id(request):
    """
    Helper function to get current tenant ID from request.
    
    Usage in views:
        tenant_id = get_current_tenant_id(request)
    """
    return getattr(request, 'tenant_id', None)

