# broker/api/v1/views/base.py
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend


class StandardResultsSetPagination(PageNumberPagination):
    """Standard pagination for API responses"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class BaseViewSet(viewsets.ModelViewSet):
    """
    Base viewset for all API views with optimized defaults
    """
    permission_classes = []
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    def get_queryset(self):
        if hasattr(self, 'queryset') and self.queryset is not None:
            return self.queryset.all()
        return super().get_queryset()
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        obj = self.get_object()
        if hasattr(obj, 'is_active'):
            obj.is_active = True
            obj.save()
            return Response({'status': 'activated'})
        return Response(
            {'error': 'Object does not have is_active field'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        obj = self.get_object()
        if hasattr(obj, 'is_active'):
            obj.is_active = False
            obj.save()
            return Response({'status': 'deactivated'})
        return Response(
            {'error': 'Object does not have is_active field'}, 
            status=status.HTTP_400_BAD_REQUEST
        )