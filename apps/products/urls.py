"""
URL patterns for Products app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, ProductTaskViewSet

app_name = 'products'

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'product-tasks', ProductTaskViewSet, basename='product-task')

urlpatterns = [
    path('', include(router.urls)),
]

