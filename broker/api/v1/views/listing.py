# broker/api/v1/views/listing.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import models
from broker.models.listing import Listing, DraftOrder
from ..serializers.listing import ListingSerializer, DraftOrderSerializer
from .base import BaseViewSet

class ListingViewSet(BaseViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'category', 'created_by']
    search_fields = ['title', 'description']

    def get_queryset(self):
        return self.queryset.filter(
            models.Q(created_by=self.request.user) |
            models.Q(status='published')
        ).distinct().prefetch_related('draft_orders')

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        listing = self.get_object()
        if listing.created_by != request.user:
            return Response(
                {'error': 'Only the listing creator can publish it'},
                status=status.HTTP_403_FORBIDDEN
            )
        listing.status = 'published'
        listing.save()
        return Response({'status': 'listing published'})

    @action(detail=True, methods=['post'])
    def create_draft_order(self, request, pk=None):
        listing = self.get_object()
        serializer = DraftOrderSerializer(
            data=request.data,
            context={'request': request, 'listing': listing}
        )
        if serializer.is_valid():
            serializer.save(listing=listing, buyer=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DraftOrderViewSet(BaseViewSet):
    serializer_class = DraftOrderSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'buyer', 'listing']
    
    def get_queryset(self):
        return DraftOrder.objects.filter(
            models.Q(buyer=self.request.user) |
            models.Q(listing__created_by=self.request.user)
        ).distinct().select_related('buyer', 'listing')

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        draft_order = self.get_object()
        new_status = request.data.get('status')
        
        if not new_status:
            return Response(
                {'error': 'Status is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if draft_order.listing.created_by != request.user:
            return Response(
                {'error': 'Only the listing creator can update the order status'},
                status=status.HTTP_403_FORBIDDEN
            )
            
        draft_order.status = new_status
        draft_order.save()
        return Response({'status': f'Order status updated to {new_status}'})