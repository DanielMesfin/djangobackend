# broker/api/v1/views/base.py
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

class BaseViewSet(viewsets.ModelViewSet):
    """
    Base viewset for all API views
    """
    permission_classes = []
    
    def get_queryset(self):
        return self.queryset.all()
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        obj = self.get_object()
        obj.is_active = True
        obj.save()
        return Response({'status': 'activated'})
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        obj = self.get_object()
        obj.is_active = False
        obj.save()
        return Response({'status': 'deactivated'})