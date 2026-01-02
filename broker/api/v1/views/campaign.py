# broker/api/v1/views/campaign.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import models
from broker.models.campaign import Campaign, CampaignCollaborator, CampaignProduct
from ..serializers.campaign import (
    CampaignSerializer,
    CampaignCollaboratorSerializer,
    CampaignProductSerializer
)
from .base import BaseViewSet

class CampaignViewSet(BaseViewSet):
    queryset = Campaign.objects.all()
    serializer_class = CampaignSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(
            models.Q(created_by=self.request.user) |
            models.Q(collaborators__user=self.request.user)
        ).distinct().prefetch_related('products', 'collaborators')

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def add_collaborator(self, request, pk=None):
        campaign = self.get_object()
        if campaign.created_by != request.user:
            return Response(
                {'error': 'Only the campaign creator can add collaborators'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = CampaignCollaboratorSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save(campaign=campaign)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def add_product(self, request, pk=None):
        campaign = self.get_object()
        if campaign.created_by != request.user:
            return Response(
                {'error': 'Only the campaign creator can add products'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = CampaignProductSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save(campaign=campaign)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CampaignCollaboratorViewSet(BaseViewSet):
    serializer_class = CampaignCollaboratorSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CampaignCollaborator.objects.filter(
            models.Q(campaign__created_by=self.request.user) |
            models.Q(user=self.request.user)
        ).distinct()

class CampaignProductViewSet(BaseViewSet):
    serializer_class = CampaignProductSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CampaignProduct.objects.filter(
            models.Q(campaign__created_by=self.request.user) |
            models.Q(campaign__collaborators__user=self.request.user)
        ).distinct()