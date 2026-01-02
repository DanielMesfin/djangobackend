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
    filterset_fields = ['status', 'promotion_type']
    search_fields = ['title', 'description']

    def get_queryset(self):
        return self.queryset.filter(
            models.Q(created_by=self.request.user) |
            models.Q(status='active')
        ).distinct().prefetch_related('claims')

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

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
    serializer_class = PromotionClaimSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'user', 'promotion']
    
    def get_queryset(self):
        return PromotionClaim.objects.filter(
            models.Q(user=self.request.user) |
            models.Q(promotion__created_by=self.request.user)
        ).distinct().select_related('user', 'promotion')

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def approve(self, request, pk=None):
        claim = self.get_object()
        if claim.promotion.created_by != request.user:
            return Response(
                {'error': 'Only the promotion creator can approve claims'},
                status=status.HTTP_403_FORBIDDEN
            )
            
        claim.status = 'approved'
        claim.save()
        return Response({'status': 'Claim approved'})

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def reject(self, request, pk=None):
        claim = self.get_object()
        if claim.promotion.created_by != request.user:
            return Response(
                {'error': 'Only the promotion creator can reject claims'},
                status=status.HTTP_403_FORBIDDEN
            )
            
        claim.status = 'rejected'
        claim.rejection_reason = request.data.get('rejection_reason', '')
        claim.save()
        return Response({'status': 'Claim rejected'})