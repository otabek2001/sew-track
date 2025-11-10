"""
Mixins for SEW-TRACK project views.
"""

from rest_framework import status
from rest_framework.response import Response


class MultiSerializerViewSetMixin:
    """
    Mixin to use different serializers for different actions.
    
    Usage:
        class MyViewSet(MultiSerializerViewSetMixin, viewsets.ModelViewSet):
            serializer_class = MySerializer
            serializer_action_classes = {
                'list': MyListSerializer,
                'create': MyCreateSerializer,
            }
    """
    serializer_action_classes = {}

    def get_serializer_class(self):
        try:
            return self.serializer_action_classes[self.action]
        except (KeyError, AttributeError):
            return super().get_serializer_class()


class CacheResponseMixin:
    """
    Mixin to add caching to ViewSet responses.
    """
    cache_timeout = 60 * 15  # 15 minutes by default

    def dispatch(self, request, *args, **kwargs):
        # Implement caching logic here if needed
        return super().dispatch(request, *args, **kwargs)


class StandardizedResponseMixin:
    """
    Mixin to standardize API responses.
    
    Returns responses in format:
    {
        "success": true/false,
        "data": {...},
        "message": "...",
        "errors": {...}
    }
    """
    
    def finalize_response(self, request, response, *args, **kwargs):
        if isinstance(response, Response):
            if 200 <= response.status_code < 300:
                response.data = {
                    'success': True,
                    'data': response.data,
                    'message': 'Operation successful',
                }
            else:
                response.data = {
                    'success': False,
                    'data': None,
                    'message': 'Operation failed',
                    'errors': response.data,
                }
        return super().finalize_response(request, response, *args, **kwargs)

