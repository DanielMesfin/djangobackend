# broker/api/v1/views/transaction.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import models
from django.db import transaction as db_transaction
from broker.models.transaction import Transaction, Wallet
from ..serializers.transaction import TransactionSerializer, WalletSerializer
from .base import BaseViewSet

class WalletViewSet(BaseViewSet):
    serializer_class = WalletSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Wallet.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def my_wallet(self, request):
        wallet, created = Wallet.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(wallet)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_funds(self, request, pk=None):
        wallet = self.get_object()
        if wallet.user != request.user:
            return Response(
                {'error': 'You can only add funds to your own wallet'},
                status=status.HTTP_403_FORBIDDEN
            )
            
        amount = request.data.get('amount')
        if not amount or not isinstance(amount, (int, float)) or amount <= 0:
            return Response(
                {'error': 'A valid positive amount is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        wallet.balance += amount
        wallet.save()
        
        # Create a transaction record
        Transaction.objects.create(
            sender=request.user,
            recipient=request.user,
            amount=amount,
            transaction_type='deposit',
            status='completed',
            description=f'Added funds to wallet: ${amount:.2f}'
        )
        
        return Response({
            'status': 'Funds added successfully',
            'new_balance': wallet.balance
        })

class TransactionViewSet(BaseViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['transaction_type', 'status', 'sender', 'recipient']
    
    def get_queryset(self):
        return Transaction.objects.filter(
            models.Q(sender=self.request.user) |
            models.Q(recipient=self.request.user)
        ).distinct().select_related('sender', 'recipient')

    @action(detail=False, methods=['post'])
    def transfer(self, request):
        recipient_id = request.data.get('recipient_id')
        amount = request.data.get('amount')
        description = request.data.get('description', '')
        
        if not recipient_id or not amount:
            return Response(
                {'error': 'Recipient ID and amount are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError("Amount must be positive")
        except (ValueError, TypeError):
            return Response(
                {'error': 'Amount must be a positive number'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            recipient = User.objects.get(id=recipient_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'Recipient not found'},
                status=status.HTTP_404_NOT_FOUND)