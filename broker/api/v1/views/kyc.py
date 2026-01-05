# broker/api/v1/views/kyc.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from broker.models.kyc import KYCVerification
from ..serializers.kyc import KYCVerificationSerializer, KYCVerificationAdminSerializer
from .base import BaseViewSet

class KYCVerificationViewSet(BaseViewSet):
    queryset = KYCVerification.objects.all()
    serializer_class = KYCVerificationSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['document_type', 'status']
    search_fields = ['document_number', 'user__email']
    ordering_fields = ['created_at', 'verified_at']

    def get_serializer_class(self):
        if self.request.user.is_staff:
            return KYCVerificationAdminSerializer
        return self.serializer_class

    def get_queryset(self):
        queryset = self.queryset
        if self.request.user.is_staff:
            return queryset.select_related('user', 'verified_by').all()
        return queryset.filter(user=self.request.user).select_related('user', 'verified_by')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def approve(self, request, pk=None):
        kyc = self.get_object()
        kyc.status = 'approved'
        kyc.verified_by = request.user
        kyc.save()
        return Response({'status': 'KYC approved'})

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def reject(self, request, pk=None):
        kyc = self.get_object()
        kyc.status = 'rejected'
        kyc.verified_by = request.user
        kyc.rejection_reason = request.data.get('rejection_reason', '')
        kyc.save()
        return Response({'status': 'KYC rejected'})