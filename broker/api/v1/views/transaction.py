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
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = []
    search_fields = ['user__email']
    ordering_fields = ['updated_at']
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Wallet.objects.all().select_related('user')
        return Wallet.objects.filter(user=self.request.user).select_related('user')

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
            user=request.user,
            amount=amount,
            transaction_type='DEPOSIT',
            status='COMPLETED',
            description=f'Added funds to wallet: ${amount:.2f}'
        )
        
        return Response({
            'status': 'Funds added successfully',
            'new_balance': wallet.balance
        })

class TransactionViewSet(BaseViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['transaction_type', 'status']
    search_fields = ['reference', 'description']
    ordering_fields = ['created_at', 'amount']
    
    def get_queryset(self):
        queryset = Transaction.objects.all()
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
        return queryset.select_related('user')

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