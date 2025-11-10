"""
Product models for SEW-TRACK.
"""

from django.db import models
from core.models import TimeStampedModel


class Product(TimeStampedModel):
    """
    Product model.
    
    Represents a product (e.g., "Женский костюм (юбка)") with article code.
    """
    
    class Category(models.TextChoices):
        MENS = 'mens', "Men's Clothing"
        WOMENS = 'womens', "Women's Clothing"
        KIDS = 'kids', "Kids' Clothing"
        ACCESSORIES = 'accessories', 'Accessories'
        OTHER = 'other', 'Other'
    
    article_code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Article Code',
        help_text='Unique product identifier (e.g., ART-034)'
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Product Name'
    )
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.OTHER,
        verbose_name='Category'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Description'
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Additional Metadata',
        help_text='Additional product information in JSON format'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Active Status'
    )
    
    class Meta:
        db_table = 'products'
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ['article_code']
        indexes = [
            models.Index(fields=['article_code']),
            models.Index(fields=['category']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f'{self.article_code} - {self.name}'


class ProductTask(TimeStampedModel):
    """
    ProductTask model - links products to tasks with pricing.
    
    Represents which tasks can be performed on a product and their prices.
    """
    
    class PriceType(models.TextChoices):
        BASE = 'base', 'Base Price'
        PREMIUM = 'premium', 'Premium Price'
    
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='product_tasks',
        verbose_name='Product'
    )
    task = models.ForeignKey(
        'tasks.Task',
        on_delete=models.CASCADE,
        related_name='product_tasks',
        verbose_name='Task'
    )
    base_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Base Price',
        help_text='Standard price per unit in UZS'
    )
    premium_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Premium Price',
        help_text='Premium/rush price per unit in UZS'
    )
    price_type = models.CharField(
        max_length=10,
        choices=PriceType.choices,
        default=PriceType.BASE,
        verbose_name='Default Price Type'
    )
    estimated_minutes = models.IntegerField(
        default=0,
        verbose_name='Estimated Minutes',
        help_text='Estimated time to complete this task (in minutes)'
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Additional Metadata'
    )
    
    class Meta:
        db_table = 'product_tasks'
        verbose_name = 'Product Task'
        verbose_name_plural = 'Product Tasks'
        ordering = ['product', 'task']
        unique_together = ['product', 'task']
        indexes = [
            models.Index(fields=['product', 'task']),
        ]
    
    def __str__(self):
        return f'{self.product.article_code} - {self.task.code}'
    
    def get_price(self, price_type=None):
        """Get price based on type."""
        if price_type == self.PriceType.PREMIUM and self.premium_price:
            return self.premium_price
        return self.base_price
