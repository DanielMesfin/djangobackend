# broker/api/v1/views/business.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import models
from broker.models.business import BusinessProfile, BusinessMember
from broker.models.kyc import BusinessDocument
from ..serializers.business import (
    BusinessProfileSerializer,
    BusinessDocumentSerializer,
    BusinessMemberSerializer
)
from .base import BaseViewSet

class BusinessProfileViewSet(BaseViewSet):
    queryset = BusinessProfile.objects.all()
    serializer_class = BusinessProfileSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['business_type', 'industry', 'is_verified']
    search_fields = ['business_name', 'description']
    ordering_fields = ['created_at', 'business_name']

    def get_queryset(self):
        return self.queryset.filter(
            models.Q(user=self.request.user) |
            models.Q(members__user=self.request.user)
        ).select_related('user').prefetch_related('members__user').distinct()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def add_member(self, request, pk=None):
        business = self.get_object()
        if business.user != request.user:
            return Response(
                {'error': 'Only the business owner can add members'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = BusinessMemberSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save(business=business)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BusinessDocumentViewSet(BaseViewSet):
    queryset = BusinessDocument.objects.all()
    serializer_class = BusinessDocumentSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['document_type', 'is_verified']
    search_fields = ['file_name', 'document_number']
    ordering_fields = ['created_at']

    def get_queryset(self):
        return BusinessDocument.objects.filter(
            models.Q(user=self.request.user) |
            models.Q(business__members__user=self.request.user)
        ).select_related('user', 'verified_by').prefetch_related('business__members').distinct()

class BusinessMemberViewSet(BaseViewSet):
    queryset = BusinessMember.objects.all()
    serializer_class = BusinessMemberSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['role', 'status']
    search_fields = ['business__business_name', 'user__email']
    ordering_fields = ['joined_at']

    def get_queryset(self):
        return BusinessMember.objects.filter(
            models.Q(business__user=self.request.user) |
            models.Q(user=self.request.user)
        ).select_related('business', 'user').distinct()