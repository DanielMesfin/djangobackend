# broker/api/v1/views/campaign.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import models
from broker.models.campaign import Campaign, CampaignCollaborator
from broker.models.listing import CampaignProduct
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
    filterset_fields = ['status', 'business']
    search_fields = ['name', 'description']
    ordering_fields = ['start_date', 'end_date', 'created_at']

    def get_queryset(self):
        return self.queryset.filter(
            models.Q(business__user=self.request.user) |
            models.Q(business__members__user=self.request.user) |
            models.Q(collaborators__user=self.request.user)
        ).select_related('business', 'created_by').prefetch_related(
            'products', 'collaborators__user'
        ).distinct()

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
        # Allow business owner or campaign creator
        if campaign.business and campaign.business.user != request.user and campaign.created_by != request.user:
            return Response(
                {'error': 'Only the campaign creator or business owner can add products'},
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
    queryset = CampaignCollaborator.objects.all()
    serializer_class = CampaignCollaboratorSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['role', 'status']
    search_fields = ['campaign__name', 'user__email']
    ordering_fields = ['joined_at']

    def get_queryset(self):
        return CampaignCollaborator.objects.filter(
            models.Q(campaign__business__user=self.request.user) |
            models.Q(user=self.request.user)
        ).select_related('campaign', 'user').distinct()

class CampaignProductViewSet(BaseViewSet):
    queryset = CampaignProduct.objects.all()
    serializer_class = CampaignProductSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status']
    search_fields = ['campaign__name', 'listing__title']
    ordering_fields = ['created_at']

    def get_queryset(self):
        return CampaignProduct.objects.filter(
            models.Q(campaign__business__user=self.request.user) |
            models.Q(campaign__collaborators__user=self.request.user)
        ).select_related('campaign', 'listing').prefetch_related('campaign__collaborators').distinct()