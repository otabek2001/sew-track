"""
Test view for debugging CSS/JS loading issues.
"""

from django.shortcuts import render


def test_page(request):
    """Simple test page to verify CSS and JavaScript loading."""
    return render(request, 'test.html')

