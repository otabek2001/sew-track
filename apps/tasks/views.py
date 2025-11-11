"""
Views for Tasks app - Work Records management.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.db.models import Q, Sum
from django.utils import timezone
from datetime import date, timedelta

from .models import Task, WorkRecord
from apps.products.models import Product, ProductTask
from apps.employees.models import Employee


@login_required
def work_record_create(request):
    """
    Create new work record (mobile-optimized form).
    """
    # Get current user's employee
    try:
        employee = request.user.employee
    except Employee.DoesNotExist:
        return render(request, 'work_records/error.html', {
            'message': 'Siz employee sifatida ro\'yxatdan o\'tmagansiz. Admin bilan bog\'laning.'
        })
    
    if request.method == 'POST':
        product_id = request.POST.get('product')
        task_id = request.POST.get('task')
        quantity = request.POST.get('quantity')
        notes = request.POST.get('notes', '')
        
        # Validation
        if not all([product_id, task_id, quantity]):
            return render(request, 'work_records/create.html', {
                'products': Product.objects.filter(is_active=True),
                'error': 'Iltimos, barcha maydonlarni to\'ldiring!'
            })
        
        try:
            product = Product.objects.get(id=product_id, is_active=True)
            task = Task.objects.get(id=task_id, is_active=True)
            quantity = int(quantity)
            
            if quantity <= 0:
                raise ValueError("Miqdor 0 dan katta bo'lishi kerak")
            
            # Get ProductTask to get price
            product_task = ProductTask.objects.filter(
                product=product,
                task=task
            ).first()
            
            if not product_task:
                return render(request, 'work_records/create.html', {
                    'products': Product.objects.filter(is_active=True),
                    'error': 'Bu mahsulot va operatsiya kombinatsiyasi topilmadi!'
                })
            
            # Create work record
            work_record = WorkRecord.objects.create(
                tenant=request.tenant,
                employee=employee,
                product=product,
                task=task,
                product_task=product_task,
                quantity=quantity,
                price_per_unit=product_task.get_price(),
                total_payment=quantity * product_task.get_price(),
                work_date=date.today(),
                notes=notes,
                status=WorkRecord.Status.PENDING
            )
            
            # Return success message (HTMX or redirect)
            if request.headers.get('HX-Request'):
                return HttpResponse(
                    '<div class="bg-green-50 border-2 border-green-200 rounded-lg p-4 mb-4">'
                    '<p class="text-green-700 font-medium">✅ Muvaffaqiyatli saqlandi!</p>'
                    '</div>',
                    headers={'HX-Redirect': '/work-records/'}
                )
            
            return redirect('tasks:work_records_list')
            
        except (Product.DoesNotExist, Task.DoesNotExist, ValueError) as e:
            return render(request, 'work_records/create.html', {
                'products': Product.objects.filter(is_active=True),
                'error': f'Xatolik: {str(e)}'
            })
    
    # GET request - show form
    # Filter products by current tenant
    products = Product.objects.filter(
        tenant=request.tenant,
        is_active=True
    ).order_by('article_code')
    
    return render(request, 'work_records/create.html', {
        'products': products,
    })


@login_required
def get_product_tasks(request, product_id):
    """
    HTMX endpoint: Get tasks for a specific product.
    Returns HTML select options.
    """
    try:
        product = Product.objects.get(
            id=product_id,
            tenant=request.tenant,
            is_active=True
        )
        product_tasks = ProductTask.objects.filter(
            product=product
        ).select_related('task').filter(
            task__tenant=request.tenant
        ).order_by('task__sequence_order')
        
        return render(request, 'work_records/_task_options.html', {
            'product_tasks': product_tasks,
        })
    except Product.DoesNotExist:
        return HttpResponse('<option value="">Mahsulot topilmadi</option>')


@login_required
def calculate_price(request):
    """
    HTMX endpoint: Calculate total price based on product, task, and quantity.
    Returns JSON with price info.
    """
    product_id = request.GET.get('product')
    task_id = request.GET.get('task')
    quantity = request.GET.get('quantity', 0)
    
    try:
        quantity = int(quantity)
        if quantity <= 0:
            return JsonResponse({'total': 0, 'per_unit': 0})
        
        product_task = ProductTask.objects.get(
            product_id=product_id,
            task_id=task_id
        )
        
        price_per_unit = float(product_task.get_price())
        total = price_per_unit * quantity
        
        return JsonResponse({
            'per_unit': f'{price_per_unit:,.0f}',
            'total': f'{total:,.0f}',
            'total_raw': total
        })
    except (ProductTask.DoesNotExist, ValueError):
        return JsonResponse({'total': 0, 'per_unit': 0})


@login_required
def work_records_list(request):
    """
    List work records for current user (mobile-optimized).
    """
    try:
        employee = request.user.employee
    except Employee.DoesNotExist:
        return render(request, 'work_records/error.html', {
            'message': 'Siz employee sifatida ro\'yxatdan o\'tmagansiz.'
        })
    
    # Filter parameters
    date_filter = request.GET.get('date', 'today')
    status_filter = request.GET.get('status', 'all')
    
    # Base query - filter by tenant and employee
    records = WorkRecord.objects.filter(
        tenant=request.tenant,
        employee=employee
    ).select_related('product', 'task', 'approved_by')
    
    # Date filter
    today = date.today()
    if date_filter == 'today':
        records = records.filter(work_date=today)
    elif date_filter == 'week':
        week_start = today - timedelta(days=today.weekday())
        records = records.filter(work_date__gte=week_start)
    elif date_filter == 'month':
        records = records.filter(
            work_date__year=today.year,
            work_date__month=today.month
        )
    
    # Status filter
    if status_filter != 'all':
        records = records.filter(status=status_filter)
    
    # Statistics
    stats = records.aggregate(
        total_quantity=Sum('quantity'),
        total_payment=Sum('total_payment')
    )
    
    # Order by date (newest first)
    records = records.order_by('-work_date', '-created_at')
    
    return render(request, 'work_records/list.html', {
        'records': records,
        'stats': stats,
        'date_filter': date_filter,
        'status_filter': status_filter,
    })


@login_required
def work_record_detail(request, record_id):
    """
    View/edit/delete work record.
    """
    try:
        employee = request.user.employee
        record = get_object_or_404(
            WorkRecord,
            id=record_id,
            employee=employee
        )
    except Employee.DoesNotExist:
        return render(request, 'work_records/error.html', {
            'message': 'Siz employee sifatida ro\'yxatdan o\'tmagansiz.'
        })
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'delete' and record.status == WorkRecord.Status.PENDING:
            record.delete()
            return redirect('tasks:work_records_list')
        
        elif action == 'update' and record.status == WorkRecord.Status.PENDING:
            # Update quantity and notes
            quantity = int(request.POST.get('quantity', record.quantity))
            notes = request.POST.get('notes', record.notes)
            
            if quantity > 0:
                record.quantity = quantity
                record.total_payment = quantity * record.price_per_unit
                record.notes = notes
                record.save()
            
            return redirect('tasks:work_record_detail', record_id=record.id)
    
    return render(request, 'work_records/detail.html', {
        'record': record,
    })
