"""
Custom validators for SEW-TRACK project.
"""

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_phone_number(value):
    """
    Validate phone number format.
    
    Expected format: +998XXXXXXXXX
    """
    if not value.startswith('+998'):
        raise ValidationError(
            _('Phone number must start with +998'),
            code='invalid_phone'
        )
    
    # Remove '+998' and check if remaining is digits
    number = value[4:]
    if not number.isdigit() or len(number) != 9:
        raise ValidationError(
            _('Phone number must be in format +998XXXXXXXXX'),
            code='invalid_phone'
        )


def validate_positive_number(value):
    """Validate that a number is positive."""
    if value <= 0:
        raise ValidationError(
            _('Value must be greater than zero'),
            code='invalid_positive'
        )


def validate_non_negative(value):
    """Validate that a number is non-negative."""
    if value < 0:
        raise ValidationError(
            _('Value must be non-negative'),
            code='invalid_non_negative'
        )


def validate_percentage(value):
    """Validate that a value is between 0 and 100."""
    if not 0 <= value <= 100:
        raise ValidationError(
            _('Value must be between 0 and 100'),
            code='invalid_percentage'
        )

