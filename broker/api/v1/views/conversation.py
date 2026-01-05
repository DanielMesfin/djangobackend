# broker/api/v1/views/conversation.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import models
from broker.models.conversation import Conversation, Message
from ..serializers.conversation import ConversationSerializer, MessageSerializer
from .base import BaseViewSet

class ConversationViewSet(BaseViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status']
    search_fields = ['listing__title']
    ordering_fields = ['last_message_at', 'created_at']

    def get_queryset(self):
        return Conversation.objects.filter(
            models.Q(buyer=self.request.user) |
            models.Q(seller=self.request.user)
        ).select_related('listing', 'buyer', 'seller').prefetch_related(
            'messages__sender'
        ).distinct()

    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        conversation = self.get_object()
        if request.user not in conversation.participants.all():
            return Response(
                {'error': 'You are not a participant in this conversation'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = MessageSerializer(
            data=request.data,
            context={'request': request, 'conversation': conversation}
        )
        if serializer.is_valid():
            serializer.save(sender=request.user, conversation=conversation)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MessageViewSet(BaseViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['message_type', 'is_read']
    search_fields = ['content']
    ordering_fields = ['created_at']

    def get_queryset(self):
        return Message.objects.filter(
            models.Q(conversation__buyer=self.request.user) |
            models.Q(conversation__seller=self.request.user)
        ).select_related('sender', 'conversation').distinct()