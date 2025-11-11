"""
Owner/Tenant Admin Panel views.

For owners and tenant administrators to manage:
- Tenants (workshops)
- Employees
- Products
- Tasks
- Reports
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import date, timedelta

from apps.tenants.models import Tenant, TenantMembership
from apps.employees.models import Employee
from apps.products.models import Product, ProductTask
from apps.tasks.models import Task, WorkRecord
from django.contrib.auth import get_user_model

User = get_user_model()


def is_owner_or_tenant_admin(user):
    """Check if user is owner or tenant admin."""
    return user.role in [User.Role.SUPER_ADMIN, User.Role.TENANT_ADMIN] or user.is_staff


@login_required
@user_passes_test(is_owner_or_tenant_admin, login_url='/dashboard/')
def admin_dashboard(request):
    """
    Admin/Owner dashboard - overview of current tenant.
    """
    tenant = request.tenant
    today = date.today()
    
    if not tenant:
        return render(request, 'admin_panel/no_tenant.html')
    
    # Statistics for current tenant
    stats = {
        'employees_count': Employee.objects.filter(tenant=tenant, is_active=True).count(),
        'products_count': Product.objects.filter(tenant=tenant, is_active=True).count(),
        'tasks_count': Task.objects.filter(tenant=tenant, is_active=True).count(),
        'pending_records': WorkRecord.objects.filter(tenant=tenant, status=WorkRecord.Status.PENDING).count(),
        'today_approved': WorkRecord.objects.filter(tenant=tenant, work_date=today, status=WorkRecord.Status.APPROVED).count(),
        'today_production': WorkRecord.objects.filter(tenant=tenant, work_date=today).aggregate(Sum('quantity'))['quantity__sum'] or 0,
        'today_payment': WorkRecord.objects.filter(tenant=tenant, work_date=today).aggregate(Sum('total_payment'))['total_payment__sum'] or 0,
    }
    
    # Recent activity
    recent_records = WorkRecord.objects.filter(
        tenant=tenant
    ).select_related('employee', 'product', 'task').order_by('-created_at')[:10]
    
    return render(request, 'admin_panel/dashboard.html', {
        'tenant': tenant,
        'stats': stats,
        'recent_records': recent_records,
    })


@login_required
@user_passes_test(is_owner_or_tenant_admin, login_url='/dashboard/')
def tenant_list(request):
    """
    List all tenants for current user.
    """
    user = request.user
    
    # Get tenants based on user role
    if user.role == User.Role.SUPER_ADMIN or user.is_staff:
        tenants = Tenant.objects.all()
    else:
        # Get tenants where user is owner or member
        tenants = Tenant.objects.filter(
            Q(owner=user) | Q(memberships__user=user, memberships__is_active=True)
        ).distinct()
    
    return render(request, 'admin_panel/tenant_list.html', {
        'tenants': tenants,
    })


@login_required
@user_passes_test(is_owner_or_tenant_admin, login_url='/dashboard/')
def tenant_edit(request, tenant_id):
    """Edit tenant info."""
    tenant = get_object_or_404(Tenant, id=tenant_id)
    
    # Check access
    if not (tenant.owner == request.user or request.user.role == User.Role.SUPER_ADMIN):
        messages.error(request, 'Sizda bu tsexni tahrirlash huquqi yo\'q!')
        return redirect('admin_panel:tenant_list')
    
    if request.method == 'POST':
        tenant.name = request.POST.get('name', tenant.name)
        tenant.address = request.POST.get('address', tenant.address)
        tenant.phone = request.POST.get('phone', tenant.phone)
        tenant.email = request.POST.get('email', tenant.email)
        tenant.is_active = request.POST.get('is_active') == 'on'
        tenant.save()
        
        messages.success(request, f'"{tenant.name}" yangilandi!')
        return redirect('admin_panel:tenant_list')
    
    return render(request, 'admin_panel/tenant_form.html', {'tenant': tenant})


@login_required
@user_passes_test(is_owner_or_tenant_admin, login_url='/dashboard/')
def tenant_create(request):
    """
    Create new tenant.
    """
    if request.method == 'POST':
        name = request.POST.get('name')
        address = request.POST.get('address', '')
        phone = request.POST.get('phone', '')
        email = request.POST.get('email', '')
        
        if not name:
            messages.error(request, 'Tsex nomi kiritilishi shart!')
            return render(request, 'admin_panel/tenant_form.html')
        
        # Create tenant
        tenant = Tenant.objects.create(
            name=name,
            owner=request.user,
            address=address,
            phone=phone,
            email=email,
            is_active=True
        )
        
        # Create membership for owner
        TenantMembership.objects.create(
            tenant=tenant,
            user=request.user,
            role=TenantMembership.Role.OWNER,
            is_active=True
        )
        
        messages.success(request, f'"{name}" tsexini muvaffaqiyatli yaratdingiz!')
        return redirect('admin_panel:tenant_list')
    
    return render(request, 'admin_panel/tenant_form.html')


@login_required
@user_passes_test(is_owner_or_tenant_admin, login_url='/dashboard/')
def switch_tenant(request, tenant_id):
    """
    Switch to a different tenant.
    Stores tenant_id in session.
    """
    try:
        tenant = Tenant.objects.get(id=tenant_id, is_active=True)
        
        # Verify user has access
        if request.user.owned_tenants.filter(id=tenant_id).exists() or \
           request.user.tenant_memberships.filter(tenant_id=tenant_id, is_active=True).exists():
            # Save to session
            request.session['selected_tenant_id'] = str(tenant_id)
            messages.success(request, f'Tsex o\'zgardi: {tenant.name}')
        else:
            messages.error(request, 'Sizda bu tsexga kirish huquqi yo\'q!')
    except Tenant.DoesNotExist:
        messages.error(request, 'Tsex topilmadi!')
    
    return redirect(request.META.get('HTTP_REFERER', 'admin_panel:dashboard'))


# ============================================================================
# EMPLOYEE MANAGEMENT
# ============================================================================

@login_required
@user_passes_test(is_owner_or_tenant_admin, login_url='/dashboard/')
def employee_list(request):
    """
    List employees for current tenant.
    """
    tenant = request.tenant
    
    if not tenant:
        return render(request, 'admin_panel/no_tenant.html')
    
    # Filter employees by current tenant
    employees = Employee.objects.filter(
        tenant=tenant
    ).select_related('user').order_by('-created_at')
    
    # Statistics
    stats = {
        'total': employees.count(),
        'active': employees.filter(is_active=True).count(),
        'masters': employees.filter(position=Employee.Position.MASTER).count(),
        'workers': employees.filter(position=Employee.Position.WORKER).count(),
    }
    
    return render(request, 'admin_panel/employee_list.html', {
        'tenant': tenant,
        'employees': employees,
        'stats': stats,
    })


@login_required
@user_passes_test(is_owner_or_tenant_admin, login_url='/dashboard/')
def employee_create(request):
    """
    Create new employee for current tenant.
    """
    tenant = request.tenant
    
    if not tenant:
        return render(request, 'admin_panel/no_tenant.html')
    
    if request.method == 'POST':
        # User data
        username = request.POST.get('username')
        password = request.POST.get('password')
        user_role = request.POST.get('user_role')
        
        # Employee data
        full_name = request.POST.get('full_name')
        phone = request.POST.get('phone')
        position = request.POST.get('position')
        employment_type = request.POST.get('employment_type')
        hourly_rate = request.POST.get('hourly_rate', 0)
        hired_at = request.POST.get('hired_at')
        
        # Validation
        if not all([username, password, full_name, phone, position, hired_at]):
            messages.error(request, 'Barcha majburiy maydonlarni to\'ldiring!')
            return render(request, 'admin_panel/employee_form.html', {
                'tenant': tenant,
            })
        
        # Check if username exists
        if User.objects.filter(username=username).exists():
            messages.error(request, f'"{username}" username allaqachon mavjud!')
            return render(request, 'admin_panel/employee_form.html', {
                'tenant': tenant,
            })
        
        try:
            # Create user
            user = User.objects.create_user(
                username=username,
                password=password,
                role=user_role
            )
            
            # Create employee
            employee = Employee.objects.create(
                tenant=tenant,
                user=user,
                full_name=full_name,
                phone=phone,
                position=position,
                employment_type=employment_type,
                hourly_rate=hourly_rate if hourly_rate else 0,
                hired_at=hired_at,
                is_active=True
            )
            
            messages.success(request, f'"{full_name}" muvaffaqiyatli qo\'shildi!')
            return redirect('admin_panel:employee_list')
            
        except Exception as e:
            messages.error(request, f'Xatolik: {str(e)}')
            return render(request, 'admin_panel/employee_form.html', {
                'tenant': tenant,
            })
    
    return render(request, 'admin_panel/employee_form.html', {
        'tenant': tenant,
    })


@login_required
@user_passes_test(is_owner_or_tenant_admin, login_url='/dashboard/')
def employee_edit(request, employee_id):
    """
    Edit employee.
    """
    tenant = request.tenant
    
    if not tenant:
        return render(request, 'admin_panel/no_tenant.html')
    
    employee = get_object_or_404(Employee, id=employee_id, tenant=tenant)
    
    if request.method == 'POST':
        # Update employee data
        employee.full_name = request.POST.get('full_name', employee.full_name)
        employee.phone = request.POST.get('phone', employee.phone)
        employee.position = request.POST.get('position', employee.position)
        employee.employment_type = request.POST.get('employment_type', employee.employment_type)
        
        hourly_rate = request.POST.get('hourly_rate', 0)
        employee.hourly_rate = hourly_rate if hourly_rate else 0
        
        hired_at = request.POST.get('hired_at')
        if hired_at:
            employee.hired_at = hired_at
        
        employee.save()
        
        # Update user role if needed
        user_role = request.POST.get('user_role')
        if user_role and employee.user.role != user_role:
            employee.user.role = user_role
            employee.user.save()
        
        messages.success(request, f'"{employee.full_name}" ma\'lumotlari yangilandi!')
        return redirect('admin_panel:employee_list')
    
    return render(request, 'admin_panel/employee_form.html', {
        'tenant': tenant,
        'employee': employee,
    })


@login_required
@user_passes_test(is_owner_or_tenant_admin, login_url='/dashboard/')
def employee_delete(request, employee_id):
    """
    Deactivate employee.
    """
    tenant = request.tenant
    
    if not tenant:
        return render(request, 'admin_panel/no_tenant.html')
    
    employee = get_object_or_404(Employee, id=employee_id, tenant=tenant)
    
    if request.method == 'POST':
        # Don't actually delete, just deactivate
        employee.deactivate()
        messages.warning(request, f'"{employee.full_name}" faolsizlantirildi.')
        return redirect('admin_panel:employee_list')
    
    return redirect('admin_panel:employee_list')


# ============================================================================
# PRODUCT MANAGEMENT
# ============================================================================

@login_required
@user_passes_test(is_owner_or_tenant_admin, login_url='/dashboard/')
def product_list(request):
    """List products for current tenant."""
    tenant = request.tenant
    
    if not tenant:
        return render(request, 'admin_panel/no_tenant.html')
    
    products = Product.objects.filter(tenant=tenant).order_by('article_code')
    
    stats = {
        'total': products.count(),
        'active': products.filter(is_active=True).count(),
    }
    
    return render(request, 'admin_panel/product_list.html', {
        'tenant': tenant,
        'products': products,
        'stats': stats,
    })


@login_required
@user_passes_test(is_owner_or_tenant_admin, login_url='/dashboard/')
def product_create(request):
    """Create new product."""
    tenant = request.tenant
    
    if not tenant:
        return render(request, 'admin_panel/no_tenant.html')
    
    if request.method == 'POST':
        article_code = request.POST.get('article_code')
        name = request.POST.get('name')
        category = request.POST.get('category')
        description = request.POST.get('description', '')
        
        if not all([article_code, name, category]):
            messages.error(request, 'Barcha majburiy maydonlarni to\'ldiring!')
            return render(request, 'admin_panel/product_form.html', {'tenant': tenant})
        
        # Check if article code exists
        if Product.objects.filter(article_code=article_code).exists():
            messages.error(request, f'"{article_code}" kod allaqachon mavjud!')
            return render(request, 'admin_panel/product_form.html', {'tenant': tenant})
        
        try:
            product = Product.objects.create(
                tenant=tenant,
                article_code=article_code,
                name=name,
                category=category,
                description=description,
                is_active=True
            )
            messages.success(request, f'"{name}" mahsuloti qo\'shildi!')
            return redirect('admin_panel:product_list')
        except Exception as e:
            messages.error(request, f'Xatolik: {str(e)}')
    
    return render(request, 'admin_panel/product_form.html', {'tenant': tenant})


@login_required
@user_passes_test(is_owner_or_tenant_admin, login_url='/dashboard/')
def product_edit(request, product_id):
    """Edit product."""
    tenant = request.tenant
    
    if not tenant:
        return render(request, 'admin_panel/no_tenant.html')
    
    product = get_object_or_404(Product, id=product_id, tenant=tenant)
    
    if request.method == 'POST':
        product.name = request.POST.get('name', product.name)
        product.category = request.POST.get('category', product.category)
        product.description = request.POST.get('description', product.description)
        product.is_active = request.POST.get('is_active') == 'on'
        product.save()
        
        messages.success(request, f'"{product.name}" yangilandi!')
        return redirect('admin_panel:product_list')
    
    return render(request, 'admin_panel/product_form.html', {
        'tenant': tenant,
        'product': product,
    })


# ============================================================================
# TASK MANAGEMENT
# ============================================================================

@login_required
@user_passes_test(is_owner_or_tenant_admin, login_url='/dashboard/')
def task_list(request):
    """List tasks for current tenant."""
    tenant = request.tenant
    
    if not tenant:
        return render(request, 'admin_panel/no_tenant.html')
    
    tasks = Task.objects.filter(tenant=tenant).order_by('sequence_order', 'code')
    
    stats = {
        'total': tasks.count(),
        'active': tasks.filter(is_active=True).count(),
    }
    
    return render(request, 'admin_panel/task_list.html', {
        'tenant': tenant,
        'tasks': tasks,
        'stats': stats,
    })


@login_required
@user_passes_test(is_owner_or_tenant_admin, login_url='/dashboard/')
def task_create(request):
    """Create new task."""
    tenant = request.tenant
    
    if not tenant:
        return render(request, 'admin_panel/no_tenant.html')
    
    if request.method == 'POST':
        code = request.POST.get('code')
        name_uz = request.POST.get('name_uz')
        name_ru = request.POST.get('name_ru', name_uz)
        category = request.POST.get('category')
        sequence_order = request.POST.get('sequence_order', 0)
        description = request.POST.get('description', '')
        
        if not all([code, name_uz, category]):
            messages.error(request, 'Barcha majburiy maydonlarni to\'ldiring!')
            return render(request, 'admin_panel/task_form.html', {'tenant': tenant})
        
        # Check if code exists
        if Task.objects.filter(code=code).exists():
            messages.error(request, f'"{code}" kod allaqachon mavjud!')
            return render(request, 'admin_panel/task_form.html', {'tenant': tenant})
        
        try:
            task = Task.objects.create(
                tenant=tenant,
                code=code,
                name_uz=name_uz,
                name_ru=name_ru,
                category=category,
                sequence_order=sequence_order,
                description=description,
                is_active=True
            )
            messages.success(request, f'"{name_uz}" operatsiyasi qo\'shildi!')
            return redirect('admin_panel:task_list')
        except Exception as e:
            messages.error(request, f'Xatolik: {str(e)}')
    
    return render(request, 'admin_panel/task_form.html', {'tenant': tenant})


@login_required
@user_passes_test(is_owner_or_tenant_admin, login_url='/dashboard/')
def task_edit(request, task_id):
    """Edit task."""
    tenant = request.tenant
    
    if not tenant:
        return render(request, 'admin_panel/no_tenant.html')
    
    task = get_object_or_404(Task, id=task_id, tenant=tenant)
    
    if request.method == 'POST':
        task.name_uz = request.POST.get('name_uz', task.name_uz)
        task.name_ru = request.POST.get('name_ru', task.name_ru)
        task.category = request.POST.get('category', task.category)
        task.sequence_order = request.POST.get('sequence_order', task.sequence_order)
        task.description = request.POST.get('description', task.description)
        task.is_active = request.POST.get('is_active') == 'on'
        task.save()
        
        messages.success(request, f'"{task.name_uz}" yangilandi!')
        return redirect('admin_panel:task_list')
    
    return render(request, 'admin_panel/task_form.html', {
        'tenant': tenant,
        'task': task,
    })


# ============================================================================
# PRODUCT-TASK LINKING (Price Management)
# ============================================================================

@login_required
@user_passes_test(is_owner_or_tenant_admin, login_url='/dashboard/')
def product_tasks(request, product_id):
    """
    Manage tasks for a product (assign tasks and set prices).
    """
    tenant = request.tenant
    
    if not tenant:
        return render(request, 'admin_panel/no_tenant.html')
    
    product = get_object_or_404(Product, id=product_id, tenant=tenant)
    
    # Get all tenant tasks
    all_tasks = Task.objects.filter(tenant=tenant, is_active=True).order_by('sequence_order', 'code')
    
    # Get already linked tasks
    linked_task_ids = ProductTask.objects.filter(product=product).values_list('task_id', flat=True)
    
    # Available tasks (not yet linked)
    available_tasks = all_tasks.exclude(id__in=linked_task_ids)
    
    # Linked product-tasks
    product_tasks = ProductTask.objects.filter(product=product).select_related('task').order_by('task__sequence_order')
    
    return render(request, 'admin_panel/product_tasks.html', {
        'tenant': tenant,
        'product': product,
        'available_tasks': available_tasks,
        'product_tasks': product_tasks,
    })


@login_required
@user_passes_test(is_owner_or_tenant_admin, login_url='/dashboard/')
def product_task_add(request, product_id):
    """Add task to product with price."""
    tenant = request.tenant
    
    if not tenant:
        return render(request, 'admin_panel/no_tenant.html')
    
    product = get_object_or_404(Product, id=product_id, tenant=tenant)
    
    if request.method == 'POST':
        task_id = request.POST.get('task_id')
        base_price = request.POST.get('base_price')
        premium_price = request.POST.get('premium_price', 0)
        estimated_minutes = request.POST.get('estimated_minutes', 30)
        
        if not all([task_id, base_price]):
            messages.error(request, 'Operatsiya va narxni kiriting!')
            return redirect('admin_panel:product_tasks', product_id=product.id)
        
        try:
            task = Task.objects.get(id=task_id, tenant=tenant)
            
            # Check if already exists
            if ProductTask.objects.filter(product=product, task=task).exists():
                messages.warning(request, 'Bu operatsiya allaqachon qo\'shilgan!')
                return redirect('admin_panel:product_tasks', product_id=product.id)
            
            # Create link
            ProductTask.objects.create(
                product=product,
                task=task,
                base_price=base_price,
                premium_price=premium_price if premium_price else base_price,
                price_type=ProductTask.PriceType.BASE,
                estimated_minutes=estimated_minutes
            )
            
            messages.success(request, f'"{task.name_uz}" operatsiyasi qo\'shildi!')
        except Exception as e:
            messages.error(request, f'Xatolik: {str(e)}')
    
    return redirect('admin_panel:product_tasks', product_id=product.id)


@login_required
@user_passes_test(is_owner_or_tenant_admin, login_url='/dashboard/')
def product_task_update(request, product_task_id):
    """Update product-task price."""
    tenant = request.tenant
    
    if not tenant:
        return render(request, 'admin_panel/no_tenant.html')
    
    product_task = get_object_or_404(ProductTask, id=product_task_id, product__tenant=tenant)
    
    if request.method == 'POST':
        product_task.base_price = request.POST.get('base_price', product_task.base_price)
        product_task.premium_price = request.POST.get('premium_price', product_task.premium_price)
        product_task.estimated_minutes = request.POST.get('estimated_minutes', product_task.estimated_minutes)
        product_task.save()
        
        messages.success(request, 'Narx yangilandi!')
    
    return redirect('admin_panel:product_tasks', product_id=product_task.product_id)


@login_required
@user_passes_test(is_owner_or_tenant_admin, login_url='/dashboard/')
def product_task_delete(request, product_task_id):
    """Remove task from product."""
    tenant = request.tenant
    
    if not tenant:
        return render(request, 'admin_panel/no_tenant.html')
    
    product_task = get_object_or_404(ProductTask, id=product_task_id, product__tenant=tenant)
    
    if request.method == 'POST':
        product_id = product_task.product_id
        product_task.delete()
        messages.warning(request, 'Operatsiya o\'chirildi.')
        return redirect('admin_panel:product_tasks', product_id=product_id)
    
    return redirect('admin_panel:product_list')

