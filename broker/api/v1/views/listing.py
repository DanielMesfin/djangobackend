# broker/api/v1/views/listing.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import models
from broker.models.listing import Listing
from ..serializers.listing import ListingSerializer
from .base import BaseViewSet

class ListingViewSet(BaseViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'category', 'listing_type', 'is_active']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'price', 'updated_at']

    def get_queryset(self):
        queryset = self.queryset
        # Only show own listings or published ones
        if not self.request.user.is_staff:
            queryset = queryset.filter(
                models.Q(user=self.request.user) |
                models.Q(status='PUBLISHED', is_active=True)
            )
        return queryset.select_related('user', 'business').distinct()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        listing = self.get_object()
        if listing.user != request.user:
            return Response(
                {'error': 'Only the listing creator can publish it'},
                status=status.HTTP_403_FORBIDDEN
            )
        listing.status = 'published'
        listing.save()
        return Response({'status': 'listing published'})

# DraftOrder model was removed - functionality moved to product.Order