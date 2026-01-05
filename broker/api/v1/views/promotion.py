# broker/api/v1/views/promotion.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import models
from broker.models.promotion import Promotion, PromotionClaim
from ..serializers.promotion import PromotionSerializer, PromotionClaimSerializer
from .base import BaseViewSet

class PromotionViewSet(BaseViewSet):
    queryset = Promotion.objects.all()
    serializer_class = PromotionSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['category', 'is_active']
    search_fields = ['title', 'description']
    ordering_fields = ['start_date', 'end_date', 'created_at']

    def get_queryset(self):
        queryset = self.queryset
        if not self.request.user.is_staff:
            queryset = queryset.filter(
                models.Q(business__user=self.request.user) |
                models.Q(business__members__user=self.request.user) |
                models.Q(is_active=True)
            )
        return queryset.select_related('business').prefetch_related('claims__user').distinct()

    def perform_create(self, serializer):
        # Business is required and should be set in serializer
        serializer.save()

    @action(detail=True, methods=['post'])
    def claim(self, request, pk=None):
        promotion = self.get_object()
        if promotion.status != 'active':
            return Response(
                {'error': 'This promotion is not active'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if promotion.claims.filter(user=request.user).exists():
            return Response(
                {'error': 'You have already claimed this promotion'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        serializer = PromotionClaimSerializer(
            data={},
            context={'request': request, 'promotion': promotion}
        )
        if serializer.is_valid():
            serializer.save(user=request.user, promotion=promotion)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PromotionClaimViewSet(BaseViewSet):
    queryset = PromotionClaim.objects.all()
    serializer_class = PromotionClaimSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = []
    search_fields = ['promotion__title', 'user__email']
    ordering_fields = ['claimed_at']

    def get_queryset(self):
        if self.request.user.is_staff:
            return PromotionClaim.objects.all().select_related('promotion', 'user')
        return PromotionClaim.objects.filter(user=self.request.user).select_related(
            'promotion', 'user'
        )

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def approve(self, request, pk=None):
        claim = self.get_object()
        if claim.promotion.business.user != request.user:
            return Response(
                {'error': 'Only the business owner can approve claims'},
                status=status.HTTP_403_FORBIDDEN
            )
            
        claim.status = 'approved'
        claim.save()
        return Response({'status': 'Claim approved'})

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def reject(self, request, pk=None):
        claim = self.get_object()
        if claim.promotion.business.user != request.user:
            return Response(
                {'error': 'Only the business owner can reject claims'},
                status=status.HTTP_403_FORBIDDEN
            )
            
        claim.status = 'rejected'
        claim.rejection_reason = request.data.get('rejection_reason', '')
        claim.save()
        return Response({'status': 'Claim rejected'})