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

    def get_queryset(self):
        return self.queryset.filter(
            models.Q(owner=self.request.user) |
            models.Q(members__user=self.request.user)
        ).distinct()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['post'])
    def add_member(self, request, pk=None):
        business = self.get_object()
        if business.owner != request.user:
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
    serializer_class = BusinessDocumentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return BusinessDocument.objects.filter(
            models.Q(business__owner=self.request.user) |
            models.Q(business__members__user=self.request.user)
        ).distinct()

class BusinessMemberViewSet(BaseViewSet):
    serializer_class = BusinessMemberSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return BusinessMember.objects.filter(
            models.Q(business__owner=self.request.user) |
            models.Q(user=self.request.user)
        ).distinct()